# Japan — Tactical Profile

## Identity & Philosophy
Hajime Moriyasu's Japan is Asia's gold standard: a positional, technical, intensely-pressing side that has dismantled Germany and Spain in recent World Cup memory and dominated AFC qualifying with the goal difference of a European top side. The identity is "European football played at Japanese tempo" — every pass has a purpose, every press is choreographed, and every transition is a five-pass move rather than a hopeful long ball. Moriyasu's group has matured into a confident outfit that no longer parks the bus against elite opposition; they go toe-to-toe. Recent form: undefeated through the third round of AFC qualifying, scoring at will, conceding almost nothing.

## Formation
- Shape: **4-2-3-1** in possession (slides to **3-4-2-1** when Itō pushes high as a left-wingback and Itakura forms a back three; defensive shape is a compact **4-4-1-1**).
- Role mapping (roster order in `japan.yaml`):
  - index 0: GK — **Zion Suzuki** — modern sweeper-keeper, comfortable starting the build-up with feet, sprints out to clear long balls behind the high line.
  - index 1: LB — **Hiroki Itō** — left-footed ball-playing fullback, inverts into the midfield when Japan has the ball in the opposition half, then steps back as the left CB of a 3-2 build-up.
  - index 2: LCB — **Ko Itakura** — left-of-centre CB, the calmest passer on the team, steps into midfield to break lines with vertical passes.
  - index 3: RCB — **Shogo Taniguchi** — physical right-of-centre CB, the aerial dominator, holds the line while Itakura steps up.
  - index 4: RB — **Takehiro Tomiyasu** — Japan's most complete defender, tucks inside as a right-of-centre CB in possession; pure defender out of possession on the right side.
  - index 5: DM — **Wataru Endō** — the captain, the destroyer, the ball-winner who screens the back four. Liverpool-conditioned: he tackles, recovers, and recycles. Limited creative range but the heartbeat.
  - index 6: DM — **Hidemasa Morita** — partner pivot, more progressive than Endō, takes the ball off the CBs and turns into space. Sporting CP-trained — comfortable under pressure.
  - index 7: RW — **Ritsu Doan** — direct right winger, cuts inside on his left foot, the team's leading goalscorer in qualifying. Replaces Mitoma's role as the wide goal threat.
  - index 8: AM — **Daichi Kamada** — the #10, drifts between the lines, links midfield to attack, late runs into the box. Eintracht/Lazio-schooled in tight pockets.
  - index 9: LW — **Takefusa Kubo** — the chief creator, free role from the left; drifts inside into the right half-space, slips passes through, the technical genius of the side.
  - index 10: CF — **Ayase Ueda** — the lone 9, presses from the front, holds the ball up, finishes inside the six-yard box. A classic centre-forward, not a false 9.

## Style of Play

### Build-up
Patient short build-up in a **3-2-shape**: Itakura and Taniguchi split, Tomiyasu inverts (or Itō steps inside on the other side, depending on the opposition shape), and Endō-Morita form the double pivot in front. Suzuki is the eleventh outfielder — always offering a back-pass option. Japan is utterly comfortable playing through the first line of pressure: 60-70% possession against most opponents. Endō shields, Morita is the line-breaker, and the CBs (especially Itakura) are licensed to carry into midfield. The first switch of play usually goes to Kubo isolated on the left.

### Pressing
**Intense, coordinated, high block** — Japan presses from the front whenever the opposition GK touches the ball. Ueda curves his run to lock the GK onto one side; Kubo and Doan cut the passing lanes to the fullbacks; Kamada jumps the deepest midfielder; Endō and Morita step up to win the second ball. The press trigger is a back-pass to the GK or a CB taking a heavy first touch. When the press breaks, Japan does NOT chase — they retreat into a compact **4-4-1-1** mid-block and start again. Stamina is a national strength — every outfielder is rated 15+ in stamina.

### Defensive shape
Compact **4-4-1-1** with Kamada dropping in front of Endō/Morita, and Doan/Kubo forming the wide midfield. The back four holds a medium-high line — Itakura and Taniguchi step up aggressively to compress space. Tomiyasu rarely gets dribbled past 1v1. Japan concedes few clear chances because the lines are narrow (15 units between back four and Kamada) and the second balls are won by Endō.

### Wide play
Asymmetric. **Left side:** Kubo drifts inside off the touchline into the right half-space, leaving Itō to overlap as the natural width-giver. **Right side:** Doan stays wide as the touchline winger, cuts inside on his left foot to shoot, with Tomiyasu holding the back-post position. The chief creative axis is Kubo–Kamada–Doan; final-ball patterns flow right-to-left-to-right with one-touch combinations.

