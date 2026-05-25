# Scotland — Tactical Profile

## Identity & Philosophy
Scotland under Steve Clarke are the embodiment of organized, transitional football — a back-three system that gives them defensive density in a compact 5-4-1 out of possession, then explodes forward through energetic wing-backs and Scott McTominay's late runs into the box. They overachieved their way to Euro 2024 and have built an identity around clean sheets, set-piece danger, and Andrew Robertson's overlapping menace down the left.

## Formation
- Shape: 3-4-2-1 (transitions to 5-4-1 defending, 3-2-4-1 attacking)
- Role mapping (roster order in `scotland.yaml`):
  - index 0 (`scotland_0`, Gunn): GK — solid shot-stopper, average distributor.
  - index 1 (`scotland_1`, Tierney): LCB (left of back-3) — ball-playing, often steps into midfield carries.
  - index 2 (`scotland_2`, Hanley): central CB — old-school stopper, aerial, slow.
  - index 3 (`scotland_3`, Hendry): RCB — covers space, sweeper-ish.
  - index 4 (`scotland_4`, Robertson, captain): LWB — Scotland's attacking talisman, overlapping crosser.
  - index 5 (`scotland_5`, Gilmour): DM — deep playmaker, recycles possession.
  - index 6 (`scotland_6`, McGregor): CM — disciplined, link between defense and attack.
  - index 7 (`scotland_7`, McTominay): AM/box-crasher — late runs, top scorer in qualifying.
  - index 8 (`scotland_8`, McGinn): AM/RW — energy, drives forward, set-piece taker.
  - index 9 (`scotland_9`, Adams): CF — mobile, runs in channels.
  - index 10 (`scotland_10`, Dykes): CF/target — physical alternative, fights for second balls.

*Note: with only 3 listed defenders, the LWB role is filled by Robertson (index 4) and the RWB by McGinn (index 8) dropping wide when defending. In 5-4-1 settled defense, Robertson is the LWB and McGinn drops to RWB.*

## Style of Play

### Build-up
Slow and deliberate. Gunn rolls to Tierney; Gilmour drops between Tierney and Hanley to form a 4-2 build. Tierney often carries the ball forward 10-20m — he's licensed to dribble out. Long balls aimed at Dykes/Adams chest control are a Plan B against high presses.

### Pressing (block height + trigger)
Mid-block — line of confrontation around the halfway line. Press triggers are conservative: only when opposition fullback receives with back to play AND McGinn/Adams are within 8m. Otherwise the front 3 screen passing lanes and Scotland trusts their compact shape.

### Defensive shape
Settled 5-4-1: back five sits deep, midfield four (Gilmour, McGregor + wing-backs tucking in) protects in front. Adams stays high as the sole outlet. Lines compact — never more than 10m between defense and midfield. Robertson actually defends in this phase, which is sacrilege but Clarke demands it.

### Wide play
Robertson + McGinn are the offensive width. Robertson overlaps from LWB, crosses with venom from deep. On the right, McGinn drives infield while Hendry covers wide if needed.

### Final third
Crosses, second balls, and McTominay's near-post runs from deep. Cutbacks rather than high crosses when possible. Set pieces are a primary attacking weapon — Scotland scored a heavy percentage of qualifying goals from corners and direct free kicks.

## Set Pieces
- Corners: Robertson delivers from the left (outswinger), McGinn from the right (inswinger). Hanley, McTominay, and Dykes are the primary aerial targets.
- Direct free kicks: McGinn from the right; Robertson from the left.
- Penalties: McTominay first; Adams second.

## decide() Decision Priorities
1. **Compact-block default:** when the ball is in Scotland's defensive half, all 10 outfield players must be within 35m of the ball (vertical). Never get stretched.
2. If my player_id ends with "_4" (LWB, Robertson, #6): in possession on the left flank, OVERLAP automatically when the player ending in "_1" (Tierney) has the ball; if the LW (none in this 3-4-2-1 — "_1" Tierney filling) carries, sprint to the byline and cross.
3. If my player_id ends with "_1" (LCB, Tierney, #3): licensed to dribble out of defense into midfield up to 25m forward. After delivering the ball, MOVE back into the defensive line.
4. If my player_id ends with "_7" (AM, McTominay, #8): when Scotland regains possession in the middle third, sprint into the opposition penalty area as a late-arriving #10. Demand cutbacks.
5. If my player_id ends with "_8" (AM/RW, McGinn, #7): from RWB position, drive infield toward the half-space; encourage 1-2s with "_9" (Adams).
6. If my player_id ends with "_5" (DM, Gilmour, #18): always available as a backward pass option; never moves beyond the halfway line.
7. If my player_id ends with "_6" (CM, McGregor, #14): shuttle — wherever "_5" (Gilmour) isn't, you are. Track the opposition #10.
8. If my player_id ends with "_9" (CF, Adams, #10): stay on the shoulder of the last CB; if "_1" (Tierney) or "_7" (McTominay) carry the ball, make a diagonal run across the back line.
9. If my player_id ends with "_10" (CF/target, Dykes, #9): act as a target man — win aerial balls and lay off to "_7" (McTominay) or "_8" (McGinn).
10. If my player_id ends with "_2" or "_3" (CBs, Hanley/Hendry): primary action is HEAD AWAY when the ball comes into the box. Never attempt a controlled clearance under pressure.
11. On opposition corner: 9 players in the box; "_9" (Adams) stays high as the counter outlet.
12. When trailing late: "_8" (McGinn) pushes higher to form a 3-4-3, "_3" (Hendry) steps into midfield as auxiliary DM.

## Key Player Notes
- **Andrew Robertson (index 4, captain):** the team's heartbeat. License to be the most advanced player on the pitch when Scotland attacks. Primary left-side set-piece taker.
- **Scott McTominay (index 7):** top scorer — instruct him to attack the back post on every wide attack. His late runs ARE the attacking plan.
- **Billy Gilmour (index 5):** technical conscience. Always shows for the ball, lowest-risk passes. Never carries forward.
- **Kieran Tierney (index 1):** unique role — CB with license to dribble. Comfortable in possession.
- **John McGinn (index 8):** dual-purpose — RWB defending, AM attacking. Set-piece deliverer from the right.

## Tournament Mindset
Scotland will not outplay Brazil, France, or Spain — but they will not be embarrassed by anyone. They are a knockout-format nightmare: defend the box, take a set-piece chance, and ride momentum.
