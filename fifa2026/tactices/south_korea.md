# South Korea — Tactical Profile

## Identity & Philosophy
Hong Myung-bo's South Korea is a high-energy, transitional 4-3-3 built around one of the great wide forwards of his generation, **Son Heung-min**, and one of the world's best centre-backs, **Kim Min-jae**. The team's identity is **box-to-box stamina + leader-driven moments of magic**: South Korea will out-run almost anyone over 90 minutes, win second balls all over the pitch, and rely on Son or Lee Kang-in to produce one decisive piece of skill per match. Hong's 4-3-3 is more direct than Japan's positional game — fewer passes, faster verticality, more counter-attacks. Recent form: comfortable through AFC qualifying, the 2024 Asian Cup semi-final exit still motivating, with veterans Son and Kim Min-jae carrying the leadership burden in what is almost certainly their final World Cup.

## Formation
- Shape: **4-3-3** in possession (morphs to **4-1-4-1** out of possession with Hwang In-beom dropping deepest and Son tucking inside to form a flat midfield five).
- Role mapping (roster order in `south_korea.yaml`):
  - index 0: GK — **Jo Hyeon-woo** — Asian Cup hero, traditional shot-stopper, less of a sweeper than modern keepers, dominates his box.
  - index 1: LB — **Kim Jin-su** — overlapping fullback, the natural width-giver on the left because Son cuts inside; veteran, set-piece deliverer.
  - index 2: LCB — **Kim Min-jae** — captain of the defence, PSG's monster, the team's leader on the pitch alongside Son. Steps into midfield, dominates aerially, wins almost every duel.
  - index 3: RCB — **Kim Young-gwon** — calm partner, sweeper-style, covers Kim Min-jae's aggressive stepping forward.
  - index 4: RB — **Kim Moon-hwan** — energetic, hard-running, more defensive than overlapping; provides width when Hwang Hee-chan/Oh stay central.
  - index 5: DM/6 — **Hwang In-beom** — deep-lying playmaker, the screen, recycles possession and switches play with diagonals. Disciplined and stamina-rich.
  - index 6: AM/10 — **Lee Kang-in** — the creative spark, the #10 in all but name, drifts to the right half-space to combine with Son cutting inside from the left. PSG-trained, technical, set-piece taker.
  - index 7: LCM/8 — **Lee Jae-sung** — Mainz workhorse, the box-to-box engine, late runner into the box from deep, the team's stamina monster.
  - index 8: LW — **Son Heung-min** — captain, free role from the left, cuts inside on his right foot, the team's leading goal-scorer for a decade. Conserved defensively for transitions.
  - index 9: CF — **Oh Hyeon-gyu** — the target forward, holds the ball up, finishes inside the box, presses from the front.
  - index 10: RW — **Hwang Hee-chan** — pacy, direct, cuts inside on his left foot from the right; can rotate with Oh into a fluid front three.

## Style of Play

### Build-up
More direct than Japan but more patient than Iran. South Korea builds in a **4-3-shape** with Hwang In-beom dropping between the CBs only when the press is intense. The chief progressor is Kim Min-jae — he steps into midfield with the ball or fires diagonals to Son on the left flank. The first instinct is to find Son between the lines; if Son is marked, the second option is Lee Kang-in dropping deep to receive and turn. South Korea is happy to play long over the top when Son sprints in behind — his **speed of 18** makes that a constant threat.

### Pressing
**High-intensity, leader-driven, but selective** — South Korea presses on triggers (back-pass to GK, heavy first touch, throw-in in own half) rather than every possession. Oh leads the press from the front, with Hwang Hee-chan and Son curving in from the wings. Lee Jae-sung is the midfield jumper — he sprints 15 yards to engage the opposition pivot. Son does NOT press for 90 minutes; he is rationed for transitions. The team's stamina ratings (all 15+) make this sustainable across a World Cup match.

### Defensive shape
Drops into a **4-1-4-1** with Hwang In-beom alone as the screen, Lee Jae-sung and Lee Kang-in forming the inside-midfield duo, and Son and Hwang Hee-chan as the wide midfielders in a flat four. Oh Hyeon-gyu stays high as the lone press target. Kim Min-jae is licensed to step up aggressively — he wins his duels because he is the strongest player on the pitch (strength 18).

### Wide play
**Asymmetric.** Left side: Son cuts inside from the touchline into the right half-space, Kim Jin-su overlaps as the natural width-giver. Right side: Hwang Hee-chan also cuts inside on his left foot, with Kim Moon-hwan providing the underlap. Both flanks funnel attacks centrally — South Korea is NOT a crossing team. They want shots from inside the 18-yard box.

