# Ecuador — Tactical Profile

## Identity & Philosophy
Ecuador under Sebastián Beccacece are a compact, athletic, counter-attacking side built on the foundation of one of the world's best defensive midfield anchors (Moisés Caicedo) and a generation of young technical talent (Páez, Plata, Hincapié, Pacho). Beccacece's philosophy is pragmatic: deny space centrally, force play wide, win the second ball through Caicedo, transition vertically via Plata and Estupiñán's overlapping runs. Recent results: solid CONMEBOL qualifying performance, points deduction navigated, arriving as a dangerous outsider known for taking points off the giants.

## Formation
- Shape: **4-3-3** (Caicedo anchoring a midfield three, becomes 4-5-1 / 4-1-4-1 out of possession as the wingers tuck in)
- Role mapping (roster order in `ecuador.yaml`):
  - index 0: GK — **Hernán Galíndez** — experienced traditional keeper, shot-stopper, modest with feet; not a sweeper.
  - index 1: LB — **Pervis Estupiñán** — elite overlapping fullback, the team's primary width-provider on the left, top dead-ball delivery from the left.
  - index 2: LCB — **Piero Hincapié** — aggressive, left-footed ball-progressor, will step into midfield to break lines.
  - index 3: RCB — **Willian Pacho** — left-footed, calm, fast across the ground; the recovery defender of the pair.
  - index 4: RB — **Ángelo Preciado** — more conservative than Estupiñán; overlaps selectively.
  - index 5: CM (anchor) — **Moisés Caicedo** — the world-class anchor, screens the back four, wins the duel, recycles to the playmakers.
  - index 6: CM (box-to-box) — **Alan Franco** — defensive runner, covers Preciado's overlaps, the box-to-box ballast alongside Caicedo.
  - index 7: CM (advanced) — **Kendry Páez** — young creative engine of the three, drifts into the half-spaces, the team's chief progressive passer in tight spaces.
  - index 8: LW — **Nilson Angulo** — direct, pacy left winger (speed 16, dribbling 15), attacks the outside lane and the byline.
  - index 9: ST — **Enner Valencia** — captain, holds the ball up, makes intelligent runs in behind, the experienced focal point and near-post threat.
  - index 10: RW — **Gonzalo Plata** — direct, pacy, 1v1 dribbler, the team's chief carrier on transitions, holds the right touchline.

## Style of Play
### Build-up
**Mixed: short out of the back, vertical as soon as Caicedo gets the ball.** Galíndez plays short to Pacho or Hincapié. Caicedo drops between the CBs when pressed. The fullbacks (Estupiñán especially) push high and wide. Once Caicedo receives facing forward, the ball goes vertical — into Páez between the lines or long to Valencia with the wingers (Angulo/Plata) breaking off him. Ecuador will go long quickly under pressure; they do not force the build-up.

### Pressing
**Mid-block with selective high-press in transition moments.** Press triggers: opposition GK passing short, opposition CM receiving with back to play. Valencia leads the press by cover-shadowing the deepest CM, with Páez stepping up beside him and the wingers (Angulo/Plata) curving runs onto the fullbacks. Caicedo aggressively jumps onto the opposition #10. Ecuador is **not** a sustained high-press team — they don't have the stamina to do it for 90 minutes.

### Defensive shape
Out-of-possession: **4-5-1 / 4-1-4-1** — Angulo and Plata tuck in alongside Franco and Páez to form a midfield five; Valencia holds the line while screening the opposition pivot. The CBs hold a **medium-deep line** behind a compact midfield. Caicedo is the screen in front of the back four.

### Wide play
**Asymmetric:** Estupiñán bombs forward as the primary attacking width on the left; Angulo can come inside as Estupiñán overlaps outside. On the right, Plata holds the touchline because Preciado is more conservative.

