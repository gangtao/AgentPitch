# Japan — Tactical Profile

## Identity & Philosophy
Hajime Moriyasu's Japan is Asia's gold standard: a positional, technical, intensely-pressing side that has dismantled Germany and Spain in recent World Cup memory and dominated AFC qualifying with the goal difference of a European top side. The identity is "European football played at Japanese tempo" — every pass has a purpose, every press is choreographed, and every transition is a five-pass move rather than a hopeful long ball. Moriyasu's group has matured into a confident outfit that no longer parks the bus against elite opposition; they go toe-to-toe. Recent form: undefeated through the third round of AFC qualifying, scoring at will, conceding almost nothing.

## Formation
- Shape: **3-4-2-1** — Moriyasu's signature back-three system. Three centre-backs, two flying wingbacks, a double pivot, two free "shadow strikers" behind a lone centre-forward. In settled possession it morphs into a **3-2-5** (the wingbacks push high, the pivot splits); out of possession it drops into a compact **5-4-1** mid-block.
- Role mapping (roster order in `japan.yaml`):
  - index 0: GK — **Zion Suzuki** — modern sweeper-keeper, comfortable starting the build-up with feet, sprints out to clear long balls behind the high line.
  - index 1: LCB — **Hiroki Itō** — left-footed ball-playing centre-back on the left of the back three, steps into midfield to break lines and covers behind the left wingback.
  - index 2: CCB — **Ko Itakura** — central anchor of the back three, the calmest passer on the team, organises the line and steps up to break lines with vertical passes.
  - index 3: RCB — **Takehiro Tomiyasu** — Japan's most complete defender, right of the back three; aggressive stepper out of possession, can play every position across the back.
  - index 4: LWB — **Keito Nakamura** — left wingback, the engine on the flank: gives width going forward, whips in early crosses, sprints back to make a back five out of possession.
  - index 5: DM — **Wataru Endō** — the captain, the destroyer, the ball-winner who screens the back three. Liverpool-conditioned: he tackles, recovers, and recycles. Limited creative range but the heartbeat.
  - index 6: DM — **Ao Tanaka** — partner pivot, more progressive than Endō, takes the ball off the back three and turns into space. Leeds-schooled — line-breaking carries and through-balls.
  - index 7: RWB — **Junya Itō** — right wingback, pure vertical pace (speed 17); hugs the touchline, beats his man on the outside and delivers early low crosses. Sprints back to make a back five out of possession.
  - index 8: LAM — **Takefusa Kubo** — left-sided shadow striker, free role; drifts inside off the left into the right half-space, slips passes through, the technical genius of the side.
  - index 9: CF — **Ayase Ueda** — the lone 9, presses from the front, holds the ball up, finishes inside the six-yard box. A classic centre-forward and Eredivisie top scorer, not a false 9.
  - index 10: RAM — **Ritsu Doan** — right-sided shadow striker with a winger's instincts; drifts between the lines, tucks inside onto his left foot to shoot, the team's leading goalscorer in qualifying. Late runs into the box.

## Style of Play

### Build-up
Patient short build-up out of a **back three**: Itakura sits central while Hiroki Itō and Tomiyasu split wide, and Endō-Tanaka form the double pivot in front, giving a **3-2** base. The wingbacks (Nakamura left, Junya Itō right) push high to pin the opposition fullbacks, turning the shape into a **3-2-5**. Suzuki is the eleventh outfielder — always offering a back-pass option. Japan is utterly comfortable playing through the first line of pressure: 60-70% possession against most opponents. Endō shields, Tanaka is the line-breaker, and the CBs (especially Itakura and Itō) are licensed to carry into midfield. The first switch of play usually goes to Kubo finding space in the left half-space.

### Pressing
**Intense, coordinated, high block** — Japan presses from the front whenever the opposition GK touches the ball. Ueda curves his run to lock the GK onto one side; Kubo and Doan cut the passing lanes to the centre-backs; the wingbacks Nakamura and Junya Itō jump the opposition fullbacks; Endō and Tanaka step up to win the second ball. The press trigger is a back-pass to the GK or a CB taking a heavy first touch. When the press breaks, Japan does NOT chase — they retreat into a compact **5-4-1** mid-block and start again. Stamina is a national strength — every outfielder is rated 15+ in stamina.

### Defensive shape
Compact **5-4-1**: the wingbacks Nakamura and Junya Itō drop to form a back five, Kubo and Doan tuck into a midfield four alongside Endō/Tanaka, Ueda leads the line alone. The back three holds a medium-high line — Itakura and Tomiyasu step up aggressively to compress space while Itō covers. Tomiyasu rarely gets dribbled past 1v1. Japan concedes few clear chances because the block is narrow (15 units between the back line and the midfield four) and the second balls are won by Endō.

### Wide play
Asymmetric. **Left side:** Kubo drifts inside off the half-space, leaving Nakamura to provide the width and the overlap as the natural touchline runner. **Right side:** Junya Itō stays wide and attacks the outside with raw pace, while Doan tucks inside off him onto his left foot to shoot; the right of the back three (Tomiyasu) covers the channel behind. The chief creative axis is Kubo–Doan–Itō; final-ball patterns flow right-to-left-to-right with one-touch combinations.

