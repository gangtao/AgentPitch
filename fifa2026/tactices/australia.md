# Australia — Tactical Profile

## Identity & Philosophy
Tony Popovic's Australia is the platonic ideal of an **organized, hard-running, set-piece-reliant** side — the modern Socceroos identity inherited from Ange Postecoglou and refined into something more pragmatic. The team is built on **structural discipline, aerial dominance, and a clear plan to score from dead-balls or counter-attacks**, with just enough creative spark from Ajdin Hrustic and Craig Goodwin to produce one open-play goal per match. Australia rarely dominates possession against top opposition; they don't need to. The squad is **fitness-obsessed** (every outfielder rated 14+ stamina), tactically literate, and led by veterans Mat Ryan, Aziz Behich, and Jackson Irvine who have been through three World Cups. Recent form: comfortable through Asian qualifying after a slow start under previous management, with Popovic restoring discipline and shape; the 2022 round-of-16 run remains the benchmark.

## Formation
- Shape: **4-2-3-1** in possession (slides to **4-4-1-1** out of possession, or **4-5-1** against superior opposition).
- Role mapping (roster order in `australia.yaml`):
  - index 0: GK — **Mat Ryan** — veteran captain, the team's leader, vocal organizer, sweeper-keeper when needed but more comfortable on his line. Hundreds of caps; the calming presence.
  - index 1: LB — **Aziz Behich** — overlapping veteran left-back, hard-runner, the natural width-giver on the left because Goodwin tucks inside.
  - index 2: LCB — **Harry Souttar** — the 6'7" aerial monster (strength 17), set-piece weapon in both boxes, wins everything in the air, slightly slower on the ground.
  - index 3: RCB — **Kye Rowles** — Souttar's calmer partner, the ball-player, sweeps in behind, covers Souttar's lack of pace.
  - index 4: RB — **Nathaniel Atkinson** — energetic, overlapping right-back, the speedster of the back four.
  - index 5: DM/6 — **Ajdin Hrustic** — actually deployed in the AM/10 role in the 4-2-3-1; in this roster ordering he sits in the deeper midfield slot but tactically is the creator. The technical heart of the team, set-piece taker, long-shot threat.
  - index 6: DM — **Jackson Irvine** — captain in the midfield, the all-action box-to-box engine, stamina 17, late runs into the box, the team's leading midfield goal-scorer.
  - index 7: AM — **Riley McGree** — the press-resistant, ball-carrying midfielder, drifts to the right half-space to combine with Atkinson.
  - index 8: CM — **Connor Metcalfe** — the disciplined double-pivot partner, screens the back four, recycles possession.
  - index 9: LW — **Craig Goodwin** — veteran left-winger, in-swinging set-piece taker, cuts inside on his right foot, the team's leading wide-area creator.
  - index 10: CF — **Martin Boyle** / lone forward — the pacy 9, runs the channel, presses from the front, finishes inside the box.

