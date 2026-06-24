# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games. France enters Matchday 3 already qualified, sitting top of Group I on 6 points (+5 GD) after a 3-1 win over Senegal and a clinical 3-0 win over Iraq. Note: Deschamps has returned to France following his mother's passing, but his structural blueprint remains the team's spine for the Norway decider.

## MD3 Lineup (vs Norway, June 26 — Group I decider for top spot)
With qualification secured, France reverts to its first-choice spine after the MD2 rotation vs Iraq:
- **Theo Hernández** returns at LB in place of Lucas Digne — France's primary attacking full-back resumes the overlapping role.
- **Aurélien Tchouaméni** returns to the deeper midfield role in place of Manu Koné — the metronome / ball-winning anchor is restored for the toughest group game.
- **Désiré Doué** comes in on the left of the front three in place of Bradley Barcola — dynamic dribbler and direct runner.
- **Dembélé** stays on the RIGHT; **Olise** stays as the #10 / CAM; **Mbappé** remains the central striker.
- Note: William Saliba carries a minor knock but is expected to start; if managed, Ibrahima Konaté is the like-for-like cover at RCB.

## Formation
- Shape: 4-2-3-1 (double pivot — Tchouaméni + Rabiot shield the back four; fluid front four of Dembélé, Olise, Doué behind Mbappé)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Theo Hernández (rampaging attacking full-back, overlaps hard, dangerous cross and shot)
  - index 2: LCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 3: RCB — William Saliba (calm progressor, steps into midfield with the ball)
  - index 4: RB — Jules Koundé (converted CB; inverts when France build, stays tucked)
  - index 5: DM/#6 — Aurélien Tchouaméni (deep-lying anchor, ball-winner, dictates tempo, shields the CBs)
  - index 6: DM/#8 — Adrien Rabiot (shuttler, late box arrivals; covers when Tchouaméni steps)
  - index 7: RW — Ousmane Dembélé (explosive dribbler, cuts inside from the right, stretches the defence)
  - index 8: CAM (#10) — Michael Olise (creative hub, cuts inside onto his left foot, set-piece deliverer)
  - index 9: LW — Désiré Doué (dynamic, two-footed dribbler on the left, direct runner, drives at the fullback)
  - index 10: CF — Kylian Mbappé (captain, the focal point of the attack, lethal finisher)

## Style of Play

### Build-up
- Patient, low-risk. Maignan to Saliba or Upamecano. CBs split wide, Tchouaméni drops between them when pressed (back-three build).
- Koundé inverts to form a 3-2 base alongside Tchouaméni; Theo Hernández bombs forward on the left, Rabiot pushes into the left half-space.
- France will accept low possession (45-55%) and play long to Mbappé / Dembélé if pressed hard — useful against Norway's tall, physical press.

### Pressing
- Mid-block, not high-press. Trigger: opponent CB takes a heavy touch or plays a sideways pass under no pressure.
- Mbappé leads, Doué curves his run to cut the switch, Olise jumps the opposite #6 with Rabiot covering behind.
- Otherwise sit in a compact 4-4-1-1 / 4-5-1 around the halfway line and force opponents wide — vital for blunting Haaland service.

### Defensive shape
- 4-4-1-1 / 4-1-4-1 mid-block. Tchouaméni holds in front of the CBs; Rabiot screens alongside or steps to press.
- Outside backs only step out when ball is on their flank. Theo can be caught high — Rabiot and Tchouaméni shuttle to cover the left channel he vacates.
- Aerial duels: Upamecano & Saliba dominate, no compromise — they must win the duel with Haaland and Sørloth.

### Wide play
- Asymmetric. LEFT is the overlapping zone: Theo Hernández sprinting beyond Doué, Doué cutting inside to free the channel, Rabiot tucking up.
- RIGHT is the dribbling zone: Koundé tucked in, Dembélé isolated 1v1 cutting inside; Olise floats to support from the half-space.

### Final third
- Two patterns:
  1. **Quick combo**: Olise / Rabiot vertical pass → Mbappé lays off → Dembélé or Doué runs the channel.
  2. **Transition**: regain ball in own half → 2-3 touches max → release Mbappé or Doué behind the line.
- Crosses from Theo Hernández aimed at Mbappé's near-post run; Doué arrives at back post, Dembélé crashes the far side.

## Set Pieces
- Corners: Tchouaméni near-post flick, Upamecano back-post target, Saliba late arriver. Olise delivers in-swingers; Theo Hernández for the left side.
- Direct FKs (18-25m): Mbappé or Olise takes anything centered; Dembélé curls from the right. Saliba and Upamecano stay back — France never commits 5 to a corner; counter risk too high (Norway's transition through Haaland is lethal).
- Defending corners: man-mark + 2 zonal at near post; double up on Haaland. Mbappé stays on halfway for the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Upamecano/Saliba) and possession_team is mine, no pressure: pass short to other CB or the DM, never long unless a forward is in space.
3. When my `player_id` ends with `_5` (DM — Tchouaméni) and team has the ball: stay between CBs and the ball, offer constant short passing option, never above halfway; dictate tempo and recycle, only drive forward when ball is won high and space opens.
4. When my `player_id` ends with `_1` (LB — Theo Hernández) and team_phase is "attacking" and ball is on left side: overlap aggressively and get to the byline — primary width on the left.
5. When my `player_id` ends with `_4` (RB — Koundé) and team_phase is "attacking": tuck inside to RCM position (inverted FB), give Dembélé free room on the right.
6. When my `player_id` ends with `_7` (RW — Dembélé) and I receive ball isolated 1v1: drive at the defender, use explosive pace to beat on the outside or cut inside — invite the duel and shoot/cutback.
7. When my `player_id` ends with `_10` (CF — Mbappé) and team_phase is "defending": press the ball-carrying CB; cut the passing lane to their #6.
8. When my `player_id` ends with `_9` (LW — Doué) and ball is regained in own half: explode diagonally into space behind opponent RB — demand the pass.
9. When my `player_id` ends with `_6` (DM/#8 — Rabiot) and team_phase is "defending": tuck into the double pivot beside Tchouaméni, never higher than the CM line until ball is won; cover the left channel when Theo is high.
10. When my `player_id` ends with `_8` (CAM — Olise) and team has the ball in the final third: find the half-space between lines, look first for the through ball to Mbappé or Doué.
11. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_5` (Upamecano/Saliba/Koundé/Tchouaméni) AND ball-carrier has poor body shape; otherwise Hold and contain.
12. When my team is leading by 1+ and clock > 70: drop into a 4-4-1-1 deep block; only the `_10` player (Mbappé) stays high as outball.
13. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_10` (Mbappé) inside the box.

## Key Player Notes
- **Mbappé (idx 10)** — captain, central striker. The focal point of the attack, primary finisher. Always the primary outlet on transitions. Shoot tendency aggressive.
- **Dembélé (idx 7)** — RW. Explosive dribbler, cuts inside from the right, stretches the defence with raw pace; set-piece deliverer from the right.
- **Olise (idx 8)** — the creative hub at #10; receives between lines and supplies the killer pass; primary set-piece deliverer.
- **Doué (idx 9)** — into the XI for the Norway decider; dynamic two-footed dribbler on the left, runs behind the line, direct and aggressive.
- **Tchouaméni (idx 5)** — restored as the deep anchor for the toughest group game; ball-winner and tempo-setter, shields the CBs against Haaland.
- **Rabiot (idx 6)** — the disciplined other half of the double pivot; covers Tchouaméni, arrives late in the box, and patrols the channel Theo vacates.
- **Saliba (idx 3)** — ball-carrying CB carrying a minor knock; allowed to drive into midfield if Tchouaméni rotates out (Konaté is cover if rested).
- **Theo Hernández (idx 1)** — rampaging attacking LB; overlaps hard and crosses, but must be screened on the counter.
- **Maignan (idx 0)** — set-piece and goal-kick distributor; takes risks with the ball.

## Tournament Mindset
Win the knockouts, not the group. France routinely peaks against top-8 opponents — pragmatism + Mbappé in a single moment is enough. France is already through to the Round of 32; MD3 vs Norway (both on 6 points) is a straight shootout for top spot and the more favourable knockout path. Expect France to play its strongest spine and go for the win, while still managing minutes — a draw still leaves the group on a knife-edge with Senegal v Iraq played simultaneously, so France will look to control rather than gamble.
