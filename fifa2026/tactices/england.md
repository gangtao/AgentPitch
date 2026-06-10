# England — Tactical Profile

## Identity & Philosophy
Thomas Tuchel's England is methodical, defensively organized, and ruthlessly effective at set pieces. Out are Southgate's tournament-pragmatist instincts; in is Tuchel's structured possession with clear positional rules, a defined press, and a strong identity in transition. Set-piece danger remains world-class. Recent results: Euro 2024 final under Southgate, qualifying campaign under Tuchel cleaned up the defensive issues — England now concedes very rarely.

## Formation
- Shape: 4-3-3 (Rice at the base of a midfield three for control)
- Role mapping (roster order in `england.yaml`):
  - index 0: GK — Jordan Pickford (vocal, distribution-savvy, big-moment saves)
  - index 1: LB — Nico O'Reilly (converted midfielder; tall, physical, left-footed; inverts or overlaps)
  - index 2: LCB — Marc Guéhi (physical, left-footed for balance; aerial duels)
  - index 3: RCB — John Stones (ball-progressor; pass 17, sometimes steps into midfield)
  - index 4: RB — Ezri Konsa (composed, defense-first; tucks in to form a back three in possession)
  - index 5: DM/#6 — Declan Rice (anchor of the three; box-to-box engine; tackles, late box arrivals)
  - index 6: CM/#8 — Elliot Anderson (left #8; tidy, energetic ball-mover; pass 16 — the shuttler)
  - index 7: CM/#8/#10 — Jude Bellingham (right #8 with a free role; floats between lines; late box arrivals)
  - index 8: LW — Marcus Rashford (direct, vertical, runs the channel; speed 17, left-footed finisher)
  - index 9: CF — Harry Kane (captain; deep #9 / target hybrid; drops to receive, shoots from 25m)
  - index 10: RW — Bukayo Saka (classic inverted RW; cuts in onto left foot)

## Style of Play

### Build-up
- 4-3 base with Pickford between CBs. Stones steps into midfield to form a 3-2-5 alongside Rice; Konsa slides across as the third of the back line.
- O'Reilly (a converted midfielder) inverts to LCM height; Anderson pushes on to the left half-space.
- Bellingham drops into the right half-space pocket to receive between lines; Kane drops deep to combine.
- Tempo: patient. Tuchel demands 25+ passes per build before vertical commitment.

### Pressing
- Mid-block primarily. Cue to step: square pass between CBs, or a wide CB receiving on the touchline.
- Kane press-leads; Bellingham jumps the opponent's #6 to cut access to the deepest midfielder.
- Saka & Rashford close down the FBs from inside.
- **No reckless high press** — Tuchel prizes shape over chaos.

### Defensive shape
- 4-5-1 / 4-1-4-1 mid-block. Kane stays slightly higher than Bellingham to enable counter outlet.
- Wingers (Saka, Rashford) drop to LM/RM heights; Rice shields the CBs with Anderson & Bellingham covering the half-spaces.
- High discipline on offside line; line ~ 45% (not as aggressive as Spain).

### Wide play
- Symmetric but different in detail: **LEFT** Rashford stays vertical and direct, O'Reilly overlaps or underlaps. **RIGHT** Saka cuts in (inverted), Konsa stays home (so the width comes from Saka holding the touchline first then cutting).
- Bellingham is the half-space connector on either side.

### Final third
- Three termination patterns:
  1. Saka cuts in → curls into far corner (signature move).
  2. O'Reilly/Rashford combo on the left → cutback for Bellingham/Kane.
  3. Kane drops, lays off to Bellingham, runs in behind — give-and-go.
- Crosses targeted at Kane near post and Bellingham far post.

## Set Pieces
- **England's super-weapon.** Rice (pass 17) takes most corners — inswingers near post; Anderson (pass 16) is the alternate deliverer.
- Targets: Guéhi, Kane, Stones, Konsa (any of 6'+). Saka/Bellingham crash the second ball edge of box.
- Direct FKs: Kane central, Saka right side, Rashford left side.
- Penalties: Kane primary; Bellingham and Rashford secondary.
- Defending: hybrid zonal/man. Stones marshalls the back-post line; Pickford commands his 6-yard box.

## decide() Decision Priorities
1. When my role is GK: first option short to CB. Only go long if double-pressed; aim for the `_9` player's (Kane) chest.
2. When my `player_id` ends with `_4` (RB — Konsa) and team has ball: tuck in beside the `_3` (Stones) to hold a back three — never overlap past the `_10` (Saka); cover Saka's inside cut.
3. When my `player_id` ends with `_3` (RCB — Stones) and pressure is low: step forward into the midfield line carrying the ball; if pressed, return to back line.
4. When my role is MID and `player_id` ends with `_5`, `_6`, or `_7` (the three — Rice/Anderson/Bellingham) and team is attacking: the `_5` (Rice) stays in front of the CBs at all times; at most one of `_6` (Anderson) and `_7` (Bellingham) above the ball line. Default: `_6` (Anderson) deeper, `_7` (Bellingham) freer.
5. When my `player_id` ends with `_7` (#8/#10 — Bellingham): drift into right half-space when the `_10` (Saka) pulls wide; arrive late at back post for cutbacks; Shoot inside the box.
6. When my `player_id` ends with `_10` (RW — Saka): start wide on touchline, Move inside diagonally when ball arrives at my feet; Shoot from 18-22m onto left foot if angle permits.
7. When my `player_id` ends with `_8` (LW — Rashford): always vertical first; run the channel between LB and LCB when the `_9` (Kane) drops; cross with my left or cut inside for the cutback and Shoot.
8. When my `player_id` ends with `_9` (CF — Kane): drop 10-15m short when team_phase is "attacking" — receive, lay off to the `_7` (Bellingham); then make a delayed run into the box. Shoot from 25m if the lane opens.
9. When team_phase is "defending": 4-5-1 shape. The `_8` and `_10` (Rashford & Saka) drop to wide-mid height. The `_7` (Bellingham) stays loosely on opp #6.
10. When defending a corner: the `_3` (Stones) marks the biggest target zonally at back post; the `_5` (Rice) anchors near post; the `_0` (Pickford) commands the 6-yard area.
11. When attacking a set piece: if my `player_id` ends with `_2`, `_3`, `_4`, or `_9` (Guéhi/Stones/Konsa/Kane) attack the ball in the 6-yard box. The `_5` (Rice) or `_6` (Anderson) to deliver.
12. Tackle aggressively only if my `player_id` ends with `_5` or `_2` (Rice/Guéhi); otherwise contain.

## Key Player Notes
- **Bellingham (idx 7)** — the free role from the right #8 slot. Allowed to roam into either half-space. Box-arrival is non-negotiable on crosses.
- **Rice (idx 5)** — primary corner/set-piece deliverer (pass 17) and box-to-box engine; the on-ball leader and anchor of the midfield three.
- **Anderson (idx 6)** — energetic shuttler at left #8; tidy distribution and the alternate set-piece taker.
- **Saka (idx 10)** — primary creator and goal threat from RW; locked-in inverted role.
- **Kane (idx 9)** — captain. False-9 instincts; not just a poacher; drops to link. Primary penalty taker.
- **O'Reilly (idx 1)** — converted midfielder at LB; treat him as a midfielder in possession.
- **Konsa (idx 4)** — defense-first RB; stays home to kill counters and free Saka.

## Tournament Mindset
Win the tight games. Tuchel's England is built to grind 1-0 results in knockouts: dominate territory, kill the game on a set piece, never concede. Expect cautious group games and a peak in the round of 16.
