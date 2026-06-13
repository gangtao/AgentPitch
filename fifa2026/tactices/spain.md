# Spain — Tactical Profile

## Identity & Philosophy
Luis de la Fuente's Spain is the modern heir to tiki-taka, refreshed with vertical wide threats. The midfield (Rodri-Pedri-Fabián) is the team's bloodstream — they dictate tempo, rotate constantly, and starve opponents of the ball. Spain won Euro 2024 with 65% average possession across the tournament, then mixed that with the most direct wingers in world football (Yamal & Williams). Juego de posición with teeth. They arrive in USA/Mexico/Canada as the FIFA No. 2-ranked side, reigning European champions, and a heavy pre-tournament favourite — drawn into Group H with Cape Verde, Uruguay and Saudi Arabia. De la Fuente named a squad with no Real Madrid players (Carvajal, Huijsen omitted) and handed the captaincy to Rodri, his Ballon d'Or-winning pivot. The chief fitness question is Lamine Yamal, managing a hamstring problem: cleared for the group stage but likely rationed rather than 90 minutes early on.

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
  - index 8: LW — Nico Williams (vertical, direct, beats his man wide; speed 19)
  - index 9: CF — Mikel Oyarzabal (link-up #9, drops to combine, holds for runners; clinical finisher, shoot 17)
  - index 10: RW — Lamine Yamal (inverted RW, dribbles inside; primary creator, shoot 17 / dribble 19)

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
- Asymmetric inversion: **LEFT** Williams stays wide and runs to byline → Cucurella underlaps. **RIGHT** Yamal cuts inside onto his left foot → Llorente overlaps to give the wide option.
- Half-space combinations: Yamal-Pedri-Llorente triangle is Spain's most dangerous pattern.

### Final third
- Patience first: ~30-40 passes per chance is not unusual. Wait for the FB overlap or the inside-forward cutback.
- Cutback target: Oyarzabal at the penalty spot, Fabián arriving late from deep.
- Yamal's shot from the right half-space onto his left foot is a recurring termination.

## Set Pieces
- Corners: Inswingers from Yamal on right, Fabián on left. Oyarzabal + Laporte + Cubarsí attack near/back posts. Rodri at edge of box for rebounds.
- Direct FKs: Yamal (right side), Fabián (left), Laporte (central, power).
- Penalties: Oyarzabal is first taker (cool finisher — winner in the Euro 2024 final); Rodri (captain) and Yamal are alternates.
- Defending: zonal with 2 man-markers on biggest threats. Rodri patrols the edge of the box.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only go long if pressed 4v4 and no FB option.
2. When my `player_id` ends with `_6` (DM — Rodri): if no one is open vertically, pass back to CB; never force; my job is to wait — pass 19 means I am the metronome.
3. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Laporte/Cubarsí) and team has ball: pass to the `_6` player (Rodri) first preference, then to the other CB, then to FB. Avoid long balls.
4. When my role is DEF and `player_id` ends with `_1` or `_4` (FB pair) and team_phase is "attacking": advance to LM/RM height; if my `player_id` ends with `_4` (Llorente) and the `_10` player (Yamal) has the ball inside, I overlap; if my `player_id` ends with `_1` (Cucurella) and the `_8` player (Williams) is wide, I underlap into half-space.
5. When my `player_id` ends with `_5` or `_7` (#8 pair — Fabián/Pedri) and team has the ball: position in opposite half-space from the ball; when received, turn forward — never backward (Pedri pass 19, Fabián pass 17).
6. When my `player_id` ends with `_8` (LW — Williams): receive wide on the touchline, take on the LB 1v1 with Move toward + Move diagonal; Shoot only if cutting inside near angle.
7. When my `player_id` ends with `_10` (RW — Yamal): stay narrow in the half-space; if ball comes to my feet, Move inside and Shoot from 20-22m with left foot, OR Pass to overlapping `_4` (Llorente).
8. When my `player_id` ends with `_9` (CF — Oyarzabal): drop 8-10m short to receive, lay off to interiors, then run in behind for the cutback.
9. When ball is lost: immediate 6-second counter-press. Nearest 3 players Move toward the carrier; if I am the closest, Tackle.
10. When team_phase is "defending" in mid-block: hold a high line — offside trap is the rule. CBs Move forward in sync the moment opponent plays backward.
11. Shoot from outside the box only if my `player_id` ends with `_10`, `_5`, or `_2` (Yamal/Fabián/Laporte) AND there's a clear lane.
12. When in doubt, Hold and recycle. Tempo is a weapon.

## Key Player Notes
- **Rodri (idx 6)** — captain and the system. Without him, Spain is a different team. Never goes above the halfway line in open play; an alternate penalty taker.
- **Pedri (idx 7)** — best on-ball player; the connector between defense and attack. Free to roam in opponent half.
- **Yamal (idx 10)** — primary creator. License to drift centrally and shoot. Set-piece taker. Managing a hamstring into the tournament: minutes may be rationed early, but Spain's most decisive attacker when fit.
- **Williams (idx 8)** — Spain's only purely vertical, byline-hugging winger; provides the width Yamal abandons.
- **Fabián Ruiz (idx 5)** — elegant left-footed #8 who arrives in the box; doubles as Spain's left-side dead-ball deliverer and a genuine long-range threat from the half-space.
- **Oyarzabal (idx 9)** — clinical, selfless #9 and the primary penalty taker (scored the Euro 2024 final winner); links play and finishes the cutbacks.
- **Cubarsí (idx 3)** — composed young ball-playing CB; steps out to break lines and covers the space behind the overlapping Llorente.
- **Cucurella (idx 1)** — sometimes inverts into the DM line when Rodri pushes forward; flexible role.

## Tournament Mindset
Reigning European champions and FIFA No. 2, Spain arrive as one of the heaviest favourites for the trophy. They expect to win the ball and the match — they will play the same way against any opponent. Discipline is in the pattern, not the result. The only caveats are managing Yamal's hamstring early in Group H and resolving the rotation in the third-midfield slot; neither changes the identity.
