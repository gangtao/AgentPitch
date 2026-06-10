# Iraq — Tactical Profile

## Identity & Philosophy
Iraq under **Graham Arnold** (the former Australia head coach hired to professionalise the side) is **direct, physical, and ruthlessly organized** — a team that has finally ended a 40-year World Cup absence, qualifying through the AFC route under Arnold and into Group I alongside France, Senegal and Norway. Arnold's identity is **Anglo-Saxon work-rate + Iraqi technical flair**: hard pressing, vertical transitions, intelligent set-piece routines, and just enough creative spark from Zidane Iqbal to combine the two cultures. The final 26 (announced 1 June 2026) blends an experienced, set-piece-savvy spine with a nine-strong European contingent (Iqbal at Utrecht, Al-Hamadi at Ipswich, Ali Jassim at Como, Ahmed Qasem at Nashville, Al-Ammari at Cracovia). Iraq is the **physical bully** of the AFC region after Iran — they will out-run, out-jump, and out-foul most opponents while remaining tactically disciplined. Arnold has brought a level of professional structure the team has lacked for years.

## Formation
- Shape: **4-4-2** in possession (two flat banks of four out of possession; **4-5-1** against superior opposition with Al-Hamadi dropping into midfield).
- Role mapping (roster order in `iraq.yaml`):
  - index 0: GK — **Jalal Hassan** (#12, captain) — traditional shot-stopper, less of a sweeper; commands his box with the back four sitting in front.
  - index 1: LB — **Merchas Doski** (#23) — most attacking of the back four, the natural width-giver on the left; overlapping fullback.
  - index 2: LCB — **Rebin Sulaka** (#2) — aerial dominator (strength 15), the duel-winner, the defensive talker.
  - index 3: RCB — **Zaid Tahseen** (#4) — physical partner (strength 15), wins headers in both boxes.
  - index 4: RB — **Hussein Ali** (#3, Pogoń Szczecin) — disciplined fullback, defensive-first, rarely overlaps deep.
  - index 5: LM — **Ibrahim Bayesh** (#8) — the chief creator from the left, cuts inside, late runs into the box, set-piece taker.
  - index 6: LCM — **Amir Al-Ammari** (#16) — the destroyer, the screen, the tactical fouler.
  - index 7: RCM — **Zidane Iqbal** (#14) — Manchester United academy product (now at FC Utrecht), the technical heartbeat, the press-resistant midfielder. Skill 15, pass 15, dribbling 14. The team's only true playmaker.
  - index 8: RM — **Youssef Amyn** (#7) — tricky, direct right-sided dribbler (dribbling 15), cuts inside onto his left foot, the wide spark.
  - index 9: ST — **Aymen Hussein** (#18) — the target forward, hold-up player, aerial threat. Strength 15, shoot 15. The team's leading scorer.
  - index 10: ST — **Ali Al-Hamadi** (#9, Ipswich) — energetic second striker, runs the channels off Aymen Hussein and leads the press.

## Style of Play

### Build-up
Direct. Iraq builds from the back when uncontested but goes long the moment any press arrives. The chief progressor is Zidane Iqbal — he drops between the CBs to receive, turns, and either dribbles or fires a vertical pass. The default long ball is aimed at Aymen Hussein for a knock-down to Al-Hamadi running off him or Bayesh arriving from the left. Iraq does NOT prioritize possession — they prioritize verticality.

### Pressing
**Mid-block, hard-running, trigger-based.** Iraq drops to the halfway line and waits. Triggers: opposition GK takes a heavy touch, back-pass under duress, opposition midfielder receives on the half-turn. Aymen Hussein and Al-Hamadi lead the press as a front two with curving runs. Bayesh and Amyn jump from the wings. Al-Ammari is the central duel-winner. The press is hard but selective — Iraq's stamina ratings (mostly 14-15) can't sustain a 90-minute high press.

### Defensive shape
Compact **4-4-2**: Bayesh and Amyn drop into a flat midfield four alongside Al-Ammari and Iqbal, while Al-Hamadi drops onto the opposition pivot and Aymen Hussein screens the deepest CB. The back four sits 22-25 units off goal. Against elite opposition Iraq drops to **4-5-1** with Al-Hamadi joining the midfield line and Aymen Hussein alone up top.

### Wide play
**Asymmetric.** Left side: Bayesh cuts inside, Doski overlaps for the natural width. Right side: Amyn drifts inside onto his left foot, Hussein Ali stays deep as cover (no overlap). The crosses come from the left (Doski) and from deep set-pieces. Iraq is a **crossing team** when they get behind the opposition fullback — Aymen Hussein attacks the near post.

### Final third
Patterns: long ball to Aymen Hussein's chest, knock-down to Al-Hamadi's run or Bayesh's late arrival, shot from 18 yards. Doski's left-flank cross to Aymen Hussein at the near post. Iqbal's slipped through-ball to Al-Hamadi sprinting in behind. Iraq creates 3-5 chances per match — they need to be clinical and rely on Aymen Hussein's aerial finishing.

## Set Pieces
**Iraq is a set-piece-dangerous side** with Sulaka and Tahseen as aerial threats in both boxes.
- Attacking corners: **Bayesh** in-swingers from the right (left foot), **Iqbal** out-swingers from the left. Targets: Sulaka (penalty spot), Tahseen (back post), Aymen Hussein (near post flick-on).
- Defending corners: man-marking heavy. Sulaka marks the most dangerous opposition striker; Tahseen marks the second; four zonal markers; Jalal Hassan stays on the line.
- Free kicks: **Iqbal** direct from any angle within 27 yards; Bayesh from the right half-space.
- Penalties: **Aymen Hussein** primary, **Iqbal** secondary, **Bayesh** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Jalal Hassan, #12) and the team has a goal-kick:** Default to a long ball aimed at the index-9 Aymen Hussein, unless no opposition press is detected.
2. **If my player_id ends with "_9" (ST Aymen Hussein, #18) and a long ball is incoming:** Win the aerial duel — strength 15. Knock down to the index-10 Al-Hamadi or the index-5 Bayesh arriving from the left.
3. **If my player_id ends with "_7" (CM Iqbal, #14) and I have the ball in midfield:** Look first for the index-10 Al-Hamadi's channel-run; second, dribble forward (skill 15, dribbling 14); third, switch the play to the index-8 Amyn on the right.
4. **If team_phase == "defending" and the opposition is past midfield:** Drop into the **4-4-2** banks at the halfway line; collapse to **4-5-1** (index-10 Al-Hamadi into midfield) if ball enters my final third.
5. **If my player_id ends with "_6" (DM Al-Ammari, #16) and the opposition is breaking past midfield:** Tactical foul — Iraq is happy to take a yellow to stop a counter.
6. **If team_phase == "transition_attack":** Index-10 Al-Hamadi runs the channel; index-8 Amyn sprints diagonally; index-5 Bayesh is the trailer; index-7 Iqbal delivers the through-ball.
7. **If my player_id ends with "_8" (RM Amyn, #7) and I have the ball on the right flank:** Cut inside onto my left foot; Shoot if angle opens within 22 units.
8. **If my role == "DEF" and a cross is incoming into my box:** The index-2 Sulaka and index-3 Tahseen attack the ball — both win aerial duels (strength 15 each).
9. **If team is trailing in the final 20 minutes:** Push the index-2 Sulaka forward as an emergency 9 for every set-piece and late cross. Index-1 Doski and index-4 Hussein Ali push high.
10. **If a defensive corner is incoming:** The index-2 Sulaka marks the opposition's most dangerous CF; the index-3 Tahseen marks the second; the index-9 Aymen Hussein stays on the halfway line as a counter-outlet.
11. **If my player_id ends with "_1" (LB Doski, #23) and team_phase == "attacking":** Overlap on the left — the index-5 Bayesh cutting inside opens the space.
12. **Set-pieces 20-30 yards from goal:** Defer dead-ball to the index-7 Iqbal (central) or the index-5 Bayesh (right half-space).

## Key Player Notes
- **Zidane Iqbal (7):** The Man United academy / Utrecht playmaker. The technical heartbeat. Iraq's first World Cup ever has him as the cultural symbol of a new generation.
- **Aymen Hussein (9):** The target 9. Aerial. Hold-up. The team's leading scorer.
- **Sulaka (2) / Tahseen (3):** The aerial CB pair. Strength 15 each. Set-piece weapons in both boxes.
- **Bayesh (5):** The creator from the left. Late runner. Set-piece deliverer.
- **Al-Hamadi (10):** The Ipswich striker. Channel-runner and press-leader off Aymen Hussein. The team's second goal threat.
- **Amyn (8):** The right-sided dribbler (dribbling 15). Cuts inside, combines, shoots.
- **Bench depth (final 26):** Ali Jassim (Como) is the standout young forward off the bench and the most likely to break the projected XI on a strong tournament — a wide/second-striker option who can replace Amyn or Al-Hamadi. Ahmed Qasem (Nashville), Aimar Sher (Sarpsborg) and Kevin Yakob (AGF) add European-based midfield cover; Frans Putros and Manaf Younis are defensive depth; Fahad Talib and Ahmed Basil back up Jalal Hassan in goal.

## Tournament Mindset
Iraq has qualified for its first World Cup in 40 years — the entire country is behind this team. Drawn in Group I with France, Senegal and Norway, the realistic ceiling is competitiveness and pride. The mentality is **honour the shirt, escape the group if everything breaks right, never embarrass ourselves**. They will compete physically with any opponent and frustrate technical sides. Arnold has installed Australian-style discipline: no soft goals, no silly red cards, no panic. The vulnerability is creativity against an organized defence — Iraq depends on Iqbal having a great game, and if he is well-marked, the team can go entire halves without a clean chance. Stamina is a concern (mostly 14-15) — Iraq will start strongly and may tire in the final 20 minutes against a deeper squad. Set-pieces are the realistic goal source against superior opposition.
