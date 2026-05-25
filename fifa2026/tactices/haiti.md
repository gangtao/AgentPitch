# Haiti — Tactical Profile

## Identity & Philosophy
Returning to the World Cup for only the **second time ever** (first appearance: 1974 in West Germany). Haiti's qualification under **Sébastien Migné** — a French manager with a long CONCACAF/African resumé — is a national triumph for a country whose football infrastructure has been shattered by political instability and natural disaster. The team is **diaspora-based**: Bellegarde at Wolves, Isidor at Sunderland, Deedson at Lille, Etienne at MLS. Migné's Haiti plays a **physical, counter-attacking 4-3-3** built around defensive organization, midfield grit, and the lightning pace of its front three. Haiti will not dominate possession against any opponent in its group; the question is how clinically it can convert its 2-3 transition moments per match.

## Formation
- Shape: **4-3-3** in possession; **4-5-1 mid-low block** out of possession with Bellegarde dropping deeper and Deedson alone up top.
- Role mapping (roster order in `haiti.yaml`):
  - index 0: GK — **Johny Placide** — veteran shot-stopper; not a sweeper, stays on the goal line.
  - index 1: LCB — **Ricardo Adé** — physical, aerially dominant CB; the box-defender on crosses.
  - index 2: RB — **Carlens Arcus** — disciplined RB; rarely overlaps, prioritizes defensive solidity.
  - index 3: RCB — **Christopher Delcroix** — ball-playing CB; comfortable on the ball, the progressor from the back.
  - index 4: LB — **Maxime Lacroix** — modest attacking LB; the more adventurous of the two fullbacks but still disciplined.
  - index 5: DM/6 — **Carl Sainte** — disciplined holding midfielder; the line-protector in front of the back four.
  - index 6: CM/8 — **Jean-Ricner Bellegarde** — the team's most-decorated player (Premier League with Wolves). The chief creator from midfield; gets between the lines, drives forward with the ball.
  - index 7: CM/8 — **Danley Jean Jacques** — physical box-to-box, the runner who supports Bellegarde and tracks back.
  - index 8: LW — **Louicius Deedson** — pacy wide forward (Lille); cuts inside off the left, the team's transition outlet.
  - index 9: CF — **Wilson Isidor** — physical, fast #9 (Sunderland); the team's chief finisher and shot rating leader. Runs the channels.
  - index 10: RW — **Derrick Etienne Jr.** — MLS-experienced wide forward; cuts inside or stays wide, secondary creator.

## Style of Play

### Build-up
**Direct.** Haiti does not try to play out from the back against a press. Placide often goes long from goal kicks aiming at Isidor for a knock-down or into the channels for Deedson / Etienne. When building short (against weaker opposition or in safe phases), Sainte drops between the CBs, Delcroix carries forward as the progressor. Bellegarde is the link between defense and attack — receive on the half-turn, drive forward.

### Pressing
**Mid-block first, selective high press.** Trigger: opposition CB facing his own goal — Isidor curves the run, Deedson jumps the fullback. Trigger #2: heavy first touch from any opposition midfielder — Bellegarde or Jean Jacques sprints in. The press is **trigger-based**, not 90-minute sustained — Migné understands his squad's stamina ceiling and rations the press for high-leverage moments.

### Defensive shape
**Compact 4-5-1** out of possession with Deedson and Etienne dropping into a midfield five. Bellegarde sits between the lines, Sainte and Jean Jacques shield the back four. The block is **mid-to-low** — Haiti is happy to absorb pressure in its own third and counter. The CBs hold a moderate line, not high; the offside trap is not a weapon.

### Wide play
**Asymmetric, but both sides are counter-attack lanes.** **Left** = Deedson inside + Lacroix as a low-volume overlap; **right** = Etienne inside + Arcus disciplined. Haiti does not manufacture width; the wide forwards cut inside and the fullbacks largely stay home. When chances arrive, they come from a sprint down the wing rather than from a worked overload.

