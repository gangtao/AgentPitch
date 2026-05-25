# Qatar — Tactical Profile

## Identity & Philosophy
Qatar are the **back-to-back AFC Asian Cup champions (2019, 2024)** and the most underrated tactical side in Asia. Coached most recently by **Tintín Márquez** (succeeding Luís García) — the staff has rotated, but the core identity inherited from Félix Sánchez Bas and refined since remains: **compact 5-3-2 / 3-5-2 block, intelligent positional rotation, lethal counter-attacks via Akram Afif**. Qatar's identity is **defensive solidity through numbers + ruthless transitions through one technical superstar**. Backed by Aspire Academy's decade-long development of the entire starting XI as a single generation, Qatar plays like a club side — they know each other's movements instinctively. Recent form: 2024 Asian Cup champions, comfortable through World Cup qualifying despite a Pot-3 ranking, hosting experience from 2022 gives them tournament composure.

## Formation
- Shape: **5-3-2** in possession (rotates to **3-5-2** when wingbacks push high; defensive shape is **5-4-1** with Muntari dropping deep).
- Role mapping (roster order in `qatar.yaml`):
  - index 0: GK — **Meshaal Barsham** — 2022 World Cup keeper, reflex shot-stopper, less of a sweeper, dominates his box.
  - index 1: LWB — **Homam Ahmed** — left wingback in the 5-3-2; hard-running, the natural width-giver on the left.
  - index 2: LCB — **Tarek Salman** — left-of-centre in the back three, calm passer, the ball-progressor.
  - index 3: CCB — **Sultan Al-Brake** — middle CB, sweeper of the three-man defence, aerial duel-winner.
  - index 4: RCB — **Lucas Mendes** — naturalised Brazilian-born CB, right-of-centre in the back three, the most technical defender.
  - index 5: RWB — **Jassem Gaber** — right wingback, energetic, overlapping; provides the right-side width.
  - index 6: DM — **Assim Madibo** — the destroyer, the screen, the disciplined ball-winner who shields the back three.
  - index 7: CM — **Mohammed Waad** — the box-to-box partner, the late-runner, the second presser.
  - index 8: CM/AM — **Abdulaziz Hatem** — the veteran, the connector, drifts to the right half-space to combine with Afif and Gaber.
  - index 9: CF/withdrawn — **Akram Afif** — the star, 2023 Asian Cup Golden Ball winner, the team's creator and finisher. Plays as a withdrawn striker / second 9 in the 5-3-2, dropping into the #10 space to receive between the lines. Skill 16, dribbling 16, shoot 15.
  - index 10: CF — **Mohammed Muntari** — the target forward, the hold-up player, the aerial threat in both boxes.

## Style of Play

### Build-up
Patient and positional, especially against weaker opposition. Qatar builds in a **3-2-shape**: back three of Salman-Al-Brake-Mendes splits wide, Madibo drops as a screen, wingbacks push high. Against a press, the team goes long to Muntari for a knock-down, with Afif gambling on the second ball. The chief progressor is Mendes — he carries the ball into midfield with the most technical CB profile. Afif drops between the opposition lines to receive — when he gets the ball facing forward in space, Qatar is dangerous.

### Pressing
**Mid-block. Selective high press on triggers.** Qatar drops to the halfway line and waits. Triggers: opposition GK takes a heavy touch, back-pass under duress, throw-in. Afif and Muntari lead the front press; Hatem and Waad jump from midfield. The press is coordinated and Aspire-trained — every player knows their cover-shadow. Out of possession, Qatar prioritizes **compact numerical superiority** over chasing.

### Defensive shape
Compact **5-4-1** with Hatem dropping alongside the double pivot to form a midfield four, and Afif tucking next to Muntari as a flat front pair (but only nominally — Afif rarely tracks back hard). The back five denies all width: the wingbacks (Ahmed, Gaber) tuck inside to become full-backs in a back five. This shape is famously hard to break down — Qatar conceded only 1 goal in 6 matches at the 2023 Asian Cup.

### Wide play
The **wingbacks** are the natural width-givers — Ahmed left, Gaber right. They push high in possession to create a 3-5-2 / 3-4-3 dynamic. The crosses come from the wingbacks; Afif drifts inside to receive cut-backs; Muntari attacks the near post. Qatar is comfortable switching play with long diagonals from Mendes to the opposite wingback.

