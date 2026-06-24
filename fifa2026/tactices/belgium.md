# Belgium — Tactical Profile

## Identity & Philosophy
Rudi García's Belgium is the post-Golden-Generation team: still talented, still anchored by De Bruyne and Doku, but rebuilt around a younger spine. García (appointed January 2025) guided Belgium through 2026 qualifying topping UEFA Group J unbeaten, settling on a pragmatic 4-2-3-1 built around De Bruyne's distribution and Doku's dribbling. The style is wide pace + De Bruyne creativity + high-tempo transitions rather than sustained possession — García wants the ball won and converted quickly, but the ageing core means Belgium cannot press for 90 minutes and accepts spells of opponent possession. **Belgium have stumbled into the final group game with two draws and no win**: a flat **1-1 draw with Egypt (MD1)** where an own goal rescued a point, then a **0-0 stalemate with Iran (MD2)** in Los Angeles in which Nathan Ngoy was sent off in the 66th minute (last-man foul on Taremi after a poor back-pass) and a profligate Belgium spurned chance after chance even against ten — sorry, against a packed Iran block — with Courtois forced into two big saves. Belgium sit **3rd in Group G on 2 points, level with Iran, and MUST WIN vs New Zealand to reach the last 16.** Romelu Lukaku, finally fit after a lost season, started and stays as the **target #9** — so the centre-forward role is hold-up and box presence again rather than the false-9 link play used when he was unavailable. **Ngoy is suspended** for the red card, so **Arthur Theate slots in alongside Mechele at CB**, flanked by Meunier (RB) and De Cuyper (LB). With Amadou Onana rotated out, **Nicolas Raskin partners Tielemans in the double pivot** — more legs, more pressing energy in front of the back four. Doku, back with the squad after travelling to London for the birth of his first child, returns to the left wing. Courtois in goal remains the spine's biggest upgrade. This is De Bruyne's last World Cup; now at Napoli, he wears the captain's armband under García.

