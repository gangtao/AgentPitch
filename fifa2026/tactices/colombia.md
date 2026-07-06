# Colombia — Tactical Profile

## Identity & Philosophy
Colombia under Néstor Lorenzo is a balanced, possession-comfortable side built around the renaissance of James Rodríguez as a deep-lying #10 and the direct, devastating wing play of Luis Díaz. After a 28-match unbeaten run from 2022 to 2024 (broken by the Copa América 2024 final loss to Argentina), Colombia have established themselves as the second-best CONMEBOL side. Lorenzo's philosophy: defensive solidity first, then unleash James and Díaz on counter-attacks and patient possession sequences. This is a big-tournament team that gets better as the games tighten.

**Group K — won the group on 7 points (+4 GD):** Uzbekistan 3-1 (Muñoz, Díaz, Campaz), DR Congo 1-0 (Muñoz header, 76'), and a controlled 0-0 draw with Portugal that clinched **top spot in Group K**. The blueprint held all group long: a settled **4-2-3-1**, **Gustavo Puerta** alongside Jefferson Lerma in the double pivot (over Richard Ríos), James floating as the 10, Suárez leading the line — two clean sheets in the last two group games exactly to Lorenzo's taste.

**Round of 32 (3 July, vs Ghana — 1-0 win):** A textbook Lorenzo knockout performance. **Jhon Arias** struck early (14') and Colombia game-managed the rest, defending the box and killing Ghana's transitions. Notably, **James Rodríguez was withdrawn at half-time** for a more defensive, game-controlling second-half shape — a reminder that Lorenzo will trade creativity for control once ahead in a knockout. Clean sheet, into the Round of 16.

**Into the Round of 16 (7 July, vs Switzerland — BC Place, Vancouver):** Colombia's XI is **settled and unchanged** — same 4-2-3-1, same Puerta-Lerma pivot, James as the floating 10, Suárez up top. **No injuries or suspensions** for Lorenzo; the one squad blow, Jhon Córdoba's tournament-ending adductor tear, only cements Luis Suárez as the first-choice striker. Expect a cagey, low-block, control-the-game approach against a disciplined Swiss side: deny the transitions, dominate the box aerially, and rely on James and Díaz to settle a tight match. This is precisely the kind of tight, James-decides-it knockout Colombia relish.

## Formation
- Shape: **4-2-3-1** (very stable, with James as the floating 10)
- Role mapping (roster order in `colombia.yaml`):
  - index 0: GK — **Camilo Vargas** — traditional shot-stopper, **not** a sweeper-keeper; stays on his line, dominates the six-yard box.
  - index 1: LB — **Johan Mojica** — pacy, attacking overlapping fullback, the main width-provider on the left because Díaz drifts inside.
  - index 2: LCB — **Davinson Sánchez** — aerial dominator, no-nonsense, stays in shape.
  - index 3: RCB — **Jhon Lucumí** — left-footed, calmer on the ball, the marginal ball-progressor of the pair.
  - index 4: RB — **Daniel Muñoz** — physical, more defensive than Mojica but still overlaps; double-fullback overlap is rare — usually one stays.
  - index 5: DM — **Gustavo Puerta** — physical, mobile ball-winner in the pivot; the energy of the double-six, presses and recovers, keeps it simple in possession (MD1 & MD2 starter over Ríos).
  - index 6: DM — **Jefferson Lerma** — destroyer, the screen, allows Puerta to range and James to roam.
  - index 7: LW — **Luis Díaz** — direct 1v1 winger, the team's chief carrier, drives at the opposition RB.
  - index 8: AM/10 — **James Rodríguez** — the conductor, plays as a deep 10, drifts to the right half-space to combine with Muñoz/Arias; the team's chief creator and dead-ball specialist.
  - index 9: RW — **Jhon Arias** — work-rate, two-way winger, defensive cover for Muñoz, secondary creator.
  - index 10: ST — **Luis Suárez** — mobile, in-form penalty-box finisher (Primeira Liga top scorer); runs the channels, makes diagonal runs behind, and combines quickly rather than holding as a static pivot.

## Style of Play
### Build-up
**Patient short build-up with vertical bursts.** Vargas plays short to Sánchez/Lucumí; Lerma drops between the CBs to form a 3-1 build-up. Mojica pushes high to give width; Muñoz holds slightly deeper. **James drops** from the 10 line into the right half-space to receive between the lines — this is the team's primary progression mechanism. When the press is tight, Colombia goes long for Suárez to chase in behind and plays for the second ball.

### Pressing
**Mid-block to low-block** — Colombia is **not** a high-pressing team. Press triggers: opposition fullback receiving with their back to play, or a misplaced pass into the opposition #6. Suárez leads the press by cover-shadowing the deepest opposition CM. Díaz and Arias jump on the fullbacks. James does NOT press hard — he hovers to receive the recovered ball.

### Defensive shape
Out-of-possession: **4-4-1-1** — Arias drops to RM, Díaz drops to LM (less reliably than Arias), forming a flat midfield four. James floats behind Suárez, neither fully a midfielder nor a forward — he's the outlet for any cleared ball.

### Wide play
**Asymmetric:** Mojica high and wide on the left providing the byline runs; Díaz drifts inside. On the right, Muñoz overlaps less aggressively; Arias works the touchline. Most chances come from the **left** (Mojica-Díaz combination).

### Final third
Patterns: **James cross-field switches** from the right half-space to Díaz on the far touchline. **Mojica byline cutbacks** to James arriving at the penalty spot. **Set-piece deliveries** from James — Colombia's most reliable scoring source. **Suárez channel runs** in behind onto James through-balls and Mojica cutbacks.

## Set Pieces
- Attacking corners: **James** delivers from both sides (in-swingers). Primary aerial targets: Davinson Sánchez, Lucumí; Suárez gambles on the near-post flick and second ball.
- Defending corners: **man-marking** with one zonal post-marker; Sánchez attacks the front ball.
- Free kicks: **James** direct from any zone within 30 yards (left-footed curlers). Mojica delivers wide free kicks from the left.
- Penalties: **James** primary, **Díaz** secondary, **Suárez** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_8` (AM/10, James) and team_phase == "build-up":** Drop deep (between the lines but closer to the 6) to receive from `_2` / `_3` (CBs Sánchez/Lucumí). Face forward before passing.
2. **If my `player_id` ends with `_8` (AM, James) and I receive in the right half-space:** First option = switch (long Pass) to `_7` (LW Díaz) on the far touchline.
3. **If my `player_id` ends with `_7` (LW, Díaz) and I have the ball with an opponent in front:** Attempt to Move (dribble) at the opponent's inside shoulder — cut inside, shoot with the right foot.
4. **If my `player_id` ends with `_1` (LB, Mojica) and team_phase == "attacking":** Sprint to byline, prefer cross/cutback Pass over carry once past the halfway line.
5. **If my `role == "GK"` (player_id `_0`, Vargas):** Stay in box, do NOT sweep aggressively (rare for Colombia).
6. **If my `player_id` ends with `_6` (DM, Lerma):** Sit between the CBs in build-up; never venture past the halfway line. The `_5` player (Puerta) is the one licensed to step forward and screen.
7. **If team_phase == "defending" and my `player_id` ends with `_7` (LW, Díaz):** Drop toward LM but only when LB `_1` (Mojica) is exposed; otherwise stay high as counter-attack outlet.
8. **If team_phase == "defending" and my `player_id` ends with `_9` (RW, Arias):** Always drop to RM, double up on the opposition LW with RB `_4` (Muñoz).
9. **If my `player_id` ends with `_10` (ST, Suárez) and ball is being played long from defense:** Spin in behind the last defender into the channel; prefer a Move (run onto the ball) or quick lay-off Pass to `_8` (James) over a static hold.
10. **If team_phase == "transition_attack":** Look for `_8` (James) first — he's the outlet; if `_8` is marked, `_7` (Díaz) on the left wing.
11. **If team is drawing or leading and minute > 80:** Drop into low block, force opposition into wide areas; rely on `_2` / `_3` (CBs Sánchez/Lucumí) aerial dominance.
12. **Set-piece in attacking third within 35 units of goal:** Defer to `_8` (James) for the delivery.

## Key Player Notes
- **James Rodríguez (10):** The team's heart. Free role between the lines. No defensive duty beyond a token jog. Every set-piece is his.
- **Luis Díaz (7):** Licensed to be the chief 1v1 dribbler. Will attempt to beat his man even when a simpler pass exists.
- **Mojica (17):** Most attacking fullback in CONMEBOL alongside Estupiñán — bombs forward.
- **Gustavo Puerta (6):** The youngest starter and the MD1 & MD2 pivot pick over Ríos. Physical, two-way midfielder who covers ground, wins second balls and keeps possession simple — the legs that let Lerma hold and James float. Ríos is the like-for-like rotation behind him.
- **Lerma (16):** The defensive sentinel — anchors so James can roam.
- **Luis Suárez (25):** In-form penalty-box finisher (Primeira Liga top scorer with Sporting); has displaced Córdoba as the starter. Runs the channels and gambles on the shoulder of the last defender rather than holding play up. Clinical inside the box.

## Tournament Mindset
Colombia are a knockout-round side: they grow into tournaments. Group winners, Ghana dispatched 1-0 in the Round of 32, and now a Round of 16 tie with Switzerland — they arrive playing exactly the low-scoring, defend-the-box, James-and-Díaz-decide-it football they thrive on. Expect a controlled, low-risk performance: sit in a mid-to-low block, deny the Swiss their transitions, dominate set pieces and aerial duels, and back the individual quality of James and Díaz to break a tight game. Lorenzo has already shown (Ghana) he will trade tempo for control once ahead. From the Round of 16 onwards expect James to seize a game and Díaz to break a tight match in transition.
