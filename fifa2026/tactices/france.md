# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly. The team trades aesthetics for outcomes: deep block when needed, devastating transitions when the opponent over-commits, and Kylian Mbappé as the on-field cheat code. Recent results — back-to-back World Cup finals (2018 winners, 2022 runners-up), Euro 2024 semifinal — confirm Deschamps' formula: keep clean sheets, let the front line decide games. France swept Group I with a perfect record (9 points, 10 scored / 2 conceded): 3-1 over Senegal, 3-0 over Iraq, and a 4-1 demolition of Norway capped by an Ousmane Dembélé hat-trick. They opened the knockouts with a controlled 3-0 win over Sweden in the Round of 32, then saw off Paraguay's low block in the Round of 16 — five wins from five, 14 scored / 2 conceded. Now the quarterfinal vs Morocco (July 9, Boston): the blueprint stays the same — control the game, smother the opponent's transitions, and trust the front line to settle it in a single moment.

## Quarterfinal Lineup (vs Morocco, July 9 — Boston Stadium, win-or-go-home)
France names its strongest spine, with one enforced change in midfield after the injury to Tchouaméni:
- **Manu Koné** starts in the double pivot in place of the injured **Aurélien Tchouaméni** — a physical, high-energy ball-winner who covers more ground and carries the ball forward, but with less of Tchouaméni's deep passing range and dead-ball value. Koné deputised well against Iraq and Paraguay; he is more foul-prone and must manage his booking (yellow vs Paraguay).
- **Lucas Digne** continues at LB in place of Theo Hernández — a more controlled, technically secure left-back who keeps the shape and delivers left-sided set pieces; slightly less of a rampaging overlap threat than Theo, so the left flank is calmer and more compact.
- **Bradley Barcola** starts on the left of the front line ahead of Désiré Doué — raw, direct pace to run behind Morocco's back line and stretch the pitch on transitions.
- **Front four**: Dembélé and Olise interchange right/centre, Barcola on the left, Mbappé central. Dembélé (4 goals) and Mbappé (7 goals) are the tournament's decisive duo — give them the ball in transition.
- **Koné + Rabiot** as the double pivot — the energetic ball-winner and the disciplined shuttler; vital for screening Morocco's press and their transitions through Brahim Díaz and Hakimi.
- Notes: Aurélien Tchouaméni is out with an adductor/thigh tear (recurrence of the issue that cost him the Iraq and Paraguay games) — highly unlikely to feature. Marcus Thuram is still working back from a calf problem and is not in the XI. Désiré Doué and Rayan Cherki are the front-line cover off the bench; Ibrahima Konaté is the like-for-like CB cover; N'Golo Kanté and Warren Zaïre-Emery are the midfield cover.
- Morocco context: unbeaten across five games, compact 4-2-3-1 built to counter. Achraf Hakimi bombs forward from right-back, Brahim Díaz (4 assists) is the transition threat, and their double pivot (Bouaddi / El Aynaoui) screens a solid Diop-anchored back line behind Bounou. France must guard Hakimi's overlaps, break down a disciplined block, and punish the space Morocco leave when they commit forward.

