# Ecuador — Tactical Profile

## Identity & Philosophy
Ecuador under Sebastián Beccacece are a compact, athletic, counter-attacking side built on the foundation of one of the world's best defensive midfield anchors (Moisés Caicedo) and a generation of young technical talent (Páez, Plata, Hincapié, Pacho). Beccacece's philosophy is pragmatic: deny space centrally, force play wide, win the second ball through Caicedo, transition vertically via Plata and Estupiñán's overlapping runs. Recent results: solid CONMEBOL qualifying performance, points deduction navigated, arriving as a dangerous outsider known for taking points off the giants.

## Formation
- Shape: **4-4-2** (compact midfield bank, becomes 4-4-1-1 / 4-5-1 out of possession when a striker drops)
- Role mapping (roster order in `ecuador.yaml`):
  - index 0: GK — **Hernán Galíndez** — experienced traditional keeper, shot-stopper, modest with feet; not a sweeper.
  - index 1: LB — **Pervis Estupiñán** — elite overlapping fullback, the team's primary width-provider on the left, top dead-ball delivery from the left.
  - index 2: LCB — **Willian Pacho** — left-footed, calm, fast across the ground; the recovery defender of the pair.
  - index 3: RCB — **Piero Hincapié** — aggressive, left-footed ball-progressor, will step into midfield to break lines.
  - index 4: RB — **Ángelo Preciado** — more conservative than Estupiñán; overlaps selectively.
  - index 5: LM — **Kendry Páez** — young creative engine on the left of the four, drifts inside into the left half-space, the team's chief progressive passer in tight spaces.
  - index 6: CM (left-central) — **Moisés Caicedo** — the world-class anchor, screens the back four, wins the duel, recycles to the playmakers.
  - index 7: CM (right-central) — **Alan Franco** — defensive runner, covers Preciado's overlaps, the box-to-box ballast alongside Caicedo.
  - index 8: RM — **Gonzalo Plata** — direct, pacy, 1v1 dribbler, the team's chief carrier on transitions, holds the right touchline.
  - index 9: ST (left of the two) — **Kevin Rodríguez** — physical forward, runner in behind / target man, occupies the left channel and the far post.
  - index 10: ST (right of the two) — **Enner Valencia** — captain, holds the ball up, makes intelligent runs in behind, the experienced focal point and near-post threat.

## Style of Play
### Build-up
**Mixed: short out of the back, vertical as soon as Caicedo gets the ball.** Galíndez plays short to Pacho or Hincapié. Caicedo drops between the CBs when pressed. The fullbacks (Estupiñán especially) push high and wide. Once Caicedo receives facing forward, the ball goes vertical — into Páez between the lines or long to the front two (Valencia/Rodríguez). Ecuador will go long quickly under pressure; they do not force the build-up.

### Pressing
**Mid-block with selective high-press in transition moments.** Press triggers: opposition GK passing short, opposition CM receiving with back to play. The front two (Valencia/Rodríguez) lead the press by cover-shadowing the deepest CM. Caicedo aggressively jumps onto the opposition #10. Ecuador is **not** a sustained high-press team — they don't have the stamina to do it for 90 minutes.

### Defensive shape
Out-of-possession: **4-4-2 / 4-4-1-1** — Páez and Plata tuck into a flat midfield four with Caicedo and Franco; one striker drops to screen the opposition pivot while the other holds the line. The CBs hold a **medium-deep line** behind a compact midfield four. Caicedo is the screen in front of the back four.

### Wide play
**Asymmetric:** Estupiñán bombs forward as the primary attacking width on the left; Páez can drift inside as Estupiñán overlaps outside. On the right, Plata holds the touchline because Preciado is more conservative.

### Final third
Patterns: **Estupiñán crosses** from the left byline to Valencia attacking the near post. **Plata 1v1 isolation** vs the opposition LB on the right — let him cook. **Páez between the lines** finding a runner. Ecuador is most dangerous in **transition** — a Caicedo turnover into a 4-pass move ending with Plata or Estupiñán's cross to the front two.

## Set Pieces
- Attacking corners: **Estupiñán** delivers (left-footed in-swingers from the right, out-swingers from the left). **Páez** alternate. Aerial targets: Pacho, Hincapié, Valencia, Rodríguez.
- Defending corners: **hybrid** — four zonal markers, three man-markers, two short-corner watchers. Pacho attacks the first ball.
- Free kicks: **Estupiñán** delivers from set positions. **Páez** direct from central positions.
- Penalties: **Valencia** primary, **Páez** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_6` (DM, Caicedo) and team_phase == "defending":** Position centrally between the CBs and the midfield line; never venture past the halfway line.
2. **If my `player_id` ends with `_6` (DM, Caicedo) and an opponent has the ball within 8 units in central midfield:** Tackle (this is his primary action).
3. **If my `player_id` ends with `_1` (LB, Estupiñán) and team_phase == "attacking":** Sprint to the byline; prefer cross Pass to `_10` (ST Valencia) at the near post.
4. **If my `role == "GK"` (player_id `_0`, Galíndez) and pressed by 1 forward:** Play short to `_2` (Pacho); **if pressed by 2 forwards:** punt long toward `_10` (Valencia).
5. **If my `player_id` ends with `_5` (LM/AM, Páez) and I receive between the lines:** Face forward, look for `_8` (RM Plata)'s diagonal run or `_1` (LB Estupiñán)'s overlap before considering carry.
6. **If team_phase == "defending" and my `player_id` ends with `_8` (RM, Plata):** Drop into the flat midfield four; `_5` (LM Páez) tucks in on the left.
7. **If my `player_id` ends with `_10` (ST, Valencia) and team_phase == "transition_attack":** Sprint into the channel between the opposition CBs; act as the outlet alongside `_9` (Rodríguez).
8. **If my `player_id` ends with `_3` (RCB, Hincapié) and no opponent within 10 units in midfield:** Step forward with the ball to break the line.
9. **If team_phase == "transition_defense":** Both wide midfielders (`_5` Páez, `_8` Plata) drop into the 4-man midfield bank within 6 ticks; only `_6` (Caicedo) holds central position immediately.
10. **If team is leading by 1+ goals and minute > 70:** Drop to low block, deny central space, rely on counters via `_8` (Plata).
11. **If my `role == "FWD"` and I'm carrying the ball in the attacking third with no clear pass:** `_10` (Valencia) Hold and wait for support, `_9` (Rodríguez) Shoot if in range else lay it off.
12. **Set-piece in attacking third with `_1` (Estupiñán) available:** Defer delivery to `_1`.

## Key Player Notes
- **Caicedo (23):** The world-class anchor. Never leaves the central screen position. Every defensive recovery in midfield is his first.
- **Estupiñán (7):** Most attacking player in the back line — provides all left-side width and delivery.
- **Páez (20):** Young creative — license to take risks between the lines from the left of midfield.
- **Valencia (13):** Captain, focal point, set-piece and penalty taker.
- **Plata (19):** Counter-attack carrier — let him 1v1 the LB on transitions from the right.
- **Pacho & Hincapié:** Two world-class, left-footed centre-backs (PSG / Arsenal) — the defensive spine and the source of progressive line-breaking carries.

## Tournament Mindset
Ecuador are the dangerous outsiders: athletic, disciplined, and capable of frustrating any of the giants for 70 minutes before Valencia or Plata break a game in transition. They will not chase a game from behind well — falling behind is fatal. Stamina-managed: Ecuador's mid-block requires fresh legs in the wide midfield positions.
