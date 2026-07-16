# France — Tactical Profile

## Identity & Philosophy
Didier Deschamps' France is pragmatic, defensively impeccable, and built to win ugly — but this is now a wounded team playing its manager's **last-ever match**. Six perfect wins (16 scored / 2 conceded) carried France into the semifinal as arguably the tournament's most complete side; then Spain dismantled them **2-0 in Arlington (July 14)** — Oyarzabal's 22nd-minute penalty after Digne fouled Yamal in the box, and Porro's 58th-minute give-and-go finish past Maignan. France never landed a punch: Mbappé didn't attempt a shot until the 67th minute, Dembélé didn't attempt a single dribble, Olise touched the ball once in the box in 72 minutes, and Barcola's left flank produced nothing. Deschamps conceded his side was outclassed "technically, tactically and physically." Worse: **William Saliba left injured (lower back) after 30 minutes, in tears**, replaced by Maxence Lacroix.

Now the bronze final vs England (Saturday July 18, Hard Rock Stadium, Miami Gardens): Deschamps — who confirmed in January 2025 that this tournament ends his 14-year reign — gets one farewell game, and **Mbappé sits level with Messi on 8 goals in the Golden Boot race**. Messi plays Sunday's final; Saturday is Mbappé's only chance to answer. Third-place goals count. Expect rotation around a purposeful spine: the fringe men get their World Cup minutes, but the captain hunts goals, and Deschamps does not do friendly exhibitions — he leaves with a medal.