## Formation
- Shape: 4-2-3-1 (double pivot — Koné + Rabiot shield the back four; fluid front four of Dembélé, Olise, Barcola behind Mbappé)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Lucas Digne (controlled attacking full-back, secure in possession, left-sided set-piece deliverer)
  - index 2: LCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 3: RCB — William Saliba (calm progressor, steps into midfield with the ball)
  - index 4: RB — Jules Koundé (converted CB; inverts when France build, stays tucked)
  - index 5: DM/#6 — Manu Koné (deep-lying anchor in for the injured Tchouaméni; physical ball-winner, covers ground, carries forward, shields the CBs)
  - index 6: DM/#8 — Adrien Rabiot (shuttler, late box arrivals; covers when Koné steps)
  - index 7: RW — Ousmane Dembélé (explosive dribbler, cuts inside from the right, stretches the defence)
  - index 8: CAM (#10) — Michael Olise (creative hub, cuts inside onto his left foot, set-piece deliverer)
  - index 9: LW — Bradley Barcola (direct, quick winger on the left, runs behind, drives at the fullback)
  - index 10: CF — Kylian Mbappé (captain, the focal point of the attack, lethal finisher)

## Style of Play

### Build-up
- Patient, low-risk. Maignan to Saliba or Upamecano. CBs split wide, Koné drops between them when pressed (back-three build).
- Koundé inverts to form a 3-2 base alongside Koné; Digne pushes forward on the left but stays more measured than Theo, Rabiot pushes into the left half-space.
- France expects to see plenty of the ball against a Morocco side that defends compact and counters — likely 55-60% possession. Break the block with patience; play long to Mbappé / Barcola only when the counter is on.

### Pressing
- Mid-block, not high-press. Trigger: opponent CB takes a heavy touch or plays a sideways pass under no pressure.
- Mbappé leads, Barcola curves his run to cut the switch, Olise jumps the opposite #6 with Rabiot covering behind.
- Otherwise sit in a compact 4-4-1-1 / 4-5-1 around the halfway line and force Morocco wide and backward — deny the vertical outlet to Brahim Díaz and the inside runs off Hakimi.

### Defensive shape
- 4-4-1-1 / 4-1-4-1 mid-block. Koné holds in front of the CBs; Rabiot screens alongside or steps to press.
- Outside backs only step out when ball is on their flank. Digne is more disciplined than Theo and less likely to be caught high; Rabiot and Koné still shuttle to cover the left channel — and Digne must track Hakimi's overlaps on that side.
- Aerial duels: Upamecano & Saliba dominate, no compromise — win every long ball and clear every set-piece delivery.

### Wide play
- Asymmetric. LEFT is a more controlled channel now: Digne provides measured width and overlap for Barcola, who runs in behind and cuts inside; Rabiot tucks up.
- RIGHT is the dribbling zone: Koundé tucked in, Dembélé isolated 1v1 cutting inside; Olise floats to support from the half-space.

### Final third
- Two patterns:
  1. **Quick combo**: Olise / Rabiot vertical pass → Mbappé lays off → Dembélé or Barcola runs the channel.
  2. **Transition**: regain ball in own half → 2-3 touches max → release Mbappé or Barcola behind the line — the fastest route to punish Morocco when Hakimi and the pivot push up.
- Crosses from Digne aimed at Mbappé's near-post run; Barcola arrives at back post, Dembélé crashes the far side.

## Set Pieces
- Corners: Koné near-post flick, Upamecano back-post target, Saliba late arriver. Olise delivers in-swingers; Digne for the left side.
- Direct FKs (18-25m): Mbappé or Olise takes anything centered; Dembélé curls from the right. Saliba and Upamecano stay back — France never commits 5 to a corner; counter risk too high (Morocco's transition through Hakimi and Brahim Díaz is dangerous).
- Defending corners & long throws: man-mark + 2 zonal at near post; double up on Morocco's aerial threats (Diop, Aguerd). Win the first contact, second balls cleared long. Mbappé stays on halfway for the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Upamecano/Saliba) and possession_team is mine, no pressure: pass short to other CB or the DM, never long unless a forward is in space.
3. When my `player_id` ends with `_5` (DM — Koné) and team has the ball: stay between CBs and the ball, offer constant short passing option, never above halfway; recycle and shield, only drive forward with the ball when it is won high and space opens ahead.
4. When my `player_id` ends with `_1` (LB — Digne) and team_phase is "attacking" and ball is on left side: advance to provide width and overlap for Barcola, but stay measured — do not over-commit against Hakimi's overlaps and Morocco's counter; deliver the left-sided cross.
5. When my `player_id` ends with `_4` (RB — Koundé) and team_phase is "attacking": tuck inside to RCM position (inverted FB), give Dembélé free room on the right.
6. When my `player_id` ends with `_7` (RW — Dembélé) and I receive ball isolated 1v1: drive at the defender, use explosive pace to beat on the outside or cut inside — invite the duel and shoot/cutback.
7. When my `player_id` ends with `_10` (CF — Mbappé) and team_phase is "defending": press the ball-carrying CB; cut the passing lane to their #6.
8. When my `player_id` ends with `_9` (LW — Barcola) and ball is regained in own half: explode diagonally into space behind opponent RB — demand the pass; run in behind first, feet second.
9. When my `player_id` ends with `_6` (DM/#8 — Rabiot) and team_phase is "defending": tuck into the double pivot beside Koné, never higher than the CM line until ball is won; cover the left channel when Digne is high.
10. When my `player_id` ends with `_8` (CAM — Olise) and team has the ball in the final third: find the half-space between lines, look first for the through ball to Mbappé or Barcola.
11. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_5` (Upamecano/Saliba/Koundé/Koné) AND ball-carrier has poor body shape; otherwise Hold and contain — Koné is on a booking, so he must contain rather than dive in.
12. When my team is leading by 1+ and clock > 70: drop into a 4-4-1-1 deep block; only the `_10` player (Mbappé) stays high as outball.
13. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_10` (Mbappé) inside the box.

## Key Player Notes
- **Mbappé (idx 10)** — captain, central striker. The focal point of the attack, primary finisher. Always the primary outlet on transitions. Shoot tendency aggressive; chasing goals to close on the tournament scoring lead.
- **Dembélé (idx 7)** — RW. Explosive dribbler, cuts inside from the right, stretches the defence with raw pace; set-piece deliverer from the right. Red-hot form off the Norway hat-trick.
- **Olise (idx 8)** — the creative hub at #10; receives between lines and supplies the killer pass; primary set-piece deliverer.
- **Barcola (idx 9)** — starts on the left of the front line in place of Doué; direct, quick and vertical, runs behind the line rather than combining short — a transition weapon against Morocco's back line.
- **Koné (idx 5)** — the deep anchor in for the injured Tchouaméni; a physical, high-energy ball-winner who covers ground and carries forward, but with less deep-passing range and no dead-ball duty. Shields the CBs and snuffs out Morocco's vertical counters before they launch. On a booking — must contain, not dive in.
- **Rabiot (idx 6)** — the disciplined other half of the double pivot; covers Koné, arrives late in the box, and patrols the channel Digne vacates.
- **Saliba (idx 3)** — ball-carrying CB; earlier back issue is resolved and he came through the group and knockouts fine. Allowed to drive into midfield when Koné steps up; Konaté is the like-for-like cover.
- **Digne (idx 1)** — controlled attacking LB in for Theo Hernández; secure in possession, provides measured width and the left-sided dead-ball delivery, less exposed on the counter.
- **Maignan (idx 0)** — set-piece and goal-kick distributor; takes risks with the ball.

## Tournament Mindset
Win the knockouts. France routinely peaks against top opponents — pragmatism + Mbappé in a single moment is enough. This is the quarterfinal: one game, win or go home, no second chances; if it is level after 90, thirty more of extra time, then a shootout. France are favourites — five wins from five, 14 scored / 2 conceded — but Morocco are unbeaten too, organised, quick in transition, and fresh off the last World Cup's semifinal run, so completely unafraid of the occasion. The plan: control possession, keep the clean sheet, break down a compact block with patience through the Olise-Dembélé right side and Barcola's runs on the left, and punish any over-commitment with Mbappé and Barcola in transition. Guard against Morocco's counters (Hakimi, Brahim Díaz) and their set pieces; win the midfield battle now that Koné, not Tchouaméni, anchors the pivot. Take the lead, then squeeze the game flat and see it out — however many whistles it takes.