## Formation
- Shape: 4-2-3-1 (double pivot + De Bruyne as a clear #10; shifts to 4-3-3 vs weaker sides — New Zealand will sit deep)
- Role mapping (roster order in `belgium.yaml`):
  - index 0: GK — Thibaut Courtois (world-class shot-stopper; save 19 — elite, the spine's biggest upgrade)
  - index 1: LB — Maxim De Cuyper (modern, energetic FB; stamina 17 — gets forward more than the old LB)
  - index 2: LCB — Brandon Mechele (Club Brugge veteran; aerially strong, good positioning, limited pace — the experienced organiser of the pair)
  - index 3: RCB — Arthur Theate (comes in for the suspended Ngoy; strong, left-footed, aggressive in the duel — pairs with Mechele)
  - index 4: RB — Thomas Meunier (experienced, two-footed tournament veteran; defensively reliable, occasional overlap; pace declining)
  - index 5: DM/#6 — Youri Tielemans (deep playmaker; pass 17 — left of the pivot, build-up starter)
  - index 6: DM/#8 — Nicolas Raskin (energetic ball-winner; stamina 17 — replaces Onana, presses and recycles in front of the CBs)
  - index 7: AM/#10 — Kevin De Bruyne (captain & engine; pass 20, skill 19 — Belgium's one true superstar)
  - index 8: LW — Jérémy Doku (dribble 19, speed 19 — direct, isolated 1v1 specialist; back from paternity)
  - index 9: CF — Romelu Lukaku (target #9; strength 18, shoot 17 — hold-up, box presence, attacks crosses and cutbacks)
  - index 10: RW — Leandro Trossard (inverted, intelligent, two-footed finisher)

## Style of Play

### Build-up
- Courtois short to Mechele or Theate by default (both comfortable on the ball, Mechele the calmer distributor); a long ball forward to Lukaku is a genuine release valve when double-pressed — he wins it and holds it.
- Tielemans drops to receive from CBs and progress; Raskin stays as the deeper, more mobile shield.
- De Cuyper (LB) pushes higher than Meunier (RB); both still stay more conservative than the elite teams — wide, but rarely above the halfway line until late phases.
- De Bruyne drops into the right half-space pocket to receive — Belgium's primary progression is through him.

### Pressing
- **Belgium does not press intensely for the full match.** García wants to win the ball high and convert in transition, but the ageing core (De Bruyne in particular) cannot sustain a 90-minute high press. Raskin's legs in the pivot help raise the press more than the Onana version.
- Mid-block primarily — 4-5-1 / 4-3-3 — with bursts of high pressing on triggers.
- Press triggers: opponent throw-ins, back-passes to the GK, or a loose touch by a CB; otherwise contain and look to spring forward fast.
- This is a defining tactical difference from Spain/Germany/Netherlands — Belgium accepts opponent possession and bets on transition speed. Against a deep New Zealand, the problem inverts: Belgium must break a low block, not survive pressure.

### Defensive shape
- 4-5-1 mid-block. Lukaku alone up top (less pressing than De Ketelaere, but a transition outlet who holds it); De Bruyne drops to right-mid in defense.
- Doku has poor defensive discipline (discipline 12) — he often fails to track back, which leaves De Cuyper exposed.
- CBs hold a moderate line (~ 45%); Theate's aggression steps out, Mechele organises; Raskin sits in front of them.

### Wide play
- **LEFT** is the explosive side: Doku in isolation 1v1; De Cuyper underlaps when Doku holds width; opposite-side overload from Trossard.
- **RIGHT** is the structured side: Trossard cuts inside, Meunier overlaps occasionally, De Bruyne drifts into the half-space.
- Belgium's most effective attacks come from giving Doku the ball wide and letting him decide alone.

### Final third
- Termination patterns:
  1. **De Bruyne assist** — diagonal cross / cutback from right half-space to Lukaku at the back post or a late-arriving Trossard.
  2. **Doku isolation** — beat the LB, cut inside, finish or cutback to Lukaku in the centre.
  3. **Lukaku target play** — hold up, lay off to De Bruyne / Trossard, then attack the box to finish crosses (strength 18, shoot 17).
- Transitions: when Belgium wins the ball in their own half, the immediate outball is Doku on the left.

## Set Pieces
- Corners: De Bruyne primary taker (pass 20); Tielemans and Trossard alternates. Targets: Lukaku (penalty spot), Mechele (near post), Theate (back post).
- Direct FKs: De Bruyne for any centered or right-side, Tielemans for left-side; Doku an option for direct efforts.
- Penalties: De Bruyne first, then Tielemans, then Trossard / Lukaku.
- Defending: man-mark biggest threats; zonal at near post; Courtois commands his box and is elite in the air and on the line.

## decide() Decision Priorities
1. When my role is GK (Courtois): short to CB by default; long-ball to the `_9` (Lukaku) if double-pressed — a genuine target release valve. Elite shot-stopper — commit late, command the box on crosses.
2. When my `player_id` ends with `_3` (RCB — Theate): aggressive left-footed CB; step out into the duel; otherwise pass to the `_5` (Tielemans) or the `_7` (De Bruyne) between lines.
3. When my `player_id` ends with `_2` (LCB — Mechele): the experienced organiser of the two CBs; conservative but can step out and progress; long ball forward to `_9` (Lukaku) is acceptable.
4. When my `player_id` ends with `_1` (LB — De Cuyper): more adventurous than the RB — underlap/overlap the `_8` (Doku) when team_phase is "attacking" AND ball is on left flank; otherwise hold LB height and stay disciplined.
5. When my `player_id` ends with `_4` (RB — Meunier): occasional overlap when the `_10` (Trossard) cuts inside; otherwise stay disciplined and deep.
6. When my `player_id` ends with `_6` (DM — Raskin): win it and recycle. Stay in front of CBs; press more readily than a deep anchor; tackle aggressively — stamina 17, ball-winner.
7. When my `player_id` ends with `_5` (DM — Tielemans): drop to receive; pass forward to the `_7` (De Bruyne) or wide to the `_8` (Doku); be the build-up starter.
8. When my `player_id` ends with `_7` (#10 — De Bruyne): drift into right half-space; receive between lines; THROUGH-BALL or cutback to the `_9` (Lukaku) is the primary action; Shoot 22m+ if no pass available.
9. When my `player_id` ends with `_8` (LW — Doku): hug LW touchline; on-ball 1v1, Move toward LB then Move diagonally inside (dribble 19 — take the duel always); Shoot from 18m onto right foot, or cutback to `_9` (Lukaku).
10. When my `player_id` ends with `_10` (RW — Trossard): inverted — cut inside onto right foot OR cross/through-ball the `_9` (Lukaku); second runner into the box.
11. When my `player_id` ends with `_9` (CF — Lukaku): target #9; hold up and lay off to `_7` (De Bruyne) / `_10` (Trossard), then attack the box to finish crosses and cutbacks (strength 18, shoot 17 — not a dropping false-9).
12. When team_phase is "defending": 4-5-1 mid-block; the `_9` (Lukaku) stays high as transition outball; do not press high unless trigger.
13. When ball is lost in own half: priority is the `_8` (Doku) outball — the `_6` (Raskin) or `_5` (Tielemans) pass long-diagonal to him.
14. Shoot from outside the box only if my `player_id` ends with `_7`, `_10`, or `_8` (De Bruyne/Trossard/Doku).

## Key Player Notes
- **Courtois (idx 0)** — world-class keeper restored to the spine (save 19). Belgium can afford a younger back line because he covers it; two big saves kept the Iran game level.
- **De Bruyne (idx 7)** — talisman, captain, and primary creator. Free role; everything goes through him. Now at Napoli; this is his last World Cup.
- **Doku (idx 8)** — explosive LW, back from paternity leave. License to dribble alone — Belgium will not double-up his side. Poor defensive discipline accepted. After two draws Belgium are leaning on him to unlock a deep block.
- **Lukaku (idx 9)** — fit again and back as the target #9 after starting vs Iran; hold-up play, attacks crosses and cutbacks. "We had plenty of chances, the ball just wouldn't go in" — Belgium need his finishing now.
- **Raskin (idx 6)** — energetic ball-winner partnering Tielemans with Onana rotated out; more press and recovery legs in the pivot.
- **Tielemans (idx 5)** — deep-lying build-up starter and secondary set-piece / penalty taker.
- **Meunier (idx 4)** — experienced, two-footed tournament veteran at RB; defensively reliable, pace declining.
- **Mechele / Theate (idx 2 / 3)** — CB pair: Mechele the calm aerial organiser, Theate the aggressive left-footed replacement for the suspended Ngoy.
- **Trossard (idx 10)** — under-rated; two-footed; can play any forward role.

## Tournament Mindset
Last dance for the Golden Generation core, and it has gone wrong so far. After a flat **1-1 draw with Egypt (MD1)** and a frustrating **0-0 with ten-man-disrupting Iran (MD2)** — Ngoy sent off, chances spurned — Belgium are **3rd in Group G on 2 points and MUST WIN vs New Zealand in Vancouver to qualify for the last 16.** New Zealand will defend deep, so the challenge is breaking a low block, not surviving pressure: Belgium must turn De Bruyne's distribution, Doku's dribbling and Lukaku's box presence into goals they failed to score in the first two games. Group G opponents: Egypt, Iran, New Zealand. Realistic ceiling if they survive: quarterfinal. The two draws exposed over-reliance on Doku and wasteful finishing — both must be fixed now.
