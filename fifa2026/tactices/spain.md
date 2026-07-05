# Spain — Tactical Profile

## Identity & Philosophy
Luis de la Fuente's Spain is the modern heir to tiki-taka, refreshed with vertical wide threats. The midfield (Rodri-Pedri + a third interior) is the team's bloodstream — they dictate tempo, rotate constantly, and starve opponents of the ball. Spain won Euro 2024 with 65% average possession across the tournament, then mixed that with the most direct wingers in world football (Yamal & Williams). Juego de posición with teeth. They arrive in USA/Mexico/Canada as the FIFA No. 2-ranked side, reigning European champions, and a heavy pre-tournament favourite. De la Fuente named a squad with no Real Madrid players (Carvajal, Huijsen omitted) and handed the captaincy to Rodri, his Ballon d'Or-winning pivot.

**Group stage (Group H): won it, unbeaten.** After a 0-0 shock draw with Cape Verde (MD1, Yamal rested with a hamstring, front three Ferran-Oyarzabal-Gavi), Spain roared back with a 4-0 demolition of Saudi Arabia (MD2 — Yamal opened his account on his first WC start, Oyarzabal brace) and closed the group with a 1-0 win over Uruguay (MD3), Álex Baena the match-winner and Man of the Match. Spain finished top of the group and, crucially, the **back line has not conceded a single goal in the tournament**.

**Round of 32 — Austria dispatched 3-0.** Spain cruised past Austria in the Round of 32 for their first non-group-stage World Cup win since the 2010 final, De la Fuente shifting to a **Pedro Porro / Dani Olmo** spine: Porro at right back and Olmo as the advanced interior. The clean-sheet run continued — Spain are one of only two sides left yet to concede.

**Round of 16 — the Iberian derby vs Portugal (Mon 6 Jul, AT&T Stadium, Dallas).** Yamal vs Ronaldo, part two. Two front-line wingers remain out: **Nico Williams (adductor strain — re-injured, ruled out)** and **Yéremy Pino (shoulder ligament sprain)**. With Williams gone, **Álex Baena** keeps the left. **Pedro Porro** starts at right back (Marcos Llorente is the alternative De la Fuente can turn to rather than risk Porro), and **Dani Olmo** operates as the advanced #8 / CAM ahead of the Rodri-Pedri base, providing a third goal threat and a link between lines. Yamal and Porro missed a Friday session for precautionary workload management but were cleared and start. No suspensions carry into the knockouts (group-stage yellows reset under FIFA rules; no Spain player was sent off). Probable XI (4-3-3 / 4-1-2-3): **Simón; Cucurella, Laporte, Cubarsí, Porro; Olmo, Rodri, Pedri; Baena, Oyarzabal, Yamal.**

