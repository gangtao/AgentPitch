# USA — Tactical Profile

## Identity & Philosophy
Host nation of the 2026 World Cup and the most scrutinised USMNT in history. Under **Mauricio Pochettino**, the United States play aggressive, energetic, vertically minded football driven by a young, athletic, European-based core — the manager's identifiable Tottenham/PSG DNA: press with the door slammed shut behind the press, transition in 4-5 passes, and **get in the opponent's face** for 90 minutes. The USA topped Group D the hard way — a commanding **4-1 win over Paraguay** and a **2-0 win over Australia** — then, after resting the spine in a dead-rubber loss to Türkiye, won a tense Round of 32 on home soil against Bosnia-Herzegovina to reach the last 16. Now it gets real: a Round of 16 meeting with **Belgium** at Seattle Stadium, the same stage on which the Red Devils eliminated the USA in 2014. Win, and the USMNT reaches the quarter-finals for the first time in 24 years.

## Round of 16 Lineup (vs Belgium, July 6 — Seattle Stadium; host nation, win-or-go-home)
The USA names essentially its strongest available spine again — but with one enforced change up top:
- **Folarin Balogun is SUSPENDED** — he was sent off (straight/second-yellow red) in the second half of the Bosnia win despite scoring the decisive goal. **Ricardo Pepi** (PSV) comes in as the lone striker: a penalty-box poacher with the best pure scoring touch in the pool, a relentless presser and a strong aerial presence, though less of a link/channel dribbler than Balogun.
- **Matt Freese** continues as the first-choice keeper — he has started nearly every game under Pochettino and starred in the Gold Cup shootouts.
- **Antonee Robinson** at LB — flying, high-stamina overlapping outlet on the left.
- **Tim Ream (captain) + Chris Richards** as the center-back pairing — Ream the calm, left-footed organiser, Richards the physical aerial monitor.
- **Tyler Adams + Weston McKennie** as the double pivot — the ball-winning anchor and the box-to-box engine.
- **Christian Pulisic** on the left — the talisman, primary creator/finisher, and penalty taker.
- **Malik Tillman** at the 10, **Sergiño Dest** wide right, **Alex Freeman** at RB.
- Belgium context: a talented but ageing golden generation built around **Kevin De Bruyne**'s vision and **Jérémy Doku**'s dribbling, dangerous in transition and from De Bruyne's set-piece delivery. They can be sat off and hit on the break; the USA must not gift transitions, must screen the space in front of the back four against De Bruyne's through-balls, and must win the physical/aerial battles.

## Formation
- Shape: **4-2-3-1** — a double pivot (Adams + McKennie) to control the center against De Bruyne, with a fluid front band of Dest, Tillman and Pulisic behind Pepi. Without the ball the front four drop into a compact **4-4-1-1 / 4-1-4-1** mid-block.
- Role mapping (roster order in `usa.yaml`):
  - index 0: GK — **Matt Freese** — first-choice keeper; competent line-bound shot-stopper, modest distribution. Stays near the goal line, short distribution to the nearest CB.
  - index 1: LB — **Antonee Robinson** — flying, high-stamina left-back; the primary attacking outlet on the left, bombs the touchline to the byline and recovers with sheer pace.
  - index 2: LCB — **Tim Ream** (captain) — veteran left-footed ball-playing center-back, the calm organiser of the back line; holds the line, progresses from the back, dictates the build.
  - index 3: RCB — **Chris Richards** — physical right-sided stopper, the aerial monitor; dominant in the box, holds the line.
  - index 4: RB — **Alex Freeman** — dynamic, high-stamina right-back; provides honest width on the right, tucks in defensively, overlaps when the ball is on his flank.
  - index 5: DM/6 — **Tyler Adams** — ball-winning anchor of the double pivot; screens the back four, intercepts, recycles short and simple, snuffs out Belgian counters before they launch.
  - index 6: DM/8 — **Weston McKennie** — box-to-box engine alongside Adams; covers when Adams steps, arrives late in the box, the team's most powerful midfield runner.
  - index 7: RW — **Sergiño Dest** — skilful, inverting right-sided forward/full-back hybrid; cuts inside off the right, combines in the half-space, dangerous on the dribble.
  - index 8: CAM/10 — **Malik Tillman** — the creative hub between the lines; receives in the half-spaces, supplies the killer through-ball, dribbles into the box, secondary set-piece option.
  - index 9: LW — **Christian Pulisic** — the talisman; cuts inside on his right foot off the left, drives at the full-back, the chief creator and primary finisher, takes penalties.
  - index 10: CF — **Ricardo Pepi** — lone striker deputising for the suspended Balogun; a penalty-box finisher with excellent movement and aerial ability, a high-energy presser, less of a link dribbler but the sharpest pure scoring touch in the squad.