## Bronze-Final Lineup (vs England, July 18 — Hard Rock Stadium, Miami Gardens)
Five changes from the semifinal XI, rotation with intent:
- **Saliba is out** (back injury picked up after 30' vs Spain — he faces a race to be fit and will not be risked in a bronze game); **Maxence Lacroix**, who replaced him in Arlington, starts at RCB. Upamecano keeps the other CB slot for stability.
- **Theo Hernandez** replaces Digne at LB — Digne conceded the decisive penalty and is mentally/physically spent; Theo's fresh legs and vertical running suit an open game far better than a possession-starved one.
- **Malo Gusto** replaces Koundé at RB — Koundé has played every knockout minute; Gusto is the classic third-place reward start.
- **Koné + Zaïre-Emery** form the pivot — Tchouaméni (just back from a groin/adductor issue, 90 hard minutes on July 14) and Rabiot (France's best player vs Spain, but 35-year-old legs across seven games) both drop out. Zaïre-Emery has been pushing Kanté in the midfield pecking order all tournament; Kanté is primed for a send-off cameo.
- **Cherki** starts at #10 for the anonymous Dembélé (rested — no dribbles attempted vs Spain, a season's fatigue showing); **Doué** returns on the left for Barcola (rated the semifinal's worst French performer).
- **Kept**: Maignan (goal), Upamecano, Koné, Olise (tournament-high 5 assists — Mbappé's supply line), and Mbappé himself, chasing the Golden Boot.
- Bench: Samba may get late GK minutes; Kanté, Rabiot, Tchouaméni midfield cover; Dembélé, Barcola, Thuram, Mateta, Akliouche the attacking changes; Konaté and Lucas Hernandez the defensive cover.

## Formation
- Shape: 4-2-3-1 (Koné + Zaïre-Emery double pivot; fluid front four of Doué, Cherki, Olise behind Mbappé)
- Role mapping (roster order in `france.yaml`):
  - index 0: GK — Mike Maignan (sweeper-keeper, elite reflexes, distribution starter)
  - index 1: LB — Theo Hernandez (rampaging attacking full-back, speed 18; the overlap engine on the left — but rash, discipline 11)
  - index 2: LCB — Dayot Upamecano (raw physical CB, aerial duels, tight-marker)
  - index 3: RCB — Maxence Lacroix (in for the injured Saliba; recovery-pace specialist, speed 17 — sweeps the space behind)
  - index 4: RB — Malo Gusto (energetic modern full-back in for Koundé; supports underlapping, stays honest vs England's left)
  - index 5: DM/#6 — Manu Koné (deep-lying anchor; physical ball-winner, covers ground, shields the CBs)
  - index 6: DM/#8 — Warren Zaïre-Emery (box-to-box, tidy progressor, late box arrivals; covers when Koné steps)
  - index 7: LW — Désiré Doué (two-footed inside-combiner on the left; links in tight spaces, cuts in to shoot — skill 18 / dribble 18 / pass 17)
  - index 8: CAM (#10) — Rayan Cherki (the creator between the lines; outrageous final pass, pass 18 / dribble 18 — his job is to feed the `_10` run)
  - index 9: RW — Michael Olise (creative wide hub, cuts inside onto his left foot, set-piece deliverer; 5 assists — tournament high)
  - index 10: CF — Kylian Mbappé (captain, 8 goals, level with Messi — the Golden Boot is decided today; lethal finisher, transition weapon)

## Style of Play

### Build-up
- Patient when allowed: Maignan short to Upamecano or Lacroix; Koné drops between the CBs when England press (back-three build).
- Gusto stays more conservative; Theo Hernandez provides the aggressive height on the left, Zaïre-Emery into the right half-space.
- Unlike the Spain game, **France will see plenty of the ball** — England after a semifinal defeat will also rotate and won't press for 90 minutes in Miami heat. Play forward earlier than usual: Cherki between the lines is the first look, Mbappé's channel run the second.

### Pressing
- Mid-block with selective triggers — this is a bronze final in Florida heat, not a 95-minute war. Conserve legs.
- Trigger: a heavy touch by an England CB or a blind square pass into midfield — then Mbappé and Cherki collapse together.
- Otherwise 4-4-1-1 around halfway: Koné screens the Bellingham lane, Zaïre-Emery tracks late runners, wingers tuck in.

### Defensive shape
- 4-4-1-1 mid-block. Koné holds in front of the CBs; Zaïre-Emery alongside.
- **Central alert**: Bellingham arriving from deep and Kane dropping off the front are England's twin threats — Koné never follows Kane into midfield and leaves the gate; Lacroix's recovery pace (17) handles the ball over the top for England's runners.
- **Left-side alert**: Theo WILL be caught high — Koné shuffles across and Lacroix covers the channel when the counter comes down England's right (Saka's side).
- Aerial duels: Upamecano and Lacroix must win everything against Kane's near-post movement and England's set-piece routine.

### Wide play
- Asymmetric, inverted from the Spain plan. LEFT is now the aggressive side: Theo overlaps hard outside Doué, who comes inside to combine with Cherki and Mbappé.
- RIGHT: Olise isolated, cuts in onto his left; Gusto underlaps to hold width and recycle.

### Final third
- Two patterns:
  1. **The Cherki ball**: Cherki receives between the lines on the half-turn → immediate slide pass behind England's line for Mbappé (pass 18 meets speed 20 — the whole gameplan in one action).
  2. **Left overload**: Doué-Theo-Cherki triangle drags England right, then switch to Olise's isolated 1v1 for the cut-inside curler or the far-post cross to Mbappé.
- Everything terminates at the `_10`: cutbacks to the penalty spot, near-post crosses from Theo, reverse passes from Olise. Mbappé needs one goal to win the Golden Boot outright — feed him relentlessly.

## Set Pieces
- Corners: Olise delivers in-swingers from the right, Theo Hernandez from the left. Upamecano near-post flick, Lacroix back-post target, Koné late arriver at the spot.
- Direct FKs (18-25m): Mbappé or Olise central; Cherki curls from the left channel. Two always stay back — England break fast through Saka.
- **Penalty-shootout order (bronze final — level after 90/120 goes to a shootout):**
  1. **Mbappé** — captain, first taker (penalty 18); a Golden Boot may hang on it.
  2. **Olise** — penalty 17, ice-cold technician.
  3. **Cherki** — penalty 15, wants the stage.
  4. **Doué** — penalty 15.
  5. **Theo Hernandez** — penalty 13, the veteran hammer closes.
- Defending: man-mark Kane wherever he goes + 2 zonal at the near post; Mbappé stays on halfway as the outball.

## decide() Decision Priorities
1. When my role is GK and ball is in opponent half: position 8-10m off goal line, ready to sweep.
2. When my role is DEF and `player_id` ends with `_2` or `_3` (CB pair — Upamecano/Lacroix) and possession_team is mine, no pressure: pass short to the other CB or the DM; if England press collapses on the first pass, go long early toward the `_10` channel rather than dribble out.
3. When my `player_id` ends with `_5` (DM — Koné) and team has the ball: stay between the CBs and the ball, offer the constant short option, recycle and shield; only drive forward when the ball is won high and space opens.
4. When my `player_id` ends with `_1` (LB — Theo Hernandez) and team_phase is "attacking" and ball is on left side: overlap HARD outside the `_7` player (Doué) — provide the width and the near-post cross; this is the aggressive flank. When possession is lost, sprint back immediately — do not jog.
5. When my `player_id` ends with `_4` (RB — Gusto) and team_phase is "attacking": underlap to RCM height, give the `_9` player (Olise) the outside-right room, stay the more conservative of the two full-backs.
6. When my `player_id` ends with `_9` (RW — Olise) and I receive isolated 1v1: cut inside onto my left foot and shoot from the right half-space (shoot 16), or slide the reverse pass to the `_10` run — the assist king (5) feeds the Golden Boot chase.
7. When my `player_id` ends with `_10` (CF — Mbappé) and team_phase is "defending": stay high near halfway as the transition outball; when we win it, sprint in behind and demand the pass. In the final third, SHOOT — one goal wins the Golden Boot outright (shoot 19).
8. When my `player_id` ends with `_7` (LW — Doué) and team has the ball: come inside off the left to combine short (pass 17 / skill 18) — give-and-go with `_8` or `_10`, let `_1` take the outside width, then attack the box; shoot when the lane opens (shoot 16).
9. When my `player_id` ends with `_8` (CAM — Cherki) and team has the ball: float between the lines, receive on the half-turn, and look FIRST for the slide pass behind the last line to `_10` (pass 18); dribble to disorganize (dribble 18), shoot from the edge when the lane opens (shoot 15) — I am the supply line, creation over conservation.
10. When my `player_id` ends with `_6` (DM/#8 — Zaïre-Emery) and team_phase is "defending": tuck into the double pivot beside Koné, track England's late midfield runners; when attacking, arrive late at the edge of the box for the second wave.
11. When tackling: only commit if my `player_id` ends with `_2`, `_3`, `_4`, or `_5` (Upamecano/Lacroix/Gusto/Koné) AND the carrier has poor body shape; otherwise Hold and contain — no cheap fouls around the box, and `_1` (Theo, discipline 11) must NEVER dive in as last man.
12. When my team is leading by 1+ and clock > 70: drop into a 4-4-1-1 mid-block; only the `_10` player (Mbappé) stays high as outball — but keep feeding his runs, the Golden Boot stays live until the whistle.
13. Shoot only if angle < 30deg from goal-center and within 22m, OR my `player_id` ends with `_10` (Mbappé) or `_8` (Cherki) inside the box — when in doubt near the box, the pass to `_10` outranks the shot for everyone except `_10`.

## Key Player Notes
- **Mbappé (idx 10)** — captain, central striker, 8 goals — level with Messi, who plays Sunday's final. This match decides the Golden Boot and Mbappé knows it: smothered by Spain (no shot until the 67th minute), he gets a rotated England defence and a team instructed to feed him. Expect ravenous.
- **Cherki (idx 8)** — the tournament's great tease finally gets his start at #10. The most naturally gifted passer in the squad (pass 18 / dribble 18); his one job is the killer ball behind England's line. Defensive workrate is the trade-off (discipline 12) — the pivot covers.
- **Olise (idx 9)** — kept in the XI despite the rotation: tournament-high 5 assists, primary set-piece deliverer, second penalty taker. Cuts in onto his left; his link with Mbappé is France's most productive channel.
- **Doué (idx 7)** — restored on the left after Barcola's non-show in Arlington; two-footed combiner who now gets a rampaging Theo Hernandez outside him instead of the measured Digne.
- **Koné (idx 5)** — the anchor and the one midfield survivor; physical ball-winner whose duel with Bellingham's arrivals decides the middle. Fresh — he sat out the semifinal as Tchouaméni returned.
- **Zaïre-Emery (idx 6)** — the 20-year-old's biggest international start; tidy progressor and late-box arriver who has pushed past Kanté in the pecking order. Kanté is primed for the sentimental late cameo in Deschamps' last game.
- **Lacroix (idx 3)** — in for the injured Saliba (back, off at 30' in the semifinal, will not be risked). Elite recovery pace (speed 17) — the insurance policy behind Theo's adventures and against England's over-the-top balls.
- **Upamecano (idx 2)** — the defensive spine-keeper; must organize a back four with three new faces and win the aerial war with Kane.
- **Theo Hernandez (idx 1)** — unleashed at last: Digne's discipline was for Yamal, Theo's chaos is for a bronze final. Overlap engine, near-post crosser, long-range hitter (shoot 13) — and a card risk (discipline 11).
- **Gusto (idx 4)** — the reward start at RB; energetic, honest, keeps the balance while the left side attacks.
- **Maignan (idx 0)** — kept in goal for the medal; sweeper-keeper and shootout threat. Samba may get farewell minutes late if the game is settled.

## Tournament Mindset
**Bronze final — Deschamps' 14-year reign ends today, win or lose.** The wound is fresh: six perfect wins, then a semifinal in which Spain took France apart "technically, tactically and physically" (Deschamps' own words) and the front four combined for almost nothing. A third-place game is what a team makes of it — and this France has three live motivations that England, drained by their extra-time run and the Argentina heartbreak, may not match: a medal for Deschamps' farewell after a World Cup win, a final, and now this; **the Golden Boot for Mbappé**, level with Messi at 8 with Messi holding one more game; and redemption minutes for the fringe — Cherki, Zaïre-Emery, Gusto, Lacroix — auditioning for the next manager's France. Play front-foot football: this is not the Spain game, England will give the ball back, and Miami heat plus two rotated XIs means space WILL appear after the hour. Feed the captain, protect the counter behind Theo, get Kanté on for the ovation — and leave Deschamps on the podium one last time. Pride is the trophy; the Golden Boot is the bonus; take both.