### Final third
Combination football inside the box: Kubo's cut-back to Kamada arriving late, Doan's left-foot curler from the right half-space, Ueda's near-post header from a Kubo cross. Japan does NOT shoot from distance; everything is engineered for a clean angle inside 18 yards. When transitions arrive, Doan and Kubo sprint diagonally toward the opposite post; Kamada is the trailer.

## Set Pieces
- Attacking corners: **Kamada** in-swingers from the right, **Kubo** out-swingers from the left. Primary targets: Taniguchi (near post), Itakura (penalty spot), Ueda (back post).
- Defending corners: hybrid — four zonal markers across the six-yard line, three man-markers (Endō tracks the most dangerous runner), two short-corner blockers.
- Free kicks: Kubo direct from the right half-space (left foot), Doan direct from the left half-space (left foot), Kamada from central range.
- Penalties: **Kubo** primary, **Kamada** secondary, **Doan** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Zion Suzuki, #1) and the ball is in the opposition half:** Sweep up to 28 units out of the box. If a long ball is played in behind, sprint to clear.
2. **If my player_id ends with "_5" (DM Endō, #6):** When my team has the ball, NEVER move beyond the halfway line — stay as the deepest midfielder. When the opposition transitions, sprint to tackle the ball-carrier within 6 units.
3. **If my player_id ends with "_9" (LW Kubo, #20) and I have the ball on the left flank:** Dribble inside (toward central) until I am in the right half-space, then Pass to the index-8 Kamada (late runner) or Shoot if angle < 30° and distance < 23.
4. **If my player_id ends with "_4" (RB Tomiyasu, #16) and team_phase == "attacking":** Invert inside as a third CB next to the index-2 Itakura — do NOT overlap. Pure security on the right.
5. **If my player_id ends with "_7" (RW Doan, #8) and I have the ball on the right with no defender within 4 units:** Cut inside onto my left foot and Shoot if distance < 20.
6. **If my role == "FWD" (index 10, Ayase Ueda, #19) and the ball is at the opposition GK's feet:** Sprint diagonally to press the GK, curving the run to block the pass to the right CB.
7. **If team_phase == "transition_defense":** Counter-press within 5 ticks. Anyone within 6 units of the ball-carrier tackles immediately.
8. **If my player_id ends with "_8" (AM Kamada, #15) and the ball is in the opposition half:** Position myself between the lines, 5-10 units behind the index-10 Ueda, in the half-space opposite to the index-9 Kubo.
9. **If my player_id ends with "_1" (LB Itō, #3) and the index-9 Kubo has drifted inside:** Sprint to the touchline as the natural width-giver — overlap automatic when Kubo gets the ball.
10. **If team is leading by 2+ goals and minute > 75:** Drop into a low **5-4-1** with the index-1 Itō and index-4 Tomiyasu becoming wingbacks; recycle possession from the back.
11. **If my role == "DEF" and my player_id ends with "_2" (LCB Itakura, #4) with the ball and no opponent within 8 units:** Carry forward into midfield (Pass only when an opponent steps to me).
12. **Set-pieces in the attacking third within 30 units:** Defer dead-ball to the index-9 Kubo (left) or index-7 Doan (right).

## Key Player Notes
- **Kubo (9):** The free role. Drifts off the left touchline into the right half-space. Almost zero defensive tracking expected — he is conserved for transitions and final-ball moments.
- **Endō (5):** Captain and screen. His positional discipline (he literally does not move past midfield) is the foundation of Japan's defensive solidity.
- **Tomiyasu (4):** The most tactically intelligent defender. Inverts in build-up; can play every position across the back four if needed.
- **Doan (7):** The leading scorer. Cuts inside, shoots early. His finishing (15) is elite for an Asian winger.
- **Suzuki (0):** The modern sweeper-keeper. His comfort with the ball at his feet unlocks Japan's 3-2 build-up.

## Tournament Mindset
Japan arrives at the World Cup believing they can reach the quarter-finals or further — and the squad has done it on paper. The mentality is no longer "park the bus and counter against Germany"; it is "out-press Germany." Expect Japan to dominate possession against opponents like Iraq, Jordan, and the Saudis; expect them to play boldly even against South American or African giants. Stamina is their hidden superpower — they will run opponents into the 80th minute and find a goal in the 87th. Discipline ratings are uniformly 14+ — they will not get red-carded.
