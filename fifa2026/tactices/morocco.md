# Morocco — Tactical Profile

## Identity & Philosophy
Mohamed Ouahbi's Morocco — who took over from Walid Regragui in March 2026 — carries forward the counter-attacking ferocity that powered the 2022 World Cup semi-final run, now built around a younger, more technical spine. They defend in a compact mid-block, then break vertically through Hakimi's overlap and the on-ball quality of Brahim Díaz, El Khannouss and Ounahi. The Atlas Lions came through Group C unbeaten and finished second on seven points, level with Brazil and separated only on goal difference — Saibari the standout, scoring three group-stage goals. For the knockout, Ouahbi reverts to his strongest XI: Mazraoui, Diop, Bouaddi and Ounahi return after being rested late in the group, and Sofyan Amrabat drops to the bench. They are tournament-tested: disciplined, fearless, and ruthless on the transition. Now they meet Ronald Koeman's Netherlands in the Round of 32 (June 29, Estadio BBVA, Monterrey) — a heavyweight European side they will look to frustrate and hit on the break, just as they did the favourites in 2022.

## Formation
- Shape: 4-2-3-1 — a double pivot screens the back four, an attacking three plays off a mobile lone striker. Morphs to a 4-4-2 / 4-5-1 mid-block out of possession.
- Role mapping (roster order in `morocco.yaml`):
  - index 0: GK — Yassine Bounou (sweeper-keeper, plays out from the back; first-choice "Bono")
  - index 1: LB — Noussair Mazraoui (left-back, tucks inside to support build-up; carried a shoulder knock into the tournament)
  - index 2: LCB — Chadi Riad (left center-back, composed ball-player; in for the injured Aguerd)
  - index 3: RCB — Issa Diop (right center-back, aerial enforcer)
  - index 4: RB — Achraf Hakimi (right-back / wingback, the overlapping bomber and tactical fulcrum)
  - index 5: LM / left #10 — Bilal El Khannouss (left of the attacking three, drifts inside to create; left-footed)
  - index 6: DM — Ayyoub Bouaddi (deep-lying pivot, 18-year-old ball-winner & screener; partners El Aynaoui)
  - index 7: DM — Neil El Aynaoui (box-to-box pivot, deep distributor and late-arriving runner)
  - index 8: CAM — Azzedine Ounahi (central attacking midfielder, half-space progressor and carrier)
  - index 9: RM / right #10 — Brahim Díaz (right of the attacking three, free-roaming primary creator)
  - index 10: CF — Ismael Saibari (mobile lone striker, drops to combine then runs the channels; three group-stage goals, Bayern Munich-bound)

## Style of Play

### Build-up
- Bounou splits the center-backs; one pivot (usually Bouaddi) drops in to form a back-three when pressed.
- Riad and Diop start moves; Riad is the more progressive passer, Diop the aerial outlet who switches to Hakimi.
- Full-backs asymmetric: Hakimi pushes very high, Mazraoui tucks inside / inverts.
- Brahim Díaz and El Khannouss drop between the lines to receive on the half-turn.

### Pressing
- Trigger when the opposition center-back receives with a heavy first touch or back to play.
- Saibari presses the ball-side CB; the nearest wide #10 jumps the full-back; the pivots step onto the opponent's deepest midfielder.
- If the first press is bypassed, the team retreats immediately into a 4-4-2 / 4-5-1 mid-block — no chasing.

### Defensive shape
- Mid-block with the Bouaddi–El Aynaoui double pivot shielding the back four and a compact vertical gap between lines.
- The wide #10s (El Khannouss, Brahim) track back to make a flat four ahead of the pivots when defending deep.
- Center-backs hold the line; full-backs tuck in narrow when the ball is on the opposite flank.

### Wide play
- Right side: Hakimi overlap + Brahim inside = constant 2v1 overloads — Morocco's most dangerous channel.
- Left side: El Khannouss drifts inside off the left, Mazraoui underlaps or holds width depending on the ball location.
- Crosses are mostly cut-backs from the byline, targeting Saibari's near-post run and El Aynaoui's late arrival.

### Final third
- Look for Saibari's near-post / channel run on any cross or through-ball from a full-back.
- Brahim Díaz takes 1v1s on the right; encouraged to drive inside onto his stronger foot and shoot.
- Late midfield runs from El Aynaoui and Ounahi into the box.
- Recycle around the box rather than force low-percentage shots.

## Set Pieces
- Dead-ball delivery falls to El Khannouss, Ounahi, Hakimi and Brahim Díaz.
- Aerial targets: Diop, Riad and Hakimi attack near/back posts; near-post flick + back-post arrival.
- Penalties: Brahim Díaz is first taker (converted in qualifying); Hakimi is the alternate.
- Defensive set pieces: zonal with a pivot (Bouaddi/El Aynaoui) picking up the late runner.