### Final third
Patterns: **Estupiñán crosses** from the left byline to Valencia attacking the near post. **Plata 1v1 isolation** vs the opposition LB on the right — let him cook. **Páez between the lines** finding a runner. Ecuador is most dangerous in **transition** — a Caicedo turnover into a 4-pass move ending with Plata or Estupiñán's cross to Valencia and the far-post winger.

## Set Pieces
- Attacking corners: **Estupiñán** delivers (left-footed in-swingers from the right, out-swingers from the left). **Páez** alternate. Aerial targets: Pacho, Hincapié, Valencia, Franco.
- Defending corners: **hybrid** — four zonal markers, three man-markers, two short-corner watchers. Pacho attacks the first ball.
- Free kicks: **Estupiñán** delivers from set positions. **Páez** direct from central positions.
- Penalties: **Valencia** primary, **Páez** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_5` (DM, Caicedo) and team_phase == "defending":** Position centrally between the CBs and the midfield line; never venture past the halfway line.
2. **If my `player_id` ends with `_5` (DM, Caicedo) and an opponent has the ball within 8 units in central midfield:** Tackle (this is his primary action).
3. **If my `player_id` ends with `_1` (LB, Estupiñán) and team_phase == "attacking":** Sprint to the byline; prefer cross Pass to `_9` (ST Valencia) at the near post.
4. **If my `role == "GK"` (player_id `_0`, Galíndez) and pressed by 1 forward:** Play short to `_3` (Pacho); **if pressed by 2 forwards:** punt long toward `_9` (Valencia).
5. **If my `player_id` ends with `_7` (advanced CM, Páez) and I receive between the lines:** Face forward, look for `_10` (RW Plata)'s diagonal run or `_1` (LB Estupiñán)'s overlap before considering carry.
6. **If team_phase == "defending" and my `player_id` ends with `_10` (RW, Plata):** Drop into the midfield five; `_8` (LW Angulo) tucks in on the left.
7. **If my `player_id` ends with `_9` (ST, Valencia) and team_phase == "transition_attack":** Sprint into the channel between the opposition CBs; act as the outlet with the wingers (`_8` Angulo, `_10` Plata) breaking either side.
8. **If my `player_id` ends with `_2` (LCB, Hincapié) and no opponent within 10 units in midfield:** Step forward with the ball to break the line.
9. **If team_phase == "transition_defense":** Both wingers (`_8` Angulo, `_10` Plata) drop into the 5-man midfield bank within 6 ticks; only `_5` (Caicedo) holds central position immediately.
10. **If team is leading by 1+ goals and minute > 70:** Drop to low block, deny central space, rely on counters via `_10` (Plata).
11. **If my `role == "FWD"` and I'm carrying the ball in the attacking third with no clear pass:** `_9` (Valencia) Hold and wait for support, `_8` (Angulo) / `_10` (Plata) Shoot if in range else lay it off.
12. **Set-piece in attacking third with `_1` (Estupiñán) available:** Defer delivery to `_1`.

## Key Player Notes
- **Caicedo (23):** The world-class anchor. Never leaves the central screen position. Every defensive recovery in midfield is his first.
- **Estupiñán (7):** Most attacking player in the back line — provides all left-side width and delivery.
- **Páez (10):** Young creative — license to take risks between the lines from the advanced midfield role.
- **Valencia (13):** Captain, focal point, set-piece and penalty taker.
- **Plata (19):** Counter-attack carrier — let him 1v1 the LB on transitions from the right.
- **Angulo (20):** Direct left winger — pace and dribbling on the outside, the left-side counter outlet.
- **Pacho & Hincapié:** Two world-class, left-footed centre-backs (PSG / Arsenal) — the defensive spine and the source of progressive line-breaking carries.

## Tournament Mindset
Ecuador are the dangerous outsiders: athletic, disciplined, and capable of frustrating any of the giants for 70 minutes before Valencia or Plata break a game in transition. They will not chase a game from behind well — falling behind is fatal. Stamina-managed: Ecuador's mid-block requires fresh legs in the wide forward positions.
