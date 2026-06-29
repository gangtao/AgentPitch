# Sweden — Tactical Profile

## Identity & Philosophy
Sweden under Graham Potter have become one of the dark horses of World Cup 2026 — a side built around the most fearsome strike pairing at the tournament, Liverpool's Alexander Isak and Arsenal's Viktor Gyökeres, with Newcastle's Anthony Elanga adding raw pace as a third forward. Potter installed an organised back-three system that defends in numbers and hurts opponents in transition: a compact block, wing-backs for width, and everything aimed at servicing the front three. The identity is pragmatic — Sweden are happy to cede possession, sit deep, and trust world-class finishers to convert the moments. They flew out of the blocks with a 5-1 demolition of Tunisia, were brutally exposed in a 5-1 hammering by the Netherlands, then ground out a 1-1 draw with Japan (Elanga the equaliser) to scrape through Group F in third on 4 points. That survival cost them dearly: centre-back Isak Hien limped off against Japan with a thigh injury and is OUT for the rest of the tournament. Now comes the hardest possible reward — a Round of 32 knockout against France.

## R32 Lineup (vs France, June 30 — MetLife Stadium, win-or-go-home)
Sweden are heavy underdogs. France are deeper, faster across the front, and lethal in exactly the transition moments that punish a side chasing the game — so Potter doubles down on control and damage limitation, not expansion:
- **Isak Hien is ruled out** (thigh injury vs Japan). **Victor Lindelöf drops from midfield into the back three** to anchor the central defensive slot, alongside Lagerbielke and Gudmundsson.
- **Lucas Bergvall** (Tottenham) — Hien's replacement off the bench vs Japan — **takes Lindelöf's vacated midfield spot** beside Yasin Ayari. A press-resistant carrier who can break lines.
- **Elliot Stroud** keeps the left wing-back berth; **Alexander Bernhardsson** keeps the right wing-back berth — both must tuck in to make a back five out of possession.
- **Anthony Elanga, Alexander Isak, and Viktor Gyökeres** start as the front three; in a deep block Elanga drops to a wing-back-height outlet, leaving Isak and Gyökeres as the twin-9 transition threat.
- **Jacob Widell Zetterström** is the first-choice keeper (started the Japan finale).

