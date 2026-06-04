# Qatar — Tactical Profile

## Identity & Philosophy
Qatar are the **back-to-back AFC Asian Cup champions (2019, 2024)** and the most underrated tactical side in Asia. They are now coached by **Julen Lopetegui** (appointed to lead the 2026 World Cup project), who has reshaped the team around a **possession-based 4-3-3 with a high defensive line and quick combinations through midfield** — a deliberate evolution from the compact 5-3-2 of the Asian Cup years. The core identity inherited from the Aspire Academy generation remains: **technical cohesion, intelligent positional rotation, lethal attacking via Akram Afif**. What Lopetegui adds is a more proactive, on-the-ball team that wants to dominate possession against peers and still counter ruthlessly against superiors. Backed by Aspire Academy's decade-long development of the entire starting XI as a single generation, Qatar plays like a club side — they know each other's movements instinctively. Recent form: 2024 Asian Cup champions, comfortable through World Cup qualifying, hosting experience from 2022 gives them tournament composure. Captain Hassan Al-Haydos (Qatar's most-capped player) returned from retirement at Lopetegui's request to add leadership.

## Formation
- Shape: **4-3-3** in possession (rotates to a **4-2-3-1** when Al-Haydos tucks inside and Afif holds width; defensive shape is a compact **4-5-1** with the wide forwards dropping to form a midfield five and Almoez leading the line alone).
- Role mapping (roster order in `qatar.yaml`):
  - index 0: GK — **Meshaal Barsham** — 2022 World Cup keeper, reflex shot-stopper, less of a sweeper, dominates his box.
  - index 1: LB — **Homam Ahmed** — left-back; hard-running, overlaps to give width on the left so Afif can drift inside.
  - index 2: LCB — **Lucas Mendes** — naturalised Brazilian-born CB, left-of-centre, the most technical defender and the chief ball-progressor from the back.
  - index 3: RCB — **Boualem Khoukhi** — veteran centre-back, aerial duel-winner, the organiser of the line and a set-piece threat.
  - index 4: RB — **Pedro Miguel** — experienced right-back, near-100-cap veteran, disciplined defender who overlaps to support Al-Haydos on the right.
  - index 5: LCM — **Abdulaziz Hatem** — the veteran connector, left-of-centre in the midfield three, drifts into the left half-space to combine with Afif and Homam Ahmed.
  - index 6: DM — **Assim Madibo** — the destroyer, the screen, the disciplined ball-winner who shields the back four and recycles possession.
  - index 7: RCM — **Karim Boudiaf** — the physical box-to-box presence, the second presser and the late runner from the right side of midfield.
  - index 8: LW — **Akram Afif** — the star, 2023 Asian Cup Golden Ball winner and two-time Asian Player of the Year, the team's creator and finisher. Plays from the left, cutting inside onto his right onto the #10 space to receive between the lines. Skill 16, dribbling 16, shoot 15.
  - index 9: CF — **Almoez Ali** — Qatar's all-time leading scorer and the focal point. The poacher and target man who runs the channels, attacks crosses, and finishes the chances Afif and Al-Haydos create. Shoot 16, strength 14.
  - index 10: RW — **Hassan Al-Haydos** — the captain and most-capped player. A clever, two-footed wide forward who comes inside to create, links midfield to attack, and arrives late in the box. Pass 15.

## Style of Play

### Build-up
Patient and positional under Lopetegui. Qatar builds from the back in a **2-3 / 3-2 shape**: the centre-backs Mendes and Khoukhi split, the full-backs (Homam Ahmed, Pedro Miguel) step up, and Madibo drops as a screen between the centre-backs to make a back three when needed. The chief progressor is Mendes — he carries the ball into midfield with the most technical CB profile. Afif drifts inside from the left to receive between the opposition lines — when he gets the ball facing forward in space, Qatar is dangerous. Against a high press the team can still go long to Almoez to run the channel or to hold up for runners.

### Pressing
**Mid-block with a Lopetegui-style aggressive trigger press.** Qatar sets in a 4-5-1 around the halfway line and presses on triggers: opposition GK takes a heavy touch, back-pass under duress, throw-in, loose first touch. Almoez leads the front press; Afif and Al-Haydos curve their runs to shut the wide build-up; Boudiaf and Hatem jump from midfield while Madibo holds. The press is coordinated and Aspire-trained — every player knows their cover-shadow. Out of possession against superior sides, Qatar prioritizes **compact numerical superiority** over chasing.

### Defensive shape
Compact **4-5-1** with the wide forwards (Afif left, Al-Haydos right) dropping to form a midfield five alongside Hatem-Madibo-Boudiaf, and Almoez leading the line alone. The back four stays narrow and deep; the full-backs (Homam Ahmed, Pedro Miguel) tuck in to deny half-space runs. This block is famously hard to break down — the Aspire generation conceded only 1 goal in 6 matches at the 2023 Asian Cup. Afif rarely tracks back hard, so the left-back and Hatem must cover behind him.

### Wide play
Width comes from the **overlapping full-backs and the inverted wide forwards**. On the left, Afif drifts inside and Homam Ahmed overlaps outside him; on the right, Al-Haydos comes inside to combine and Pedro Miguel provides the overlap. Crosses arrive from the full-backs and cut-backs from the wide forwards; Almoez attacks the near post and penalty spot. Qatar is comfortable switching play with long diagonals from Mendes to the opposite full-back.

### Final third
Patterns: **Afif drifts in from the left, receives between the lines, dribbles inside, shoots or slips a through-ball to Almoez**. Cut-back from Pedro Miguel's right-side overlap to Al-Haydos or Boudiaf arriving late. Homam Ahmed's deep cross to Almoez at the back post. Afif's signature move: receive on the half-turn, dribble past two defenders, finish low to the far corner. Almoez's poacher instinct turns half-chances into goals in the box.

## Set Pieces
- Attacking corners: **Afif** in-swingers from the right (left foot), **Al-Haydos** out-swingers from the left. Targets: Almoez (penalty spot, primary aerial), Khoukhi (back post), Mendes (near post flick-on).
- Defending corners: hybrid — Khoukhi attacks the first ball; Almoez and Mendes mark the two most dangerous opposition runners; zonal markers across the six-yard line; Barsham on his line.
- Free kicks: **Afif** direct from any angle within 28 yards; he scored from a direct free kick against Lebanon in the 2023 Asian Cup.
- Penalties: **Afif** primary, **Almoez** secondary, **Al-Haydos** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_8" (LW Afif, #19) and team_phase == "attacking":** Drift inside from the left into the #10 space between the opposition lines, 8-12 units behind the index-9 Almoez. Receive on the half-turn.
2. **If my player_id ends with "_8" (LW Afif, #19) and I have the ball facing forward in the opposition half:** Dribble — skill 16, dribbling 16. Take on the first defender; Shoot if angle opens within 24 units.
3. **If my role == "GK" (index 0, Meshaal Barsham, #22) and a cross is incoming:** Punch under physical pressure; otherwise stay on the line.
4. **If my player_id ends with "_1" (LB Homam Ahmed, #14) or "_4" (RB Pedro Miguel, #2) and team_phase == "attacking":** Overlap to the touchline in the opposition's defensive third — the full-backs supply width while the wide forwards (index-8 Afif, index-10 Al-Haydos) tuck inside.
5. **If my player_id ends with "_1" or "_4" (full-backs) and team_phase == "defending":** Tuck inside and stay narrow next to the CBs to deny the half-spaces; keep a compact back four.
6. **If my player_id ends with "_6" (DM Madibo, #12) and the opposition has the ball within 35 units of my goal:** Step to the ball-carrier, tactical foul if breaking through; otherwise screen in front of the back four.
7. **If team_phase == "transition_attack":** Index-8 Afif sprints into the left half-space to receive; index-9 Almoez runs the channel behind the CBs; index-10 Al-Haydos and the ball-side full-back sprint forward for width.
8. **If my player_id ends with "_9" (CF Almoez, #18) and the index-8 Afif has the ball:** Make a channel-run behind the opposition CBs OR pin the last defender and attack the cut-back / near post.
9. **If team is trailing by 1 in the final 15 minutes:** Push to a front-heavy **4-2-3-1**: index-10 Al-Haydos and index-8 Afif stay high and wide, index-5 Hatem pushes up as the lone #10 behind index-9 Almoez, full-backs overload the flanks.
10. **If a defensive corner is incoming:** The index-3 Khoukhi marks the most dangerous opposition striker; the index-2 Mendes and index-9 Almoez mark zonal; the index-8 Afif stays on the halfway line as a counter-outlet.
11. **If my role == "DEF" and team_phase == "attacking":** The index-2 Mendes carries the ball into midfield (the most technical CB); the index-3 Khoukhi stays deep as cover; the full-backs push high.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-8 Afif (left-footed in-swingers, direct free kicks).

## Key Player Notes
- **Afif (8):** The 2023 Asian Cup Golden Ball winner and two-time Asian Player of the Year. The creator and finisher. The inverted left winger who drifts between the lines. The team's only world-class technical player.
- **Almoez (9):** Qatar's all-time leading scorer. The focal-point striker — poacher, channel-runner, aerial threat in the box. Shoot 16, strength 14.
- **Al-Haydos (10):** The captain and most-capped player; returned from retirement at Lopetegui's request. Two-footed wide creator who comes inside to link play and arrive late. Pass 15.
- **Mendes (2):** The technical CB. Naturalised Brazilian, the ball-progressor from the back four.
- **Khoukhi (3):** The veteran CB. Aerial duel-winner, line organiser, and set-piece threat at both ends.
- **Madibo (6):** The screen. Tactical fouler. Recycles possession in front of the back four.

## Tournament Mindset
Qatar are the AFC-champion sleeper. They are not pre-tournament favourites to escape a World Cup group (Group B with Switzerland, Canada, and Bosnia and Herzegovina), but their tactical discipline, Aspire-trained cohesion, Lopetegui's structure, and Afif's individual brilliance make them dangerous. The mentality under Lopetegui is **be competitive, enjoy it, don't feel the pressure** — a proactive, possession-minded version of the team. They will trust the shape, trust Afif, and let Almoez finish the chances. The vulnerability is **goal-scoring depth against elite opposition** — if Afif and Almoez are marked out, the secondary creators (Al-Haydos, Hatem) must step up. Qatar's defensive solidity in the compact **4-5-1** remains its hidden weapon: against a top-eight side they aim to keep it tight and steal one through an Afif transition or a set-piece.
