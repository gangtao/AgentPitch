# Curaçao — Tactical Profile

## Identity & Philosophy
A debut World Cup nation and one of the most romantic stories of the 2026 tournament. **Curaçao**, a Caribbean island of fewer than 160,000 people, qualified for its first-ever World Cup under the veteran Dutch manager **Dick Advocaat** — a 76-year-old who came out of semi-retirement to lead the diaspora-heavy squad of Dutch-trained, Eredivisie-pedigreed players who hold Curaçaoan passports. Advocaat's philosophy is **uncompromising defensive organization** within a classic **4-4-2**: two banks of four, compact lines, narrow shape, and a willingness to absorb 70% possession in exchange for one or two transition or set-piece moments per game. Curaçao knows it cannot out-football the elite; it will out-organize them or die trying.

## Formation
- Shape: **4-4-2** rigidly — two banks of four, two strikers, narrow.
- Role mapping (roster order in `curacao.yaml`):
  - index 0: GK — **Eloy Room** — veteran shot-stopper, MLS-tested; not a sweeper, stays on the goal line.
  - index 1: LB — **Joshua Brenet** — experienced Eredivisie fullback; disciplined, rarely overlaps deep.
  - index 2: LCB — **Juninho Bacuna** — captain, listed as DEF but a hybrid CB/DM; the team's leader and emotional anchor (Leandro Bacuna's brother).
  - index 3: RCB — **Armando Obispo** — physical CB, the strongest aerial defender; PSV-tested.
  - index 4: RB — **Sherel Floranus** — disciplined RB, rarely overlaps; the team's most defensive fullback.
  - index 5: LM — **Leandro Bacuna** — experienced wide midfielder; gives shape to the left bank of four, occasionally drifts inside.
  - index 6: CM — **Godfried Roemeratoe** — disciplined holding midfielder; the line-protector in front of the back four.
  - index 7: CM — **Roshon van Eijma** — physical box-to-box, the energy of the midfield two.
  - index 8: RM/AM — **Tahith Chong** — the team's most technical player; the wide midfielder on paper, but the chief creator in practice. Drifts inside to combine with the strikers.
  - index 9: ST — **Jürgen Locadia** — target striker; physical, holds up balls, peels off CBs for late runs.
  - index 10: ST — **Gervane Kastaneer** — pacy mobile striker; runs the channels, the transition outlet alongside Locadia.

## Style of Play

### Build-up
**Direct.** Curaçao does not enjoy possession against pressing opposition — Advocaat will not subject his side to building out of pressure they cannot resist. Room often goes long from goal kicks aiming at Locadia for a knock-down or into the channel for Kastaneer. When building short (against weaker opposition), the two CBs split and Roemeratoe drops between them; Chong drifts inside to receive between the lines.

### Pressing
**Mid-low block, no high press.** Curaçao does not chase the ball. The two strikers (Locadia, Kastaneer) sit at the halfway line waiting to spring on a transition rather than pressing the opposition CBs. The trigger to engage is: **opposition midfielder receiving facing his own goal in his own half** — then Chong jumps. Otherwise, the side absorbs.

### Defensive shape
**Two banks of four**, narrow, central. The block sits **deep** — around the edge of the 18-yard box when under sustained pressure. Roemeratoe and van Eijma protect the channels in front of the CBs. The fullbacks stay narrow without the ball, prioritizing central compactness over wide cover. **Crosses are accepted** — Advocaat would rather concede the cross than let a runner through the middle, and Obispo wins the aerial duel anyway.

### Wide play
Minimal. **Bacuna (Leandro)** and **Chong** are the wide midfielders in the 4-4-2, but they tuck inside more than overlap. Curaçao does not manufacture width; on the rare occasions it gets to the byline, Chong cuts inside and Brenet overlaps as a one-off. The default attack is direct down the middle, not wide.

### Final third
Patterns: Locadia hold-up → lay-off to Chong → through-ball to Kastaneer running the channel; Chong cut-in shot from 22 units; long ball over the top to Kastaneer's sprint; **set-piece delivery** is the most reliable route. Curaçao's chance map will be heavily weighted to set pieces and counter-attacks.

