# Australia — Tactical Profile

## Identity & Philosophy
Tony Popovic's Australia is the platonic ideal of an **organized, hard-running, set-piece-reliant** side — the modern Socceroos identity inherited from Ange Postecoglou and refined into something more pragmatic. The team is built on **structural discipline, aerial dominance, and a clear plan to score from dead-balls or counter-attacks**, with just enough creative spark from Nishan Velupillay and Mathew Leckie to produce one open-play goal per match. Australia rarely dominates possession against top opposition; they don't need to. The squad is **fitness-obsessed** (every outfielder rated 14+ stamina), tactically literate, and led by veterans Mat Ryan, Mathew Leckie, and Jackson Irvine — Ryan and Leckie are each at a fourth World Cup. The 2026 group is heavily refreshed: seventeen first-time World Cup players, with a new young spine of Jordy Bos, Alessandro Circati, Aiden O'Neill and Mohamed Touré around the veteran core. Recent form: comfortable through Asian qualifying after a slow start under previous management, with Popovic restoring discipline and shape; the 2022 round-of-16 run remains the benchmark.

## Formation
- Shape: **4-2-3-1** in possession (slides to **4-4-1-1** out of possession, or **4-5-1** against superior opposition).
- Role mapping (roster order in `australia.yaml`):
  - index 0: GK — **Mat Ryan** (#1) — veteran captain, the team's leader, vocal organizer, sweeper-keeper when needed but more comfortable on his line. Fourth World Cup; the calming presence.
  - index 1: LB — **Jordy Bos** (#5) — flying young left-back, the natural width-giver on the left because Leckie tucks inside. Athletic, gets to the by-line, a genuine attacking outlet.
  - index 2: LCB — **Harry Souttar** (#19) — the 6'7" aerial monster (strength 17), set-piece weapon in both boxes, wins everything in the air, slightly slower on the ground.
  - index 3: RCB — **Alessandro Circati** (#3) — Souttar's composed young partner, the ball-player, sweeps in behind, covers Souttar's lack of pace and starts build-up with progressive passing.
  - index 4: RB — **Jacob Italiano** (#4) — energetic, overlapping right-back, the speedster of the back four.
  - index 5: DM/6 — **Aiden O'Neill** (#13) — the deep-lying organizer, screens the back four, dictates tempo and recycles possession; Popovic's preferred pivot anchor.
  - index 6: DM — **Jackson Irvine** (#22) — captain in the midfield, the all-action box-to-box engine, stamina 17, late runs into the box, the team's leading midfield goal-scorer.
  - index 7: AM — **Nishan Velupillay** (#23) — the press-resistant, ball-carrying attacking midfielder, drifts into half-spaces to combine, the chief open-play creative spark behind the striker.
  - index 8: CM/RW — **Connor Metcalfe** (#8) — the disciplined runner who provides the right-side width and works back; balances Velupillay's freedom and supports Italiano.
  - index 9: LW — **Mathew Leckie** (#7) — veteran wide forward, cuts inside, direct on the dribble, the team's experienced wide-area threat.
  - index 10: CF — **Mohamed Touré** (#9) / lone forward — the pacy 9, runs the channel, presses from the front, finishes inside the box.

(Note: the roster's `MID` block is deep and the actual on-pitch arrangement reads as O'Neill-Irvine double pivot with Velupillay as AM and Leckie/Metcalfe wide of the lone striker; the engine should accept this fluid front-six.)

## Style of Play

### Build-up
Pragmatic. Australia builds from the back when uncontested but goes long the moment any press arrives. Mat Ryan is comfortable with his feet but defaults to a goal-kick aimed at Souttar or the channels. Circati starts the progression from the back, while Velupillay is the chief between-the-lines progressor — he drops to receive from the CBs, turns, and either dribbles or fires a diagonal. The first long ball is typically aimed at Touré running the channel; the second is aimed at Souttar arriving late for a set-piece. Australia is content to play 40% possession against superior opposition.

### Pressing
**Mid-block, trigger-based.** Australia does not high-press. They retreat to the halfway line, compress, and wait. Triggers: a back-pass to the opposition GK, a heavy first touch, or a throw-in. When triggered, Touré leads the press with curving runs, and Velupillay jumps the opposition pivot. Irvine is the central duel-winner. The press is hard-running but not constant — Australia conserves stamina for the final 20 minutes.

### Defensive shape
Compact **4-4-1-1** with Leckie and Metcalfe forming the wide midfield (Leckie drops from LW to LM; Metcalfe shifts to RM). O'Neill and Irvine are the double pivot. Touré stays high as the lone presser. The back four holds a medium line. Against elite opposition Australia drops to **4-5-1** with all three of O'Neill/Irvine/Velupillay narrow in front of the back four.

### Wide play
Asymmetric. Left side: Leckie cuts inside, Bos overlaps for the natural width. Right side: Velupillay drifts to the half-space while Metcalfe and Italiano work the touchline. The crosses come from deep (35-40 yards out) and are aimed at Souttar, Irvine (late runner), or Touré at the near post. Australia is a **crossing team** — they live and die by the quality of the ball into the box.

### Final third
Patterns: Velupillay's slipped through-ball to Touré sprinting in behind; Leckie's in-swinging cross from the left to Souttar (Souttar pushes forward for set-pieces and late corners); Metcalfe/Italiano's cut-back from the right by-line to Irvine's late run; Velupillay's drive and long-range effort from the edge of the box. Australia creates 4-6 chances per match — they need to convert one and rely on Souttar or set-pieces for the second.

## Set Pieces
**Australia is a set-piece monster.** Souttar is the focal aerial weapon in both boxes; Leckie and Bos are the primary in-swing deliverers.
- Attacking corners: **Leckie** in-swingers from the left, **Velupillay** deliveries from the right. Targets: Souttar (penalty spot, primary), Circati (back post, late runner), Irvine (near post, flick-on).
- Defending corners: hybrid — Souttar attacks the first ball; Circati marks the most dangerous opposition CF; four zonal markers across the six-yard line; Ryan stays on the goal line.
- Free kicks: Velupillay direct from central range within 25 yards; Bos/Leckie direct deliveries from the left half-space.
- Throw-ins in the attacking third: aim for Souttar arriving from CB.
- Penalties: **Velupillay** primary, **Leckie** secondary, **Irvine** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Mat Ryan, #1) and the team has a goal-kick:** Default to a long kick aimed at the index-2 Souttar or into the channel for the index-10 Touré, unless no opposition press is detected (then short to the index-3 Circati).
2. **If my player_id ends with "_2" (LCB Souttar, #19) and an attacking corner or cross is incoming:** Sprint to the penalty spot — attack the ball aggressively. Strength 17, aerial dominator.
3. **If my player_id ends with "_7" (AM Velupillay, #23) and I am within 25 units of the opposition goal with the ball:** Shoot if angle is open; otherwise look for the index-10 Touré's run in behind.
4. **If my player_id ends with "_6" (DM Irvine, #22) and team_phase == "attacking":** Late run from deep into the box — arrive on the back post for crosses or cut-backs.
5. **If my player_id ends with "_10" (CF Touré, #9) and the ball is in midfield:** Run the channel behind the opposition RB — receive long diagonals from the index-7 Velupillay.
6. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-4-1-1** — index-9 Leckie to LM, index-8 Metcalfe to RM, index-5 O'Neill and index-6 Irvine narrow.
7. **If team_phase == "transition_defense":** Hard tactical foul within 4 units of the ball-carrier in midfield — STOP the counter. Australia is comfortable taking a yellow to break up a transition.
8. **If my role == "DEF" and a defensive corner is incoming:** The index-2 Souttar marks the opposition's most dangerous CF; the index-3 Circati covers behind Souttar; the index-4 Italiano and index-1 Bos on the posts.
9. **If team is trailing by 1 in the final 15 minutes:** Push the index-2 Souttar forward as an emergency 9 for every set-piece and cross.
10. **If my player_id ends with "_9" (LW Leckie, #7) and I have the ball on the left flank:** Whip an in-swinging cross to the index-2 Souttar at the penalty spot, OR cut inside and Shoot.
11. **If team_phase == "attacking" and possession is settled in the opposition half:** Send the index-4 Italiano and index-1 Bos high simultaneously; Australia plays 2-3-5 with width.
12. **Set-pieces 22-30 yards from goal (central):** Defer to the index-7 Velupillay.

## Key Player Notes
- **Souttar (2):** The 6'7" aerial weapon. Goal threat at every set-piece. Slightly slow on the ground — protect him with Circati covering.
- **Velupillay (7):** The creator. Set-piece taker. The press-resistant ball-carrier who turns Australian honest work into chances.
- **Irvine (6):** Captain in midfield. Stamina 17. Late-run goal threat. Box-to-box.
- **Mat Ryan (0):** The veteran captain. Calming presence. Fourth World Cup.
- **Touré (10):** The lone 9. Pacy. Runs the channel. Presses from the front. Finishes from inside the box.
- **Bos (1) & Italiano (4):** The athletic young full-backs providing the team's attacking width and overlap.

## Tournament Mindset
Australia has a clear ceiling — round-of-16 is the realistic upper bound, and group-stage exit is the danger if drawn into a tough group. The mentality is **win the games we can, draw the games we should lose, never embarrass the shirt**. They will beat any team rated below them through sheer organization and set-pieces. Against a top-eight opponent, they will sit deep, foul tactically, and hope for one Souttar set-piece moment. Stamina is the squad-wide superpower — Australia gets stronger in the 75th minute. The vulnerability is creativity against an organized opponent who denies set-pieces — Australia can struggle to break down a deep block.
