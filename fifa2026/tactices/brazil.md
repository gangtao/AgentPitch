# Brazil — Tactical Profile

## Identity & Philosophy
Brazil under Carlo Ancelotti is a study in contradiction: the Italian's pragmatic, possession-with-control philosophy bolted onto the most flamboyant attacking talent pool on Earth. Ancelotti has tightened the defensive structure, demanded Vinícius and Raphinha contribute more out of possession, and built the team around a Casemiro-anchored midfield three — Bruno Guimarães and Lucas Paquetá either side — that gives the front three license to improvise. Neymar (#10) is in the squad but is nursing a calf strain and is not expected to start. Recent results: rocky start to qualifying under previous coaches, stabilized by Ancelotti, who arrives at a World Cup for the first time as a national-team manager with a clear mission to restore Brazilian dignity after the 2022 quarter-final exit.

## Formation
- Shape: **4-3-3** (with Vinícius and Raphinha tucking inside, fullbacks providing measured width)
- Role mapping (roster order in `brazil.yaml`):
  - index 0: GK — **Alisson Becker** — elite **sweeper-keeper**, world-class with the ball at his feet, regularly plays 30-yard line-breaking passes.
  - index 1: LB — **Alex Sandro** — experienced overlapping/inverting fullback, comfortable tucking into midfield as a third pivot.
  - index 2: LCB — **Gabriel Magalhães** — left-footed, physical, aerial dominator, primary aggressive defender of the pair.
  - index 3: RCB — **Marquinhos** — captain, ball-playing libero, the calmest passer in the back line; steps into midfield with possession.
  - index 4: RB — **Danilo** — veteran positional fullback (in for the injured Wesley França); tucks inside to form a back three, reads danger, picks his overlaps sparingly.
  - index 5: LCM — **Lucas Paquetá** — the left-sided 8, half-space dribbler and late box-arriver; the creative connector between midfield and the front three.
  - index 6: DM — **Casemiro** — destroyer, sits in front of the back four, ball-winner, allows the 8s to roam.
  - index 7: RCM — **Bruno Guimarães** — deep-lying playmaker, the metronome; the most progressive midfielder, switches play with diagonal passes.
  - index 8: LW — **Vinícius Júnior** — direct 1v1 dribbler, the team's pace and chaos; gets the ball wide left and goes at the right-back.
  - index 9: ST — **Matheus Cunha** — mobile striker, drops between the lines, links play, makes diagonal runs in behind from a withdrawn position.
  - index 10: RW — **Raphinha** — inverted right winger who drifts inside to combine, set-piece deliverer, relentless work rate.

## Style of Play
### Build-up
**Patient short build-up.** Alisson plays out from the back as a rule. Marquinhos and Gabriel split wide; Bruno or Casemiro drops between them when needed. Fullbacks (especially Alex Sandro) often invert to form a 3-2 build-up shape. The deepest playmaker is **Bruno Guimarães** — the team is built to get him on the ball facing forward. Brazil will pass 5-7 times in their own half to draw the press before going long.

### Pressing
**Mid-block default, with selective high-press triggers.** Press triggers: opposition GK passing to a CB with a teammate within 5 yards (jump the angle), CB receiving with back to play. Vinícius will press the opposition RB; Raphinha presses the LB. **Matheus Cunha curves his run** to press the deeper CB. Casemiro is the man behind, intercepting any vertical pass through the middle.

### Defensive shape
Out-of-possession: **4-4-2 mid-block** with Lucas Paquetá pushing up alongside Matheus Cunha. Vinícius drops to LM (a key Ancelotti demand), Raphinha drops to RM. Compact between the lines; Brazil concedes the wide channels to deny the central penetration.

### Wide play
**Asymmetric:** Vinícius wide-and-high on the left, Alex Sandro inverts. Raphinha drifts inside on the right while Danilo stays home and tucks in to form a back three — right-side width comes from Raphinha holding the touchline early or Bruno's underlapping runs. This creates a lopsided shape: wide-left, narrow-right.

