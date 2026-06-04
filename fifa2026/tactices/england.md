# England — Tactical Profile

## Identity & Philosophy
Thomas Tuchel's England is methodical, defensively organized, and ruthlessly effective at set pieces. Out are Southgate's tournament-pragmatist instincts; in is Tuchel's structured possession with clear positional rules, a defined press, and a strong identity in transition. Set-piece danger remains world-class. Recent results: Euro 2024 final under Southgate, qualifying campaign under Tuchel cleaned up the defensive issues — England now concedes very rarely.

## Formation
- Shape: 4-2-3-1 (Tuchel's preferred — double pivot for control)
- Role mapping (roster order in `england.yaml`):
  - index 0: GK — Jordan Pickford (vocal, distribution-savvy, big-moment saves)
  - index 1: LB — Tino Livramento (pacey, energetic young full-back; overlaps and recovers)
  - index 2: LCB — Marc Guéhi (physical, left-footed for balance; aerial duels)
  - index 3: RCB — John Stones (ball-progressor; pass 17, sometimes steps into midfield)
  - index 4: RB — Reece James (inverts into midfield in possession; pass 17 — the right-side metronome)
  - index 5: DM/#6 — Declan Rice (left of double pivot; box-to-box; tackles, late box arrivals)
  - index 6: DM/#6 — Elliot Anderson (right of double pivot; tidy, energetic ball-mover; pass 16 — the shuttler)
  - index 7: LW — Marcus Rashford (direct, vertical, runs the channel; speed 17, left-footed finisher)
  - index 8: AM/#10 — Jude Bellingham (the free #10; floats between lines; late box arrivals)
  - index 9: RW — Bukayo Saka (classic inverted RW; cuts in onto left foot)
  - index 10: CF — Harry Kane (captain; deep #9 / target hybrid; drops to receive, shoots from 25m)

## Style of Play

### Build-up
- 4-2 base with Pickford between CBs. Stones steps into midfield to form a 3-2-5 alongside Rice/Anderson.
- James inverts to RCM height; Livramento stays wider and higher.
- Bellingham drops into the right half-space pocket to receive between lines; Kane drops deep to combine.
- Tempo: patient. Tuchel demands 25+ passes per build before vertical commitment.

### Pressing
- Mid-block primarily. Cue to step: square pass between CBs, or a wide CB receiving on the touchline.
- Kane press-leads; Bellingham jumps the opponent's #6 to cut access to the deepest midfielder.
- Saka & Rashford close down the FBs from inside.
- **No reckless high press** — Tuchel prizes shape over chaos.

### Defensive shape
- 4-4-1-1 / 4-2-3-1 mid-block. Kane stays slightly higher than Bellingham to enable counter outlet.
- Wide mids (Saka, Rashford) drop to LM/RM heights; Rice & Anderson shield the CBs.
- High discipline on offside line; line ~ 45% (not as aggressive as Spain).

### Wide play
- Symmetric but different in detail: **LEFT** Rashford stays vertical and direct, Livramento overlaps. **RIGHT** Saka cuts in (inverted), James inverts (so the width comes from Saka holding the touchline first then cutting).
- Bellingham is the half-space connector on either side.

### Final third
- Three termination patterns:
  1. Saka cuts in → curls into far corner (signature move).
  2. Livramento/Rashford combo on the left → cutback for Bellingham/Kane.
  3. Kane drops, lays off to Bellingham, runs in behind — give-and-go.
- Crosses targeted at Kane near post and Bellingham far post.

## Set Pieces
- **England's super-weapon.** Rice (pass 17) takes most corners — inswingers near post; Anderson (pass 16) is the alternate deliverer.
- Targets: Guéhi, Kane, Stones (any of 6'+). Saka/Bellingham crash the second ball edge of box.
- Direct FKs: Kane central, James right side, Rashford left side.
- Penalties: Kane primary; Bellingham and Rashford secondary.
- Defending: hybrid zonal/man. Stones marshalls the back-post line; Pickford commands his 6-yard box.

## decide() Decision Priorities
1. When my role is GK: first option short to CB. Only go long if double-pressed; aim for the `_10` player's (Kane) chest.
2. When my `player_id` ends with `_4` (RB — James) and team has ball: invert to RCM height — sit alongside the `_5`/`_6` pivot (Rice/Anderson) in a 2-2-5 structure.
3. When my `player_id` ends with `_3` (RCB — Stones) and pressure is low: step forward into the midfield line carrying the ball; if pressed, return to back line.
4. When my role is MID and `player_id` ends with `_5` or `_6` (DM pivot — Rice/Anderson) and team is attacking: one of us stays in front of CBs at all times — never both above the halfway line. Default: `_6` (Anderson) deeper, `_5` (Rice) freer.
5. When my `player_id` ends with `_8` (#10 — Bellingham): drift into right half-space when the `_9` (Saka) pulls wide; arrive late at back post for cutbacks; Shoot inside the box.
6. When my `player_id` ends with `_9` (RW — Saka): start wide on touchline, Move inside diagonally when ball arrives at my feet; Shoot from 18-22m onto left foot if angle permits.
7. When my `player_id` ends with `_7` (LW — Rashford): always vertical first; run the channel between LB and LCB when the `_10` (Kane) drops; cross with my left or cut inside for the cutback and Shoot.
8. When my `player_id` ends with `_10` (CF — Kane): drop 10-15m short when team_phase is "attacking" — receive, lay off to the `_8` (Bellingham); then make a delayed run into the box. Shoot from 25m if the lane opens.
9. When team_phase is "defending": 4-4-1-1 shape. The `_7` and `_9` (Rashford & Saka) drop to wide-mid height. The `_8` (Bellingham) stays loosely on opp #6.
10. When defending a corner: the `_3` (Stones) marks the biggest target zonally at back post; the `_5` (Rice) anchors near post; the `_0` (Pickford) commands the 6-yard area.
11. When attacking a set piece: if my `player_id` ends with `_2`, `_3`, `_10`, or `_5` (Guéhi/Stones/Kane/Rice) attack the ball in the 6-yard box. The `_5` (Rice) or `_6` (Anderson) to deliver.
12. Tackle aggressively only if my `player_id` ends with `_5` or `_2` (Rice/Guéhi); otherwise contain.

## Key Player Notes
- **Bellingham (idx 8)** — the free role. Allowed to roam into either half-space. Box-arrival is non-negotiable on crosses.
- **Rice (idx 5)** — primary corner/set-piece deliverer (pass 17) and box-to-box engine; the on-ball leader of the pivot.
- **Anderson (idx 6)** — energetic shuttler in the double pivot; tidy distribution and the alternate set-piece taker.
- **Saka (idx 9)** — primary creator and goal threat from RW; locked-in inverted role.
- **Kane (idx 10)** — captain. False-9 instincts; not just a poacher; drops to link. Primary penalty taker.
- **James (idx 4)** — inverted FB; treat him as a midfielder in possession.

## Tournament Mindset
Win the tight games. Tuchel's England is built to grind 1-0 results in knockouts: dominate territory, kill the game on a set piece, never concede. Expect cautious group games and a peak in the round of 16.
