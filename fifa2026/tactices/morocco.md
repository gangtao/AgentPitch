# Morocco — Tactical Profile

## Identity & Philosophy
Mohamed Ouahbi's Morocco — who took over from Walid Regragui in March 2026 — carries forward the counter-attacking ferocity that powered the 2022 World Cup semi-final run, now built around a younger, more technical spine. They defend in a compact mid-block, then break vertically through Hakimi's overlap and the on-ball quality of Brahim Díaz, El Khannouss and Ounahi. The Atlas Lions came through Group C unbeaten, knocked out Ronald Koeman's Netherlands **on penalties** in the Round of 32 (June 29, Estadio BBVA, Monterrey) — Bounou the shootout hero with an innovative save — then swept aside co-hosts Canada **3-0** in the Round of 16 (July 4, Houston), Issa Diop and a stoppage-time Soufiane Rahimi strike among the goals. That extends Morocco's status as the ultimate tournament specialists and takes them to **consecutive World Cup quarter-finals for the first time in their history**. They remain **unbeaten across the whole tournament** (34 matches unbeaten in all) and have tightened with every game: through the knockouts they have faced just ~8 shots and ~0.8 xGA per match — the meanest defensive record of any edition. Two fitness doubts cloud the quarter-final: LCB **Chadi Riad** hurt his knee against the Netherlands, missed the Canada game and remains a doubt — **Redouane Halhal** deputised at left centre-back vs Canada and is the probable starter here. Leading scorer **Ismael Saibari** limped off after 22 minutes vs Canada with a hamstring/thigh problem; early word is it may not be severe, but he is racing the clock and **Rahimi is primed to start** if he fails to recover. Otherwise they are tournament-tested: disciplined, fearless, and ruthless on the transition. Next up is **France in the quarter-final (July 9, Boston)** — the world champions who ended Morocco's fairy-tale at the 2022 semi-final, so this is a shot at redemption against the tournament's most talented squad. Morocco are underdogs on paper but arrive with the meaner defence and the tie-turning nerve: frustrate France, deny Mbappé and Co. clean transitions, and strike on the break or from a set piece.

## Formation
- Shape: 4-2-3-1 — a double pivot screens the back four, an attacking three plays off a mobile lone striker. Morphs to a 4-4-2 / 4-5-1 mid-block out of possession.
- Role mapping (roster order in `morocco.yaml`):
  - index 0: GK — Yassine Bounou (sweeper-keeper, plays out from the back; first-choice "Bono")
  - index 1: LB — Noussair Mazraoui (left-back, tucks inside to support build-up; carried a shoulder knock into the tournament)
  - index 2: LCB — Redouane Halhal (left center-back; deputised here for the injured Aguerd and the knee-doubtful Riad, started vs Canada)
  - index 3: RCB — Issa Diop (right center-back, aerial enforcer)
  - index 4: RB — Achraf Hakimi (right-back / wingback, the overlapping bomber and tactical fulcrum)
  - index 5: LM / left #10 — Bilal El Khannouss (left of the attacking three, drifts inside to create; left-footed)
  - index 6: DM — Ayyoub Bouaddi (deep-lying pivot, 18-year-old ball-winner & screener; partners El Aynaoui)
  - index 7: DM — Neil El Aynaoui (box-to-box pivot, deep distributor and late-arriving runner)
  - index 8: CAM — Azzedine Ounahi (central attacking midfielder, half-space progressor and carrier)
  - index 9: RM / right #10 — Brahim Díaz (right of the attacking three, free-roaming primary creator)
  - index 10: CF — Ismael Saibari (mobile lone striker, drops to combine then runs the channels; tournament-leading 3 goals, Bayern Munich-bound — carrying a hamstring doubt into the QF, with Soufiane Rahimi primed to deputise)

## Style of Play

### Build-up
- Bounou splits the center-backs; one pivot (usually Bouaddi) drops in to form a back-three when pressed.
- Halhal and Diop start moves; Diop is the aerial outlet who switches to Hakimi, Halhal the left-sided ball-player who steps out from the back.
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
- Aerial targets: Diop, Halhal and Hakimi attack near/back posts; near-post flick + back-post arrival.
- Penalties / shootout order: Brahim Díaz first, Hakimi second, Soufiane Rahimi (bench) third. Bounou is a proven shootout stopper (saved to beat the Netherlands in R32).
- Defensive set pieces: zonal with a pivot (Bouaddi/El Aynaoui) picking up the late runner.

