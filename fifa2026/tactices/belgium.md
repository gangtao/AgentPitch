# Belgium — Tactical Profile

## Identity & Philosophy
Rudi García's Belgium is the post-Golden-Generation team: still talented, still anchored by De Bruyne and Doku, but rebuilt around a younger spine and finally clicking. García (appointed January 2025) topped UEFA qualifying unbeaten and settled on a pragmatic 4-2-3-1 built around De Bruyne's distribution and Doku's dribbling. The style is wide pace + De Bruyne creativity + high-tempo transitions rather than sustained possession — García wants the ball won and converted quickly, and the ageing core means Belgium cannot press for 90 minutes and will accept spells of opponent possession. **And it has worked: Belgium swept Group G with a perfect record (9 points, 11 scored / 4 conceded)** — a **4-1 win over Egypt (MD1)** with Doku scoring twice off the left, a **3-1 win over Iran (MD2)** in which Doku answered Mehdi Ghayedi's opener with a hat-trick, and a **4-2 win over New Zealand (MD3)** in Vancouver capped by another Doku hat-trick. **In the Round of 32 they edged Senegal 3-2, Youri Tielemans burying a 120th-minute extra-time penalty to settle a war of transitions.** The recurring García pattern is De Bruyne and Doku manufacturing, the centre-forward converting. This is De Bruyne's last World Cup; now at Napoli, he wears the captain's armband under García.

## Round of 16 Lineup (vs USA, July 6 — Lumen Field, Seattle, win-or-go-home)
The knockout marches on and García keeps his settled hand: the predicted call again pairs a false-nine with the De Bruyne/Doku axis, **Charles De Ketelaere as a mobile false-nine** dropping to link De Bruyne and the wide men rather than holding as a fixed target — Lukaku held in reserve as the matchwinning bench card, an "almost certain" second-half appearance if the game demands proper centre-forward runs:
- **De Ketelaere at CF (false 9)** — links play and drifts wide; the trade-off is less penalty-box presence. Belgium can dominate possession without truly threatening in this shape, so **Lukaku and his proper centre-forward runs are the early Plan B** if Belgium look toothless — 2 goals in 4 appearances says he can still finish.
- **Tielemans + Vanaken as the double pivot** — Tielemans the deep build-up starter, penalty taker (he scored the 120th-minute winner vs Senegal) and set-piece man; Vanaken the experienced, physical screen in front of the back four (Onana and Raskin rotated out).
- **Front three**: Doku isolated on the left, De Bruyne as the clear #10, Trossard inverted from the right — confirmed fit despite a prior injury scare. This is the trio that produced three Doku group hat-tricks and Trossard's repeated cut-ins.
- **Back four**: Castagne (RB), Mechele + Theate (CBs), De Cuyper (LB); Courtois behind them. Zeno Debast (leg) remains an injury doubt after missing the whole tournament and is not relied upon.
- USA context: Pochettino's hosts play a 4-2-3-1 built on pressing Belgium's back four and transitioning fast through Christian Pulisic and quick wide men (Sergiño Dest), Weston McKennie the creative #10, Tyler Adams + Malik Tillman the ball-covering double pivot tasked with smothering De Bruyne in deep areas. Balogun is suspended, so Ricardo Pepi leads the line — good movement, less vertical threat. Home crowd, high fitness, system coherence: Belgium must beat the press cleanly, guard the channels Doku vacates, and not get caught upfield with the full-backs high. This is billed as the tie most likely to go the distance.

