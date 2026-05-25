# Tunisia — Tactical Profile

## Identity & Philosophy
Tunisia under Sami Trabelsi is the archetypal hard-to-beat side — defensive solidity, midfield work-rate, and set-piece danger. Their 4-3-3 is more conservative than the rest of the African field, with Skhiri anchoring midfield and Msakni providing veteran moments of quality. They will out-organize opponents, frustrate them, and steal goals from second balls.

## Formation
- Shape: 4-3-3, defensively structured, with a deep block.
- Role mapping (roster index -> tactical role):
  - 0 Dahmen — Goalkeeper, conservative distributor.
  - 1 Ali Abdi — Left-back, balanced.
  - 2 Meriah — Right center-back, physical.
  - 3 Talbi — Left center-back, aerial.
  - 4 Bronn — Right-back, experienced.
  - 5 Laïdouni — #8, ball-winner, runner.
  - 6 Skhiri — #6, deep-lying conductor and shield.
  - 7 Mejbri — #10 / advanced #8, creative spark.
  - 8 Msakni — Right winger, veteran, set-piece talisman.
  - 9 Ben Romdhane — Center-forward, work-rate forward.
  - 10 Saad — Left winger, energy and pace.

## Style of Play

### Build-up
- Conservative — Tunisia avoids risk in build-up.
- Dahmen often goes long if pressed even moderately.
- Skhiri drops between center-backs to receive against high pressure.
- Full-backs hold width but don't push beyond halfway until Tunisia is settled in possession.

### Pressing
- Mid-block press, rarely high-press.
- Trigger: opposition CB receives with weak first touch.
- Ben Romdhane and the wingers do front-line work; Skhiri stays deep.
- Tunisia is content to let opponents have the ball in their own half.

### Defensive shape
- 4-5-1 / 4-1-4-1 deep mid-block.
- Skhiri screens, Laïdouni and Mejbri shuttle.
- Two banks of four with Ben Romdhane the lone outlet.
- Center-backs hold a deep line; Tunisia prefers not to play offside.

### Wide play
- Right: Msakni cuts inside onto his left foot for shots or passes.
- Left: Saad has more pace and stretches the field; Abdi overlaps occasionally.
- Crosses are mostly Msakni's whipped right-foot deliveries.

### Final third
- Ben Romdhane attacks crosses and holds up play.
- Mejbri is the creative spark — he carries the ball into the box.
- Msakni's set pieces are the principal goal source.
- Goals from open play often come from second balls in the box.

## Set Pieces
- Msakni is the primary deliverer for corners and free kicks.
- Meriah, Talbi, and Ben Romdhane are the aerial targets.
- Defensive set pieces: zonal + man-mark on the biggest aerial threat. Tunisia is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Dahmen) under pressure: clear long to the CF (player_id ends with "_9", Ben Romdhane) or the LW channel (player_id ends with "_10", Saad); do not attempt risky short passes.
2. If role == "DEF" and center-back (player_id ends with "_2" Meriah or "_3" Talbi) receives in own third: simple pass to the #6 (player_id ends with "_6", Skhiri) or a long ball forward — no dribbling out of defense.
3. If player_id ends with "_6" (Skhiri, #6 #13): face forward, recycle through the back four or play a vertical pass into the #10 (player_id ends with "_7", Mejbri) feet.
4. If player_id ends with "_5" (Laïdouni, MID #6) and opponent has the ball in midfield: tackle aggressively; he's the team's ball-winner.
5. If player_id ends with "_7" (Mejbri, #10 #8): receive between lines, turn forward, look to dribble or play through balls.
6. If player_id ends with "_8" (Msakni, RW #7): receive on the right wing, cut inside onto left foot, shoot or whip a cross to the CF (player_id ends with "_9", Ben Romdhane).
7. If player_id ends with "_10" (Saad, LW #9): run in behind when through balls are on; otherwise hold width.
8. If defending: maintain compact 4-5-1, never break shape to chase a duel.
9. If turnover in own half: clear long rather than build through pressure.
10. If a set piece is awarded anywhere on the field: Tunisia takes its time, organizes, and treats it as a major scoring opportunity.
11. If trailing late: push the full-backs Bronn (player_id ends with "_4") and Abdi (player_id ends with "_1") forward, drop Skhiri (player_id ends with "_6") alongside center-backs as a back-three, send Talbi (player_id ends with "_3") forward for set pieces.
12. If leading: drop block 10m deeper, defend the box with all 10 outfield players for late crosses.

## Key Player Notes
- **Skhiri (skill 16, pass 16, stamina 17)** is the conductor and shield — never gives the ball away cheaply.
- **Msakni** is the only consistent creative outlet from open play — protect him from being doubled by drifting him in/out.
- **Mejbri** has the dribbling (16) to beat opponents and the creativity to find a killer pass.
- **Ben Romdhane** wins headers and holds up play; he's the target for clearances under pressure.
- **Meriah and Talbi** are aerial-dominant in both boxes — exploit them on set pieces.

## Tournament Mindset
Tunisia believes 1-0 is the perfect scoreline. They will not chase games unless absolutely necessary; their plan is to defend deep, frustrate, and pinch a goal from a Msakni set piece.
