# Jordan — Tactical Profile

## Identity & Philosophy
Jordan are the **fairytale story of Asian football** — the 2024 Asian Cup runners-up who shocked South Korea in the semi-final, qualifying for their first-ever World Cup. The team's identity, built under Hussein Ammouta and now Jamal Sellami, is **compact 4-5-1 defending + lightning-fast counter-attacks via Musa Al-Tamari**. Jordan plays a deeper block than any Asian qualifier, conserves stamina obsessively, and unleashes its one world-class player on every transition. The collective belief in this group is **the highest among AFC second-tier sides** — they have already beaten Iraq, South Korea, and drawn with Saudi Arabia in knockout football. Recent form: comfortable through AFC qualifying (a different proposition than knockout tournament football), the 2024 Asian Cup final loss to Qatar still motivating, with Al-Tamari now an established starter at Rennes (Ligue 1) and one of the most underrated players in Europe. **Major blow for the World Cup: first-choice striker Yazan Al-Naimat is OUT with an ACL injury (surgery after the 2024 Arab Cup)** — Sellami must replace his goals, with 2025 Arab Cup Golden Boot winner Ali Olwan leading the line.

## Formation
- Shape: **4-3-3** in possession (collapses to **4-5-1 low block** out of possession — this is the default shape).
- Role mapping (roster order in `jordan.yaml`):
  - index 0: GK — **Yazeed Abulaila** (#1) — traditional shot-stopper, less of a sweeper; commands his box; the calm presence behind the deep block.
  - index 1: LB — **Mohammad Abu Al-Nadi** (#16) — disciplined fullback, rarely overlaps; defensive-first.
  - index 2: LCB — **Yazan Al-Arab** (#5) — physical (strength 15), the aerial duel-winner, the defensive talker.
  - index 3: RCB — **Abdallah Nasib** (#3) — Al-Arab's calmer partner; disciplined and positionally sound.
  - index 4: RB — **Mahmoud Al-Mardi** (#13) — most attacking of the back four (speed 14), the natural width-giver when Jordan can build up.
  - index 5: DM — **Ibrahim Sa'deh** (#15) — the screen in front of the back four, recycles possession, the deep pivot.
  - index 6: CM — **Amer Jamous** (#6) — disciplined ball-winner alongside the pivot, the team's defensive midfield aggression.
  - index 7: CM/AM — **Nizar Al-Rashdan** (#21) — the box-to-box engine, late runs into the box, stamina 16; the most progressive midfielder and a connector to Al-Tamari.
  - index 8: LW — **Musa Al-Tamari** (#10) — the star, the talisman, the captain in spirit. Speed 17, dribbling 16, shoot 15. Plays at Rennes in Ligue 1. Cuts inside from the left or sprints down the line; the team's only world-class attacker.
  - index 9: CF — **Ali Olwan** (#9) — the lone 9 now that Al-Naimat is injured; 2025 Arab Cup Golden Boot winner, the channel runner and primary finisher, the press-leader.
  - index 10: RW — **Mohammad Abu Zrayq** (#7) — direct right-sided forward, the third forward in transitions, the secondary outlet on the break.

## Style of Play

### Build-up
Pragmatic and direct. Jordan does NOT play out from the back against pressing opponents — Abulaila will launch a long ball to Olwan or down the channel for Al-Tamari to chase. When build-up is possible, the team plays short through Sa'deh as the deep pivot, with Al-Rashdan stepping up to connect. The first instinct is always **find Al-Tamari in space on the left wing** — once he has the ball facing forward, Jordan is dangerous.

### Pressing
**Low to mid-block. No high press.** Jordan retreats to a compact shape inside their own half and waits. Triggers: opposition pass into a wide channel (the fullback + winger close down), heavy first touch in midfield (Jamous jumps). Olwan presses occasionally but mostly stays high as the counter-attack outlet. The team conserves stamina for the final 30 minutes when they will run a tired opponent into the ground via Al-Tamari.

### Defensive shape
Compact **4-5-1 low block** — this is the default shape. Al-Tamari drops to LM (he tracks back diligently — a non-negotiable from the staff). Abu Zrayq drops to RM. Olwan is the lone front presser. The midfield five (Al-Tamari, Sa'deh, Jamous, Al-Rashdan, Abu Zrayq) sits in a flat line 25 units off goal. The back four sits 20 units off goal. This shape held a clean sheet against Australia and South Korea at the 2024 Asian Cup.

### Wide play
Almost everything runs through Al-Tamari on the left. He cuts inside or sprints down the touchline depending on the defender's positioning. The right side (Abu Zrayq + Al-Mardi) is the secondary outlet. Jordan does not cross much — they prefer Al-Tamari to dribble inside and shoot.

### Final third
Patterns: **Al-Tamari isolated 1v1 on the left, dribbles inside, shoots**. Long ball over the top for Al-Tamari to chase with his 17 speed. Cut-back from Al-Tamari to Olwan at the near post. Al-Rashdan's slipped through-ball to Olwan sprinting in behind. Jordan creates 2-4 chances per match — they need to be clinical and depend on Al-Tamari producing one moment. **Without Al-Naimat's aerial presence, goal-scoring depth is the team's biggest concern.**

## Set Pieces
- Attacking corners: **Al-Rashdan** in-swingers from the right, **Al-Tamari** out-swingers from the left. Targets: Al-Arab (penalty spot), Nasib (back post), Olwan (near post flick-on).
- Defending corners: man-marking heavy. Al-Arab marks the most dangerous opposition striker; four zonal markers; Abulaila stays on his line.
- Free kicks: **Al-Tamari** direct from the right half-space (left-footed), **Al-Rashdan** from central range.
- Penalties: **Al-Tamari** primary, **Olwan** secondary, **Al-Rashdan** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_8" (LW Al-Tamari, #10) and team_phase == "transition_attack":** Sprint diagonally inside or down the touchline — my speed 17 is the team's primary weapon.
2. **If my player_id ends with "_8" (LW Al-Tamari, #10) and I have the ball on the left with no defender within 4 units:** Dribble inside; Shoot if angle opens within 23 units.
3. **If my player_id ends with "_8" (LW Al-Tamari, #10) and team_phase == "defending":** Drop to LM and track back diligently — non-negotiable from the staff. Conserve stamina for transitions.
4. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-5-1 low block** at 25 units off goal; do not push higher.
5. **If my player_id ends with "_5" (DM Sa'deh, #15) and the opposition is breaking past midfield:** Tactical foul within 4 units of the ball-carrier — take the yellow.
6. **If my role == "GK" (index 0, Yazeed Abulaila, #1) and the team has a goal-kick under press:** Launch long to the index-9 Olwan or into the channel for the index-8 Al-Tamari.
7. **If my player_id ends with "_9" (CF Olwan, #9) and a long ball is incoming:** Run the channel — outpace the opposition CB and finish 1v1 if possible.
8. **If team_phase == "transition_attack":** Index-8 Al-Tamari sprints; index-9 Olwan runs the channel; index-7 Al-Rashdan is the late-arriving trailer; index-10 Abu Zrayq is the secondary winger.
9. **If my role == "DEF" and a cross is incoming:** The index-2 Al-Arab attacks the ball — strength 15.
10. **If team is leading by 1 in the final 15 minutes:** Drop everyone behind the ball into **5-4-1** with the index-4 Al-Mardi tucking inside as a third CB; recycle every dead-ball by taking 30 seconds.
11. **If a defensive corner is incoming:** The index-2 Al-Arab marks the opposition's most dangerous CF; the index-9 Olwan AND index-8 Al-Tamari stay on the halfway line as counter-outlets.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-8 Al-Tamari (left-footed) or the index-7 Al-Rashdan (central).

## Key Player Notes
- **Al-Tamari (10):** The team. The talisman. Speed 17, dribbling 16, shoot 15. Rennes Ligue 1 winger. Without him Jordan is mid-table AFC; with him, they're a knockout-tournament threat.
- **Olwan (9):** The lone 9 in Al-Naimat's absence. 2025 Arab Cup Golden Boot winner. Channel runner and primary finisher.
- **Al-Arab (5):** The aerial CB. Strength 15. The defensive talker.
- **Al-Rashdan (21):** The box-to-box engine. Stamina 16. The progressive midfielder, set-piece deliverer, and connector to Al-Tamari.
- **Sa'deh (15):** The deep pivot. The screen. Sets the team's defensive aggression baseline in front of the back four.

## Tournament Mindset
Jordan arrives at the World Cup having already beaten the odds — qualification itself is the historic achievement. The mentality is **defend deep, trust Al-Tamari, take one chance**. They will draw with mid-tier opposition 0-0 and beat anyone if Al-Tamari produces. They will lose comprehensively to a top-five side that denies Al-Tamari space. The collective belief (built through the 2024 Asian Cup final run) is the team's hidden weapon — they don't fear anyone. The vulnerability is **goal-scoring depth** — magnified by the loss of Al-Naimat to an ACL injury; if Al-Tamari is injured, marked out, or off form, Jordan can go entire matches without a clean chance. Stamina is uniformly 14-16 — they will run hard for 90 minutes and grow into matches in the final 30.
