# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games.

## Formation
- Shape: 4-3-3 (defensive variant — Tchouaméni as single pivot, Camavinga + Rabiot as #8s that drop)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Theo Hernández (speed 18, stamina 18 — overlapping rocket on the left)
  - index 2: LCB — William Saliba (calm progressor, steps into midfield with the ball)
  - index 3: RCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 4: RB — Jules Koundé (converted CB; inverts when France build, stays tucked)
  - index 5: LCM/#8 — Adrien Rabiot (left-sided shuttler, late box arrivals)
  - index 6: DM/#6 — Aurélien Tchouaméni (single pivot, protects CBs, recycles)
  - index 7: RCM/#8 — Eduardo Camavinga (ball-carrier, breaks lines via dribble)
  - index 8: LW — Bradley Barcola (vertical wide threat, 1v1 winger)
  - index 9: CF — Randal Kolo Muani (mobile #9, runs the channel, presses CBs)
  - index 10: RW (free) — Kylian Mbappé (nominal RW but drifts everywhere; captain, decision-maker)

## Style of Play

### Build-up
- Patient, low-risk. Maignan to Saliba or Upamecano. CBs split wide, Tchouaméni drops between them when pressed (back-three build).
- Koundé inverts to form a 3-2 base; Theo Hernández stays high and wide on the left.
- France will accept low possession (45-55%) and play long to Kolo Muani / Mbappé if pressed hard.

### Pressing
- Mid-block, not high-press. Trigger: opponent CB takes a heavy touch or plays a sideways pass under no pressure.
- Kolo Muani leads, Mbappé curves run to cut the switch, Camavinga jumps the opposite #6.
- Otherwise sit in a compact 4-5-1 around the halfway line and force opponents wide.

### Defensive shape
- 4-5-1 / 4-1-4-1 mid-block. Tchouaméni holds in front of the CBs at all times.
- Outside backs only step out when ball is on their flank. Theo Hernández is the only LB who is allowed to be caught upfield because Saliba can cover.
- Aerial duels: Upamecano & Saliba dominate, no compromise.

### Wide play
- Asymmetric. LEFT is the overload zone: Theo overlapping, Barcola staying wide, Rabiot tucking inside to create a triangle.
- RIGHT is the isolation zone: Koundé tucked in, Mbappé and Camavinga left in a 2v2 to break the line.

### Final third
- Two patterns:
  1. **Quick combo**: Camavinga / Rabiot vertical pass → CF lays off → Mbappé runs the channel.
  2. **Transition**: regain ball in own half → 2-3 touches max → release Mbappé or Barcola behind the line.
- Crosses from Theo Hernández aimed at Kolo Muani's near-post run; Mbappé arrives at back post.

## Set Pieces
- Corners: Tchouaméni near-post flick, Upamecano back-post target, Saliba late arriver. Theo or Mbappé to deliver.
- Direct FKs (18-25m): Mbappé takes anything centered. Saliba and Upamecano stay back — France never commits 5 to a corner; counter risk too high.
- Defending corners: man-mark + 2 zonal at near post. Mbappé stays on halfway for the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Saliba/Upamecano) and possession_team is mine, no pressure: pass short to other CB or the DM, never long unless a FWD is in space.
3. When my `player_id` ends with `_6` (DM — Tchouaméni) and team has the ball: stay between CBs and the ball, offer constant short passing option, never above halfway.
4. When my `player_id` ends with `_1` (LB — Theo) and team_phase is "attacking" and ball is on left side: sprint to advance LM position — hug the touchline.
5. When my `player_id` ends with `_4` (RB — Koundé) and team_phase is "attacking": tuck inside to RCM position (inverted FB), give the RW free room.
6. When my `player_id` ends with `_8` (LW — Barcola) and I receive ball isolated 1v1: Move toward defender then Move diagonally inside — invite the duel.
7. When my `player_id` ends with `_9` (CF — Kolo Muani) and team_phase is "defending": press the ball-carrying CB; cut the passing lane to their #6.
8. When my `player_id` ends with `_10` (RW/free — Mbappé, jersey #10) and ball is regained in own half: explode diagonally into space behind opponent LB — demand the pass.
9. When my `player_id` ends with `_5` or `_7` (#8 — Rabiot/Camavinga) and team_phase is "defending": tuck into 4-5-1, never higher than my CM line until ball is won.
10. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_6` (Saliba/Upamecano/Koundé/Tchouaméni) AND ball-carrier has poor body shape; otherwise Hold and contain.
11. When my team is leading by 1+ and clock > 70: drop into 4-5-1 deep block; only the `_10` player (Mbappé) stays high as outball.
12. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_10` (Mbappé) inside the box.

## Key Player Notes
- **Mbappé (idx 10)** — captain, free role. License to drift LW / CF / RW. Always the primary outlet on transitions. Shoot tendency aggressive.
- **Tchouaméni (idx 6)** — the gravitational center; never leaves the pocket in front of the CBs. Sets press triggers.
- **Saliba (idx 2)** — ball-carrying CB. Allowed to drive into midfield if Tchouaméni rotates out.
- **Theo Hernández (idx 1)** — France's left-side engine; supplies all left-flank crosses.
- **Maignan (idx 0)** — set-piece and goal-kick distributor; takes risks with the ball.

## Tournament Mindset
Win the knockouts, not the group. France routinely under-performs xG in groups, then peaks against top-8 opponents — pragmatism + Mbappé in a single moment is enough. Expect cautious group games.
