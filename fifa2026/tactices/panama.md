# Panama — Tactical Profile

## Identity & Philosophy
Panama's second-ever World Cup (first: Russia 2018). Under the Danish-Spanish manager **Thomas Christiansen**, Panama has matured from the wide-eyed debutants of 2018 into a tactically sophisticated, **mid-block counter-attacking** side that has consistently challenged Mexico and USA in CONCACAF qualifying. Christiansen's Panama plays a **flexible 4-3-3 / 4-2-3-1** with two clear identities: **compact mid-block** without the ball, **direct counter** with it. The team is well-organized on set pieces (both ways), tactically disciplined, and full of veterans who have been together for the better part of a decade. Panama is the prototypical **smart underdog** — it will not beat itself, and it will punish a careless elite team.

## Formation
- Shape: **4-3-3** in possession, often morphing to **4-2-3-1** with Carrasquilla pushed forward as a #10; **4-1-4-1** mid-block out of possession.
- Role mapping (roster order in `panama.yaml`):
  - index 0: GK — **Orlando Mosquera** — experienced shot-stopper; not a sweeper, stays on the goal line.
  - index 1: LB — **Eric Davis** — veteran captain (over 130 caps), the team's emotional and tactical anchor. Disciplined attacking LB; selective overlaps, never gets caught out of position.
  - index 2: LCB — **José Córdoba** — physical young CB; the aerial monitor and biggest defensive talent.
  - index 3: RCB — **Andrés Andrade** — disciplined CB, the line-holder; not a ball player.
  - index 4: RB — **Michael Amir Murillo** — adventurous attacking RB (Marseille); the team's pacy outlet on the right.
  - index 5: DM/6 — **Aníbal Godoy** — veteran holding midfielder, the press-breaker; sits in front of the back four, recycles short, the slow heartbeat.
  - index 6: CM/8 — **Adalberto Carrasquilla** — the team's chief creator. Box-to-box #8 with the highest pass and skill ratings; can play as a #10 in the 4-2-3-1 variant.
  - index 7: CM/8 — **Carlos Harvey** — physical box-to-box, the runner alongside Carrasquilla.
  - index 8: LW/AM — **Yoel Bárcenas** — wide-and-inside hybrid; cuts inside off the left, the secondary creator.
  - index 9: CF — **Cecilio Waterman** — pacy physical #9; the transition outlet, runs the channels.
  - index 10: RW/CF — **Ismael Díaz** — clinical finisher (shoot 15); can play as the lone #9 or wide-and-inside off the right.

## Style of Play

### Build-up
**Mixed.** Panama is comfortable with short build-up against weaker opposition: Godoy drops between the CBs, the fullbacks push high, Carrasquilla operates between the lines. Against pressing opposition, Mosquera goes long aiming at Waterman or into the channel for Murillo's run. **Godoy is the press-breaker** — receive between the lines, find the diagonal to Murillo or the through-ball to Waterman.

### Pressing
**Mid-block first.** Panama does not high-press as a default; the front three sits at the halfway line. Trigger: opposition CB taking a heavy first touch or facing his own goal — Waterman curves the run, Bárcenas / Díaz jump the fullbacks. The press is **trigger-based** and **selective** — never sustained. Christiansen's team is disciplined about energy management.

### Defensive shape
**Compact 4-1-4-1** out of possession with Godoy as the single pivot. Carrasquilla and Harvey drop to form a flat midfield four with Bárcenas and Díaz (or Waterman dropping). The block is **mid-to-low** — Christiansen prefers to defend the edge of the 18-yard box. The CBs hold a moderate-to-low line; the offside trap is not a primary weapon. **Tactical fouling** in midfield is encouraged to break counter-attacks.

### Wide play
**Symmetric.** Both Davis (LB) and Murillo (RB) overlap selectively, with Murillo more adventurous. Bárcenas and Díaz both cut inside, opening the wide lanes for the fullbacks. The right side (Murillo + Díaz) is the higher-volume attacking lane.

### Final third
Patterns: Murillo overlap to byline → low cross to Waterman near post or Carrasquilla edge of the box; Bárcenas cut-in shot from the left half-space; Carrasquilla through-ball to Waterman running the channel; Díaz one-on-one finish from the right inside the box. Panama's set pieces are a major weapon — Carrasquilla's deliveries and Córdoba's aerial threat produce 30%+ of expected goals.

