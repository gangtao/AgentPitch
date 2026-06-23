# Scotland — Tactical Profile

## Identity & Philosophy
Scotland under Steve Clarke are the embodiment of organized, transitional football — a disciplined system that gives them defensive density in a compact block out of possession, then springs forward through driving wing-backs, John McGinn's running, and Scott McTominay's late surges into the box. They opened with a 1-0 win over Haiti on Matchday 1 (McGinn the scorer) — their first World Cup finals victory since 1990 — but were then undone by Morocco on Matchday 2, conceding to Ismael Saibari inside the opening two minutes and never recovering in a 0-1 defeat. That loss flipped their tournament: Scotland sit third in Group C on 3 points, behind Morocco (4) and Brazil (4), and now MUST get a result against Brazil in the final group game (Wed June 24, Hard Rock Stadium, Miami) to reach the last 32 — a draw will likely not be enough. Stung by the early concession in Boston, Clarke has shifted from the Haiti 4-4-2 to a more pragmatic back-three system (3-4-2-1) to add a body in central defence against Brazil's front line, keep the team compact, and counter through the wing-backs. The principles are unchanged: team shape over individual possession, structural discipline, set-piece danger, and width from athletic wing-backs.

## Formation
- Shape: 3-4-2-1 (a back three with two driving wing-backs; two central mids screen, two No.10s support a lone striker — compressing to a 5-4-1 when defending deep)
- Role mapping (roster order in `scotland.yaml`):
  - index 0 (`scotland_0`, Gunn): GK — agile shot-stopper, commands his box, tidy short distributor.
  - index 1 (`scotland_1`, Hendry): RCB — composed right-sided stopper, strong in the air and the best passer of the back three; steps out to carry.
  - index 2 (`scotland_2`, Hanley): CCB — experienced, aggressive, dominant in the air, the organiser of the back line and the central spare man.
  - index 3 (`scotland_3`, Tierney): LCB — converted full-back used as a ball-playing left-sided centre-back; comfortable carrying out and overlapping the left wing-back.
  - index 4 (`scotland_4`, Patterson): RWB — explosive, athletic right wing-back; flies up the line, gets to the byline, and tracks back to make a back five.
  - index 5 (`scotland_5`, Robertson, captain): LWB — Scotland's attacking talisman and overlapping crosser, now operating as the left wing-back; the most advanced wide outlet and a primary set-piece deliverer.
  - index 6 (`scotland_6`, Ferguson): RCM — box-to-box engine, recycles and breaks lines, screens in front of the back three and arrives in the box late.
  - index 7 (`scotland_7`, McTominay): LCM/box-crasher — late runs into the box, top scorer, the chief goal threat from midfield; first-choice penalty taker.
  - index 8 (`scotland_8`, Christie): RAM — energetic right-sided No.10, presses, links, and breaks beyond the striker; tireless runner off McTominay.
  - index 9 (`scotland_9`, McGinn): LAM — energy and drive, cuts infield into the left half-space, scorer vs Haiti, primary free-kick deliverer and joint corner taker.
  - index 10 (`scotland_10`, Adams): CF — mobile but physical lone striker; holds the ball up, links play, runs the channels, and is the high outlet on clearances.

*Note: width comes entirely from the wing-backs (Patterson index 4 on the right, Robertson index 5 on the left). When defending deep the two wing-backs drop in to form a back five and the two No.10s (`_8` Christie, `_9` McGinn) tuck alongside the central pair (`_6` Ferguson, `_7` McTominay) to make a 5-4-1, with Adams (`_10`) the lone presser and counter outlet. Gannon-Doak and Shankland drop to the bench in this pragmatic setup.*

## Style of Play

### Build-up
Slow and deliberate. Gunn rolls to a centre-back; the back three split with Hendry (`_1`) and Tierney (`_3`) carrying out wide, Hanley (`_2`) the spare man. The wing-backs (`_4` Patterson, `_5` Robertson) push high to pin Brazil's full-backs. Long balls aimed at Adams' (`_10`) chest control and hold-up are a Plan B against a high press, with McTominay (`_7`), McGinn (`_9`) and Christie (`_8`) crashing the second ball.

### Pressing (block height + trigger)
Against Brazil, a deep-to-mid block. Line of confrontation around the halfway line at most, often dropping to defend the edge of the box. Press triggers are conservative: only when a Brazil defender receives with back to play AND a No.10 (`_8`/`_9`) is within 8m. Otherwise Adams screens passing lanes and Scotland trusts their compact five-four shape, denying space in behind for Vinícius Júnior.

### Defensive shape
Settled 5-4-1 when pinned back: back five (three CBs plus both wing-backs dropping in), a flat four ahead (the two central mids plus the No.10s tucking in), and Adams as the lone screen/outlet. Lines compact — never more than 10m between defence and midfield. The central spare man (Hanley, `_2`) covers in behind; Hendry and Tierney pick up runners. Discipline is everything: do not get drawn out, do not concede early again.

### Wide play
Patterson (`_4`) and Robertson (`_5`) are the offensive width as wing-backs. Robertson crosses with venom from deep on the left; Patterson uses raw pace to get to the byline on the right. McGinn (`_9`) drifts infield into the left half-space while Robertson overlaps outside him; Christie (`_8`) does the same on the right to free Patterson.

