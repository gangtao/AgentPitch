# Panama — Tactical Profile

## Identity & Philosophy
Panama's second-ever World Cup (first: Russia 2018). Under the Danish-Spanish manager **Thomas Christiansen**, Panama has matured from the wide-eyed debutants of 2018 into a tactically sophisticated, **mid-block counter-attacking** side that has consistently challenged Mexico and USA in CONCACAF qualifying. For the tournament Christiansen has leaned on a **back-three / wing-back** system — a **3-4-3** that morphs into a compact **5-4-1 / 5-2-3** block out of possession. Two clear identities: **compact mid-to-low block** without the ball, **direct counter** with it. The team is well-organized on set pieces (both ways), tactically disciplined, and built around veterans who have been together for the better part of a decade. Panama is the prototypical **smart underdog** — it will not beat itself, and it will punish a careless elite team.

**Matchday 1 update (17 June, vs Ghana — 0-1):** Panama opened Group L in Toronto and lost 1-0 to a 90+5' Caleb Yirenkyi tap-in, having defended doggedly for almost the entire match. Christiansen set up in a **3-4-3** (Mosquera; Ramos, Córdoba, Andrade; Murillo, Harvey, Bárcenas, Blackman; Martínez, Waterman, Rodríguez), prioritising a wing-back block and counters over Díaz's pace as the lone #9. Carlos Harvey was booked late in stoppage time (one yellow, no suspension); no other Panama cards, suspensions or injuries. For **Matchday 2 vs Croatia (23 June, BMO Field)** the most likely XI is unchanged from the Ghana side — the same 3-4-3 with the wing-back block — now a near must-win after the opener slipped away. Ismael Díaz (clinical finisher, the squad's primary penalty taker) and Aníbal Godoy (veteran pivot) are the chief high-impact options off the bench; Eric Davis (captain, 130+ caps) provides set-piece delivery from the bench.

## Formation
- Shape: **3-4-3** in possession — a back three, two wing-backs, a central pair, and a front three; **5-4-1 / 5-2-3** mid-to-low block out of possession (wing-backs drop to make a back five).
- Role mapping (roster order in `panama.yaml`):
  - index 0: GK — **Orlando Mosquera** — experienced shot-stopper; not a sweeper, stays on the goal line.
  - index 1: LCB — **Jiovany Ramos** — left of the back three; the line-holder drafted into the XI, disciplined and physical, not a ball-player.
  - index 2: CCB — **José Córdoba** (Norwich City) — physical young CB at the heart of the three; the aerial monitor and biggest defensive talent, organises the block.
  - index 3: RCB — **Andrés Andrade** — right of the back three; disciplined central defender, the cover man, steps across to shield Murillo's forward runs.
  - index 4: LWB — **César Blackman** — left wing-back; pacy up-and-down runner who provides the width on the left and tucks back to a back five out of possession.
  - index 5: CM — **Carlos Harvey** (Minnesota United) — left of the central pair; box-to-box engine, physical, comfortable carrying through midfield. Booked vs Ghana — one card in hand.
  - index 6: CM — **Yoel Bárcenas** — right of the central pair; the most technical midfielder, the press-breaker and tempo-setter who recycles and threads the diagonal to the wing-backs.
  - index 7: RWB — **Michael Amir Murillo** (Beşiktaş) — right wing-back; the team's pacy outlet and top-tier experience, the highest-volume attacking lane, bombs the right flank and drops into a back five when needed.
  - index 8: LW — **Cecilio Waterman** — left of the front three; pacy, physical, the transition outlet who runs the left channel and a secondary penalty taker.
  - index 9: CF — **Cristian Martínez** — central of the front three; energetic, tidy carrier who links the block to the counter and shuttles between the lines as the false-9 / link man.
  - index 10: RW — **José Luis Rodríguez** (FC Juárez) — right of the front three; quick dribbler (speed 15) who cuts inside from the right, the primary creator and direct free-kick taker.

## Style of Play

