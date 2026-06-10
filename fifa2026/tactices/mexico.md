# Mexico — Tactical Profile

## Identity & Philosophy
Co-hosts of the 2026 World Cup and the most-supported team in CONCACAF. Returning veteran **Javier Aguirre** ("El Vasco") was brought back to steady a team that had lost its identity after disastrous Copa Américas. Aguirre's Mexico is **possession-based but pragmatic**: technically excellent in midfield, comfortable building from the back, but with the defensive discipline and tactical fouling of a manager who learned in Spain. The team plays a narrow 4-3-3 that funnels the ball through the half-spaces, leans on Edson Álvarez as the defensive anchor, and looks to release the wide forwards on the counter. As co-hosts, Mexico has the loudest crowd at the Azteca and the highest baseline expectation — anything short of the quarter-finals will be considered failure.

## Formation
- Shape: **4-3-3** with a narrow midfield (the three CMs are tight); compresses to **4-1-4-1** out of possession with Álvarez shielding.
- Role mapping (roster order in `mexico.yaml`):
  - index 0: GK — **Raúl Rangel** (#1) — first-choice shot-stopper, having beaten out the veteran Ochoa (squad presence only); good with feet for short build-up, not a sweeper.
  - index 1: LB — **Jesús Gallardo** (#23) — experienced overlapping fullback; provides natural width on the left because the LW cuts inside.
  - index 2: LCB — **Johan Vásquez** (#5) — ball-playing CB, comfortable carrying out, the primary progressor from the back.
  - index 3: RCB — **César Montes** (#3) — physical, aerially dominant, the back-line enforcer; not a ball player.
  - index 4: RB — **Israel Reyes** (#15) — disciplined two-way right back; positionally sound first, picks his moments to overlap behind the RW.
  - index 5: CM/8/10 — **Gilberto Mora** (#19) — the young #10 operating from the left interior, the team's chief creator from midfield; gets between the lines, slips passes into the forwards.
  - index 6: DM/6 — **Edson Álvarez** (#4) — defensive anchor and captain; the holding midfielder who covers the entire width of the pitch, tackles 1v1, and starts short attacks.
  - index 7: CM/8 — **Álvaro Fidalgo** (#8) — the right-sided #8; Spain-schooled ball-circulation metronome (pass 17), sets the tempo between Álvarez and Mora.
  - index 8: LW — **Julián Quiñones** (#16) — mobile, in-form goalscorer (33 goals this season); cuts inside off the left, runs in behind, and can rotate with Jiménez.
  - index 9: CF — **Raúl Jiménez** (#9) — physical, hold-up #9, target man for crosses and second balls; the veteran centre-forward.
  - index 10: RW — **Roberto Alvarado** (#25) — "El Piojo"; tricky, two-footed dribbler (dribbling 16), direct off the right, the wide spark on the counter.

## Style of Play

### Build-up
**Patient short build-up.** Rangel splits the CBs wide, Álvarez drops between them to form a 3+1, Gallardo and Reyes push high to give width. **Vásquez is the primary progressor** — he carries forward into midfield with the ball at his feet. Mexico is comfortable in long possession sequences (15+ passes), waiting for the opposition press to fatigue before going vertical. When pressed hard, the first option is back to Rangel, then a switch to the opposite fullback.

### Pressing
**Mid-block first, selective high press.** Trigger: opposition CB taking a heavy first touch — Jiménez and Quiñones squeeze, Mora jumps into midfield. The press is **possession-oriented** rather than chaos-oriented — Mexico wants to win the ball back to play, not just disrupt. Álvarez does not press; he sits in front of the back four as the safety net.

### Defensive shape
Compact **4-1-4-1** with Álvarez as the single pivot. The two #8s (Mora, Fidalgo) drop to form a flat midfield four with Quiñones and Alvarado (or Jiménez dropping). The block is **mid-to-low**, conservative — Aguirre is happy to absorb pressure and counter through Quiñones and Alvarado. **Tactical fouling** is encouraged: a yellow card to break a counter-attack on Álvarez or Fidalgo is a feature, not a failure.

### Wide play
Asymmetric. **Left** = Quiñones inside + Gallardo overlap; this is where Mexico's chance creation happens via cut-backs from the byline. **Right** = Reyes overlap + Alvarado wide-and-inside hybrid. Mora drifts to the left half-space to combine with Quiñones-Gallardo.

### Final third
Patterns: Quiñones cut-back from the left byline to Mora arriving at the top of the box; Mora through-ball to Jiménez peeling off the LCB's shoulder; Alvarado running the channel between LB and LCB onto a Vásquez diagonal; switch of play from Álvarez to Reyes isolating the opposition LB. Mexico will also drop second balls into Jiménez and play off his knock-downs.

## Set Pieces
- **Set-piece danger team.** Aguirre's Mexico is among the best in CONCACAF on dead balls.
- Attacking corners: **Mora** delivers from the right (in-swinger), **Fidalgo** from the left (in-swinger). Primary aerial targets: Montes (front post), Jiménez (penalty spot), Vásquez (back post).
- Defending corners: **man-marking** with two zonal at the front post. Montes takes the most dangerous opposing target.
- Free kicks: **Mora** takes direct from any zone within 28 units; **Fidalgo** delivers wide free kicks.
- Penalties: **Jiménez** primary, **Quiñones** secondary, **Mora** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_6" (DM, jersey #4 — Álvarez) and the opposition has the ball within 10 units of the centre circle:** Move to intercept the passing lane to the opposition #10. Tackle if within 5 units.
2. **If my player_id ends with "_8" (LW, jersey #16 — Quiñones) and team_phase == "transition_attack":** Sprint forward on the diagonal cutting inside — the through-ball or shot is the priority over wide play.
3. **If my player_id ends with "_2" (LCB, jersey #5 — Vásquez) and team_phase == "building_up" and no opponent within 8 units:** Carry the ball forward into midfield. Do not pass short.
4. **If my role is GK (player_id ends with "_0" — Rangel) and team_phase == "building_up":** Pass short to the nearest unmarked CB. Avoid long balls unless press intensity is high.
5. **If my player_id ends with "_5" (CM, jersey #19 — Mora) and I receive the ball between the lines:** Prefer a forward through-ball Pass to a forward running in behind (CF "_9" Jiménez or LW "_8" Quiñones) over a recycle.
6. **If team_phase == "defending" and the opposition counter-attacks:** Nearest midfielder commits a tactical foul (Tackle) on the ball-carrier within 5 units of the centre circle.
7. **If my player_id ends with "_9" (CF, jersey #9 — Jiménez) and a teammate delivers a cross:** attack the penalty spot or back post — not the near post.
8. **If my player_id ends with "_1" (LB, jersey #23 — Gallardo) and team_phase == "attacking" and the LW (player_id ends with "_8") has the ball inside:** Sprint forward and outside the LW (overlap to byline).
9. **If my role is MID and team has held possession > 30 seconds:** keep circulating the ball — patience over verticality unless a clear through-ball is available.
10. **If team is leading by 1+ goals and minute > 75:** Compress the block. The DM (player_id ends with "_6") drops between the CBs to form a 5-3-1 if needed. Tactical fouling intensifies.
11. **If my player_id ends with "_10" (RW, jersey #25 — Alvarado) and the ball is on the left:** make a blindside run between LB and LCB.
12. **Set pieces / penalties / direct free kicks within 28 units:** defer to the CM (player_id ends with "_5" — Mora) for creation and the CF (player_id ends with "_9" — Jiménez) for penalties.

## Key Player Notes
- **Edson Álvarez (index 6, #4):** Captain, defensive anchor, tackle leader — fully recovered from spring ankle surgery. The most important player tactically — his discipline (17) and stamina (17) allow him to cover for both fullbacks pushing up.
- **Quiñones (index 8, #16):** In-form goalscorer (33 goals this season); the team's primary counter-attack outlet from the left, rotates with Jiménez, secondary penalty taker.
- **Mora (index 5, #19):** The 17-year-old creator. The team's chief creator from open play and primary set-piece deliverer.
- **Fidalgo (index 7, #8):** The metronome. Best passer in the team (pass 17); recycles possession and dictates when Mexico goes vertical.
- **Vásquez (index 2, #5):** The ball-playing CB. Licensed to carry into midfield.
- **Jiménez (index 9, #9):** Target man and primary penalty taker. Wins the aerial duels that set up second-phase attacks.
- **Alvarado (index 10, #25):** The wide spark on the right. Dribbling 16, two-footed; isolates the opposition LB and feeds cut-backs.

## Tournament Mindset
Mexico carries the largest crowd in tournament history at the Azteca and the most fervent expectation in CONCACAF. Aguirre will play pragmatically — Mexico will not be drawn into open shoot-outs with the European elite. Expect controlled possession, mid-block defending, tactical fouling, and one or two moments of brilliance from Mora or Quiñones per game. Mexico's ceiling is the quarter-finals; the floor (and disaster scenario) is the round of 16. Set-piece goals will be a key route to victory.