## Formation
- Shape: 3-4-3 (Potter's knockout setup vs France; collapses to a 5-4-1 / 5-2-3 deep block out of possession, with Isak and Gyökeres held high as transition outlets)
- Role mapping (roster order in `sweden.yaml`):
  - index 0 (`sweden_0`, Zetterström): GK — first-choice keeper; distributes short to the back three or long to the front line under press.
  - index 1 (`sweden_1`, Lagerbielke): LCB — left-sided centre-back of the back three; covers behind the left wing-back.
  - index 2 (`sweden_2`, Lindelöf): CB — captain and central pillar, dropped in from midfield; the brain of the defence, reads the game and steps the line.
  - index 3 (`sweden_3`, Gudmundsson): RCB — right-sided centre-back; comfortable on the ball, can step out and progress.
  - index 4 (`sweden_4`, Stroud): LWB — left wing-back; attacking outlet and primary left-side crosser. Tucks in to make a back five when defending.
  - index 5 (`sweden_5`, Bergvall): LCM — press-resistant carrier; breaks lines with dribbles and vertical passes into the front three.
  - index 6 (`sweden_6`, Ayari): RCM — box-to-box engine and long-range threat (scored vs Tunisia); screens centrally and arrives for cutbacks.
  - index 7 (`sweden_7`, Bernhardsson): RWB — right wing-back; pace and width, overlaps and crosses on the right. Tucks in to make a back five when defending.
  - index 8 (`sweden_8`, Elanga): RF/wide outlet — blistering pace; in the block he drops wide-right as the first transition runner, then sprints the channel in behind.
  - index 9 (`sweden_9`, Isak): LF/second-9 — mobile, drifts infield into pockets; dribble + finish.
  - index 10 (`sweden_10`, Gyökeres): CF — physical runner, leads the line, relentless in behind.

## Style of Play

### Build-up
Direct and risk-averse. The back three of Lagerbielke, Lindelöf and Gudmundsson splits; Bergvall or Ayari drops to receive. Zetterström builds short only when France don't press, and goes long to Gyökeres or into the channels for the runners when squeezed. Sweden do not need the ball to hurt France — the plan is to win it back and release the front three at pace.

### Pressing (block height + trigger)
Selective. A short front-press from Isak and Gyökeres on an obvious back-pass trigger, then an immediate compact retreat. The default is a 5-4-1 / 5-2-3 block around and below the halfway line, wing-backs tucked in to make a back five, the midfield pair screening the half-spaces. Crucially, Sweden do NOT chase the game against France — pressing high leaves the exact space Mbappé and the French wide men feast on.

### Defensive shape
5-4-1 / 5-2-3 with a back three plus two recovering wing-backs. Lindelöf marshals the centre; Lagerbielke and Gudmundsson handle the flanks of the three and cover behind the wing-backs. Bergvall and Ayari shield the centre and track French runners between the lines. The extra centre-back is a deliberate guard against France's pace through Mbappé, Doué and Dembélé.

### Wide play
Wing-backs are Sweden's width. On the left Stroud overlaps and delivers; on the right Bernhardsson's pace stretches the line. Both target the channels behind the French full-backs, and their cutbacks from the byline are the staple chance creation for the front three. Defensively both must get back to form the back five — Theo Hernández and Dembélé will punish a high wing-back.

### Final third
Transition chaos. Win the ball, two-three touches, release Elanga or Gyökeres into the space France vacate when they over-commit. Isak drifts off the left into pockets to combine and drag a centre-back; Gyökeres attacks in behind; Elanga runs the right channel. Ayari arrives late for cutbacks. Set pieces are a genuine secondary plan — Sweden have height and must make every dead ball count.

## Set Pieces
- Corners: Stroud delivers from the left (outswingers toward Gyökeres and Lagerbielke); inswingers from the right toward the near-post run. Gyökeres, Lindelöf and Lagerbielke attack the box.
- Direct free kicks: Ayari from central/right positions (long-range threat); Bergvall from central areas; Stroud's delivery from the left.
- Penalties: Isak first; Gyökeres second; Ayari third.

## decide() Decision Priorities
1. If my player_id ends with "_9" (LF/second-9, Isak): drift infield off the left into the pocket between France's DM and CB; when receiving, turn forward and DRIBBLE if 1v1.
2. If my player_id ends with "_10" (CF, Gyökeres): when "_9" (Isak) drops into the pocket, sprint diagonally across the back line — stay the #9 and attack the space in behind.
3. If my player_id ends with "_8" (RF/wide outlet, Elanga): on every regain, sprint into the RIGHT channel behind the opposition full-back — pace is the primary transition outlet. When defending, drop to right wing-back height and help make a back five.
4. If my player_id ends with "_0" (GK, Zetterström): if Sweden regains the ball or wins a goal kick under heavy press, kick LONG toward "_10" (Gyökeres) or into the wide channels for the runners — do not invite the French press.
5. If my player_id ends with "_6" (RCM, Ayari): box-to-box engine — when receiving with space ahead in midfield, DRIBBLE forward 10-15m, then either PASS a vertical lane to "_9"/"_8"/"_10" or SHOOT from 20-25m if the lane is clear (long-range threat).
6. If my player_id ends with "_5" (LCM, Bergvall): press-resistant link — when receiving under pressure, DRIBBLE out of trouble and play the line-breaking vertical pass to the front three; never cross the halfway line when Sweden are in the deep block.
7. If my player_id ends with "_7" (RWB, Bernhardsson): when team_phase is "attacking", advance to RM height and provide width on the right; when defending, tuck in to make a back five (France attack hard down their left through Theo Hernández).
8. If my player_id ends with "_4" (LWB, Stroud): when team_phase is "attacking", advance to LM height and provide width; primary left-side crosser. When defending, tuck in to make a back five.
9. If my player_id ends with "_2" (CB, Lindelöf): captain and organiser — if no opposition forward within 8m AND a Swedish forward makes a vertical run, PASS the line-breaking long ball (pass 15); otherwise hold shape and build short. Never step out and leave the central gap against Mbappé.
10. If my player_id ends with "_1" (LCB, Lagerbielke): cover the space behind the overlapping "_4" (Stroud); stay home when the left wing-back is high — France's counters come fast.
11. If my player_id ends with "_3" (RCB, Gudmundsson): cover the space behind the overlapping "_7" (Bernhardsson); comfortable on the ball, step out only when the lane is safe.
12. On opposition corner: "_2" (Lindelöf) and "_1" (Lagerbielke) mark the tallest attackers; "_9" (Isak) and "_10" (Gyökeres) stay high near halfway as counter outlets (their pace is wasted in the box defensively).
13. When trailing late (a draw still means extra time, not elimination — only a loss ends the tournament): push "_1" (Lagerbielke) forward for set pieces; shift to a front-loaded shape with the wing-backs as auxiliary forwards flanking the front three.

## Key Player Notes
- **Alexander Isak (index 9):** technically gifted second-9 off the left — shoot 17, dribbling 16, skill 16, penalty 17 (first taker). License to drift infield and drop into midfield to receive; expect him to combine 1-2 then sprint into the box.
- **Viktor Gyökeres (index 10):** runner-finisher hybrid — shoot 17, strength 16, speed 16. Leads the line as the #9; his ball-in-behind runs are constant. Scored vs Tunisia.
- **Anthony Elanga (index 8):** blistering pace (speed 18) and the third forward; equalised vs Japan to keep Sweden alive. The primary right-channel transition outlet — drops to wing-back height in the block, then sprints in behind on the regain.
- **Yasin Ayari (index 6):** box-to-box engine and breakout star — skill 15, pass 15, shoot 14. Scored vs Tunisia; license to shoot from distance and arrive for cutbacks.
- **Lucas Bergvall (index 5):** press-resistant Tottenham midfielder added to the XI after Hien's injury reshuffle; carries the ball through pressure and breaks lines into the front three.
- **Victor Lindelöf (index 2):** captain and brain of the defence; dropped from midfield into the back three to cover for the injured Hien — organises the block and steps the line.
- **Jacob Widell Zetterström (index 0):** first-choice keeper; busy night expected behind a deep block, his long distribution launches the counters.

## Tournament Mindset
This is the knife-edge. Sweden survived a chaotic Group F — a 5-1 rout of Tunisia, a 5-1 thrashing by the Netherlands, and a backs-to-the-wall 1-1 draw with Japan — to limp into the knockouts in third, but at the cost of Isak Hien's tournament. Now they face France, deeper and faster everywhere, in a single-leg, win-or-go-home Round of 32. Potter's answer is discipline: a 3-4-3 that collapses to a back five, packs the centre against Mbappé and the French wide men, and refuses to chase the game. They will absorb pressure, screen the half-spaces, and trust two world-class strikers plus Elanga's pace to steal the moments that win a World Cup knockout. A second-round exit would be Sweden's earliest since 1990 — they intend to make France beat them.
