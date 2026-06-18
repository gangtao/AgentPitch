# Sweden — Tactical Profile

## Identity & Philosophy
Sweden under Graham Potter have reinvented themselves as one of the dark horses of World Cup 2026. After Potter took the job in October 2025 and dragged the side through to the finals, he installed an organised, possession-leaning **3-4-3** that uses wing-backs for width and presses high in transition. The headline is the most fearsome strike pairing at the tournament — Liverpool's Alexander Isak and Arsenal's Viktor Gyökeres in the same front line — with Anthony Elanga's raw pace as the third forward. The identity: a compact back three and double pivot that wins the ball, then feeds two world-class finishers running in behind. Sweden opened with a statement 5-1 demolition of Tunisia (Ayari brace, Isak, Gyökeres, Svanberg) and sit top of Group F.

## Formation
- Shape: 3-4-3 (Potter's wing-back system; morphs to a 3-5-2 / 5-2-3 out of possession, with Isak and Gyökeres as a twin-9 threat)
- Role mapping (roster order in `sweden.yaml`):
  - index 0 (`sweden_0`, Nordfeldt): GK — first-choice keeper for MD1, distributes to the back three or long to the strikers.
  - index 1 (`sweden_1`, Lindelöf): LCB — captain and ball-playing left-sided centre-back, the brain of the defence.
  - index 2 (`sweden_2`, Hien): CB — central pillar, physical destroyer, aerial dominance.
  - index 3 (`sweden_3`, Lagerbielke): RCB — right-sided stopper, covers behind the right wing-back.
  - index 4 (`sweden_4`, Gudmundsson): LWB — left wing-back, attacking outlet, primary left-side crosser & set-piece deliverer.
  - index 5 (`sweden_5`, Karlström): DM — deep-lying anchor of the double pivot, screens the back three.
  - index 6 (`sweden_6`, Ayari): CM — box-to-box engine and progressor; long-range threat (scored twice vs Tunisia).
  - index 7 (`sweden_7`, Svensson): RWB — right wing-back, energetic, overlaps and underlaps on the right.
  - index 8 (`sweden_8`, Elanga): LF — speed merchant (18), runs in behind from the left.
  - index 9 (`sweden_9`, Gyökeres): CF — physical runner, leads the line, relentless in behind.
  - index 10 (`sweden_10`, Isak): RF/second-9 — mobile, drifts infield and drops into pockets; dribble + finish.

## Style of Play

### Build-up
Mixed. The back three splits with Lindelöf and Lagerbielke wide; Karlström drops between/in front of them to receive. Nordfeldt builds short when allowed but goes long to Gyökeres when pressed. Wing-backs Gudmundsson and Svensson push high to provide the width. Sweden are equally happy in transition — they don't NEED the ball to hurt opponents.

### Pressing (block height + trigger)
Aggressive front press from Isak and Gyökeres, then a compact retreat. Press triggers when an opposition CB receives facing his own goal — the nearest striker curves to cut the back pass. Otherwise Sweden drop into a 5-2-3 / 5-4-1, the wing-backs tucking in to make a back five and the double pivot screening centrally.

### Defensive shape
5-2-3 / 5-4-1 with a back three plus two recovering wing-backs. Karlström shields the centre-backs; Ayari covers ground box-to-box. Hien dominates aerially in the middle; Lindelöf reads the game on the left, Lagerbielke handles the right. The extra centre-back gives cover for the high wing-backs.

### Wide play
Wing-backs are Sweden's width. On the left Gudmundsson overlaps and delivers; on the right Svensson supports Elanga. Elanga's speed (18) is the primary outlet behind the opposition full-back — every long ball or counter targets his channel.

### Final third
Two-9 chaos. Isak drifts off the right into pockets, drags a CB, opening space for Gyökeres or Elanga to attack in behind. Ayari arrives late for cutbacks and is a genuine long-range threat. Wing-back cutbacks from the byline are the staple chance creation.

## Set Pieces
- Corners: Gudmundsson delivers from the left (outswingers toward Hien and Gyökeres); inswingers from the right toward the near-post run. Hien, Gyökeres and Lagerbielke attack the box.
- Direct free kicks: Ayari from central/right positions (long-range threat); Gudmundsson's left foot from the left.
- Penalties: Isak first; Gyökeres second; Ayari third.

## decide() Decision Priorities
1. If my player_id ends with "_10" (RF/second-9, Isak): drift infield off the right into the pocket between the opposition DM and CB; when receiving, turn forward and DRIBBLE if 1v1.
2. If my player_id ends with "_9" (CF, Gyökeres): when "_10" (Isak) drops into the pocket, sprint diagonally across the back line — stay the #9 and attack the space in behind.
3. If my player_id ends with "_8" (LF, Elanga): on every regain in Sweden's half, sprint into the LEFT channel — the long ball is coming. Speed 18 wins all foot-races.
4. If my player_id ends with "_0" (GK, Nordfeldt): if Sweden regains the ball or wins a goal kick under heavy press, kick LONG toward "_9" (Gyökeres) or down the "_8" (Elanga) channel.
5. If my player_id ends with "_6" (CM, Ayari): box-to-box engine — when receiving with space ahead in midfield, DRIBBLE forward 10-15m, then either PASS a vertical lane to "_9"/"_10" or SHOOT from 20-25m if the lane is clear (long-range threat).
6. If my player_id ends with "_5" (DM, Karlström): never cross the halfway line. Pure screen of the back three. If an opposition midfielder breaks through, TACKLE; otherwise recycle to the centre-backs.
7. If my player_id ends with "_4" (LWB, Gudmundsson): when team_phase is "attacking", advance to LM height and provide the width; primary left-side crosser. When defending, tuck in to make a back five.
8. If my player_id ends with "_7" (RWB, Svensson): when team_phase is "attacking", overlap or underlap to support "_8" (Elanga) on the right. When defending, tuck in to make a back five.
9. If my player_id ends with "_1" (LCB, Lindelöf): if no opposition forward within 8m AND a Swedish forward makes a vertical run, PASS the line-breaking long ball (pass 15); otherwise build short.
10. If my player_id ends with "_2" (CB, Hien): physical central CB — clear all crosses with strength; mark the tallest attacker on opposition set pieces; never attempt a controlled clearance under pressure.
11. If my player_id ends with "_3" (RCB, Lagerbielke): cover the space behind the overlapping "_7" (Svensson); stay home when the right wing-back is high.
12. On opposition corner: "_2" (Hien) marks the tallest attacker; "_8" (Elanga) and "_10" (Isak) stay high near halfway as counter outlets (their pace is wasted in the box defensively).
13. When trailing late: push "_2" (Hien) forward for set pieces; shift to a front-loaded 3-4-3 with "_8" (Elanga) and "_10" (Isak) either side of "_9" (Gyökeres).

## Key Player Notes
- **Alexander Isak (index 10):** technically gifted second-9 off the right — shoot 17, dribbling 16, skill 16, penalty 17 (first taker). License to drift infield and drop into midfield to receive; expect him to combine 1-2 then sprint into the box. Scored vs Tunisia and assisted Gyökeres.
- **Viktor Gyökeres (index 9):** runner-finisher hybrid — shoot 17, strength 16, speed 16. Leads the line as the #9; his ball-in-behind runs are constant. Scored vs Tunisia.
- **Yasin Ayari (index 6):** box-to-box engine and breakout star — skill 15, pass 15, shoot 14. Scored a brace (two long-range strikes) vs Tunisia; license to shoot from distance and arrive for cutbacks.
- **Anthony Elanga (index 8):** pure speed asset (18) on the left front. Every long ball or counter targets the channel behind the opposition right-back.
- **Victor Lindelöf (index 1):** captain and brain of the back three; left-sided ball-player who steps the line and starts attacks.
- **Isak Hien (index 2):** central defensive pillar — strength 16; wins everything in the air and anchors the back three.

## Tournament Mindset
Sweden are no longer just a counter-attacking outfit — Potter has given them organisation and a clear shape, but the lethal edge remains the Isak-Gyökeres twin threat. They absorb pressure behind a back three, then KILL on transition. After a 5-1 opening rout of Tunisia, confidence is high: against a top attacking side like the Netherlands, the plan is to sit a touch deeper, weather the storm, and let two world-class strikers punish every turnover.
