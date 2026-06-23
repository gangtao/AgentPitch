# South Korea — Tactical Profile

## Identity & Philosophy
Hong Myung-bo's South Korea is a high-energy, transitional side built around one of the great forwards of his generation, **Son Heung-min**, and one of the world's best centre-backs, **Kim Min-jae**. The team's identity is **box-to-box stamina + leader-driven moments of magic**: South Korea will out-run almost anyone over 90 minutes, win second balls all over the pitch, and rely on Son or Lee Kang-in to produce one decisive piece of skill per match. Hong's setup is more direct than Japan's positional game — fewer passes, faster verticality, more counter-attacks. For this World Cup Hong has committed to a **three-at-the-back system**, freeing the wing-backs to bomb forward while a compact midfield two screens the back line and Son leads the line as a roaming No. 9. Veterans Son and Kim Min-jae carry the leadership burden in what is almost certainly their final World Cup.

**Group A status (entering Matchday 3, 24 June, vs South Africa — Estadio BBVA, Monterrey/Guadalupe):** South Korea sit **2nd on 3 points** behind hosts Mexico, with Czechia and South Africa in the mix. A win over South Africa likely secures qualification to the knockouts. Hong has been consistent in selection — through the first two matches he made only one change (Kim Moon-hwan in for Lee Tae-seok at right wing-back vs Mexico). Son leads the attack as the lone striker, with Lee Kang-in and Lee Jae-sung as the two free attacking midfielders behind him.