### Build-up
**Direct-leaning.** With a back three Panama is content to go long early against stronger opposition: Mosquera or a CB aims for Waterman / Martínez to hold and bring the wing-backs into play. Against weaker pressing, the back three splits, **Bárcenas drops to receive** between the lines as the press-breaker, and the wing-backs (Blackman, Murillo) push high to give width. Murillo's diagonal and the through-ball into the channel for Waterman are the go-to progressions.

### Pressing
**Mid-block first.** Panama does not high-press as a default; the front three sit around the halfway line. Trigger: opposition CB taking a heavy first touch or facing his own goal — Martínez curves the run, Waterman / Rodríguez jump the full-backs. The press is **trigger-based** and **selective** — never sustained. Christiansen's team is disciplined about energy management.

### Defensive shape
**Compact 5-4-1 / 5-2-3** out of possession: the wing-backs (Blackman, Murillo) drop to form a back five, Harvey and Bárcenas screen in front, and two of the front three tuck in while one stays high to spearhead the counter. The block is **mid-to-low** — Christiansen prefers to defend the edge of the 18-yard box and deny space in behind. The back three holds a moderate-to-low line; the offside trap is not a primary weapon. **Tactical fouling** in midfield is encouraged to break counter-attacks.

### Wide play
**Wing-back driven.** Width comes entirely from Blackman (LWB) and Murillo (RWB), with Murillo more adventurous. Waterman and Rodríguez can stay wide or drift into the half-spaces, opening lanes for the overlapping wing-backs. The right side (Murillo + Rodríguez) is the higher-volume attacking lane.

### Final third
Patterns: Murillo overlap to byline → low cross to the near post or Rodríguez at the edge of the box; Rodríguez cut-in shot from the right half-space; Bárcenas / Martínez through-ball to Waterman running the channel; a counter-break with Rodríguez and Murillo against an exposed back line. Panama's set pieces are a major weapon — Córdoba's aerial threat produces 30%+ of expected goals.

