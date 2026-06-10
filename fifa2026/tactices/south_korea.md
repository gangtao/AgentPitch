# South Korea — Tactical Profile

## Identity & Philosophy
Hong Myung-bo's South Korea is a high-energy, transitional side built around one of the great wide forwards of his generation, **Son Heung-min**, and one of the world's best centre-backs, **Kim Min-jae**. The team's identity is **box-to-box stamina + leader-driven moments of magic**: South Korea will out-run almost anyone over 90 minutes, win second balls all over the pitch, and rely on Son or Lee Kang-in to produce one decisive piece of skill per match. Hong's setup is more direct than Japan's positional game — fewer passes, faster verticality, more counter-attacks. Recent form: unbeaten through AFC third-round qualifying (six wins, four draws), the 2024 Asian Cup semi-final exit still motivating, with veterans Son and Kim Min-jae carrying the leadership burden in what is almost certainly their final World Cup. South Korea sit in Group A with hosts Mexico, South Africa and Czechia.

## Formation
- Shape: **4-2-3-1** in possession (the formation Hong rode through qualifying — a double pivot behind a creative band of three, with Son tucking in from the left). Morphs to a compact **4-4-1-1 / 4-2-3-1 mid-block** out of possession, with the double pivot screening and Son dropping onto the left of the midfield four.
- Role mapping (roster order in `south_korea.yaml`):
  - index 0: GK — **Kim Seung-gyu** — experienced shot-stopper, commands his box, distributes short to start build-up; less of a modern sweeper-keeper.
  - index 1: LB — **Seol Young-woo** — quick, attacking fullback, the natural width-giver on the left because Son cuts inside; the highest-stamina defender, gets up and down the touchline.
  - index 2: LCB — **Kim Min-jae** — captain of the defence, Bayern's monster, the team's leader on the pitch alongside Son. Steps into midfield, dominates aerially, wins almost every duel.
  - index 3: RCB — **Kim Tae-hyeon** — calm, positionally disciplined partner; covers Kim Min-jae's aggressive stepping forward, holds the back line.
  - index 4: RB — **Lee Tae-seok** — energetic, hard-running fullback; provides the overlap on the right when Lee Kang-in drifts inside.
  - index 5: DM/6 — **Paik Seung-ho** — left-sided pivot, ball-winner and progressor, screens in front of the back four alongside Hwang In-beom.
  - index 6: DM/6 — **Hwang In-beom** — deep-lying playmaker, the screen, recycles possession and switches play with diagonals. Disciplined and stamina-rich.
  - index 7: LAM/LW — **Son Heung-min** — captain, free role from the left, cuts inside on his right foot, the team's leading goal-scorer for a decade. Conserved defensively for transitions.
  - index 8: CAM/10 — **Lee Jae-sung** — Mainz workhorse, the box-to-box engine in the middle of the three, late runner into the box from deep, the team's stamina monster.
  - index 9: RAM/RW — **Lee Kang-in** — the creative spark on the right, drifts into the right half-space to combine with Son cutting inside from the left. PSG-trained, technical, set-piece taker.
  - index 10: CF — **Oh Hyeon-gyu** — the lone target forward, holds the ball up, finishes inside the box, presses from the front.

## Style of Play

### Build-up
More direct than Japan but more patient than Iran. South Korea builds with the double pivot of Paik Seung-ho and Hwang In-beom in front of the back four, one of them dropping between the CBs only when the press is intense. The chief progressor is Kim Min-jae — he steps into midfield with the ball or fires diagonals to Son on the left flank. The first instinct is to find Son between the lines; if Son is marked, the second option is Lee Kang-in dropping deep to receive and turn. South Korea is happy to play long over the top when Son sprints in behind — his **speed of 18** makes that a constant threat.

### Pressing
**High-intensity, leader-driven, but selective** — South Korea presses on triggers (back-pass to GK, heavy first touch, throw-in in own half) rather than every possession. Oh leads the press from the front, with Lee Kang-in and Son curving in from the wide attacking positions. Paik Seung-ho is the midfield jumper — he sprints 15 yards to engage the opposition pivot. Son does NOT press for 90 minutes; he is rationed for transitions. The team's stamina ratings (the spine all 15+) make this sustainable across a World Cup match.

### Defensive shape
Drops into a compact **4-4-1-1** with Paik Seung-ho and Hwang In-beom as the central screen, Son and Lee Kang-in tucking back as the wide midfielders in a flat four, and Lee Jae-sung floating just ahead as the link. Oh Hyeon-gyu stays high as the lone press target. Kim Min-jae is licensed to step up aggressively — he wins his duels because he is the strongest player on the pitch (strength 18).

### Wide play
**Asymmetric.** Left side: Son cuts inside from the touchline into the right half-space, Seol Young-woo overlaps as the natural width-giver. Right side: Lee Kang-in drifts inside to combine, with Lee Tae-seok providing the overlap. Both flanks funnel attacks centrally — South Korea is NOT a crossing team. They want shots from inside the 18-yard box.

