# Scotland — Tactical Profile

## Identity & Philosophy
Scotland under Steve Clarke are the embodiment of organized, transitional football — a disciplined system that gives them defensive density in a compact mid-block out of possession, then explodes forward through energetic full-backs and Scott McTominay's late runs into the box. They overachieved their way to Euro 2024 and have built an identity around clean sheets, set-piece danger, and Andrew Robertson's overlapping menace. For their first World Cup since 1998, Clarke has shifted to a back four, but the principles are unchanged: team shape over individual possession, structural discipline, and width that comes from the full-backs.

## Formation
- Shape: 4-2-3-1 (transitions to 4-4-1-1 / 4-5-1 defending, 2-3-5 attacking when full-backs push)
- Role mapping (roster order in `scotland.yaml`):
  - index 0 (`scotland_0`, Gunn): GK — agile shot-stopper, commands his box, tidy short distributor (veteran Gordon is now the backup).
  - index 1 (`scotland_1`, Robertson, captain): LB — Scotland's attacking talisman, overlapping crosser, back on his natural left side and still the most advanced full-back.
  - index 2 (`scotland_2`, McKenna): LCB — aggressive, good in the air, steps out to cover.
  - index 3 (`scotland_3`, Souttar): RCB — composed right-sided stopper, strong in the air, the better passer of the pair.
  - index 4 (`scotland_4`, Hickey): RB — overlapping, athletic, gets to the byline.
  - index 5 (`scotland_5`, Ferguson): DM/pivot — box-to-box engine, recycles and breaks lines, arrives in the box late.
  - index 6 (`scotland_6`, Christie): DM/pivot — energetic shuttler, presses and links play.
  - index 7 (`scotland_7`, McGinn): LW/AM — energy, drives infield, set-piece taker.
  - index 8 (`scotland_8`, McTominay): AM/box-crasher — late runs, top scorer, the central #10.
  - index 9 (`scotland_9`, Gannon-Doak): RW — direct dribbler, beats his man, the squad's x-factor.
  - index 10 (`scotland_10`, Adams): CF — mobile but physical focal point, links play and fights for second balls.

*Note: width comes from the full-backs (Robertson index 1 on the left, Hickey index 4 on the right) overlapping the wide forwards. When defending, the wide forwards (`_7` McGinn, `_9` Gannon-Doak) tuck back to form a 4-4-1-1 with McTominay (`_8`) screening just ahead.*

## Style of Play

### Build-up
Slow and deliberate. Gunn rolls to a center-back; one of the pivot (Ferguson `_5` or Christie `_6`) drops between the CBs to form a 3-2 build. Full-backs push high and wide to stretch the pitch. Long balls aimed at Adams' chest control are a Plan B against high presses, with McTominay and McGinn crashing the second ball.

### Pressing (block height + trigger)
Mid-block — line of confrontation around the halfway line. Press triggers are conservative: only when the opposition full-back receives with back to play AND McGinn/Gannon-Doak are within 8m. Otherwise the front line screens passing lanes and Scotland trusts their compact shape.

### Defensive shape
Settled 4-4-1-1: back four sits deep, midfield four (the two pivots plus the wide forwards tucking in) protects in front, McTominay screens just ahead, and Adams stays high as the sole outlet. Lines compact — never more than 10m between defense and midfield. Robertson and Hickey both track back diligently, which Clarke demands.

### Wide play
Robertson + Hickey are the offensive width from full-back, overlapping the wingers. Robertson crosses with venom from deep on the left; Hickey gets to the byline on the right. Gannon-Doak (`_9`) takes defenders on 1v1 to the touchline; McGinn (`_7`) drives infield into the half-space while Robertson overlaps outside him.

### Final third
Crosses, second balls, and McTominay's near-post runs from deep. Cutbacks rather than high crosses when possible. Set pieces are a primary attacking weapon — Scotland scored a heavy percentage of qualifying goals from corners and direct free kicks.

## Set Pieces
- Corners: Robertson delivers from the left; McGinn from the right. McKenna, Souttar, McTominay, and Adams are the primary aerial targets.
- Direct free kicks: McGinn first; Ferguson as an alternate from range.
- Penalties: McGinn first; McTominay second.

## decide() Decision Priorities
1. **Compact-block default:** when the ball is in Scotland's defensive half, all 10 outfield players must be within 35m of the ball (vertical). Never get stretched.
2. If my player_id ends with "_1" (LB, Robertson, captain, #3): in possession on the left flank, OVERLAP automatically when the player ending in "_7" (McGinn) carries infield; sprint to the byline and cross.
3. If my player_id ends with "_4" (RB, Hickey, #2): overlap on the right when "_9" (Gannon-Doak) cuts inside; get to the byline and cut the ball back. Track back fully when Scotland loses possession.
4. If my player_id ends with "_8" (AM, McTominay, #4): when Scotland regains possession in the middle third, sprint into the opposition penalty area as a late-arriving #10. Demand cutbacks.
5. If my player_id ends with "_7" (LW/AM, McGinn, #7): drive infield toward the left half-space; encourage 1-2s with "_10" (Adams) and "_8" (McTominay). Set-piece deliverer.
6. If my player_id ends with "_9" (RW, Gannon-Doak, #17): take your defender on 1v1 toward the touchline; if blocked, lay back to "_4" (Hickey) overlapping and crash the far post.
7. If my player_id ends with "_5" (DM, Ferguson, #19): screen in front of the back four; available as a backward pass option, but break forward into the box on the second phase when "_8" (McTominay) drags markers.
8. If my player_id ends with "_6" (DM, Christie, #11): shuttle — wherever "_5" (Ferguson) isn't, you are. Track the opposition #10 and press the ball-side pivot.
9. If my player_id ends with "_10" (CF, Adams, #10): act as the focal point — win aerial balls and lay off to "_8" (McTominay) or "_7" (McGinn); stay on the shoulder of the last CB on counters.
10. If my player_id ends with "_2" or "_3" (CBs, McKenna/Souttar): primary action is HEAD AWAY when the ball comes into the box. Never attempt a controlled clearance under pressure.
11. On opposition corner: 9 players in the box; "_10" (Adams) stays high as the counter outlet.
12. When trailing late: "_1" (Robertson) and "_4" (Hickey) push higher to form a 2-3-5, "_6" (Christie) drops as the lone screening pivot.

## Key Player Notes
- **Andrew Robertson (index 1, captain):** the team's heartbeat. License to be the most advanced player on the pitch when Scotland attacks. Primary left-side set-piece taker and overlapping crosser.
- **Scott McTominay (index 8):** top scorer — instruct him to attack the back post on every wide attack. His late runs from the #10 position ARE the attacking plan.
- **John McGinn (index 7):** dual-purpose — LW defending and tucking in, AM attacking. Primary set-piece deliverer and first-choice penalty taker.
- **Ben Gannon-Doak (index 9):** the x-factor — direct, fearless dribbler who provides 1v1 threat down the right. Encourage him to commit defenders.
- **Lewis Ferguson (index 5):** the engine of the double pivot — recycles possession but is licensed to arrive late in the box on the second phase.
- **Aaron Hickey (index 4):** athletic overlapping right-back who provides the width on the right, freeing Gannon-Doak to come inside.

## Tournament Mindset
Scotland will not outplay Brazil, France, or Spain — but they will not be embarrassed by anyone. They are a knockout-format nightmare: defend the box, take a set-piece chance, and ride momentum.
