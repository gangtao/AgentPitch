# Belgium — Tactical Profile

## Identity & Philosophy
Rudi García's Belgium is the post-Golden-Generation team: still talented, still anchored by De Bruyne, Lukaku, and Doku, but no longer young or pressing-fit. The style has shifted from Roberto Martinez's possession-heavy 3-4-3 to a more pragmatic 4-2-3-1 built around De Bruyne's distribution, Doku's dribbling, and Lukaku's hold-up play. Less press, more transition. The back line is a younger rebuild (De Winter, De Cuyper) screened by a double pivot. Recent results: failed Euro 2024 round of 16 exit to France; qualifying for 2026 has been functional rather than dominant. Courtois back in goal is the single biggest upgrade on the spine.

## Formation
- Shape: 4-2-3-1 (double pivot + De Bruyne as a clear #10; shifts to 4-3-3 vs weaker sides)
- Role mapping (roster order in `belgium.yaml`):
  - index 0: GK — Thibaut Courtois (world-class shot-stopper; save 19 — elite, the spine's biggest upgrade)
  - index 1: LB — Maxim De Cuyper (modern, energetic FB; stamina 17 — gets forward more than the old LB)
  - index 2: LCB — Arthur Theate (steady, defensively responsible; now central rather than at LB)
  - index 3: RCB — Koni De Winter (younger CB; strength 16 — physical anchor of the rebuilt line)
  - index 4: RB — Thomas Meunier (experienced, defensively reliable, occasional overlapping run)
  - index 5: DM/#6 — Youri Tielemans (captain; deep playmaker; pass 17 — left of the pivot, build-up starter)
  - index 6: DM/#8 — Amadou Onana (the destroyer; strength 17; ball-winner; tucks in front of CBs)
  - index 7: AM/#10 — Kevin De Bruyne (the engine; pass 20, skill 19 — Belgium's one true superstar)
  - index 8: LW — Jérémy Doku (dribble 19, speed 19 — direct, isolated 1v1 specialist)
  - index 9: CF — Romelu Lukaku (target #9; strength 18, shoot 17 — physical battle CF)
  - index 10: RW — Leandro Trossard (inverted, intelligent, two-footed finisher)

## Style of Play

### Build-up
- Courtois long to Lukaku when pressed; short to De Winter or Theate otherwise (Courtois is comfortable starting build-up).
- Tielemans drops to receive from CBs and progress; Onana stays as the deeper shield.
- De Cuyper (LB) pushes higher than Meunier (RB); both still stay more conservative than the elite teams — wide, but rarely above the halfway line until late phases.
- De Bruyne drops into the right half-space pocket to receive — Belgium's primary progression is through him.

### Pressing
- **Belgium DOES NOT press intensely.** Ageing core (De Bruyne, Lukaku, Meunier) cannot sustain a high press 90 minutes.
- Mid-block primarily — 4-5-1 / 4-3-3.
- Press triggers: only on opp throw-ins or back-passes to the GK; otherwise contain.
- This is a defining tactical difference from Spain/Germany/Netherlands — Belgium accepts opponent possession.

### Defensive shape
- 4-5-1 mid-block. Lukaku alone up top; De Bruyne drops to right-mid in defense.
- Doku has poor defensive discipline (discipline 12) — he often fails to track back, which leaves De Cuyper exposed.
- CBs hold a moderate line (~ 45%); Onana sits in front of them.

### Wide play
- **LEFT** is the explosive side: Doku in isolation 1v1; De Cuyper underlaps when Doku holds width; opposite-side overload from Trossard.
- **RIGHT** is the structured side: Trossard cuts inside, Meunier overlaps occasionally, De Bruyne drifts into the half-space.
- Belgium's most effective attacks come from giving Doku the ball wide and letting him decide alone.

### Final third
- Termination patterns:
  1. **De Bruyne assist** — diagonal cross / cutback from right half-space to Lukaku.
  2. **Doku isolation** — beat the LB, cut inside, finish or cutback to Lukaku.
  3. **Lukaku hold-up** — long ball, lay-off to De Bruyne or Trossard.
- Transitions: when Belgium wins the ball in their own half, the immediate outball is Doku on the left.

## Set Pieces
- Corners: De Bruyne primary taker (pass 20); Tielemans and Trossard alternates. Targets: Lukaku (penalty spot), De Winter (near post), Onana (back post).
- Direct FKs: De Bruyne for any centered or right-side, Tielemans for left-side; Doku an option for direct efforts.
- Penalties: De Bruyne first, then Tielemans, then Lukaku.
- Defending: man-mark biggest threats; zonal at near post; Courtois commands his box and is elite in the air and on the line.

## decide() Decision Priorities
1. When my role is GK (Courtois): short to CB by default; long-ball to the `_9` (Lukaku) if double-pressed — physical battle in the air is an outcome we accept. Elite shot-stopper — commit late, command the box on crosses.
2. When my `player_id` ends with `_3` (RCB — De Winter): physical anchor of the rebuilt line; carry the ball forward when a lane opens; otherwise pass to the `_5` (Tielemans) or the `_7` (De Bruyne) between lines.
3. When my `player_id` ends with `_2` (LCB — Theate): the more comfortable ball-player of the two CBs; conservative but can step out and progress; long ball forward is acceptable.
4. When my `player_id` ends with `_1` (LB — De Cuyper): more adventurous than the RB — underlap/overlap the `_8` (Doku) when team_phase is "attacking" AND ball is on left flank; otherwise hold LB height and stay disciplined.
5. When my `player_id` ends with `_4` (RB — Meunier): occasional overlap when the `_10` (Trossard) cuts inside; otherwise stay disciplined and deep.
6. When my `player_id` ends with `_6` (DM — Onana): destroy and recycle. Stay in front of CBs at all times. Tackle aggressively — strength 17, ball-winner.
7. When my `player_id` ends with `_5` (DM — Tielemans): drop to receive; pass forward to the `_7` (De Bruyne) or wide to the `_8` (Doku); be the build-up starter.
8. When my `player_id` ends with `_7` (#10 — De Bruyne): drift into right half-space; receive between lines; THROUGH-BALL to the `_9` (Lukaku) is the primary action; Shoot 22m+ if no pass available.
9. When my `player_id` ends with `_8` (LW — Doku): hug LW touchline; on-ball 1v1, Move toward LB then Move diagonally inside (dribble 19 — take the duel always); Shoot from 18m onto right foot.
10. When my `player_id` ends with `_10` (RW — Trossard): inverted — cut inside onto right foot OR through-ball the `_9` (Lukaku); second runner into the box.
11. When my `player_id` ends with `_9` (CF — Lukaku): stay central in the box; physical hold-up; near-post run on `_7` (De Bruyne) crosses; Move toward defender to win aerials.
12. When team_phase is "defending": 4-5-1 mid-block; the `_9` (Lukaku) stays high as outball; do not press high unless trigger.
13. When ball is lost in own half: priority is the `_8` (Doku) outball — the `_6` (Onana) or `_5` (Tielemans) pass long-diagonal to him.
14. Shoot from outside the box only if my `player_id` ends with `_7`, `_10`, or `_8` (De Bruyne/Trossard/Doku).

## Key Player Notes
- **Courtois (idx 0)** — world-class keeper restored to the spine (save 19). Belgium can afford a younger back line because he covers it.
- **De Bruyne (idx 7)** — talisman, primary creator. Free role; everything goes through him. (Tielemans, idx 5, wears the captain's armband.)
- **Doku (idx 8)** — explosive LW. License to dribble alone — Belgium will not double-up his side. Poor defensive discipline accepted.
- **Lukaku (idx 9)** — target #9. Hold-up is more valuable than goals.
- **Onana (idx 6)** — Belgium's defensive midfielder backbone — without him, midfield gets overrun.
- **Trossard (idx 10)** — under-rated; two-footed; can play any forward role.

## Tournament Mindset
Last dance for the Golden Generation. Belgium expects to be a counter-attacking, transition-based team that wins through De Bruyne's distribution and Doku's runs. Realistic ceiling: quarterfinal. Vulnerable to teams that press them — Belgium will not press back.