### Final third
The chief patterns: Son's cut-inside curler from the left half-space (right foot), Lee Kang-in's slipped through-ball to Son sprinting in behind, Oh's near-post header from a Seol Young-woo cross, Lee Jae-sung's late arrival into the box from central midfield. South Korea is a counter-attack monster — Son's 18 speed means three passes and a finish in under 10 seconds.

## Set Pieces
- Attacking corners: **Lee Kang-in** in-swingers from the right, **Son** out-swingers from the left. Aerial targets: Kim Min-jae (penalty spot), Oh (near post), Kim Tae-hyeon (back post), Lee Jae-sung (late runner).
- Defending corners: hybrid — Kim Min-jae attacks the first ball, four zonal markers across the six-yard line, two man-markers on the most dangerous runners.
- Free kicks: Son direct from the left half-space, Lee Kang-in direct from the right half-space, Hwang In-beom and Lee Tae-seok deliver wide free kicks into the box.
- Penalties: **Son** primary, **Lee Kang-in** secondary, **Oh Hyeon-gyu** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_7" (LAM/LW Son Heung-min, #7) and I have the ball on the left flank:** Dribble diagonally inside toward the right half-space; Shoot if distance < 25 and angle is open. Otherwise Pass to the index-10 Oh's near-post run or the index-8 Lee Jae-sung's late run.
2. **If my player_id ends with "_7" (LAM/LW Son, #7) and team_phase == "defending":** Drop to LM, but conserve stamina — do not press the opposition GK or CB unless they take a heavy touch within 8 units of me.
3. **If my player_id ends with "_2" (LCB Kim Min-jae, #4) and team_phase == "defending":** Step up to engage any forward within 7 units. Win the duel — strength is 18. If beaten, the index-3 Kim Tae-hyeon covers behind.
4. **If my player_id ends with "_8" (CAM Lee Jae-sung, #10) and I have the ball between the lines:** Look first for the index-7 Son's run in behind on the left; second, slip the index-9 Lee Kang-in in the right half-space; third, dribble forward.
5. **If my role == "FWD" and team_phase == "transition_attack":** Sprint forward immediately — Son's pace (index-7) means counter-attacks resolve in 3-4 passes.
6. **If team_phase == "transition_defense":** Counter-press for 4 seconds; if ball not recovered, retreat into the 4-4-1-1 shape.
7. **If my player_id ends with "_6" (DM Hwang In-beom, #6) and I have the ball:** Look first for a forward diagonal to the index-7 Son (left) or the index-9 Lee Kang-in (right). Avoid sideways passes — South Korea plays vertically. The index-5 Paik Seung-ho stays as the holding partner behind me.
8. **If my player_id ends with "_10" (CF Oh Hyeon-gyu, #18) and the ball is in the opposition box:** Position at the near post for a header from the index-1 Seol Young-woo's cross.
9. **If my player_id ends with "_9" (RAM Lee Kang-in, #19) and I have the ball:** Drift into the right half-space; look first for a through-ball to the index-7 Son or index-10 Oh sprinting in behind; Shoot if distance < 20.
10. **If team is trailing in the final 20 minutes:** Push the index-4 Lee Tae-seok and index-1 Seol Young-woo high as wingbacks; the index-9 Lee Kang-in and index-7 Son both go high; the index-8 Lee Jae-sung becomes the lone 10 behind a front three.
11. **If my role == "GK" (index 0, Kim Seung-gyu, #1) and a corner is incoming:** Stay on the goal line; do not punch unless under direct physical pressure.
12. **Set-pieces inside 30 units of goal:** Defer to the index-7 Son (left half-space) or the index-9 Lee Kang-in (right half-space).

## Key Player Notes
- **Son (index 7):** Captain, free role, cuts inside from the left. Speed 18 makes him the team's outlet on every transition. Penalty taker.
- **Kim Min-jae (index 2):** The defensive captain. Strength 18, save-the-day duels. Licensed to step into midfield with the ball.
- **Lee Kang-in (index 9):** The creator on the right of the band. Drifts into the right half-space, takes set-pieces, slips through-balls. The other technical superstar after Son; Lee Jae-sung (index 8) does the running that frees him.
- **Hwang In-beom (index 6):** The metronome. His pass accuracy (16) and vertical instincts make South Korea direct; pairs with Paik Seung-ho (index 5) in the double pivot.
- **Oh Hyeon-gyu (index 10):** The lone CF whose job is to occupy both CBs and finish from inside the box. Less of a hold-up player than a goal-poacher.

## Tournament Mindset
South Korea always shows up at World Cups. This generation feels the weight of two unfinished projects — the 2022 round-of-16 run and the 2024 Asian Cup semi-final collapse — and Son is playing what is almost certainly his last tournament at 33/34. The team plays with **urgency**: high tempo, hard-running, leader-driven. They will get behind early in matches against South American or European elites and come back with two Son goals in the final 30 minutes. The hidden weapon is stamina — the spine runs at 15+ stamina, so the third match in eight days will be when they overrun a tired opponent. The vulnerability is on the wide flanks against a true overlapping fullback — Son's defensive disinterest leaves Seol Young-woo exposed behind him.
