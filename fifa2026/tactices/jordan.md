# Jordan — Tactical Profile

## Identity & Philosophy
Jordan are the **fairytale story of Asian football** — the 2024 Asian Cup runners-up who shocked South Korea in the semi-final, qualifying for their first-ever World Cup. The team's identity, built under Hussein Ammouta and now Jamal Sellami, is **compact defensive organisation + lightning-fast counter-attacks via Musa Al-Tamari**. Jordan plays a deeper block than any Asian qualifier, conserves stamina obsessively, and unleashes its one world-class player on every transition. The collective belief in this group is **the highest among AFC second-tier sides** — they have already beaten Iraq, South Korea, and drawn with Saudi Arabia in knockout football. Recent form: comfortable through AFC qualifying, the 2024 Asian Cup final loss to Qatar still motivating, with Al-Tamari now an established starter at Rennes (Ligue 1) and one of the most underrated players in Europe. **Major blow for the World Cup: first-choice striker Yazan Al-Naimat is OUT with an ACL injury (surgery after the 2024 Arab Cup)** — Sellami must replace his goals, with 2025 Arab Cup Golden Boot winner Ali Olwan leading the line.

**MD1 result: Austria 3-1 Jordan.** Jordan competed well in the first half (trailed 1-0 to a Schmid wonder-strike), equalised through Olwan at 50', but then collapsed — Yazan Al-Arab's own goal from a corner (76') and a late Arnautovic penalty (90+12') after Saleem Obaid's handball. Sellami is expected to **switch from the 3-4-3/5-4-1 to a 4-3-3** for MD2 against Algeria, bringing in Sa'deh and Al-Rawabdeh to add midfield control. No injuries or suspensions from MD1.

