# Argentina — Tactical Profile

## Identity & Philosophy
Reigning World Cup champions (2022) and back-to-back Copa América winners (2021, 2024), Argentina under Lionel Scaloni are the most complete side of their generation: pragmatic but technical, comfortable in possession yet ruthless on the break. Scaloni's philosophy fuses Bielsa-era verticality with Simeone-era ugly defensive grit and a Spanish-style midfield triangle, all built around giving Lionel Messi total freedom in the final third. Argentina cruised through Group J as winners — six points early, group sewn up with a game to spare, Messi already the all-time World Cup top scorer — and now enter the single-elimination phase. **Round of 16 vs Egypt, 7 July 2026, Mercedes-Benz Stadium, Atlanta.** Win or go home: the defending champions are heavy favourites but face a disciplined Egypt side whose one world-class weapon, Mohamed Salah, makes this a game to be respected rather than assumed.

## Formation
- Shape: **4-3-3** (morphs to 4-4-2 / 4-2-3-1 out of possession with Messi tucking in)
- Role mapping (roster order in `argentina.yaml`):
  - index 0: GK — **Emiliano Martínez** (#23) — elite shot-stopper, vocal organizer, mentality monster on penalties. Sweeper-keeper duties only in mid-block phases; he prefers to stay in the box and dominate aerially. In a knockout tie he is the ultimate shootout insurance.
  - index 1: LB — **Facundo Medina** (#25) — a ball-playing centre-back by trade, deputising at left-back with Tagliafico sidelined (calf). Quick, aggressive, progressive passer; tucks inside to form a back three alongside Romero-Lisandro on the build-up. Must stay disciplined defensively — his flank is the one Salah attacks.
  - index 2: LCB — **Cristian Romero** (#13) — front-foot, aggressive stepper, will sprint 20 yards to crunch a forward; biggest defensive risk-taker.
  - index 3: RCB — **Lisandro Martínez** (#6) — combative, intelligent ball-playing CB; excellent on the left side of a central pair despite compact frame. Strong in the tackle, reads the game, and steps out to intercept. Distributes crisply to Enzo and the fullbacks.
  - index 4: RB — **Gonzalo Montiel** (#4) — World Cup final hero, solid and dependable; provides width on the right because Messi tucks inside. Less pace than Molina but better positional discipline and 1v1 defending.
  - index 5: RCM/8 — **Rodrigo De Paul** (#7) — Messi's bodyguard, box-to-box engine, all-action presser. Covers the right channel when Montiel bombs on.
  - index 6: DM/6 — **Enzo Fernández** (#24) — deep-lying playmaker, the metronome who dictates tempo with long diagonals and split passes; the deepest screener in front of the back four, key to smothering Egypt's transitions.
  - index 7: LCM/8 — **Alexis Mac Allister** (#20) — left-sided box-to-box, late runs into the box, second-phase corner threat, alternate set-piece taker.
  - index 8: LW — **Thiago Almada** (#16) — creative winger/attacking midfielder; quick feet, incisive dribbler, can play either flank. Preferred over Álvarez and Nico González on the left of the front three; cuts inside to create or drives at the byline. Works harder than most attackers off the ball — vital, because his tracking helps double up on Salah.
  - index 9: ST — **Lautaro Martínez** (#22) — central striker and primary penalty-box presence; strong runner who attacks the channels, holds the ball under pressure, and finishes first time. Near-post aerial target on corners.
  - index 10: RW — **Lionel Messi** (#10) — free role from the right; no defensive responsibility, drops between the lines, the team's chief creator and finisher. Now the all-time World Cup top scorer. At 39 his minutes are managed, but he remains the focal point and the man Argentina turn to for the decisive moment in a tight knockout.

## Style of Play
### Build-up
Patient short build-up from the back: Emi Martínez splits the CBs, Enzo drops between them to form a 3+1, fullbacks push high to give width. With Lisandro Martínez a crisp distributor, progression runs through Enzo dropping deep and the fullbacks stepping up. When pressed, Argentina is comfortable going long to Lautaro to win a knock-down for the onrushing De Paul/Mac Allister. Against an Egypt side that will sit in a compact 4-2-3-1 and defend deep, expect Argentina to dominate the ball and patiently probe for openings — with the explicit caveat that turnovers must not spring Salah and Marmoush into space.

### Pressing
**Mid-block** primarily, with selective high-press triggers: a back-pass to the opposition GK, or a CB taking a heavy first touch. Lautaro leads the press, curving his run to cut the passing lane to the deeper CB. Messi does NOT press — he hovers between the lines, conserving energy for the transition. De Paul and Mac Allister are the engines who jump into midfield duels. Discipline in rest-defence is paramount: leave two men (Enzo + a CB) anchored at all times so a lost ball cannot be turned into a 3-on-3 the other way.

### Defensive shape
Drops into a **4-4-2** with Messi alongside Lautaro nominally but really walking. Almada tucks in on the left of a midfield four; Mac Allister and De Paul anchor the wider midfield slots with Enzo shielding; the front two stay high to spearhead the counter. CBs hold a high line behind a compact mid-block; offside trap is a weapon — but the line drops a fraction deeper than usual against Marmoush's pace. **Salah watch:** Egypt's #10 drifts to Argentina's left; Medina and Almada double up, and De Paul/Enzo shade across to screen the inside lane whenever the ball travels to that flank.

### Wide play
Asymmetric: **left** = Medina underlap/overlap with Almada cutting inside or driving at the byline, **right** = Montiel overlap + Messi inside. The right side is where the chances are manufactured (Messi-Montiel-De Paul triangle); the left side is where the creativity arrives (Almada's dribbling, Mac Allister late runs). Against Egypt, the left flank carries defensive priority (Salah) so Medina overlaps more selectively.

### Final third
Patterns: Messi-to-Montiel cut-back from the right byline; Messi between the lines slipping Lautaro through the middle; Almada driving inside from the left; Mac Allister's late arrival at the back post; switches of play from Enzo to isolate a full-back. Against a low block, patience plus one flash of Messi quality is the template; Argentina remains a counter-attack monster if Egypt over-commits chasing a goal.

## Set Pieces
- Attacking corners: Messi delivers from the right (in-swinger), Mac Allister from the left (in-swinger). Primary aerial targets: Romero, Lisandro Martínez, Lautaro at the near post.
- Defending corners: **hybrid** — three zonal markers on the six-yard line, four man-markers, two short-corner blockers. Romero attacks the first ball. Keep a fast man high (Lautaro/Almada) as a counter outlet against Egypt's set-piece commitment.
- Free kicks: Messi takes direct from any zone within 30 yards. Enzo delivers wide free kicks into the box.
- Penalties: **Messi** primary, **Lautaro** secondary, **Mac Allister** tertiary. In a shootout, Emi Martínez (#23) is Argentina's decisive edge.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_10` (RW free role, Messi) and team_phase == "defending":** Hold or slow-walk toward the halfway line — do NOT track back. Conserve stamina.
2. **If my `player_id` ends with `_10` (RW free role, Messi) and I have the ball in the right half-space:** Prefer Pass to a striker running in behind through the middle/left channel (ST `_9` Lautaro / LW `_8` Almada) or to RB `_4` / LB `_1` on the overlap. Shoot only if angle < 25° and distance < 22.
3. **If my `role == "GK"` (player_id `_0`, Emi Martínez) and the ball is in the opposition half:** Sweep up to 25 units out of the box; otherwise stay on the goal line. Against a counter-heavy Egypt, err toward staying home unless the sweep is certain.
4. **If my `player_id` ends with `_3` (RCB, Lisandro Martínez) and team_phase == "attacking" and no opponent within 8 units:** Recycle a safe forward Pass to Enzo or the fullback rather than carrying.
5. **If my `player_id` ends with `_4` (RB, Montiel) and team_phase == "attacking" and the ball is on the left:** Sprint forward to the opposition byline — overlap is automatic.
6. **If my `player_id` ends with `_5` (RCM, De Paul) and the ball-carrier's `player_id` ends with `_10` (Messi):** Position myself 8-12 units behind and to the carrier's right (cover-shadow for the counter-press if `_10` loses it).
7. **If my `role == "FWD"` and Argentina has just lost the ball in the opposition third:** Immediately tackle the nearest opponent within 6 units (5-second counter-press window) — deny Egypt the first pass of the counter.
8. **If team_phase == "defending" and my `player_id` ends with `_9` (ST, Lautaro):** Stay high as the right of a front two — do NOT drop into the back four. Hold a position to spearhead the counter and screen the lane to the opposition's deeper CB.
9. **If my `player_id` ends with `_8` (LW, Almada) and team_phase == "attacking" and I have the ball:** Drive inside from the left — dribble past the first man if space, else lay off to Mac Allister `_7` or Enzo `_6`. Cut inside to shoot when within 22 units of goal. **When defending, tuck in and help LB `_1` double Salah.**
10. **If team is leading by 1+ goals and minute > 75:** Drop deeper, recycle possession, kill the clock. `_5` (De Paul) / `_7` (Mac Allister) hold ball in corner.
11. **If my `role == "MID"` and team_phase == "transition_attack":** Sprint forward — Argentina counters in 3-4 passes. Prefer forward Pass over carry.
12. **Penalties / set-pieces in attacking third within 28 units of goal:** Defer to `_10` (Messi) unless he is off the pitch.

## Key Player Notes
- **Messi (#10):** Free role on the right. No defensive responsibility. Walking is a tactical instruction, not laziness. Every dead ball within 30 yards is his. All-time World Cup top scorer — in a knockout, Argentina engineer the game to give him one clean look.
- **Almada (#16):** Creative left winger with quick feet and an eye for the final ball. Works harder off the ball than typical attackers; presses from the front and tucks into a midfield four to help contain Salah. Preferred over Álvarez in the starting XI.
- **Mac Allister (#20):** License to gamble on the second ball in the box; late runner from deep. Tertiary penalty taker.
- **De Paul (#7):** Messi's bodyguard — instructed to occupy the space Messi vacates and counter-press the moment Messi loses possession. Fitness monitored after the group stage but starts.
- **Lisandro Martínez (#6):** Combative ball-playing CB; aggressive in the tackle, reads the game, distributes crisply. Starting CB partner for Romero.
- **Medina (#25):** Natural CB filling in at LB while Tagliafico recovers from a calf injury. Progressive passer, combative in duels; tucks inside on the build-up. Primary responsibility this tie: contain Salah on Argentina's left.
- **Montiel (#4):** World Cup final hero at RB; solid positionally, better defensive discipline than Molina though less pace. Provides reliable width on the right.
- **Lautaro (#22):** Central striker and chief penalty-box finisher; strong, attacks the channels, holds the ball to bring runners in. Near-post aerial target on corners. Secondary penalty taker.
- **Emi Martínez (#23):** Elite shot-stopper and Argentina's ace in the hole should the tie reach a shootout — a genuine psychological edge from twelve yards.

## Tournament Mindset
Knockout football, win or go home. Defending champions know how to win ugly, and that is exactly the plan against Egypt: control the ball, smother the counter, keep Salah quiet, and let Messi conjure the decisive moment. Egypt will defend deep in a 4-2-3-1 and live for transitions through Salah (tournament-leading chance creator) and Marmoush's pace — so rest-defence discipline outweighs adventurous overlaps, and the offside line is calibrated to Marmoush rather than the ball. Argentina will happily take a tight, low-scoring win. If it goes the distance, extra time and penalties favour the champions: Messi, Lautaro and Mac Allister on the spot, and Emiliano Martínez in goal. Stamina-managed: Messi and De Paul are monitored, but the side is built to protect Messi and finish the job.
