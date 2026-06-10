# Haiti — Tactical Profile

## Identity & Philosophy
Returning to the World Cup for only the **second time ever** (first appearance: 1974 in West Germany). Haiti's qualification under **Sébastien Migné** — a French manager with a long CONCACAF/African resumé — is a national triumph for a country whose football infrastructure has been shattered by political instability and natural disaster. The team is **diaspora-based**: Bellegarde at Wolves, Isidor at Sunderland, Deedson at FC Dallas, and the well-travelled **Duckens Nazon — the national team's all-time top scorer** — leading the line. Only one player in the 26 (Woodensky Pierre, Violette AC) plays domestically. Migné's Haiti plays a **physical, counter-attacking 4-4-2** built around defensive organization, midfield grit, and a classic big-man/runner strike pairing. Haiti will not dominate possession against any opponent in its group; the question is how clinically it can convert its 2-3 transition moments per match.

## Formation
- Shape: **4-4-2** in possession; **two compact banks of four** out of possession with Nazon and Isidor staying high as the counter outlets.
- Role mapping (roster order in `haiti.yaml`):
  - index 0: GK — **Johny Placide** (#1, captain) — veteran shot-stopper; not a sweeper, stays on the goal line.
  - index 1: LB — **Duke Lacroix** (#13) — modest attacking LB; the more adventurous of the two fullbacks but still disciplined.
  - index 2: LCB — **Hannes Delcroix** (#5) — ball-playing CB; comfortable on the ball, the progressor from the back.
  - index 3: RCB — **Ricardo Adé** (#4) — physical, aerially dominant CB; the box-defender on crosses.
  - index 4: RB — **Carlens Arcus** (#2) — disciplined RB; rarely overlaps, prioritizes defensive solidity.
  - index 5: LM — **Louicius Deedson** (#11) — pacy wide midfielder (FC Dallas); cuts inside off the left, the team's transition outlet.
  - index 6: LCM — **Jean-Ricner Bellegarde** (#10) — the team's most-decorated player (Premier League with Wolves). The chief creator from midfield; gets between the lines, drives forward with the ball.
  - index 7: RCM — **Danley Jean Jacques** (#17) — physical box-to-box, the runner who supports Bellegarde and tracks back.
  - index 8: RM — **Ruben Providence** (#15) — quick, direct wide midfielder; stays wider than Deedson, sprints the right lane on the counter.
  - index 9: ST — **Duckens Nazon** (#9) — the all-time top scorer; physical target striker (strength 15), holds the ball up and finishes in the box.
  - index 10: ST — **Wilson Isidor** (#18) — physical, fast striker (Sunderland); runs the channels off Nazon and shares the finishing load (shoot 15).

## Style of Play

### Build-up
**Direct.** Haiti does not try to play out from the back against a press. Placide often goes long from goal kicks aiming at Nazon for a knock-down, with Isidor and Deedson attacking the second ball or the channels. When building short (against weaker opposition or in safe phases), Jean Jacques drops alongside the CBs, Delcroix carries forward as the progressor. Bellegarde is the link between defense and attack — receive on the half-turn, drive forward.

### Pressing
**Mid-block first, selective high press.** Trigger: opposition CB facing his own goal — Nazon curves the run, Isidor jumps the other CB. Trigger #2: heavy first touch from any opposition midfielder — Bellegarde or Jean Jacques sprints in. The press is **trigger-based**, not 90-minute sustained — Migné understands his squad's stamina ceiling and rations the press for high-leverage moments.

### Defensive shape
**Compact 4-4-2** out of possession with Deedson and Providence tucking into a flat midfield four. Bellegarde and Jean Jacques shield the back four; one striker drops onto the opposing pivot while the other stays high. The block is **mid-to-low** — Haiti is happy to absorb pressure in its own third and counter. The CBs hold a moderate line, not high; the offside trap is not a weapon.

### Wide play
**Both flanks are counter-attack lanes.** **Left** = Deedson inside + Lacroix as a low-volume overlap; **right** = Providence staying wide + Arcus disciplined behind him. Haiti does not manufacture width through overloads; the wide midfielders sprint the lanes and the fullbacks largely stay home. When chances arrive, they come from a sprint down the wing rather than from a worked overload.

### Final third
Patterns: Bellegarde-through-ball to Isidor running the channel; Deedson cut-in shot from the left half-space; Nazon hold-up → lay-off to Bellegarde for a shot from 22 units; counter-attack with Bellegarde carrying 40 units before slipping Isidor in behind; Providence sprint-and-cross from the right to Nazon at the penalty spot. Haiti's chance map will be heavy on transition and 1v1 isolations of Deedson against an opposing fullback.

## Set Pieces
- Attacking corners: **Bellegarde** delivers from the right (in-swinger), **Duke Lacroix** from the left (in-swinger). Primary aerial targets: Adé (penalty spot), Nazon (near post), Hannes Delcroix (back post).
- Defending corners: **mostly man-marking** with two zonal at the near post. Adé takes the most dangerous opposing target.
- Free kicks: **Bellegarde** takes direct from any zone within 26 units; **Duke Lacroix** delivers wide free kicks.
- Penalties: **Nazon** primary (the all-time top scorer), **Isidor** secondary, **Bellegarde** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_6" (LCM, jersey #10 — Bellegarde) and I receive the ball facing forward in midfield:** Carry forward (skill 15, dribbling 14). Through-ball to ST "_10" (Isidor) or LM "_5" (Deedson) is the priority.
2. **If my role is FWD and team_phase == "transition_attack":** Sprint forward on a diagonal — Haiti's counter-attack is the chief route to goal.
3. **If my role is FWD and team_phase == "defending":** One striker drops onto the opposing pivot, the other stays high — ST "_9" (Nazon) drops, ST "_10" (Isidor) stays as the outlet.
4. **If my role is GK (player_id ends with "_0" — Placide) and pressure is on:** Pass long to ST "_9" (Nazon, strength 15) for a knock-down. Avoid short build-up under press.
5. **If my player_id ends with "_9" (ST, jersey #9 — Nazon) and a long ball is in flight:** Hold position, contest the aerial duel, lay off to CM "_6" (Bellegarde) or ST "_10" (Isidor).
6. **If my player_id ends with "_4" (RB, jersey #2 — Arcus) and team_phase == "attacking":** Hold RB position. Do not overlap. Defensive discipline first.
7. **If team has just won possession in own half:** Vertical Pass to CM "_6" (Bellegarde) or directly to a forward within 2 ticks. No long recycle.
8. **If my role is MID and opposition has the ball in our half:** Drop into the flat midfield four of the 4-4-2; nearest central midfielder marks the opposing #10.
9. **If my player_id ends with "_5" (LM, jersey #11 — Deedson) and I receive the ball wide on the left:** Cut inside on the right foot. Shoot if angle < 30° and distance < 24, or slip ST "_10" (Isidor) in behind.
10. **If team is drawing or losing and minute > 75:** Push LB "_1" (Duke Lacroix) forward, drop to 3-4-3 risk-on; otherwise keep the 4-4-2 block.
11. **If my player_id ends with "_3" (RCB, jersey #4 — Adé) and a cross is incoming:** attack the first ball at the penalty spot. Do not get drawn to the near post.
12. **If my player_id ends with "_8" (RM, jersey #15 — Providence) and team_phase == "transition_attack":** Sprint the right lane (speed 15) and deliver an early cross to ST "_9" (Nazon) at the penalty spot.
13. **Set pieces / penalties:** defer to CM "_6" (Bellegarde, delivery and direct FKs) and ST "_9" (Nazon, penalties).

## Key Player Notes
- **Bellegarde (#10):** The team's only Premier League player (Wolves). The chief creator and tactical leader. License to carry the ball forward.
- **Nazon (#9):** The all-time top scorer and penalty taker. Strength 15, shoot 15 — the target man and the team's most clinical box presence.
- **Isidor (#18):** Fast second striker (speed 15, shoot 15). Runs the channels off Nazon and finishes the counters.
- **Deedson (#11):** Pacy LM (FC Dallas). The transition outlet on the left.
- **Adé (#4):** Aerially dominant CB. The box-defender on set pieces both ways.
- **Providence (#15):** Quick, direct RM (speed 15). Stays wide and sprints the right lane on the break.

## Tournament Mindset
Haiti is at the World Cup as a national catharsis after a brutal half-decade of political crisis. The realistic objective is **one point** in the group stage — a draw against the weakest opponent. Every match will be a defensive siege punctuated by 2-3 lightning counter-attacks. The squad's physical profile (speed 14-15 from the wide midfielders and Isidor) is genuinely dangerous in transition, but the lack of depth and the gap to the European elite is enormous. A win — any win — would be one of the great World Cup stories. Bellegarde is the difference-maker; if he is on the pitch and on form, Haiti has a puncher's chance. If he is injured, Haiti will struggle to create.
