# Panama — Tactical Profile

## Identity & Philosophy
Panama's second-ever World Cup (first: Russia 2018). Under the Danish-Spanish manager **Thomas Christiansen**, Panama has matured from the wide-eyed debutants of 2018 into a tactically sophisticated, **mid-block counter-attacking** side that has consistently challenged Mexico and USA in CONCACAF qualifying. For the tournament Christiansen has switched to a **3-4-2-1** — a back three with wing-backs — keeping the two clear identities: **compact mid-block** without the ball, **direct counter** with it. The team is well-organized on set pieces (both ways), tactically disciplined, and full of veterans who have been together for the better part of a decade. Panama is the prototypical **smart underdog** — it will not beat itself, and it will punish a careless elite team.

## Formation
- Shape: **3-4-2-1** in possession — back three, two wing-backs, double pivot, two attacking mids behind a lone #9; **5-4-1** mid-block out of possession.
- Role mapping (roster order in `panama.yaml`):
  - index 0: GK — **Orlando Mosquera** — experienced shot-stopper; not a sweeper, stays on the goal line.
  - index 1: LCB — **José Córdoba** — physical young CB; the aerial monitor and biggest defensive talent.
  - index 2: CCB — **Andrés Andrade** — disciplined central CB of the three, the line-holder; not a ball player.
  - index 3: RCB — **Carlos Harvey** — converted from midfield into the right of the back three; physical, comfortable stepping out with the ball.
  - index 4: LWB — **Eric Davis** — veteran captain (over 130 caps), the team's emotional and tactical anchor. Disciplined left wing-back; provides the width, never gets caught out of position.
  - index 5: CM — **Cristian Martínez** — energetic pivot partner; tidy carrier, shuttles box-to-box.
  - index 6: CM/6 — **Aníbal Godoy** — veteran holding midfielder, the press-breaker; sits in front of the back three, recycles short, the slow heartbeat.
  - index 7: RWB — **Michael Amir Murillo** — adventurous right wing-back (Marseille); the team's pacy outlet on the right.
  - index 8: LAM/SS — **Cecilio Waterman** — left of the two behind the striker; pacy, physical, the transition outlet who runs the channels.
  - index 9: ST — **Ismael Díaz** — the lone #9 and clinical finisher (shoot 15).
  - index 10: RAM — **José Luis Rodríguez** — right of the two; quick dribbler (speed 15) who cuts inside, the secondary creator.

## Style of Play

### Build-up
**Mixed.** Panama is comfortable with short build-up against weaker opposition: the back three splits wide, Godoy drops in to form a 3+1, the wing-backs push high, Rodríguez and Waterman operate between the lines. Against pressing opposition, Mosquera goes long aiming at Díaz or into the channel for Murillo's run. **Godoy is the press-breaker** — receive between the lines, find the diagonal to Murillo or the through-ball to Waterman.

### Pressing
**Mid-block first.** Panama does not high-press as a default; the front three sits at the halfway line. Trigger: opposition CB taking a heavy first touch or facing his own goal — Díaz curves the run, Waterman / Rodríguez jump the fullbacks. The press is **trigger-based** and **selective** — never sustained. Christiansen's team is disciplined about energy management.

### Defensive shape
**Compact 5-4-1** out of possession: Davis and Murillo drop alongside the back three, Martínez and Godoy hold the middle, Waterman and Rodríguez tuck in to form a flat midfield four. The block is **mid-to-low** — Christiansen prefers to defend the edge of the 18-yard box. The back three holds a moderate-to-low line; the offside trap is not a primary weapon. **Tactical fouling** in midfield is encouraged to break counter-attacks.

### Wide play
**Wing-back driven.** All the width comes from Davis (LWB) and Murillo (RWB), with Murillo more adventurous. Waterman and Rodríguez stay in the half-spaces, opening the wide lanes for the wing-backs. The right side (Murillo + Rodríguez) is the higher-volume attacking lane.

### Final third
Patterns: Murillo overlap to byline → low cross to Díaz near post or Rodríguez at the edge of the box; Rodríguez cut-in shot from the right half-space; Godoy through-ball to Waterman running the channel; Díaz one-on-one finish inside the box. Panama's set pieces are a major weapon — Davis's deliveries and Córdoba's aerial threat produce 30%+ of expected goals.

