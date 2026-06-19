# Belgium — Tactical Profile

## Identity & Philosophy
Rudi García's Belgium is the post-Golden-Generation team: still talented, still anchored by De Bruyne and Doku, but rebuilt around a younger spine. García (appointed January 2025) guided Belgium through 2026 qualifying topping UEFA Group J unbeaten, settling on a pragmatic 4-2-3-1 built around De Bruyne's distribution and Doku's dribbling. The style is wide pace + De Bruyne creativity + high-tempo transitions rather than sustained possession — García wants the ball won and converted quickly, but the ageing core means Belgium cannot press for 90 minutes and accepts spells of opponent possession. Matchday 1 was a flat 1-1 draw with Egypt (Egypt led, an own goal rescued a point shortly after Lukaku came off the bench); García is under pressure to win the Iran game. Lukaku — barely fit after a lost season at Napoli — drops to the bench, so **Charles De Ketelaere starts as a mobile false-9** rather than a target man, which changes the centre-forward role from hold-up to dropping-link play. The back line is a younger rebuild: with Zeno Debast out (thigh) and Theate/De Winter on the bench, the centre-back pair is **Mechele (Club Brugge veteran) and Ngoy (young, quick)**, flanked by **Meunier (RB)** and **De Cuyper (LB)**, screened by a double pivot. Courtois restored to goal is the single biggest upgrade on the spine. This is De Bruyne's last World Cup; De Bruyne, now at Napoli, wears the captain's armband under García.

