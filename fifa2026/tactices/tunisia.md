# Tunisia — Tactical Profile

## Identity & Philosophy
Tunisia under Sabri Lamouchi is the archetypal hard-to-beat side — defensive solidity, midfield work-rate, and set-piece danger. Their 4-2-3-1 is more conservative than the rest of the African field, with a Skhiri–Khedira double pivot screening the back four and Hannibal providing the moments of quality between the lines. They will out-organize opponents, frustrate them, and steal goals from second balls.

## Formation
- Shape: 4-2-3-1, defensively structured, with a deep block and a protected double pivot.
- Role mapping (roster index -> tactical role):
  - 0 Dahmen — Goalkeeper, conservative distributor.
  - 1 Ali Abdi — Left-back, balanced.
  - 2 Talbi — Left center-back, aerial.
  - 3 Bronn — Right center-back, experienced.
  - 4 Valery — Right-back, energetic overlapper.
  - 5 Skhiri — Deep-lying pivot, conductor and shield (captain).
  - 6 Khedira — Holding pivot, ball-winner and screen.
  - 7 Mejbri — Attacking midfielder (#10), creative spark.
  - 8 Achouri — Left winger, energy and pace.
  - 9 Saad — Center-forward, runs the channels and finishes.
  - 10 Ben Slimane — Right winger / advanced runner, work-rate.

## Style of Play

### Build-up
- Conservative — Tunisia avoids risk in build-up.
- Dahmen often goes long if pressed even moderately.
- Skhiri drops between center-backs to receive against high pressure; Khedira stays central as the spare pivot.
- Full-backs hold width but don't push beyond halfway until Tunisia is settled in possession.

### Pressing
- Mid-block press, rarely high-press.
- Trigger: opposition CB receives with weak first touch.
- Saad and the wingers do front-line work; the double pivot stays deep.
- Tunisia is content to let opponents have the ball in their own half.

### Defensive shape
- 4-4-1-1 / 4-2-3-1 deep mid-block that collapses into two banks of four.
- Skhiri and Khedira screen as a double pivot; the wide attackers tuck in to form the second bank.
- Saad is the lone outlet; Mejbri drops onto the opposition pivot.
- Center-backs hold a deep line; Tunisia prefers not to play offside.

### Wide play
- Right: Ben Slimane runs in behind and combines with the overlapping Valery.
- Left: Achouri has pace and dribbling to stretch the field; Abdi overlaps occasionally.
- Crosses come from the full-backs and from Achouri cutting in off the left.

### Final third
- Saad attacks crosses, runs the channels, and is the principal finisher.
- Mejbri is the creative spark — he carries the ball into the box and threads the killer pass.
- Achouri's carries and the wide overloads create the openings.
- Goals from open play often come from second balls in the box.

## Set Pieces
- Mejbri and Skhiri are the primary deliverers for corners and free kicks.
- Talbi, Bronn, and Khedira are the aerial targets.
- Defensive set pieces: zonal + man-mark on the biggest aerial threat. Tunisia is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Dahmen) under pressure: clear long to the CF (player_id ends with "_9", Saad) or the LW channel (player_id ends with "_8", Achouri); do not attempt risky short passes.
2. If role == "DEF" and center-back (player_id ends with "_2" Talbi or "_3" Bronn) receives in own third: simple pass to the pivot (player_id ends with "_5", Skhiri) or a long ball forward — no dribbling out of defense.
3. If player_id ends with "_5" (Skhiri, captain): face forward, recycle through the back four or play a vertical pass into the #10 (player_id ends with "_7", Mejbri) feet.
4. If player_id ends with "_6" (Khedira) and opponent has the ball in midfield: tackle aggressively; he's the team's ball-winner and screen.
5. If player_id ends with "_7" (Mejbri, #10): receive between lines, turn forward, look to dribble or play through balls.
6. If player_id ends with "_10" (Ben Slimane, RW): receive on the right, run in behind, or combine with the overlapping right-back and cross to the CF (player_id ends with "_9", Saad).
7. If player_id ends with "_8" (Achouri, LW): run in behind when through balls are on; otherwise hold width and look to cut inside.
8. If defending: maintain compact 4-4-1-1, never break shape to chase a duel.
9. If turnover in own half: clear long rather than build through pressure.
10. If a set piece is awarded anywhere on the field: Tunisia takes its time, organizes, and treats it as a major scoring opportunity.
11. If trailing late: push the full-backs Valery (player_id ends with "_4") and Abdi (player_id ends with "_1") forward, drop Skhiri (player_id ends with "_5") alongside center-backs as a back-three, send Talbi (player_id ends with "_2") forward for set pieces.
12. If leading: drop block 10m deeper, defend the box with all 10 outfield players for late crosses.

## Key Player Notes
- **Skhiri (skill 16, pass 16, stamina 17)** is the captain, conductor, and shield — never gives the ball away cheaply.
- **Khedira** is the disciplined ball-winner alongside Skhiri; together they protect the back four.
- **Mejbri** has the dribbling (16) to beat opponents and the creativity to find a killer pass — the main open-play threat.
- **Saad** is the focal point of the attack: pace, movement, and a reliable finish; he's the target for clearances under pressure.
- **Talbi and Bronn** are aerial-dominant in both boxes — exploit them on set pieces.

## Tournament Mindset
Tunisia believes 1-0 is the perfect scoreline. They will not chase games unless absolutely necessary; their plan is to defend deep, frustrate, and pinch a goal from a set piece or a moment of Mejbri quality.