## Set Pieces
- **Set-piece organized both ways.** Christiansen drills the team relentlessly.
- Attacking corners: **Carrasquilla** delivers from both sides (in-swinger from the right, out-swinger from the left). Primary aerial targets: Córdoba (penalty spot), Andrade (near post), Waterman (back post).
- Defending corners: **hybrid** — three zonal at the six-yard line, four man-markers (Córdoba on the most dangerous), two short-corner blockers.
- Free kicks: **Carrasquilla** takes direct from any zone within 26 units; **Davis** delivers wide free kicks on the left.
- Penalties: **Díaz** primary, **Carrasquilla** secondary, **Waterman** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_5" (DM, jersey #20 — Godoy) and team_phase == "building_up":** Drop between the CBs to form a 3+1. Recycle short, do not force vertical.
2. **If my player_id ends with "_6" (CM, jersey #6 — Carrasquilla) and I receive the ball between the lines:** Prefer a forward Pass (through-ball to CF "_9" Waterman or diagonal to RB "_4" Murillo) over a recycle.
3. **If my role is FWD and team_phase == "defending":** Drop to form a 4-1-4-1 (LW "_8" Bárcenas to LM, RW "_10" Díaz to RM, CF "_9" Waterman stays high).
4. **If my player_id ends with "_4" (RB, jersey #13 — Murillo) and team_phase == "attacking":** Overlap to the byline aggressively. The right side is the chance-creation lane.
5. **If my player_id ends with "_1" (LB, jersey #15 — Davis) and team_phase == "attacking":** Overlap selectively — only when the LW (player_id ends with "_8" — Bárcenas) has the ball in the half-space. Otherwise hold LB position.
6. **If team has just won possession in our own third:** Vertical Pass to CM "_6" (Carrasquilla) or directly to a forward within 3 ticks.
7. **If my player_id ends with "_9" (CF, jersey #9 — Waterman) and team_phase == "transition_attack":** Sprint forward on the channel — speed 14, the team's vertical outlet.
8. **If my role is MID and opposition has the ball in our half:** Tighten to compact 4-1-4-1; tactical foul on the ball-carrier within 5 units of the centre circle is encouraged.
9. **If my player_id ends with "_2" (LCB, jersey #3 — Córdoba) and a cross is incoming:** Attack the first ball at the penalty spot. Do not get drawn to the near post.
10. **If team is leading by 1+ goals and minute > 75:** Drop the block 8 units deeper. Burn the clock by recycling possession in the corner via LB "_1" (Davis) and DM "_5" (Godoy).
11. **If my player_id ends with "_10" (RW/CF, jersey #7 — Díaz) and I have the ball in the box:** Shoot — clinical finishing is the priority (shoot rating 15).
12. **Set pieces / penalties:** defer to CM "_6" (Carrasquilla, delivery and direct FKs) and RW "_10" (Díaz, penalties).

## Key Player Notes
- **Eric Davis (1):** Captain. Over 130 caps. The team's emotional and tactical anchor.
- **Carrasquilla (6):** The chief creator. Highest pass rating (15) and skill (15) — every chance from open play runs through him.
- **Córdoba (2):** Young CB on the rise (Levski Sofia / Ligue 1 watch). Aerially dominant.
- **Murillo (4):** Marseille fullback. The pacy attacking outlet on the right.
- **Díaz (10):** Primary penalty taker, clinical finisher. Shoot rating 15.
- **Godoy (5):** Veteran DM. The slow heartbeat — drops the tempo when needed, recycles under press.
- **Waterman (9):** The transition outlet. Speed 14, strength 13. Runs the channels.

## Tournament Mindset
Panama under Christiansen is the **smart underdog**. The team has been together for a long time, knows its identity, and will not beat itself. The realistic objective is the **round of 16** — a stretch but achievable depending on draw. Panama is the prototype CONCACAF mid-block counter team: compact, organized, set-piece dangerous, with one or two technical players (Carrasquilla, Bárcenas) who can produce a moment of quality. Expect Panama to score 1-2 goals per match and concede 1-2 — most games will be tight, low-scoring, and decided by a set piece or a transition moment. The team's biggest weakness is squad depth; a long tournament will stretch the veterans (Davis, Godoy) thin.
