# Argentina — Tactical Profile

## Identity & Philosophy
Reigning World Cup champions (2022) and back-to-back Copa América winners (2021, 2024), Argentina under Lionel Scaloni are the most complete side of their generation: pragmatic but technical, comfortable in possession yet ruthless on the break. Scaloni's philosophy fuses Bielsa-era verticality with Simeone-era ugly defensive grit and a Spanish-style midfield triangle, all built around giving Lionel Messi total freedom in the final third. Recent results: defending champions arriving with momentum, undefeated in CONMEBOL qualifiers' tougher stretches and confident in tournament football.

## Formation
- Shape: **4-3-3** (morphs to 4-4-2 / 4-2-3-1 out of possession with Messi tucking in)
- Role mapping (roster order in `argentina.yaml`):
  - index 0: GK — **Emiliano Martínez** — elite shot-stopper, vocal organizer, mentality monster on penalties. Sweeper-keeper duties only in mid-block phases; he prefers to stay in the box and dominate aerially.
  - index 1: LB — **Nicolás Tagliafico** — disciplined, tucks inside to form a back three when Tagliafico-Romero-Martínez shape is needed; rarely overlaps deep but joins late.
  - index 2: LCB — **Cristian Romero** — front-foot, aggressive stepper, will sprint 20 yards to crunch a forward; biggest defensive risk-taker.
  - index 3: RCB — **Lisandro Martínez** — left-footed ball-player, the deep playmaker from the back; carries into midfield and switches play diagonally.
  - index 4: RB — **Nahuel Molina** — overlapping fullback, top speed in the back four; provides the width on the right because Messi tucks inside.
  - index 5: RCM/8 — **Rodrigo De Paul** — Messi's bodyguard, box-to-box engine, all-action presser. Covers the right channel when Molina bombs on.
  - index 6: DM/6 — **Enzo Fernández** — deep-lying playmaker, the metronome who dictates tempo with long diagonals and split passes.
  - index 7: LCM/8 — **Alexis Mac Allister** — left-sided box-to-box, late runs into the box, second-phase corner threat, alternate set-piece taker.
  - index 8: LW — **Thiago Almada** — inside-forward, ball-carrier, drifts inside to combine with Mac Allister; gives natural width to Tagliafico's overlap.
  - index 9: ST — **Julián Álvarez** — pressing forward, both 9 and 10 in one body; drops into the half-space when Messi pushes high, runs the channel when Messi gets the ball.
  - index 10: RW — **Lionel Messi** — free role from the right; no defensive responsibility, drops between the lines, the team's chief creator and finisher.

## Style of Play
### Build-up
Patient short build-up from the back: Martínez splits the CBs, Enzo drops between them to form a 3+1, fullbacks push high to give width. Lisandro Martínez is the primary progressor — he steps into midfield with the ball under his foot. When pressed hard, Argentina is comfortable going long to Álvarez to win a knock-down for the onrushing De Paul/Mac Allister. Enzo is the deepest playmaker; De Paul connects the lines.

### Pressing
**Mid-block** primarily, with selective high-press triggers: a back-pass to the opposition GK, or a CB taking a heavy first touch. Álvarez leads the press, curving his run to cut the passing lane to the deeper CB. Messi does NOT press — he hovers between the lines, conserving energy for the transition. De Paul and Mac Allister are the engines who jump into midfield duels.

### Defensive shape
Drops into a **4-4-2** with Messi alongside Álvarez nominally but really walking. Almada drops to LM forming the left bank of four. De Paul and Mac Allister become the wider midfielders in a flat four with Enzo and one of them shielding. CBs hold a high line behind a compact mid-block; offside trap is a weapon.

### Wide play
Asymmetric: **left** = Tagliafico underlap + Almada wide, **right** = Molina overlap + Messi inside. The right side is where the chances are manufactured (Messi-Molina-De Paul triangle); the left side is where the second-phase finishing arrives (Mac Allister late runs).