### Final third
Crosses, second balls, and McTominay's late near-post runs from deep. Cutbacks rather than high crosses when possible, feeding Adams and the arriving McTominay and No.10s. Set pieces are a primary attacking weapon — Scotland scored a heavy percentage of qualifying goals from corners and direct free kicks, and against Brazil they may be the most reliable route to goal.

## Set Pieces
- Corners: Robertson and McGinn deliver; Christie and Ferguson are alternates. Hanley, Hendry, McTominay, and Adams are the primary aerial targets, with deliveries primarily aimed at McTominay.
- Direct free kicks: McGinn first; Ferguson and Christie as alternates from range.
- Penalties: McTominay first; McGinn second (both have converted in past shootouts).

## decide() Decision Priorities
1. **Compact-block default:** when the ball is in Scotland's defensive half, all 10 outfield players must be within 35m of the ball (vertical) and the wing-backs must drop to form a back five. Never get stretched — and never switch off early after the lead-conceding lapse vs Morocco.
2. If my player_id ends with "_5" (LWB, Robertson, captain, #3): in possession on the left flank, OVERLAP automatically when the player ending in "_9" (McGinn) carries infield; sprint to the byline and cross. Drop to left centre-back of a back five when Scotland loses the ball. Primary corner deliverer.
3. If my player_id ends with "_4" (RWB, Patterson, #2): overlap on the right when "_8" (Christie) cuts inside; use pace to get to the byline and cut the ball back. Track back fully to make a back five when Scotland loses possession.
4. If my player_id ends with "_7" (LCM, McTominay, #4): when Scotland regains possession in the middle third, sprint into the opposition penalty area as a late-arriving box-crasher. Demand cutbacks. First-choice penalty taker and the primary goal threat.
5. If my player_id ends with "_9" (LAM, McGinn, #7): drive infield toward the left half-space; encourage 1-2s with "_10" (Adams) and "_7" (McTominay). Primary free-kick deliverer and joint corner taker.
6. If my player_id ends with "_8" (RAM, Christie, #11): support the lone striker by breaking beyond him on the right; press from the front as the trigger man, then lay back to "_4" (Patterson) overlapping and crash the far post.
7. If my player_id ends with "_6" (RCM, Ferguson, #19): screen in front of the back three as the deepest midfielder; available as a backward pass option, but break forward into the box on the second phase when "_7" (McTominay) drags markers.
8. If my player_id ends with "_10" (CF, Adams, #10): act as the lone focal point — hold the ball up, drop to link play and lay off to "_7" (McTominay), "_8" (Christie) or "_9" (McGinn); run the channels, stay on the shoulder of the last CB on counters, and be the high outlet on clearances.
9. If my player_id ends with "_1" or "_3" (wide CBs, Hendry/Tierney): step out to carry or pass when space opens, but the primary action is to pick up the runner in your channel; HEAD AWAY when the ball comes into the box under pressure.
10. If my player_id ends with "_2" (CCB, Hanley): the central spare man — sweep behind the back line, cover in behind, and HEAD AWAY when the ball comes into the box. Never attempt a controlled clearance under pressure.
11. On opposition corner: 9 players in the box; the lone striker ("_10" Adams) stays high as the counter outlet.
12. When chasing the game (which Scotland likely must do): "_4" (Patterson) and "_5" (Robertson) push higher to make a 3-4-3, "_6" (Ferguson) drops as the lone screening pivot, and both No.10s ("_8" Christie, "_9" McGinn) join Adams in attack.

## Key Player Notes
- **Andrew Robertson (index 5, captain):** the team's heartbeat, now driving from left wing-back. License to be the most advanced wide player when Scotland attacks; primary left-side set-piece deliverer and overlapping crosser. Must also tuck into a back five when defending.
- **Scott McTominay (index 7):** top scorer and first-choice penalty taker — instruct him to attack the box on every wide attack. His late runs from central midfield ARE the attacking plan against Brazil.
- **John McGinn (index 9):** dual-purpose — defending and tucking in from the left, attacking from the left half-space as a No.10. Scored the Matchday-1 winner; primary free-kick deliverer and second penalty taker.
- **Nathan Patterson (index 4):** explosive right wing-back providing the width on the right; raw pace to the byline, but must track back diligently to complete the back five against Vinícius Júnior's side.
- **Kieran Tierney (index 3):** converted to a ball-playing left centre-back in the back three; comfortable carrying out and underlapping, giving Robertson licence to fly forward.
- **Lewis Ferguson (index 6):** the engine of the central pair — screens the back three and recycles possession, but is licensed to arrive late in the box on the second phase.
- **Grant Hanley (index 2):** the experienced organiser and central spare man of the back three; dominant in the air, sweeps in behind, and a set-piece aerial threat at both ends.

## Tournament Mindset
The Morocco defeat changed everything: Scotland are third in Group C and must beat Brazil — a side that has never lost to them and has won their last three World Cup meetings — to survive. This is a do-or-die knockout in all but name, and it suits them. Defend the box in a compact back five, deny Vinícius space in behind, stay disciplined after the early-goal lesson from Boston, and trust the set-piece threat and McTominay's runs to nick the goal that sends them through. No fear, no chaos — control the game, take the one chance that matters.
