# Iraq — Tactical Profile

## Identity & Philosophy
Iraq under **Graham Arnold** (the former Australia head coach hired to professionalise the side) is **direct, physical, and ruthlessly organized** — a team that has finally translated its talent into qualification after decades of near-misses. Arnold's identity is **Anglo-Saxon work-rate + Iraqi technical flair**: hard pressing, vertical transitions, intelligent set-piece routines, and just enough creative spark from Zidane Iqbal to combine the two cultures. Iraq is the **physical bully** of the AFC region after Iran — they will out-run, out-jump, and out-foul most opponents while remaining tactically disciplined. Recent form: 2023 Asian Cup quarter-final exit (controversially to Jordan), through the AFC third round with momentum, with Arnold bringing a level of professional structure the team has lacked for years.

## Formation
- Shape: **4-2-3-1** in possession (drops to **4-4-1-1** out of possession, **4-5-1** against superior opposition).
- Role mapping (roster order in `iraq.yaml`):
  - index 0: GK — **Jalal Hassan** — traditional shot-stopper, less of a sweeper; commands his box with the back four sitting in front.
  - index 1: LB — **Hussein Ali Al-Saedi** — disciplined fullback, defensive-first, rarely overlaps deep.
  - index 2: LCB — **Rebin Sulaka** — aerial dominator (strength 15), the duel-winner, the defensive talker.
  - index 3: RCB — **Zaid Tahseen** — physical partner (strength 15), wins headers in both boxes.
  - index 4: RB — **Merchas Doski** — most attacking of the back four, the natural width-giver on the right; overlapping fullback.
  - index 5: DM — **Amir Al-Ammari** — the destroyer, the screen, the tactical fouler.
  - index 6: DM/CM — **Zidane Iqbal** — Manchester United academy product (now at FC Utrecht), the technical heartbeat, the press-resistant midfielder. Skill 15, pass 15, dribbling 14. The team's only true playmaker.
  - index 7: LW/AM — **Ali Al-Hamadi** — versatile, energetic attacker; in the 4-2-3-1 he often plays as the LW with license to drift inside.
  - index 8: AM — **Ibrahim Bayesh** — the #10 in the 4-2-3-1, the creator, late runs into the box, set-piece taker.
  - index 9: RW — **Mohanad Ali** — pacy right winger, cuts inside on his left foot, the team's second goal threat.
  - index 10: CF — **Aymen Hussein** — the lone 9, the target forward, hold-up player, aerial threat. Strength 15, shoot 15. The team's leading scorer.

## Style of Play

### Build-up
Direct. Iraq builds from the back when uncontested but goes long the moment any press arrives. The chief progressor is Zidane Iqbal — he drops between the CBs to receive, turns, and either dribbles or fires a vertical pass. The default long ball is aimed at Aymen Hussein for a knock-down to Bayesh arriving from the #10 position. Iraq does NOT prioritize possession — they prioritize verticality.

### Pressing
**Mid-block, hard-running, trigger-based.** Iraq drops to the halfway line and waits. Triggers: opposition GK takes a heavy touch, back-pass under duress, opposition midfielder receives on the half-turn. Aymen Hussein leads the press from the front with curving runs. Mohanad Ali and Ali Al-Hamadi jump from the wings. Al-Ammari is the central duel-winner. The press is hard but selective — Iraq's stamina ratings (mostly 14-15) can't sustain a 90-minute high press.

### Defensive shape
Compact **4-4-1-1** with Al-Hamadi and Mohanad Ali forming the wide midfield (both drop into a flat four with Al-Ammari and Iqbal). Bayesh tucks alongside Aymen Hussein as a second forward in pressing situations, dropping into a midfield five when defending deep. The back four sits 22-25 units off goal. Against elite opposition Iraq drops to **4-5-1** with Iqbal alongside Al-Ammari as a double pivot.

### Wide play
**Asymmetric.** Right side: Mohanad Ali cuts inside, Doski overlaps for the natural width. Left side: Al-Hamadi drifts inside, Al-Saedi stays deep as cover (no overlap). The crosses come from the right (Doski) and from deep set-pieces. Iraq is a **crossing team** when they get behind the opposition fullback — Aymen Hussein attacks the near post.

