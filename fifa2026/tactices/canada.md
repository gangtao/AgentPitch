# Canada — Tactical Profile

## Identity & Philosophy
Co-hosts of the 2026 World Cup and the rising power of CONCACAF. After the underwhelming 2022 group-stage exit, the Canadian Soccer Association brought in **Jesse Marsch** — a Red Bull-tree disciple of Ralf Rangnick — to install a **vertical, high-intensity, transitional** identity that suits the squad's athletic profile better than the slower possession game it had tried. Marsch's Canada is the most physically aggressive team in CONCACAF: high press, sprint duels, second balls, and direct passing into Jonathan David's runs. The team is **less technically refined** than Mexico but more athletic and arguably more dangerous in transition. As co-hosts with home crowds in Toronto and Vancouver, Canada targets the round of 16 minimum.

## Formation
- Shape: **4-3-3** primarily; **3-4-3** in possession when Davies advances and Johnston inverts; **4-4-2 mid-block** when the press is broken.
- Role mapping (roster order in `canada.yaml`):
  - index 0: GK — **Dayne St. Clair** — modern shot-stopper, good with feet, comfortable as the sweeper-keeper for a high line.
  - index 1: LB/LWB — **Alphonso Davies** — the team's superstar. Plays as an attacking LB but in possession effectively a LW; the rocket-fast carrier who can beat any opponent 1v1 over 30 yards.
  - index 2: LCB — **Moïse Bombito** — physical, fast, the recovery defender behind Davies' adventures.
  - index 3: RCB — **Derek Cornelius** — disciplined, line-holder, the steadier of the two CBs.
  - index 4: RB — **Alistair Johnston** — Canada's first-choice right-back (Celtic, captain-grade leader); overlaps or inverts based on game state and balances Davies' adventures with disciplined positioning and high stamina.
  - index 5: CM/8 — **Ismaël Koné** — physical box-to-box midfielder; the press's middle layer.
  - index 6: DM/6 — **Stephen Eustáquio** — the technical anchor. The lone deep playmaker; Marsch lets him sit deep because the rest of the midfield is verticality-and-running.
  - index 7: CM/8 — **Ali Ahmed** — energetic shuttler, presses high, late runner; complements Koné and Eustáquio.
  - index 8: LW/RW — **Tajon Buchanan** — pacy wide forward; can play on either flank, prefers RW so Davies provides the left width.
  - index 9: CF — **Jonathan David** — the team's chief finisher; runs the channels, peels off shoulders, the false-9-ish #9 who drops into pockets but always finishes the move.
  - index 10: RW/CF — **Cyle Larin** — physical target striker, the alternative #9 to David; comes on for second-phase aerial threat.

## Style of Play

### Build-up
**Direct.** Marsch's Canada does not enjoy long possession sequences. St. Clair often goes long from the goal kick aiming at David or into the channels for Buchanan. When building short, Eustáquio drops between the CBs to form a 3+1, Davies pushes very high (effectively a LW), and Johnston inverts to cover. **Three-pass goals are the dream** — keeper to midfielder to David to goal.

### Pressing
**High press is the identity.** This is Canada's defining trait. Trigger #1: any back-pass to the GK — David sprints, Buchanan and Ahmed jump the fullbacks. Trigger #2: opposition CB receiving facing his own goal — David curves the run to block the back-pass, Koné jumps. The press is **man-oriented** in all phases. Marsch wants the ball won in the opposition third **at all costs**, including bodily contact and tactical fouls.

### Defensive shape
When the press is broken, Canada drops into a **4-4-2** with David alongside Buchanan or Larin. Davies tucks back to LB (his secondary discipline is **the** tactical question — when does he track back?). The block is **mid-to-high**, never deep — Marsch refuses to invite pressure. Eustáquio shields, the two #8s (Koné, Ahmed) press the half-spaces.

### Wide play
**Asymmetric and lopsided to the left**: Davies-Davies-Davies. He is the width on the left because Buchanan plays as a narrow #10 / RW. On the right, Johnston overlaps Buchanan when Buchanan is wide, underlaps when Buchanan tucks inside. The right side is largely a counterweight to free Davies on the left.