## decide() Decision Priorities
1. When my role is "GK" (`player_id` ends with `_0`, Bounou) and ball is in own penalty area unpressed: short pass to nearest CB; otherwise long diagonal to the RB (`_4`, Hakimi) or the CF (`_10`, Saibari).
2. When my role is "DEF" and `player_id` ends with `_2` (Riad, LCB) and pressed by one striker: dribble-step forward; if pressed by two, pass to a dropping pivot (`_6` Bouaddi or `_7` El Aynaoui).
3. When `player_id` ends with `_6` or `_7` (pivots — Bouaddi / El Aynaoui) and team has the ball: never shoot from outside 25m; prioritize simple lateral passes that switch play to the RB (`_4`, Hakimi).
4. When `player_id` ends with `_4` (Hakimi, RB) and team has possession in midfield: sprint past the halfway line to offer the overlap — almost every attack routes through or past me.
5. When `player_id` ends with `_9` (Brahim Díaz, right #10): receive between lines on the half-turn; if 1v1 and inside the half-space, dribble inside onto the stronger foot and Shoot, OR play in the overlapping `_4` (Hakimi).
6. When `player_id` ends with `_5` (El Khannouss, left #10): drift inside off the left to combine; carry into the left half-space, then cut back or thread to the CF (`_10`, Saibari).
7. When `player_id` ends with `_8` (Ounahi, CAM): position between the lines in the ball-far half-space; on receiving, turn forward and carry — never backward.
8. When `player_id` ends with `_10` (Saibari, CF) and ball is wide near the byline: make a near-post run; if the cross is cut back, attack the penalty spot; drop short to link when build-up stalls.
9. When defending and the ball-side opponent has the ball: maintain mid-block distances, never break shape to dive in.
10. When turnover occurs in the opposition half: counter-press for ~5 seconds; if not won, drop into the mid-block.
11. When defending in own third: the nearest pivot (`_6` Bouaddi / `_7` El Aynaoui) tracks the central runner; the wide #10s (`_5`, `_9`) recover to flatten the midfield four.
12. When trailing in the final 15 minutes: the RB (`_4`, Hakimi) pushes onto the wing as a wingback and the LB (`_1`, Mazraoui) drops into a back-three to free numbers forward.
13. When leading by 1+ in the final 10 minutes against a superior or level opponent: drop the block ~5 meters deeper and prioritize ball circulation over progression.
14. Knockout vs Netherlands (Round of 32) — this is single-elimination, so there is no goal-difference incentive: a 1-0 is as good as a 4-0. Stay patient and compact against a technically superior side; do not over-commit numbers forward and gift the Dutch (Gakpo, Brobbey, Dumfries) the transition. Bank the lead and defend it — if the game goes level into the final stages, hold the mid-block and look to win it on one Hakimi-`_4`-fed counter or a set piece rather than chasing the game open. Comfortable taking the tie to extra time / penalties (Brahim `_9` first, Hakimi `_4` alternate).

## Key Player Notes
- **Hakimi (idx 4)** — the tactical fulcrum; route attacks through or past him. Stamina 18 sustains 90 minutes of overlap. Alternate penalty taker.
- **Brahim Díaz (idx 9)** — the creative engine and primary penalty taker; dribbling 18 means he should attempt 1v1s liberally and shoot from the right half-space.
- **El Khannouss (idx 5)** — left-footed dribbler/creator who started vs Brazil in place of the injured Ezzalzouli; drifts infield and shares dead-ball duties.
- **Saibari (idx 10)** — Bayern Munich-bound, operating as a mobile false-nine; three group-stage goals and Morocco's hottest finisher. Feed his near-post and channel runs relentlessly. Links play and finishes channel runs.
- **Bouaddi (idx 6)** — 18-year-old Lille pivot; composed beyond his years, the deepest ball-winner and screener.
- **El Aynaoui (idx 7)** — box-to-box partner in the double pivot; wins duels, recycles, and hits the deep switch (pass 16).
- **Bounou (idx 0)** — "Bono"; comfortable starting attacks with his feet — first option short to a CB, second a long diagonal to Hakimi.
- **Riad (idx 2)** — Crystal Palace center-back deputising for the injured Aguerd (pubalgia); the more progressive of the CB pair.

## Tournament Mindset
Patient against superior opponents, ruthless on the transition; Morocco believes any match can be won 1-0 on a Hakimi assist and a Bounou clean sheet. Having come through Group C unbeaten, the Atlas Lions now face Koeman's Netherlands in the Round of 32 — the kind of heavyweight European tie they thrive in, mirroring the 2022 run that ended in a semi-final. This is knockout football: no goal-difference incentive, so the game plan is to stay compact, deny the Dutch (Gakpo, Brobbey, Dumfries) clean transitions, and strike on the counter through Hakimi and Saibari or from a set piece. They are entirely comfortable taking the tie deep — to extra time and penalties — where their nerve (Hakimi's panenka vs Spain in 2022) and Bounou's shot-stopping make them dangerous. The mindset is fearless control: respect the opponent, suffer when needed, and trust one moment of Brahim or Hakimi quality to settle it.