## Set Pieces
- **Set-piece organized both ways.** Christiansen drills the team relentlessly.
- Attacking corners: **Bárcenas** delivers (out-swinger from the left, in-swinger from the right); **Rodríguez** can take the opposite side. Primary aerial targets: Córdoba (penalty spot), Andrade (near post), Harvey (back post).
- Defending corners: **hybrid** — three zonal at the six-yard line, four man-markers (Córdoba on the most dangerous), two short-corner blockers.
- Free kicks: **Rodríguez** takes direct from any zone within 26 units; **Bárcenas** delivers wide free kicks.
- Penalties: **Waterman** primary on the pitch, **Rodríguez** secondary; **Díaz** (bench) is the squad's designated taker when on.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_6" (CM, jersey #17 — Bárcenas) and team_phase == "building_up":** Drop between the lines to receive as the press-breaker. Recycle short or thread the diagonal to a wing-back; do not force vertical under pressure.
2. **If my player_id ends with "_10" (RW, jersey #7 — Rodríguez) and I receive the ball between the lines:** Prefer a forward action — cut inside and Shoot, or a through-ball to CF "_9" (Martínez) / diagonal to RWB "_7" (Murillo) — over a recycle.
3. **If my role is MID/FWD and team_phase == "defending":** Drop to form a 5-4-1 — wing-backs LWB "_4" (Blackman) and RWB "_7" (Murillo) fall into a back five, LW "_8" (Waterman) and RW "_10" (Rodríguez) tuck alongside the central pair, CF "_9" (Martínez) stays high as the lone outlet.
4. **If my player_id ends with "_7" (RWB, jersey #23 — Murillo) and team_phase == "attacking":** Push to the byline aggressively. The right side is the chance-creation lane.
5. **If my player_id ends with "_4" (LWB, jersey #13 — Blackman) and team_phase == "attacking":** Push on selectively — provide the width when the LW (player_id ends with "_8" — Waterman) tucks into the half-space, but never both wing-backs high at once.
6. **If team has just won possession in our own third:** Vertical Pass to RW "_10" (Rodríguez) or directly to CF "_9" (Martínez) within 3 ticks — the counter is the primary scoring route.
7. **If my player_id ends with "_8" (LW, jersey #18 — Waterman) and team_phase == "transition_attack":** Sprint forward on the channel — speed 14, the team's vertical outlet.
8. **If my role is MID and opposition has the ball in our half:** Tighten to a compact block; tactical foul on the ball-carrier within 5 units of the centre circle is encouraged.
9. **If my player_id ends with "_2" (CCB, jersey #3 — Córdoba) and a cross is incoming:** Attack the first ball at the penalty spot. Do not get drawn to the near post.
10. **If team is leading by 1+ goals and minute > 75:** Drop the block 8 units deeper into a back five. Burn the clock by recycling possession in the corner via the wing-backs and CM "_6" (Bárcenas).
11. **If my player_id ends with "_8" (LW — Waterman) or "_10" (RW — Rodríguez) and I have the ball in the box:** Shoot — they are the on-pitch finishing threats (Waterman shoot 14).
12. **Set pieces / penalties:** defer to CM "_6" (Bárcenas, corner & wide FK delivery), RW "_10" (Rodríguez, direct FKs) and LW "_8" (Waterman, penalties).

## Key Player Notes
- **Jiovany Ramos (1):** Left of the back three, drafted in as the disciplined line-holder; physical, not a ball-player — keeps it simple and clears the danger.
- **José Córdoba (2):** Young CB on the rise (Norwich City) and the spine of the back three. Aerially dominant — the chief set-piece threat at both ends.
- **Carlos Harvey (5):** Box-to-box engine in the central pair; physical, carries through midfield. Booked vs Ghana — must avoid a second-tournament caution that risks a ban.
- **Yoel Bárcenas (6):** The technical heartbeat of the central pair — press-breaker, tempo-setter and corner/wide-FK deliverer with Carrasquilla on the bench.
- **Murillo (7):** Beşiktaş wing-back (ex-Marseille). The pacy outlet on the right, the squad's top-tier experience, and the highest-volume attacking lane.
- **Martínez (9):** The central link man / false-9 of the front three — energetic shuttler connecting the block to the counter.
- **Rodríguez (10):** The primary creator — speed 15, dribbling 14, cuts in from the right and takes direct free kicks.
- **Díaz (bench, alternative #9):** Clinical finisher (shoot 15) and the squad's designated penalty taker; a like-for-like change to add a pure box striker when chasing a game.
- **Godoy (bench):** Veteran pivot and the slow heartbeat — comes on to drop the tempo and control late leads under press.
- **Davis (bench):** Captain, 130+ caps; an experienced left-sided option and set-piece deliverer from the bench.
- **Carrasquilla (squad):** the usual chief creator and tempo-setter (Pumas UNAM) is carrying a groin/muscular injury from the Liga MX final — fit only for the bench, which pushes creation duties onto Bárcenas, Rodríguez and Martínez.

## Tournament Mindset
Panama under Christiansen is the **smart underdog**, having opened **Group L with a narrow 0-1 loss to Ghana** (June 17, 2026, Toronto) on a stoppage-time goal — a cruel result for a disciplined defensive display. The team has been together for a long time, knows its identity, and will not beat itself. With the opener lost, **Matchday 2 vs Croatia (June 23, BMO Field) is a near must-win** to keep round-of-16 hopes alive against the group's most technical side. Panama is the prototype CONCACAF block-and-counter team: compact in a back five, organized, set-piece dangerous, with one or two technical players (Rodríguez, Bárcenas) who can produce a moment of quality. Expect Panama to score 0-2 goals and concede 1-2 — tight, low-scoring, decided by a set piece or a transition moment. The biggest weakness is squad depth — sharpened by Carrasquilla's injury; a long tournament will stretch the veterans thin. Against Croatia, Panama will sit deep, deny space behind Modrić's passes, frustrate the rhythm, and hunt the win on a set piece or a Rodríguez/Murillo break.
