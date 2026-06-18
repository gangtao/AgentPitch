# Curaçao — Tactical Profile

## Identity & Philosophy
A debut World Cup nation and the most romantic story of the 2026 tournament: **Curaçao**, a Caribbean island of fewer than 160,000 people, is the **smallest nation by population ever to reach a World Cup**. They qualified under the veteran Dutch manager **Dick Advocaat** — at 78 the oldest head coach in World Cup history and the first man to lead three different nations at the finals — reappointed for the tournament after Fred Rutten's interim spell, out of semi-retirement to lead the diaspora-heavy squad of Dutch-trained, Eredivisie-pedigreed players who hold Curaçaoan passports. Advocaat's philosophy is **uncompromising defensive organization**: nominally a **4-3-3** that becomes a low **4-1-4-1 / 4-5-1** block out of possession — compact lines, narrow shape, and a willingness to absorb 70%+ possession in exchange for one or two transition or set-piece moments per game. Matchday 1 confirmed the gap: a **7-1 defeat to Germany**, with Livano Comenencia's debut goal the lone bright spot. Curaçao knows it cannot out-football the elite; it will out-organize them or die trying.

## Formation
- Shape: **4-3-3** nominally; collapses to a deep **4-1-4-1 / 4-5-1** block without the ball. This is the back-four shape Advocaat fielded against Germany.
- Role mapping (roster order in `curacao.yaml`):
  - index 0: GK — **Eloy Room** (1) — veteran shot-stopper, MLS/Eredivisie-tested; not a sweeper, stays on the goal line.
  - index 1: LB — **Sherel Floranus** (5) — disciplined fullback, rarely overlaps; the team's most defensive wide defender, prioritizes shape over forward runs.
  - index 2: LCB — **Armando Obispo** (18) — physical CB, the strongest aerial defender (PSV-tested); wins the channel duels and the first ball.
  - index 3: RCB — **Riechedly Bazoer** (6) — the most technical and physical of the back line; ball-playing CB who steps out. Conceded the penalty vs Germany — must stay disciplined.
  - index 4: RB — **Deveron Fonville** (2) — pacy, energetic right-back; the one fullback occasionally allowed to break forward on the counter, otherwise tucks in.
  - index 5: CM/anchor — **Leandro Bacuna** (10) — captain and emotional anchor; the deepest-lying organiser who screens the back four (the de facto single pivot in the low block) and delivers set pieces.
  - index 6: CM — **Juninho Bacuna** (7) — hybrid DM/CB, the captain's brother; shields the back four, recycles, drops between the CBs to make a back three when needed. Three goals in qualifying.
  - index 7: CM — **Livano Comenencia** (8) — the box-crashing interior; the qualifying revelation, late attacking runs and clinical finishing. Scored Curaçao's only goal vs Germany.
  - index 8: RW — **Tahith Chong** (21) — the team's most technical player and chief creator. Nominal right winger, drifts inside to combine; the only player who manufactures chances in open play.
  - index 9: ST — **Jürgen Locadia** (9) — target striker; physical, holds up balls (Brighton Premier League experience), peels off CBs for late runs.
  - index 10: LW — **Sontje Hansen** (12) — quick, skillful young forward (speed 15, dribbling 14); Ajax-raised, runs the channels, the transition outlet from the left.

## Style of Play

### Build-up
**Direct.** Curaçao does not enjoy possession against pressing opposition — Advocaat will not subject his side to building out of pressure they cannot resist. Room often goes long from goal kicks aiming at Locadia for a knock-down or into the channel for Hansen. When building short (against weaker opposition), the two CBs split, Juninho Bacuna drops between them, and Chong drifts inside to receive between the lines.

### Pressing
**Mid-low block, no high press.** Curaçao does not chase the ball. The front line (Chong, Locadia, Hansen) sits near the halfway line waiting to spring on a transition rather than pressing the opposition CBs. The trigger to engage is: **opposition midfielder receiving facing his own goal in his own half** — then Comenencia or Chong jumps. Otherwise, the side absorbs.

### Defensive shape
**A deep 4-1-4-1 / 4-5-1 block**, narrow, central. The block sits **deep** — around the edge of the 18-yard box under sustained pressure. Leandro Bacuna anchors in front of the CBs; Juninho Bacuna and Comenencia drop alongside to make a flat midfield five. The fullbacks stay narrow without the ball, prioritizing central compactness over wide cover. **Crosses are accepted** — Advocaat would rather concede the cross than let a runner through the middle, and Obispo wins the aerial duel anyway.

### Wide play
Minimal. **Chong** and **Hansen** are the wide forwards but they tuck inside more than overlap. Curaçao does not manufacture width; on the rare occasions it gets to the byline, Chong cuts inside and Fonville overlaps as a one-off. The default attack is direct down the middle, not wide.

### Final third
Patterns: Locadia hold-up → lay-off to Chong → through-ball to Hansen running the channel; Chong cut-in shot from 22 units; long ball over the top to Hansen's sprint; Comenencia's late run into the box; **set-piece delivery** is the most reliable route. Curaçao's chance map is heavily weighted to set pieces and counter-attacks.