## Formation
- Shape: **3-4-2-1** in possession (a back three, two wing-backs giving all the width, a central midfield double pivot, and two attacking midfielders — the "2" — floating behind Son as the lone striker). Drops into a compact **5-2-2-1 / 5-4-1** out of possession, the wing-backs tucking into a back five and the two No. 10s dropping alongside the central pair.
- Role mapping (roster order in `south_korea.yaml`):
  - index 0: GK — **Kim Seung-gyu** (#1) — experienced shot-stopper, commands his box, distributes short to start build-up; less of a modern sweeper-keeper.
  - index 1: LCB — **Lee Ki-hyuk** (#3) — left-sided centre-back of the three; steps wide to cover when Seol Young-woo overlaps, comfortable carrying into midfield.
  - index 2: CB — **Kim Min-jae** (#4) — captain of the defence, Bayern's monster, the central anchor of the back three and the team's leader on the pitch alongside Son. Steps into midfield, dominates aerially, wins almost every duel (strength 18).
  - index 3: RCB — **Lee Han-beom** (#2) — right-sided centre-back; covers behind the marauding Kim Moon-hwan, calm and positionally disciplined.
  - index 4: LWB — **Seol Young-woo** (#22) — quick, attacking left wing-back; in a back three he provides all the left-side width, getting up and down the touchline with the highest defensive stamina (17).
  - index 5: RWB — **Kim Moon-hwan** (#15) — energetic, hard-running right wing-back; provides the overlap on the right when Lee Kang-in drifts inside, high stamina (17).
  - index 6: CM — **Paik Seung-ho** (#8) — left-sided of the double pivot, ball-winner and progressor, screens in front of the back three alongside Hwang In-beom.
  - index 7: CM — **Hwang In-beom** (#6) — deep-lying playmaker, the screen, recycles possession and switches play with diagonals. Disciplined and stamina-rich (pass 16).
  - index 8: LAM — **Lee Jae-sung** (#10) — left of the attacking two; Mainz workhorse, the box-to-box engine, late runner into the box from deep, the team's stamina monster.
  - index 9: RAM — **Lee Kang-in** (#19) — right of the attacking two; the creative spark, drifts into the right half-space to combine, PSG-trained, technical, set-piece taker.
  - index 10: ST — **Son Heung-min** (#7) — captain, leads the line as a roaming No. 9, drops to link and breaks in behind on his pace, the team's leading goal-scorer for a decade. Penalty taker; conserved defensively for transitions.

## Style of Play

### Build-up
More direct than Japan but more patient than Iran. South Korea builds out of a back three, with the double pivot of Paik Seung-ho and Hwang In-beom dropping into pockets to receive. The chief progressor is Kim Min-jae — he steps out of the three with the ball or fires diagonals to the wing-backs pushed high. The first instinct is to find Lee Kang-in or Lee Jae-sung between the lines; the second option is a quick ball into Son's feet so he can turn and run. South Korea is happy to play long over the top when Son sprints in behind — his **speed of 18** makes that a constant threat.

### Pressing
**High-intensity, leader-driven, but selective** — South Korea presses on triggers (back-pass to GK, heavy first touch, throw-in in own half) rather than every possession. Son leads the press from the front, with Lee Kang-in and Lee Jae-sung jumping from the attacking band. Paik Seung-ho is the midfield jumper — he sprints to engage the opposition pivot. Son does NOT press for 90 minutes; he is rationed for transitions. The team's stamina ratings (the spine all 15+) make this sustainable across a World Cup match.

### Defensive shape
Drops into a compact **5-2-2-1**: the wing-backs (Seol Young-woo, Kim Moon-hwan) fold back to make a back five, Paik Seung-ho and Hwang In-beom as the central screen, and Lee Jae-sung and Lee Kang-in tucking in just ahead. Son stays high as the lone outlet. Kim Min-jae is licensed to step up aggressively from the centre of the three — he wins his duels because he is the strongest player on the pitch (strength 18), and the two flanking CBs (Lee Ki-hyuk, Lee Han-beom) cover behind him.

### Wide play
**Width comes from the wing-backs.** Left side: Seol Young-woo provides the overlapping width while Lee Jae-sung tucks inside. Right side: Kim Moon-hwan overlaps while Lee Kang-in drifts into the right half-space to combine. Both attacking midfielders funnel play centrally toward Son — South Korea is NOT a crossing team. They want shots from inside the 18-yard box, or the wing-back's cutback to a late runner.

### Final third
The chief patterns: Lee Kang-in's slipped through-ball to Son sprinting in behind, Son dropping to link then spinning into the channel, Kim Moon-hwan's cutback from the right by-line, Lee Jae-sung's late arrival into the box from deep. South Korea is a counter-attack monster — Son's 18 speed means three passes and a finish in under 10 seconds.

## Set Pieces
- Attacking corners: **Lee Kang-in** in-swingers from the right, **Son** out-swingers from the left. Aerial targets: Kim Min-jae (penalty spot), Lee Ki-hyuk / Lee Han-beom (posts), Lee Jae-sung (late runner).
- Defending corners: hybrid — Kim Min-jae attacks the first ball, zonal markers across the six-yard line, two man-markers on the most dangerous runners.
- Free kicks: Son direct from the left half-space, Lee Kang-in direct from the right half-space, Hwang In-beom and Kim Moon-hwan deliver wide free kicks into the box.
- Penalties: **Son** primary, **Lee Kang-in** secondary, **Lee Jae-sung** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_10" (ST Son Heung-min, #7) and I have the ball in or near the box:** Shoot if distance < 25 and angle is open. Otherwise dribble at the last defender, or lay off to the index-9 Lee Kang-in or index-8 Lee Jae-sung arriving.
2. **If my player_id ends with "_10" (ST Son, #7) and team_phase == "defending":** Stay high as the lone outlet; conserve stamina — do not press the opposition GK or CB unless they take a heavy touch within 8 units of me.
3. **If my player_id ends with "_2" (CB Kim Min-jae, #4) and team_phase == "defending":** Step up to engage any forward within 7 units. Win the duel — strength is 18. If beaten, the index-1 Lee Ki-hyuk and index-3 Lee Han-beom cover behind.
4. **If my player_id ends with "_8" (LAM Lee Jae-sung, #10) and I have the ball between the lines:** Look first for the index-10 Son's run in behind; second, slip the index-9 Lee Kang-in in the right half-space; third, dribble forward and arrive late in the box.
5. **If my role == "FWD" and team_phase == "transition_attack":** Sprint forward immediately — Son's pace (index-10) means counter-attacks resolve in 3-4 passes.
6. **If team_phase == "transition_defense":** Counter-press for 4 seconds; if ball not recovered, retreat into the 5-2-2-1 shape — wing-backs (index-4, index-5) drop to make a back five.
7. **If my player_id ends with "_7" (CM Hwang In-beom, #6) and I have the ball:** Look first for a forward diagonal to a high wing-back (index-4 Seol left, index-5 Kim Moon-hwan right) or a vertical ball to the index-9 Lee Kang-in / index-10 Son. Avoid sideways passes — South Korea plays vertically. The index-6 Paik Seung-ho stays as the holding partner.
8. **If my player_id ends with "_5" (RWB Kim Moon-hwan, #15) and team_phase == "attacking":** Overlap high on the right; deliver a cutback to the index-10 Son or a late runner rather than an aimless cross. Mirror on the left for the index-4 Seol Young-woo.
9. **If my player_id ends with "_9" (RAM Lee Kang-in, #19) and I have the ball:** Drift into the right half-space; look first for a through-ball to the index-10 Son sprinting in behind; Shoot if distance < 20.
10. **If team is trailing in the final 20 minutes:** Push both wing-backs (index-4 Seol, index-5 Kim Moon-hwan) permanently high as wingers; the index-8 Lee Jae-sung and index-9 Lee Kang-in both go higher to support Son; drop to a back three pressing aggressively.
11. **If my role == "GK" (index 0, Kim Seung-gyu, #1) and a corner is incoming:** Stay on the goal line; do not punch unless under direct physical pressure.
12. **Set-pieces inside 30 units of goal:** Defer to the index-9 Lee Kang-in (right half-space) or the index-10 Son (left half-space / penalties).

## Key Player Notes
- **Son (index 10):** Captain, leads the line as a roaming No. 9. Speed 18 makes him the team's outlet on every transition. Primary penalty taker, shoot 18.
- **Kim Min-jae (index 2):** The defensive captain and anchor of the back three. Strength 18, save-the-day duels. Licensed to step into midfield with the ball; flanked by Lee Ki-hyuk (index 1) and Lee Han-beom (index 3).
- **Lee Kang-in (index 9):** The creator of the attacking two. Drifts into the right half-space, takes set-pieces, slips through-balls. The technical superstar after Son; Lee Jae-sung (index 8) does the running alongside him.
- **Hwang In-beom (index 7):** The metronome. His pass accuracy (16) and vertical instincts make South Korea direct; pairs with Paik Seung-ho (index 6) in the double pivot.
- **Wing-backs (index 4 Seol Young-woo, index 5 Kim Moon-hwan):** The width of the whole side. Both run at stamina 17 and bomb the touchlines; in defence they fold into a back five.

## Tournament Mindset
South Korea always shows up at World Cups. This generation feels the weight of two unfinished projects — the 2022 round-of-16 run and the 2024 Asian Cup semi-final collapse — and Son is playing what is almost certainly his last tournament at 33/34. Sitting 2nd in Group A on 3 points, a win over South Africa on Matchday 3 likely books their place in the knockouts, and the team will play with **urgency**: high tempo, hard-running, leader-driven. The hidden weapon is stamina — the spine and both wing-backs run at 15+ stamina, so the third match in eight days is when they overrun a tired opponent. The vulnerability is the space in behind the high wing-backs — if a counter beats them before the back three can shuffle across, Son's defensive disinterest leaves the flanks exposed in transition.
