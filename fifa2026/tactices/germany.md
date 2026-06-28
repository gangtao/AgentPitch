# Germany — Tactical Profile

## Identity & Philosophy
Julian Nagelsmann's Germany is positional, asymmetric, and intense — a synthesis of Bayern's juego de posición and RB's gegenpress. Possession is purposeful (zones, not numbers); the press is high and coordinated. For the **Round of 32 vs Paraguay** (Gillette Stadium, Foxborough, June 29), the **first-choice spine returns**: after rotating heavily in the dead-rubber 2-1 loss to Ecuador, Nagelsmann restores Neuer, Kimmich, the Wirtz–Musiala–Sané attacking band and Havertz. Germany topped Group E on six points — a statement **7-1 over Curaçao** (Houston, June 14) and a battling **2-1 comeback over Ivory Coast** (Toronto, June 20) — before resting their stars against Ecuador. The one enforced change: **Nico Schlotterbeck is out for the rest of the tournament** (ankle, suffered vs Ivory Coast), so **Antonio Rüdiger partners Jonathan Tah** at centre-back. **Nathaniel Brown** (Eintracht Frankfurt) is cleared to start at left-back after a muscular issue kept him out of the Ecuador match. The shape sharpens to a **4-2-3-1** for the knockouts: a Pavlović–Nmecha double pivot screens the back four, Musiala plays as the free #10 behind Havertz, and Wirtz/Sané invert from the flanks. The press and positional principles do not change — now with the elite ball-players back on the pitch.

