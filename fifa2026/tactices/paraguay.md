# Paraguay — Tactical Profile

## Identity & Philosophy
Paraguay under **Gustavo Alfaro** are the tournament's archetypal pragmatists: a compact, disciplined, hard-running **4-4-2** built around captain **Gustavo Gómez** at the back and the breakaway threat of **Miguel Almirón**. Alfaro — the man who took Ecuador to the 2022 World Cup — rebuilt a moribund Paraguay into qualifiers by demanding two banks of four out of possession, ferocious defensive transitions, and a willingness to sit deep and strike on the counter. They are not a possession side; they are a "win the moment" side, content with 35% of the ball if it means springing Almirón and the front runners into space against an exposed back line.

The group stage was a survival story. **Matchday 1 was a 4-1 hammering by hosts USA** (June 12), where an early own goal and a Balogun brace buried them before half-time and Maurício pulled one back for scant consolation. They answered with grit on **Matchday 2: a 1-0 win over Türkiye** (June 19), withstanding a barrage (Türkiye registered 30+ shots) and winning through an early **Matías Galarza strike (2')** and a clinical, smash-and-grab defensive shift — the very definition of Alfaro-ball. They then ground out a **0-0 draw with Australia** (June 25) to finish **third in Group D on 4 points**, sneaking into the Round of 32 as one of the best third-placed sides.

Now comes the reward and the reckoning: **the Round of 32 against Germany** (June 29, Gillette Stadium, Foxborough). Paraguay are the heavy underdog against Julian Nagelsmann's side, and the matchup could not suit Alfaro better — a low-event, defend-deep, counter-and-set-piece game where one moment of Enciso quality or a Gómez header can stun a favourite. This is exactly the kind of knockout knife-fight Paraguay were built for.

## Formation
- Shape: **4-4-2** (two compact banks of four; fullbacks tuck in, the two strikers split to press and to attack the channels; Almirón drifts inside off the left into a free No. 10 space when Paraguay have the ball)
- Role mapping (roster order in `paraguay.yaml`):
  - index 0: GK — **Orlando Gill** — composed shot-stopper, reliable rather than flashy; distributes long to relieve pressure rather than playing risky short build-up.
  - index 1: LB — **Júnior Alonso** — left-footed, aggressive, strong in the duel; defends first, overlaps Almirón only when the situation is safe.
  - index 2: LCB — **Omar Alderete** — left-footed, athletic, front-foot defender; steps out to break up play and is comfortable carrying into midfield. (Carried a knee knock from the group stage but expected to start; Gustavo Velázquez of Cerro Porteño is the cover.)
  - index 3: RCB — **Gustavo Gómez** — **captain**, 33, the heart of the side; aerially dominant, aggressive timing, organises the block and is a genuine set-piece threat at the other end.
  - index 4: RB — **Juan José Cáceres** — energetic, tucks in to form a back three in build-up, picks his overlaps down the right.
  - index 5: LM — **Miguel Almirón** — the face of the team, back from a one-match suspension; relentless runner who drifts inside from the left into the 10 space, links play, presses from the front, and is the chief outlet in transition.
  - index 6: LCM — **Andrés Cubas** — the destroyer and screen; sits deepest of the midfield, breaks up play, recycles simply. The anchor in front of the back four.
  - index 7: RCM — **Matías Galarza** — disciplined, two-way central midfielder and the man who struck the winner vs Türkiye; shuttles, screens, and steps into the line-breaking pass. Diego Gómez's replacement in the engine room.
  - index 8: RM — **Maurício** — Palmeiras' technical, two-footed midfielder (scorer vs USA); carries in transition, provides delivery from the right, and arrives late in the box. Paraguay's secondary creative spark.
  - index 9: ST — **Julio Enciso** — 22, the talent; a dribbling, shoot-on-sight forward who drops to combine and drives at defenders. The primary penalty and free-kick threat, especially with Diego Gómez suspended.
  - index 10: ST — **Gabriel Ávalos** — experienced focal-point striker; holds the ball up, occupies the centre-backs, and finishes the chances the counter creates. The reference No. 9.

## Style of Play
### Build-up
**Direct and risk-averse.** Gill prefers to go long rather than play through a press. When Paraguay do build short, the fullbacks tuck in and one of Cubas/Alderete drops to make a back three; the aim is to get the ball forward to Ávalos's hold-up or into the channels for Almirón and Maurício to run onto. Paraguay will not pass for passing's sake — verticality over patience.

### Pressing
**Mid-block default with sharp counter-press triggers.** Paraguay defend in a compact 4-4-2 and pick their moments. Press triggers: a loose touch by the opposition centre-backs, a backpass to the keeper, or a throw-in deep in the opponent's half — Enciso and Ávalos curve their runs to cut the field in half while Almirón jumps the nearest pivot. On winning the ball, the whole front four attacks at speed before the opponent can reset.

### Defensive shape
Out of possession: **two banks of four, narrow and deep.** Gustavo Gómez marshals the line; Cubas screens the central channel; the wide midfielders (Almirón, Maurício) drop to make a flat four. Paraguay willingly concede the wide areas and territory to deny central penetration, inviting crosses to be headed clear by Gómez and Alderete. Against a side as ball-dominant as Germany, expect long, organised defensive shifts.

### Wide play
**Asymmetric and transition-led.** Almirón starts left but drifts inside, so left-side width comes from Alonso's overlap. On the right, Maurício stays wider and is the primary outlet to break — Cáceres supports late. Paraguay's wide threat is almost entirely about counter-attacking space, not patient flank build-up.

### Final third
Patterns: **Almirón and Maurício running the channels** in transition onto Ávalos's flick or a Cubas/Alderete line-breaking pass. **Enciso isolation** — get him the ball facing up at a defender and let him dribble or shoot. **Ávalos hold-up** to bring runners into play. Crosses to **Gustavo Gómez** arriving for set pieces. Against Germany, expect Paraguay to defend deep, weather sustained pressure, and look to win the game on the break or from a dead ball — a true smash-and-grab brief.

## Set Pieces
- Attacking corners: **Maurício** and **Almirón** deliver (in-swingers); primary aerial targets **Gustavo Gómez** (captain, dominant), **Omar Alderete**, and **Gabriel Ávalos** at near/back post. (Note: regular taker Diego Gómez is suspended, so delivery duties shift to Maurício/Almirón.)
- Defending corners: **man-and-zone hybrid** — Gómez and Alderete pick up the biggest threats, Cubas guards the near post, Gill commands his six-yard box.
- Free kicks: **Julio Enciso** direct from central/right positions; **Maurício** and **Almirón** as delivery from wide free kicks.
- Penalties: **Julio Enciso** is the primary taker, **Miguel Almirón** secondary, **Gabriel Ávalos** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode (keyed to `player_id` `_N` suffixes):
1. **If my `role == "GK"` (player_id `_0`, Gill) and pressed by 1 forward:** Play short to the nearest CB only if completely safe; **if pressed by 2 forwards or any uncertainty:** clear long toward `_10` (Ávalos) to compete for the second ball. Risk-averse distribution by default.
2. **If my `player_id` ends with `_3` (RCB, Gustavo Gómez, captain):** Hold the deepest line, organise the block, win aerial duels. Only carry forward if no opponent is within 12 units. The defensive reference point — never get dragged out of position.
3. **If my `player_id` ends with `_2` (LCB, Alderete) and team_phase == "attacking" and no opponent within 10 units:** Step out and carry into midfield or play the line-breaking vertical pass to a runner — he is the back line's progressor.
4. **If my `player_id` ends with `_1` (LB, Alonso) and team_phase == "attacking":** Overlap `_5` (Almirón) down the left ONLY when the ball is on the left and the situation is safe; otherwise tuck in to keep a back four. Defend first.
5. **If my `player_id` ends with `_4` (RB, Cáceres) and team_phase == "attacking":** Provide the right-side width behind `_8` (Maurício); pick overlaps sparingly and recover quickly. Tuck into a back three in build-up.
6. **If my `player_id` ends with `_6` (LCM, Cubas):** Stay as the deepest screen; never go beyond halfway in open play. Win the ball and give it simple to `_5` (Almirón) or `_2` (Alderete). The anchor.
7. **If my `player_id` ends with `_5` (LM, Almirón) and team has the ball:** Drift inside into the No. 10 space; on a turnover, immediately attack the space in behind — he is the chief transition outlet. When team_phase == "defending", drop to LM and hold the bank of four.
8. **If my `player_id` ends with `_7` (RCM, Galarza):** Shuttle box-to-box — support the press, then break forward to support the counter. Cover the channel `_8` (Maurício) vacates. Disciplined ball-winner and recycler in front of the back four.
9. **If my `player_id` ends with `_8` (RM, Maurício) and team_phase == "attacking" or "transition_attack":** Carry at speed down the right channel or cut inside; arrive late in the box for cutbacks. When team_phase == "defending", drop to RM in the bank of four.
10. **If team_phase == "transition_attack" (just won the ball):** `_5` (Almirón), `_8` (Maurício), `_9` (Enciso) and `_10` (Ávalos) all attack vertical space immediately — Paraguay's whole game is winning the moment. Prefer the fast forward pass over recycling.
11. **If my `player_id` ends with `_9` (ST, Enciso) and I have the ball facing up with an opponent within 5 units:** Take him on (Move/dribble) or shoot — Enciso is licensed to be direct. Drop short to combine when `_10` (Ávalos) pins the CBs.
12. **If my `player_id` ends with `_10` (ST, Ávalos) and team_phase == "attacking":** Hold the ball up with back to goal to bring runners in, occupy the centre-backs, and attack crosses and cutbacks. The reference striker.
13. **If team_phase == "transition_defense" (just lost the ball):** All MIDs and FWDs counter-press within a 6-unit radius for ~4 seconds; if no recovery, drop urgently into the deep 4-4-2 block.
14. **If the match is in the final 20 minutes and the team is losing:** Commit fullbacks (`_1`, `_4`) higher and push `_7` (Galarza) forward — chase the game. But as the underdog vs Germany, the default is to stay compact and protect a draw deep into the match before gambling.
15. **Penalty assignment:** Defer to `_9` (Enciso) first; if unavailable/fatigued (`stamina < 9`), `_5` (Almirón), then `_10` (Ávalos).

## Key Player Notes
- **Gustavo Gómez (15, idx 3):** Captain and spiritual leader, 33. The block is built around his reading of the game; aerially dominant at both ends. Set-piece weapon.
- **Miguel Almirón (23, idx 5):** The face of the team, fresh off a one-match suspension. Tireless running, drifts inside to create, presses from the front, and is the No. 1 transition outlet.
- **Julio Enciso (19, idx 9):** 22, the most talented attacker. Dribbler and shoot-on-sight forward; now the primary penalty and free-kick taker with Diego Gómez suspended. Paraguay's most likely man to conjure something from nothing.
- **Gabriel Ávalos (9, idx 10):** Experienced focal-point striker; holds play up and finishes the chances the counter creates. The hold-up axis the whole attack pivots through.
- **Andrés Cubas (14, idx 6):** The destroyer in front of the back four; his ball-winning and discipline are what make the deep block function. Booking risk to manage.
- **Matías Galarza (18, idx 7):** Two-way midfielder who scored the winner vs Türkiye; steps in for the suspended Diego Gómez and pairs with Cubas to screen the back line.
- **Maurício (20, idx 8):** Palmeiras' technical, two-footed midfielder and the scorer vs USA; the secondary creative spark and a late-arriving box threat down the right who also takes on dead-ball delivery.

## Tournament Mindset
A pragmatic, resilient side that lives on the counter and on set pieces. Battered 4-1 by the USA on opening day, Paraguay showed their true character in a backs-to-the-wall 1-0 win over Türkiye and a stout 0-0 with Australia to finish third in Group D and squeak into the Round of 32. Now they meet **Germany** as clear underdogs — but in a one-off knockout, that is precisely where Alfaro's Paraguay are most dangerous. The brief is simple: defend deep in two compact banks of four, frustrate a possession-heavy favourite, ride the storm, and strike once on an Enciso/Almirón counter or a Gustavo Gómez set-piece header. Stay in the game, take it to penalties if you must, and make Germany earn every inch. If Paraguay fall behind, the gloves come off and the fullbacks push up — but their best route to an upset is patience, discipline, and one ruthless moment.
