# Germany — Tactical Profile

## Identity & Philosophy
Julian Nagelsmann's Germany is positional, asymmetric, and intense — a synthesis of Bayern's juego de posición and RB's gegenpress. Possession is purposeful (zones, not numbers); the press is high and coordinated. Wirtz, Musiala, Sané and Havertz are the first-choice attacking spine, but **for Matchday 3 vs Ecuador the picture is different**: Germany have already topped Group E and qualified for the Round of 32, so Nagelsmann is rotating heavily — "it will probably be a mix," he said. Germany opened with a statement **7-1 over Curaçao** (Houston, June 14) — Nmecha, Schlotterbeck, Musiala and a Havertz brace (incl. penalty) plus Brown and Undav — then ground out a **2-1 comeback win over Ivory Coast** (Toronto, June 20) to seal first place on six points. That win came at a cost: **Nico Schlotterbeck is out for the rest of the tournament** with an ankle injury, forcing an enforced reshuffle at centre-back. The rotated XI for Ecuador (MetLife Stadium, East Rutherford, June 25) is a **4-3-3**: Baumann in goal, Rüdiger deputising for Schlotterbeck, a fresh midfield three of Goretzka, Stiller and Amiri, and an in-form front line of Leweling, Undav and Beier. The goal is to win the group in style and keep the first-choice spine rested — but the press and positional principles do not change.