## Style of Play

### Build-up
Short build-up from the back when possible: the center-backs (Ream, Richards) split, Adams drops to form a 3+1, and the full-backs (Robinson, Freeman) push high to provide width while Dest and Pulisic tuck inside. When the press is intense, Pochettino has no qualms about going long to the striker — second-ball wins around the halfway line are a feature, not a fallback. Adams and McKennie are the orchestrators at the base; Tillman connects the half-spaces between the lines.

### Pressing
**High press is the identity.** Trigger #1: opposition GK receiving a back-pass — Pepi curves his run, Dest and Pulisic jump the full-backs, Adams steps into the #6 space. Trigger #2: a heavy first touch from any opposition midfielder — the nearest USA player sprints to engage within 6 units. The press is **man-oriented** in the front four, **zonal** in the back four. Pepi is a relentless presser who leads the line's work without the ball.

### Defensive shape
When the press is broken, the USA drop into a compact **4-4-1-1 / 4-1-4-1** mid-block with the wide forwards (Dest, Pulisic) tucking into the midfield band and Pepi leading the line. The block is **mid-height** (around the halfway line) rather than deep — Pochettino refuses to invite pressure, but against De Bruyne's range the double pivot must be extra-disciplined shielding the central channel. Ream and Richards hold a moderately high line; Adams shields in front of them. The full-backs fold back into the back four without the ball, and Adams + McKennie screen against the over-the-top and cut-back balls that De Bruyne feeds.

> **Form note (Round of 16):** The USA topped Group D (4-1 vs Paraguay, 2-0 vs Australia) before resting the spine in a dead-rubber loss to Türkiye, then beat Bosnia-Herzegovina in the Round of 32 — Balogun scoring the winner but earning a **red card** that rules him out here. **Ricardo Pepi** steps up as the lone striker. Otherwise this is the USA's strongest available XI, and the knockout intent is total.

### Wide play
Asymmetric: **left** = Pulisic cutting inside off the left with Robinson bombing the overlap (the main creation channel — Robinson reaches the byline, Pulisic shoots/combines from the half-space); **right** = Dest inverting and combining with Freeman providing the overlap. McKennie is the late runner arriving on cut-backs; Pepi attacks the near/back posts.

### Final third
Patterns: Pulisic-Robinson 1-2 down the left ending in a Robinson cut-back to Pepi arriving in the box; Dest cutting inside onto his left to feed Tillman; Pepi pinning the center-backs and darting onto crosses and cut-backs; Tillman threading the through-ball to the runners. Direct counter-attack from a press turnover: Adams wins it → vertical pass to a wide forward → into Pepi in 3 passes.

