# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games. France swept Group I with a perfect record (9 points, 10 scored / 2 conceded): 3-1 over Senegal, 3-0 over Iraq, and a 4-1 demolition of Norway capped by an Ousmane Dembélé hat-trick. Now the knockouts begin — win or go home. The blueprint stays the same: control the game, smother the opponent's transitions, and trust the front line to settle it in a single moment.

## Round of 32 Lineup (vs Sweden, June 30 — MetLife Stadium, win-or-go-home)
France names its strongest spine for the first knockout test; no rotation, this is a clean-sheet-first knockout:
- **Theo Hernández** at LB — France's primary attacking full-back, overlapping outlet on the left.
- **Aurélien Tchouaméni + Rabiot** as the double pivot — the ball-winning anchor and the disciplined shuttler; vital for screening Sweden's direct, vertical counters.
- **Front four**: Dembélé and Olise interchange right/centre, Doué on the left, Mbappé central. Dembélé arrives red-hot off his Norway hat-trick — give him the ball in transition.
- Note: William Saliba is managing a back issue (rested vs Norway) but is expected to start the knockout; Ibrahima Konaté is the like-for-like cover at CB if the knock flares.
- Sweden context: physical, set-piece dangerous, and lethal on the break through Gyökeres / Isak / Elanga. They sit deep and play direct — France must guard against the vertical ball over the top and dominate the box on Swedish corners and long throws.

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
- France will accept low possession (45-55%) and play long to Mbappé / Dembélé if pressed hard — but expects to dominate the ball against a Sweden side that defends deep in a back three.

### Pressing
- Mid-block, not high-press. Trigger: opponent CB takes a heavy touch or plays a sideways pass under no pressure.
- Mbappé leads, Doué curves his run to cut the switch, Olise jumps the opposite #6 with Rabiot covering behind.
- Otherwise sit in a compact 4-4-1-1 / 4-5-1 around the halfway line and force opponents wide — vital for cutting off the vertical service to Gyökeres and Isak.

### Defensive shape
- 4-4-1-1 / 4-1-4-1 mid-block. Tchouaméni holds in front of the CBs; Rabiot screens alongside or steps to press.
- Outside backs only step out when ball is on their flank. Theo can be caught high — Rabiot and Tchouaméni shuttle to cover the left channel he vacates.
- Aerial duels: Upamecano & Saliba dominate, no compromise — they must win the duel with Gyökeres and clear every long ball / set-piece delivery, Sweden's main route to goal.

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
- Direct FKs (18-25m): Mbappé or Olise takes anything centered; Dembélé curls from the right. Saliba and Upamecano stay back — France never commits 5 to a corner; counter risk too high (Sweden's transition through Gyökeres / Isak / Elanga is lethal).
- Defending corners & long throws: man-mark + 2 zonal at near post; double up on Gyökeres and the tall Swedish CBs (Lindelöf, Lagerbielke). Sweden are genuinely set-piece dangerous — win the first contact, second balls cleared long. Mbappé stays on halfway for the outball.

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
- **Doué (idx 9)** — starts on the left of the front line; dynamic two-footed dribbler, runs behind the line, direct and aggressive against the Swedish wing-backs.
- **Tchouaméni (idx 5)** — the deep anchor for the knockout; ball-winner and tempo-setter, shields the CBs and snuffs out Sweden's vertical counters before they launch.
- **Rabiot (idx 6)** — the disciplined other half of the double pivot; covers Tchouaméni, arrives late in the box, and patrols the channel Theo vacates.
- **Saliba (idx 3)** — ball-carrying CB managing a back issue (rested vs Norway); expected to start the knockout. Allowed to drive into midfield when Tchouaméni rotates out; Konaté is the like-for-like cover if the knock flares.
- **Theo Hernández (idx 1)** — rampaging attacking LB; overlaps hard and crosses, but must be screened on the counter.
- **Maignan (idx 0)** — set-piece and goal-kick distributor; takes risks with the ball.

## Tournament Mindset
Win the knockouts. France routinely peaks against top-8 opponents — pragmatism + Mbappé in a single moment is enough. This is the Round of 32: one game, win or go home, no second chances. France are clear favourites and topped Group I with a perfect record, but Sweden are exactly the kind of awkward, physical, set-piece-and-counter side that can punish a single lapse. The plan: control possession, keep the clean sheet, deny Sweden the over-the-top ball to Gyökeres / Isak, win the aerial battles on their set pieces, and let the front four — Dembélé in red-hot form — break a deep block. Don't gamble; take the lead, then squeeze the game flat and see it out.
