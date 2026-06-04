# Germany — Tactical Profile

## Identity & Philosophy
Julian Nagelsmann's Germany is positional, asymmetric, and intense — a synthesis of Bayern's juego de posición and RB's gegenpress. Possession is purposeful (zones, not numbers); the press is high and coordinated; the wide structure is deliberately asymmetric (Kimmich inverts, Raum stays wide). Wirtz & Musiala are the on-ball stars; Havertz is the structural CF. The defining pre-tournament story is the return from international retirement of 40-year-old Manuel Neuer, restored as Nagelsmann's first-choice keeper and captain alongside skipper Joshua Kimmich. Recent results: Euro 2024 quarterfinal exit on home soil rebuilt confidence; qualifying since has been dominant.

## Formation
- Shape: 4-2-3-1 with asymmetric width (Kimmich inverts from RB → RCM in possession; effective 3-2-5 in attack)
- Role mapping (roster order in `germany.yaml`):
  - index 0: GK — Manuel Neuer (sweeper-keeper; pass 16; experienced build-up node and box commander)
  - index 1: LB — David Raum (stays wide and high; left-flank crosser)
  - index 2: LCB — Jonathan Tah (more conservative anchor; covers Kimmich's vacated zone)
  - index 3: RCB — Nico Schlotterbeck (aggressive, left-footed ball-player; carries and steps into midfield)
  - index 4: RB — Joshua Kimmich (captain; inverts to RCM; pass 18, skill 18 — the brain when he steps inside)
  - index 5: DM/#6 — Aleksandar Pavlović (left of double pivot; deeper, controlling)
  - index 6: DM/#8 — Leon Goretzka (right of double pivot; box-to-box; late box arrivals)
  - index 7: AM/#10 — Florian Wirtz (the free #10; floats between lines; primary creator)
  - index 8: LW (drifting) — Jamal Musiala (nominal LW but drifts inside as second #10; ball-carrier supreme; dribble 19)
  - index 9: RW — Leroy Sané (vertical, speed 18; stretches the line)
  - index 10: CF — Kai Havertz (structural CF — drops, links, runs the channel; aerial threat too)

## Style of Play

### Build-up
- Neuer central. Tah and Schlotterbeck split wide.
- In possession: Kimmich steps inside from RB to form a 3-2 base (Tah-Schlotterbeck-Raum back, Kimmich-Pavlović pivot) → 3-2-5 with Wirtz, Musiala, Sané, Havertz and Goretzka in 5-line.
- Raum stays HIGH on left as winger-FB hybrid; this is why Musiala drifts inside (no conflict for wide space).
- Patient, but Wirtz-Musiala connection looks to break lines vertically.

### Pressing
- **High press is Germany's identity** — Nagelsmann uses RB-Leipzig man-oriented pressing.
- Havertz presses the central CB; Wirtz man-jumps the deepest opp midfielder; Sané and Musiala cover the FBs.
- Trigger: any back-pass to the GK, any sideways pass between CBs.
- Counter-press: 5-second rule — nearest 3 players collapse on the carrier the moment ball is lost in opp half.

### Defensive shape
- When the press is broken, Germany falls into a 4-2-3-1 mid-block. Kimmich slots back to RB.
- High line; Tah and Schlotterbeck step up aggressively. Risky against pace.
- Wide mids (Musiala, Sané) must track back — sometimes Musiala fails to, which leaves the LCB-LB seam exposed.

### Wide play
- Strictly asymmetric:
  - **LEFT**: Raum (LB) is the only wide source; Musiala drifts inside; overload central.
  - **RIGHT**: Kimmich inverts; Sané holds width; Goretzka makes the underlapping run.
- This is the **5-3-2-on-attack asymmetry** that Nagelsmann is known for.

### Final third
- Through-the-thirds: build to Wirtz between the lines, who finds Musiala running diagonal or Sané in behind.
- Cutback target: Havertz at penalty spot.
- Late box arrivals: Goretzka, Wirtz.
- Sané isolated 1v1 → Move toward defender + Move inside to shoot far-corner.

## Set Pieces
- Corners: Kimmich is the primary taker. Inswingers from the right (left foot from the right corner). Targets: Tah, Schlotterbeck, Havertz, Goretzka.
- Direct FKs: Kimmich centrally and right-side; Raum on the left.
- Defending: zonal back-post wall, man-mark on Tah's nearest threat; Neuer commands the box.

## decide() Decision Priorities
1. When my role is GK: always short to a CB first. Step out of the box to sweep if a runner gets in behind — sweeper-keeper licensed.
2. When my `player_id` ends with `_4` (RB — Kimmich) and team has ball: invert to RCM height — this is non-negotiable when team_phase is "attacking". Behave like a midfielder.
3. When my `player_id` ends with `_1` (LB — Raum): stay HIGH and WIDE — provide the only left-side touchline width. If the `_8` (Musiala) vacates left, push to LW position.
4. When my `player_id` ends with `_3` (RCB — Schlotterbeck, left-footed ball-player) and pressure is low: carry the ball forward into midfield; pass to the `_7` (Wirtz) between lines.
5. When my `player_id` ends with `_5` (DM — Pavlović): drop between CBs when the `_4` (Kimmich) inverts (form a back-3 base in build); never above halfway in open play.
6. When my `player_id` ends with `_6` (#8 — Goretzka): late box arrivals from right half-space; my late run is the disguise behind the `_7` (Wirtz).
7. When my `player_id` ends with `_7` (#10 — Wirtz): receive between lines; turn forward; Pass vertically to the `_8`/`_10`/`_9` (Musiala/Havertz/Sané); Shoot from 18-22m.
8. When my `player_id` ends with `_8` (LW — Musiala): drift inside to the left half-space; on-ball, dribble inside; combine with the `_7` (Wirtz); Shoot from inside the box.
9. When my `player_id` ends with `_9` (RW — Sané): stay vertical, hug touchline; on-ball 1v1 with LB, Move toward + Move past; Shoot near post.
10. When my `player_id` ends with `_10` (CF — Havertz): press the CB first; in possession drop short and turn; late run for cutbacks.
11. When team loses possession in opponent half: 5-second counter-press — nearest 3 players Move toward carrier; closest Tackle.
12. When opponent plays back to their GK: full press — the `_10` and `_7` (Havertz + Wirtz) step up immediately; FBs jump opp FBs.
13. Hold the high line — when opponent passes backward, CBs Move forward in sync.

## Key Player Notes
- **Kimmich (idx 4)** — inverted FB; he is the structural genius. In open play he is a midfielder, not a defender.
- **Wirtz (idx 7)** — primary creator. Free role between lines.
- **Musiala (idx 8)** — ball-carrying weapon. Drifts inside from LW into the left half-space.
- **Havertz (idx 10)** — works as the structural CF; not pure goalscorer, but the link.
- **Neuer (idx 0)** — returning captain and sweeper-keeper; commands the box and starts build-up; treat him as a reliable extra passer but step out to sweep behind the high line.

## Tournament Mindset
Aggressive from kickoff. Nagelsmann wants Germany to dominate the ball AND the territory — no compromise. Risky against fast counter-attackers, but on song, the most positionally sophisticated team in the tournament.
