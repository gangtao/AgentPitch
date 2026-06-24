# Argentina — Tactical Profile

## Identity & Philosophy
Reigning World Cup champions (2022) and back-to-back Copa América winners (2021, 2024), Argentina under Lionel Scaloni are the most complete side of their generation: pragmatic but technical, comfortable in possession yet ruthless on the break. Scaloni's philosophy fuses Bielsa-era verticality with Simeone-era ugly defensive grit and a Spanish-style midfield triangle, all built around giving Lionel Messi total freedom in the final third. Argentina come into Matchday 3 having already clinched top spot in Group J: a 3-0 demolition of Algeria on MD1 (Messi hat-trick) was followed by a 2-0 win over Austria on MD2, in which Messi scored twice to become the all-time leading goalscorer in World Cup history. Six points, +5 goal difference, group won with a game to spare — the defending champions are flawless and have nothing left to prove against an already-eliminated Jordan.

## Formation
- Shape: **4-3-3** (morphs to 4-4-2 / 4-2-3-1 out of possession with Messi tucking in)
- Role mapping (roster order in `argentina.yaml`):
  - index 0: GK — **Emiliano Martínez** — elite shot-stopper, vocal organizer, mentality monster on penalties. Sweeper-keeper duties only in mid-block phases; he prefers to stay in the box and dominate aerially.
  - index 1: LB — **Facundo Medina** — a ball-playing centre-back by trade, deputising at left-back with Tagliafico sidelined (calf). Quick, aggressive, progressive passer; tucks inside to form a back three alongside Romero-Lisandro on the build-up. Less natural overlap than Tagliafico but more combative in duels.
  - index 2: LCB — **Cristian Romero** — front-foot, aggressive stepper, will sprint 20 yards to crunch a forward; biggest defensive risk-taker.
  - index 3: RCB — **Lisandro Martínez** — combative, intelligent ball-playing CB; excellent on the left side of a central pair despite compact frame. Strong in the tackle, reads the game, and steps out to intercept. Distributes crisply to Enzo and the fullbacks.
  - index 4: RB — **Gonzalo Montiel** — World Cup final hero, solid and dependable; provides width on the right because Messi tucks inside. Less pace than Molina but better positional discipline and 1v1 defending.
  - index 5: RCM/8 — **Rodrigo De Paul** — Messi's bodyguard, box-to-box engine, all-action presser. Covers the right channel when Montiel bombs on.
  - index 6: DM/6 — **Enzo Fernández** — deep-lying playmaker, the metronome who dictates tempo with long diagonals and split passes.
  - index 7: LCM/8 — **Alexis Mac Allister** — left-sided box-to-box, late runs into the box, second-phase corner threat, alternate set-piece taker.
  - index 8: LW — **Thiago Almada** — creative winger/attacking midfielder; quick feet, incisive dribbler, can play either flank. Preferred over Álvarez and Nico González on the left of the front three; cuts inside to create or drives at the byline. Works harder than most attackers off the ball.
  - index 9: ST — **Lautaro Martínez** — central striker and primary penalty-box presence; strong runner who attacks the channels, holds the ball under pressure, and finishes first time. Near-post aerial target on corners.
  - index 10: RW — **Lionel Messi** — free role from the right; no defensive responsibility, drops between the lines, the team's chief creator and finisher. Five goals in two games (hat-trick vs Algeria MD1, brace vs Austria MD2); now the all-time World Cup top scorer. With the group already won, Scaloni may stagger his minutes, but he remains the focal point whenever on the pitch.

## Style of Play
### Build-up
Patient short build-up from the back: Emi Martínez splits the CBs, Enzo drops between them to form a 3+1, fullbacks push high to give width. With Lisandro Martínez a crisp distributor, progression runs through Enzo dropping deep and the fullbacks stepping up. When pressed hard, Argentina is comfortable going long to Lautaro to win a knock-down for the onrushing De Paul/Mac Allister. Enzo is the deepest playmaker; De Paul connects the lines. Against a deep-sitting Jordan side that will defend in a 4-4-2 low block, expect Argentina to dominate the ball and patiently probe for openings rather than counter.

### Pressing
**Mid-block** primarily, with selective high-press triggers: a back-pass to the opposition GK, or a CB taking a heavy first touch. Lautaro leads the press, curving his run to cut the passing lane to the deeper CB. Messi does NOT press — he hovers between the lines, conserving energy for the transition. De Paul and Mac Allister are the engines who jump into midfield duels.

### Defensive shape
Drops into a **4-4-2** with Messi alongside Lautaro nominally but really walking. Almada tucks in on the left of a midfield four; Mac Allister and De Paul anchor the wider midfield slots with Enzo shielding; the front two stay high to spearhead the counter. CBs hold a high line behind a compact mid-block; offside trap is a weapon.

