# Spain — Tactical Profile

## Identity & Philosophy
Luis de la Fuente's Spain is the modern heir to tiki-taka, refreshed with vertical wide threats. The midfield (Rodri-Pedri-Fabián) is the team's bloodstream — they dictate tempo, rotate constantly, and starve opponents of the ball. Spain won Euro 2024 with 65% average possession across the tournament, then mixed that with the most direct wingers in world football (Yamal & Williams). Juego de posición with teeth.

## Formation
- Shape: 4-3-3 with a single pivot (Rodri); FBs ultra-high in possession (effectively 2-3-5)
- Role mapping (roster order in `spain.yaml`):
  - index 0: GK — Unai Simón (ball-playing keeper, build-up partner)
  - index 1: LB — Marc Cucurella (overlapping, sometimes inverts; left side overload)
  - index 2: LCB — Robin Le Normand (physical CB, aerial)
  - index 3: RCB — Aymeric Laporte (ball-progressor; passes ~17 — the deeper playmaker of the pair)
  - index 4: RB — Dani Carvajal (overlaps when Yamal cuts in)
  - index 5: LCM/#8 — Fabián Ruiz (left-side interior; arrives in box late, half-space passer)
  - index 6: DM/#6 — Rodri (the irreplaceable pivot — pass 19, skill 18 — sets every tempo)
  - index 7: RCM/#8 — Pedri (right-side interior; receives between lines, the best on-ball link)
  - index 8: LW — Nico Williams (vertical, direct, beats his man wide; speed 19)
  - index 9: CF — Álvaro Morata (link-up #9, drops to combine, holds for runners)
  - index 10: RW — Lamine Yamal (inverted RW, dribbles inside; primary creator, shoot 17 / dribble 19)

## Style of Play

### Build-up
- From Unai Simón: short to Le Normand or Laporte every time. Goal-kick to row 1 unless pressed 4v4 high.
- Rodri drops between CBs only when needed (3-2-5 vs high press); otherwise stays as pivot.
- Both FBs step into midfield height; Pedri and Fabián float between lines.
- **Possession target ~65%**. Spain accepts U-shape passing (CB-DM-CB-DM) to wait for a vertical lane.

### Pressing
- Counter-press (Cruyff/Guardiola school): the moment Spain loses it, the nearest 3 players collapse on the carrier for 6 seconds. If not won back, drop to mid-block.
- Trigger high press: opponent CB receives with back to play, OR a square pass between CBs is in flight.
- Morata leads, Yamal & Williams curve runs to lock the FBs. Pedri/Fabián jump #6.

### Defensive shape
- 4-1-4-1 with Rodri shielding. High line (offside trap) — line ~ 50% of pitch length.
- Fabián and Pedri have moderate defensive responsibility; tracking back is shared by the wingers.
- Vulnerable to direct balls in behind — Spain accepts the risk for compression.

### Wide play
- Asymmetric inversion: **LEFT** Williams stays wide and runs to byline → Cucurella underlaps. **RIGHT** Yamal cuts inside onto his left foot → Carvajal overlaps to give the wide option.
- Half-space combinations: Yamal-Pedri-Carvajal triangle is Spain's most dangerous pattern.

### Final third
- Patience first: ~30-40 passes per chance is not unusual. Wait for the FB overlap or the inside-forward cutback.
- Cutback target: Morata at the penalty spot, Fabián arriving late from deep.
- Yamal's shot from the right half-space onto his left foot is a recurring termination.

## Set Pieces
- Corners: Inswingers from Yamal on right, Fabián on left. Morata + Le Normand + Laporte attack near/back posts. Rodri at edge of box for rebounds.
- Direct FKs: Yamal (right side), Fabián (left), Laporte (central, power).
- Defending: zonal with 2 man-markers on biggest threats. Rodri patrols the edge of the box.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only go long if pressed 4v4 and no FB option.
2. When my `player_id` ends with `_6` (DM — Rodri): if no one is open vertically, pass back to CB; never force; my job is to wait — pass 19 means I am the metronome.
3. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Le Normand/Laporte) and team has ball: pass to the `_6` player (Rodri) first preference, then to the other CB, then to FB. Avoid long balls.
4. When my role is DEF and `player_id` ends with `_1` or `_4` (FB pair) and team_phase is "attacking": advance to LM/RM height; if my `player_id` ends with `_4` (Carvajal) and the `_10` player (Yamal) has the ball inside, I overlap; if my `player_id` ends with `_1` (Cucurella) and the `_8` player (Williams) is wide, I underlap into half-space.
5. When my `player_id` ends with `_5` or `_7` (#8 pair — Fabián/Pedri) and team has the ball: position in opposite half-space from the ball; when received, turn forward — never backward — pass 19.
6. When my `player_id` ends with `_8` (LW — Williams): receive wide on the touchline, take on the LB 1v1 with Move toward + Move diagonal; Shoot only if cutting inside near angle.
7. When my `player_id` ends with `_10` (RW — Yamal): stay narrow in the half-space; if ball comes to my feet, Move inside and Shoot from 20-22m with left foot, OR Pass to overlapping `_4` (Carvajal).
8. When my `player_id` ends with `_9` (CF — Morata): drop 8-10m short to receive, lay off to interiors, then run in behind for the cutback.
9. When ball is lost: immediate 6-second counter-press. Nearest 3 players Move toward the carrier; if I am the closest, Tackle.
10. When team_phase is "defending" in mid-block: hold a high line — offside trap is the rule. CBs Move forward in sync the moment opponent plays backward.
11. Shoot from outside the box only if my `player_id` ends with `_10`, `_5`, or `_3` (Yamal/Fabián/Laporte) AND there's a clear lane.
12. When in doubt, Hold and recycle. Tempo is a weapon.

## Key Player Notes
- **Rodri (idx 6)** — the system. Without him, Spain is a different team. Never goes above the halfway line in open play.
- **Pedri (idx 7)** — best on-ball player; the connector between defense and attack. Free to roam in opponent half.
- **Yamal (idx 10)** — primary creator. License to drift centrally and shoot. Set-piece taker.
- **Williams (idx 8)** — Spain's only purely vertical, byline-hugging winger; provides the width Yamal abandons.
- **Cucurella (idx 1)** — sometimes inverts into the DM line when Rodri pushes forward; flexible role.

## Tournament Mindset
Spain expect to win the ball and the match — they will play the same way against any opponent. Discipline is in the pattern, not the result.
