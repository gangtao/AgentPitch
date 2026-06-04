# Curaçao — Tactical Profile

## Identity & Philosophy
A debut World Cup nation and one of the most romantic stories of the 2026 tournament. **Curaçao**, a Caribbean island of fewer than 160,000 people, qualified for its first-ever World Cup under the veteran Dutch manager **Dick Advocaat** — at 78 the oldest head coach in World Cup history and the first man to lead three different nations at the finals — who came out of semi-retirement to lead the diaspora-heavy squad of Dutch-trained, Eredivisie-pedigreed players who hold Curaçaoan passports. Advocaat's philosophy is **uncompromising defensive organization** within a classic **4-4-2**: two banks of four, compact lines, narrow shape, and a willingness to absorb 70% possession in exchange for one or two transition or set-piece moments per game. Curaçao knows it cannot out-football the elite; it will out-organize them or die trying.

## Formation
- Shape: **4-4-2** rigidly — two banks of four, two strikers, narrow.
- Role mapping (roster order in `curacao.yaml`):
  - index 0: GK — **Eloy Room** (1) — veteran shot-stopper, MLS-tested (Miami FC); not a sweeper, stays on the goal line.
  - index 1: LB — **Sherel Floranus** (5) — disciplined fullback, rarely overlaps; the team's most defensive wide defender.
  - index 2: LCB — **Armando Obispo** (18) — physical CB, the strongest aerial defender; PSV-tested.
  - index 3: RCB — **Roshon van Eijma** (4) — physical, no-nonsense central defender; reads the first ball, wins the channel duels.
  - index 4: RB — **Shurandy Sambo** (2) — the quickest fullback (Sparta Rotterdam); the one defender allowed to break forward on the counter.
  - index 5: LM — **Leandro Bacuna** (10) — captain and emotional anchor; experienced wide midfielder, gives shape to the left bank of four and occasionally drifts inside.
  - index 6: CM — **Juninho Bacuna** (7) — hybrid DM/CB, the team's deepest-lying organiser (Leandro Bacuna's brother); shields the back four and recycles.
  - index 7: CM — **Godfried Roemeratoe** (6) — disciplined holding midfielder; the second line-protector and energy of the midfield two.
  - index 8: RM/AM — **Tahith Chong** (22) — the team's most technical player; the wide midfielder on paper, but the chief creator in practice. Drifts inside to combine with the strikers.
  - index 9: ST — **Jürgen Locadia** (9) — target striker; physical, holds up balls, peels off CBs for late runs.
  - index 10: ST — **Gervane Kastaneer** (19) — pacy mobile striker; runs the channels, the transition outlet alongside Locadia.

## Style of Play

### Build-up
**Direct.** Curaçao does not enjoy possession against pressing opposition — Advocaat will not subject his side to building out of pressure they cannot resist. Room often goes long from goal kicks aiming at Locadia for a knock-down or into the channel for Kastaneer. When building short (against weaker opposition), the two CBs split and Juninho Bacuna drops between them; Chong drifts inside to receive between the lines.

### Pressing
**Mid-low block, no high press.** Curaçao does not chase the ball. The two strikers (Locadia, Kastaneer) sit at the halfway line waiting to spring on a transition rather than pressing the opposition CBs. The trigger to engage is: **opposition midfielder receiving facing his own goal in his own half** — then Chong jumps. Otherwise, the side absorbs.

### Defensive shape
**Two banks of four**, narrow, central. The block sits **deep** — around the edge of the 18-yard box when under sustained pressure. Juninho Bacuna and Roemeratoe protect the channels in front of the CBs. The fullbacks stay narrow without the ball, prioritizing central compactness over wide cover. **Crosses are accepted** — Advocaat would rather concede the cross than let a runner through the middle, and Obispo wins the aerial duel anyway.

### Wide play
Minimal. **Bacuna (Leandro)** and **Chong** are the wide midfielders in the 4-4-2, but they tuck inside more than overlap. Curaçao does not manufacture width; on the rare occasions it gets to the byline, Chong cuts inside and Sambo overlaps as a one-off. The default attack is direct down the middle, not wide.

### Final third
Patterns: Locadia hold-up → lay-off to Chong → through-ball to Kastaneer running the channel; Chong cut-in shot from 22 units; long ball over the top to Kastaneer's sprint; **set-piece delivery** is the most reliable route. Curaçao's chance map will be heavily weighted to set pieces and counter-attacks.

