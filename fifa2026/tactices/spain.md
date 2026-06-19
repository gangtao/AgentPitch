# Spain — Tactical Profile

## Identity & Philosophy
Luis de la Fuente's Spain is the modern heir to tiki-taka, refreshed with vertical wide threats. The midfield (Rodri-Pedri-Fabián) is the team's bloodstream — they dictate tempo, rotate constantly, and starve opponents of the ball. Spain won Euro 2024 with 65% average possession across the tournament, then mixed that with the most direct wingers in world football (Yamal & Williams). Juego de posición with teeth. They arrive in USA/Mexico/Canada as the FIFA No. 2-ranked side, reigning European champions, and a heavy pre-tournament favourite — drawn into Group H with Cape Verde, Uruguay and Saudi Arabia. De la Fuente named a squad with no Real Madrid players (Carvajal, Huijsen omitted) and handed the captaincy to Rodri, his Ballon d'Or-winning pivot.

**Matchday 1 update (15 June, vs Cape Verde — 0-0):** A 0-0 stalemate and one of the tournament's biggest early shocks. Spain piled up 27 shots (7 on target) but Cape Verde keeper Vozinha and a deep block held firm. Crucially, with Lamine Yamal managing a hamstring, de la Fuente started a more functional front three — **Ferran Torres (right), Oyarzabal (centre), Gavi (left)** — and kept Yamal and Nico Williams on the bench (Yamal came on in the second half but could not break the deadlock). Only one booking (Pedri, 90+3'), no suspensions. For Matchday 2 vs Saudi Arabia (21 June) the wide-forward workload is the chief selection watch point; the most likely XI continues with the Cape Verde front three (Ferran/Oyarzabal/Gavi) and Yamal/Williams as high-impact options off the bench while Yamal's minutes are managed. The defence and midfield are unchanged from MD1.