### Final third
Patterns: long ball from St. Clair or Eustáquio into the channel for David's first-time touch; Davies sprinting 40 units down the left and crossing low across the six-yard box; Buchanan running in behind onto a Eustáquio diagonal; counter-attack with David receiving the press-turnover and slipping Davies in behind. Canada does not pattern-make in 15-pass build-ups — the goals come from 3-4 pass transitions.

## Set Pieces
- Attacking corners: **Eustáquio** delivers from both sides (technical 16 pass rating). Primary aerial targets: Bombito, Cornelius, Larin (penalty spot).
- Defending corners: **man-marking** with one zonal at the near post (Koné). Bombito takes the most dangerous opposing target.
- Free kicks: **Eustáquio** delivers all wide free kicks; **Davies** takes direct from the left half-space.
- Penalties: **David** primary, **Davies** secondary, **Eustáquio** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_1" (LB, jersey #19 — Davies) and team_phase == "attacking":** Sprint forward — assume LW position. Do not wait for the ball; arrive at the byline by the time the ball reaches the final third.
2. **If my player_id ends with "_1" (LB, jersey #19 — Davies) and team_phase == "defending" and the ball is on the right:** Hold a deeper LB position; do not push high.
3. **If my role is FWD and an opponent (CB/GK) has just received the ball:** Sprint to press within 6 units within 3 ticks.
4. **If my player_id ends with "_6" (DM, jersey #7 — Eustáquio) and I have the ball:** Prefer the long forward Pass (diagonal to LB "_1" Davies, through-ball to CF "_9" David) over the short recycle.
5. **If my player_id ends with "_9" (CF, jersey #10 — David) and team_phase == "transition_attack":** Sprint forward on the diagonal — Marsch's vertical philosophy requires the CF to lead the break.
6. **If team has just won possession in the opposition third:** Vertical Pass to the nearest forward within 2 ticks. No recycle.
7. **If my role is GK (player_id ends with "_0" — St. Clair) and team has possession in our half:** Pass long to the CF (player_id ends with "_9" — David) if pressed, short to CB if not. Avoid medium-range balls (turnover risk).
8. **If my role is MID and an opponent has the ball within 7 units in opposition half:** Tackle — including with a tactical foul if necessary.
9. **If my player_id ends with "_8" (jersey #17 — Buchanan) and the LB (player_id ends with "_1" — Davies) is bombing forward:** Tuck inside as a narrow RW to create the back-three shape (3-4-3 in possession).
10. **If team is leading by 1+ goals and minute > 80:** Drop into 5-3-2 (LB "_1" Davies drops, "_8" Buchanan drops to RM); kill the game with deep block.
11. **If my player_id ends with "_4" (RB, jersey #2 — Johnston) and the LB (player_id ends with "_1" — Davies) has the ball at the LB position:** invert into central midfield to cover the DM (player_id ends with "_6" — Eustáquio).
12. **Set pieces in attacking third / penalties:** defer to CF "_9" (David, penalties), DM "_6" (Eustáquio, delivery), LB "_1" (Davies, direct FKs left side).

## Key Player Notes
- **Davies (1):** The team's superstar. Listed as DEF but effectively a LW. Speed 19, dribbling 17. Marsch's entire left side is constructed to free him.
- **David (9):** Primary finisher and penalty taker. Shoot rating 17 — the team's most clinical attacker. License to drop into pockets but always finishes the move.
- **Eustáquio (6):** The lone deep playmaker. The team's pass rating leader (16) — he is the only player tasked with long-range diagonal distribution.
- **Buchanan (8):** Pacy hybrid; flexible between RW and the second-striker role.
- **Bombito (2):** Recovery defender behind Davies. Speed 14, strength 16 — the cover when Davies' raids leave the LB position empty.

## Tournament Mindset
Canada under Marsch is the **most physically aggressive** team in the tournament. The press, the sprint duels, the tactical fouling — it is a Red Bull team in a Canada shirt. The ceiling is the quarter-finals (a stretch); the floor is the group stage but Canada **will** be the most uncomfortable opponent for any team that wants to play out from the back. Stamina management is the open question — Marsch's press requires 90-minute intensity, and the bench depth is thinner than the European elite. Expect Canada to score in transition and to either win 2-1 or lose 3-2.