## Formation
- Shape: 4-2-3-1 (double pivot + De Bruyne as a clear #10; De Ketelaere drops from CF into a false-9 / second-#10 link role)
- Role mapping (roster order in `belgium.yaml`):
  - index 0: GK — Thibaut Courtois (world-class shot-stopper; save 19 — elite, the spine's biggest upgrade)
  - index 1: LB — Maxim De Cuyper (modern, energetic FB; stamina 17 — gets forward and underlaps Doku)
  - index 2: LCB — Arthur Theate (strong, left-footed, aggressive in the duel; steps out — pairs with Mechele)
  - index 3: RCB — Brandon Mechele (Club Brugge veteran; aerially strong, calm distributor, limited pace — the experienced organiser of the pair)
  - index 4: RB — Timothy Castagne (energetic two-footed tournament veteran; reliable, overlaps when Trossard inverts; stamina 17)
  - index 5: DM/#6 — Youri Tielemans (deep playmaker; pass 17 — left of the pivot, build-up starter, set-piece / penalty taker)
  - index 6: DM/#8 — Hans Vanaken (experienced, physical screen; pass 16 — recycles and shields the CBs in front of the back four)
  - index 7: AM/#10 — Kevin De Bruyne (captain & engine; pass 20, skill 19 — Belgium's one true superstar)
  - index 8: LW — Jérémy Doku (dribble 19, speed 19 — direct, isolated 1v1 specialist; the tournament's form forward, three hat-tricks)
  - index 9: CF — Charles De Ketelaere (mobile false-9; links and drifts; Lukaku is the like-for-like target-man swap from the bench)
  - index 10: RW — Leandro Trossard (inverted, intelligent, two-footed finisher)

## Style of Play

### Build-up
- Courtois short to Mechele or Theate by default (both comfortable on the ball, Mechele the calmer distributor); against the USA's high press, a long ball to De Ketelaere dropping or into the channel for Doku is the release valve.
- Tielemans drops to receive from CBs and progress; Vanaken stays as the deeper, physical shield.
- De Cuyper (LB) and Castagne (RB) both join late, but stay more conservative than the elite teams — wide outlets rather than constant overlaps, mindful of the USA's transition speed through Pulisic and Dest.
- De Bruyne drops into the right half-space pocket to receive — Belgium's primary progression is through him.

### Pressing
- **Belgium does not press intensely for the full match.** García wants to win the ball high and convert in transition, but the ageing core (De Bruyne in particular) cannot sustain a 90-minute high press. De Ketelaere's mobility up top helps lead the press more than a static #9 would.
- Mid-block primarily — 4-5-1 / 4-3-3 — with bursts of high pressing on triggers.
- Press triggers: opponent throw-ins, back-passes to the GK, or a loose touch by a CB; otherwise contain and look to spring forward fast.
- This is a defining tactical difference from Spain/Germany/Netherlands — Belgium accepts opponent possession and bets on transition speed. Against the USA that bet is symmetrical: Pochettino's side also want the press-and-transition game, so winning the second ball matters, and the free-kick-quick outball to Doku beats their compact block.

### Defensive shape
- 4-5-1 mid-block. De Ketelaere alone up top (mobile, presses and links rather than a target outlet); De Bruyne drops to right-mid in defense.
- Doku has poor defensive discipline (discipline 12) — he often fails to track back, which leaves De Cuyper exposed against the USA's right-sided runners.
- CBs hold a moderate line (~ 45%); Theate's aggression steps out, Mechele organises; Vanaken sits in front of them.

### Wide play
- **LEFT** is the explosive side: Doku in isolation 1v1; De Cuyper underlaps when Doku holds width; opposite-side overload from Trossard.
- **RIGHT** is the structured side: Trossard cuts inside, Castagne overlaps, De Bruyne drifts into the half-space.
- Belgium's most effective attacks come from giving Doku the ball wide and letting him decide alone — three group hat-tricks say so.

### Final third
- Termination patterns:
  1. **De Bruyne assist** — diagonal cross / cutback from right half-space to the late-arriving forward or a back-post Trossard.
  2. **Doku isolation** — beat the LB, cut inside, finish onto his right or cutback to the centre.
  3. **False-9 link** — De Ketelaere drops, lays off to De Bruyne / Trossard, then a runner attacks the vacated space (this is where Lukaku, if introduced, instead attacks crosses directly — strength 18, shoot 17).
- Transitions: when Belgium wins the ball in their own half, the immediate outball is Doku on the left.

## Set Pieces
- Corners: De Bruyne primary taker (pass 20); Tielemans and Trossard alternates. Targets: De Ketelaere / Theate (back post), Mechele (near post), Lukaku (penalty spot) if on.
- Direct FKs: De Bruyne for any centered or right-side, Tielemans for left-side; Doku an option for direct efforts.
- Penalties: De Bruyne first, then Tielemans, then Trossard.
- Defending: man-mark biggest threats (Pulisic, McKennie, Pepi); zonal at near post; Courtois commands his box and is elite in the air and on the line.

## decide() Decision Priorities
1. When my role is GK (Courtois): short to CB by default; long-ball to the `_9` (De Ketelaere dropping) or into the left channel for `_8` (Doku) if double-pressed. Elite shot-stopper — commit late, command the box on crosses.
2. When my `player_id` ends with `_2` (LCB — Theate): aggressive left-footed CB; step out into the duel; otherwise pass to the `_5` (Tielemans) or the `_7` (De Bruyne) between lines.
3. When my `player_id` ends with `_3` (RCB — Mechele): the experienced organiser of the two CBs; conservative but can step out and progress; long ball forward is acceptable only if a forward is in space.
4. When my `player_id` ends with `_1` (LB — De Cuyper): more adventurous than the RB — underlap/overlap the `_8` (Doku) when team_phase is "attacking" AND ball is on left flank; otherwise hold LB height and stay disciplined against Senegal's right-sided break.
5. When my `player_id` ends with `_4` (RB — Castagne): overlap when the `_10` (Trossard) cuts inside; otherwise stay disciplined and deep.
6. When my `player_id` ends with `_6` (DM — Vanaken): win it and recycle. Stay in front of CBs; physical screen; press on triggers but do not get dragged upfield — cover the pivot when Tielemans steps.
7. When my `player_id` ends with `_5` (DM — Tielemans): drop to receive; pass forward to the `_7` (De Bruyne) or wide to the `_8` (Doku); be the build-up starter.
8. When my `player_id` ends with `_7` (#10 — De Bruyne): drift into right half-space; receive between lines; THROUGH-BALL or cutback to the runner (`_9` De Ketelaere or back-post `_10` Trossard) is the primary action; Shoot 22m+ if no pass available.
9. When my `player_id` ends with `_8` (LW — Doku): hug LW touchline; on-ball 1v1, Move toward LB then Move diagonally inside (dribble 19 — take the duel always); Shoot from 18m onto right foot, or cutback to the centre.
10. When my `player_id` ends with `_10` (RW — Trossard): inverted — cut inside onto right foot OR cross/through-ball to the runner; second runner into the box at the back post.
11. When my `player_id` ends with `_9` (CF — De Ketelaere): mobile false-9; DROP to link and lay off to `_7` (De Bruyne) / `_10` (Trossard), then attack the vacated space — not a fixed target. (If swapped for Lukaku, instead hold up and attack crosses/cutbacks directly.)
12. When team_phase is "defending": 4-5-1 mid-block; the `_9` (De Ketelaere) leads the press / stays as transition outball; do not press high unless trigger.
13. When ball is lost in own half: priority is the `_8` (Doku) outball — the `_6` (Vanaken) or `_5` (Tielemans) pass long-diagonal to him.
14. Shoot from outside the box only if my `player_id` ends with `_7`, `_10`, or `_8` (De Bruyne/Trossard/Doku).

## Key Player Notes
- **Courtois (idx 0)** — world-class keeper anchoring the spine (save 19). Belgium can afford a younger back line because he covers it; will be busy against Senegal's transition shooters.
- **De Bruyne (idx 7)** — talisman, captain, and primary creator. Free role; everything goes through him. Now at Napoli; this is his last World Cup.
- **Doku (idx 8)** — explosive LW and the tournament's form forward, three hat-tricks across the group. License to dribble alone — Belgium will not double-up his side. Poor defensive discipline accepted; the player most likely to break a tight knockout open, and the man to isolate against USA right-back Dest.
- **De Ketelaere (idx 9)** — mobile false-9; links the front line and presses. The trade-off is box presence: "Belgium can dominate possession without truly threatening" in this shape, so **Lukaku is the early Plan B** for proper centre-forward runs if it stalls.
- **Vanaken (idx 6)** — experienced, physical screen partnering Tielemans with Onana/Raskin rotated out; recycles and shields the back four.
- **Tielemans (idx 5)** — deep-lying build-up starter and secondary set-piece / penalty taker.
- **Castagne (idx 4)** — energetic two-footed tournament veteran at RB; reliable, overlaps when Trossard inverts.
- **Mechele / Theate (idx 3 / 2)** — CB pair: Mechele the calm aerial organiser, Theate the aggressive left-footed stepper. Debast remains an injury doubt and is not relied upon.
- **Trossard (idx 10)** — under-rated; two-footed; can play any forward role; cut-ins and back-post arrivals produced goals all group.

## Tournament Mindset
Last dance for the Golden Generation core — and this Belgium arrived in the knockouts hot, **topping Group G with a perfect nine points** on the back of three Jérémy Doku hat-tricks, then surviving a 3-2 extra-time war with Senegal that Tielemans settled from the spot in the 120th minute. The Round of 16 is one game, win or go home, and it is billed as the tightest tie of the round. The USA are the hosts: quick, physical, lethal in transition through Pulisic and Dest, pressing Belgium's back four and hunting De Bruyne in deep areas with the Adams–Tillman pivot — a mirror of Belgium's own bet, so win the second ball, beat the press cleanly, don't get caught with the full-backs high, and trust the front line to settle it in a single moment. García's one open question is the centre-forward — De Ketelaere's link play versus Lukaku's box threat — and the second-half bench card may decide it. Realistic ceiling: quarterfinal and beyond if Doku stays this hot. Get Doku isolated on Dest, feed De Bruyne, ride out the extra time this tie may demand, and finish the chances they create.
