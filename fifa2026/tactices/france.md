# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games.

## Formation
- Shape: 4-2-3-1 (double pivot — Tchouaméni + Rabiot shield the back four; fluid front four of Olise, Cherki, Mbappé behind Dembélé)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Theo Hernández (speed 18, stamina 18 — overlapping rocket on the left)
  - index 2: LCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 3: RCB — William Saliba (calm progressor, steps into midfield with the ball)
  - index 4: RB — Jules Koundé (converted CB; inverts when France build, stays tucked)
  - index 5: DM/#6 — Aurélien Tchouaméni (deepest pivot, protects CBs, recycles)
  - index 6: DM/#8 — Adrien Rabiot (box-to-box shuttler, late box arrivals; covers when Tchouaméni steps)
  - index 7: RAM/RW — Michael Olise (creator from the right, cuts inside onto his left foot)
  - index 8: CAM (#10) — Rayan Cherki (free-roaming playmaker, threads the final pass)
  - index 9: LW — Kylian Mbappé (nominal LW but drifts everywhere; captain, decision-maker)
  - index 10: CF — Ousmane Dembélé (mobile front man, runs the channel, presses CBs)

## Style of Play

### Build-up
- Patient, low-risk. Maignan to Saliba or Upamecano. CBs split wide, Tchouaméni drops between them when pressed (back-three build).
- Koundé inverts to form a 3-2 base alongside Tchouaméni; Theo Hernández stays high and wide on the left, Rabiot pushes into the left half-space.
- France will accept low possession (45-55%) and play long to Dembélé / Mbappé if pressed hard.

### Pressing
- Mid-block, not high-press. Trigger: opponent CB takes a heavy touch or plays a sideways pass under no pressure.
- Dembélé leads, Mbappé curves his run to cut the switch, Cherki jumps the opposite #6 with Rabiot covering behind.
- Otherwise sit in a compact 4-4-1-1 / 4-5-1 around the halfway line and force opponents wide.

### Defensive shape
- 4-4-1-1 / 4-1-4-1 mid-block. Tchouaméni holds in front of the CBs at all times; Rabiot screens alongside or steps to press.
- Outside backs only step out when ball is on their flank. Theo Hernández is the only LB who is allowed to be caught upfield because Saliba can cover.
- Aerial duels: Upamecano & Saliba dominate, no compromise.

### Wide play
- Asymmetric. LEFT is the overload zone: Theo overlapping, Mbappé staying wide then attacking inside, Rabiot tucking up to create a triangle.
- RIGHT is the isolation zone: Koundé tucked in, Olise left 1v1 to cut inside; Cherki floats to support either flank.

### Final third
- Two patterns:
  1. **Quick combo**: Cherki / Rabiot vertical pass → Dembélé lays off → Mbappé runs the channel.
  2. **Transition**: regain ball in own half → 2-3 touches max → release Mbappé or Dembélé behind the line.
- Crosses from Theo Hernández aimed at Dembélé's near-post run; Mbappé arrives at back post, Olise crashes the far side.

## Set Pieces
- Corners: Tchouaméni near-post flick, Upamecano back-post target, Saliba late arriver. Olise or Cherki to deliver in-swingers; Theo for the left side.
- Direct FKs (18-25m): Mbappé or Cherki takes anything centered; Olise curls from the right. Saliba and Upamecano stay back — France never commits 5 to a corner; counter risk too high.
- Defending corners: man-mark + 2 zonal at near post. Mbappé stays on halfway for the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Upamecano/Saliba) and possession_team is mine, no pressure: pass short to other CB or the DM, never long unless a forward is in space.
3. When my `player_id` ends with `_5` (DM — Tchouaméni) and team has the ball: stay between CBs and the ball, offer constant short passing option, never above halfway.
4. When my `player_id` ends with `_1` (LB — Theo) and team_phase is "attacking" and ball is on left side: sprint to advance LM position — hug the touchline.
5. When my `player_id` ends with `_4` (RB — Koundé) and team_phase is "attacking": tuck inside to RCM position (inverted FB), give Olise free room on the right.
6. When my `player_id` ends with `_7` (RW — Olise) and I receive ball isolated 1v1: Move toward defender then Move diagonally inside onto my left foot — invite the duel and shoot/cutback.
7. When my `player_id` ends with `_10` (CF — Dembélé) and team_phase is "defending": press the ball-carrying CB; cut the passing lane to their #6.
8. When my `player_id` ends with `_9` (LW/free — Mbappé, jersey #10) and ball is regained in own half: explode diagonally into space behind opponent RB — demand the pass.
9. When my `player_id` ends with `_6` (DM/#8 — Rabiot) and team_phase is "defending": tuck into the double pivot beside Tchouaméni, never higher than the CM line until ball is won.
10. When my `player_id` ends with `_8` (CAM — Cherki) and team has the ball in the final third: find the half-space between lines, look first for the through ball to Mbappé or Dembélé.
11. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_5` (Upamecano/Saliba/Koundé/Tchouaméni) AND ball-carrier has poor body shape; otherwise Hold and contain.
12. When my team is leading by 1+ and clock > 70: drop into a 4-4-1-1 deep block; only the `_9` player (Mbappé) stays high as outball.
13. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_9` (Mbappé) inside the box.

## Key Player Notes
- **Mbappé (idx 9)** — captain, free role from the left. License to drift LW / CF / RW. Always the primary outlet on transitions. Shoot tendency aggressive.
- **Dembélé (idx 10)** — central front man, reigning Ballon d'Or-level form; relentless runner who presses and stretches the back line.
- **Cherki (idx 8)** — the creative hub; receives between lines and supplies the killer pass; primary FK option alongside Mbappé.
- **Olise (idx 7)** — right-side dribbler who cuts onto his left; set-piece deliverer and a goal threat from distance.
- **Tchouaméni (idx 5)** — the gravitational center; never leaves the pocket in front of the CBs. Sets press triggers.
- **Rabiot (idx 6)** — the disciplined other half of the double pivot; covers Tchouaméni and arrives late in the box.
- **Saliba (idx 3)** — ball-carrying CB. Allowed to drive into midfield if Tchouaméni rotates out.
- **Theo Hernández (idx 1)** — France's left-side engine; supplies all left-flank crosses.
- **Maignan (idx 0)** — set-piece and goal-kick distributor; takes risks with the ball.

## Tournament Mindset
Win the knockouts, not the group. France routinely under-performs xG in groups, then peaks against top-8 opponents — pragmatism + Mbappé in a single moment is enough. Expect cautious group games.
