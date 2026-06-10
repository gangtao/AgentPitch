# Australia — Tactical Profile

## Identity & Philosophy
Tony Popovic's Australia is the platonic ideal of an **organized, hard-running, set-piece-reliant** side — the modern Socceroos identity inherited from Ange Postecoglou and refined into something more pragmatic. For 2026 Popovic has restructured into a **back-five 5-4-1**, built on **structural discipline, aerial dominance, and a clear plan to score from dead-balls or counter-attacks**, with the creative spark coming from teenage flyer Nestory Irankunda off the right. Australia rarely dominates possession against top opposition; they don't need to. The squad is **fitness-obsessed** (every outfielder rated 14+ stamina), tactically literate, and led by veterans Mat Ryan and Jackson Irvine — Ryan is at a fourth World Cup. The 2026 group is heavily refreshed: a new young spine of Jordy Bos, Alessandro Circati, Aiden O'Neill, Irankunda and Mohamed Touré around the veteran core. Recent form: comfortable through Asian qualifying after a slow start under previous management, with Popovic restoring discipline and shape; the 2022 round-of-16 run remains the benchmark.

## Formation
- Shape: **5-4-1** in and out of possession (wing-backs push to make a **3-4-3 / 3-2-5** when settled in the opposition half; pure low-block 5-4-1 against superior opposition).
- Role mapping (roster order in `australia.yaml`):
  - index 0: GK — **Mat Ryan** (#1) — veteran captain, the team's leader, vocal organizer, sweeper-keeper when needed but more comfortable on his line. Fourth World Cup; the calming presence.
  - index 1: LWB — **Jordy Bos** (#5) — flying young left wing-back, the natural width-giver on the left. Athletic, gets to the by-line, a genuine attacking outlet and in-swing deliverer.
  - index 2: LCB — **Cameron Burgess** (#21) — left-sided tower (strength 16), no-nonsense defender, second aerial weapon in both boxes.
  - index 3: CCB — **Harry Souttar** (#19) — the 6'7" aerial monster (strength 17), central pillar of the back three, set-piece weapon in both boxes, wins everything in the air, slightly slower on the ground.
  - index 4: RCB — **Alessandro Circati** (#3) — the composed young ball-player on the right of the three, sweeps in behind, covers Souttar's lack of pace and starts build-up with progressive passing.
  - index 5: RWB — **Jacob Italiano** (#4) — energetic right wing-back, the speedster of the back five, works the touchline both ways.
  - index 6: LM — **Connor Metcalfe** (#8) — the disciplined left-midfield runner who tucks in and works back; balances Bos's freedom on the overlap.
  - index 7: LCM — **Jackson Irvine** (#22) — captain in the midfield, the all-action box-to-box engine, stamina 17, late runs into the box, the team's leading midfield goal-scorer.
  - index 8: RCM — **Aiden O'Neill** (#13) — the deep-lying organizer, screens the back three, dictates tempo and recycles possession (pass 15); Popovic's preferred anchor.
  - index 9: RM — **Nestory Irankunda** (#17) — the teenage flyer (speed 17, dribbling 16), direct on the dribble, cuts in off the right, the chief open-play creative spark.
  - index 10: CF — **Mohamed Touré** (#9) / lone forward — the pacy 9, runs the channel, presses from the front, finishes inside the box.

(Note: the back three reads Burgess–Souttar–Circati left to right with Bos/Italiano as the wing-backs, and the midfield four reads Metcalfe–Irvine–O'Neill–Irankunda; the engine should accept the wing-backs as the team's only true width.)

## Style of Play

### Build-up
Pragmatic. Australia builds from the back three when uncontested but goes long the moment any press arrives. Mat Ryan is comfortable with his feet but defaults to a goal-kick aimed at Souttar or the channels. Circati starts the progression from the right of the three, while O'Neill drops between the lines to receive and recycle; Irankunda is the out-ball — find his feet wide right and let him carry. The first long ball is typically aimed at Touré running the channel; the second is aimed at Souttar arriving late for a set-piece. Australia is content to play 40% possession against superior opposition.

### Pressing
**Mid-block, trigger-based.** Australia does not high-press. They retreat to the halfway line, compress, and wait. Triggers: a back-pass to the opposition GK, a heavy first touch, or a throw-in. When triggered, Touré leads the press with curving runs, and Irvine jumps the opposition pivot as the central duel-winner. Irankunda presses the opposition left-back with his pace. The press is hard-running but not constant — Australia conserves stamina for the final 20 minutes.

### Defensive shape
Compact **5-4-1** with Bos and Italiano dropping in to complete the back five and Metcalfe/Irankunda tucking into the midfield four around the Irvine–O'Neill double screen. Touré stays high as the lone presser. The back three of Burgess–Souttar–Circati holds a medium line, dropping deeper against elite opposition into a pure low block that concedes the flanks and defends the box.

### Wide play
All width comes from the wing-backs. Left side: Bos overlaps Metcalfe, who tucks in. Right side: Irankunda drifts into the half-space while Italiano takes the touchline. The crosses come from deep (35-40 yards out) and are aimed at Souttar, Burgess, Irvine (late runner), or Touré at the near post. Australia is a **crossing team** — they live and die by the quality of the ball into the box.

### Final third
Patterns: Irankunda's carry from the right ending in a cut-inside shot or far-post cross; Bos's in-swinging cross from the left to Souttar (Souttar pushes forward for set-pieces and late corners); Italiano's cut-back from the right by-line to Irvine's late run; O'Neill's slipped diagonal to Touré sprinting in behind. Australia creates 4-6 chances per match — they need to convert one and rely on Souttar or set-pieces for the second.

## Set Pieces
**Australia is a set-piece monster.** Souttar and Burgess are twin aerial weapons in both boxes; Bos and O'Neill are the primary deliverers.
- Attacking corners: **Bos** in-swingers from the left, **O'Neill** deliveries from the right. Targets: Souttar (penalty spot, primary), Burgess (near post, flick-on), Circati (back post, late runner), Irvine (second ball).
- Defending corners: hybrid — Souttar attacks the first ball; Burgess marks the most dangerous opposition CF; four zonal markers across the six-yard line; Ryan stays on the goal line.
- Free kicks: Irankunda direct from central range within 25 yards; Bos direct deliveries from the left half-space.
- Throw-ins in the attacking third: aim for Souttar arriving from CB.
- Penalties: **Irvine** primary, **Irankunda** secondary, **Touré** tertiary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Mat Ryan, #1) and the team has a goal-kick:** Default to a long kick aimed at the index-3 Souttar or into the channel for the index-10 Touré, unless no opposition press is detected (then short to the index-4 Circati).
2. **If my player_id ends with "_3" (CCB Souttar, #19) and an attacking corner or cross is incoming:** Sprint to the penalty spot — attack the ball aggressively. Strength 17, aerial dominator.
3. **If my player_id ends with "_9" (RM Irankunda, #17) and I have the ball on the right flank:** Carry at the defender — cut inside and Shoot if within 25 units with an open angle, otherwise drive to the by-line and cross.
4. **If my player_id ends with "_7" (LCM Irvine, #22) and team_phase == "attacking":** Late run from deep into the box — arrive on the back post for crosses or cut-backs.
5. **If my player_id ends with "_10" (CF Touré, #9) and the ball is in midfield:** Run the channel behind the opposition full-back — receive long diagonals from the index-8 O'Neill.
6. **If team_phase == "defending" and the opposition is past midfield:** Drop into **5-4-1** — index-1 Bos and index-5 Italiano into the back five, index-6 Metcalfe and index-9 Irankunda into the midfield four, index-7 Irvine and index-8 O'Neill narrow.
7. **If team_phase == "transition_defense":** Hard tactical foul within 4 units of the ball-carrier in midfield — STOP the counter. Australia is comfortable taking a yellow to break up a transition.
8. **If my role == "DEF" and a defensive corner is incoming:** The index-3 Souttar attacks the first ball; the index-2 Burgess marks the opposition's most dangerous CF; the index-4 Circati covers behind; the index-5 Italiano and index-1 Bos on the posts.
9. **If team is trailing by 1 in the final 15 minutes:** Push the index-3 Souttar forward as an emergency 9 for every set-piece and cross.
10. **If my player_id ends with "_1" (LWB Bos, #5) and I have the ball on the left flank:** Whip an in-swinging cross to the index-3 Souttar at the penalty spot, OR recycle inside to the index-7 Irvine.
11. **If team_phase == "attacking" and possession is settled in the opposition half:** Send the index-1 Bos and index-5 Italiano high simultaneously; Australia plays 3-2-5 with wing-back width.
12. **Set-pieces 22-30 yards from goal (central):** Defer to the index-9 Irankunda.

## Key Player Notes
- **Souttar (3):** The 6'7" aerial weapon at the heart of the back three. Goal threat at every set-piece. Slightly slow on the ground — protect him with Circati and Burgess either side.
- **Irankunda (9):** The spark. Speed 17, dribbling 16. The direct ball-carrier who turns Australian honest work into chances; direct free-kick taker.
- **Irvine (7):** Captain in midfield. Stamina 17. Late-run goal threat. Box-to-box. Primary penalty taker.
- **Mat Ryan (0):** The veteran captain. Calming presence. Fourth World Cup.
- **Touré (10):** The lone 9. Pacy. Runs the channel. Presses from the front. Finishes from inside the box.
- **Bos (1) & Italiano (5):** The wing-backs providing all of the team's attacking width and overlap.
- **Burgess (2):** The second tower (strength 16) — near-post flick-on target and an extra body in both boxes.

## Tournament Mindset
Australia has a clear ceiling — round-of-16 is the realistic upper bound, and group-stage exit is the danger if drawn into a tough group. The mentality is **win the games we can, draw the games we should lose, never embarrass the shirt**. They will beat any team rated below them through sheer organization and set-pieces. Against a top-eight opponent, they will sit deep in the back five, foul tactically, and hope for one Souttar set-piece moment. Stamina is the squad-wide superpower — Australia gets stronger in the 75th minute. The vulnerability is creativity against an organized opponent who denies set-pieces — Australia can struggle to break down a deep block.
