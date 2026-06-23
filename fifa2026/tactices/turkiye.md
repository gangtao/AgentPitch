# Türkiye — Tactical Profile

## Identity & Philosophy
Türkiye under Vincenzo Montella arrived at their first World Cup since 2002 as a fashionable dark horse — a technically rich, possession-leaning side built around a deep-lying regista (Hakan Çalhanoğlu, captain, #10) and a generational creator (Arda Güler, #8). The reality has been a chastening one. Montella's men dominated the ball but never the scoreline: a flat **0-2 defeat to Australia** in Vancouver on Matchday 1 (30 shots, 72% possession, no goals — Irankunda and Metcalfe punished them), then a damaging **0-1 loss to 10-man Paraguay** on Matchday 2 at Levi's Stadium, conceding Matías Galarza's strike after just 64 seconds — the fastest goal of the tournament — and failing to break down a side reduced to ten before half-time. Back-to-back defeats, **zero points, zero goals**, and **elimination confirmed** before the final group game. The recurring theme: a wealth of the ball, a poverty of penetration, and recurring early concessions. For the dead-rubber finale against the already-qualified **United States** (Thu June 25, SoFi Stadium, Inglewood), Montella — who keeps his job under FA backing — is expected to freshen the side and finally start **Kenan Yıldız** from the first whistle, demanding the verticality and cutting edge that two performances of sterile possession sorely lacked.

## Formation
- Shape: **4-2-3-1** (double pivot; attacking band of three behind a lone striker)
- Role mapping (roster order in `turkiye.yaml`):
  - index 0: GK — **Uğurcan Çakır** — first-choice keeper, commanding shot-stopper, decent distribution; kept busy and blameless across both losses.
  - index 1: LB — **Ferdi Kadıoğlu** — modern, creative fullback; created five chances vs Australia; can invert into midfield in the build phase.
  - index 2: LCB — **Abdülkerim Bardakcı** — left-footed, physical, strong in the air; the calmer ball-player of the pair.
  - index 3: RCB — **Merih Demiral** — physical, aerial, aggressive; primary set-piece aerial threat but carries a card-risk profile.
  - index 4: RB — **Zeki Çelik** — disciplined overlapping fullback; supplies the right-side width Güler abandons when he drifts inside.
  - index 5: LDM — **Hakan Çalhanoğlu** — captain and deepest playmaker (pass 18); long-range distributor, all set-pieces and penalties; drops between the CBs to form a 3-2 build.
  - index 6: RDM — **Orkun Kökçü** — left-footed two-way midfielder partnering Çalhanoğlu in the pivot; ball progression (pass 16) and arriving runs, screens the central channel.
  - index 7: LW — **Barış Alper Yılmaz** — direct, powerful wide runner (speed 16, dribbling 15); beats his man and shoots; the team's most vertical threat in the band of three.
  - index 8: AM — **Arda Güler** — the central creative focal point in the #10 slot; both feet, dribble + pass + shoot all elite; receives between the lines and drifts right to combine and shoot.
  - index 9: FWD — **Kenan Yıldız** — Juventus forward, set to start at last; directness and goal threat off the left flank of the front line, pace and a left-footed cutting-in shot.
  - index 10: CF — **Kerem Aktürkoğlu** — pacy, mobile lone striker who also drifts wide; led Türkiye's shot count and is the qualification hero; alternative is Deniz Gül.

## Style of Play

### Build-up
Patient, technical. Çakır plays to Bardakcı or Demiral; Çalhanoğlu drops deep between the CBs forming a 3-2 build. Kadıoğlu can invert into midfield, creating a numerical superiority. Türkiye are comfortable on the ball — across two games they have monopolised possession yet produced almost nothing decisive. The standing instruction for the USA game is to break lines earlier and pull the trigger sooner; sterile circulation has already cost them the tournament.

### Pressing (block height + trigger)
Medium-high block — line of confrontation around 5-10m inside the opposition half. The press is selective rather than constant: triggered when an opposition CB plays a square pass under pressure. Yılmaz and Güler jump the wide CBs; Aktürkoğlu blocks the central passing lane. Early-game concentration is the priority — both losses began with avoidable concessions inside the opening half-hour.

### Defensive shape
4-4-2 out of possession: Yıldız pushes alongside Aktürkoğlu up top. Kökçü anchors and shuttles laterally; Çalhanoğlu drops beside him in the double-pivot. The wide players track back diligently to form a midfield bank of four.

### Wide play
Wingers are the primary 1v1 threat. Yılmaz (LW) is the most direct, powerful runner; Yıldız drives at defenders off the left of the front line; Güler drifts inside off the right to combine and shoot. Both fullbacks support: Çelik (RB) overlaps to give the width Güler abandons; Kadıoğlu pushes high and creates from the left.

### Final third
Through-balls from Güler and Çalhanoğlu, cutbacks from Kadıoğlu and the wide players, long-range shots from Güler, Kökçü and Yıldız. Aktürkoğlu makes diagonal runs in behind the back line. Demiral arrives for set pieces — a major aerial threat. The mandate: fewer touches in front of the block, more passes that break it.

## Set Pieces
- Corners: Çalhanoğlu delivers everything. Inswingers from the right toward Demiral (near post) and Bardakcı (back post).
- Direct free kicks: Çalhanoğlu from anywhere within 30m. Güler and Yıldız (left-footed) as alternatives.
- Penalties: Çalhanoğlu first (lethal, Inter Milan regular taker); Güler second; Yıldız third.

## decide() Decision Priorities
1. If my player_id ends with "_5" (LDM/regista, Çalhanoğlu): every tick, scan for long diagonal switches (≥30m) to the opposite winger. If the switch is available and that flank has space, PASS immediately.
2. If my player_id ends with "_5" (Çalhanoğlu): if receiving with time (>2 seconds estimated) and a runner is in the channel between CB and FB, attempt a long through-ball — prioritize verticality over recycling.
3. If my player_id ends with "_8" (AM, Güler): receive between the lines facing forward; if "_10" (Aktürkoğlu) makes a back-line run, slip the through-ball within 1 tick. SHOOT if cutting inside within 22m.
4. If my player_id ends with "_7" (LW, Yılmaz): when isolated 1v1 with the RB and within 30m of the byline, DRIBBLE at him; cut inside for a shot or pull back a cutback.
5. If my player_id ends with "_9" (FWD, Yıldız): attack the left channel; drive at the defender off the left foot, cut inside to SHOOT within 24m, and make underlapping runs in behind when "_8" (Güler) or "_10" (Aktürkoğlu) holds the ball centrally.
6. If my player_id ends with "_6" (RDM, Kökçü): screen the central channel and recycle to "_5" (Çalhanoğlu) only when no forward pass exists, otherwise progress vertically (pass 16); arrive late into the box when the attack is settled.
7. If my player_id ends with "_1" (LB, Kadıoğlu): push high and create from the left (chance-creator); invert into midfield in the build phase alongside "_6" (Kökçü) when Türkiye is settled in possession; revert to LB when the ball is lost.
8. If my player_id ends with "_4" (RB, Çelik): overlap aggressively when "_8" (Güler) drifts inside — the right touchline width is his responsibility.
9. If my player_id ends with "_3" (RCB, Demiral): on an opposition cross, attack the ball physically; do NOT attempt a clean clearance, just clear it long.
10. If my player_id ends with "_10" (CF, Aktürkoğlu): make 2 distinct movements per attacking phase — one drop to feet, one run in behind. "_5" (Çalhanoğlu) and "_8" (Güler) read both options.
11. On regain in the opposition third: nearest player TACKLES; second-nearest demands a forward outlet from "_8" (Güler) or "_5" (Çalhanoğlu).
12. When trailing late: "_3" (Demiral) pushes forward as an auxiliary striker for crosses; "_2" (Bardakcı) stays as the lone CB.
13. Discipline note: players ending in "_3" (Demiral) have a card-risk profile — avoid late challenges in the defensive third when on a yellow.
14. Early-game discipline: from kickoff through tick 600, all defenders and the pivot ("_5", "_6") prioritise shape and a clean clearance over playing out under pressure — both group losses came from early concessions.

## Key Player Notes
- **Hakan Çalhanoğlu (index 5, #10):** the team's brain and captain. Operates as a deep-lying regista — pass 18, skill 17. All set-pieces (corners, free-kicks, penalties). License to roam vertically into AM space when the band of three rotates.
- **Arda Güler (index 8, #8):** the team's future and creative focal point — both feet, dribble + pass + shoot all elite. Nominally central but drifts right; give him license to take long shots from the edge of the box.
- **Kenan Yıldız (index 9, #9):** finally a starter after a calf problem limited him earlier. Pace, directness and a left-footed cutting-in shot off the left of the front line — Türkiye's freshest attacking weapon for the dead rubber.
- **Kerem Aktürkoğlu (index 10, #7):** pacy, mobile lone striker who led the team's shot count across the group stage; drifts wide and runs in behind. The qualification hero still hunting his first goal of the tournament.
- **Barış Alper Yılmaz (index 7, #21):** the most direct, powerful runner — speed 16, dribbling 15. Direct him to take on his man and drive at the byline.
- **Merih Demiral (index 3, #3):** primary aerial threat on set pieces. Always crashes the box from corners; manage his card risk in the defensive third.
- **Ferdi Kadıoğlu (index 1, #20):** the most creative defender — created five chances vs Australia. Pushes high from left-back and can invert into midfield in possession.

## Tournament Mindset
The dream is over before the final whistle of the group stage. Two performances of dominant, sterile possession yielded zero points and zero goals, two early concessions undid them, and Türkiye are eliminated heading into the USA game. The dead rubber at SoFi Stadium is about pride, a first goal, and an audition: Montella, backed by his FA but under fire, will freshen the side, hand Kenan Yıldız a start, and demand the verticality that was missing. They are not a counter-attacking team — they want the ball — but they must finally turn possession into penetration. With the pressure of qualification gone, their technical ceiling against a possibly-rotated United States side remains their one route to ending the tournament on a positive note.