### Final third
Combination football inside the box: Kubo's cut-back to Doan arriving late, Doan's left-foot curler from the right, Ueda's near-post header from a Nakamura or Junya Itō cross. Japan does NOT shoot from distance; everything is engineered for a clean angle inside 18 yards. When transitions arrive, Doan and Kubo sprint diagonally toward the opposite post; Itō provides the outlet run down the right.

## Set Pieces
- Attacking corners: **Doan** in-swingers from the right, **Kubo** out-swingers from the left. Primary targets: Tomiyasu (near post), Itakura (penalty spot), Ueda (back post).
- Defending corners: hybrid — four zonal markers across the six-yard line, three man-markers (Endō tracks the most dangerous runner), two short-corner blockers.
- Free kicks: Kubo direct from the right half-space (left foot), Doan direct from the left half-space (left foot), Tanaka from central range.
- Penalties: **Kubo** primary, **Doan** secondary, **Ueda** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Zion Suzuki, #1) and the ball is in the opposition half:** Sweep up to 28 units out of the box. If a long ball is played in behind, sprint to clear.
2. **If my player_id ends with "_5" (DM Endō, #6):** When my team has the ball, NEVER move beyond the halfway line — stay as the deepest midfielder. When the opposition transitions, sprint to tackle the ball-carrier within 6 units.
3. **If my player_id ends with "_8" (LAM Kubo, #8) and I have the ball on the left flank:** Dribble inside (toward central) until I am in the right half-space, then Pass to the index-10 Doan (late runner) or Shoot if angle < 30° and distance < 23.
4. **If my player_id ends with "_3" (RCB Tomiyasu, #22) and team_phase == "attacking":** Hold the right side of the back three and cover the channel behind the index-7 Junya Itō — do NOT push beyond the halfway line. Pure security on the right.
5. **If my player_id ends with "_7" (RWB Junya Itō, #14) and I have the ball on the right with no defender within 4 units:** Sprint outside down the touchline and deliver an early low cross toward the index-9 Ueda (near post) or the index-10 Doan (cut-back).
6. **If my role == "FWD" (index 9, Ayase Ueda, #18) and the ball is at the opposition GK's feet:** Sprint diagonally to press the GK, curving the run to block the pass to the right centre-back.
7. **If team_phase == "transition_defense":** Counter-press within 5 ticks. Anyone within 6 units of the ball-carrier tackles immediately.
8. **If my player_id ends with "_10" (RAM Doan, #10) and the ball is in the opposition half:** Position myself between the lines, 5-10 units behind the index-9 Ueda, in the half-space opposite to the index-8 Kubo. With the ball and no defender within 4 units, cut onto my left foot and Shoot if distance < 20.
9. **If my player_id ends with "_4" (LWB Nakamura, #13) and the index-8 Kubo has drifted inside:** Sprint to the touchline as the natural width-giver — overlap automatic when Kubo gets the ball. Out of possession, drop to form a back five.
10. **If team is leading by 2+ goals and minute > 75:** Drop into a low **5-4-1** — the wingbacks index-4 Nakamura and index-7 Junya Itō sit as full-time defenders; recycle possession from the back.
11. **If my role == "DEF" and my player_id ends with "_2" (CCB Itakura, #4) with the ball and no opponent within 8 units:** Carry forward into midfield (Pass only when an opponent steps to me).
12. **Set-pieces in the attacking third within 30 units:** Defer dead-ball to the index-8 Kubo (left) or index-10 Doan (right).

## Key Player Notes
- **Kubo (8):** The free role. Drifts off the left into the right half-space. Almost zero defensive tracking expected — he is conserved for transitions and final-ball moments.
- **Endō (5):** Captain and screen. His positional discipline (he literally does not move past midfield) is the foundation of Japan's defensive solidity.
- **Tomiyasu (3):** The most tactically intelligent defender. Anchors the right of the back three; can play every position across the back line if needed.
- **Doan (10):** The leading scorer, deployed as the right-sided shadow striker. Cuts inside, shoots early. His finishing (15) is elite for an Asian wide player.
- **Junya Itō (7):** The right wingback and the fastest man in the squad (speed 17). Stretches the pitch on his own; his early low crosses are Ueda's primary supply line.
- **Suzuki (0):** The modern sweeper-keeper. His comfort with the ball at his feet unlocks Japan's back-three build-up.

## Tournament Mindset
Japan arrives at the World Cup believing they can reach the quarter-finals or further — and the squad has done it on paper. The mentality is no longer "park the bus and counter against Germany"; it is "out-press Germany." Drawn in Group F alongside the Netherlands, Sweden, and Tunisia, expect Japan to back themselves to dominate possession and play boldly even against European or South American giants. Stamina is their hidden superpower — they will run opponents into the 80th minute and find a goal in the 87th. Discipline ratings are uniformly 14+ — they will not get red-carded.