### Final third
The chief patterns: Son's cut-inside curler from the left half-space (right foot), Lee Kang-in's slipped through-ball to Son sprinting in behind, Oh's near-post header from a Kim Jin-su cross, Hwang Hee-chan's drift inside to combine with Lee Kang-in. South Korea is a counter-attack monster — Son's 18 speed means three passes and a finish in under 10 seconds.

## Set Pieces
- Attacking corners: **Lee Kang-in** in-swingers from the right, **Son** out-swingers from the left. Aerial targets: Kim Min-jae (penalty spot), Oh (near post), Lee Jae-sung (back post late runner).
- Defending corners: hybrid — Kim Min-jae attacks the first ball, four zonal markers across the six-yard line, two man-markers on the most dangerous runners.
- Free kicks: Son direct from the left half-space, Lee Kang-in direct from the right half-space, Kim Jin-su wide free kicks into the box.
- Penalties: **Son** primary, **Lee Kang-in** secondary, **Hwang Hee-chan** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_8" (LW Son Heung-min, #7) and I have the ball on the left flank:** Dribble diagonally inside toward the right half-space; Shoot if distance < 25 and angle is open. Otherwise Pass to the index-9 Oh's near-post run or the index-7 Lee Jae-sung's late run.
2. **If my player_id ends with "_8" (LW Son, #7) and team_phase == "defending":** Drop to LM, but conserve stamina — do not press the opposition GK or CB unless they take a heavy touch within 8 units of me.
3. **If my player_id ends with "_2" (LCB Kim Min-jae, #4) and team_phase == "defending":** Step up to engage any forward within 7 units. Win the duel — strength is 18. If beaten, the index-3 Kim Young-gwon covers behind.
4. **If my player_id ends with "_6" (AM Lee Kang-in, #18) and I have the ball between the lines:** Look first for the index-8 Son's run in behind on the left; second, dribble forward; third, Shoot if distance < 20.
5. **If my role == "FWD" and team_phase == "transition_attack":** Sprint forward immediately — Son's pace (index-8) means counter-attacks resolve in 3-4 passes.
6. **If team_phase == "transition_defense":** Counter-press for 4 seconds; if ball not recovered, retreat into the 4-1-4-1 shape.
7. **If my player_id ends with "_5" (DM Hwang In-beom, #6) and I have the ball:** Look first for a forward diagonal to the index-8 Son (left) or the index-10 Hwang Hee-chan (right). Avoid sideways passes — South Korea plays vertically.
8. **If my player_id ends with "_9" (CF Oh Hyeon-gyu, #16) and the ball is in the opposition box:** Position at the near post for a header from the index-1 Kim Jin-su's cross.
9. **If my player_id ends with "_7" (LCM Lee Jae-sung, #17) and the index-6 Lee Kang-in has the ball:** Make a late forward run from deep — I am the box-arrival threat.
10. **If team is trailing in the final 20 minutes:** Push the index-4 Kim Moon-hwan and index-1 Kim Jin-su high as wingbacks; the index-10 Hwang Hee-chan and index-8 Son both go high; the index-6 Lee Kang-in becomes the lone 10 behind a front three.
11. **If my role == "GK" (index 0, Jo Hyeon-woo, #1) and a corner is incoming:** Stay on the goal line; do not punch unless under direct physical pressure.
12. **Set-pieces inside 30 units of goal:** Defer to the index-8 Son (left half-space) or the index-6 Lee Kang-in (right half-space).

## Key Player Notes
- **Son (8):** Captain, free role, cuts inside from the left. Speed 18 makes him the team's outlet on every transition. Penalty taker.
- **Kim Min-jae (2):** The defensive captain. Strength 18, save-the-day duels. Licensed to step into midfield with the ball.
- **Lee Kang-in (6):** The creator. Drifts to the right half-space, takes set-pieces, slips through-balls. The other technical superstar after Son.
- **Hwang In-beom (5):** The metronome. His pass accuracy (16) and vertical instincts make South Korea direct.
- **Oh Hyeon-gyu (9):** The CF whose job is to occupy both CBs and finish from inside the box. Less of a hold-up player than a goal-poacher.

## Tournament Mindset
South Korea always shows up at World Cups. This generation feels the weight of two unfinished projects — the 2022 round-of-16 run and the 2024 Asian Cup semi-final collapse — and Son is playing what is almost certainly his last tournament at 33/34. The team plays with **urgency**: high tempo, hard-running, leader-driven. They will get behind early in matches against South American or European elites and come back with two Son goals in the final 30 minutes. The hidden weapon is stamina — every outfielder is 15+ in stamina, so the third match in eight days will be when they overrun a tired opponent. The vulnerability is on the wide flanks against a true overlapping fullback — Son's defensive disinterest leaves Kim Jin-su exposed.