### Final third
Patterns: **Afif drops between the lines, receives, dribbles inside, shoots or slips through-ball to Muntari**. Cut-back from Gaber's right-side overlap to Hatem arriving late. Ahmed's deep cross to Muntari at the back post. Afif's signature move: receive on the half-turn, dribble past two defenders, finish low to the far corner.

## Set Pieces
- Attacking corners: **Afif** in-swingers from the right (left foot), **Hatem** out-swingers from the left. Targets: Muntari (penalty spot, primary aerial), Al-Brake (back post), Mendes (near post flick-on).
- Defending corners: hybrid — Al-Brake attacks the first ball; Muntari and Mendes mark the two most dangerous opposition runners; four zonal markers across the six-yard line; Barsham on his line.
- Free kicks: **Afif** direct from any angle within 28 yards; he scored from a direct free kick against Lebanon in the 2023 Asian Cup.
- Penalties: **Afif** primary, **Muntari** secondary, **Hatem** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_9" (CF Afif, #17) and team_phase == "attacking":** Drop into the #10 space between the opposition lines, 8-12 units behind the index-10 Muntari. Receive on the half-turn.
2. **If my player_id ends with "_9" (CF Afif, #17) and I have the ball facing forward in the opposition half:** Dribble — skill 16, dribbling 16. Take on the first defender; Shoot if angle opens within 24 units.
3. **If my role == "GK" (index 0, Meshaal Barsham, #1) and a cross is incoming:** Punch under physical pressure; otherwise stay on the line.
4. **If my player_id ends with "_1" (LWB Ahmed, #14) or "_5" (RWB Gaber, #15) and team_phase == "attacking":** Push to the touchline at the opposition's defensive third — both wingbacks high simultaneously to form a 3-4-3.
5. **If my player_id ends with "_1" or "_5" (wingbacks) and team_phase == "defending":** Tuck inside next to the CBs to form a back five; deny width.
6. **If my player_id ends with "_6" (DM Madibo, #8) and the opposition has the ball within 35 units of my goal:** Step to the ball-carrier, tactical foul if breaking through.
7. **If team_phase == "transition_attack":** Index-9 Afif sprints into space to receive; index-10 Muntari runs the channel; the wingback on the ball-side sprints forward for width.
8. **If my player_id ends with "_10" (CF Muntari, #19) and the index-9 Afif has the ball:** Make a channel-run behind the opposition CBs OR hold up the long ball for Afif to combine.
9. **If team is trailing by 1 in the final 15 minutes:** Push to **3-4-3** with wingbacks high, the index-10 Muntari and index-9 Afif both forward, the index-8 Hatem as the lone #10 behind.
10. **If a defensive corner is incoming:** The index-3 Al-Brake marks the most dangerous opposition striker; the index-4 Mendes and index-10 Muntari mark zonal; the index-9 Afif stays on the halfway line as a counter-outlet.
11. **If my role == "DEF" and team_phase == "attacking":** The index-4 Mendes carries the ball into midfield (the most technical CB); the index-2 Salman and index-3 Al-Brake stay deep as cover.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-9 Afif (left-footed in-swingers, direct free kicks).

## Key Player Notes
- **Afif (9):** The 2023 Asian Cup Golden Ball winner. The creator and finisher. The withdrawn striker who drifts between the lines. The team's only world-class technical player.
- **Muntari (10):** The target 9. Hold-up. Aerial. Channel-runner. Strength 15.
- **Mendes (4):** The technical CB. Naturalised Brazilian, the ball-progressor from the back three.
- **Al-Brake (3):** The middle CB. Aerial duel-winner. The defensive captain.
- **Madibo (6):** The screen. Tactical fouler. Recycles possession.

## Tournament Mindset
Qatar are the AFC-champion sleeper. They are not pre-tournament favourites to escape a World Cup group, but their tactical discipline, Aspire-trained cohesion, and Afif's individual brilliance make them dangerous. The mentality is **trust the shape, trust Afif, take one chance per match**. They will draw a top-eight side 0-0 and beat a mid-table opponent 1-0. The vulnerability is **goal-scoring depth** — if Afif and Muntari are marked out, the secondary creators (Hatem, Waad) lack the cutting edge. Qatar's defensive solidity in the **5-4-1** is its hidden weapon: they go entire matches conceding 0.3 xG. Set-pieces and Afif transitions are the only realistic goal sources against top opposition.