## Set Pieces
- **Set pieces are the lifeline.** Half of Curaçao's expected goals will come from dead balls.
- Attacking corners: **Leandro Bacuna** delivers from both sides (in-swinger from the right, out-swinger from the left). Primary aerial targets: Obispo (penalty spot), Locadia (near post), Juninho Bacuna (back post).
- Defending corners: **zonal-heavy** — six zonal markers along the six-yard line; only two man-markers on the most dangerous attackers. Obispo takes the front-post zonal.
- Free kicks: **Chong** takes direct from any zone within 26 units; **Leandro Bacuna** delivers wide free kicks.
- Penalties: **Locadia** primary, **Chong** secondary, **Leandro Bacuna** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my role is FWD (player_id ends with "_9" Locadia or "_10" Kastaneer) and team_phase == "defending":** Stay at the halfway line. Do not press the opposition CBs. Wait for transition.
2. **If my role is GK (player_id ends with "_0" — Room) and goal kick / open play with pressure:** Pass long toward the ST (player_id ends with "_9" — Locadia, target man, strength 14). Avoid short build-up under press.
3. **If my role is DEF and opposition has crossed the ball into the box:** Move to clear (Tackle / interception). Prioritize the first ball; the RCB (player_id ends with "_3" — Obispo) handles the aerial duel.
4. **If my role is MID and team_phase == "defending":** Tuck narrow; keep within 10 units of the central CBs. Do not chase the ball wide.
5. **If my player_id ends with "_8" (RM, jersey #10 — Chong) and I receive the ball between the lines:** Carry forward (dribbling 14). Look for a Shoot from 22 units or a through-ball to ST "_10" (Kastaneer).
6. **If team has just won possession in our own third:** Long forward Pass to ST "_9" (Locadia) or into the channel for ST "_10" (Kastaneer) within 2 ticks. No short recycle.
7. **If my player_id ends with "_10" (ST, jersey #9 — Kastaneer) and team_phase == "transition_attack":** Sprint forward on the channel between LB and LCB or RB and RCB.
8. **If my player_id ends with "_9" (ST, jersey #11 — Locadia) and a long ball is in flight:** Hold position, win the aerial duel (strength 14), lay off to RM "_8" (Chong) or ST "_10" (Kastaneer).
9. **If team is leading or drawing and minute > 70:** Drop the block deeper (5-4-1 with LCB "_2" — Juninho Bacuna — dropping to RB if needed). Burn the clock.
10. **If my role is DEF and opposition wins a corner / wide free kick:** Drop into the box, zonal slot. RCB "_3" (Obispo) near post, LB "_1" (Brenet) back post.
11. **If my player_id ends with "_2" (LCB, jersey #5 — Juninho Bacuna) and team has possession in our half:** Step into midfield to form a 3+1 (hybrid DM role); recycle to the CM (player_id ends with "_6" — Roemeratoe).
12. **Set pieces / penalties:** defer to RM "_8" (Chong, delivery and direct FKs) and ST "_9" (Locadia, penalties).

## Key Player Notes
- **Juninho Bacuna (2):** Captain. The emotional and tactical anchor. Listed as DEF but operates as a hybrid CB/DM in build-up.
- **Chong (8):** Manchester United / Birmingham technician — the team's chief creator and most-skilled ball-handler. The only player who can manufacture a chance from open play.
- **Locadia (9):** Target striker. Premier League experience (Brighton). Wins the long ball.
- **Obispo (3):** Aerially dominant CB. The box-defender on crosses and corners.
- **Leandro Bacuna (5):** Captain's brother, set-piece deliverer. The veteran presence in midfield.
- **Eloy Room (0):** MLS veteran (Columbus Crew). Steady, not spectacular.

## Tournament Mindset
Curaçao is at the World Cup to **be there**. The team's realistic objective is **one point** in the group stage — a draw against the weakest opponent, a respectable defeat against the elite. Every match will be a defensive siege: park the bus, win set pieces, hope for a Chong moment or a Kastaneer counter. The squad has no Premier League stars, no Champions League regulars, but has the Eredivisie depth and the diaspora's chip-on-shoulder mentality. Advocaat's tactical clarity and emotional management is the team's biggest asset. A 0-0 draw will feel like a victory; a 1-0 win will feel like a national holiday.
