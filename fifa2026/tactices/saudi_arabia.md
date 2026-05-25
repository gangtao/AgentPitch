# Saudi Arabia — Tactical Profile

## Identity & Philosophy
Saudi Arabia under Hervé Renard (returned for a second spell after the 2022 World Cup heroics) is the **counter-attacking specialist of Asia** — a team that famously beat Lionel Messi's Argentina 2-1 in Qatar 2022 and built its identity on **defensive compactness, lightning transitions, and one moment of magic from Salem Al-Dawsari**. The team is possession-shy by design: they will happily cede 60% of the ball to a superior opponent and wait for the moment to spring a counter. The Saudi Pro League's foreign investment has improved the league quality but the national team identity remains old-school: **organize, defend, counter, set-pieces**. Recent form: comfortable through the AFC third round, less dominant than Iran or Japan, but a tactically mature side that knows how to win 1-0.

## Formation
- Shape: **4-2-3-1** in possession (collapses to a **4-4-1-1 mid-block** out of possession, **4-5-1** against elite opposition).
- Role mapping (roster order in `saudi_arabia.yaml`):
  - index 0: GK — **Mohammed Al-Owais** — 2022 World Cup hero against Argentina, traditional shot-stopper, less of a sweeper, dominates aerially.
  - index 1: LB — **Ali Lajami** — disciplined, defensive-first fullback, rarely overlaps deep; cover-shifts for Al-Bulayhi.
  - index 2: LCB — **Ali Al-Bulayhi** — the aerial monster (strength 16), the talker, the duel-winner, the famous "I won't be sad if we lose" Argentina-game CB.
  - index 3: RCB — **Hassan Tambakti** — Al-Bulayhi's calmer partner, sweeper-style, the ball-player of the defence.
  - index 4: RB — **Saud Abdulhamid** — most attacking of the back four, the natural width-giver on the right, overlapping fullback.
  - index 5: DM — **Mohamed Kanno** — the destroyer, the screen, the foul-taker, the captain figure in midfield.
  - index 6: DM — **Abdulelah Al-Malki** — Kanno's disciplined partner, recycles possession, screens the back four.
  - index 7: AM — **Nasser Al-Dawsari** — the press-resistant midfielder, drifts to the right half-space to combine with Salem cutting inside from the left.
  - index 8: LW — **Salem Al-Dawsari** — the star, the talisman, the captain in spirit. Cuts inside from the left on his right foot. Shoot 16, dribbling 16, skill 16. The team's only world-class creator and finisher.
  - index 9: RW — **Musab Al-Juwayr** — the technical right-winger, drifts inside to combine; the second creator.
  - index 10: CF — **Firas Al-Buraikan** — the lone 9, hold-up player, the press-leader, the channel-runner, the team's leading striker.

## Style of Play

### Build-up
Direct and pragmatic. Saudi Arabia builds short from the back when uncontested but immediately goes long when pressed. The chief progressor is Tambakti — he steps into midfield with the ball and fires diagonals. The team's preferred build-up is short-short-LONG: Al-Owais to Tambakti, Tambakti to Kanno, Kanno to a long diagonal toward Salem isolated on the left flank. Possession is not a goal — verticality is. The first thought is always **find Salem 1v1 on the left**.

### Pressing
**Low to mid-block. No high press.** Saudi Arabia retreats to a compact shape around the halfway line or deeper. They do not press the opposition GK or CBs. The press triggers are: (1) opposition pass into a wide channel (the fullback + winger close down), (2) a heavy first touch in midfield (Kanno jumps). The team is happy to defend in their own half for 70% of the match against a top opponent and conserve stamina for the counter.

### Defensive shape
Compact **4-4-1-1** with Salem dropping to LM out of possession (yes — Salem tracks back, a Renard non-negotiable). Al-Juwayr drops to RM. Nasser Al-Dawsari plays alongside Al-Buraikan as a second forward in transition but drops into the midfield five when defending. The back four sits 25 units off goal. The CBs (Al-Bulayhi, Tambakti) hold the line. The shape is famously hard to break down — Saudi Arabia conceded only 4 goals in the 2022 group stage despite drawing Argentina and Mexico.

### Wide play
**Asymmetric, heavily left-loaded.** Almost every Saudi attack runs through Salem on the left. He cuts inside on his right foot, Lajami underlaps to occupy the opposition RB, and Nasser Al-Dawsari arrives late from central midfield. The right side is the secondary outlet — Al-Juwayr drifts inside, Abdulhamid overlaps. The crosses come from deep when they come at all; Saudi Arabia would rather have Salem cut inside and shoot than cross from the touchline.