### Final third
Patterns: **Vinícius isolation** in the left half-space — get him 1v1 vs the RB, no help, let him cook. **Raphinha-Bruno combinations** down the right — give-and-go around the fullback with Bruno underlapping. **Paquetá between the lines** finding Matheus Cunha's diagonal run in behind. **Cutbacks** from the byline to the edge of the box for Bruno's arriving shot. Set-piece delivery from Raphinha is a major weapon.

## Set Pieces
- Attacking corners: **Raphinha** delivers from the right (in-swinger), **Bruno Guimarães** from the left (in-swinger). Primary aerial targets: Marquinhos, Gabriel Magalhães, Vinícius at the back post.
- Defending corners: **zonal** — six players on the six-yard line, two near-post blockers, two short-corner watchers, Alisson dominant in the air.
- Free kicks: **Raphinha** direct from the right side, **Bruno Guimarães** direct from central positions.
- Penalties: **Vinícius** primary, **Raphinha** secondary, **Lucas Paquetá** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_8` (LW, Vinícius) and I have the ball in the left third with an opponent within 5 units:** Attempt a Move (dribble) at the opponent's outside shoulder — accept loss of possession as a cost.
2. **If my `role == "GK"` (player_id `_0`, Alisson) and pressed by 1 forward:** Play short to the nearest CB. **If pressed by 2 forwards:** play long-diagonal to LW `_8` (Vinícius) on the left wing.
3. **If my `player_id` ends with `_3` (RCB, Marquinhos) and team_phase == "attacking" and no opponent within 10 units:** Carry the ball into midfield (treat as an extra midfielder in possession).
4. **If my `player_id` ends with `_4` (RB, Danilo) and team_phase == "attacking":** Hold a conservative line — tuck inside to form a back three; only overlap when `_10` (Raphinha) has drifted inside AND the ball is in the right third.
5. **If my `player_id` ends with `_1` (LB, Alex Sandro) and team_phase == "attacking":** Invert into the half-space alongside `_6` (Casemiro) — form 3-2 build-up. Do NOT overlap LW `_8` (Vinícius) unless he checks back inside.
6. **If my `role == "MID"` and the carrier's `player_id` is not `_7` (Bruno Guimarães):** Move to give `_7` a passing option in space.
7. **If my `player_id` ends with `_9` (ST, Matheus Cunha) and team_phase == "attacking":** Drop into the AM space when `_5` (Paquetá) pushes higher; make a diagonal run in behind when `_7` (Bruno) receives facing forward.
8. **If team_phase == "defending" and my `player_id` ends with `_8` (LW, Vinícius):** Drop to LM, track the opposition overlapping runner on my flank.
9. **If team_phase == "transition_defense" (just lost the ball):** All MIDs and FWDs counter-press within a 6-unit radius for 4 seconds; if no recovery, drop into 4-4-2 shape.
10. **If my `role == "FWD"` or `role == "MID"` and I'm carrying the ball and a teammate is in space inside the opposition box:** Always prefer Pass over Shoot (Brazil is built on combination play, not long-shot speculation).
11. **If team is leading by 2+ goals:** Keep possession, do NOT counter-attack at speed. Recycle through `_7` (Bruno) and `_6` (Casemiro).
12. **Penalty assignment:** Defer to `_8` (Vinícius) first; if he is fatigued (`stamina < 10`), `_10` (Raphinha).

## Key Player Notes
- **Vinícius (7):** No defensive tracking duty beyond LM line. Free to isolate vs RB. Always 1v1 the first defender.
- **Marquinhos (4):** Licensed to step into midfield with the ball; the team's best passer between the lines from deep.
- **Bruno Guimarães (8):** Free to roam; the playmaker, the chief switch-of-play passer.
- **Lucas Paquetá (20):** The left-sided 8. Half-space dribbler (dribbling 16) and late box-arriver. Trusted to take risks in the final third.
- **Alisson (1):** Sweeper-keeper extreme — line as high as 18-20 units from goal when Brazil have the ball.

## Tournament Mindset
Pressure-tournament team carrying decades of expectation. Brazil under Ancelotti will be more controlled than the Tite-era cavaliers, prepared to grind out 1-0 wins. But when Vinícius gets isolated against a tired fullback in the 70th minute, the game can break open in 60 seconds.
