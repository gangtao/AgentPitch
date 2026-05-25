# United States — Tactical Profile

## Identity & Philosophy
Co-hosts of the 2026 World Cup and the most-watched USMNT in history. Under **Mauricio Pochettino**, the United States have abandoned the slow, possession-curious experiments of the post-Berhalter era and embraced the manager's identifiable Tottenham/PSG DNA: aggressive, energetic, vertically minded football played by a young, athletic, European-based core. Pochettino's USMNT presses with the door slammed shut behind the press, transitions in 4-5 passes, and tries to **get in the opponent's face** for 90 minutes. Pragmatism wins out — if the home crowd demands a result, the USA will sit 5cm deeper and counter rather than chase the ball. The expectation, as co-hosts, is the round of 16 minimum, with a realistic shot at the quarter-finals.

## Formation
- Shape: **4-3-3** in possession; **4-4-2 mid-block** without the ball with Pulisic tucking alongside Balogun.
- Role mapping (roster order in `usa.yaml`):
  - index 0: GK — **Matt Freese** — competent shot-stopper, modest distribution. Stays near the goal line, no sweeping ambition.
  - index 1: LB — **Antonee Robinson** — overlapping attacking fullback, Pulisic's underlap partner; the engine of the left side, recovers any deficit with sheer pace and stamina.
  - index 2: LCB — **Chris Richards** — front-foot stepper, athletic, the primary aerial monitor of the back four.
  - index 3: RCB — **Cameron Carter-Vickers** — old-school stopper, prefers to drop and defend the box rather than carry forward.
  - index 4: RB — **Sergiño Dest** — inverted/attacking fullback, technical, drifts into midfield in build-up to free Tillman to push wide.
  - index 5: DM/6 — **Tyler Adams** — ball-winning anchor, all-action presser, the leader of the press triggers; protects the back four and recycles short.
  - index 6: CM/8 — **Tanner Tessmann** — physical, disciplined #8, the line-holder between Adams and McKennie; reads counter-attacks.
  - index 7: CM/8 — **Weston McKennie** — box-to-box engine, late runner into the box, the team's best aerial threat from midfield.
  - index 8: LW — **Christian Pulisic** — inside-forward, the team's chief creator; cuts inside off the left to combine or shoot. Captain and primary set-piece taker.
  - index 9: CF — **Folarin Balogun** — pressing forward, runs the channels, holds up balls into feet, the focal point of attack.
  - index 10: RW — **Malik Tillman** — wide-and-inside hybrid; can play as a #10 if McKennie shifts wide, mostly drifts inside off the right to overload the half-spaces.

## Style of Play

### Build-up
Short build-up from the back when possible: CBs split wide, Adams drops between them to form a 3+1, Dest inverts into midfield to create a midfield diamond with Tessmann/McKennie/Adams. Robinson stays high and wide on the left because Pulisic is tucking inside. When the press is intense, Pochettino has no qualms about going long to Balogun — second-ball wins around the halfway line are a feature, not a fallback. Adams is the orchestrator at the base; McKennie connects the half-spaces.

### Pressing
**High press is the identity.** Trigger #1: opposition GK receiving a back-pass — Balogun curves his run, Pulisic and Tillman jump the fullbacks, Adams steps into the #6 space. Trigger #2: a heavy first touch from any opposition midfielder — the nearest USA player (often McKennie) sprints to engage within 6 units. The press is **man-oriented** in the front six, **zonal** in the back four. The whole side is fit, stamina rated 14+ across the spine, and Pochettino expects 90-minute intensity.

### Defensive shape
When the press is broken, the USA drop into a compact **4-4-2** with Pulisic alongside Balogun nominally and Tillman dropping to RM. The block is **mid-height** (around the halfway line) rather than deep — Pochettino refuses to invite pressure. Carter-Vickers and Richards hold a moderately high line; Adams shields the channel in front of them. Robinson and Dest tuck narrow without the ball.

### Wide play
Asymmetric: **left** = Pulisic inside + Robinson overlap (the main creation channel — Robinson reaches the byline, Pulisic shoots from the half-space). **Right** = Tillman inside + Dest underlap. McKennie is the late runner who arrives at the back post on cut-backs.

### Final third
Patterns: Pulisic-Robinson 1-2 down the left ending in a Robinson cut-back; Pulisic cutting inside onto his right foot for a curling shot from 22 units; Balogun running the channel between RB and RCB onto a Tillman through-ball; McKennie late arriving on a corner or a deflected ball in the six-yard box. Direct counter-attack from a press turnover: Adams wins it → vertical pass to Pulisic → Pulisic-Balogun in 3 passes.

