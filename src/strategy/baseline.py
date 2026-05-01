# Baseline test strategy — hand-written, deterministic, used by both teams to
# validate the simulation framework before bringing LLMs back in.
#
# Wire-up: pass via `agent-pitch run --baseline playtest/strategies/baseline.py`.
# When that flag is set, CGP and PMEP are bypassed and the same file is used
# for team_a and team_b. The two teams play identical logic — match outcomes
# reveal asymmetries in the simulation, not strategy differences.
#
# Schema reference: src/foundation/system_prompt_builder/prompt_files/generation.jinja2 v2.0.
# Sandbox constraints (RestrictedPython): no imports, no math.*, helpers must
# be nested inside decide(), only the documented builtins.
#
# Behaviour overview (post-2026-04-22 role-aware rewrite):
#   - GK: hover near own goal, mirror ball y, punt to nearest forward when held.
#   - Carrier: shoot if within 25u of opp goal, pass if pressured, dribble.
#   - DEF off-ball: close down nearest opponent in own half (man-mark) when our
#     team doesn't have the ball; drift forward into half when we do.
#   - MID off-ball: press the carrier (if opp) or push forward to support
#     (if us).
#   - FWD off-ball: when we have the ball, run into space — away from the
#     nearest defender, toward opp goal. When opp has it, stay high (counter
#     threat) until ball comes loose.
#   - Closest non-GK to a loose ball chases it.


