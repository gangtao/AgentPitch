# South Africa — Tactical Profile

## Identity & Philosophy
Hugo Broos has rebuilt Bafana Bafana into a confident, technically clean side that defends compactly and counters fluidly. Penalty-saving captain Ronwen Williams gives the team belief, and Relebohile Mofokeng's craft is the creative heartbeat. Modest individual quality, but excellent team structure.

**Round of 32 (28 June, vs Canada — SoFi Stadium, Los Angeles):** South Africa are into the World Cup knockout stage for the **first time in their history** — runners-up of Group A behind Mexico after battling back from an opening 0–2 loss to draw Czechia (a late Mokoena penalty) and beat South Korea 1–0 (Maseko, 63'). Now it is win-or-go-home. The big team-news boost: **Teboho Mokoena is back** from the one-match suspension that kept him out of the South Korea game — the deep-lying conductor, set-piece deliverer and the man who scored the Czechia penalty returns to anchor midfield, most likely in for **Sphephelo Sithole**. **Themba Zwane remains banned** for the tournament (red card vs Mexico). Broos keeps the front-foot **4-2-3-1** that served the must-win finale: a Mokoena–Mbatha double pivot behind a roaming **Mofokeng as the #10**, **Thapelo Maseko**'s pace on the right and **Lyle Foster** leading the line. Bafana sense a Canada side without the injured Koné and with Alphonso Davies only easing back from the bench — a genuine chance to make more history.

## Formation
- Shape: 4-2-3-1, double pivot screening a fluid attacking band; knockout, front-foot tilt.
- Role mapping (roster index -> tactical role):
  - index 0: GK — Ronwen Williams (captain, penalty-saver, leader)
  - index 1: LB — Aubrey Modiba (attacking, technical; pushes high)
  - index 2: LCB — Mbekezeli Mbokazi (physical, left center-back)
  - index 3: RCB — Ime Okon (tall, composed right center-back)
  - index 4: RB — Khuliso Mudau (balanced; overlaps to support the right)
  - index 5: LCM/pivot — Teboho Mokoena (returning deep-lying conductor & set-piece taker; the deeper screen and primary outlet alongside Mbatha; skill 15, pass 16)
  - index 6: RCM/pivot — Thalente Mbatha (energetic ball-winner, long-range threat; the runner of the pair, partners Mokoena)
  - index 7: AM/#10 — Relebohile Mofokeng (free creative role behind the striker; the team's young star, dribble 16)
  - index 8: LW — Oswin Appollis (direct left-sided dribbler)
  - index 9: CF — Lyle Foster (mobile target striker, shoot 15, primary penalty taker)
  - index 10: RW — Thapelo Maseko (pacey, vertical right winger, speed 16; stretches and runs in behind)

## Style of Play

### Build-up
- Williams comfortable distributing short to the center-backs.
- Center-backs split; one pivot (Mokoena) drops to form a 3+1 against pressure while Mbatha stays higher.
- Modiba pushes high on the left; Mudau more conservative but joins when South Africa chase the game.
- Mokoena dictates tempo from deep; Mofokeng drifts between the lines to receive and turn.

### Pressing
- Aggressive in a knockout: Foster and Mofokeng press the center-backs, the wingers (Appollis, Maseko) jump the full-backs.
- Trigger: opposition CB receives in poor body shape, or a square pass between CBs is in flight.
- Mokoena and Mbatha step on the opposition pivot; the double pivot gives license to press without exposing the back four.

### Defensive shape
- 4-2-3-1 / 4-4-2 mid-block out of possession; Mokoena and Mbatha shield the back four together.
- Center-backs hold a moderate line; full-backs tuck inside when the ball is opposite.
- Mofokeng and the strikers lead the first line of pressure; wingers track back to form a flat four when pinned.

### Wide play
- Left: Appollis attacks the channel and takes on his man 1v1; Modiba overlaps aggressively.
- Right: Maseko stretches the line with pace and runs in behind; Mudau supports underneath.
- Crosses target Foster's near-post runs and Mofokeng arriving at the edge of the box.

### Final third
- Mofokeng is the creative hub — as the #10 he conducts the final third, finding cutbacks and through balls.
- Foster runs the channels and attacks crosses; Maseko's pace threatens the space in behind.
- Appollis pressures and finishes secondary chances down the left; the pivots (especially Mbatha) arrive late for long-range strikes.

## Set Pieces
- With Mokoena back, **Mokoena** takes most attacking set pieces (corners and wide free kicks); Mofokeng and Mbatha are alternates.
- Mbokazi, Okon, and Foster are aerial targets.
- Williams's reputation makes set-piece defending a strength — he commands his box.
- Penalties: **Mokoena** (penalty 15, converted vs Czechia) is the primary taker; Foster (15) and Mofokeng (14) are the alternates.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Ronwen Williams): start attacks short to a center-back; long balls reserved for clear channel opportunities.
2. If player_id ends with "_5" (Mokoena, LCM pivot) or "_6" (Mbatha, RCM pivot) and opponent has the ball in midfield: tackle hard and screen the back four; the double pivot wins the ball and protects the defense.
3. If player_id ends with "_5" or "_6" and team has the ball: one pivot (player_id ends with "_5", Mokoena; skill 15, pass 16) sits deeper as the deep-lying conductor and primary outlet from defense, always facing forward; the other (player_id ends with "_6", Mbatha) supports forward and arrives late at the edge of the box for cutbacks.
4. If player_id ends with "_7" (Mofokeng, AM/#10; skill 15, dribble 16, pass 15): roam between the lines, receive and turn forward, dribble from the half-space, and feed the front three — this is the creative engine of a must-win game.
5. If player_id ends with "_8" (Appollis, LW #7): attack the left channel, dribble at the full-back, combine with the CF (player_id ends with "_9", Foster) and the #10 (player_id ends with "_7", Mofokeng).
6. If player_id ends with "_10" (Maseko, RW #40; speed 16): stretch the right flank, run in behind the full-back, and get to the byline to cross or cut back.
7. If player_id ends with "_9" (Foster, CF #9): run channels constantly; attack near-post on crosses; primary penalty taker.
8. If player_id ends with "_1" (Modiba, LB): overlap aggressively on the left to provide width and crosses.
9. If turnover in own half: counter-press for 4 seconds, then drop into the 4-2-3-1 / 4-4-2 mid-block.
10. If defending in own third: maintain block distances; Mokoena (player_id ends with "_5") and Mbatha (player_id ends with "_6") screen together in front of the back four.
11. If trailing late in a knockout: push both full-backs (Modiba "_1", Mudau "_4") high, keep Mokoena ("_5") deep as the outlet and send Mbatha (player_id ends with "_6") forward as an extra attacker, commit Mofokeng (player_id ends with "_7") into the box.
12. If a penalty is awarded against South Africa: trust the GK (player_id ends with "_0", Ronwen Williams) to save it — he is the team's saving grace.

## Key Player Notes
- **Ronwen Williams (save 16)** — captain and the spine of the side; his shot-stopping and penalty saves are SA's edge in tight games (still chasing his first World Cup clean sheet).
- **Relebohile Mofokeng (idx 7)** — the team's young star, freed as a roaming #10; give him license to dribble and create. Alternate set-piece and penalty taker.
- **Teboho Mokoena (idx 5)** — back from his one-match suspension; the deep-lying conductor (skill 15, pass 16), primary set-piece deliverer and penalty taker (scored vs Czechia). Without him the team loses shape — his return is the midfield upgrade for the knockout.
- **Thalente Mbatha (idx 6)** — energetic, two-way pivot with a long-range threat; the runner of the pair, arriving late in the box.
- **Thapelo Maseko (idx 10)** — pace and verticality on the right (speed 16); the man to run in behind and stretch a defense in a must-win.
- **Oswin Appollis (idx 8)** — the direct left-sided threat; let him run at his marker.
- **Lyle Foster (idx 9)** — mobile target striker and primary penalty taker; feed him through balls and channel runs.

## Tournament Mindset
History already made — a first-ever World Cup knockout — but Bafana arrive in Los Angeles believing there is more. The attacking 4-2-3-1 is built to create chances, with Mofokeng unleashed as a #10 and Maseko's pace stretching the game, and the return of **Mokoena** restores the side's calm and its set-piece edge. They will press, counter through their quick front line, and trust Ronwen Williams behind them. Zwane is still missed, but a steadier midfield and a Canada side missing Koné (and easing Davies back from the bench) hand South Africa a real opening. Bafana believe they are better than the world expects — and this is the night to prove it again.