## Formation
- Shape: 4-2-3-1 (double pivot + De Bruyne as a clear #10; shifts to 4-3-3 vs weaker sides)
- Role mapping (roster order in `belgium.yaml`):
  - index 0: GK — Thibaut Courtois (world-class shot-stopper; save 19 — elite, the spine's biggest upgrade)
  - index 1: LB — Maxim De Cuyper (modern, energetic FB; stamina 17 — gets forward more than the old LB)
  - index 2: LCB — Brandon Mechele (Club Brugge veteran; aerially strong, good positioning, limited pace — the experienced organiser of the pair)
  - index 3: RCB — Nathan Ngoy (young Lille CB; speed 16 — the quick recovery defender alongside Mechele)
  - index 4: RB — Thomas Meunier (experienced, two-footed tournament veteran; defensively reliable, occasional overlap; pace declining)
  - index 5: DM/#6 — Youri Tielemans (deep playmaker; pass 17 — left of the pivot, build-up starter)
  - index 6: DM/#8 — Amadou Onana (the destroyer; strength 17; ball-winner; tucks in front of CBs)
  - index 7: AM/#10 — Kevin De Bruyne (captain & engine; pass 20, skill 19 — Belgium's one true superstar)
  - index 8: LW — Jérémy Doku (dribble 19, speed 19 — direct, isolated 1v1 specialist)
  - index 9: CF — Charles De Ketelaere (mobile false-9; skill 16, dribbling 15 — drops to link play rather than a target man; Lukaku is the like-for-like #9 off the bench)
  - index 10: RW — Leandro Trossard (inverted, intelligent, two-footed finisher)

## Style of Play

### Build-up
- Courtois short to Mechele or Ngoy by default (both comfortable on the ball, Mechele the calmer distributor); a long ball forward to De Ketelaere is a release valve when double-pressed, but De Ketelaere prefers to drop and link rather than battle in the air.
- Tielemans drops to receive from CBs and progress; Onana stays as the deeper shield.
- De Cuyper (LB) pushes higher than Meunier (RB); both still stay more conservative than the elite teams — wide, but rarely above the halfway line until late phases.
- De Bruyne drops into the right half-space pocket to receive — Belgium's primary progression is through him.

### Pressing
- **Belgium does not press intensely for the full match.** García wants to win the ball high and convert in transition, but the ageing core (De Bruyne in particular) cannot sustain a 90-minute high press.
- Mid-block primarily — 4-5-1 / 4-3-3 — with bursts of high pressing on triggers.
- Press triggers: opponent throw-ins, back-passes to the GK, or a loose touch by a CB; otherwise contain and look to spring forward fast.
- This is a defining tactical difference from Spain/Germany/Netherlands — Belgium accepts opponent possession and bets on transition speed.

### Defensive shape
- 4-5-1 mid-block. De Ketelaere alone up top (works harder pressing than Lukaku would); De Bruyne drops to right-mid in defense.
- Doku has poor defensive discipline (discipline 12) — he often fails to track back, which leaves De Cuyper exposed.
- CBs hold a moderate line (~ 45%); Ngoy's pace (16) covers the space in behind, Mechele organises; Onana sits in front of them.

### Wide play
- **LEFT** is the explosive side: Doku in isolation 1v1; De Cuyper underlaps when Doku holds width; opposite-side overload from Trossard.
- **RIGHT** is the structured side: Trossard cuts inside, Meunier overlaps occasionally, De Bruyne drifts into the half-space.
- Belgium's most effective attacks come from giving Doku the ball wide and letting him decide alone.

### Final third
- Termination patterns:
  1. **De Bruyne assist** — diagonal cross / cutback from right half-space to De Ketelaere or a late-arriving Trossard.
  2. **Doku isolation** — beat the LB, cut inside, finish or cutback to the central runner.
  3. **De Ketelaere link** — drops between lines, lays off to De Bruyne / Trossard, then spins to attack the box (no longer a hold-up target man).
- Transitions: when Belgium wins the ball in their own half, the immediate outball is Doku on the left.

## Set Pieces
- Corners: De Bruyne primary taker (pass 20); Tielemans and Trossard alternates. Targets: Onana (penalty spot), Mechele (near post), Ngoy (back post).
- Direct FKs: De Bruyne for any centered or right-side, Tielemans for left-side; Doku an option for direct efforts.
- Penalties: De Bruyne first, then Tielemans, then Trossard.
- Defending: man-mark biggest threats; zonal at near post; Courtois commands his box and is elite in the air and on the line.

## decide() Decision Priorities
1. When my role is GK (Courtois): short to CB by default; long-ball to the `_9` (De Ketelaere) if double-pressed — accepted as a release valve. Elite shot-stopper — commit late, command the box on crosses.
2. When my `player_id` ends with `_3` (RCB — Ngoy): quick young CB; carry the ball forward when a lane opens; otherwise pass to the `_5` (Tielemans) or the `_7` (De Bruyne) between lines.
3. When my `player_id` ends with `_2` (LCB — Mechele): the experienced organiser of the two CBs; conservative but can step out and progress; long ball forward is acceptable.
4. When my `player_id` ends with `_1` (LB — De Cuyper): more adventurous than the RB — underlap/overlap the `_8` (Doku) when team_phase is "attacking" AND ball is on left flank; otherwise hold LB height and stay disciplined.
5. When my `player_id` ends with `_4` (RB — Meunier): occasional overlap when the `_10` (Trossard) cuts inside; otherwise stay disciplined and deep.
6. When my `player_id` ends with `_6` (DM — Onana): destroy and recycle. Stay in front of CBs at all times. Tackle aggressively — strength 17, ball-winner.
7. When my `player_id` ends with `_5` (DM — Tielemans): drop to receive; pass forward to the `_7` (De Bruyne) or wide to the `_8` (Doku); be the build-up starter.
8. When my `player_id` ends with `_7` (#10 — De Bruyne): drift into right half-space; receive between lines; THROUGH-BALL to the `_9` (De Ketelaere) is the primary action; Shoot 22m+ if no pass available.
9. When my `player_id` ends with `_8` (LW — Doku): hug LW touchline; on-ball 1v1, Move toward LB then Move diagonally inside (dribble 19 — take the duel always); Shoot from 18m onto right foot.
10. When my `player_id` ends with `_10` (RW — Trossard): inverted — cut inside onto right foot OR through-ball the `_9` (De Ketelaere); second runner into the box.
11. When my `player_id` ends with `_9` (CF — De Ketelaere): mobile false-9; drop between lines to link, lay off to `_7` (De Bruyne) / `_10` (Trossard), then spin to attack the box on crosses (not a hold-up target man).
12. When team_phase is "defending": 4-5-1 mid-block; the `_9` (De Ketelaere) stays high as outball; do not press high unless trigger.
13. When ball is lost in own half: priority is the `_8` (Doku) outball — the `_6` (Onana) or `_5` (Tielemans) pass long-diagonal to him.
14. Shoot from outside the box only if my `player_id` ends with `_7`, `_10`, or `_8` (De Bruyne/Trossard/Doku).

## Key Player Notes
- **Courtois (idx 0)** — world-class keeper restored to the spine (save 19). Belgium can afford a younger back line because he covers it.
- **De Bruyne (idx 7)** — talisman, captain, and primary creator. Free role; everything goes through him. Now at Napoli; this is his last World Cup.
- **Doku (idx 8)** — explosive LW. License to dribble alone — Belgium will not double-up his side. Poor defensive discipline accepted. After the Egypt draw Belgium were criticised as over-reliant on him.
- **De Ketelaere (idx 9)** — starts as a mobile false-9 with Lukaku unfit; links play and runs the channels rather than holding the ball up. Lukaku is the like-for-like target #9 off the bench.
- **Onana (idx 6)** — Belgium's defensive midfielder backbone — without him, midfield gets overrun.
- **Tielemans (idx 5)** — deep-lying build-up starter and secondary set-piece / penalty taker.
- **Meunier (idx 4)** — experienced, two-footed tournament veteran at RB; started MD1; defensively reliable, pace declining.
- **Mechele / Ngoy (idx 2 / 3)** — emergency CB pair with Debast injured and Theate/De Winter on the bench: Mechele the calm aerial organiser, Ngoy the quick cover.
- **Trossard (idx 10)** — under-rated; two-footed; can play any forward role.

## Tournament Mindset
Last dance for the Golden Generation core. After a flat 1-1 Matchday-1 draw with Egypt, Belgium MUST win this Iran game to control Group G. Belgium expects to be a counter-attacking, transition-based team that wins through De Bruyne's distribution and Doku's runs. Group G opponents: Egypt, Iran, New Zealand. Realistic ceiling: quarterfinal. Vulnerable to teams that press them or sustain possession — Belgium will not press back for the full 90, and the Egypt draw exposed an over-reliance on Doku to create.
