# Tunisia — Tactical Profile

## Identity & Philosophy
Tunisia arrive at their final group game with the World Cup already gone. After a historic clean-sheet qualifying run under Sami Trabelsi, the federation sacked him post-AFCON, hired Sabri Lamouchi — dismissed after a brutal 5-1 opening loss to Sweden on 14 June — and handed the team to French firefighter **Hervé Renard** four days before the Japan game. In real life that rescue mission failed: Japan won handsomely and Tunisia were mathematically eliminated. In *our* simulation, Renard's reorganization clicked — Tunisia ground out a 2-1 win over Japan on Matchday 2 with a **Firas Chaouat brace** — but the maths in this group are unforgiving and elimination is confirmed regardless of this final result. Now comes the Netherlands: top of Group F, chasing first place, with Van Dijk, De Jong, Gakpo and Brobbey. The Eagles of Carthage play for pride and identity — a hard-to-beat, set-piece-dangerous side built on a solid back four, a Skhiri-anchored midfield, and Hannibal Mejbri as the one creator who can produce a moment of quality. The brief vs the Dutch: stay compact, frustrate, ride out the storm, and steal something from a set piece or a transition.

## Formation
- Shape: 4-3-3 — Renard keeps the back four that steadied the ship against Japan (a return from the 5-3-2/back-three that collapsed against Sweden). Defensively conservative with a deep block; Skhiri shields, full-backs hold position until settled.
- Role mapping (roster order in `tunisia.yaml`):
  - index 0: GK — Aymen Dahmen (first choice; kept all 10 qualifying clean sheets; conservative distributor)
  - index 1: RB — Yan Valery (energetic overlapper on the right)
  - index 2: RCB — Omar Rekik (young ball-playing CB; powerful in the air, scored a header vs Sweden)
  - index 3: LCB — Montassar Talbi (aerial dominance, deepest of the back line, organizer)
  - index 4: LB — Ali Abdi (balanced, overlaps, **first-choice penalty taker**)
  - index 5: CM — Ellyes Skhiri (captain, conductor and shield; pass 16, stamina 17 — first name on the sheet, 83+ caps)
  - index 6: CM — Hannibal Mejbri (creative #10 dropping into midfield; dribble 16, the open-play spark)
  - index 7: CM — Anis Ben Slimane (box-to-box runner, work-rate, screens)
  - index 8: RW — Firas Chaouat (right-sided forward; runs the channels, attacks crosses, top finisher — two goals vs Japan in the sim)
  - index 9: CF — Elias Saad (central striker; direct, two-footed, drives at the back line and shoots)
  - index 10: LW — Hazem Mastouri (pacey left-sided forward; carries, cuts in, transition outlet)

## Style of Play

### Build-up
- Conservative — Tunisia avoids risk in build-up, especially against a Dutch press.
- Dahmen often goes long if pressed even moderately; he will not be asked to play out under pressure.
- Skhiri drops between center-backs to receive against high pressure; the other two midfielders stay central.
- Full-backs hold width but don't push beyond halfway until Tunisia is settled in possession.

### Pressing
- Mid-block press, rarely high-press. Against a possession side like the Netherlands, Renard wants the block compact, not stretched.
- Trigger: opposition CB receives with a weak first touch, or a Dutch full-back is isolated near the touchline.
- Saad and the wide forwards do front-line work; the midfield three stays deep.
- Tunisia is content to let the Netherlands have the ball in their own half and defends the spaces in front of the box.

### Defensive shape
- 4-1-4-1 / 4-5-1 deep mid-block that collapses into two banks.
- Skhiri screens in front of the back four; Mejbri and Ben Slimane drop to form the midfield line; the wide forwards tuck in.
- Saad is the lone outlet up top.
- Center-backs hold a deep line; Tunisia prefers not to play offside (especially against De Jong's diagonal passing and Dutch runners in behind).

### Wide play
- Right: Chaouat plays off the right shoulder, runs the channel and attacks crosses; Valery overlaps to give the wide option.
- Left: Mastouri drives directly at his man and cuts inside; Abdi overlaps when Tunisia is settled.
- Crosses come from the full-backs and from the wide forwards cutting in.

### Final third
- Saad attacks the channels and is a principal finisher; Chaouat arrives at the back post.
- Mejbri is the creative spark — carries into the box and threads the killer pass.
- Chaouat's, Mastouri's and Saad's carries plus wide overloads create the openings.
- Goals from open play often come from second balls and transitions in the box — exactly how Chaouat got his brace vs Japan.

## Set Pieces
- Corners: Mejbri and Abdi are the deliverers. Talbi, Rekik, and Ben Slimane attack near/back posts.
- Direct free kicks: Mejbri (primary), Abdi, and Saad.
- Penalties: **Ali Abdi** is the first taker (converted vs Namibia in qualifying); Mejbri is an alternate.
- Defending: zonal + man-mark on the biggest aerial threat (Van Dijk, Brobbey). Tunisia is well-drilled and treats set pieces as a major chance to score against a stronger opponent.

## decide() Decision Priorities
1. When my role is GK (`player_id` ends with `_0`, Dahmen) under pressure: clear long to the CF (`_9`, Saad) or the RW channel (`_8`, Chaouat); do not attempt risky short passes against the Dutch press.
2. When my role is DEF and center-back (`_2` Rekik or `_3` Talbi) receives in own third: simple pass to the pivot (`_5`, Skhiri) or a long ball forward — no dribbling out of defense.
3. When my `player_id` ends with `_5` (Skhiri, captain): face forward, recycle through the back four, or play a vertical pass into Mejbri's (`_6`) feet (pass 16 — be the metronome).
4. When my `player_id` ends with `_7` (Ben Slimane) and opponent has the ball in midfield: tackle aggressively and screen; he is the legs of the midfield three against De Jong and Reijnders.
5. When my `player_id` ends with `_6` (Mejbri): receive between lines, turn forward, look to dribble (dribble 16) or play through balls — the main open-play threat.
6. When my `player_id` ends with `_8` (Chaouat, RW): run the right channel and in behind, attack crosses at the back post, or combine with the overlapping right-back (`_1` Valery) — he is the top finisher (brace vs Japan).
7. When my `player_id` ends with `_10` (Mastouri, LW): drive at the full-back, cut inside and Shoot from the left half-space, or run in behind on through balls.
8. When my `player_id` ends with `_9` (Saad, CF): attack the channels, hold up long clearances, and finish chances inside the box (shoot 14).
9. When defending: maintain a compact 4-5-1 / 4-1-4-1, never break shape to chase a duel — especially against the Netherlands' patient circulation.
10. When there is a turnover in own half: clear long rather than build through pressure.
11. When a set piece is awarded anywhere on the field: Tunisia takes its time, organizes, and treats it as a major scoring opportunity (Mejbri/Abdi deliver; Talbi/Rekik attack the ball).
12. When trailing late: push full-backs Valery (`_1`) and Abdi (`_4`) forward, drop Skhiri (`_5`) alongside the center-backs as a back three, and send Talbi (`_3`) forward for set pieces.
13. When leading or level late: drop the block 10m deeper and defend the box with all 10 outfield players for Dutch crosses.

## Key Player Notes
- **Skhiri (idx 5; skill 16, pass 16, stamina 17)** — captain, conductor, and shield; the most decorated Tunisian in the squad and the only one with regular Champions League minutes. First name on the sheet; never gives the ball away cheaply.
- **Mejbri (idx 6; dribble 16)** — the creative heartbeat. Beats opponents and finds the killer pass; primary free-kick and corner deliverer. Tunisia's chief open-play threat.
- **Chaouat (idx 8; shoot 14)** — the simulation's matchday-two hero with a brace against Japan; runs the channels and attacks crosses, Tunisia's most clinical finisher.
- **Ali Abdi (idx 4; penalty 14)** — overlapping left-back and the first-choice penalty taker; a reliable spot-kick and a dead-ball deliverer.
- **Dahmen (idx 0; save 14)** — first-choice keeper who anchored a record clean-sheet qualifying run; the target for clearances is the forwards, not a risky short build-up.
- **Talbi & Rekik (idx 3, idx 2)** — aerial-dominant in both boxes; the set-piece weapons at both ends. Rekik is young, fast and a goal threat from corners.
- **Mastouri & Saad (idx 10, idx 9)** — the pace and dribbling up front; Tunisia's transition outlets and the most likely sources of a goal-from-nothing.

## Tournament Mindset
Tunisia are eliminated and playing only for pride and identity. The campaign has been chaos — two managers gone in six months, a 5-1 hammering by Sweden — but Renard's reorganization produced a morale-restoring 2-1 win over Japan in the simulation, and the Eagles want to leave the tournament with their heads up. Against a Netherlands side chasing top spot, the plan is damage control and defiance: defend deep, stay compact, frustrate the Dutch, and pinch a goal from a set piece or a Mejbri/Chaouat moment. They believe a clean sheet and a 0-0 would feel like a victory against this opposition — but with nothing left to lose, expect them to commit numbers forward late if there's any chance of an upset.
