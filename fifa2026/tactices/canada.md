# Canada — Tactical Profile

## Identity & Philosophy
Co-hosts of the 2026 World Cup and the rising power of CONCACAF. After the underwhelming 2022 group-stage exit, the Canadian Soccer Association brought in **Jesse Marsch** — a Red Bull-tree disciple of Ralf Rangnick — to install a **vertical, high-intensity, transitional** identity that suits the squad's athletic profile better than the slower possession game it had tried. Marsch's Canada is the most physically aggressive team in CONCACAF: high press, sprint duels, second balls, and direct passing into Jonathan David's runs. The team is **less technically refined** than Mexico but more athletic and arguably more dangerous in transition.

**Group B Matchday 3 (24 June, vs Switzerland — BC Place, Vancouver):** Canada top Group B on 4 points with a **+6 goal difference** after a thumping **6-0 win over Qatar** — co-hosts now playing the group decider at home in Vancouver, level on points with Switzerland but ahead on GD (a draw likely tops the group). Two big personnel stories shape this XI. **Ismaël Koné is OUT for the tournament** — stretchered off with a broken leg against Qatar — and **Nathan Saliba** (a free-kick scorer in that same Qatar win) steps into central midfield. **Alphonso Davies is fit again** after his hamstring strain kept him out of the first two matches, but the medical staff are expected to **ease him in from the bench** rather than start him cold in a knockout-weight game; **Richie Laryea continues at LB**. At centre-back, **Moïse Bombito** — remarkably back to ~100% after a tibia injury, having played the second half against Qatar — pushes for a start, with both Cornelius and de Fougerolles also carrying yellow cards (a suspension risk Marsch may manage). Marsch keeps the team in the **4-4-2** that beat Qatar.

## Formation
- Shape: **4-4-2** — two flat banks of four with David and Larin paired up top; morphs into a **4-2-2-2** in the high press and a **4-4-2 mid-block** when the press is broken.
- Role mapping (roster order in `canada.yaml`):
  - index 0: GK — **Maxime Crépeau** — confirmed starter over St. Clair; agile shot-stopper, vocal organizer, willing to go long early.
  - index 1: LB — **Richie Laryea** — fast (speed 16), relentless engine (stamina 16); continues to deputize for Alphonso Davies, who is fit again but eased back from the bench. An honest overlapping fullback — direct sprint-and-cross, not the 1v1 superstar Davies is.
  - index 2: LCB — **Moïse Bombito** — powerful, recovering athlete (strength 16) back from a tibia injury; aggressive front-foot defender who steps into the press, the senior physical presence of the back line.
  - index 3: RCB — **Derek Cornelius** — disciplined line-holder and organizing CB; carries a yellow card so picks his moments to commit.
  - index 4: RB — **Alistair Johnston** — Canada's first-choice right-back (Celtic, captain-grade leader); overlaps or inverts based on game state, disciplined positioning and high stamina.
  - index 5: LM — **Ali Ahmed** — direct, hard-pressing left winger; pacy (speed 16) and high-energy, hugs the touchline early and attacks the back post late.
  - index 6: CM — **Nathan Saliba** — the new central midfielder in for the injured Koné; box-to-box runner, set-piece weapon (scored a free kick vs Qatar), the press's middle layer.
  - index 7: CM — **Stephen Eustáquio** — the technical anchor. The lone deep playmaker; Marsch lets him sit because the rest of the midfield is verticality-and-running.
  - index 8: RM — **Tajon Buchanan** — pacy wide threat as the right mid in the 4-4-2; tucks inside to combine, leaving the overlap lane to Johnston.
  - index 9: ST — **Jonathan David** — **captain** and the team's chief finisher; runs the channels, peels off shoulders, the movement-first #9 who drops into pockets but always finishes the move.
  - index 10: ST — **Cyle Larin** — physical target striker alongside David; aerial threat, occupies both CBs, the wall for David to play off.

## Style of Play

### Build-up
**Direct.** Marsch's Canada does not enjoy long possession sequences. Crépeau often goes long from the goal kick aiming at Larin's chest or into the channels for David. When building short, Eustáquio drops between the CBs to form a 3+1, the fullbacks (Laryea and Johnston) push on in turn — never both at once — and Saliba offers the vertical bounce pass. **Three-pass goals are the dream** — keeper to midfielder to David to goal.

### Pressing
**High press is the identity.** This is Canada's defining trait. The 4-4-2 gives Marsch a natural two-striker press: David and Larin split the CBs. Trigger #1: any back-pass to the GK — David sprints, Ahmed and Buchanan jump the fullbacks. Trigger #2: opposition CB receiving facing his own goal — David curves the run to block the back-pass, Saliba jumps. The press is **man-oriented** in all phases. Marsch wants the ball won in the opposition third **at all costs**, including bodily contact and tactical fouls — though against Switzerland's experienced Xhaka-Freuler pivot, with the midfield a man light after the Koné injury, Saliba must pick his pressing moments to avoid being outnumbered centrally.

### Defensive shape
When the press is broken, Canada drops into its base **4-4-2** with David alongside Larin. Ahmed and Buchanan retreat onto the fullbacks, and Laryea — a far more natural tracker than Davies — holds an honest LB line. The block is **mid-to-high**, never deep — Marsch refuses to invite pressure. Eustáquio shields while Saliba presses the half-spaces.

