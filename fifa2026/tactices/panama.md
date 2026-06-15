# Panama — Tactical Profile

## Identity & Philosophy
Panama's second-ever World Cup (first: Russia 2018). Under the Danish-Spanish manager **Thomas Christiansen**, Panama has matured from the wide-eyed debutants of 2018 into a tactically sophisticated, **mid-block counter-attacking** side that has consistently challenged Mexico and USA in CONCACAF qualifying. For the tournament Christiansen has settled on a **4-2-3-1** — a back four, a double pivot, an attacking trio behind a lone #9 — keeping the two clear identities: **compact mid-block** without the ball, **direct counter** with it. The team is well-organized on set pieces (both ways), tactically disciplined, and built around veterans who have been together for the better part of a decade. Panama is the prototypical **smart underdog** — it will not beat itself, and it will punish a careless elite team.

## Formation
- Shape: **4-2-3-1** in possession — back four, double pivot (Godoy + Harvey), a three behind a lone #9 (Díaz); **4-4-1-1 / 4-1-4-1** mid-block out of possession.
- Role mapping (roster order in `panama.yaml`):
  - index 0: GK — **Orlando Mosquera** — experienced shot-stopper; not a sweeper, stays on the goal line.
  - index 1: LB — **Eric Davis** — veteran captain (over 130 caps), the team's emotional and tactical anchor. Disciplined left-back; the primary set-piece deliverer, never gets caught out of position.
  - index 2: LCB — **José Córdoba** (Norwich City) — physical young CB; the aerial monitor and biggest defensive talent.
  - index 3: RCB — **Andrés Andrade** — disciplined central CB, the line-holder; not a ball player.
  - index 4: RB — **Michael Amir Murillo** (Beşiktaş) — converted from wing-back into a high, adventurous right-back; the team's pacy outlet on the right and top-tier experience.
  - index 5: DM/6 — **Aníbal Godoy** — veteran holding midfielder, the press-breaker; sits in front of the back four, recycles short, the slow heartbeat.
  - index 6: DM/8 — **Carlos Harvey** (Minnesota United) — box-to-box pivot partner; steps in for the injured Carrasquilla, physical, comfortable carrying through midfield.
  - index 7: LW — **Cecilio Waterman** — left of the attacking three; pacy, physical, the transition outlet who runs the channels.
  - index 8: AM/10 — **Cristian Martínez** — the central #10 with Carrasquilla out; energetic, tidy carrier who links pivot to attack and shuttles between the lines.
  - index 9: RW — **José Luis Rodríguez** (FC Juárez) — right of the three; quick dribbler (speed 15) who cuts inside, the secondary creator and direct free-kick taker.
  - index 10: ST — **Ismael Díaz** — the lone #9 and clinical finisher (shoot 15); primary penalty taker.

## Style of Play

### Build-up
**Mixed.** Panama is comfortable with short build-up against weaker opposition: the CBs split wide, Godoy drops in to form a 3+1, the full-backs (Davis, Murillo) push high, Rodríguez and Waterman operate between the lines. Against pressing opposition, Mosquera goes long aiming at Díaz or into the channel for Murillo's run. **Godoy is the press-breaker** — receive between the lines, find the diagonal to Murillo or the through-ball to Waterman.

### Pressing
**Mid-block first.** Panama does not high-press as a default; the front line sits at the halfway line. Trigger: opposition CB taking a heavy first touch or facing his own goal — Díaz curves the run, Waterman / Rodríguez jump the full-backs. The press is **trigger-based** and **selective** — never sustained. Christiansen's team is disciplined about energy management.

### Defensive shape
**Compact 4-4-1-1 / 4-1-4-1** out of possession: Waterman and Rodríguez drop alongside Godoy and Harvey to form a flat midfield four, Martínez tucks behind Díaz. The block is **mid-to-low** — Christiansen prefers to defend the edge of the 18-yard box. The back four holds a moderate-to-low line; the offside trap is not a primary weapon. **Tactical fouling** in midfield is encouraged to break counter-attacks.

### Wide play
**Full-back driven.** Width comes from Davis (LB) and Murillo (RB), with Murillo more adventurous. Waterman and Rodríguez can stay wide or drift into the half-spaces, opening lanes for the overlapping full-backs. The right side (Murillo + Rodríguez) is the higher-volume attacking lane.

### Final third
Patterns: Murillo overlap to byline → low cross to Díaz near post or Rodríguez at the edge of the box; Rodríguez cut-in shot from the right half-space; Godoy/Martínez through-ball to Waterman running the channel; Díaz one-on-one finish inside the box. Panama's set pieces are a major weapon — Davis's deliveries and Córdoba's aerial threat produce 30%+ of expected goals.

