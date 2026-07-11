# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games. France swept Group I with a perfect record (3-1 Senegal, 3-0 Iraq, 4-1 Norway with a Dembélé hat-trick), opened the knockouts with a controlled 3-0 over Sweden, ground out 1-0 over Paraguay's low block in the Round of 16, and beat Morocco 2-0 in the quarterfinal in Boston — Mbappé (60') and Dembélé (66', his 5th of the tournament) striking in a six-minute burst after Mbappé had missed a first-half penalty. **Six wins from six, 16 scored / 2 conceded.** Now the semifinal vs Spain (July 14, AT&T Stadium, Arlington): the reigning European champions, the side that knocked France out of Euro 2024 — and the first opponent left who will take the ball away from them.

## Semifinal Lineup (vs Spain, July 14 — AT&T Stadium, Arlington, win-or-go-home)
France carries the quarterfinal XI forward, with one selection call up front already made in that round:
- **Désiré Doué** keeps the left of the front line ahead of Bradley Barcola — Deschamps' sole change for the Morocco QF, retained for the semifinal: a two-footed combiner who links play in tight spaces and cuts inside, better suited to a possession-starved game than Barcola's pure vertical running.
- **Manu Koné** continues in the double pivot in place of **Aurélien Tchouaméni** — Tchouaméni returned to training before the QF but was an unused substitute (lingering groin/adductor issue since July 3); Koné keeps his place unless Tchouaméni proves full fitness late. Koné's booking risk is reset: **single yellows were wiped after the quarterfinals**, so no France player enters the semifinal one caution from suspension.
- **Lucas Digne** continues at LB in place of Theo Hernández — a more controlled, technically secure left-back who keeps the shape and delivers left-sided set pieces; vital discipline against Yamal's side of the pitch... which is actually France's RIGHT. Digne's flank faces Yamal only when Spain switch; his day-job is tracking Porro's overlaps beyond Yamal — no, Yamal attacks France's LEFT (Digne's side). Digne must NOT be caught high.
- **Front four**: Doué left, Dembélé at #10, Olise right, Mbappé central. Dembélé (5 goals) and Mbappé (8 goals, leading the Golden Boot race) are the tournament's decisive duo — release them in transition.
- Notes: Marcus Thuram (calf) is fit for the bench. Barcola, Cherki and Thuram are the front-line cover; Konaté the CB cover; Kanté and Zaïre-Emery the midfield cover. Tchouaméni is the wildcard — bench at best.
- Spain context: reigning European champions, six wins from six, only one goal conceded all tournament (De Ketelaere's equalizer in their 2-1 QF win over Belgium). They will have 60%+ of the ball. The tie is decided in transition moments: France must survive the Yamal-Porro right side, deny Rodri clean tempo, and strike into the space behind Spain's high line — exactly how they beat this press-resistant side in the 2021 Nations League final.

## Formation
- Shape: 4-2-3-1 (double pivot — Koné + Rabiot shield the back four; fluid front four of Doué, Dembélé, Olise behind Mbappé)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Lucas Digne (controlled attacking full-back, secure in possession, left-sided set-piece deliverer; disciplined vs Yamal's flank)
  - index 2: LCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 3: RCB — William Saliba (calm progressor, steps into midfield with the ball)
  - index 4: RB — Jules Koundé (converted CB; inverts when France build, stays tucked; primary duel vs Baena/Cucurella overloads)
  - index 5: DM/#6 — Manu Koné (deep-lying anchor in for the injured Tchouaméni; physical ball-winner, covers ground, carries forward, shields the CBs)
  - index 6: DM/#8 — Adrien Rabiot (shuttler, late box arrivals; covers when Koné steps)
  - index 7: LW — Désiré Doué (two-footed inside-combiner on the left; links in tight spaces, cuts in to shoot — skill 18 / dribble 18 / pass 17)
  - index 8: CAM (#10) — Ousmane Dembélé (the floating creator-finisher between the lines; 5 goals, red-hot — drifts right to overload with Olise, shoot 17)
  - index 9: RW — Michael Olise (creative wide hub, cuts inside onto his left foot, set-piece deliverer)
  - index 10: CF — Kylian Mbappé (captain, 8 goals — the focal point, lethal finisher, transition outlet)

## Style of Play

### Build-up
- Patient, low-risk when allowed. Maignan to Saliba or Upamecano. CBs split wide, Koné drops between them when pressed (back-three build).
- Koundé inverts to form a 3-2 base alongside Koné; Digne pushes on more measured; Rabiot into the left half-space.
- **Against Spain, France will NOT have the ball** — expect 35-45% possession. Do not force build-up into Spain's counter-press: when Oyarzabal-Baena-Yamal curve their pressing runs, go long early to Mbappé's channel runs or into Dembélé between the lines. Losing the ball cheaply in the first phase is the one unforgivable error against the best counter-pressing side in the tournament.

### Pressing
- Mid-block, not high-press. Do NOT chase Spain's back line — they want to bait the press and play through it.
- Trigger only: a heavy touch by a CB, or a square pass to Rodri played blind. Then Mbappé and Dembélé collapse on the pivot together.
- Otherwise sit compact in a 4-4-1-1 around halfway: Koné screens the Olmo lane, Rabiot tracks the late Fabián Ruiz arrivals, wingers tuck in to keep Spain's fullback overlaps in view.

### Defensive shape
- 4-4-1-1 / 4-5-1 mid-to-low block. Koné holds in front of the CBs; Rabiot alongside.
- **Right side alert**: Yamal cuts in from Spain's right onto his left foot — Digne shows him wide, Upamecano covers the curler zone, Koné collapses the half-space. Never let Yamal receive facing goal at the top of the box.
- **Left side alert**: Baena drifts inside with Cucurella overlapping — Koundé passes Baena on to the pivot and takes the overlap.
- Aerial duels: Upamecano & Saliba dominate; win every long ball, clear every set-piece delivery.

### Wide play
- Asymmetric. LEFT: Digne stays measured; Doué combines short, comes inside, plays give-and-gos with Mbappé and Rabiot.
- RIGHT is the transition zone: Olise isolated, cuts in onto his left; Dembélé drifts over to create the 2v1 vs Cucurella when Spain's left is high.

### Final third
- Two patterns:
  1. **Quick combo**: Dembélé/Rabiot vertical pass → Mbappé lays off → Doué or Olise runs the channel.
  2. **Transition** (the primary weapon in this tie): regain → 2-3 touches max → release Mbappé behind Spain's high line. Spain squeeze up to halfway; the space behind Cubarsí-Laporte is where this semifinal is won.
- Crosses from Digne aimed at Mbappé's near-post run; Dembélé arrives at the far post, Olise pulls back to the spot.

## Set Pieces
- Corners: Koné near-post flick, Upamecano back-post target, Saliba late arriver. Olise delivers in-swingers; Digne from the left.
- Direct FKs (18-25m): Mbappé or Olise central; Dembélé curls from the right. Saliba and Upamecano stay back — France never commits five forward; Spain's counter through Yamal is lethal.
- **Penalty-shootout order (knockout — level after 90/120 goes to a shootout):**
  1. **Mbappé** — captain, first taker (penalty 18); scored four shootout/spot kicks in the 2022 final cycle — but missed from the spot vs Morocco in the QF, so expect extra focus.
  2. **Dembélé** — penalty 17, in the form of his life.
  3. **Olise** — penalty 17, ice-cold technician.
  4. **Doué** — penalty 15.
  5. **Rabiot** — penalty 14, the veteran closes.
- Defending: man-mark + 2 zonal at near post; Mbappé stays on halfway as the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Upamecano/Saliba) and possession_team is mine, no pressure: pass short to other CB or the DM; if Spain's press collapses on the first pass, clear long toward the `_10` channel rather than dribble out.
3. When my `player_id` ends with `_5` (DM — Koné) and team has the ball: stay between CBs and the ball, offer the constant short option, never above halfway; recycle and shield; only drive forward when the ball is won high and space opens.
4. When my `player_id` ends with `_1` (LB — Digne) and team_phase is "attacking" and ball is on left side: provide width and the overlap for the `_7` player (Doué), but stay measured — never leave the space behind open for Yamal's transitions; deliver the left-sided cross.
5. When my `player_id` ends with `_4` (RB — Koundé) and team_phase is "attacking": tuck inside to RCM (inverted FB), give the `_9` player (Olise) room outside-right.
6. When my `player_id` ends with `_9` (RW — Olise) and I receive isolated 1v1: cut inside onto my left foot and shoot from the right half-space (shoot 16), or slide the reverse pass to the `_10` run.
7. When my `player_id` ends with `_10` (CF — Mbappé) and team_phase is "defending": stay high near halfway as the transition outball; when we win it, sprint in behind the last line and demand the pass.
8. When my `player_id` ends with `_7` (LW — Doué) and team has the ball: come inside off the left to combine short (pass 17 / skill 18) — give-and-go with `_10` or `_6`, then attack the box; shoot when the lane opens (shoot 16).
9. When my `player_id` ends with `_8` (CAM — Dembélé) and team has the ball: float between the lines, drift right to overload with `_9`; take on the last defender (dribble 19) and shoot (shoot 17) or slip `_10` through — I am the second scoring threat, not just a creator.
10. When my `player_id` ends with `_6` (DM/#8 — Rabiot) and team_phase is "defending": tuck into the double pivot beside Koné, never higher than the CM line until the ball is won; cover the left channel when Digne is high.
11. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_5` (Upamecano/Saliba/Koundé/Koné) AND the carrier has poor body shape; otherwise Hold and contain — do not dive in around the box against Yamal or Olmo.
12. When my team is leading by 1+ and clock > 70: drop into a 4-4-1-1 deep block; only the `_10` player (Mbappé) stays high as outball.
13. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_10` (Mbappé) or `_8` (Dembélé) inside the box.

## Key Player Notes
- **Mbappé (idx 10)** — captain, central striker, 8 goals and leading the Golden Boot race. The focal point and the transition weapon this tie is built around: Spain's high line is exactly the space he lives in. Missed a penalty vs Morocco but scored in open play minutes later — fearless.
- **Dembélé (idx 8)** — now the #10, floating behind Mbappé and drifting right; 5 goals including the QF clincher. Explosive dribbler (19) with a genuine finish (17) — the Ballon d'Or holder in the form of his life.
- **Olise (idx 9)** — RW, cuts in onto his left foot; the primary set-piece deliverer and third shootout taker. His half-space curler mirrors Yamal's at the other end.
- **Doué (idx 7)** — LW, kept his place after the QF; a two-footed combiner rather than a burner — the right profile for a match where France sees little of the ball and must keep the moves alive in tight space.
- **Koné (idx 5)** — the anchor while Tchouaméni's groin issue lingers (unused sub in the QF). Physical ball-winner; his duel with Olmo's between-the-lines movement is a tie-decider. Booking slate wiped after the QF — he can tackle freely again, within reason.
- **Rabiot (idx 6)** — the disciplined other half of the pivot; tracks Fabián Ruiz's late runs, arrives late in the box himself.
- **Saliba (idx 3)** — ball-carrying CB, steps into midfield; Konaté is like-for-like cover.
- **Upamecano (idx 2)** — physical duel-winner; must defend the space behind when the line steps up.
- **Digne (idx 1)** — controlled LB in for Theo Hernández; his discipline against Yamal's flank is non-negotiable.
- **Maignan (idx 0)** — sweeper-keeper and distribution starter; will be busy — Spain average 60%+ possession.

## Tournament Mindset
**Semifinal — two wins from a third straight final.** Six from six, 16 scored, 2 conceded, and the tournament's two most decisive attackers. But Spain are the mirror: also six from six, European champions, one goal conceded all tournament, and the side that ended France's Euro 2024 in this exact fixture — Yamal's wonder-strike and Olmo's winner overturning an early French lead in four minutes. Deschamps' teams don't lose this kind of game twice: the 2021 Nations League final (2-1, Benzema-Mbappé after going behind) is the blueprint — concede the ball, stay compact for 90 minutes, and strike through Mbappé the moment Spain's line steps too high. Do not chase possession statistics; chase the three or four transition moments the game will offer. Guard Yamal's half-space, screen Olmo, survive the spells without the ball — and if it goes all the way to penalties, the takers are set and Maignan is a shootout monster. One game from the final. Control the moments, not the ball.