### Wide play
**Balanced — for once.** With Davies eased back from the bench, the famous lopsided-left identity is shelved at kickoff. The left is a conventional winger-fullback pairing: Ahmed holds the touchline, Laryea overlaps on the sprint when Ahmed cuts inside. On the right, Johnston overlaps Buchanan when Buchanan is wide, underlaps when Buchanan tucks inside. The danger comes from both flanks equally rather than one superstar channel — until Davies enters to weaponize the left.

### Final third
Patterns: long ball from Crépeau or Eustáquio into the channel for David's first-time touch; Larin pinning the CBs and flicking on for David's run; Buchanan running in behind onto a Eustáquio diagonal; Laryea sprinting the left touchline and crossing low across the six-yard box for the two strikers. Canada does not pattern-make in 15-pass build-ups — the goals come from 3-4 pass transitions.

## Set Pieces
- Attacking corners: **Eustáquio** delivers from both sides (technical 16 pass rating). Primary aerial targets: Larin (penalty spot), Bombito, Cornelius.
- Free kicks: **Eustáquio** delivers all wide free kicks; **Saliba** is a direct-attempt option from central range (free-kick scorer vs Qatar).
- Defending corners: **man-marking** with one zonal at the near post (Saliba). Bombito and Cornelius take the most dangerous opposing targets.
- Penalties: **David** primary, **Larin** secondary, **Eustáquio** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_1" (LB, jersey #22 — Laryea) and team_phase == "attacking" and the LM "_5" (Ahmed) has tucked inside:** Sprint the overlap down the left touchline — but recover immediately if possession is lost; no permanent winger licence.
2. **If my player_id ends with "_1" (LB, jersey #22 — Laryea) and team_phase == "defending" and the ball is on the right:** Hold a deeper LB position; do not push high.
3. **If my role is FWD and an opponent (CB/GK) has just received the ball:** Sprint to press within 6 units within 3 ticks — David and Larin split the two CBs.
4. **If my player_id ends with "_7" (CM, jersey #7 — Eustáquio) and I have the ball:** Prefer the long forward Pass (diagonal to RM "_8" Buchanan, through-ball to ST "_9" David) over the short recycle.
5. **If my player_id ends with "_9" (ST, jersey #10 — David) and team_phase == "transition_attack":** Sprint forward on the diagonal — Marsch's vertical philosophy requires the captain-striker to lead the break.
6. **If team has just won possession in the opposition third:** Vertical Pass to the nearest forward within 2 ticks. No recycle.
7. **If my role is GK (player_id ends with "_0" — Crépeau) and team has possession in our half:** Pass long to the target ST (player_id ends with "_10" — Larin) if pressed, short to CB if not. Avoid medium-range balls (turnover risk).
8. **If my role is MID and an opponent has the ball within 7 units in opposition half:** Tackle — but if my player_id ends with "_6" (CM — Saliba), only commit when cover exists; the midfield is a man light, so do not get dragged out of the central screen.
9. **If my player_id ends with "_8" (RM, jersey #17 — Buchanan) and the RB "_4" (Johnston) is overlapping:** Tuck inside as a narrow second-line attacker between the lines.
10. **If team is leading by 1+ goals and minute > 80:** Drop into 4-5-1 ("_10" Larin drops to midfield); kill the game with a compact block — a draw or win tops Group B.
11. **If my player_id ends with "_4" (RB, jersey #2 — Johnston) and the LB (player_id ends with "_1" — Laryea) has pushed forward on the overlap:** stay home and tuck toward the centre — the back line never loses both fullbacks at once.
12. **Set pieces in attacking third / penalties:** defer to ST "_9" (David, penalties), CM "_7" (Eustáquio, all delivery and wide FKs); CM "_6" (Saliba) takes central direct free kicks.

## Key Player Notes
- **David (9):** Captain, primary finisher and penalty taker. Shoot rating 17 — the team's most clinical attacker. License to drop into pockets but always finishes the move.
- **Eustáquio (7):** The lone deep playmaker. The team's pass rating leader (16) — he is the only player tasked with long-range diagonal distribution and wide dead-ball delivery.
- **Saliba (6):** Koné's replacement in central midfield after the broken-leg injury. A box-to-box runner and free-kick threat (scored vs Qatar) who must balance the press with shielding a midfield that is now a man light.
- **Bombito (2):** Powerhouse centre-back (strength 16) back to near-full fitness after a tibia injury; steps into the front-foot press and is a major aerial threat at attacking set pieces.
- **Larin (10):** Target striker alongside David. Strength 15, shoot 14 — pins the CBs, wins the first ball, and frees David's channel runs.
- **Davies (bench):** Fit again after a hamstring strain but eased back from the bench; when he enters at LB he transforms the left into the lopsided superstar channel and is Canada's most dangerous transition runner.

## Tournament Mindset
Canada under Marsch is the **most physically aggressive** team in the tournament. The press, the sprint duels, the tactical fouling — it is a Red Bull team in a Canada shirt. Having already secured passage with the 6-0 demolition of Qatar, Canada arrive at the Switzerland decider needing only a draw to top Group B — but as co-hosts at a packed BC Place they will chase the win. The chief worries are the **thinner-than-ideal midfield** after Koné's tournament-ending injury (Saliba must hold a man-light centre against Xhaka and Freuler) and **stamina management** — Marsch's press demands 90-minute intensity. Expect Canada to score in transition through David and Larin, ride the home crowd, and either win the group outright or grind out the draw that does the same.