## Set Pieces
- **Set-piece organized both ways.** Christiansen drills the team relentlessly.
- Attacking corners: **Davis** delivers from both sides (out-swinger from the left, in-swinger from the right). Primary aerial targets: Córdoba (penalty spot), Andrade (near post), Harvey (back post).
- Defending corners: **hybrid** — three zonal at the six-yard line, four man-markers (Córdoba on the most dangerous), two short-corner blockers.
- Free kicks: **Rodríguez** takes direct from any zone within 26 units; **Davis** delivers wide free kicks on the left.
- Penalties: **Díaz** primary, **Waterman** secondary, **Rodríguez** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_5" (DM/6, jersey #20 — Godoy) and team_phase == "building_up":** Drop in front of the back four to form a 3+1. Recycle short, do not force vertical.
2. **If my player_id ends with "_9" (RW, jersey #7 — Rodríguez) and I receive the ball between the lines:** Prefer a forward Pass (through-ball to ST "_10" Díaz or diagonal to RB "_4" Murillo) over a recycle.
3. **If my role is MID/FWD in the attacking band and team_phase == "defending":** Drop to form a 4-4-1-1 (LW "_7" Waterman to LM, RW "_9" Rodríguez to RM, AM "_8" Martínez behind ST "_10" Díaz, who stays high).
4. **If my player_id ends with "_4" (RB, jersey #23 — Murillo) and team_phase == "attacking":** Push to the byline aggressively. The right side is the chance-creation lane.
5. **If my player_id ends with "_1" (LB, jersey #15 — Davis) and team_phase == "attacking":** Push on selectively — provide the width when the LW (player_id ends with "_7" — Waterman) tucks into the half-space, but never both full-backs high at once.
6. **If team has just won possession in our own third:** Vertical Pass to RW "_9" (Rodríguez) or directly to the ST "_10" (Díaz) within 3 ticks.
7. **If my player_id ends with "_7" (LW, jersey #18 — Waterman) and team_phase == "transition_attack":** Sprint forward on the channel — speed 14, the team's vertical outlet.
8. **If my role is MID and opposition has the ball in our half:** Tighten to a compact block; tactical foul on the ball-carrier within 5 units of the centre circle is encouraged.
9. **If my player_id ends with "_2" (LCB, jersey #3 — Córdoba) and a cross is incoming:** Attack the first ball at the penalty spot. Do not get drawn to the near post.
10. **If team is leading by 1+ goals and minute > 75:** Drop the block 8 units deeper. Burn the clock by recycling possession in the corner via LB "_1" (Davis) and DM "_5" (Godoy).
11. **If my player_id ends with "_10" (ST, jersey #10 — Díaz) and I have the ball in the box:** Shoot — clinical finishing is the priority (shoot rating 15).
12. **Set pieces / penalties:** defer to LB "_1" (Davis, corner and wide FK delivery), RW "_9" (Rodríguez, direct FKs) and ST "_10" (Díaz, penalties).

## Key Player Notes
- **Eric Davis (1):** Captain. Over 130 caps. The team's emotional and tactical anchor, now at left-back; the primary set-piece deliverer.
- **José Córdoba (2):** Young CB on the rise (Norwich City). Aerially dominant — the chief set-piece threat at both ends.
- **Murillo (4):** Beşiktaş full-back (ex-Marseille), now an attacking right-back. The pacy outlet on the right and the squad's top-tier experience.
- **Godoy (5):** Veteran pivot. The slow heartbeat — drops the tempo when needed, recycles under press.
- **Harvey (6):** Box-to-box pivot drafted into the starting XI to cover Carrasquilla's absence; physical, carries through midfield.
- **Martínez (8):** The makeshift #10 with Coco out — energetic shuttler linking the double pivot to the front three.
- **Rodríguez (9):** The secondary creator stepping up with Carrasquilla out — speed 15, dribbling 14, cuts in from the right and takes direct free kicks.
- **Díaz (10):** The lone #9. Primary penalty taker, clinical finisher. Shoot rating 15.
- **Carrasquilla (squad, not starting):** the usual chief creator and tempo-setter (Pumas UNAM) is carrying a groin/muscular injury from the Liga MX final — fit only for the bench, which pushes creation duties onto Martínez, Rodríguez and Godoy.
- **Fajardo (squad, alternative #9):** clinical finisher who rotates with Díaz up top; a like-for-like change when chasing or rotating the lone striker.

## Tournament Mindset
Panama under Christiansen is the **smart underdog**, opening **Group L against Ghana** (June 17, 2026, Toronto). The team has been together for a long time, knows its identity, and will not beat itself. The realistic objective is the **round of 16** — a stretch but achievable depending on the group. Panama is the prototype CONCACAF mid-block counter team: compact, organized, set-piece dangerous, with one or two technical players (Rodríguez, Díaz) who can produce a moment of quality. Expect Panama to score 1-2 goals per match and concede 1-2 — most games will be tight, low-scoring, and decided by a set piece or a transition moment. The team's biggest weakness is squad depth — sharpened by Carrasquilla's injury; a long tournament will stretch the veterans (Davis, Godoy) thin. Against Ghana, Panama will sit in the mid-block, deny space behind, and look to win the opener on a set piece or a Rodríguez/Murillo transition.