## Set Pieces
- **Set-piece organized both ways.** Christiansen drills the team relentlessly.
- Attacking corners: **Davis** delivers from both sides (out-swinger from the left, in-swinger from the right). Primary aerial targets: Córdoba (penalty spot), Andrade (near post), Harvey (back post).
- Defending corners: **hybrid** — three zonal at the six-yard line, four man-markers (Córdoba on the most dangerous), two short-corner blockers.
- Free kicks: **Rodríguez** takes direct from any zone within 26 units; **Davis** delivers wide free kicks on the left.
- Penalties: **Díaz** primary, **Waterman** secondary, **Rodríguez** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_6" (CM/6, jersey #20 — Godoy) and team_phase == "building_up":** Drop in front of the back three to form a 3+1. Recycle short, do not force vertical.
2. **If my player_id ends with "_10" (RAM, jersey #7 — Rodríguez) and I receive the ball between the lines:** Prefer a forward Pass (through-ball to ST "_9" Díaz or diagonal to RWB "_7" Murillo) over a recycle.
3. **If my role is FWD and team_phase == "defending":** Drop to form a 5-4-1 (LAM "_8" Waterman to LM, RAM "_10" Rodríguez to RM, ST "_9" Díaz stays high).
4. **If my player_id ends with "_7" (RWB, jersey #23 — Murillo) and team_phase == "attacking":** Push to the byline aggressively. The right side is the chance-creation lane.
5. **If my player_id ends with "_4" (LWB, jersey #15 — Davis) and team_phase == "attacking":** Push on selectively — provide the width when the LAM (player_id ends with "_8" — Waterman) tucks into the half-space, but never both wing-backs high at once.
6. **If team has just won possession in our own third:** Vertical Pass to RAM "_10" (Rodríguez) or directly to a forward within 3 ticks.
7. **If my player_id ends with "_8" (LAM, jersey #18 — Waterman) and team_phase == "transition_attack":** Sprint forward on the channel — speed 14, the team's vertical outlet.
8. **If my role is MID and opposition has the ball in our half:** Tighten to compact 5-4-1; tactical foul on the ball-carrier within 5 units of the centre circle is encouraged.
9. **If my player_id ends with "_1" (LCB, jersey #3 — Córdoba) and a cross is incoming:** Attack the first ball at the penalty spot. Do not get drawn to the near post.
10. **If team is leading by 1+ goals and minute > 75:** Drop the block 8 units deeper. Burn the clock by recycling possession in the corner via LWB "_4" (Davis) and CM "_6" (Godoy).
11. **If my player_id ends with "_9" (ST, jersey #10 — Díaz) and I have the ball in the box:** Shoot — clinical finishing is the priority (shoot rating 15).
12. **Set pieces / penalties:** defer to LWB "_4" (Davis, corner and wide FK delivery), RAM "_10" (Rodríguez, direct FKs) and ST "_9" (Díaz, penalties).

## Key Player Notes
- **Eric Davis (4):** Captain. Over 130 caps. The team's emotional and tactical anchor, now at left wing-back; set-piece deliveries.
- **Rodríguez (10):** The secondary creator stepping up with Carrasquilla out — speed 15, dribbling 14, cuts in from the right of the two.
- **Córdoba (1):** Young CB on the rise (Levski Sofia / Ligue 1 watch). Aerially dominant.
- **Murillo (7):** Marseille fullback, now right wing-back. The pacy attacking outlet on the right.
- **Díaz (9):** The lone #9. Primary penalty taker, clinical finisher. Shoot rating 15.
- **Godoy (6):** Veteran pivot. The slow heartbeat — drops the tempo when needed, recycles under press.
- **Waterman (8):** The transition outlet off the left of the two. Speed 14, strength 13. Runs the channels.
- **Carrasquilla (squad, not starting):** the usual chief creator is carrying a groin injury — fit only for the bench, which pushes creation duties onto Rodríguez and Godoy.

## Tournament Mindset
Panama under Christiansen is the **smart underdog**. The team has been together for a long time, knows its identity, and will not beat itself. The realistic objective is the **round of 16** — a stretch but achievable depending on draw. Panama is the prototype CONCACAF mid-block counter team: compact, organized, set-piece dangerous, with one or two technical players (Rodríguez, Díaz) who can produce a moment of quality. Expect Panama to score 1-2 goals per match and concede 1-2 — most games will be tight, low-scoring, and decided by a set piece or a transition moment. The team's biggest weakness is squad depth — sharpened by Carrasquilla's groin injury; a long tournament will stretch the veterans (Davis, Godoy) thin.