## Formation
- Shape: 4-3-3 (rotated side) with a single pivot and two #8s; full-backs provide the width, wingers stay high and direct
- Role mapping (roster order in `germany.yaml`):
  - index 0: GK — Oliver Baumann (rotation keeper; calm distributor, commands his box)
  - index 1: LB — David Raum (high, energetic; overlapping width and whipped crosses — left-side attacking outlet)
  - index 2: LCB — Jonathan Tah (conservative anchor; aerial monster; the senior leader of a reshuffled back line)
  - index 3: RCB — Antonio Rüdiger (enforced starter for the injured Schlotterbeck; aggressive, front-foot defending, steps out to win it high)
  - index 4: RB — Waldemar Anton (steady, defensively solid; tucks in to form a back-three base when Raum overlaps)
  - index 5: LCM/#8 — Leon Goretzka (box-to-box dynamism; late arrivals into the box; shoot 15)
  - index 6: DM/#6 — Angelo Stiller (deep-lying playmaker; pass 18; the metronome who controls tempo from the base)
  - index 7: RCM/#8 — Nadiem Amiri (creative right-sided #8; carries and threads through-balls; takes on shots from the edge)
  - index 8: LW — Jamie Leweling (direct, speed 17; runs the channel and stretches the line on the left)
  - index 9: CF — Deniz Undav (in-form #9 — five goal contributions off the bench; sharp poacher and link man; primary penalty taker)
  - index 10: RW — Maximilian Beier (vertical, fast, two-footed; cuts inside to shoot or runs in behind)

## Style of Play

### Build-up
- Baumann central. Tah and Rüdiger split wide.
- In possession: Anton tucks inside to form a 3-2 base (Tah-Rüdiger plus Anton, with Stiller dropping) while Raum pushes high to provide left-side width → an effective 3-2-5.
- Stiller is the deepest controller; Goretzka and Amiri push forward as the two #8s flanking him.
- Raum drives the left-side attacking thrust with overlaps and crosses; Leweling can then drift inside.
- Patient, but the Stiller-to-runner connection looks to break lines vertically into the front three.

### Pressing
- **High press is Germany's identity** — Nagelsmann uses RB-Leipzig man-oriented pressing.
- Undav presses the central CB; Goretzka/Amiri man-jump the opp pivot; Leweling and Beier press the FBs.
- Trigger: any back-pass to the GK, any sideways pass between CBs.
- Counter-press: 5-second rule — nearest 3 players collapse on the carrier the moment ball is lost in opp half.

### Defensive shape
- When the press is broken, Germany falls into a 4-3-3 / 4-1-4-1 mid-block. Anton slots back to RB.
- High line; Tah and Rüdiger step up aggressively. Risky against pace, but Rüdiger's recovery speed helps.
- Wide forwards (Leweling, Beier) must track back — when they fail to, the FB-CB seam is exposed.

### Wide play
- More symmetric than the first-choice side, but still left-weighted:
  - **LEFT**: Raum (LB) overlaps high; Leweling drifts inside or holds width; Goretzka supports.
  - **RIGHT**: Anton stays tucked/conservative; Beier holds width and attacks 1v1; Amiri underlaps.
- The front three press and rotate; the two #8s provide the box arrivals.

### Final third
- Through-the-thirds: build to Stiller, then to Amiri/Goretzka between the lines, who find a diagonal runner or a winger in behind.
- Cutback target: Undav at the penalty spot.
- Late box arrivals: Goretzka, Amiri.
- Beier isolated 1v1 → Move toward defender + Move inside to shoot far-corner.

## Set Pieces
- Corners: Raum and Amiri are the primary takers. Inswingers toward the back post. Targets: Tah, Rüdiger, Undav.
- Direct FKs: Amiri and Raum deliver; Goretzka strikes the longer central efforts.
- Penalties: Undav is the nominated on-pitch taker (clinical finisher in form); Goretzka is the backup.
- Defending: zonal back-post wall, man-mark on Tah's nearest threat; Baumann commands the box.

## decide() Decision Priorities
1. When my role is GK: always short to a CB first. Step out of the box to sweep if a runner gets in behind — sweeper-keeper licensed.
2. When my `player_id` ends with `_1` (LB — Raum) and team has ball: push HIGH on the left; overlap when the `_8` (Leweling) drifts inside. Provide the left-side attacking width and whipped crosses.
3. When my `player_id` ends with `_4` (RB — Anton) and team_phase is "attacking": tuck inside to form a back-three base with the CBs; stay conservative — do not bomb forward both full-backs at once.
4. When my `player_id` ends with `_3` (RCB — Rüdiger) and pressure is low: step out aggressively to win the ball high; carry forward into midfield when space opens; pass to the `_6`/`_7` (Stiller/Amiri).
5. When my `player_id` ends with `_6` (DM — Stiller): drop between/behind the CBs to receive in build-up (form a back-3 base); spray the play; never above halfway in open play — be the metronome.
6. When my `player_id` ends with `_5` (#8 — Goretzka): box-to-box; late box arrivals from the left half-space; my late run is the disguise behind the front three.
7. When my `player_id` ends with `_7` (#8 — Amiri): receive between lines on the right; turn forward; Pass vertically to the `_9`/`_10`/`_8` (Undav/Beier/Leweling); Shoot from 18-22m.
8. When my `player_id` ends with `_8` (LW — Leweling): stay direct on the left; on-ball 1v1 with the RB, Move toward + Move past; drift inside to combine with the `_9` (Undav); Shoot near post.
9. When my `player_id` ends with `_10` (RW — Beier): stay vertical, hug the touchline; on-ball 1v1, Move toward + Move inside to shoot far-corner; run in behind on the diagonal.
10. When my `player_id` ends with `_9` (CF — Undav): press the CB first; in possession drop short and link, then spin in behind; late run for cutbacks; take the penalty if awarded.
11. When team loses possession in opponent half: 5-second counter-press — nearest 3 players Move toward carrier; closest Tackle.
12. When opponent plays back to their GK: full press — the `_9` and `_5`/`_7` (Undav + Goretzka/Amiri) step up immediately; wingers jump opp FBs.
13. Hold the high line — when opponent passes backward, CBs Move forward in sync.

## Key Player Notes
- **Stiller (idx 6)** — the rotated side's brain; single pivot, deep-lying playmaker with pass 18. He sets the tempo and drops to make a back-three in build-up.
- **Undav (idx 9)** — in-form #9 rewarded with a start; clinical poacher with five goal contributions off the bench across the group stage; nominated penalty taker.
- **Rüdiger (idx 3)** — enforced starter at RCB after Schlotterbeck's tournament-ending ankle injury; front-foot defending and recovery pace to protect the high line.
- **Raum (idx 1)** — left-side attacking outlet; overlaps high and delivers crosses; primary set-piece deliverer from the left.
- **Goretzka (idx 5)** — experienced box-to-box #8; late runs into the box and a shooting threat from range.
- **Beier & Leweling (idx 10 & 8)** — fast, direct wingers who run in behind and stretch the Ecuadorian back line; the verticality that keeps the press honest.
- **Baumann (idx 0)** — rotation keeper; calm distributor who starts build-up and commands his box; step out to sweep behind the high line.

## Tournament Mindset
Already qualified as group winners, Germany approach Ecuador to **finish the group in style while protecting the first-choice spine**. Nagelsmann rests Neuer, Kimmich, Wirtz, Musiala, Sané and Havertz, trusting a deep, hungry second unit to maintain the same high-press, possession-heavy identity. The enforced loss of Schlotterbeck is the one cloud, but Rüdiger steps in seamlessly. Ecuador need a first-ever win over Germany to advance — Germany want to deny them and send a message about their squad depth ahead of the knockouts. Chasing a record-equalling fifth World Cup, even the rotated side should impose itself; risky against fast counter-attackers, but on song, the most positionally sophisticated squad in the tournament from front to back.
