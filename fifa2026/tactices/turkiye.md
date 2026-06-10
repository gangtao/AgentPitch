# Türkiye — Tactical Profile

## Identity & Philosophy
Türkiye under Vincenzo Montella are a technically rich, possession-leaning side built around a deep-lying regista (Hakan Çalhanoğlu, captain, #10), an emerging generational creator (Arda Güler, #8), and pacy, direct wingers. Montella has restored Italian tactical structure while embracing the natural flair of his squad. Having reached their first World Cup since 2002 via the European playoffs, and off the back of a thrilling Euro 2024 quarterfinal run, Türkiye arrive as a dark horse — capable of carving open defenses with technical quality and equally capable of late-game self-destruction.

## Formation
- Shape: 4-2-3-1
- Role mapping (roster order in `turkiye.yaml`):
  - index 0 (`turkiye_0`, Günok): GK — solid shot-stopper, decent distribution.
  - index 1 (`turkiye_1`, Kadıoğlu): LB — modern inverted fullback, can play midfield.
  - index 2 (`turkiye_2`, Bardakcı): LCB — left-footed, physical, strong in the air.
  - index 3 (`turkiye_3`, Demiral): RCB — physical, aerial, aggressive.
  - index 4 (`turkiye_4`, Çelik): RB — disciplined overlapper.
  - index 5 (`turkiye_5`, Çalhanoğlu): DM/regista — deepest playmaker, long-range passer.
  - index 6 (`turkiye_6`, Yüksek): DM — defensive midfielder, runs alongside Çalhanoğlu.
  - index 7 (`turkiye_7`, Aktürkoğlu): RW — direct, cuts in onto left foot, shoots.
  - index 8 (`turkiye_8`, Güler): AM — primary creator, the next great Turkish #10.
  - index 9 (`turkiye_9`, Yıldız): LW — direct dribbler, beats defenders 1v1.
  - index 10 (`turkiye_10`, Yılmaz): CF — runs in behind, mobile striker.

## Style of Play

### Build-up
Patient, technical. Günok plays to Bardakcı or Demiral; Çalhanoğlu drops deep between the CBs forming a 3-2 build. Kadıoğlu inverts into midfield, creating a numerical superiority. Türkiye are comfortable on the ball — they will spend long periods in the build phase if pressed lightly.

### Pressing (block height + trigger)
Medium-high block — line of confrontation around 5-10m inside opposition half. Press is selective rather than constant: triggered when an opposition CB plays a square pass under pressure. Aktürkoğlu and Yıldız jump the wide CBs; Yılmaz blocks the central passing lane.

### Defensive shape
4-4-2 out of possession: Güler pushes alongside Yılmaz. Yüksek anchors and shuttles laterally; Çalhanoğlu drops alongside in a double-pivot. Wingers track back diligently to form a midfield bank of four.

### Wide play
Wingers are the primary 1v1 threat. Yıldız (LW) is the dribbler-in-chief — speed 16, dribbling 17. Aktürkoğlu (RW) cuts inside to shoot. Both fullbacks support, but Çelik (RB) overlaps more than Kadıoğlu (who inverts).

### Final third
Through-balls from Güler and Çalhanoğlu, cutbacks from the wide players, long-range shots from Aktürkoğlu. Yılmaz makes diagonal runs across the back line. Demiral arrives for set pieces — a major aerial threat.

## Set Pieces
- Corners: Çalhanoğlu delivers everything. Inswingers from the right toward Demiral (near post) and Bardakcı (back post).
- Direct free kicks: Çalhanoğlu from anywhere within 30m. Güler as alternative from the left.
- Penalties: Çalhanoğlu first (lethal, Inter Milan regular taker); Güler second.

## decide() Decision Priorities
1. If my player_id ends with "_5" (DM/regista, Çalhanoğlu): every tick, scan for long diagonal switches (≥30m) to opposite winger. If switch is available and that flank has space, PASS immediately.
2. If my player_id ends with "_5" (Çalhanoğlu): if receiving with time (>2 seconds estimated) and a runner is in the channel between CB and FB, attempt a long through-ball.
3. If my player_id ends with "_8" (AM, Güler): receive between the lines facing forward; if "_10" (Yılmaz) makes a back-line run, slip the through-ball within 1 tick.
4. If my player_id ends with "_9" (LW, Yıldız): when isolated 1v1 with RB and within 30m of byline, DRIBBLE inside aiming for shot or cutback.
5. If my player_id ends with "_7" (RW, Aktürkoğlu): when receiving wide right, cut inside immediately onto left foot; SHOOT if within 22m of goal.
6. If my player_id ends with "_1" (LB, Kadıoğlu): invert into midfield in the build phase (move to LDM position alongside "_6" Yüksek); revert to LB when Türkiye loses the ball.
7. If my player_id ends with "_4" (RB, Çelik): overlap aggressively when "_7" (Aktürkoğlu) cuts inside — the touchline width is his responsibility.
8. If my player_id ends with "_3" (RCB, Demiral): on opposition cross, attack the ball physically; do NOT attempt a clean clearance, just clear it long.
9. If my player_id ends with "_10" (CF, Yılmaz): make 2 distinct movements per attacking phase — one drop to feet, one in behind. "_5" Çalhanoğlu reads both options.
10. If my player_id ends with "_6" (DM, Yüksek): shadow opposition #10, recycle possession sideways/backward to "_5" (Çalhanoğlu) — never gamble a forward pass.
11. On regain in opposition third: nearest player TACKLES; second-nearest demands forward outlet from "_8" (Güler) or "_5" (Çalhanoğlu).
12. When trailing late: "_3" (Demiral) pushes forward as auxiliary striker for crosses; "_2" (Bardakcı) stays as lone CB.
13. Discipline note: players ending in "_3" (Demiral) and "_10" (Yılmaz) have a card-risk profile — avoid late challenges in defensive third when on a yellow.

## Key Player Notes
- **Hakan Çalhanoğlu (index 5):** the team's brain. Operates as a deep-lying regista — pass 18, skill 17. All set-pieces (corners, free-kicks, penalties). License to roam vertically into AM space when Güler drifts wide.
- **Arda Güler (index 8, #8):** the team's future. Free role between the lines, both feet, dribble + pass + shoot all elite for an AM. Allow him to take long shots from edge of box.
- **Kenan Yıldız (index 9, #11):** primary 1v1 dribbler — dribbling 17. Direct him to take on his man every time he receives wide.
- **Merih Demiral (index 3):** primary aerial threat on set pieces. Always crashes the box from corners.
- **Ferdi Kadıoğlu (index 1):** modern inverted fullback role — moves into midfield in possession, generates +1 in central buildup.

## Tournament Mindset
Türkiye trust their quality. They are not a counter-attacking team — they want the ball and will hurt opponents who give it to them. The discipline risk (high cards, occasional defensive lapses) makes them vulnerable to teams that exploit transitions, but their technical ceiling against tired legs in the second half is dangerous.