## Formation
- Shape: 4-2-3-1 with a double pivot; full-backs (Kimmich, Brown) provide width, the front band of Sané/Musiala/Wirtz rotates freely behind a lone #9
- Role mapping (roster order in `germany.yaml`):
  - index 0: GK — Manuel Neuer (sweeper-keeper; elite distributor, commands his box and starts build-up)
  - index 1: LB — Nathaniel Brown (high, energetic; overlapping width and crosses — left-side attacking outlet)
  - index 2: LCB — Jonathan Tah (aerial monster; the senior anchor of the reshuffled back line)
  - index 3: RCB — Antonio Rüdiger (enforced starter for the injured Schlotterbeck; aggressive front-foot defending, recovery pace, steps out to win it high)
  - index 4: RB — Joshua Kimmich (inverts into midfield in possession; pass 19 — the right-sided build-up brain and primary set-piece taker)
  - index 5: DM/#6 — Aleksandar Pavlović (deep-lying playmaker; pass 18; the metronome who controls tempo from the base)
  - index 6: CM/#8 — Felix Nmecha (box-to-box dynamism; late arrivals into the box; carries through the lines)
  - index 7: LW — Leroy Sané (speed 18; direct, two-footed; runs in behind and cuts inside to shoot)
  - index 8: CAM/#10 — Jamal Musiala (free roaming creator; skill/dribble 19; the chief chance creator between the lines)
  - index 9: RW — Florian Wirtz (inverted right winger; pass/skill elite; combines and threads the killer ball, arrives late in the box)
  - index 10: CF — Kai Havertz (lone #9; clever link play, runs the channels, finishes; primary penalty taker)

## Style of Play

### Build-up
- Neuer central; Tah and Rüdiger split wide.
- In possession: **Kimmich inverts** into midfield to form a 3-2 base (Tah-Rüdiger plus Pavlović, with Nmecha advancing) while Brown pushes high to provide left-side width → an effective 3-2-5.
- Pavlović is the deepest controller; Nmecha pushes forward as the advanced #8.
- Brown drives the left-side attacking thrust with overlaps and crosses; Sané can then drift inside.
- Patient, but the Pavlović/Kimmich-to-runner connection looks to break lines vertically into Musiala and the front band.

### Pressing
- **High press is Germany's identity** — Nagelsmann uses RB-Leipzig man-oriented pressing.
- Havertz presses the central CB; Musiala/Nmecha man-jump the opp pivot; Sané and Wirtz press the FBs.
- Trigger: any back-pass to the GK, any sideways pass between CBs.
- Counter-press: 5-second rule — nearest 3 players collapse on the carrier the moment ball is lost in opp half.

### Defensive shape
- When the press is broken, Germany falls into a 4-2-3-1 / 4-4-2 mid-block. Kimmich slots back to RB.
- High line; Tah and Rüdiger step up aggressively. Risky against pace, but Rüdiger's recovery speed helps.
- Wide forwards (Sané, Wirtz) must track back — when they fail to, the FB-CB seam is exposed.

### Wide play
- Asymmetric and left-weighted in attack:
  - **LEFT**: Brown (LB) overlaps high; Sané drifts inside or runs in behind; Musiala drifts left to combine.
  - **RIGHT**: Kimmich tucks inside as a playmaker; Wirtz inverts and underlaps, arriving in the box.
- The front band rotates fluidly; Nmecha provides the box arrivals from deep.

### Final third
- Through-the-thirds: build to Pavlović/Kimmich, then to Musiala/Wirtz between the lines, who find a diagonal runner or a winger in behind.
- Cutback target: Havertz at the penalty spot.
- Late box arrivals: Nmecha, Wirtz.
- Sané isolated 1v1 → Move toward defender + Move inside to shoot far-corner, or run in behind on the diagonal.

## Set Pieces
- Corners: Kimmich is the primary taker; Wirtz and Brown deliver the alternates. Inswingers toward the back post. Targets: Tah, Rüdiger, Havertz.
- Direct FKs: Kimmich and Wirtz deliver; Sané strikes the longer central efforts.
- Penalties: Havertz is the nominated on-pitch taker (penalty 16); Kimmich is the backup.
- Defending: zonal back-post wall, man-mark on Tah's nearest threat; Neuer commands the box.

## decide() Decision Priorities
1. When my role is GK: always short to a CB first. Step out of the box to sweep if a runner gets in behind — sweeper-keeper licensed.
2. When my `player_id` ends with `_1` (LB — Brown) and team has ball: push HIGH on the left; overlap when the `_7` (Sané) drifts inside. Provide the left-side attacking width and whipped crosses.
3. When my `player_id` ends with `_4` (RB — Kimmich) and team_phase is "attacking": invert into midfield to form a 3-2 base; orchestrate from the right half-space; spray the play and deliver set pieces — do not bomb both full-backs forward at once.
4. When my `player_id` ends with `_3` (RCB — Rüdiger) and pressure is low: step out aggressively to win the ball high; carry forward into midfield when space opens; pass to the `_5`/`_4` (Pavlović/Kimmich).
5. When my `player_id` ends with `_5` (DM — Pavlović): drop between/behind the CBs to receive in build-up (form a back-3 base); spray the play; never above halfway in open play — be the metronome.
6. When my `player_id` ends with `_6` (#8 — Nmecha): box-to-box; late box arrivals from the half-space; carry through the lines; my late run is the disguise behind the front band.
7. When my `player_id` ends with `_8` (CAM — Musiala): receive between lines and roam free; turn forward; dribble at the defense (skill 19); Pass vertically to the `_10`/`_7`/`_9` (Havertz/Sané/Wirtz); Shoot from 18-22m.
8. When my `player_id` ends with `_7` (LW — Sané): stay direct on the left; on-ball 1v1 with the RB, Move toward + Move past; run in behind on the diagonal; cut inside and Shoot far-corner.
9. When my `player_id` ends with `_9` (RW — Wirtz): invert from the right; combine with Kimmich/Musiala; thread the killer ball to the `_10` (Havertz); arrive late in the box to Shoot.
10. When my `player_id` ends with `_10` (CF — Havertz): press the CB first; in possession drop short and link, then spin in behind; late run for cutbacks; take the penalty if awarded.
11. When team loses possession in opponent half: 5-second counter-press — nearest 3 players Move toward carrier; closest Tackle.
12. When opponent plays back to their GK: full press — the `_10` and `_8`/`_6` (Havertz + Musiala/Nmecha) step up immediately; wingers jump opp FBs.
13. Hold the high line — when opponent passes backward, CBs Move forward in sync.

## Key Player Notes
- **Musiala (idx 8)** — the free #10 and chief creator; skill/dribble 19. Roams between the lines, beats defenders off the dribble, and unlocks the final third.
- **Wirtz (idx 9)** — inverted right winger with elite passing and skill; combines, threads the killer ball, and arrives late in the box.
- **Sané (idx 7)** — speed 18 on the left; direct 1v1, runs in behind, cuts in to shoot — the verticality that keeps the press honest.
- **Kimmich (idx 4)** — the right-sided brain; inverts to a 3-2 base, pass 19, and is the primary set-piece deliverer; backup penalty taker.
- **Pavlović (idx 5)** — single deep pivot, deep-lying playmaker with pass 18; sets the tempo and drops to make a back-three in build-up.
- **Rüdiger (idx 3)** — enforced starter at RCB after Schlotterbeck's tournament-ending ankle injury; front-foot defending and recovery pace to protect the high line.
- **Havertz (idx 10)** — lone #9; clever link play, channel runs and finishing; nominated penalty taker (penalty 16).
- **Neuer (idx 0)** — sweeper-keeper; elite distributor who starts build-up and commands his box; steps out to sweep behind the high line.

## Tournament Mindset
The group is won; the knockouts begin. Germany restore the **first-choice spine** for Paraguay — Neuer, Kimmich, Wirtz, Musiala, Sané and Havertz all return after the rotated Ecuador defeat — trusting their elite ball-players to impose the same high-press, possession-heavy identity at full strength. The enforced loss of Schlotterbeck is the one cloud, but Rüdiger steps in seamlessly alongside Tah. Paraguay are organised, physical and counter-attacking; the danger is the space behind a high line against quick transitions, where Rüdiger's recovery pace and Neuer's sweeping are the insurance. Chasing a record-equalling fifth World Cup, Germany want a controlled, professional win to set up the Round of 16 — the most positionally sophisticated squad in the tournament, now with its first XI back on the pitch.
