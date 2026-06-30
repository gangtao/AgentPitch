# England — Tactical Profile

## Identity & Philosophy
Thomas Tuchel's England is methodical, defensively organized, and ruthlessly effective in transition. Out are Southgate's tournament-pragmatist instincts; in is Tuchel's structured possession with clear positional rules, a defined mid-block press, and a strong identity on the counter. Tuchel has settled on a 4-2-3-1 — a double pivot of Rice and Anderson shielding the back four, with Jude Bellingham freed as a genuine No. 10 behind Harry Kane. Set-piece danger is world-class. England arrived as Euro 2024 finalists and a favourites-tier side, and topped Group L (above Croatia, Ghana and Panama): a 4-2 win over Croatia, a sterile 0-0 draw with Ghana, and a controlled 2-0 over Panama in which Kane became England's all-time leading World Cup scorer. Now the knockouts begin — win or go home.

## Round of 32 Lineup (vs Congo DR, July 1 — Mercedes-Benz Stadium, Atlanta, win-or-go-home)
England name their sharpest attacking band for the first knockout test against a deep, physical Congo DR block:
- **Djed Spence** starts at RB — **Reece James is injured** and **Jarell Quansah picked up an ankle knock vs Panama**, so Spence is the natural athletic replacement, overlapping outside Saka.
- **Rice + Anderson** as the double pivot — the box-to-box anchor and the disciplined left-side shuttler; control the game and screen Congo DR's 5-3-2 counters through Wissa and Bakambu.
- **Front line shuffled for a low block**: **Bukayo Saka** comes in on the right and **Marcus Rashford** on the left — Tuchel's call that Saka/Rashford unlock a deep block better than the Madueke/Gordon pairing that started the group. Bellingham floats as the free No. 10 behind Kane.
- **Saka fitness**: managed an Achilles complaint through the group (bench cameos), now back to full fitness and starting the knockout.
- Congo DR context: the "Leopards" qualified as the best third-placed nation and sit in a compact 5-3-2 / 3-5-2. Threats are **Yoane Wissa** (3 group goals, a pure penalty-box finisher), the experienced **Cedric Bakambu**, captain **Chancel Mbemba** marshalling the back line, and **Aaron Wan-Bissaka** at right wing-back. They defend deep and spring direct — England must break a low block patiently while guarding the over-the-top ball and Congo DR set pieces.