### Final third
Patterns: long ball to Aymen Hussein's chest, knock-down to Bayesh's late run, shot from 18 yards. Doski's right-flank cross to Aymen Hussein at the near post. Iqbal's slipped through-ball to Mohanad Ali sprinting in behind. Iraq creates 3-5 chances per match — they need to be clinical and rely on Aymen Hussein's aerial finishing.

## Set Pieces
**Iraq is a set-piece-dangerous side** with Sulaka and Tahseen as aerial threats in both boxes.
- Attacking corners: **Bayesh** in-swingers from the right (left foot), **Iqbal** out-swingers from the left. Targets: Sulaka (penalty spot), Tahseen (back post), Aymen Hussein (near post flick-on).
- Defending corners: man-marking heavy. Sulaka marks the most dangerous opposition striker; Tahseen marks the second; four zonal markers; Jalal Hassan stays on the line.
- Free kicks: **Iqbal** direct from any angle within 27 yards; Bayesh from the right half-space.
- Penalties: **Aymen Hussein** primary, **Iqbal** secondary, **Bayesh** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Jalal Hassan, #1) and the team has a goal-kick:** Default to a long ball aimed at the index-10 Aymen Hussein, unless no opposition press is detected.
2. **If my player_id ends with "_10" (CF Aymen Hussein, #11) and a long ball is incoming:** Win the aerial duel — strength 15. Knock down to the index-8 Bayesh or hold up for a runner.
3. **If my player_id ends with "_6" (CM Iqbal, #8) and I have the ball in midfield:** Look first for the index-10 Aymen Hussein's channel-run; second, dribble forward (skill 15, dribbling 14); third, switch the play to the index-9 Mohanad Ali on the right.
4. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-4-1-1** at the halfway line; collapse to **4-5-1** if ball enters my final third.
5. **If my player_id ends with "_5" (DM Al-Ammari, #6) and the opposition is breaking past midfield:** Tactical foul — Iraq is happy to take a yellow to stop a counter.
6. **If team_phase == "transition_attack":** Index-10 Aymen Hussein runs the channel; index-9 Mohanad Ali sprints diagonally; index-8 Bayesh is the trailer; index-6 Iqbal delivers the through-ball.
7. **If my player_id ends with "_9" (RW Mohanad Ali, #9) and I have the ball on the right flank:** Cut inside onto my left foot; Shoot if angle opens within 22 units.
8. **If my role == "DEF" and a cross is incoming into my box:** The index-2 Sulaka and index-3 Tahseen attack the ball — both win aerial duels (strength 15 each).
9. **If team is trailing in the final 20 minutes:** Push the index-2 Sulaka forward as an emergency 9 for every set-piece and late cross. Index-4 Doski and index-1 Al-Saedi push high.
10. **If a defensive corner is incoming:** The index-2 Sulaka marks the opposition's most dangerous CF; the index-3 Tahseen marks the second; the index-10 Aymen Hussein stays on the halfway line as a counter-outlet.
11. **If my player_id ends with "_4" (RB Doski, #2) and team_phase == "attacking":** Overlap on the right — the index-9 Mohanad Ali cutting inside opens the space.
12. **Set-pieces 20-30 yards from goal:** Defer dead-ball to the index-6 Iqbal (central) or the index-8 Bayesh (right half-space).

## Key Player Notes
- **Zidane Iqbal (6):** The Man United academy / Utrecht playmaker. The technical heartbeat. Iraq's first World Cup ever has him as the cultural symbol of a new generation.
- **Aymen Hussein (10):** The target 9. Aerial. Hold-up. The team's leading scorer.
- **Sulaka (2) / Tahseen (3):** The aerial CB pair. Strength 15 each. Set-piece weapons in both boxes.
- **Bayesh (8):** The #10 creator. Late runner. Set-piece deliverer.
- **Mohanad Ali (9):** The pacy right winger. Cuts inside, shoots. The team's second goal threat.

## Tournament Mindset
Iraq has qualified for its first World Cup in 40 years — the entire country is behind this team. The mentality is **honour the shirt, escape the group if everything breaks right, never embarrass ourselves**. They will compete physically with any opponent and frustrate technical sides. Arnold has installed Australian-style discipline: no soft goals, no silly red cards, no panic. The vulnerability is creativity against an organized defence — Iraq depends on Iqbal having a great game, and if he is well-marked, the team can go entire halves without a clean chance. Stamina is a concern (mostly 14-15) — Iraq will start strongly and may tire in the final 20 minutes against a deeper squad. Set-pieces are the realistic goal source against superior opposition.