## Set Pieces
- Attacking corners: **Pulisic** delivers from both sides (in-swinger from the right, out-swinger from the left). Primary aerial targets: McKennie, Richards, Carter-Vickers at the near post.
- Defending corners: **hybrid** — three zonal markers on the six-yard line, four man-markers (one each on the most dangerous attackers), two short-corner blockers. Adams takes the front-post zonal slot.
- Free kicks: **Pulisic** takes direct from any zone within 28 units. McKennie delivers wide free kicks into the box.
- Penalties: **Pulisic** primary, **Balogun** secondary, **McKennie** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_8" (LW, jersey #10 — Pulisic) and I receive the ball wide on the left:** cut inside on my right foot. If a teammate (the LB, player_id ends with "_1") is overlapping outside me, prefer a 1-2 Pass; else dribble to the half-space and Shoot if angle < 30° and distance < 24.
2. **If my player_id ends with "_5" (DM, jersey #4 — Adams) and an opponent has the ball within 8 units in central midfield:** Tackle immediately. Do not hesitate.
3. **If my player_id ends with "_1" (LB, jersey #5 — Robinson) and team_phase == "attacking":** Sprint forward to the opposition byline. The overlap is automatic — even at low stamina.
4. **If my player_id ends with "_4" (RB, jersey #2 — Dest) and team_phase == "building_up":** Move inside to the right half-space (invert) — sit ~6 units to the right of the DM (player_id ends with "_5").
5. **If my role is FWD and team has just won possession in our own half:** Sprint forward on a vertical line — counter-attack in 3-4 passes is the default.
6. **If team_phase == "defending" and player_id ends with "_8" (LW) is alongside player_id ends with "_9" (CF) (LW becomes nominal ST):** drop to LM only when the ball is on the LW's side; otherwise stay as a second striker for the counter.
7. **If my role is GK (player_id ends with "_0" — Freese):** stay on the goal line unless ball > 40 units away. Avoid sweeping — distribution is short to nearest CB.
8. **If my player_id ends with "_9" (CF, jersey #9 — Balogun) and the opposition CB takes a heavy first touch (ball > 3 units from feet):** Sprint to press; curve the run to cut the deeper CB.
9. **If my player_id ends with "_7" (CM, jersey #8 — McKennie) and a teammate is delivering a cross into the box:** Sprint into the box, target the back post.
10. **If my player_id ends with "_3" (RCB, jersey #15 — Carter-Vickers) and team has possession in opposition half:** Hold position at the halfway line. Do not carry forward — let the LCB (player_id ends with "_2") or the midfield progress the ball.
11. **If team is leading by 1+ goals and minute > 80:** drop the block 8 units deeper. The DM (player_id ends with "_5") sits in front of the back four, no more high pressing.
12. **Set pieces / penalties / direct free kicks within 28 units:** defer to the LW (player_id ends with "_8" — Pulisic).

## Key Player Notes
- **Pulisic (8):** Captain, primary creator, primary set-piece taker, primary penalty taker. Free to drift inside; Robinson's overlap provides the width.
- **Adams (5):** Press leader and ball-winning anchor. His stamina (18) is the highest in the squad — he can run 90 minutes at intensity.
- **Robinson (1):** Underrated attacking weapon — speed 17, stamina 17. Pochettino licenses him to overlap repeatedly even into stoppage time.
- **Balogun (9):** Pressing forward. License to gamble on the offside line and run the channel between RB and RCB.
- **McKennie (7):** Late runner. Best aerial midfielder. Tertiary penalty taker.
- **Dest (4):** Inverts in build-up. Pochettino's primary tactical wrinkle — turns the 4-3-3 into a 3-2-5 in possession.

## Tournament Mindset
The USA carries the weight of being co-host on home soil with packed stadiums in NYC, LA, Dallas and Atlanta. Pochettino has explicitly told the squad to **embrace** the pressure rather than retreat from it. The team will run, press, and play vertically — even against superior opposition. The realistic ceiling is the quarter-finals; the floor (and disaster scenario) is a group-stage exit. Expect the USA to be the most physically intense team in the tournament. Pochettino's pragmatism shows late: if the team is leading 1-0 in the 80th minute, the press goes off and the block compresses — pragmatism wins.