## Formation
- Shape: 4-2-3-1 (Rice + Anderson double pivot; Bellingham as the No. 10; FBs high — Spence overlaps the right, O'Reilly pushes to wing-back on the left)
- Role mapping (roster order in `england.yaml`):
  - index 0: GK — Jordan Pickford (vocal, distribution-savvy, big-moment saves)
  - index 1: LB — Nico O'Reilly (converted midfielder; tall, physical, left-footed; pushes up to wing-back height)
  - index 2: LCB — Marc Guéhi (physical, left-footed for balance; aerial duels; retained from the group)
  - index 3: RCB — Ezri Konsa (mobile, recovery-pace CB; partnered Guéhi in the Ghana shutout)
  - index 4: RB — Djed Spence (athletic, high-stamina FB in for the injured James; overlaps outside Saka)
  - index 5: LDM/#6 — Elliot Anderson (left side of the pivot; tidy, energetic ball-mover; pass 16 — the shuttler)
  - index 6: RDM/#6 — Declan Rice (anchor of the double pivot; box-to-box engine; tackles, late box arrivals, primary set-piece deliverer)
  - index 7: RW — Bukayo Saka (back to full fitness; cuts in onto his left foot, drives at the Congo wing-back; shoot 16, dribble 18)
  - index 8: AM/#10 — Jude Bellingham (free role behind Kane; floats between lines; late box arrivals; shoot 17)
  - index 9: LW — Marcus Rashford (direct, vertical, byline-hugging LW; speed 18; runs the channel, left-footed)
  - index 10: CF — Harry Kane (captain & all-time WC top scorer; deep #9 / target hybrid; drops to receive, shoots from 25m)

## Style of Play

### Build-up
- 4-2 base with Pickford between CBs. Spence stays high on the right; Konsa can step out wide to cover, forming a back-three look in possession.
- O'Reilly (a converted midfielder) pushes high on the left to wing-back height; Anderson supports the left half-space.
- Bellingham drops between the lines to receive as the free No. 10; Kane drops deep to combine.
- Tempo: patient but purposeful. Against a deep Congo DR 5-3-2, Tuchel demands a settled build — but the Ghana stalemate is a warning that patience must not tip into sterility. Quicker combinations and earlier box runs are the brief.

### Pressing
- Mid-block primarily. Cue to step: square pass between CBs, or a wide CB receiving on the touchline.
- Kane press-leads; Bellingham jumps Congo DR's deepest midfielder from the No. 10 slot.
- Saka & Rashford close down the wing-backs from inside.
- **No reckless high press** — Tuchel prizes shape over chaos. Against a deep block, expect more controlled territory than counter-pressing, with eyes on Wissa's runs in behind.

### Defensive shape
- 4-4-1-1 / 4-2-3-1 mid-block. Kane stays highest as the counter outlet; Bellingham sits just behind him on the opponent's pivot.
- Wingers (Saka, Rashford) drop to RM/LM heights; Rice & Anderson screen the back four as a flat two.
- High discipline on the offside line; line ~ 45% (not as aggressive as Spain). The Guéhi–Konsa pairing kept a clean sheet against Ghana; communication and the offside trap are the emphasis. Both must win their aerial duels with Bakambu and clear every direct ball, Congo DR's main route to goal.

### Wide play
- Asymmetric: **RIGHT** Saka cuts in (inverted) onto his left foot, Spence overlaps to provide the touchline width Saka abandons. **LEFT** Rashford stays vertical and direct, O'Reilly overlaps/underlaps from wing-back.
- Bellingham is the central half-space connector, drifting to support either flank.

### Final third
- Three termination patterns:
  1. Saka cuts in from the right → curls/strikes onto left foot (signature move).
  2. Spence or O'Reilly overlap → whipped cross or cutback for Kane/Bellingham.
  3. Kane drops, lays off to Bellingham, runs in behind — give-and-go.
- Crosses targeted at Kane near post and Bellingham far post; Rashford arrives at the back post from the left. Breaking a low block demands quicker combinations and earlier box runs.

## Set Pieces
- **England's super-weapon.** Rice (pass 17) is the primary corner/free-kick deliverer — inswingers and outswingers from both sides; Anderson and Spence are alternates.
- Targets: Guéhi, Kane, Konsa, Rice (any of 6'+). Bellingham crashes the second ball edge of box.
- Direct FKs: Kane central, Saka right side onto his left foot, Rashford left side, Rice whipped delivery.
- Penalties: Kane primary; Bellingham and Rice secondary.
- Defending: hybrid zonal/man. Konsa marshalls the back-post line; Pickford commands his 6-yard box. Double-up on Bakambu and the tall Congo DR CBs; win the first contact and clear second balls long.

## decide() Decision Priorities
1. When my role is GK: first option short to a CB. Only go long if double-pressed; aim for the `_10` player's (Kane) chest.
2. When my `player_id` ends with `_4` (RB — Spence) and team has ball: stay high on the right and overlap past the `_7` (Saka) when Saka cuts inside — provide the touchline width; tuck back beside the `_3` (Konsa) to hold a back three when O'Reilly is high on the left.
3. When my `player_id` ends with `_3` (RCB — Konsa) and pressure is low: step out wide or carry into space to cover Spence's overlaps; if pressed, return to the back line and hold the offside line with the `_2` (Guéhi).
4. When my role is MID and `player_id` ends with `_5` or `_6` (the double pivot — Anderson/Rice) and team is attacking: at least one of the two always stays in front of the CBs. Default: `_6` (Rice) screens deeper, `_5` (Anderson) shuttles slightly higher on the left.
5. When my `player_id` ends with `_8` (#10 — Bellingham): play between the lines behind the `_10` (Kane); drift into whichever half-space the ball is on; arrive late at back post for cutbacks; Shoot inside the box.
6. When my `player_id` ends with `_7` (RW — Saka): start wide on the touchline, Move inside diagonally onto my left foot when the ball arrives at my feet; Shoot from 18-22m if the angle permits; if I cut in, leave the touchline for the overlapping `_4` (Spence).
7. When my `player_id` ends with `_9` (LW — Rashford): always vertical first; run the channel between RB and RCB when the `_10` (Kane) drops; cross with my left or cut inside for the cutback and Shoot.
8. When my `player_id` ends with `_10` (CF — Kane): drop 10-15m short when team_phase is "attacking" — receive, lay off to the `_8` (Bellingham); then make a delayed run into the box. Shoot from 25m if the lane opens.
9. When team_phase is "defending": 4-4-1-1 shape. The `_7` and `_9` (Saka & Rashford) drop to wide-mid height. The `_5` and `_6` (Anderson & Rice) hold as a flat screen; the `_8` (Bellingham) presses the opponent's deepest midfielder.
10. When defending a corner: the `_3` (Konsa) marks the biggest target zonally at back post; the `_6` (Rice) anchors near post; the `_0` (Pickford) commands the 6-yard area.
11. When attacking a set piece: if my `player_id` ends with `_2`, `_3`, or `_10` (Guéhi/Konsa/Kane) attack the ball in the 6-yard box. The `_6` (Rice) to deliver.
12. Tackle aggressively only if my `player_id` ends with `_6` or `_2` (Rice/Guéhi); otherwise contain.

## Key Player Notes
- **Bellingham (idx 8)** — the free No. 10 behind Kane. Allowed to roam into either half-space. Box-arrival is non-negotiable on crosses; a genuine goal threat (shoot 17, penalty 17). Scored vs Croatia and again vs Panama.
- **Rice (idx 6)** — primary corner/set-piece deliverer (pass 17) and box-to-box engine; the on-ball leader and the anchor of the double pivot.
- **Anderson (idx 5)** — energetic shuttler on the left of the pivot; tidy distribution and an alternate set-piece taker.
- **Spence (idx 4)** — athletic, high-stamina RB starting because **Reece James is injured** and **Quansah is hurt**; bombs forward outside Saka and provides right-side width, but must recover hard against Congo DR's left wing-back on the break.
- **Saka (idx 7)** — back to full fitness after an Achilles complaint through the group; inverted RW who cuts onto his left foot to shoot or threads the cutback; Tuchel's pick to unlock a deep block.
- **Rashford (idx 9)** — direct, vertical, byline-hugging LW (speed 18); runs the channel and arrives at the back post; in for Gordon to bring extra final-ball threat against a low block.
- **Kane (idx 10)** — captain and England's all-time leading World Cup scorer. False-9 instincts; drops to link, then runs the box. Primary penalty taker; sharpness fully restored after the Panama win.
- **O'Reilly (idx 1)** — converted midfielder operating as an attacking LB/wing-back; treat him as a midfielder in possession; nearly won the Ghana game with a header off the bar.
- **Guéhi (idx 2)** — physical, left-footed CB; strong in the air and a key set-piece target. Anchored the Ghana clean sheet.
- **Konsa (idx 3)** — mobile, recovery-pace CB who partnered Guéhi in the group shutout; comfortable stepping wide to cover Spence's overlaps.

## Tournament Mindset
This is the Round of 32: one game, win or go home, no second chances. England topped Group L and arrive as clear favourites, but Congo DR are exactly the awkward, compact, counter-and-set-piece side that can punish a single lapse — and they have already shown a clinical edge through Wissa. MD1 (Croatia) proved England can win a shootout; MD2 (Ghana) proved they can be smothered by a disciplined block. The plan is the lesson learned: control possession and territory, get Saka and Rashford at the wing-backs, feed Bellingham in the pockets, deny Wissa the ball over the top, win the aerial battles on Congo DR's set pieces, and lean on the world-class corner threat of Rice and Kane to break the block. Don't gamble; take the lead, squeeze the game flat, and carry momentum deeper into the knockouts — a team built to peak in the later rounds.
