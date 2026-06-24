# Sweden — Tactical Profile

## Identity & Philosophy
Sweden under Graham Potter have become one of the dark horses of World Cup 2026. After Potter took the job in October 2025 and dragged the side through to the finals, he installed an organised, possession-leaning back-three system that uses wing-backs for width and presses high in transition. The headline is the most fearsome strike pairing at the tournament — Liverpool's Alexander Isak and Arsenal's Viktor Gyökeres in the same front line. The identity: a compact back three and midfield trio that wins the ball, then floods bodies forward to service two world-class finishers. Sweden opened with a statement 5-1 demolition of Tunisia (Ayari brace, Isak, Gyökeres, Svanberg) and topped Group F overnight — but a chastening 5-1 hammering by the Netherlands on Matchday 2 dumped them to third on three points. Now it is win-or-go-home against Japan in the final group game. Potter shifts to a **3-5-2** for this one: an extra midfielder for control, Isak and Gyökeres alone up top as a twin-9, and everything aimed at the one result that survives — a victory.

## Formation
- Shape: 3-5-2 (Potter's must-win setup vs Japan; morphs to a 5-3-2 / 5-4-1 out of possession, with Isak and Gyökeres as a twin-9 threat)
- Role mapping (roster order in `sweden.yaml`):
  - index 0 (`sweden_0`, Nordfeldt): GK — first-choice keeper, distributes to the back three or long to the strikers.
  - index 1 (`sweden_1`, Lindelöf): LCB — captain and ball-playing left-sided centre-back, the brain of the defence.
  - index 2 (`sweden_2`, Hien): CB — central pillar, physical destroyer, aerial dominance.
  - index 3 (`sweden_3`, Lagerbielke): RCB — right-sided stopper, covers behind the right wing-back.
  - index 4 (`sweden_4`, Gudmundsson): LWB — left wing-back, attacking outlet, primary left-side crosser & set-piece deliverer.
  - index 5 (`sweden_5`, Ayari): LCM — box-to-box engine and progressor; long-range threat (scored twice vs Tunisia).
  - index 6 (`sweden_6`, Karlström): DM — deep-lying anchor, screens the back three.
  - index 7 (`sweden_7`, Nygren): RCM — creative attacking midfielder, arrives late in the box; sharp left-foot finisher.
  - index 8 (`sweden_8`, Bernhardsson): RWB — right wing-back, pace and width, overlaps and crosses on the right.
  - index 9 (`sweden_9`, Isak): LF/second-9 — mobile, drifts infield and drops into pockets; dribble + finish.
  - index 10 (`sweden_10`, Gyökeres): CF — physical runner, leads the line, relentless in behind.

## Style of Play

### Build-up
Mixed. The back three splits with Lindelöf and Lagerbielke wide; Karlström drops between/in front of them to receive. Nordfeldt builds short when allowed but goes long to Gyökeres when pressed. Wing-backs Gudmundsson and Bernhardsson push high to provide the width while the midfield trio rotates. Sweden are equally happy in transition — they don't NEED the ball to hurt opponents.

### Pressing (block height + trigger)
Aggressive front press from Isak and Gyökeres, then a compact retreat. Press triggers when an opposition CB receives facing his own goal — the nearest striker curves to cut the back pass. Otherwise Sweden drop into a 5-3-2 / 5-4-1, the wing-backs tucking in to make a back five and the midfield three screening centrally.

### Defensive shape
5-3-2 / 5-4-1 with a back three plus two recovering wing-backs. Karlström shields the centre-backs; Ayari and Nygren cover ground box-to-box. Hien dominates aerially in the middle; Lindelöf reads the game on the left, Lagerbielke handles the right. The extra centre-back gives cover for the high wing-backs — a deliberate guard against Japan's pacey counters through Doan and Ito.

### Wide play
Wing-backs are Sweden's width. On the left Gudmundsson overlaps and delivers; on the right Bernhardsson's pace stretches the line. Both target the channels behind the opposition full-backs, and their cutbacks from the byline are the staple chance creation for the twin-9.

### Final third
Two-9 chaos. Isak drifts off the left into pockets, drags a CB, opening space for Gyökeres to attack in behind. Ayari and Nygren arrive late for cutbacks — both genuine goal threats from midfield. With no third forward, the wing-backs must get to the byline and the midfielders must crash the box.

## Set Pieces
- Corners: Gudmundsson delivers from the left (outswingers toward Hien and Gyökeres); inswingers from the right toward the near-post run. Hien, Gyökeres and Lagerbielke attack the box.
- Direct free kicks: Ayari from central/right positions (long-range threat); Nygren's left foot from the right channel; Gudmundsson's left foot from the left.
- Penalties: Isak first; Gyökeres second; Ayari third.

## decide() Decision Priorities
1. If my player_id ends with "_9" (LF/second-9, Isak): drift infield off the left into the pocket between the opposition DM and CB; when receiving, turn forward and DRIBBLE if 1v1.
2. If my player_id ends with "_10" (CF, Gyökeres): when "_9" (Isak) drops into the pocket, sprint diagonally across the back line — stay the #9 and attack the space in behind.
3. If my player_id ends with "_8" (RWB, Bernhardsson): on every regain, sprint into the RIGHT channel behind the opposition full-back — pace is the outlet. When defending, tuck in to make a back five.
4. If my player_id ends with "_0" (GK, Nordfeldt): if Sweden regains the ball or wins a goal kick under heavy press, kick LONG toward "_10" (Gyökeres) or into the wide channels for the wing-backs.
5. If my player_id ends with "_5" (LCM, Ayari): box-to-box engine — when receiving with space ahead in midfield, DRIBBLE forward 10-15m, then either PASS a vertical lane to "_9"/"_10" or SHOOT from 20-25m if the lane is clear (long-range threat).
6. If my player_id ends with "_6" (DM, Karlström): never cross the halfway line. Pure screen of the back three. If an opposition midfielder breaks through, TACKLE; otherwise recycle to the centre-backs.
7. If my player_id ends with "_7" (RCM, Nygren): creative engine — when "_5" (Ayari) and "_6" (Karlström) hold, make a late run into the box for cutbacks; if receiving in the half-space within 22m with a clear sight of goal, SHOOT (sharp left foot).
8. If my player_id ends with "_4" (LWB, Gudmundsson): when team_phase is "attacking", advance to LM height and provide the width; primary left-side crosser. When defending, tuck in to make a back five.
9. If my player_id ends with "_1" (LCB, Lindelöf): if no opposition forward within 8m AND a Swedish forward makes a vertical run, PASS the line-breaking long ball (pass 15); otherwise build short.
10. If my player_id ends with "_2" (CB, Hien): physical central CB — clear all crosses with strength; mark the tallest attacker on opposition set pieces; never attempt a controlled clearance under pressure.
11. If my player_id ends with "_3" (RCB, Lagerbielke): cover the space behind the overlapping "_8" (Bernhardsson); stay home when the right wing-back is high — Japan's counters come fast.
12. On opposition corner: "_2" (Hien) marks the tallest attacker; "_9" (Isak) and "_10" (Gyökeres) stay high near halfway as counter outlets (their pace is wasted in the box defensively).
13. When trailing late (a draw is not enough vs Japan): push "_2" (Hien) forward for set pieces; shift to a front-loaded shape with the wing-backs as auxiliary forwards flanking the twin-9.

## Key Player Notes
- **Alexander Isak (index 9):** technically gifted second-9 off the left — shoot 17, dribbling 16, skill 16, penalty 17 (first taker). License to drift infield and drop into midfield to receive; expect him to combine 1-2 then sprint into the box. Scored vs Tunisia and assisted Gyökeres.
- **Viktor Gyökeres (index 10):** runner-finisher hybrid — shoot 17, strength 16, speed 16. Leads the line as the #9; his ball-in-behind runs are constant. Scored vs Tunisia.
- **Yasin Ayari (index 5):** box-to-box engine and breakout star — skill 15, pass 15, shoot 14. Scored a brace (two long-range strikes) vs Tunisia; license to shoot from distance and arrive for cutbacks.
- **Benjamin Nygren (index 7):** creative attacking midfielder added for the must-win game — sharp left-foot finisher (16 club goals), skill 15. Arrives late in the box and shoots from the half-space; the extra goal threat from midfield with only two forwards up top.
- **Alexander Bernhardsson (index 8):** pace and width at right wing-back (speed 15); targets the channel behind the opposition full-back and whips cutbacks for the twin-9.
- **Victor Lindelöf (index 1):** captain and brain of the back three; left-sided ball-player who steps the line and starts attacks.
- **Isak Hien (index 2):** central defensive pillar — strength 16; wins everything in the air and anchors the back three.

## Tournament Mindset
This is the knife-edge. Sweden flew out of the blocks with a 5-1 rout of Tunisia, then were brutally exposed by the Netherlands in a 5-1 defeat that dropped them to third in Group F on three points. Only a win against Japan keeps the dream alive — a draw sends Japan through and likely ends Sweden's tournament. Potter answers with control: a 3-5-2 that adds a midfielder, packs the centre against Japan's quick wide men (Doan, Ito), and pours everything into servicing Isak and Gyökeres. They will absorb pressure behind a back five, screen the half-spaces, and trust two world-class strikers to convert the moments that win a World Cup knockout-in-disguise.