## Formation
- Shape: 4-3-3 with a single pivot (Rodri); FBs ultra-high in possession (effectively 2-3-5)
- Role mapping (roster order in `spain.yaml`):
  - index 0: GK — Unai Simón (ball-playing keeper, build-up partner)
  - index 1: LB — Marc Cucurella (overlapping, sometimes inverts; left side overload)
  - index 2: LCB — Aymeric Laporte (ball-progressor; passes ~17 — the deeper playmaker of the pair)
  - index 3: RCB — Pau Cubarsí (composed young CB, line-breaking passer, steps out to cover)
  - index 4: RB — Marcos Llorente (athletic, overlaps when Yamal cuts in; big lungs, stamina 18)
  - index 5: LCM/#8 — Fabián Ruiz (left-side advanced interior; elegant left foot, arrives in box late, half-space passer & long-range threat — this third-midfield slot is contested by Gavi, Merino and Dani Olmo, but Fabián is the Euro 2024 incumbent)
  - index 6: DM/#6 — Rodri (captain & irreplaceable pivot — pass 19, skill 18 — sets every tempo)
  - index 7: RCM/#8 — Pedri (right-side interior; receives between lines, the best on-ball link)
  - index 8: LW — Gavi (left-sided forward; energetic, drifts inside to combine and presses relentlessly; stamina 18 — MD1 starter with Williams benched)
  - index 9: CF — Mikel Oyarzabal (link-up #9, drops to combine, holds for runners; clinical finisher, shoot 17)
  - index 10: RW — Ferran Torres (right-sided forward; orthodox width with a goal threat, shoot 16 — MD1 starter while Yamal's minutes are managed)
  - bench impact: Nico Williams (vertical byline LW, speed 19) and Lamine Yamal (inverted RW, dribble 19 / shoot 17) enter to change games — the _8 and _10 spatial roles are theirs when on

## Style of Play

### Build-up
- From Unai Simón: short to Laporte or Cubarsí every time. Goal-kick to row 1 unless pressed 4v4 high.
- Rodri drops between CBs only when needed (3-2-5 vs high press); otherwise stays as pivot.
- Both FBs step into midfield height; Pedri and Fabián float between lines.
- **Possession target ~65%**. Spain accepts U-shape passing (CB-DM-CB-DM) to wait for a vertical lane.

### Pressing
- Counter-press (Cruyff/Guardiola school): the moment Spain loses it, the nearest 3 players collapse on the carrier for 6 seconds. If not won back, drop to mid-block.
- Trigger high press: opponent CB receives with back to play, OR a square pass between CBs is in flight.
- Oyarzabal leads, Yamal & Williams curve runs to lock the FBs. Pedri/Fabián jump #6.

### Defensive shape
- 4-1-4-1 with Rodri shielding. High line (offside trap) — line ~ 50% of pitch length.
- Fabián and Pedri have moderate defensive responsibility; tracking back is shared by the wingers.
- Vulnerable to direct balls in behind — Spain accepts the risk for compression.

### Wide play
- Asymmetric width: **LEFT** Gavi (_8) holds the wide channel and combines inside → Cucurella overlaps/underlaps. **RIGHT** Ferran (_10) stretches the line and arrives at the back post → Llorente overlaps. (When Williams/Yamal sub on, the pattern sharpens into pure byline width left and inverted-cut right.)
- Half-space combinations: the right-side Ferran-Pedri-Llorente triangle is Spain's most dangerous pattern.

### Final third
- Patience first: ~30-40 passes per chance is not unusual. Wait for the FB overlap or the inside-forward cutback.
- Cutback target: Oyarzabal at the penalty spot, Fabián arriving late from deep.
- Ferran's run to the back post / strike from the right is a recurring termination (Yamal's left-foot half-space curler when he subs on).

## Set Pieces
- Corners: Inswingers from Fabián on left, Pedri/Ferran on right (Yamal when on). Oyarzabal + Laporte + Cubarsí attack near/back posts. Rodri at edge of box for rebounds.
- Direct FKs: Fabián (left), Ferran/Pedri (right), Laporte (central, power); Yamal takes over when on.
- Penalties: Oyarzabal is first taker (cool finisher — winner in the Euro 2024 final); Rodri (captain) and Yamal are alternates.
- Defending: zonal with 2 man-markers on biggest threats. Rodri patrols the edge of the box.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only go long if pressed 4v4 and no FB option.
2. When my `player_id` ends with `_6` (DM — Rodri): if no one is open vertically, pass back to CB; never force; my job is to wait — pass 19 means I am the metronome.
3. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Laporte/Cubarsí) and team has ball: pass to the `_6` player (Rodri) first preference, then to the other CB, then to FB. Avoid long balls.
4. When my role is DEF and `player_id` ends with `_1` or `_4` (FB pair) and team_phase is "attacking": advance to LM/RM height; if my `player_id` ends with `_4` (Llorente) and the `_10` player (Ferran/Yamal) is occupied inside, I overlap; if my `player_id` ends with `_1` (Cucurella) and the `_8` player (Gavi/Williams) holds the left, I support into half-space.
5. When my `player_id` ends with `_5` or `_7` (#8 pair — Fabián/Pedri) and team has the ball: position in opposite half-space from the ball; when received, turn forward — never backward (Pedri pass 19, Fabián pass 17).
6. When my `player_id` ends with `_8` (LW — Gavi, or Williams off the bench): receive wide on the left, take on the FB 1v1 with Move toward + Move diagonal; Shoot only if cutting inside near angle.
7. When my `player_id` ends with `_10` (RW — Ferran, or Yamal off the bench): stay in the right half-space; if ball comes to my feet, Move inside and Shoot, OR Pass to overlapping `_4` (Llorente).
8. When my `player_id` ends with `_9` (CF — Oyarzabal): drop 8-10m short to receive, lay off to interiors, then run in behind for the cutback.
9. When ball is lost: immediate 6-second counter-press. Nearest 3 players Move toward the carrier; if I am the closest, Tackle.
10. When team_phase is "defending" in mid-block: hold a high line — offside trap is the rule. CBs Move forward in sync the moment opponent plays backward.
11. Shoot from outside the box only if my `player_id` ends with `_10`, `_5`, or `_2` (Yamal/Fabián/Laporte) AND there's a clear lane.
12. When in doubt, Hold and recycle. Tempo is a weapon.

## Key Player Notes
- **Rodri (idx 6)** — captain and the system. Without him, Spain is a different team. Never goes above the halfway line in open play; an alternate penalty taker.
- **Pedri (idx 7)** — best on-ball player; the connector between defense and attack. Free to roam in opponent half.
- **Ferran Torres (idx 10)** — MD1 right-sided starter; orthodox width with a real goal threat (shoot 16), arrives at the back post. Holds the _10 slot while Yamal's minutes are managed.
- **Gavi (idx 8)** — MD1 left-sided starter; relentless energy and pressing (stamina 18), drifts inside to combine rather than hugging the byline. Holds the _8 slot.
- **Yamal (bench, _10 when on)** — primary creator. License to drift centrally and shoot. Set-piece taker. Managing a hamstring: started MD1 on the bench, came on in the second half; Spain's most decisive attacker when fit.
- **Williams (bench, _8 when on)** — Spain's purely vertical, byline-hugging winger (speed 19); benched MD1, enters to provide direct width.
- **Fabián Ruiz (idx 5)** — elegant left-footed #8 who arrives in the box; doubles as Spain's left-side dead-ball deliverer and a genuine long-range threat from the half-space.
- **Oyarzabal (idx 9)** — clinical, selfless #9 and the primary penalty taker (scored the Euro 2024 final winner); links play and finishes the cutbacks.
- **Cubarsí (idx 3)** — composed young ball-playing CB; steps out to break lines and covers the space behind the overlapping Llorente.
- **Cucurella (idx 1)** — sometimes inverts into the DM line when Rodri pushes forward; flexible role.

## Tournament Mindset
Reigning European champions and FIFA No. 2, Spain arrive as one of the heaviest favourites for the trophy. They expect to win the ball and the match — they will play the same way against any opponent. Discipline is in the pattern, not the result. After being held 0-0 by Cape Verde on MD1, the pressure is on to break down a second deep block (Saudi Arabia) — but the identity is unchanged. The open questions are managing Yamal's hamstring (a high-impact sub for now) and the wide-forward rotation; neither alters the system.