### Final third
Patterns: Bellegarde-through-ball to Isidor running the channel; Deedson cut-in shot from the left half-space; Isidor hold-up → lay-off to Bellegarde for a shot from 22 units; counter-attack with Bellegarde carrying 40 units before slipping Deedson in behind. Haiti's chance map will be heavy on transition and 1v1 isolations of Deedson against an opposing fullback.

## Set Pieces
- Attacking corners: **Bellegarde** delivers from the right (in-swinger), **Lacroix** from the left (in-swinger). Primary aerial targets: Adé (penalty spot), Isidor (near post), Delcroix (back post).
- Defending corners: **mostly man-marking** with two zonal at the near post. Adé takes the most dangerous opposing target.
- Free kicks: **Bellegarde** takes direct from any zone within 26 units; **Lacroix** delivers wide free kicks.
- Penalties: **Isidor** primary, **Bellegarde** secondary, **Deedson** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_6" (CM, jersey #8 — Bellegarde) and I receive the ball facing forward in midfield:** Carry forward (skill 15, dribbling 14). Through-ball to CF "_9" (Isidor) or LW "_8" (Deedson) is the priority.
2. **If my role is FWD and team_phase == "transition_attack":** Sprint forward on a diagonal — Haiti's counter-attack is the chief route to goal.
3. **If my role is FWD and team_phase == "defending":** Drop to form a 4-5-1 (LW "_8" Deedson to LM, RW "_10" Etienne to RM, CF "_9" Isidor stays high).
4. **If my role is GK (player_id ends with "_0" — Placide) and pressure is on:** Pass long to CF "_9" (Isidor, strength 14) for a knock-down. Avoid short build-up under press.
5. **If my player_id ends with "_9" (CF, jersey #9 — Isidor) and a long ball is in flight:** Hold position, contest the aerial duel, lay off to CM "_6" (Bellegarde) or LW "_8" (Deedson).
6. **If my player_id ends with "_2" (RB, jersey #2 — Arcus) and team_phase == "attacking":** Hold RB position. Do not overlap. Defensive discipline first.
7. **If team has just won possession in own half:** Vertical Pass to CM "_6" (Bellegarde) or directly to a forward within 2 ticks. No long recycle.
8. **If my role is MID and opposition has the ball in our half:** Drop to compact 4-5-1; nearest midfielder marks the opposing #10.
9. **If my player_id ends with "_8" (LW, jersey #11 — Deedson) and I receive the ball wide on the left:** Cut inside on the right foot. Shoot if angle < 30° and distance < 24, or slip CF "_9" (Isidor) in behind.
10. **If team is drawing or losing and minute > 75:** Push LB "_4" (Lacroix) forward, drop to 3-4-3 risk-on; otherwise keep the 4-5-1.
11. **If my player_id ends with "_1" (LCB, jersey #3 — Adé) and a cross is incoming:** attack the first ball at the penalty spot. Do not get drawn to the near post.
12. **Set pieces / penalties:** defer to CM "_6" (Bellegarde, delivery and direct FKs) and CF "_9" (Isidor, penalties).

## Key Player Notes
- **Bellegarde (6):** Captain in spirit, the team's only Premier League player. The chief creator and tactical leader. License to carry the ball forward.
- **Isidor (9):** Primary finisher and penalty taker. Shoot rating 15 — the team's most clinical attacker.
- **Deedson (8):** Pacy LW (Lille). The transition outlet on the left.
- **Adé (1):** Aerially dominant CB. The box-defender on set pieces both ways.
- **Etienne (10):** MLS-experienced RW. Secondary creator.
- **Sainte (5):** Disciplined holding midfielder. Frees Bellegarde to push forward.

## Tournament Mindset
Haiti is at the World Cup as a national catharsis after a brutal half-decade of political crisis. The realistic objective is **one point** in the group stage — a draw against the weakest opponent. Every match will be a defensive siege punctuated by 2-3 lightning counter-attacks. The squad's physical profile (speed 14-15 across the front three) is genuinely dangerous in transition, but the lack of depth and the gap to the European elite is enormous. A win — any win — would be one of the great World Cup stories. Bellegarde is the difference-maker; if he is on the pitch and on form, Haiti has a puncher's chance. If he is injured, Haiti will struggle to create.