## Set Pieces
- Attacking corners: **Pulisic** delivers from both sides (in-swinger from the right, out-swinger from the left); **Tillman** alternates. Primary aerial targets: Richards, Ream, McKennie, Pepi.
- Defending corners: **hybrid** — three zonal markers on the six-yard line, four man-markers, two short-corner blockers. Adams takes the front-post zonal slot; Pepi stays high on the halfway line for the outball. Beware De Bruyne's inswinging delivery.
- Free kicks: **Pulisic** takes direct from any zone within 28 units; **Tillman** delivers wide free kicks into the box.
- Penalties: **Pulisic** primary, **Tillman** secondary, **Pepi** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my player_id ends with "_9" (LW, jersey #10 — Pulisic) and I receive the ball wide on the left:** cut inside on my right foot. If a teammate (the LB, player_id ends with "_1" — Robinson) is overlapping outside me, prefer a 1-2 Pass; else dribble to the half-space and Shoot if angle < 30° and distance < 24.
2. **If my player_id ends with "_5" (DM, jersey #4 — Adams) and an opponent has the ball within 8 units in central midfield:** Tackle immediately. Do not hesitate — shield the back four against De Bruyne.
3. **If my player_id ends with "_1" (LB, jersey #5 — Robinson) and team_phase == "attacking":** Sprint forward to the opposition byline. The overlap is automatic — even at low stamina; primary width on the left.
4. **If my player_id ends with "_4" (RB, jersey #22 — Freeman) and team_phase == "attacking" and the ball is in the right half:** Overlap or underlap to support the RW (player_id ends with "_7" — Dest); otherwise hold the back-four line.
5. **If my role is FWD and team has just won possession in our own half:** Sprint forward on a vertical line — counter-attack in 3-4 passes is the default.
6. **If team_phase == "defending" and player_id ends with "_7" (RW — Dest) or "_9" (LW — Pulisic):** drop into the wide slots of the midfield band to form a 4-4-1-1/4-1-4-1; track the opposition full-back on your flank.
7. **If my role is GK (player_id ends with "_0" — Freese):** stay on the goal line unless ball > 40 units away. Avoid sweeping — distribution is short to the nearest CB.
8. **If my player_id ends with "_10" (CF, jersey #9 — Pepi) and the opposition CB takes a heavy first touch (ball > 3 units from feet):** Sprint to press; curve the run to cut the deeper CB.
9. **If my player_id ends with "_6" (DM/8, jersey #8 — McKennie) and a teammate is delivering a cross into the box:** Sprint into the box, target the back post — McKennie is the late-arriving runner.
10. **If my player_id ends with "_2" (LCB, jersey #13 — Ream) or "_3" (RCB, jersey #3 — Richards) and team has possession in opposition half:** Hold position at the halfway line. Ream (`_2`) may carry into midfield if no opponent is within 10 units; Richards (`_3`) holds.
11. **If my player_id ends with "_8" (CAM — Tillman) and I receive the ball between the lines facing forward:** look first for the through ball to Pepi (`_10`) or the wide runners; carry into the box and Shoot if the lane opens — Tillman is the chief creative hub.
12. **If team is leading by 1+ goals and minute > 80:** drop the block 8 units deeper. The DM (player_id ends with "_5" — Adams) sits in front of the back four, no more high pressing; only Pepi (`_10`) stays high as outball.
13. **Set pieces / penalties / direct free kicks within 28 units:** defer to the LW (player_id ends with "_9" — Pulisic) for penalties, corners and direct free kicks; Tillman (`_8`) is the secondary deliverer.

## Key Player Notes
- **Pulisic (10, idx 9):** The talisman on the left; chief creator and primary finisher. Primary penalty, corner and free-kick taker. Cuts inside on his right to shoot or combine.
- **Pepi (9, idx 10):** Lone striker in for the suspended Balogun; a penalty-box poacher with the best pure scoring touch in the squad and strong aerial movement, a relentless presser but less of a link/channel dribbler — feed him to feet in the box and on cut-backs. Tertiary penalty option.
- **Adams (4, idx 5):** Ball-winning anchor of the double pivot; screens the back four and snuffs out Belgian counters before they launch.
- **McKennie (8, idx 6):** Box-to-box engine alongside Adams; powerful runner, arrives late in the box on cut-backs, the team's most physical midfielder.
- **Tillman (18, idx 8):** The creative hub at the 10; receives between the lines, threads the killer pass, secondary set-piece taker.
- **Dest (2, idx 7):** Skilful inverting right-sided forward; cuts inside off the right, combines in the half-space, dangerous on the dribble.
- **Robinson (5, idx 1):** Rampaging attacking LB — speed 18, stamina 18; overlaps repeatedly to the byline, primary width on the left.
- **Ream (13, idx 2, captain) & Richards (3, idx 3):** The center-back pairing; Ream the calm left-footed organiser and ball-player, Richards the physical aerial monitor who dominates the box.
- **Freese (24, idx 0):** First-choice keeper; line-bound shot-stopper, short distribution to the nearest CB.

## Tournament Mindset
The USA carries the weight of being host nation on home soil — a partisan, packed Seattle Stadium and a nation watching. This is the Round of 16: one game, win or go home; if level after 90, thirty more of extra time; if still level, a penalty shootout — and Freese's shootout pedigree is a genuine edge. Belgium ended the USA's 2014 World Cup at this same stage, and revenge is on the line with a first quarter-final in 24 years the prize. Missing the suspended Balogun, Pochettino trusts **Ricardo Pepi**'s poacher's instinct, restores the rest of his strongest spine, and embraces the home-crowd intensity. The plan: control the center against De Bruyne, press relentlessly, refuse the transition, guard against the killer through-ball and inswinging set-piece, and trust Pulisic — and Pepi's finishing touch — to settle it in a single moment. Expect the USA to remain the most physically intense team in the tournament and to ride the home momentum through the first knockout hurdle and beyond.
