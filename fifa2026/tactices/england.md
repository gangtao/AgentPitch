# England — Tactical Profile

## Identity & Philosophy
Thomas Tuchel's England is methodical, defensively organized, and ruthlessly effective in transition. Out are Southgate's tournament-pragmatist instincts; in is Tuchel's structured possession with clear positional rules, a defined mid-block press, and a strong identity on the counter. Tuchel has settled on a 4-2-3-1 — a double pivot of Rice and Anderson shielding the back four, with Jude Bellingham freed as a genuine No. 10 behind Harry Kane. Set-piece danger is world-class. England arrive as Euro 2024 finalists and a tournament-favourites-tier side, drawn into Group L with Croatia, Ghana and Panama.

**Matchday 1 update (17 June, vs Croatia — won 4-2):** A thrilling, slightly chaotic opening win. Harry Kane bagged a brace (one penalty), Bellingham drilled in just after the restart, and Marcus Rashford came off the bench to finish a fourth, teed up by Saka. But England conceded twice — Baturina and Musa punished defensive lapses, and **Ezri Konsa and John Stones were both culpable** for the Croatia goals. Tuchel handed six senior World Cup debuts (Konsa, O'Reilly, Anderson, Gordon, Madueke, James). For Matchday 2 vs Ghana (23 June) the headline change is **Marc Guéhi replacing Konsa** at centre-back after the MD1 errors; Stones is retained. The chief watch points are fitness: **Bukayo Saka (Achilles)** has been restricted to individual training and is doubtful, so **Noni Madueke continues on the right**; **Marcus Rashford (hamstring)** and **Declan Rice (hamstring)** had scares but trained fully, with Rice expected to start and **Anthony Gordon retained on the left**. The most likely XI keeps the MD1 attacking shape (Madueke / Bellingham / Gordon behind Kane) with Guéhi the lone defensive switch. England can seal a knockout place with a game to spare.

## Formation
- Shape: 4-2-3-1 (Rice + Anderson double pivot; Bellingham as the No. 10; FBs ultra-high — James inverts, O'Reilly pushes to wing-back)
- Role mapping (roster order in `england.yaml`):
  - index 0: GK — Jordan Pickford (vocal, distribution-savvy, big-moment saves)
  - index 1: LB — Nico O'Reilly (converted midfielder; tall, physical, left-footed; pushes up to wing-back height)
  - index 2: LCB — Marc Guéhi (physical, left-footed for balance; aerial duels; in for Konsa after MD1)
  - index 3: RCB — John Stones (ball-progressor; pass 17, sometimes steps into midfield)
  - index 4: RB — Reece James (elite crosser & passer; pass 17; tucks inside to form a back three in possession)
  - index 5: LDM/#6 — Elliot Anderson (left side of the pivot; tidy, energetic ball-mover; pass 16 — the shuttler)
  - index 6: RDM/#6 — Declan Rice (anchor of the double pivot; box-to-box engine; tackles, late box arrivals)
  - index 7: RW — Noni Madueke (explosive, powerful inverted RW; cuts in onto left foot; speed 17, dribble 17)
  - index 8: AM/#10 — Jude Bellingham (free role behind Kane; floats between lines; late box arrivals; shoot 17)
  - index 9: LW — Anthony Gordon (direct, vertical, byline-hugging LW; speed 18; runs the channel, left-footed)
  - index 10: CF — Harry Kane (captain; deep #9 / target hybrid; drops to receive, shoots from 25m)

## Style of Play

### Build-up
- 4-2 base with Pickford between CBs. James tucks inside to form a 3-2-5 alongside the pivot; Stones can also step up.
- O'Reilly (a converted midfielder) pushes high on the left to wing-back height; Anderson supports the left half-space.
- Bellingham drops between the lines to receive as the free No. 10; Kane drops deep to combine.
- Tempo: patient. Tuchel demands a settled build before vertical commitment.

### Pressing
- Mid-block primarily. Cue to step: square pass between CBs, or a wide CB receiving on the touchline.
- Kane press-leads; Bellingham jumps the opponent's deepest midfielder from the No. 10 slot.
- Madueke & Gordon close down the FBs from inside.
- **No reckless high press** — Tuchel prizes shape over chaos.

### Defensive shape
- 4-4-1-1 / 4-2-3-1 mid-block. Kane stays highest as the counter outlet; Bellingham sits just behind him on the opponent's pivot.
- Wingers (Madueke, Gordon) drop to RM/LM heights; Rice & Anderson screen the back four as a flat two.
- High discipline on offside line; line ~ 45% (not as aggressive as Spain). After conceding twice on MD1, communication between Guéhi and Stones is the emphasis.

### Wide play
- Asymmetric: **LEFT** Gordon stays vertical and direct, O'Reilly overlaps/underlaps from wing-back. **RIGHT** Madueke cuts in (inverted), James overlaps to provide the touchline width Madueke abandons.
- Bellingham is the central half-space connector, drifting to support either flank.

### Final third
- Three termination patterns:
  1. Madueke cuts in → curls/strikes onto left foot (signature move).
  2. James overlap on the right → whipped cross or cutback for Kane/Bellingham.
  3. Kane drops, lays off to Bellingham, runs in behind — give-and-go.
- Crosses targeted at Kane near post and Bellingham far post; Gordon arrives at the back post from the left.

## Set Pieces
- **England's super-weapon.** Rice (pass 17) and Reece James (pass 17) take corners — James inswingers from the right, Rice/Anderson the alternates from the left.
- Targets: Guéhi, Kane, Stones, James (any of 6'+). Bellingham crashes the second ball edge of box.
- Direct FKs: Kane central, Madueke right side, Gordon left side, James whipped delivery.
- Penalties: Kane primary; Bellingham and Rice secondary.
- Defending: hybrid zonal/man. Stones marshalls the back-post line; Pickford commands his 6-yard box.

## decide() Decision Priorities
1. When my role is GK: first option short to a CB. Only go long if double-pressed; aim for the `_10` player's (Kane) chest.
2. When my `player_id` ends with `_4` (RB — James) and team has ball: tuck in beside the `_3` (Stones) to hold a back three when O'Reilly is high; overlap past the `_7` (Madueke) when Madueke cuts inside — provide the touchline width.
3. When my `player_id` ends with `_3` (RCB — Stones) and pressure is low: step forward into the midfield line carrying the ball; if pressed, return to back line.
4. When my role is MID and `player_id` ends with `_5` or `_6` (the double pivot — Anderson/Rice) and team is attacking: at least one of the two always stays in front of the CBs. Default: `_6` (Rice) screens deeper, `_5` (Anderson) shuttles slightly higher on the left.
5. When my `player_id` ends with `_8` (#10 — Bellingham): play between the lines behind the `_10` (Kane); drift into whichever half-space the ball is on; arrive late at back post for cutbacks; Shoot inside the box.
6. When my `player_id` ends with `_7` (RW — Madueke): start wide on touchline, Move inside diagonally when ball arrives at my feet; Shoot from 18-22m onto left foot if angle permits; if I cut in, leave the touchline for the overlapping `_4` (James).
7. When my `player_id` ends with `_9` (LW — Gordon): always vertical first; run the channel between RB and RCB when the `_10` (Kane) drops; cross with my left or cut inside for the cutback and Shoot.
8. When my `player_id` ends with `_10` (CF — Kane): drop 10-15m short when team_phase is "attacking" — receive, lay off to the `_8` (Bellingham); then make a delayed run into the box. Shoot from 25m if the lane opens.
9. When team_phase is "defending": 4-4-1-1 shape. The `_7` and `_9` (Madueke & Gordon) drop to wide-mid height. The `_5` and `_6` (Anderson & Rice) hold as a flat screen; the `_8` (Bellingham) presses the opponent's deepest midfielder.
10. When defending a corner: the `_3` (Stones) marks the biggest target zonally at back post; the `_6` (Rice) anchors near post; the `_0` (Pickford) commands the 6-yard area.
11. When attacking a set piece: if my `player_id` ends with `_2`, `_3`, `_4`, or `_10` (Guéhi/Stones/James/Kane) attack the ball in the 6-yard box. The `_6` (Rice) or `_4` (James) to deliver.
12. Tackle aggressively only if my `player_id` ends with `_6` or `_2` (Rice/Guéhi); otherwise contain.

## Key Player Notes
- **Bellingham (idx 8)** — the free No. 10 behind Kane. Allowed to roam into either half-space. Box-arrival is non-negotiable on crosses; a genuine goal threat (shoot 17, penalty 17). Scored in MD1.
- **Rice (idx 6)** — primary corner/set-piece deliverer (pass 17) and box-to-box engine; the on-ball leader and the anchor of the double pivot. Had a hamstring scare in MD1 but is expected to start.
- **Anderson (idx 5)** — energetic shuttler on the left of the pivot; tidy distribution and an alternate set-piece taker.
- **James (idx 4)** — first-choice RB; elite crosser (pass 17) and a primary right-side set-piece deliverer. Inverts to a back three when O'Reilly bombs on, or overlaps when Madueke cuts in.
- **Madueke (idx 7)** — explosive inverted RW deputising while Saka (Achilles) is doubtful; powerful dribbler who cuts onto his left foot to shoot. Started MD1.
- **Gordon (idx 9)** — direct, vertical, byline-hugging LW (speed 18); runs the channel and arrives at the back post. Started MD1.
- **Kane (idx 10)** — captain. False-9 instincts; not just a poacher; drops to link. Primary penalty taker; scored a brace in MD1.
- **O'Reilly (idx 1)** — converted midfielder operating as an attacking LB/wing-back; treat him as a midfielder in possession.
- **Guéhi (idx 2)** — physical, left-footed CB drafted in for Konsa after the MD1 defensive errors; strong in the air and a key set-piece target.

## Tournament Mindset
Win the tight games — but MD1 showed this England can also win a shootout. Tuchel's side is built to dominate territory and kill games on set pieces, yet conceding twice to Croatia exposed lapses that the Guéhi-for-Konsa switch is meant to tighten. A win over Ghana seals knockout qualification with a game to spare. Expect controlled, low-risk possession with the wide pace of Madueke and Gordon (and Saka's return looming) as the cutting edge — a side built to peak in the knockout rounds.
