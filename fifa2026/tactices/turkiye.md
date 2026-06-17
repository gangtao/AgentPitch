# Türkiye — Tactical Profile

## Identity & Philosophy
Türkiye under Vincenzo Montella are a technically rich, possession-leaning side built around a deep-lying regista (Hakan Çalhanoğlu, captain, #10) and an emerging generational creator (Arda Güler, #8). Montella has imposed Italian tactical structure on a squad bursting with flair. Türkiye reached their first World Cup since 2002 off the back of a thrilling Euro 2024 quarterfinal run — they arrived as a dark horse, capable of carving open defenses with technical quality and equally capable of late-game self-destruction. That second tendency cost them on Matchday 1: a flat, error-prone 2-0 defeat to Australia in Vancouver where they dominated the ball but never threatened. With Paraguay (June 19, Levi's Stadium) now a must-not-lose, Montella keeps faith with the same shape but demands more verticality and cutting edge in the final third.

## Formation
- Shape: 4-2-3-1 (double pivot; attacking band of three behind a lone striker)
- Role mapping (roster order in `turkiye.yaml`):
  - index 0 (`turkiye_0`, Çakır): GK — first-choice keeper, commanding shot-stopper, decent distribution.
  - index 1 (`turkiye_1`, Kadıoğlu): LB — modern fullback, creates chances (5 vs Australia), can invert into midfield.
  - index 2 (`turkiye_2`, Bardakcı): LCB — left-footed, physical, strong in the air.
  - index 3 (`turkiye_3`, Demiral): RCB — physical, aerial, aggressive.
  - index 4 (`turkiye_4`, Çelik): RB — disciplined overlapper.
  - index 5 (`turkiye_5`, Çalhanoğlu): DM/regista — deepest playmaker, long-range passer, set-piece & penalty taker.
  - index 6 (`turkiye_6`, Yüksek): DM — defensive midfielder, ball-winner alongside Çalhanoğlu.
  - index 7 (`turkiye_7`, Yılmaz): LW — direct, powerful runner, beats defenders and shoots.
  - index 8 (`turkiye_8`, Kökçü): AM — left-footed connector in the #10 slot, ball progression and arriving runs.
  - index 9 (`turkiye_9`, Güler): RW — drifts inside off the right, primary creator, the next great Turkish playmaker.
  - index 10 (`turkiye_10`, Aktürkoğlu): CF — pacy, mobile lone striker who also drifts wide; alternative is Deniz Gül.

## Style of Play

### Build-up
Patient, technical. Çakır plays to Bardakcı or Demiral; Çalhanoğlu drops deep between the CBs forming a 3-2 build. Kadıoğlu can invert into midfield, creating a numerical superiority. Türkiye are comfortable on the ball — they will spend long periods in the build phase if pressed lightly. The Australia game exposed the flaw: lots of possession, too few penetrative passes. The instruction now is to break lines earlier.

### Pressing (block height + trigger)
Medium-high block — line of confrontation around 5-10m inside opposition half. Press is selective rather than constant: triggered when an opposition CB plays a square pass under pressure. Yılmaz and Güler jump the wide CBs; Aktürkoğlu blocks the central passing lane.

### Defensive shape
4-4-2 out of possession: Kökçü pushes alongside Aktürkoğlu. Yüksek anchors and shuttles laterally; Çalhanoğlu drops alongside in a double-pivot. Wingers track back diligently to form a midfield bank of four.

### Wide play
Wingers are the primary 1v1 threat. Yılmaz (LW) is the more direct, powerful runner; Güler (RW) drifts inside off the right to combine and shoot. Both fullbacks support: Çelik (RB) overlaps to give the width Güler abandons; Kadıoğlu pushes high and creates from the left.

### Final third
Through-balls from Güler and Çalhanoğlu, cutbacks from Kadıoğlu and the wide players, long-range shots from Güler and Kökçü. Aktürkoğlu makes diagonal runs in behind the back line. Demiral arrives for set pieces — a major aerial threat.

## Set Pieces
- Corners: Çalhanoğlu delivers everything. Inswingers from the right toward Demiral (near post) and Bardakcı (back post).
- Direct free kicks: Çalhanoğlu from anywhere within 30m. Güler as alternative from the left.
- Penalties: Çalhanoğlu first (lethal, Inter Milan regular taker); Güler second.

## decide() Decision Priorities
1. If my player_id ends with "_5" (DM/regista, Çalhanoğlu): every tick, scan for long diagonal switches (≥30m) to the opposite winger. If the switch is available and that flank has space, PASS immediately.
2. If my player_id ends with "_5" (Çalhanoğlu): if receiving with time (>2 seconds estimated) and a runner is in the channel between CB and FB, attempt a long through-ball — prioritize verticality over recycling.
3. If my player_id ends with "_9" (RW, Güler): receive between the lines facing forward; if "_10" (Aktürkoğlu) makes a back-line run, slip the through-ball within 1 tick. SHOOT if cutting inside within 22m.
4. If my player_id ends with "_7" (LW, Yılmaz): when isolated 1v1 with the RB and within 30m of the byline, DRIBBLE at him; cut inside for a shot or pull back a cutback.
5. If my player_id ends with "_8" (AM, Kökçü): drop to link play, then arrive late into the box; recycle to "_5" (Çalhanoğlu) only when no forward pass exists, otherwise progress vertically (pass 16).
6. If my player_id ends with "_1" (LB, Kadıoğlu): push high and create from the left (chance-creator); invert into midfield in the build phase alongside "_6" Yüksek when Türkiye is settled in possession; revert to LB when the ball is lost.
7. If my player_id ends with "_4" (RB, Çelik): overlap aggressively when "_9" (Güler) drifts inside — the right touchline width is his responsibility.
8. If my player_id ends with "_3" (RCB, Demiral): on an opposition cross, attack the ball physically; do NOT attempt a clean clearance, just clear it long.
9. If my player_id ends with "_10" (CF, Aktürkoğlu): make 2 distinct movements per attacking phase — one drop to feet, one run in behind. "_5" Çalhanoğlu and "_9" Güler read both options.
10. If my player_id ends with "_6" (DM, Yüksek): shadow the opposition #10, win second balls, recycle possession sideways/backward to "_5" (Çalhanoğlu) — never gamble a forward pass.
11. On regain in the opposition third: nearest player TACKLES; second-nearest demands a forward outlet from "_9" (Güler) or "_5" (Çalhanoğlu).
12. When trailing late: "_3" (Demiral) pushes forward as an auxiliary striker for crosses; "_2" (Bardakcı) stays as the lone CB.
13. Discipline note: players ending in "_3" (Demiral) have a card-risk profile — avoid late challenges in the defensive third when on a yellow.

## Key Player Notes
- **Hakan Çalhanoğlu (index 5):** the team's brain. Operates as a deep-lying regista — pass 18, skill 17. All set-pieces (corners, free-kicks, penalties). License to roam vertically into AM space when the band of three rotates.
- **Arda Güler (index 9, #8):** the team's future and creative focal point — both feet, dribble + pass + shoot all elite. Plays right but drifts inside; give him license to take long shots from the edge of the box.
- **Orkun Kökçü (index 8, #18):** left-footed connector in the #10 role; reliable progression (pass 16) and late box arrivals — the glue between the pivot and the front line.
- **Barış Alper Yılmaz (index 7, #21):** the most direct, powerful runner — speed 16, dribbling 15. Direct him to take on his man and drive at the byline.
- **Merih Demiral (index 3):** primary aerial threat on set pieces. Always crashes the box from corners.
- **Ferdi Kadıoğlu (index 1):** the most creative defender — created five chances vs Australia. Pushes high from left-back and can invert into midfield in possession.
- **Kenan Yıldız (bench):** Juventus winger and a starter on paper, but a calf problem kept him to a second-half cameo vs Australia. Likely an impact substitute again vs Paraguay rather than a full starter.

## Tournament Mindset
Türkiye trust their quality, but Matchday 1 was a wake-up call: 0 points, 2-0 down to Australia, dominant on the ball yet toothless. The Paraguay game is effectively must-not-lose — both sides lost their openers. They are not a counter-attacking team; they want the ball and must now turn possession into penetration. The discipline risk (cards, occasional defensive lapses) makes them vulnerable in transition, but their technical ceiling against tired legs in the second half remains dangerous — and a fit Yıldız off the bench is a late-game weapon.
