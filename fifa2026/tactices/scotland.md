# Scotland — Tactical Profile

## Identity & Philosophy
Scotland under Steve Clarke are the embodiment of organized, transitional football — a disciplined system that gives them defensive density in a compact mid-block out of possession, then explodes forward through energetic full-backs, John McGinn's running, and Scott McTominay's late surges into the box. They ground out a 1-0 win over Haiti on Matchday 1 (McGinn the scorer) to claim their first World Cup finals victory since 1990 and sit top of Group C. For their first World Cup since 1998, Clarke has settled on a tight 4-4-2 that compresses into two banks of four, the principles unchanged: team shape over individual possession, structural discipline, set-piece danger, and width that comes from the full-backs and a hard-working wide-midfield pair. A win vs Morocco on June 19 all but seals the last-32.

## Formation
- Shape: 4-4-2 (two compact banks of four defending; the wide mids push on and the full-backs overlap to a 2-4-4 / 2-3-5 attacking)
- Role mapping (roster order in `scotland.yaml`):
  - index 0 (`scotland_0`, Gunn): GK — agile shot-stopper, commands his box, tidy short distributor (veteran Gordon is the backup).
  - index 1 (`scotland_1`, Robertson, captain): LB — Scotland's attacking talisman, overlapping crosser on the left, still the most advanced full-back and a primary corner deliverer.
  - index 2 (`scotland_2`, Hanley): LCB — experienced, aggressive, dominant in the air, the leader of the back line.
  - index 3 (`scotland_3`, Hendry): RCB — composed right-sided stopper, strong in the air and the better passer of the central pair.
  - index 4 (`scotland_4`, Hickey): RB — overlapping, athletic, gets to the byline.
  - index 5 (`scotland_5`, McGinn): LM — energy and drive, cuts infield into the half-space, scorer vs Haiti, primary free-kick and joint corner deliverer.
  - index 6 (`scotland_6`, Ferguson): LCM — box-to-box engine, recycles and breaks lines, arrives in the box late.
  - index 7 (`scotland_7`, McTominay): RCM/box-crasher — late runs into the box, top scorer, the chief goal threat from midfield.
  - index 8 (`scotland_8`, Gannon-Doak): RM — direct dribbler, beats his man, the squad's x-factor; his cross set up the Haiti winner.
  - index 9 (`scotland_9`, Adams): CF — mobile but physical, links play, fights for second balls and runs the channels.
  - index 10 (`scotland_10`, Shankland): CF — penalty-box poacher and aerial target; partners Adams as the second striker.

*Note: width comes from the full-backs (Robertson index 1 on the left, Hickey index 4 on the right) overlapping the wide midfielders. When defending, the wide mids (`_5` McGinn, `_8` Gannon-Doak) drop to form a flat midfield four ahead of the back four, with one striker pressing and the other screening.*

## Style of Play

### Build-up
Slow and deliberate. Gunn rolls to a center-back; Ferguson (`_6`) or McTominay (`_7`) drops to help form a 3-2 build. Full-backs push high and wide to stretch the pitch. Long balls aimed at Adams' (`_9`) chest control and Shankland's (`_10`) hold-up are a Plan B against high presses, with McTominay and McGinn crashing the second ball.

### Pressing (block height + trigger)
Mid-block — line of confrontation around the halfway line. Press triggers are conservative: only when the opposition full-back receives with back to play AND McGinn/Gannon-Doak are within 8m. Otherwise the front pair screens passing lanes and Scotland trusts their compact two-bank shape.

### Defensive shape
Settled 4-4-2: back four sits deep, a flat midfield four (the two central mids plus the wide mids dropping in) protects in front, and one striker drops to screen while the other stays high as the outlet. Lines compact — never more than 10m between defense and midfield. Robertson and Hickey both track back diligently, which Clarke demands.

### Wide play
Robertson + Hickey are the offensive width from full-back, overlapping the wide mids. Robertson crosses with venom from deep on the left; Hickey gets to the byline on the right. Gannon-Doak (`_8`) takes defenders on 1v1 to the touchline or runs in behind; McGinn (`_5`) drives infield into the half-space while Robertson overlaps outside him.