## Formation
- Shape: **4-3-3** in possession (collapses to a **4-5-1 mid-block** out of possession — the wingers tuck in alongside the midfield three). Sellami switched from the MD1 back three after conceding three goals to Austria.
- Role mapping (roster order in `jordan.yaml`):
  - index 0: GK — **Yazeed Abulaila** (#1) — traditional shot-stopper, less of a sweeper; commands his box; the calm presence behind the defensive line.
  - index 1: LB — **Yazan Al-Arab** (#5) — physical (strength 15), the aerial duel-winner, the defensive talker; moved to left-back from left centre-back to give more width.
  - index 2: LCB — **Abdallah Nasib** (#3) — the central organiser; disciplined and positionally sound, the senior CB.
  - index 3: RCB — **Mo Abualnadi** (#16) — started MD1 at centre-back; steady and physical, replaces Abu Dahab in the starting XI.
  - index 4: RB — **Ehsan Haddad** (#23) — the captain; disciplined right-back who organises the defence, modest going forward but never beaten twice. Moved from RWB to RB.
  - index 5: LCM — **Noor Al-Rawabdeh** (#8) — energetic box-to-box midfielder who started MD1; adds pressing intensity and ball-carrying from deep.
  - index 6: CM — **Ibrahim Sa'deh** (#15) — the screen in front of the back line, recycles possession, the deep pivot. Restored to the starting XI for MD2 after being dropped for MD1.
  - index 7: RCM — **Nizar Al-Rashdan** (#21) — the box-to-box engine, late runs into the box, stamina 16; the most progressive midfielder and a connector to Al-Tamari.
  - index 8: LW — **Mohammad Abu Zrayq** (#7) — direct left-sided forward, the third forward in transitions, the secondary outlet on the break.
  - index 9: CF — **Ali Olwan** (#9) — the lone 9 now that Al-Naimat is injured; 2025 Arab Cup Golden Boot winner, the channel runner and primary finisher, the press-leader. **Scored against Austria (50') — confidence is high.**
  - index 10: RW — **Musa Al-Tamari** (#10) — the star, the talisman, the captain in spirit. Speed 17, dribbling 16, shoot 15. Plays at Rennes in Ligue 1. Cuts inside from the right onto his left foot or sprints down the line; the team's only world-class attacker.

## Style of Play

### Build-up
Pragmatic and direct. Jordan does NOT play out from the back against pressing opponents — Abulaila will launch a long ball to Olwan or down the channel for Al-Tamari to chase. When build-up is possible, the back four splits and the team plays short through Sa'deh as the deep pivot, with Al-Rashdan stepping up to connect and the fullbacks Al-Arab and Haddad offering the wide outlets. The first instinct is always **find Al-Tamari in space on the right wing** — once he has the ball facing forward, Jordan is dangerous.

### Pressing
**Low to mid-block. No high press.** Jordan retreats to a compact shape inside their own half and waits. Triggers: opposition pass into a wide channel (the fullback + winger close down), heavy first touch in midfield (Sa'deh jumps). Olwan presses occasionally but mostly stays high as the counter-attack outlet. The team conserves stamina for the final 30 minutes when they will run a tired opponent into the ground via Al-Tamari.

### Defensive shape
Compact **4-5-1 mid-block** — this is the default shape. The fullbacks Al-Arab and Haddad hold the back four at 22-25 units off goal. Abu Zrayq tucks in to LM and Al-Tamari tracks back to RM (he tracks back diligently — a non-negotiable from the staff). Olwan is the lone front presser. The midfield band (Abu Zrayq, Al-Rawabdeh, Sa'deh, Al-Rashdan, Al-Tamari) sits in a compact line 28-30 units off goal. The 4-3-3 → 4-5-1 collapse provides better cover against the wide overloads that hurt Jordan vs Austria.

### Wide play
Almost everything runs through Al-Tamari on the right. He cuts inside onto his left foot or sprints down the touchline depending on the defender's positioning, with Haddad's underlap behind him for security rather than overlap. The left side (Abu Zrayq + Al-Arab overlapping) is the secondary outlet. Jordan does not cross much — they prefer Al-Tamari to dribble inside and shoot.

### Final third
Patterns: **Al-Tamari isolated 1v1 on the right, dribbles inside, shoots**. Long ball over the top for Al-Tamari to chase with his 17 speed. Cut-back from Al-Tamari to Olwan at the near post. Al-Rashdan's slipped through-ball to Olwan sprinting in behind. Jordan creates 2-4 chances per match — they need to be clinical and depend on Al-Tamari producing one moment. **Without Al-Naimat's aerial presence, goal-scoring depth is the team's biggest concern.** Olwan's goal against Austria has boosted morale.

## Set Pieces
- Attacking corners: **Al-Rashdan** in-swingers from the left, **Al-Tamari** in-swingers from the right (left foot). Targets: Al-Arab (penalty spot), Nasib (back post), Olwan (near post flick-on).
- Defending corners: man-marking heavy. Al-Arab marks the most dangerous opposition striker; four zonal markers; Abulaila stays on his line. **Must improve set-piece defending after conceding from a corner vs Austria (Al-Arab own goal).**
- Free kicks: **Al-Tamari** direct from the right half-space (left-footed), **Al-Rashdan** from central range.
- Penalties: **Al-Tamari** primary, **Olwan** secondary, **Al-Rashdan** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_10" (RW Al-Tamari, #10) and team_phase == "transition_attack":** Sprint diagonally inside or down the touchline — my speed 17 is the team's primary weapon.
2. **If my player_id ends with "_10" (RW Al-Tamari, #10) and I have the ball on the right with no defender within 4 units:** Dribble inside onto my left foot; Shoot if angle opens within 23 units.
3. **If my player_id ends with "_10" (RW Al-Tamari, #10) and team_phase == "defending":** Drop to RM and track back diligently — non-negotiable from the staff. Conserve stamina for transitions.
4. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-5-1 mid-block** — fullbacks index-1 Al-Arab and index-4 Haddad hold the back four at 22-25 units, midfield five at 28-30 units; do not push higher.
5. **If my player_id ends with "_6" (CM Sa'deh, #15) and the opposition is breaking past midfield:** Tactical foul within 4 units of the ball-carrier — take the yellow.
6. **If my role == "GK" (index 0, Yazeed Abulaila, #1) and the team has a goal-kick under press:** Launch long to the index-9 Olwan or into the channel for the index-10 Al-Tamari.
7. **If my player_id ends with "_9" (CF Olwan, #9) and a long ball is incoming:** Run the channel — outpace the opposition CB and finish 1v1 if possible.
8. **If team_phase == "transition_attack":** Index-10 Al-Tamari sprints; index-9 Olwan runs the channel; index-7 Al-Rashdan is the late-arriving trailer; index-8 Abu Zrayq is the secondary winger.
9. **If my role == "DEF" and a cross is incoming:** The index-1 Al-Arab attacks the ball — strength 15.
10. **If team is leading by 1 in the final 15 minutes:** Drop everyone behind the ball — compact 4-5-1, recycle every dead-ball by taking 30 seconds.
11. **If a defensive corner is incoming:** The index-1 Al-Arab marks the opposition's most dangerous CF; the index-9 Olwan AND index-10 Al-Tamari stay on the halfway line as counter-outlets.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-10 Al-Tamari (left-footed) or the index-7 Al-Rashdan (central).

## Key Player Notes
- **Al-Tamari (10):** The team. The talisman. Speed 17, dribbling 16, shoot 15. Rennes Ligue 1 winger. Without him Jordan is mid-table AFC; with him, they're a knockout-tournament threat.
- **Olwan (9):** The lone 9 in Al-Naimat's absence. 2025 Arab Cup Golden Boot winner. Channel runner and primary finisher. **Scored vs Austria — confidence high.**
- **Al-Arab (5):** The aerial FB. Strength 15. The defensive talker. Must recover mentally from the own goal vs Austria.
- **Al-Rashdan (21):** The box-to-box engine. Stamina 16. The progressive midfielder, set-piece deliverer, and connector to Al-Tamari.
- **Haddad (23):** The captain. Right-back and the organiser of the defence; his discipline lets Al-Tamari stay high.
- **Sa'deh (15):** The deep pivot. The screen. Sets the team's defensive aggression baseline in front of the back line. Restored to the XI for MD2.
- **Al-Rawabdeh (8):** Energetic box-to-box midfielder. Started MD1 vs Austria. Adds pressing intensity and ball-winning in the middle third.
- **Abualnadi (16):** Physical centre-back. Started MD1 vs Austria. Steady presence in the back four.

## Tournament Mindset
Jordan arrives at the World Cup having already beaten the odds — qualification itself is the historic achievement. The MD1 3-1 loss to Austria was a reality check: competitive for 76 minutes before set-piece and late-game fragility cost them. The mentality for MD2 is **must-win against Algeria (who also lost their opener 3-0 to Argentina)** — both teams on zero points, and the loser is effectively eliminated. The switch to 4-3-3 with Sa'deh screening aims to shore up the midfield control that was lacking in the back-three system. The belief remains: **defend deep, trust Al-Tamari, take one chance**. Olwan's goal against Austria proves they can score at this level.