(Note: the roster's `MID` block is deep and the actual on-pitch arrangement reads as Hrustic-Irvine double pivot with McGree as AM and Goodwin/Boyle wide of the lone striker; the engine should accept this fluid front-six.)

## Style of Play

### Build-up
Pragmatic. Australia builds from the back when uncontested but goes long the moment any press arrives. Mat Ryan is comfortable with his feet but defaults to a goal-kick aimed at Souttar or the channels. Hrustic is the chief progressor — he drops between the lines to receive from the CBs, turns, and either dribbles or fires a diagonal. The first long ball is typically aimed at Boyle running the channel; the second is aimed at Souttar arriving late for a set-piece. Australia is content to play 40% possession against superior opposition.

### Pressing
**Mid-block, trigger-based.** Australia does not high-press. They retreat to the halfway line, compress, and wait. Triggers: a back-pass to the opposition GK, a heavy first touch, or a throw-in. When triggered, Boyle leads the press with curving runs, and McGree jumps the opposition pivot. Irvine is the central duel-winner. The press is hard-running but not constant — Australia conserves stamina for the final 20 minutes.

### Defensive shape
Compact **4-4-1-1** with Goodwin and McGree forming the wide midfield (Goodwin drops from LW to LM; McGree shifts from AM to RM). Hrustic and Irvine are the double pivot. Boyle stays high as the lone presser. The back four holds a medium line. Against elite opposition Australia drops to **4-5-1** with all three of Hrustic/Irvine/McGree narrow in front of the back four.

### Wide play
Asymmetric. Left side: Goodwin cuts inside, Behich overlaps for the natural width. Right side: McGree drifts to the half-space, Atkinson sprints down the touchline. The crosses come from deep (35-40 yards out) and are aimed at Souttar, Irvine (late runner), or Boyle at the near post. Australia is a **crossing team** — they live and die by the quality of the ball into the box.

### Final third
Patterns: Hrustic's slipped through-ball to Boyle sprinting in behind; Goodwin's in-swinging cross from the left to Souttar (Souttar pushes forward for set-pieces and late corners); McGree's cut-back from the right by-line to Irvine's late run; Hrustic's long-range curler from 25 yards. Australia creates 4-6 chances per match — they need to convert one and rely on Souttar or set-pieces for the second.

## Set Pieces
**Australia is a set-piece monster.** Souttar is the focal aerial weapon in both boxes; Goodwin and Hrustic are elite in-swing deliverers.
- Attacking corners: **Goodwin** in-swingers from the left (right foot), **Hrustic** in-swingers from the right (left foot). Targets: Souttar (penalty spot, primary), Rowles (back post, late runner), Irvine (near post, flick-on).
- Defending corners: hybrid — Souttar attacks the first ball; Rowles marks the most dangerous opposition CF; four zonal markers across the six-yard line; Ryan stays on the goal line.
- Free kicks: Hrustic direct from any angle within 27 yards (left foot); Goodwin direct from the left half-space (right foot).
- Throw-ins in the attacking third: aim for Souttar arriving from CB.
- Penalties: **Hrustic** primary, **Goodwin** secondary, **Irvine** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Mat Ryan, #1) and the team has a goal-kick:** Default to a long kick aimed at the index-2 Souttar or into the channel for the index-10 Boyle, unless no opposition press is detected (then short to the index-3 Rowles).
2. **If my player_id ends with "_2" (LCB Souttar, #19) and an attacking corner or cross is incoming:** Sprint to the penalty spot — attack the ball aggressively. Strength 17, aerial dominator.
3. **If my player_id ends with "_5" (Hrustic, #13) and I am within 27 units of the opposition goal with the ball:** Shoot if angle is open; otherwise look for the index-10 Boyle's run in behind.
4. **If my player_id ends with "_6" (DM Irvine, #22) and team_phase == "attacking":** Late run from deep into the box — arrive on the back post for crosses or cut-backs.
5. **If my player_id ends with "_10" (CF Boyle, #9) and the ball is in midfield:** Run the channel behind the opposition RB — receive long diagonals from the index-5 Hrustic.
6. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-4-1-1** — index-9 Goodwin to LM, index-7 McGree to RM, index-5 Hrustic and index-6 Irvine narrow.
7. **If team_phase == "transition_defense":** Hard tactical foul within 4 units of the ball-carrier in midfield — STOP the counter. Australia is comfortable taking a yellow to break up a transition.
8. **If my role == "DEF" and a defensive corner is incoming:** The index-2 Souttar marks the opposition's most dangerous CF; the index-3 Rowles covers behind Souttar; the index-4 Atkinson and index-1 Behich on the posts.
9. **If team is trailing by 1 in the final 15 minutes:** Push the index-2 Souttar forward as an emergency 9 for every set-piece and cross.
10. **If my player_id ends with "_9" (LW Goodwin, #11) and I have the ball on the left flank:** Whip an in-swinging cross to the index-2 Souttar at the penalty spot, OR cut inside and Shoot.
11. **If team_phase == "attacking" and possession is settled in the opposition half:** Send the index-4 Atkinson and index-1 Behich high simultaneously; Australia plays 2-3-5 with width.
12. **Set-pieces 22-30 yards from goal (central):** Defer to the index-5 Hrustic.

## Key Player Notes
- **Souttar (2):** The 6'7" aerial weapon. Goal threat at every set-piece. Slightly slow on the ground — protect him with Rowles covering.
- **Hrustic (5):** The creator. Set-piece taker. Long-range shooter. The technical glue that turns Australian honest work into goals.
- **Irvine (6):** Captain in midfield. Stamina 17. Late-run goal threat. Box-to-box.
- **Mat Ryan (0):** The veteran captain. Calming presence. Hundreds of international caps.
- **Boyle (10):** The lone 9. Pacy. Runs the channel. Presses from the front. Finishes from inside the box.

## Tournament Mindset
Australia has a clear ceiling — round-of-16 is the realistic upper bound, and group-stage exit is the danger if drawn into a tough group. The mentality is **win the games we can, draw the games we should lose, never embarrass the shirt**. They will beat any team rated below them through sheer organization and set-pieces. Against a top-eight opponent, they will sit deep, foul tactically, and hope for one Hrustic set-piece moment. Stamina is the squad-wide superpower — Australia gets stronger in the 75th minute. The vulnerability is creativity against an organized opponent who denies set-pieces — Australia can struggle to break down a deep block.
