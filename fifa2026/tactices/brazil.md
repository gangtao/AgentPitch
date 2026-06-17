# Brazil — Tactical Profile

## Identity & Philosophy
Brazil under Carlo Ancelotti is a study in contradiction: the Italian's pragmatic, possession-with-control philosophy bolted onto the most flamboyant attacking talent pool on Earth. Ancelotti has settled on a **4-2-3-1** — a Casemiro/Bruno Guimarães double pivot screening the back four, a free No. 10 (Lucas Paquetá) behind a lone striker, and the front line's flair carried wide by Vinícius and Raphinha. He has tightened the defensive structure and demanded the wingers contribute more out of possession. Neymar (#10) was named in the 26 at age 34 but is recovering from a grade-two calf tear and is not available. The Matchday-1 opener was a frustrating **1-1 draw with Morocco** (Vinícius equalised on 32'); Ancelotti was unhappy with the performance level — Casemiro struggled, and the surprise striker pick **Igor Thiago endured a poor outing (subbed ~62')**, sparking calls for Endrick and a likely return to **Matheus Cunha** through the middle. Ancelotti arrives at a World Cup for the first time as a national-team manager with a mandate to restore Brazilian dignity after the 2022 quarter-final exit.

## Formation
- Shape: **4-2-3-1** (double pivot; Vinícius and Raphinha tuck inside, fullbacks provide measured width)
- Role mapping (roster order in `brazil.yaml`):
  - index 0: GK — **Alisson Becker** — elite **sweeper-keeper**, world-class with the ball at his feet, regularly plays 30-yard line-breaking passes.
  - index 1: LB — **Alex Sandro** — experienced overlapping/inverting fullback, comfortable tucking into midfield as a third pivot (back in for the Matchday-1 rotation of Douglas Santos).
  - index 2: LCB — **Gabriel Magalhães** — left-footed, physical, aerial dominator, primary aggressive defender of the pair.
  - index 3: RCB — **Marquinhos** — captain, ball-playing libero, the calmest passer in the back line; steps into midfield with possession.
  - index 4: RB — **Danilo** — veteran positional fullback (back in for the Matchday-1 rotation of Roger Ibañez); tucks inside, reads danger, picks his overlaps sparingly.
  - index 5: LDM — **Casemiro** — destroyer, sits in front of the back four, ball-winner; half of the double pivot, shields the central channel.
  - index 6: RDM — **Bruno Guimarães** — deep-lying playmaker, the metronome; the most progressive of the pivot pair, switches play with diagonal passes.
  - index 7: CAM — **Lucas Paquetá** — the free No. 10; half-space dribbler and late box-arriver; the creative connector between the pivot and the front line.
  - index 8: LW — **Vinícius Júnior** — direct 1v1 dribbler, the team's pace and chaos; gets the ball wide left and goes at the right-back.
  - index 9: ST — **Matheus Cunha** — mobile lone striker, drops between the lines, links play, makes diagonal runs in behind (preferred over Igor Thiago after the Morocco game).
  - index 10: RW — **Raphinha** — inverted right winger who drifts inside to combine, primary set-piece and penalty taker, relentless work rate.

## Style of Play
### Build-up
**Patient short build-up.** Alisson plays out from the back as a rule. Marquinhos and Gabriel split wide; Casemiro or Bruno drops between them when needed to make a 3-2. Fullbacks (especially Alex Sandro) often invert to support the double pivot. The team is built to get **Bruno Guimarães** on the ball facing forward. Brazil will pass 5-7 times in their own half to draw the press before going long.

### Pressing
**Mid-block default, with selective high-press triggers.** Press triggers: opposition GK passing to a CB with a teammate within 5 yards (jump the angle), CB receiving with back to play. Vinícius will press the opposition RB; Raphinha presses the LB. **Matheus Cunha curves his run** to press the deeper CB; **Paquetá jumps the opposition pivot**. Casemiro is the man behind, intercepting any vertical pass through the middle.

### Defensive shape
Out-of-possession: **4-4-2 mid-block** — Paquetá pushes up alongside Matheus Cunha, the pivot (Casemiro, Bruno) screens, and Vinícius drops to LM (a key Ancelotti demand) with Raphinha at RM. Compact between the lines; Brazil concedes the wide channels to deny central penetration.

### Wide play
**Asymmetric:** Vinícius wide-and-high on the left, Alex Sandro inverts or underlaps. Raphinha drifts inside on the right while Danilo stays home and tucks in to form a back three — right-side width comes from Raphinha holding the touchline early or Bruno's underlapping runs. This creates a lopsided shape: wide-left, narrow-right.

### Final third
Patterns: **Vinícius isolation** in the left half-space — get him 1v1 vs the RB, no help, let him cook. **Raphinha-Bruno combinations** down the right — give-and-go around the fullback with Bruno underlapping. **Paquetá between the lines** finding Matheus Cunha's diagonal run in behind. **Cutbacks** from the byline to the penalty spot for an arriving Paquetá or Bruno. Set-piece delivery from Raphinha is a major weapon.

## Set Pieces
- Attacking corners: **Raphinha** delivers from the right (in-swinger), **Bruno Guimarães** from the left (in-swinger); **Vinícius** an alternate. Primary aerial targets: Marquinhos, Gabriel Magalhães at near/back post.
- Defending corners: **zonal** — six players on the six-yard line, two near-post blockers, two short-corner watchers, Alisson dominant in the air.
- Free kicks: **Raphinha** direct from the right side, **Lucas Paquetá** and **Bruno Guimarães** from central positions, **Danilo** an option.
- Penalties: **Raphinha** primary (confirmed first taker), **Lucas Paquetá** secondary, **Vinícius** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_8` (LW, Vinícius) and I have the ball in the left third with an opponent within 5 units:** Attempt a Move (dribble) at the opponent's outside shoulder — accept loss of possession as a cost.
2. **If my `role == "GK"` (player_id `_0`, Alisson) and pressed by 1 forward:** Play short to the nearest CB. **If pressed by 2 forwards:** play long-diagonal to LW `_8` (Vinícius) on the left wing.
3. **If my `player_id` ends with `_3` (RCB, Marquinhos) and team_phase == "attacking" and no opponent within 10 units:** Carry the ball into midfield (treat as an extra midfielder in possession).
4. **If my `player_id` ends with `_4` (RB, Danilo) and team_phase == "attacking":** Hold a conservative line — tuck inside to form a back three; only overlap when `_10` (Raphinha) has drifted inside AND the ball is in the right third.
5. **If my `player_id` ends with `_1` (LB, Alex Sandro) and team_phase == "attacking":** Invert into the half-space alongside the pivot — support the 3-2 build-up. Do NOT overlap LW `_8` (Vinícius) unless he checks back inside.
6. **If my `player_id` ends with `_5` (DM, Casemiro):** Stay as the deepest screen; never go beyond halfway in open play. Win the ball, give it simple to `_6` (Bruno).
7. **If my `role == "MID"` and the carrier's `player_id` is not `_6` (Bruno Guimarães):** Move to give `_6` a passing option in space — he is the chief progressor.
8. **If my `player_id` ends with `_7` (CAM, Paquetá) and team has the ball:** Position between the opposition lines; when received, turn forward and either thread `_9` (Cunha)'s run or carry into the box. Late arrival into the box for cutbacks.
9. **If my `player_id` ends with `_9` (ST, Matheus Cunha) and team_phase == "attacking":** Drop short to link when `_7` (Paquetá) is deep; make a diagonal run in behind when `_6` (Bruno) or `_7` receives facing forward.
10. **If team_phase == "defending" and my `player_id` ends with `_8` (LW, Vinícius):** Drop to LM, track the opposition overlapping runner on my flank.
11. **If team_phase == "transition_defense" (just lost the ball):** All MIDs and FWDs counter-press within a 6-unit radius for 4 seconds; if no recovery, drop into 4-4-2 shape.
12. **If my `role == "FWD"` or `role == "MID"` and I'm carrying the ball and a teammate is in space inside the opposition box:** Always prefer Pass over Shoot (Brazil is built on combination play, not long-shot speculation).
13. **If team is leading by 2+ goals:** Keep possession, do NOT counter-attack at speed. Recycle through `_6` (Bruno) and `_5` (Casemiro).
14. **Penalty assignment:** Defer to `_10` (Raphinha) first; if he is fatigued (`stamina < 10`), `_7` (Paquetá), then `_8` (Vinícius).

## Key Player Notes
- **Vinícius (7, idx 8):** No defensive tracking duty beyond LM line. Free to isolate vs RB. Always 1v1 the first defender. Brazil's matchwinner — scored the Morocco equaliser.
- **Raphinha (11, idx 10):** Confirmed primary penalty and set-piece taker; led Brazil in qualifying scoring. Inverted RW who delivers and combines.
- **Marquinhos (4, idx 3):** Captain. Licensed to step into midfield with the ball; the team's best passer between the lines from deep.
- **Bruno Guimarães (8, idx 6):** The progressive half of the pivot; the chief switch-of-play passer and metronome.
- **Casemiro (5, idx 5):** The anchor and ball-winner; struggled vs Morocco and under rotation pressure (Fabinho an alternate), but the established screen in front of the back four.
- **Matheus Cunha (9, idx 9):** Mobile lone striker preferred after Igor Thiago's poor Morocco display; links play and finishes the cutbacks. Endrick is the impact-sub option (won a penalty and assisted off the bench).
- **Alisson (1, idx 0):** Sweeper-keeper extreme — line as high as 18-20 units from goal when Brazil have the ball.

## Tournament Mindset
Pressure-tournament team carrying decades of expectation. After a flat 1-1 with Morocco that drew Ancelotti's ire, Brazil face Haiti (Matchday 2, June 19, Philadelphia) needing a convincing, controlled win to settle the group. Ancelotti's Brazil will be more measured than the Tite-era cavaliers, prepared to grind. But when Vinícius gets isolated against a tired fullback in the second half, the game can break open in 60 seconds.