## Set Pieces
- **Set pieces are the lifeline.** Half of Curaçao's expected goals will come from dead balls.
- Attacking corners: **Leandro Bacuna** delivers from both sides (in-swinger from the right, out-swinger from the left). Primary aerial targets: Obispo (penalty spot), Locadia (near post), van Eijma (back post).
- Defending corners: **zonal-heavy** — six zonal markers along the six-yard line; only two man-markers on the most dangerous attackers. Obispo takes the front-post zonal.
- Free kicks: **Chong** takes direct from any zone within 26 units; **Leandro Bacuna** delivers wide free kicks.
- Penalties: **Locadia** primary, **Chong** secondary, **Leandro Bacuna** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my role is FWD (player_id ends with "_9" Locadia or "_10" Kastaneer) and team_phase == "defending":** Stay at the halfway line. Do not press the opposition CBs. Wait for transition.
2. **If my role is GK (player_id ends with "_0" — Room, jersey #1) and goal kick / open play with pressure:** Pass long toward the ST (player_id ends with "_9" — Locadia, jersey #9, target man, strength 14). Avoid short build-up under press.
3. **If my role is DEF and opposition has crossed the ball into the box:** Move to clear (Tackle / interception). Prioritize the first ball; the LCB (player_id ends with "_2" — Obispo, jersey #18) handles the aerial duel.
4. **If my role is MID and team_phase == "defending":** Tuck narrow; keep within 10 units of the central CBs. Do not chase the ball wide.
5. **If my player_id ends with "_8" (RM, jersey #22 — Chong) and I receive the ball between the lines:** Carry forward (dribbling 14). Look for a Shoot from 22 units or a through-ball to ST "_10" (Kastaneer).
6. **If team has just won possession in our own third:** Long forward Pass to ST "_9" (Locadia) or into the channel for ST "_10" (Kastaneer) within 2 ticks. No short recycle.
7. **If my player_id ends with "_10" (ST, jersey #19 — Kastaneer) and team_phase == "transition_attack":** Sprint forward on the channel between LB and LCB or RB and RCB.
8. **If my player_id ends with "_9" (ST, jersey #9 — Locadia) and a long ball is in flight:** Hold position, win the aerial duel (strength 14), lay off to RM "_8" (Chong) or ST "_10" (Kastaneer).
9. **If team is leading or drawing and minute > 70:** Drop the block deeper (5-4-1 with CM "_6" — Juninho Bacuna — dropping between the CBs as needed). Burn the clock.
10. **If my role is DEF and opposition wins a corner / wide free kick:** Drop into the box, zonal slot. LCB "_2" (Obispo) near post, RCB "_3" (van Eijma) back post.
11. **If my player_id ends with "_6" (CM, jersey #7 — Juninho Bacuna) and team has possession in our half:** Drop between the CBs to form a 3+1 (hybrid DM role); recycle to the captain at LM (player_id ends with "_5" — Leandro Bacuna) or to CM "_7" (Roemeratoe).
12. **Set pieces / penalties:** defer to RM "_8" (Chong, delivery and direct FKs) and ST "_9" (Locadia, penalties).

## Key Player Notes
- **Leandro Bacuna (#10, index 5):** Captain. The emotional and tactical anchor and the primary set-piece deliverer. Ex-Aston Villa; the veteran presence on the left of midfield.
- **Juninho Bacuna (#7, index 6):** The captain's brother; a hybrid DM/CB who drops between the centre-backs in build-up and shields the back four out of possession.
- **Chong (#22, index 8):** Manchester United academy / Sheffield United technician — the team's chief creator and most-skilled ball-handler. The only player who can manufacture a chance from open play.
- **Locadia (#9, index 9):** Target striker. Premier League experience (Brighton). Wins the long ball.
- **Obispo (#18, index 2):** Aerially dominant CB (PSV). The box-defender on crosses and corners.
- **Eloy Room (#1, index 0):** MLS-pedigree veteran goalkeeper (Miami FC). Steady, not spectacular.

## Tournament Mindset
Curaçao is at the World Cup to **be there**. The team's realistic objective is **one point** in the group stage — a draw against the weakest opponent, a respectable defeat against the elite. Every match will be a defensive siege: park the bus, win set pieces, hope for a Chong moment or a Kastaneer counter. The squad has no Premier League stars, no Champions League regulars, but has the Eredivisie depth and the diaspora's chip-on-shoulder mentality. Advocaat's tactical clarity and emotional management is the team's biggest asset. A 0-0 draw will feel like a victory; a 1-0 win will feel like a national holiday.
