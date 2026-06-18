# Germany — Tactical Profile

## Identity & Philosophy
Julian Nagelsmann's Germany is positional, asymmetric, and intense — a synthesis of Bayern's juego de posición and RB's gegenpress. Possession is purposeful (zones, not numbers); the press is high and coordinated; the wide structure is deliberately asymmetric (Kimmich, now the captain, inverts from RB while the left back overlaps). Wirtz & Musiala are the on-ball stars; Havertz is the structural CF and first-choice #9. The defining pre-tournament story was the return from international retirement of 40-year-old Manuel Neuer, restored as Nagelsmann's first-choice keeper. Germany opened the World Cup with a statement: **7-1 over Curaçao** in Houston on June 14, 2026 — Nmecha and Schlotterbeck on target, Havertz a brace (incl. penalty), Musiala a goal, plus Brown and Undav. The selection that flexed in that match — Nathaniel Brown at LB, Felix Nmecha alongside Pavlović in the pivot, Musiala central with Wirtz left and Sané right — is the working first XI for Matchday 2 vs Ivory Coast (Toronto, June 20).

## Formation
- Shape: 4-2-3-1 with asymmetric width (Kimmich inverts from RB → RCM in possession; effective 3-2-5 in attack)
- Role mapping (roster order in `germany.yaml`):
  - index 0: GK — Manuel Neuer (sweeper-keeper; pass 16; experienced build-up node and box commander)
  - index 1: LB — Nathaniel Brown (high, energetic; underlapping runs and recovery pace — Germany's left-side X-factor; scored vs Curaçao)
  - index 2: LCB — Jonathan Tah (more conservative anchor; covers Kimmich's vacated zone; aerial monster)
  - index 3: RCB — Nico Schlotterbeck (aggressive, left-footed ball-player; carries and steps into midfield; scored vs Curaçao)
  - index 4: RB — Joshua Kimmich (captain; inverts to RCM; pass 18, skill 18 — the brain when he steps inside)
  - index 5: DM/#6 — Aleksandar Pavlović (left of double pivot; deeper, controlling)
  - index 6: DM/#8 — Felix Nmecha (right of double pivot; box-to-box dynamism; late box arrivals — opened the scoring vs Curaçao)
  - index 7: LW — Florian Wirtz (nominal LW but floats inside as a free #10; primary creator; assisted Nmecha's opener)
  - index 8: AM/#10 — Jamal Musiala (central free role; ball-carrier supreme; dribble 19; drifts to find pockets)
  - index 9: RW — Leroy Sané (vertical, speed 18; stretches the line)
  - index 10: CF — Kai Havertz (structural CF — drops, links, runs the channel; aerial threat; primary on-pitch penalty taker)

## Style of Play

### Build-up
- Neuer central. Tah and Schlotterbeck split wide.
- In possession: Kimmich steps inside from RB to form a 3-2 base (Tah-Schlotterbeck-Brown back, Kimmich-Pavlović pivot) → 3-2-5 with Wirtz, Musiala, Sané, Havertz and Nmecha in the 5-line.
- Brown pushes HIGH on the left and underlaps into the half-space — he carries the left-side attacking thrust, freeing Wirtz to float inside.
- Patient, but the Wirtz-Musiala connection looks to break lines vertically.

### Pressing
- **High press is Germany's identity** — Nagelsmann uses RB-Leipzig man-oriented pressing.
- Havertz presses the central CB; Musiala/Wirtz man-jump the deepest opp midfielder; Sané and Brown cover the FBs.
- Trigger: any back-pass to the GK, any sideways pass between CBs.
- Counter-press: 5-second rule — nearest 3 players collapse on the carrier the moment ball is lost in opp half.

### Defensive shape
- When the press is broken, Germany falls into a 4-2-3-1 mid-block. Kimmich slots back to RB.
- High line; Tah and Schlotterbeck step up aggressively. Risky against pace.
- Wide attackers (Wirtz, Sané) must track back — when they fail to, the LCB-LB seam is exposed.

### Wide play
- Strictly asymmetric:
  - **LEFT**: Brown (LB) provides the overlap/underlap; Wirtz drifts inside; overload central.
  - **RIGHT**: Kimmich inverts; Sané holds width; Nmecha makes the underlapping run.
- This is the asymmetric 3-2-5-on-attack shape that Nagelsmann is known for.

### Final third
- Through-the-thirds: build to Wirtz/Musiala between the lines, who find a diagonal runner or Sané in behind.
- Cutback target: Havertz at penalty spot.
- Late box arrivals: Nmecha, Wirtz.
- Sané isolated 1v1 → Move toward defender + Move inside to shoot far-corner.

## Set Pieces
- Corners: Kimmich is the primary taker. Inswingers from the right (left foot from the right corner). Wirtz and Brown are alternates. Targets: Tah, Schlotterbeck, Havertz.
- Direct FKs: Kimmich centrally and right-side; Wirtz and Havertz also deliver.
- Penalties: Kimmich is the nominated first taker (scored the qualifier vs Luxembourg), but Havertz took and converted the spot-kick vs Curaçao — treat Havertz as the on-pitch taker when he is on the field, Kimmich otherwise.
- Defending: zonal back-post wall, man-mark on Tah's nearest threat; Neuer commands the box.

## decide() Decision Priorities
1. When my role is GK: always short to a CB first. Step out of the box to sweep if a runner gets in behind — sweeper-keeper licensed.
2. When my `player_id` ends with `_4` (RB — Kimmich) and team has ball: invert to RCM height — this is non-negotiable when team_phase is "attacking". Behave like a midfielder.
3. When my `player_id` ends with `_1` (LB — Brown): push HIGH on the left; overlap when the `_7` (Wirtz) drifts inside, or underlap into the left half-space. Provide the left-side attacking width.
4. When my `player_id` ends with `_3` (RCB — Schlotterbeck, left-footed ball-player) and pressure is low: carry the ball forward into midfield; pass to the `_7`/`_8` (Wirtz/Musiala) between lines.
5. When my `player_id` ends with `_5` (DM — Pavlović): drop between CBs when the `_4` (Kimmich) inverts (form a back-3 base in build); never above halfway in open play.
6. When my `player_id` ends with `_6` (#8 — Nmecha): box-to-box; late box arrivals from the right half-space; my late run is the disguise behind the `_8` (Musiala).
7. When my `player_id` ends with `_7` (LW — Wirtz): drift inside to receive between lines; turn forward; Pass vertically to the `_8`/`_10`/`_9` (Musiala/Havertz/Sané); Shoot from 18-22m.
8. When my `player_id` ends with `_8` (#10 — Musiala): roam centrally into pockets; on-ball, dribble at the defender; combine with the `_7` (Wirtz); Shoot from inside the box.
9. When my `player_id` ends with `_9` (RW — Sané): stay vertical, hug touchline; on-ball 1v1 with LB, Move toward + Move past; Shoot near post.
10. When my `player_id` ends with `_10` (CF — Havertz): press the CB first; in possession drop short and turn; late run for cutbacks; take the penalty if awarded.
11. When team loses possession in opponent half: 5-second counter-press — nearest 3 players Move toward carrier; closest Tackle.
12. When opponent plays back to their GK: full press — the `_10` and `_7`/`_8` (Havertz + Wirtz/Musiala) step up immediately; FBs jump opp FBs.
13. Hold the high line — when opponent passes backward, CBs Move forward in sync.

## Key Player Notes
- **Kimmich (idx 4)** — captain and inverted FB; he is the structural genius. In open play he is a midfielder, not a defender. Nominated penalty/FK/corner taker.
- **Wirtz (idx 7)** — primary creator. Free role: nominally LW but drifts inside between the lines.
- **Musiala (idx 8)** — ball-carrying weapon in the central #10 role; tormented Curaçao for 45 minutes and scored after the break.
- **Nmecha (idx 6)** — dynamic box-to-box #8 who beat out Goretzka for the pivot spot; opened the scoring vs Curaçao with a Wirtz-assisted finish.
- **Brown (idx 1)** — 22-year-old Eintracht Frankfurt LB and Germany's left-side X-factor; recovery pace and underlapping runs; scored his first international goal vs Curaçao.
- **Havertz (idx 10)** — structural CF and first-choice #9; links play, runs the channel, and converted the on-pitch penalty vs Curaçao.
- **Neuer (idx 0)** — returning keeper; commands the box and starts build-up; treat him as a reliable extra passer but step out to sweep behind the high line.

## Tournament Mindset
Aggressive from kickoff. Nagelsmann wants Germany to dominate the ball AND the territory — no compromise. The 7-1 opener vs Curaçao confirmed the attacking blueprint; chasing a record-equalling fifth World Cup, they will impose the same high-press, possession-heavy game on Ivory Coast. Risky against fast counter-attackers, but on song, the most positionally sophisticated team in the tournament.