### Final third
Crosses, second balls, and McTominay's near-post runs from deep. Cutbacks rather than high crosses when possible, feeding the two strikers and the arriving McTominay. Set pieces are a primary attacking weapon — Scotland scored a heavy percentage of qualifying goals from corners and direct free kicks.

## Set Pieces
- Corners: Robertson and McGinn deliver; Christie and Ferguson are alternates. Hanley, Hendry, McTominay, and Shankland are the primary aerial targets, with deliveries primarily aimed at McTominay.
- Direct free kicks: McGinn first; Ferguson and Christie as alternates from range.
- Penalties: McTominay first; McGinn second (both have converted in past shootouts).

## decide() Decision Priorities
1. **Compact-block default:** when the ball is in Scotland's defensive half, all 10 outfield players must be within 35m of the ball (vertical). Never get stretched.
2. If my player_id ends with "_1" (LB, Robertson, captain, #3): in possession on the left flank, OVERLAP automatically when the player ending in "_5" (McGinn) carries infield; sprint to the byline and cross. Primary corner deliverer.
3. If my player_id ends with "_4" (RB, Hickey, #2): overlap on the right when "_8" (Gannon-Doak) cuts inside; get to the byline and cut the ball back. Track back fully when Scotland loses possession.
4. If my player_id ends with "_7" (RCM, McTominay, #4): when Scotland regains possession in the middle third, sprint into the opposition penalty area as a late-arriving box-crasher. Demand cutbacks. First-choice penalty taker.
5. If my player_id ends with "_5" (LM, McGinn, #7): drive infield toward the left half-space; encourage 1-2s with "_9" (Adams) and "_7" (McTominay). Primary free-kick deliverer and joint corner taker.
6. If my player_id ends with "_8" (RM, Gannon-Doak, #17): take your defender on 1v1 toward the touchline or run in behind; if blocked, lay back to "_4" (Hickey) overlapping and crash the far post.
7. If my player_id ends with "_6" (LCM, Ferguson, #19): screen in front of the back four; available as a backward pass option, but break forward into the box on the second phase when "_7" (McTominay) drags markers.
8. If my player_id ends with "_9" (CF, Adams, #10): act as a mobile focal point — drop to link play and lay off to "_7" (McTominay) or "_5" (McGinn); run the channels and stay on the shoulder of the last CB on counters.
9. If my player_id ends with "_10" (CF, Shankland, #9): play as the penalty-box poacher — stay central between the CBs, attack crosses and cutbacks, and be the high outlet on clearances.
10. If my player_id ends with "_2" or "_3" (CBs, Hanley/Hendry): primary action is HEAD AWAY when the ball comes into the box. Never attempt a controlled clearance under pressure.
11. On opposition corner: 9 players in the box; one striker ("_9" Adams) stays high as the counter outlet.
12. When trailing late: "_1" (Robertson) and "_4" (Hickey) push higher to form a 2-3-5, "_6" (Ferguson) drops as the lone screening pivot.

## Key Player Notes
- **Andrew Robertson (index 1, captain):** the team's heartbeat. License to be the most advanced player on the pitch when Scotland attacks. Primary left-side set-piece deliverer and overlapping crosser.
- **Scott McTominay (index 7):** top scorer and first-choice penalty taker — instruct him to attack the box on every wide attack. His late runs from central midfield ARE the attacking plan.
- **John McGinn (index 5):** dual-purpose — LM defending and tucking in, attacking from the left half-space. Scored the Matchday-1 winner; primary free-kick deliverer and second penalty taker.
- **Ben Gannon-Doak (index 8):** the x-factor — direct, fearless dribbler who provides 1v1 threat and runs in behind down the right; his cross created the winner vs Haiti. Encourage him to commit defenders.
- **Lewis Ferguson (index 6):** the engine of the central pair — recycles possession but is licensed to arrive late in the box on the second phase.
- **Aaron Hickey (index 4):** athletic overlapping right-back who provides the width on the right, freeing Gannon-Doak to come inside.
- **Grant Hanley (index 2):** the experienced organiser of the back line; dominant in the air and a set-piece aerial threat at both ends.

## Tournament Mindset
Scotland top Group C after grinding out a 1-0 win over Haiti and will not be embarrassed by anyone. They are a knockout-format nightmare: defend the box in two compact banks, take a set-piece chance, and ride momentum. A point against Morocco likely advances them; they will play for control of the game, not chaos.