def decide(game_state, player_state, history):
    field = game_state["field"]
    ball = game_state["ball"]
    players = game_state["players"]
    my_team = player_state["team"]
    my_id = player_state["player_id"]
    my_pos = player_state["position"]
    my_role = player_state["role"]
    my_anchor = player_state["formation_position"]
    has_ball = player_state["has_ball"]
    on_cooldown = player_state["cooldown_remaining"] > 0

    opp_team = "team_b" if my_team == "team_a" else "team_a"
    # Goal x-coords swap at halftime — read from snapshot, never hardcode.
    my_goal_x = field[my_team + "_goal_x"]
    opp_goal_x = field[opp_team + "_goal_x"]
    goal_y = (field["goal_top"] + field["goal_bottom"]) / 2.0
    field_w = field["width"]
    field_h = field["height"]
    halfway_x = field_w / 2.0
    own_half_low = my_goal_x < halfway_x  # True if our half is x ∈ [0, 50]

    ball_pos = ball["position"]
    carrier_id = ball.get("carrier_id")
    we_have_ball = (carrier_id is not None and players[carrier_id]["team"] == my_team)
    they_have_ball = (carrier_id is not None and players[carrier_id]["team"] != my_team)

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def normalize(dx, dy):
        m = (dx * dx + dy * dy) ** 0.5
        if m < 1e-6:
            return (1.0, 0.0)
        return (dx / m, dy / m)

    def move_toward(target, speed=1.0):
        nx, ny = normalize(target[0] - my_pos[0], target[1] - my_pos[1])
        return Move(dx=nx, dy=ny, speed=speed)

    def in_own_half(pos):
        return (pos[0] <= halfway_x) if own_half_low else (pos[0] >= halfway_x)

    def opponents():
        out = []
        for pid, p in players.items():
            if p["team"] != my_team:
                out.append((pid, p))
        return out

    def teammates():
        out = []
        for pid, p in players.items():
            if pid != my_id and p["team"] == my_team:
                out.append((pid, p))
        return out

    def closest_opponent_to(pos):
        best_pid, best_d = None, 1e9
        for pid, p in opponents():
            d = dist(pos, p["position"])
            if d < best_d:
                best_d = d
                best_pid = pid
        return best_pid, best_d

    # ---- GK behavior --------------------------------------------------------
    if my_role == "GK":
        if has_ball and not on_cooldown:
            # Punt to nearest non-GK teammate ahead of midfield.
            best_tm_pos = None
            best_d = 1e9
            for pid, p in teammates():
                if p["role"] not in ("MID", "FWD"):
                    continue
                d = dist(my_pos, p["position"])
                if d < best_d:
                    best_d = d
                    best_tm_pos = p["position"]
            if best_tm_pos is not None:
                return Pass(target_pos=best_tm_pos, power=18)
            mid_x = (my_goal_x + opp_goal_x) / 2.0
            return Pass(target_pos=(mid_x, goal_y), power=18)

        # Defensive positioning: hover 2u in front of own goal, mirror ball y.
        keep_x = my_goal_x + (2.0 if own_half_low else -2.0)
        keep_y = max(field["goal_bottom"] + 1.0,
                     min(field["goal_top"] - 1.0, ball_pos[1]))
        if dist(my_pos, (keep_x, keep_y)) < 0.3:
            return Hold()
        return move_toward((keep_x, keep_y))

    # ---- Defensive: tackle if opp carrier is in range -----------------------
    # Engine TACKLE_RANGE = 2.0u (post-2026-04-22). Stay just inside the
    # window so the engine doesn't reject as out_of_range.
    if they_have_ball and not on_cooldown:
        opp_carrier_pos = players[carrier_id]["position"]
        if dist(my_pos, opp_carrier_pos) < 1.9:
            return Tackle(target_player_id=carrier_id)

    # ---- Carrier behavior ---------------------------------------------------
    # Strategy v2 (round 4 of iteration log, 2026-04-23): more selective
    # shooting, more patient build-up. Cuts the shot-per-match count from
    # ~50 toward the 5-15 real-soccer range; cuts possession churn by
    # building up patiently instead of dribble-into-pressure.
    if has_ball:
        d_to_goal = dist(my_pos, (opp_goal_x, goal_y))
        in_opp_half = (my_pos[0] > halfway_x) if own_half_low else (my_pos[0] < halfway_x)
        _, closest_opp_d = closest_opponent_to(my_pos)

        # SHOT (quality-gated). Only shoot when:
        #   - within 12u of goal (was 15u — tightened) AND
        #   - y is within the goal mouth ±5u (decent angle, not from corner)
        in_y_window = (field["goal_bottom"] - 5) <= my_pos[1] <= (field["goal_top"] + 5)
        if d_to_goal < 12.0 and in_y_window and not on_cooldown:
            return Shoot(angle=0.0, power=20)

        # NARROW SPECULATIVE SHOT (v3, round 7+). Long-range effort only when
        # carrier is genuinely unmarked (closest opp ≥8u) AND in the 18-25u
        # window AND in opp half. A "you've got time, take a shot" decision.
        # Should fire ~2-3 times per match; ~half end as goal kicks (skill 8
        # FWD spread is wide enough at 25u to often miss the goal mouth).
        # The earlier wide speculative range (15-35u) fired too freely and
        # made the match look like 50-shot ping-pong. Narrowing it brings
        # back OOB events without inflating shot count.
        if (in_opp_half
                and 18.0 <= d_to_goal < 25.0
                and closest_opp_d > 8.0
                and not on_cooldown):
            return Shoot(angle=0.0, power=18)

        # BACK-PASS TO GK (added 2026-04-23). When DEF is in own
        # penalty area (within 16.5u of own goal) AND under heavy
        # pressure AND own GK is on the field, pass back to the GK.
        # Real soccer: defenders sometimes recycle to keeper under
        # pressure. With DEF skill ≈ 12 the pass deviation is ~3-4u;
        # an inaccurate back-pass can overshoot the GK and clear the
        # end line behind, producing a corner to the opposing team.
        # Fires BEFORE the panic clearance so the closer-to-goal
        # situation gets the more conservative recycling option.
        d_to_own_goal = abs(my_pos[0] - my_goal_x)
        if (my_role == "DEF"
                and d_to_own_goal < 16.5
                and closest_opp_d < 3.0
                and not on_cooldown):
            our_gk_pos = None
            for pid, p in teammates():
                if p["role"] == "GK":
                    our_gk_pos = p["position"]
                    break
            if our_gk_pos is not None:
                return Pass(target_pos=our_gk_pos, power=14)

        # PANIC CLEARANCE (DEF/MID under heavy pressure in own half).
        if (my_role in ("DEF", "MID")
                and not in_opp_half
                and closest_opp_d < 3.0
                and not on_cooldown):
            return Pass(target_pos=(opp_goal_x, goal_y), power=18)

        # PRESSURE PASS (any role, opp within 5u). Pass to the most
        # advanced unmarked teammate.
        if closest_opp_d < 5.0 and not on_cooldown:
            best_tm_pos = None
            best_score = -1e9
            for pid, p in teammates():
                if p["role"] == "GK":
                    continue
                tm_to_goal = dist(p["position"], (opp_goal_x, goal_y))
                _, marked_d = closest_opponent_to(p["position"])
                marked_pen = -10.0 if marked_d < 3.0 else 0.0
                score = -tm_to_goal + marked_pen
                if score > best_score:
                    best_score = score
                    best_tm_pos = p["position"]
            if best_tm_pos is not None:
                return Pass(target_pos=best_tm_pos, power=14)

        # PATIENT BUILD-UP (v2). Not under pressure → look for an
        # unmarked teammate ahead. If found, pass instead of dribbling.
        # Soccer reality: dribbling INTO pressure is bad; passing through
        # the lines is how possessions advance.
        if closest_opp_d > 6.0 and not on_cooldown:
            best_tm_pos = None
            best_progress = -1e9
            for pid, p in teammates():
                if p["role"] == "GK":
                    continue
                tm_x = p["position"][0]
                if own_half_low:
                    forward_progress = tm_x - my_pos[0]
                else:
                    forward_progress = my_pos[0] - tm_x
                if forward_progress < 8.0:
                    continue
                _, tm_marked_d = closest_opponent_to(p["position"])
                if tm_marked_d < 3.0:
                    continue
                if forward_progress > best_progress:
                    best_progress = forward_progress
                    best_tm_pos = p["position"]
            if best_tm_pos is not None:
                return Pass(target_pos=best_tm_pos, power=12)

        # CIRCULATE THE BALL (v4, 2026-04-23). When carrier has time AND no
        # forward pass option is available (above patient-build-up returned
        # None), recycle the ball sideways/backward to the most-isolated
        # unmarked teammate. Real soccer's "play out from the back" or
        # "switch the play" pattern. Without this, the strategy falls
        # through to dribbling toward goal — running headlong at defenders
        # and producing the high possession-churn observed in the 10-round
        # iteration.
        if closest_opp_d > 6.0 and not on_cooldown:
            best_tm_pos = None
            best_clear_d = 4.0  # only consider teammates with ≥4u of space
            for pid, p in teammates():
                if p["role"] == "GK":
                    continue
                _, tm_marked_d = closest_opponent_to(p["position"])
                if tm_marked_d > best_clear_d:
                    best_clear_d = tm_marked_d
                    best_tm_pos = p["position"]
            if best_tm_pos is not None:
                return Pass(target_pos=best_tm_pos, power=10)

        # Default: dribble straight at opp goal.
        return move_toward((opp_goal_x, goal_y))

    # ---- Off-ball: closest non-GK teammate chases a LOOSE ball -------------
    # Loose = nobody has it. Whoever is nearest gets it. Other players
    # simultaneously play their role-specific positioning below.
    if carrier_id is None:
        closest_chaser_id = None
        closest_chaser_d = 1e9
        for pid, p in players.items():
            if p["team"] != my_team or p["role"] == "GK":
                continue
            d = dist(p["position"], ball_pos)
            if d < closest_chaser_d:
                closest_chaser_d = d
                closest_chaser_id = pid
        if closest_chaser_id == my_id:
            return move_toward(ball_pos)

    # ---- Role-aware off-ball positioning ------------------------------------
    # Per the 2026-04-22 rewrite: defenders close down attackers in own half;
    # midfielders press the carrier (or support our carrier); forwards seek
    # space when we attack and stay high when we defend.

    if my_role == "DEF":
        if they_have_ball:
            # Man-mark the nearest opponent in our own half. If no opponent
            # has crossed into our half yet, fall back to the dynamic anchor
            # (which is now deep & goal-side per ADR-0022 amendment c).
            mark_pid, mark_d = None, 1e9
            for pid, p in opponents():
                if p["role"] == "GK":
                    continue
                if not in_own_half(p["position"]):
                    continue
                d = dist(my_anchor, p["position"])
                if d < mark_d:
                    mark_d = d
                    mark_pid = pid
            if mark_pid is not None:
                # Stand 1.0u BETWEEN the marked opponent and our goal (goal-
                # side defending). Direction from opponent toward our goal.
                opp_pos = players[mark_pid]["position"]
                gx, gy = my_goal_x, goal_y
                ux, uy = normalize(gx - opp_pos[0], gy - opp_pos[1])
                target = (opp_pos[0] + ux * 1.0, opp_pos[1] + uy * 1.0)
                return move_toward(target, speed=1.0)
            # Fallback when no opponent in own half — use the anchor (which
            # is dynamically positioned goal-side by the phase-zone system).
            target = my_anchor
        elif we_have_ball:
            # Push aggressively into the opponent's half to overlap. Forward
            # bias from anchor by ~15u toward opp goal. With the dynamic
            # phase-aware anchor (ADR-0022), attacking-phase DEF anchor is
            # already at x≈52 (in opp half), so anchor.x + 15 lands near 67
            # — deep in the opponent's half, exactly the "fullback overlap"
            # pattern.
            forward = 1.0 if opp_goal_x > my_anchor[0] else -1.0
            target = (my_anchor[0] + 15.0 * forward, my_anchor[1])
        else:
            # Loose ball — already handled above for the chaser; otherwise
            # hold anchor.
            target = my_anchor

        if dist(my_pos, target) < 0.5:
            return Hold()
        return move_toward(target, speed=0.9)

    if my_role == "MID":
        if they_have_ball:
            # Press the carrier directly — second-defender pressure.
            opp_carrier_pos = players[carrier_id]["position"]
            return move_toward(opp_carrier_pos, speed=1.0)
        elif we_have_ball:
            # Support the carrier by occupying a passing lane ahead of them.
            carrier_pos = players[carrier_id]["position"]
            forward = 1.0 if opp_goal_x > carrier_pos[0] else -1.0
            # Position 12u ahead of carrier and 8u to one side (use my
            # anchor's y to pick which side — the higher-y MID supports
            # the high lane, the lower-y MID supports the low lane).
            side = 8.0 if my_anchor[1] > goal_y else -8.0
            target = (carrier_pos[0] + 12.0 * forward, carrier_pos[1] + side)
            # Clamp to field bounds.
            target = (max(2.0, min(field_w - 2.0, target[0])),
                      max(2.0, min(field_h - 2.0, target[1])))
        else:
            target = my_anchor

        if dist(my_pos, target) < 0.5:
            return Hold()
        return move_toward(target, speed=0.9)

    if my_role == "FWD":
        if we_have_ball:
            # Run into space — away from the nearest defender, biased toward
            # opp goal. Pick a target ~15u from current position in the
            # away-from-defender direction, but clamped to be no further
            # back than my anchor x.
            nearest_def_pid, nearest_def_d = None, 1e9
            for pid, p in opponents():
                if p["role"] == "GK":
                    continue
                d = dist(my_pos, p["position"])
                if d < nearest_def_d:
                    nearest_def_d = d
                    nearest_def_pid = pid
            if nearest_def_pid is not None:
                def_pos = players[nearest_def_pid]["position"]
                # Direction AWAY from defender.
                away_x, away_y = normalize(my_pos[0] - def_pos[0],
                                           my_pos[1] - def_pos[1])
                # Bias the away vector toward opp goal: blend 50/50 with
                # toward-goal direction so we don't run sideways or
                # backwards just to escape pressure.
                tg_x, tg_y = normalize(opp_goal_x - my_pos[0],
                                       goal_y - my_pos[1])
                bx = 0.5 * away_x + 0.5 * tg_x
                by = 0.5 * away_y + 0.5 * tg_y
                bx, by = normalize(bx, by)
                target = (my_pos[0] + bx * 12.0, my_pos[1] + by * 12.0)
            else:
                # No defender in range — just push toward opp goal.
                target = (opp_goal_x, goal_y)
            # Clamp to field.
            target = (max(2.0, min(field_w - 2.0, target[0])),
                      max(2.0, min(field_h - 2.0, target[1])))
        elif they_have_ball:
            # Phase-aware: in defending phase the system has already dropped
            # the FWD anchor into midfield (x≈45 per ADR-0022 amendment c) —
            # honor that anchor instead of biasing forward. Outside defending
            # phase keep the +5u counter-threat bias.
            my_phase = player_state.get("formation_zone_phase", "transitioning")
            if my_phase == "defending":
                target = my_anchor   # tracks back with the team
            else:
                forward = 1.0 if opp_goal_x > my_anchor[0] else -1.0
                target = (my_anchor[0] + 5.0 * forward, my_anchor[1])
        else:
            target = my_anchor

        if dist(my_pos, target) < 0.5:
            return Hold()
        return move_toward(target, speed=1.0)

    # Fallback (shouldn't be reachable — every role handled above).
    if dist(my_pos, my_anchor) < 0.5:
        return Hold()
    return move_toward(my_anchor, speed=0.8)
