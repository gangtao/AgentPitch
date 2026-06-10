# Jordan — Tactical Profile

## Identity & Philosophy
Jordan are the **fairytale story of Asian football** — the 2024 Asian Cup runners-up who shocked South Korea in the semi-final, qualifying for their first-ever World Cup. The team's identity, built under Hussein Ammouta and now Jamal Sellami, is **compact 5-4-1 defending out of a back-three system + lightning-fast counter-attacks via Musa Al-Tamari**. Jordan plays a deeper block than any Asian qualifier, conserves stamina obsessively, and unleashes its one world-class player on every transition. The collective belief in this group is **the highest among AFC second-tier sides** — they have already beaten Iraq, South Korea, and drawn with Saudi Arabia in knockout football. Recent form: comfortable through AFC qualifying (a different proposition than knockout tournament football), the 2024 Asian Cup final loss to Qatar still motivating, with Al-Tamari now an established starter at Rennes (Ligue 1) and one of the most underrated players in Europe. **Major blow for the World Cup: first-choice striker Yazan Al-Naimat is OUT with an ACL injury (surgery after the 2024 Arab Cup)** — Sellami must replace his goals, with 2025 Arab Cup Golden Boot winner Ali Olwan leading the line.

## Formation
- Shape: **3-4-3** in possession (collapses to **5-4-1 low block** out of possession — the wing-backs drop into a back five; this is the default shape). Sellami switched from the old back four during World Cup preparation.
- Role mapping (roster order in `jordan.yaml`):
  - index 0: GK — **Yazeed Abulaila** (#1) — traditional shot-stopper, less of a sweeper; commands his box; the calm presence behind the deep block.
  - index 1: LCB — **Yazan Al-Arab** (#5) — physical (strength 15), the aerial duel-winner, the defensive talker; left of the back three.
  - index 2: CCB — **Abdallah Nasib** (#3) — the central organiser of the back three; Al-Arab's calmer partner, disciplined and positionally sound.
  - index 3: RCB — **Husam Abu Dahab** (#4) — the new third centre-back; a no-frills stopper who covers the channel behind the right wing-back.
  - index 4: LWB — **Mahmoud Al-Mardi** (#13) — converted fullback now playing left wing-back (speed 14), the natural width-giver when Jordan can build up; drops to make a back five.
  - index 5: CM — **Ibrahim Sa'deh** (#15) — the screen in front of the back line, recycles possession, the deep pivot.
  - index 6: CM — **Nizar Al-Rashdan** (#21) — the box-to-box engine, late runs into the box, stamina 16; the most progressive midfielder and a connector to Al-Tamari.
  - index 7: RWB — **Ehsan Haddad** (#23) — the captain; disciplined right wing-back who organises the block, modest going forward but never beaten twice.
  - index 8: LW — **Mohammad Abu Zrayq** (#7) — direct left-sided forward, the third forward in transitions, the secondary outlet on the break.
  - index 9: CF — **Ali Olwan** (#9) — the lone 9 now that Al-Naimat is injured; 2025 Arab Cup Golden Boot winner, the channel runner and primary finisher, the press-leader.
  - index 10: RW — **Musa Al-Tamari** (#10) — the star, the talisman, the captain in spirit. Speed 17, dribbling 16, shoot 15. Plays at Rennes in Ligue 1. Cuts inside from the right onto his left foot or sprints down the line; the team's only world-class attacker.

## Style of Play

### Build-up
Pragmatic and direct. Jordan does NOT play out from the back against pressing opponents — Abulaila will launch a long ball to Olwan or down the channel for Al-Tamari to chase. When build-up is possible, the back three split and the team plays short through Sa'deh as the deep pivot, with Al-Rashdan stepping up to connect and the wing-backs Al-Mardi and Haddad offering the wide outlets. The first instinct is always **find Al-Tamari in space on the right wing** — once he has the ball facing forward, Jordan is dangerous.

### Pressing
**Low to mid-block. No high press.** Jordan retreats to a compact shape inside their own half and waits. Triggers: opposition pass into a wide channel (the wing-back + winger close down), heavy first touch in midfield (Sa'deh jumps). Olwan presses occasionally but mostly stays high as the counter-attack outlet. The team conserves stamina for the final 30 minutes when they will run a tired opponent into the ground via Al-Tamari.

### Defensive shape
Compact **5-4-1 low block** — this is the default shape. The wing-backs Al-Mardi and Haddad drop alongside the three centre-backs to make a back five at 20 units off goal. Al-Tamari drops to RM (he tracks back diligently — a non-negotiable from the staff). Abu Zrayq drops to LM. Olwan is the lone front presser. The midfield four (Abu Zrayq, Sa'deh, Al-Rashdan, Al-Tamari) sits in a flat line 25 units off goal. The deep-block DNA held a clean sheet against Australia and South Korea at the 2024 Asian Cup.

### Wide play
Almost everything runs through Al-Tamari on the right. He cuts inside onto his left foot or sprints down the touchline depending on the defender's positioning, with Haddad's underlap behind him for security rather than overlap. The left side (Abu Zrayq + Al-Mardi) is the secondary outlet. Jordan does not cross much — they prefer Al-Tamari to dribble inside and shoot.

### Final third
Patterns: **Al-Tamari isolated 1v1 on the right, dribbles inside, shoots**. Long ball over the top for Al-Tamari to chase with his 17 speed. Cut-back from Al-Tamari to Olwan at the near post. Al-Rashdan's slipped through-ball to Olwan sprinting in behind. Jordan creates 2-4 chances per match — they need to be clinical and depend on Al-Tamari producing one moment. **Without Al-Naimat's aerial presence, goal-scoring depth is the team's biggest concern.**

## Set Pieces
- Attacking corners: **Al-Rashdan** in-swingers from the left, **Al-Tamari** in-swingers from the right (left foot). Targets: Al-Arab (penalty spot), Nasib (back post), Olwan (near post flick-on).
- Defending corners: man-marking heavy. Al-Arab marks the most dangerous opposition striker; four zonal markers; Abulaila stays on his line.
- Free kicks: **Al-Tamari** direct from the right half-space (left-footed), **Al-Rashdan** from central range.
- Penalties: **Al-Tamari** primary, **Olwan** secondary, **Al-Rashdan** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_10" (RW Al-Tamari, #10) and team_phase == "transition_attack":** Sprint diagonally inside or down the touchline — my speed 17 is the team's primary weapon.
2. **If my player_id ends with "_10" (RW Al-Tamari, #10) and I have the ball on the right with no defender within 4 units:** Dribble inside onto my left foot; Shoot if angle opens within 23 units.
3. **If my player_id ends with "_10" (RW Al-Tamari, #10) and team_phase == "defending":** Drop to RM and track back diligently — non-negotiable from the staff. Conserve stamina for transitions.
4. **If team_phase == "defending" and the opposition is past midfield:** Drop into **5-4-1 low block** — wing-backs index-4 Al-Mardi and index-7 Haddad into the back five at 20 units, midfield four at 25 units; do not push higher.
5. **If my player_id ends with "_5" (CM Sa'deh, #15) and the opposition is breaking past midfield:** Tactical foul within 4 units of the ball-carrier — take the yellow.
6. **If my role == "GK" (index 0, Yazeed Abulaila, #1) and the team has a goal-kick under press:** Launch long to the index-9 Olwan or into the channel for the index-10 Al-Tamari.
7. **If my player_id ends with "_9" (CF Olwan, #9) and a long ball is incoming:** Run the channel — outpace the opposition CB and finish 1v1 if possible.
8. **If team_phase == "transition_attack":** Index-10 Al-Tamari sprints; index-9 Olwan runs the channel; index-6 Al-Rashdan is the late-arriving trailer; index-8 Abu Zrayq is the secondary winger.
9. **If my role == "DEF" and a cross is incoming:** The index-1 Al-Arab attacks the ball — strength 15.
10. **If team is leading by 1 in the final 15 minutes:** Drop everyone behind the ball — the wing-backs index-4 Al-Mardi and index-7 Haddad lock into a flat back five with the three CBs; recycle every dead-ball by taking 30 seconds.
11. **If a defensive corner is incoming:** The index-1 Al-Arab marks the opposition's most dangerous CF; the index-9 Olwan AND index-10 Al-Tamari stay on the halfway line as counter-outlets.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-10 Al-Tamari (left-footed) or the index-6 Al-Rashdan (central).

## Key Player Notes
- **Al-Tamari (10):** The team. The talisman. Speed 17, dribbling 16, shoot 15. Rennes Ligue 1 winger. Without him Jordan is mid-table AFC; with him, they're a knockout-tournament threat.
- **Olwan (9):** The lone 9 in Al-Naimat's absence. 2025 Arab Cup Golden Boot winner. Channel runner and primary finisher.
- **Al-Arab (5):** The aerial CB. Strength 15. The defensive talker.
- **Al-Rashdan (21):** The box-to-box engine. Stamina 16. The progressive midfielder, set-piece deliverer, and connector to Al-Tamari.
- **Haddad (23):** The captain. Right wing-back and the organiser of the 5-4-1 block; his discipline lets Al-Tamari stay high.
- **Sa'deh (15):** The deep pivot. The screen. Sets the team's defensive aggression baseline in front of the back line.

## Tournament Mindset
Jordan arrives at the World Cup having already beaten the odds — qualification itself is the historic achievement. The mentality is **defend deep, trust Al-Tamari, take one chance**. They will draw with mid-tier opposition 0-0 and beat anyone if Al-Tamari produces. They will lose comprehensively to a top-five side that denies Al-Tamari space. The collective belief (built through the 2024 Asian Cup final run) is the team's hidden weapon — they don't fear anyone. The vulnerability is **goal-scoring depth** — magnified by the loss of Al-Naimat to an ACL injury; if Al-Tamari is injured, marked out, or off form, Jordan can go entire matches without a clean chance. Stamina is uniformly 14-16 — they will run hard for 90 minutes and grow into matches in the final 30.