### Final third
Patterns: **Salem cuts inside, shoots** (this is 30% of Saudi attacks). Salem's slipped through-ball to Al-Buraikan sprinting in behind. Nasser Al-Dawsari's late arrival in the box for a cut-back. Al-Juwayr's combination with Abdulhamid on the right. Saudi Arabia creates 3-5 chances per match — the conversion depends entirely on Salem and Al-Buraikan being clinical.

## Set Pieces
- Attacking corners: **Salem Al-Dawsari** in-swingers from the right (right foot), **Nasser Al-Dawsari** out-swingers from the left. Targets: Al-Bulayhi (penalty spot, primary aerial), Tambakti (back post), Al-Buraikan (near post flick-on).
- Defending corners: man-marking heavy. Al-Bulayhi marks the opposition's most dangerous striker; four zonal markers; Al-Owais on his line.
- Free kicks: **Salem** direct from any angle within 28 yards (right foot, world-class striker of a free kick — he scored a world-class direct free kick against Argentina).
- Penalties: **Salem** primary, **Al-Buraikan** secondary, **Nasser Al-Dawsari** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_8" (LW Salem Al-Dawsari, #10) and I have the ball on the left flank:** Dribble inside onto my right foot; Shoot if distance < 23 and angle < 35°. This is the team's primary attacking pattern.
2. **If my player_id ends with "_8" (LW Salem, #10) and team_phase == "defending":** Drop to LM. Renard's instruction is non-negotiable — Salem tracks back.
3. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-4-1-1** at the halfway line, then collapse to **4-5-1** if the ball enters my final third.
4. **If my role == "GK" (index 0, Al-Owais, #21) and a long ball is incoming into my box:** Stay on my line; do not sweep. Punch only under direct physical pressure.
5. **If my player_id ends with "_2" (LCB Al-Bulayhi, #5) and a cross or aerial duel is incoming:** Attack the ball aggressively. Win the header. Strength 16, aerial dominator.
6. **If team_phase == "transition_attack":** Index-8 Salem (LW) sprints diagonally inside; index-10 Al-Buraikan runs the channel; index-7 Nasser Al-Dawsari is the trailer; index-9 Al-Juwayr the secondary runner on the right.
7. **If my player_id ends with "_5" (DM Kanno, #23) and the opposition is breaking past midfield:** Tactical foul within 4 units of the ball-carrier. Take the yellow.
8. **If my role == "DEF" and my player_id ends with "_1" (LB Lajami, #13) or "_4" (RB Abdulhamid, #2) and team_phase == "attacking":** Only Abdulhamid (index 4) overlaps; Lajami (index 1) stays underlap-deep as cover for Salem cutting inside.
9. **If my player_id ends with "_10" (CF Al-Buraikan, #9) and the index-8 Salem has the ball cutting inside:** Make a near-post run; Salem's pass-or-shoot decision will use me as the third option.
10. **If team is leading by 1+ goals after minute 75:** Drop everyone behind the ball into **4-5-1**; recycle possession with deliberate time-wasting via the index-0 Al-Owais.
11. **If a defensive corner is incoming:** The index-2 Al-Bulayhi marks the most dangerous CF; the index-3 Tambakti covers; the index-10 Al-Buraikan stays on the halfway line as a counter-outlet.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-8 Salem Al-Dawsari (every time).

## Key Player Notes
- **Salem Al-Dawsari (8):** The team. The talisman. The scorer of the goal that beat Argentina. Cuts inside from the left, shoots, takes every set-piece. Without him, Saudi Arabia is mid-table Asian. With him, they're a knockout-stage threat.
- **Al-Bulayhi (2):** The aerial talker. Strength 16. Wins every set-piece duel in both boxes.
- **Al-Owais (0):** The 2022 World Cup hero. Made 10 saves against Argentina. Calm under pressure.
- **Kanno (5):** The destroyer. Tactical fouler. Sets the team's defensive aggression baseline.
- **Al-Buraikan (10):** The lone 9. Channel runner. Hold-up player. Finishes inside the box.

## Tournament Mindset
Saudi Arabia carries the swagger of Argentina-22 — they know they can beat anyone on any day. The mentality is **organize, defend, wait for Salem's moment**. They will lose 2-0 to a top-eight side they didn't get an opening against, then beat the next opponent 1-0 on a Salem free kick. The hidden weapon is **mental resilience** — they don't panic when behind, and they execute the tactical plan to the letter for 90 minutes. The vulnerability is creativity if Salem is well-marked or absent — the secondary creators (Al-Juwayr, Nasser Al-Dawsari) are good but not match-winning. Renard's set-piece coaching is elite and the team practices dead-balls for hours every week.