## decide() Decision Priorities
1. When my role is "GK" (`player_id` ends with `_0`, Bounou) and ball is in own penalty area unpressed: short pass to nearest CB; otherwise long diagonal to the RB (`_4`, Hakimi) or the CF (`_10`, Saibari).
2. When my role is "DEF" and `player_id` ends with `_2` (Halhal, LCB) and pressed by one striker: dribble-step forward; if pressed by two, pass to a dropping pivot (`_6` Bouaddi or `_7` El Aynaoui).
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
14. Knockout vs France (Quarter-final) — this is single-elimination, so there is no goal-difference incentive: a 1-0 is as good as a 4-0. Here Morocco are the **underdogs** against the world champions — France carry elite individual quality (Mbappé's pace in behind, a stacked midfield even without the injured Tchouaméni), so the discipline is non-negotiable. Sit in the compact mid-block, deny France the spaces between the lines, and above all protect the transition: do NOT over-commit numbers forward and gift France a break, especially down the flank behind the advanced `_4` (Hakimi), where Mbappé will look to attack the space. Absorb pressure, make them chase in the heat, and strike on one Hakimi-`_4`-fed counter, a Brahim `_9` moment, or a set piece. Bank any lead and defend it ruthlessly in the mid-block. Entirely comfortable taking the tie to extra time / penalties (Brahim `_9` first, Hakimi `_4` second, Rahimi third) — Bounou `_0` is a shootout weapon, and Morocco's nerve from the spot is their edge over any opponent.

## Key Player Notes
- **Hakimi (idx 4)** — the tactical fulcrum; route attacks through or past him. Stamina 18 sustains 90 minutes of overlap. Alternate penalty taker.
- **Brahim Díaz (idx 9)** — the creative engine and primary penalty taker; dribbling 18 means he should attempt 1v1s liberally and shoot from the right half-space.
- **El Khannouss (idx 5)** — left-footed dribbler/creator who started vs Brazil in place of the injured Ezzalzouli; drifts infield and shares dead-ball duties.
- **Saibari (idx 10)** — Bayern Munich-bound, operating as a mobile false-nine; tournament-leading 3 goals and Morocco's hottest finisher. Feed his near-post and channel runs relentlessly. Links play and finishes channel runs. Fitness doubt for the QF (hamstring off after 22 min vs Canada) — if he starts, manage his sprint load; if not, Rahimi takes the lone-striker role.
- **Bouaddi (idx 6)** — 18-year-old Lille pivot; composed beyond his years, the deepest ball-winner and screener.
- **El Aynaoui (idx 7)** — box-to-box partner in the double pivot; wins duels, recycles, and hits the deep switch (pass 16).
- **Bounou (idx 0)** — "Bono"; comfortable starting attacks with his feet — first option short to a CB, second a long diagonal to Hakimi.
- **Halhal (idx 2)** — 22-year-old left-sided centre-back (Mechelen); steps in at LCB with Aguerd out (pubalgia) and Riad a knee doubt after starting vs Canada. Composed on the ball; keep his distribution simple and let Diop lead the aerial duels.
- **Riad (idx 18, bench doubt)** — Crystal Palace centre-back and the usual LCB starter, but a knee injury from the Netherlands tie kept him out vs Canada and leaves him a doubt for France; Halhal deputises.
- **Rahimi (bench)** — Al Ain striker and third penalty-taker; came off the bench vs Canada to hit the crossbar and score in stoppage time, and is primed to start up top if Saibari's hamstring fails to recover.

## Tournament Mindset
Patient and ruthless on the transition; Morocco believes any match can be won 1-0 on a Hakimi assist and a Bounou clean sheet. Having come through Group C unbeaten, eliminated Koeman's Netherlands on penalties in the Round of 32 — Bounou the shootout hero — and then dispatched co-hosts Canada 3-0 in the last 16, the Atlas Lions reach the quarter-final as the meanest defence of the tournament (~0.8 xGA per game) and 34 matches unbeaten. The opponent now is **France**, the world champions — the same side that ended Morocco's dream in the 2022 semi-final, so this is redemption night. France are favourites on individual talent (Mbappé's threat in behind, a deep and star-studded squad, though missing the injured Tchouaméni), and Morocco carry their own doubts up front: Saibari's hamstring is touch-and-go and Riad's knee keeps Halhal at LCB. This is knockout football: no goal-difference incentive, so the plan is to stay compact, deny France clean transitions (mind the space behind the advanced Hakimi that Mbappé will attack), and strike through Hakimi, Brahim and whoever leads the line — Saibari or Rahimi — or from a set piece. They are entirely comfortable taking the tie deep — to extra time and penalties — where their nerve and Bounou's shot-stopping make them lethal (Brahim first, Hakimi second, Rahimi third). The mindset is fearless control: respect the champions, suffer when needed, avoid needless bookings, and trust one moment of Brahim or Hakimi quality — and a Bounou clean sheet — to settle it.