### Wide play
Asymmetric: **left** = Medina underlap/overlap with Almada cutting inside or driving at the byline, **right** = Montiel overlap + Messi inside. The right side is where the chances are manufactured (Messi-Montiel-De Paul triangle); the left side is where the creativity arrives (Almada's dribbling, Mac Allister late runs).

### Final third
Patterns: Messi-to-Montiel cut-back from the right byline; Messi between the lines slipping Lautaro through the middle; Almada driving inside from the left; Mac Allister's late arrival at the back post; switches of play from Enzo to the left isolating the opposition RB. Argentina is a counter-attack monster — three passes from own half to a shot is a feature, not an accident.

## Set Pieces
- Attacking corners: Messi delivers from the right (in-swinger), Mac Allister from the left (in-swinger). Primary aerial targets: Romero, Lisandro Martínez, Lautaro at the near post.
- Defending corners: **hybrid** — three zonal markers on the six-yard line, four man-markers, two short-corner blockers. Romero attacks the first ball.
- Free kicks: Messi takes direct from any zone within 30 yards. Enzo delivers wide free kicks into the box.
- Penalties: **Messi** primary, **Lautaro** secondary, **Mac Allister** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_10` (RW free role, Messi) and team_phase == "defending":** Hold or slow-walk toward the halfway line — do NOT track back. Conserve stamina.
2. **If my `player_id` ends with `_10` (RW free role, Messi) and I have the ball in the right half-space:** Prefer Pass to a striker running in behind through the middle/left channel (ST `_9` Lautaro / LW `_8` Almada) or to RB `_4` / LB `_1` on the overlap. Shoot only if angle < 25° and distance < 22.
3. **If my `role == "GK"` (player_id `_0`, Emi Martínez) and the ball is in the opposition half:** Sweep up to 25 units out of the box; otherwise stay on the goal line.
4. **If my `player_id` ends with `_3` (RCB, Lisandro Martínez) and team_phase == "attacking" and no opponent within 8 units:** Recycle a safe forward Pass to Enzo or the fullback rather than carrying.
5. **If my `player_id` ends with `_4` (RB, Montiel) and team_phase == "attacking" and the ball is on the left:** Sprint forward to the opposition byline — overlap is automatic.
6. **If my `player_id` ends with `_5` (RCM, De Paul) and the ball-carrier's `player_id` ends with `_10` (Messi):** Position myself 8-12 units behind and to the carrier's right (cover-shadow for the counter-press if `_10` loses it).
7. **If my `role == "FWD"` and Argentina has just lost the ball in the opposition third:** Immediately tackle the nearest opponent within 6 units (5-second counter-press window).
8. **If team_phase == "defending" and my `player_id` ends with `_9` (ST, Lautaro):** Stay high as the right of a front two — do NOT drop into the back four. Hold a position to spearhead the counter and screen the lane to the opposition's deeper CB.
9. **If my `player_id` ends with `_8` (LW, Almada) and team_phase == "attacking" and I have the ball:** Drive inside from the left — dribble past the first man if space, else lay off to Mac Allister `_7` or Enzo `_6`. Cut inside to shoot when within 22 units of goal.
10. **If team is leading by 1+ goals and minute > 75:** Drop deeper, recycle possession, kill the clock. `_5` (De Paul) / `_7` (Mac Allister) hold ball in corner.
11. **If my `role == "MID"` and team_phase == "transition_attack":** Sprint forward — Argentina counters in 3-4 passes. Prefer forward Pass over carry.
12. **Penalties / set-pieces in attacking third within 28 units of goal:** Defer to `_10` (Messi) unless he is off the pitch.

## Key Player Notes
- **Messi (#10):** Free role on the right. No defensive responsibility. Walking is a tactical instruction, not laziness. Every dead ball within 30 yards is his. Five goals in two games (MD1 hat-trick vs Algeria, MD2 brace vs Austria) — now the outright all-time World Cup top scorer, having passed Klose.
- **Almada (#18):** Creative left winger with quick feet and an eye for the final ball. Works harder off the ball than typical attackers; presses from the front and tucks into a midfield four when defending. Preferred over Álvarez in the starting XI.
- **Mac Allister (#20):** License to gamble on the second ball in the box; late runner from deep. Tertiary penalty taker.
- **De Paul (#7):** Messi's bodyguard — instructed to occupy the space Messi vacates and counter-press the moment Messi loses possession.
- **Lisandro Martínez (#25):** Combative ball-playing CB; aggressive in the tackle, reads the game, distributes crisply. Replaced Otamendi as the starting CB partner for Romero.
- **Medina (#17):** Natural CB filling in at LB while Tagliafico recovers from a calf injury. Progressive passer, combative in duels; tucks inside on the build-up.
- **Montiel (#4):** World Cup final hero at RB; solid positionally, better defensive discipline than Molina though less pace. Provides reliable width on the right.
- **Lautaro (#22):** Central striker and chief penalty-box finisher; strong, attacks the channels, holds the ball to bring runners in. Near-post aerial target on corners.

## Tournament Mindset
Defending champions know how to win ugly. Argentina will happily play a tight, low-scoring tournament: keep clean sheets, let Messi produce one moment per game — as he has in both group games so far (five goals in two matches). With Group J already sewn up (6 points, +5, top spot guaranteed), the Jordan match is a dead rubber: Scaloni will prioritise fitness and minutes management heading into the knockout rounds, but the squad's depth means even a rotated XI overwhelms an eliminated opponent. Stamina-managed: Messi at <14 stamina is still better than most teams' best player, but the side is built to protect him — and against Jordan there is every incentive to keep him fresh.