## Formation
- Shape: 4-3-3 with a single pivot (Rodri); FBs ultra-high in possession (effectively 2-3-5)
- Role mapping (roster order in `spain.yaml`):
  - index 0: GK — Unai Simón (ball-playing keeper, build-up partner)
  - index 1: LB — Marc Cucurella (overlapping, sometimes inverts; left side overload)
  - index 2: LCB — Aymeric Laporte (ball-progressor; passes ~17 — the deeper playmaker of the pair)
  - index 3: RCB — Pau Cubarsí (composed young CB, line-breaking passer, steps out to cover)
  - index 4: RB — Pedro Porro (attacking, quick overlapping full-back, speed 17 / stamina 18; overlaps when Yamal cuts in and whips crosses to the back post)
  - index 5: LCM/#8 — Dani Olmo (left-side advanced interior; a second-striker-turned-#8 who arrives late in the box and shoots — skill 18 / shoot 16 / dribble 16; the goal threat from midfield, an alternate penalty option)
  - index 6: DM/#6 — Rodri (captain & irreplaceable pivot — pass 19, skill 18 — sets every tempo)
  - index 7: RCM/#8 — Pedri (right-side interior; receives between lines, the best on-ball link)
  - index 8: LW — Álex Baena (left-sided creator standing in for the injured Williams; skill 17 / pass 17 / shoot 15, drifts inside to combine rather than hugging the byline — Spain's dead-ball deliverer and scorer of the R16-clinching winner vs Uruguay)
  - index 9: CF — Mikel Oyarzabal (link-up #9, drops to combine, holds for runners; clinical finisher, shoot 17 — two goals vs Saudi Arabia; primary penalty taker)
  - index 10: RW — Lamine Yamal (inverted right winger; dribble 19 / shoot 17, drifts into the right half-space to curl with his left — Spain's primary creator and a set-piece taker)
  - bench impact: Fabián Ruiz (elegant left-footed #8, pass 17, long-range threat — the Euro 2024 incumbent, a high-impact change in the _5 slot), Mikel Merino (powerful box-to-box #8, strength 17 — aerial threat off the bench in the _5 slot), Marcos Llorente (athletic RB alternative to Porro, stamina 18 — the _4 slot), Gavi (relentless left-sided forward, stamina 18) and Ferran Torres (orthodox right width, shoot 16) are the key changes off the bench; they take the _4/_5/_8/_10 spatial roles when on

## Style of Play

### Build-up
- From Unai Simón: short to Laporte or Cubarsí every time. Goal-kick to row 1 unless pressed 4v4 high.
- Rodri drops between CBs only when needed (3-2-5 vs high press); otherwise stays as pivot.
- Both FBs step into midfield height; Pedri and Fabián float between lines.
- **Possession target ~65%**. Spain accepts U-shape passing (CB-DM-CB-DM) to wait for a vertical lane.

### Pressing
- Counter-press (Cruyff/Guardiola school): the moment Spain loses it, the nearest 3 players collapse on the carrier for 6 seconds. If not won back, drop to mid-block.
- Trigger high press: opponent CB receives with back to play, OR a square pass between CBs is in flight.
- Oyarzabal leads, Baena & Yamal curve runs to lock the FBs. Pedri/Olmo jump #6.

### Defensive shape
- 4-1-4-1 with Rodri shielding. High line (offside trap) — line ~ 50% of pitch length.
- Olmo and Pedri have moderate defensive responsibility; tracking back is shared by the wingers.
- Vulnerable to direct balls in behind — Spain accepts the risk for compression.

### Wide play
- Asymmetric width: **LEFT** Baena (_8) drifts inside off the touchline to combine in the half-space (skill 17 / pass 17) → Cucurella now provides the overlapping width outside him rather than underlapping. **RIGHT** Yamal (_10) starts wide but drifts into the half-space to cut inside on his left → Porro overlaps outside to give him the cutback option. (With Williams injured, the left is an inside-combination channel first; if Ferran/Gavi sub on, the shape flexes back toward orthodox stretch-and-back-post width on either flank.)
- Half-space combinations: the right-side Yamal-Pedri-Porro triangle is Spain's most dangerous pattern — Yamal cuts in, Pedri links, Porro overlaps.

### Final third
- Patience first: ~30-40 passes per chance is not unusual. Wait for the FB overlap or the inside-forward cutback.
- Cutback target: Oyarzabal at the penalty spot, Olmo arriving late from deep to attack it (skill 18 / shoot 16).
- Yamal's left-foot half-space curler from the right is the recurring termination; Baena's inswinging delivery from the left and Oyarzabal's near-post finish are the alternatives.

## Set Pieces
- Corners: Inswingers from Baena on left, Yamal/Pedri on right. Oyarzabal + Laporte + Cubarsí + Olmo attack near/back posts. Rodri at edge of box for rebounds.
- Direct FKs: Yamal (right, primary), Baena (left/central — lethal dead-ball delivery, scored a FK in the 2024 Olympic final), Laporte (central, power).
- **Penalty-shootout order (knockout — level after 90/120 mins goes to a shootout, so this order is live):**
  1. **Oyarzabal** — first taker; ice-cold, scored the Euro 2024 final winner (penalty 17).
  2. **Yamal** — penalty 16, primary creator with the composure for it.
  3. **Pedri** — penalty 16.
  4. **Rodri** — captain, penalty 15.
  5. **Olmo** — penalty 14, the advanced #8 with the composure to close out the five.
  - Note: **Baena is NOT in the top shootout five** despite his dead-ball quality — his real-world spot-kick record is poor (penalty 9); he takes free kicks and corners, not penalties.
- Defending: zonal with 2 man-markers on biggest threats. Rodri patrols the edge of the box.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only go long if pressed 4v4 and no FB option.
2. When my `player_id` ends with `_6` (DM — Rodri): if no one is open vertically, pass back to CB; never force; my job is to wait — pass 19 means I am the metronome.
3. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Laporte/Cubarsí) and team has ball: pass to the `_6` player (Rodri) first preference, then to the other CB, then to FB. Avoid long balls.
4. When my role is DEF and `player_id` ends with `_1` or `_4` (FB pair) and team_phase is "attacking": advance to LM/RM height; if my `player_id` ends with `_4` (Porro) and the `_10` player (Yamal) cuts inside, I overlap outside him; if my `player_id` ends with `_1` (Cucurella) and the `_8` player (Baena) drifts inside off the left touchline, I overlap OUTSIDE him to provide the width Baena vacates.
5. When my `player_id` ends with `_5` or `_7` (#8 pair — Olmo/Pedri) and team has the ball: position in opposite half-space from the ball; when received, turn forward — never backward (Pedri pass 19). If I am `_5` (Olmo), also make late runs into the box for cutbacks and shots (skill 18 / shoot 16).
6. When my `player_id` ends with `_8` (LW — Baena): receive on the left, then drift INSIDE into the half-space to combine (skill 17 / pass 17) rather than beating the FB on the outside; play the give-and-go with `_5`/`_9`, deliver the inswinging cross, or Shoot from the left half-space (shoot 15) — let overlapping `_1` (Cucurella) take the outside width.
7. When my `player_id` ends with `_10` (RW — Yamal): start wide then drift into the right half-space; if the ball comes to my feet, Move inside and Shoot with my left (dribble 19 / shoot 17), OR Pass to overlapping `_4` (Porro) outside me.
8. When my `player_id` ends with `_9` (CF — Oyarzabal): drop 8-10m short to receive, lay off to interiors, then run in behind for the cutback.
9. When ball is lost: immediate 6-second counter-press. Nearest 3 players Move toward the carrier; if I am the closest, Tackle.
10. When team_phase is "defending" in mid-block: hold a high line — offside trap is the rule. CBs Move forward in sync the moment opponent plays backward.
11. Shoot from outside the box only if my `player_id` ends with `_10`, `_8`, `_7`, or `_2` (Yamal/Baena/Pedri/Laporte) AND there's a clear lane.
12. When in doubt, Hold and recycle. Tempo is a weapon.

## Key Player Notes
- **Rodri (idx 6)** — captain and the system. Without him, Spain is a different team. Never goes above the halfway line in open play; an alternate penalty taker.
- **Pedri (idx 7)** — best on-ball player; the connector between defense and attack. Free to roam in opponent half.
- **Lamine Yamal (idx 10)** — Spain's primary creator and most decisive attacker. Inverted right winger with license to drift into the half-space and shoot with his left (dribble 19 / shoot 17); the right-side set-piece taker and No. 2 in the shootout order. Fit through the knockouts after his group-stage hamstring scare.
- **Álex Baena (idx 8)** — stands in for the injured Nico Williams on the left. A creative inside-forward, not a touchline burner (skill 17 / pass 17 / shoot 15): drifts into the half-space to combine and delivers Spain's left-side dead balls. Scored the Man-of-the-Match winner vs Uruguay that clinched top spot. NOTE: poor real-world penalty record — a free-kick/corner specialist, NOT a shootout taker.
- **Dani Olmo (idx 5)** — the advanced #8 / CAM in De la Fuente's knockout shape (skill 18 / shoot 16 / dribble 16). A second-striker-turned-interior who arrives late in the box and shoots — the goal threat from midfield and an alternate penalty option (No. 5 in the shootout order).
- **Pedro Porro (idx 4)** — attacking right back (speed 17 / stamina 18) who overlaps outside Yamal when the winger cuts in and whips crosses to the back post; the right-side width in the 2-3-5.
- **Fabián Ruiz / Mikel Merino (bench, _5 when on)** — Fabián is the elegant left-footed Euro 2024 incumbent (long-range threat, pass 17); Merino is the powerful aerial box-to-box option (strength 17). Both high-impact changes in the advanced-interior slot.
- **Marcos Llorente (bench, _4 when on)** — athletic RB alternative to Porro (stamina 18); the change De la Fuente turns to rather than risk Porro.
- **Gavi (bench)** — relentless energy and pressing (stamina 18), drifts inside to combine. High-impact change on the left or in midfield.
- **Ferran Torres (bench, _10/_8 when on)** — orthodox width with a real goal threat (shoot 16), arrives at the back post. A high-impact change given the winger injuries.
- **Oyarzabal (idx 9)** — clinical, selfless #9 and the No. 1 penalty/shootout taker (scored the Euro 2024 final winner); links play and finishes the cutbacks.
- **Cubarsí (idx 3)** — composed young ball-playing CB; steps out to break lines and covers the space behind the overlapping Porro.
- **Cucurella (idx 1)** — sometimes inverts into the DM line when Rodri pushes forward; flexible role.

## Tournament Mindset
**Round of 16 — win or go home.** The group is over; there are no points, no standings, no second chances. Ninety minutes to survive; if it is level, thirty more of extra time; if still level, a penalty shootout. Spain must win the match, not just the ball.

The opponent is **Portugal** — the Iberian derby, Yamal vs Ronaldo part two. Portugal are a heavyweight with elite individuals (Ronaldo, Bruno Fernandes, Bernardo Silva, Vitinha, Rafael Leão) who can hurt Spain both in transition and on the ball, and who carry a genuine set-piece and aerial threat led by Ronaldo. This is not the deep-block puzzle Austria posed: Portugal will contest possession, so Spain must win the midfield battle (Rodri-Pedri-Olmo) and the counter-press to keep the game on their terms. Keep the ball, move Portugal side to side, wait for the Yamal-Pedri-Porro right-side triangle or a Baena combination on the left to unlock the door. The high line must stay disciplined against Leão's pace in behind, and set-piece marking must account for Ronaldo — the one goal that has not yet been conceded is the edge to protect.

Spain carry two edges into this tie: a back line that **has not conceded in the tournament**, and the calm of knowing that if Austria drag it to a shootout, Spain have the nerve and the takers (Oyarzabal, Yamal, Pedri, Rodri, Llorente) to win it. The winger injuries (Williams, Pino) thin the bench, so managing the game — protecting the lead once it comes, staying 11 v 11, avoiding needless bookings that could compound over a long knockout run — matters more than ever. Identity unchanged: keep the ball, break them down, and see it through to the whistle — however many whistles it takes.