## Set Pieces
- **Set pieces are the lifeline.** Half of Curaçao's expected goals will come from dead balls.
- Attacking corners: **Leandro Bacuna** delivers from both sides (in-swinger from the right, out-swinger from the left). Primary aerial targets: Obispo (penalty spot), Bazoer (near post), Locadia (back post). Comenencia crashes the second ball.
- Defending corners: **zonal-heavy** — six zonal markers along the six-yard line; only two man-markers on the most dangerous attackers. Obispo takes the front-post zonal.
- Free kicks: **Chong** takes direct from any zone within 26 units; **Leandro Bacuna** delivers wide free kicks.
- Penalties: **Locadia** primary, **Chong** secondary, **Leandro Bacuna** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my role is FWD (player_id ends with "_8" Chong, "_9" Locadia, or "_10" Hansen) and team_phase == "defending":** Drop toward the halfway line into the midfield five. Do not press the opposition CBs. Wait for transition.
2. **If my role is GK (player_id ends with "_0" — Room, jersey #1) and goal kick / open play with pressure:** Pass long toward the ST (player_id ends with "_9" — Locadia, jersey #9, target man, strength 14). Avoid short build-up under press.
3. **If my role is DEF and opposition has crossed the ball into the box:** Move to clear (Tackle / interception). Prioritize the first ball; the LCB (player_id ends with "_2" — Obispo, jersey #18) handles the aerial duel.
4. **If my role is MID and team_phase == "defending":** Tuck narrow into a flat five; keep within 10 units of the central CBs. Do not chase the ball wide.
5. **If my player_id ends with "_8" (RW, jersey #21 — Chong) and I receive the ball between the lines:** Carry forward (dribbling 14). Look for a Shoot from 22 units or a through-ball to LW "_10" (Hansen).
6. **If team has just won possession in our own third:** Long forward Pass to ST "_9" (Locadia) or into the channel for LW "_10" (Hansen) within 2 ticks. No short recycle.
7. **If my player_id ends with "_10" (LW, jersey #12 — Hansen) and team_phase == "transition_attack":** Sprint forward on the channel between the opposition fullback and centre-back.
8. **If my player_id ends with "_9" (ST, jersey #9 — Locadia) and a long ball is in flight:** Hold position, win the aerial duel (strength 14), lay off to RW "_8" (Chong) or the late-arriving CM "_7" (Comenencia).
9. **If team is leading or drawing and minute > 70:** Drop the block deeper (5-4-1 with CM "_6" — Juninho Bacuna — dropping between the CBs). Burn the clock.
10. **If my role is DEF and opposition wins a corner / wide free kick:** Drop into the box, zonal slot. LCB "_2" (Obispo) front-post zonal, RCB "_3" (Bazoer) near post.
11. **If my player_id ends with "_6" (CM, jersey #7 — Juninho Bacuna) and team has possession in our half:** Drop between the CBs to form a 3+1 (hybrid DM role); recycle to the captain anchor (player_id ends with "_5" — Leandro Bacuna) or out to LB "_1" (Floranus).
12. **If my player_id ends with "_7" (CM, jersey #8 — Comenencia) and team_phase == "transition_attack":** Make a late forward run into the box for the lay-off or cutback (offensive 13). Otherwise hold midfield shape.
13. **Set pieces / penalties:** defer to CM "_5" (Leandro Bacuna, corners/wide FKs), RW "_8" (Chong, direct FKs) and ST "_9" (Locadia, penalties).

## Key Player Notes
- **Leandro Bacuna (#10, index 5):** Captain. The emotional and tactical anchor, the single pivot screening the back four, and the primary set-piece deliverer. Ex-Aston Villa veteran.
- **Juninho Bacuna (#7, index 6):** The captain's brother; a hybrid DM/CB who drops between the centre-backs in build-up and shields the back four out of possession. Three goals in qualifying.
- **Livano Comenencia (#8, index 7):** The 22-year-old revelation of qualifying — late box-crashing runs and clinical finishing. Scored Curaçao's only World Cup goal so far (vs Germany).
- **Chong (#21, index 8):** Manchester United academy / Sheffield United technician — the team's chief creator and most-skilled ball-handler. The only player who can manufacture a chance from open play.
- **Hansen (#12, index 10):** Ajax-raised forward, qualifying standout — the pace partner for Locadia and the chief counter-attack outlet.
- **Locadia (#9, index 9):** Target striker. Premier League experience (Brighton). Wins the long ball.
- **Obispo (#18, index 2):** Aerially dominant CB (PSV). The box-defender on crosses and corners.
- **Bazoer (#6, index 3):** Ball-playing CB who steps out of the line; conceded the penalty vs Germany, so discipline and positioning are the watchwords.
- **Eloy Room (#1, index 0):** Veteran goalkeeper, the longest-serving man in the squad. Steady, not spectacular.

## Tournament Mindset
Curaçao is at the World Cup to **be there**. After the chastening 7-1 opening loss to Germany, the realistic objective shifts to **one point or a respectable scoreline** against Ecuador and Côte d'Ivoire in Group E. Every match is a defensive siege: park the bus, win set pieces, hope for a Chong moment, a Comenencia run, or a Hansen counter. The squad has no Premier League stars and no Champions League regulars, but has Eredivisie depth and the diaspora's chip-on-shoulder mentality. Advocaat's tactical clarity and emotional management is the team's biggest asset. A 0-0 draw will feel like a victory; a single goal will feel like a national holiday.