### Final third
Patterns: Messi-to-Molina cut-back from the right byline; Messi between the lines slipping Álvarez through the middle; Mac Allister's late arrival at the back post; switches of play from Enzo to Almada isolating the opposition RB. Argentina is a counter-attack monster — three passes from own half to a shot is a feature, not an accident.

## Set Pieces
- Attacking corners: Messi delivers from the right (in-swinger), Mac Allister from the left (in-swinger). Primary aerial targets: Romero, Lisandro Martínez, Álvarez at the near post.
- Defending corners: **hybrid** — three zonal markers on the six-yard line, four man-markers, two short-corner blockers. Romero attacks the first ball.
- Free kicks: Messi takes direct from any zone within 30 yards. Enzo delivers wide free kicks into the box.
- Penalties: **Messi** primary, **Álvarez** secondary, **Mac Allister** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_10` (RW free role, Messi) and team_phase == "defending":** Hold or slow-walk toward the halfway line — do NOT track back. Conserve stamina.
2. **If my `player_id` ends with `_10` (RW free role, Messi) and I have the ball in the right half-space:** Prefer Pass to a teammate running in behind on the left (LW `_8` / LB `_1`) or to RB `_4` on the overlap. Shoot only if angle < 25° and distance < 22.
3. **If my `role == "GK"` (player_id `_0`, Emi Martínez) and the ball is in the opposition half:** Sweep up to 25 units out of the box; otherwise stay on the goal line.
4. **If my `player_id` ends with `_3` (LCB, Lisandro Martínez) and team_phase == "attacking" and no opponent within 8 units:** Move forward with the ball into midfield (carry, not pass).
5. **If my `player_id` ends with `_4` (RB, Molina) and team_phase == "attacking" and the ball is on the left:** Sprint forward to the opposition byline — overlap is automatic.
6. **If my `player_id` ends with `_5` (RCM, De Paul) and the ball-carrier's `player_id` ends with `_10` (Messi):** Position myself 8-12 units behind and to the carrier's right (cover-shadow for the counter-press if `_10` loses it).
7. **If my `role == "FWD"` and Argentina has just lost the ball in the opposition third:** Immediately tackle the nearest opponent within 6 units (5-second counter-press window).
8. **If team_phase == "defending" and my `player_id` ends with `_8` (LW, Almada):** Drop to LM position, stay within 5 units of LB `_1` (Tagliafico).
9. **If my `player_id` ends with `_9` (ST, Álvarez) and a Brazilian/Uruguayan CB takes a heavy first touch (ball > 3 units from their feet):** Sprint to press.
10. **If team is leading by 1+ goals and minute > 75:** Drop deeper, recycle possession, kill the clock. `_5` (De Paul) / `_7` (Mac Allister) hold ball in corner.
11. **If my `role == "MID"` and team_phase == "transition_attack":** Sprint forward — Argentina counters in 3-4 passes. Prefer forward Pass over carry.
12. **Penalties / set-pieces in attacking third within 28 units of goal:** Defer to `_10` (Messi) unless he is off the pitch.

## Key Player Notes
- **Messi (10):** Free role on the right. No defensive responsibility. Walking is a tactical instruction, not laziness. Every dead ball within 30 yards is his.
- **Mac Allister (7):** License to gamble on the second ball in the box; late runner from deep. Tertiary penalty taker.
- **De Paul (5):** Messi's bodyguard — instructed to occupy the space Messi vacates and counter-press the moment Messi loses possession.
- **Lisandro Martínez (3):** Licensed to step into midfield with the ball; treated as a third midfielder in build-up.
- **Álvarez (9):** Free to drop into the 10 when Messi pushes up the channel; effectively a fluid front three with Almada.

## Tournament Mindset
Defending champions know how to win ugly. Argentina will happily play a tight, low-scoring tournament: keep clean sheets, let Messi-Álvarez-Mac Allister produce one moment per game. Stamina-managed: Messi at <14 stamina is still better than most teams' best player, but the side is built to protect him.
