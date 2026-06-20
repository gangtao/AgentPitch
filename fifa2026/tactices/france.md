# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games.

## MD2 Rotation (vs Iraq, June 22)
Deschamps rotates three starters from the 3-1 win over Senegal:
- **Lucas Digne** replaces Theo Hernández at LB (managed minutes for Theo)
- **Manu Koné** replaces Aurélien Tchouaméni in the deeper midfield role (fresh legs, Tchouaméni managed)
- **Bradley Barcola** replaces Désiré Doué on the left wing (earned the start after scoring off the bench vs Senegal)
- **Ousmane Dembélé** shifts from CF to RW; **Michael Olise** moves from RW to the #10 / CAM role; **Kylian Mbappé** moves to the central striker position.

## Formation
- Shape: 4-2-3-1 (double pivot — Koné + Rabiot shield the back four; fluid front four of Dembélé, Olise, Barcola behind Mbappé)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Lucas Digne (experienced left-back, solid crosser, less adventurous than Theo)
  - index 2: LCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 3: RCB — William Saliba (calm progressor, steps into midfield with the ball)
  - index 4: RB — Jules Koundé (converted CB; inverts when France build, stays tucked)
  - index 5: DM/#6 — Manu Koné (box-to-box energy, ball-winning, drives forward when space opens)
  - index 6: DM/#8 — Adrien Rabiot (shuttler, late box arrivals; covers when Koné steps)
  - index 7: RW — Ousmane Dembélé (explosive dribbler, cuts inside from the right, stretches the defence)
  - index 8: CAM (#10) — Michael Olise (creative hub, cuts inside onto his left foot, set-piece deliverer)
  - index 9: LW — Bradley Barcola (pace merchant on the left, direct runner, scored off the bench in MD1)
  - index 10: CF — Kylian Mbappé (captain, the focal point of the attack, lethal finisher)

## Style of Play

### Build-up
- Patient, low-risk. Maignan to Saliba or Upamecano. CBs split wide, Koné drops between them when pressed (back-three build).
- Koundé inverts to form a 3-2 base alongside Koné; Digne overlaps on the left (less aggressively than Theo), Rabiot pushes into the left half-space.
- France will accept low possession (45-55%) and play long to Mbappé / Dembélé if pressed hard.

### Pressing
- Mid-block, not high-press. Trigger: opponent CB takes a heavy touch or plays a sideways pass under no pressure.
- Mbappé leads, Barcola curves his run to cut the switch, Olise jumps the opposite #6 with Rabiot covering behind.
- Otherwise sit in a compact 4-4-1-1 / 4-5-1 around the halfway line and force opponents wide.

### Defensive shape
- 4-4-1-1 / 4-1-4-1 mid-block. Koné holds in front of the CBs; Rabiot screens alongside or steps to press.
- Outside backs only step out when ball is on their flank. Digne is more disciplined than Theo — stays deeper.
- Aerial duels: Upamecano & Saliba dominate, no compromise.

### Wide play
- Asymmetric. LEFT is now the direct running zone: Barcola sprinting in behind, Digne overlapping conservatively, Rabiot tucking up.
- RIGHT is the dribbling zone: Koundé tucked in, Dembélé isolated 1v1 cutting inside; Olise floats to support from the half-space.

### Final third
- Two patterns:
  1. **Quick combo**: Olise / Rabiot vertical pass → Mbappé lays off → Dembélé or Barcola runs the channel.
  2. **Transition**: regain ball in own half → 2-3 touches max → release Mbappé or Barcola behind the line.
- Crosses from Digne aimed at Mbappé's near-post run; Barcola arrives at back post, Dembélé crashes the far side.

## Set Pieces
- Corners: Koné near-post flick, Upamecano back-post target, Saliba late arriver. Olise delivers in-swingers; Digne for the left side.
- Direct FKs (18-25m): Mbappé or Olise takes anything centered; Dembélé curls from the right. Saliba and Upamecano stay back — France never commits 5 to a corner; counter risk too high.
- Defending corners: man-mark + 2 zonal at near post. Mbappé stays on halfway for the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Upamecano/Saliba) and possession_team is mine, no pressure: pass short to other CB or the DM, never long unless a forward is in space.
3. When my `player_id` ends with `_5` (DM — Koné) and team has the ball: stay between CBs and the ball, offer constant short passing option, never above halfway; but allowed to drive forward when ball is won high and space opens.
4. When my `player_id` ends with `_1` (LB — Digne) and team_phase is "attacking" and ball is on left side: advance on the left but stay more conservative than Theo — support rather than overlap at full tilt.
5. When my `player_id` ends with `_4` (RB — Koundé) and team_phase is "attacking": tuck inside to RCM position (inverted FB), give Dembélé free room on the right.
6. When my `player_id` ends with `_7` (RW — Dembélé) and I receive ball isolated 1v1: drive at the defender, use explosive pace to beat on the outside or cut inside — invite the duel and shoot/cutback.
7. When my `player_id` ends with `_10` (CF — Mbappé) and team_phase is "defending": press the ball-carrying CB; cut the passing lane to their #6.
8. When my `player_id` ends with `_9` (LW — Barcola) and ball is regained in own half: explode diagonally into space behind opponent RB — demand the pass.
9. When my `player_id` ends with `_6` (DM/#8 — Rabiot) and team_phase is "defending": tuck into the double pivot beside Koné, never higher than the CM line until ball is won.
10. When my `player_id` ends with `_8` (CAM — Olise) and team has the ball in the final third: find the half-space between lines, look first for the through ball to Mbappé or Barcola.
11. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_5` (Upamecano/Saliba/Koundé/Koné) AND ball-carrier has poor body shape; otherwise Hold and contain.
12. When my team is leading by 1+ and clock > 70: drop into a 4-4-1-1 deep block; only the `_10` player (Mbappé) stays high as outball.
13. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_10` (Mbappé) inside the box.

## Key Player Notes
- **Mbappé (idx 10)** — captain, central striker for MD2. The focal point of the attack, primary finisher. Always the primary outlet on transitions. Shoot tendency aggressive.
- **Dembélé (idx 7)** — moved to RW for MD2. Explosive dribbler, cuts inside from the right, stretches the defence with raw pace; set-piece deliverer from the right.
- **Olise (idx 8)** — the creative hub at #10 for MD2; receives between lines and supplies the killer pass; primary set-piece deliverer.
- **Barcola (idx 9)** — earned the start after scoring off the bench vs Senegal; pace merchant on the left, runs behind the line, direct and aggressive.
- **Koné (idx 5)** — fresh legs replacing Tchouaméni; box-to-box energy, ball-winning, covers the CBs but also drives forward when space opens.
- **Rabiot (idx 6)** — the disciplined other half of the double pivot; covers Koné and arrives late in the box.
- **Saliba (idx 3)** — ball-carrying CB. Allowed to drive into midfield if Koné rotates out.
- **Digne (idx 1)** — experienced LB, more conservative than Theo; supports the left flank without the overlapping rocket runs.
- **Maignan (idx 0)** — set-piece and goal-kick distributor; takes risks with the ball.

## Tournament Mindset
Win the knockouts, not the group. France routinely under-performs xG in groups, then peaks against top-8 opponents — pragmatism + Mbappé in a single moment is enough. MD1's 3-1 win over Senegal gives France breathing room; expect Deschamps to rotate vs Iraq and still collect three points.
