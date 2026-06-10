# Algeria — Tactical Profile

## Identity & Philosophy
Under Vladimir Petković, Algeria embraces a possession-based 4-2-3-1 with North African technical flair. The Desert Foxes prize ball circulation, half-space combinations, and Mahrez's right-foot whip; they will attempt to control matches with the ball rather than counter from a defensive shell. Tactically continental, technically silky, vulnerable in transition.

## Formation
- Shape: 4-2-3-1, possession-oriented with a double pivot.
- Role mapping (roster index -> tactical role):
  - 0 Zidane — Goalkeeper, comfortable with the ball at his feet.
  - 1 Aït-Nouri — Left-back, explosive and technical, drives the overlap.
  - 2 Bensebaïni — Left center-back, physical and a set-piece threat.
  - 3 Mandi — Right center-back, experienced organizer and record cap-holder.
  - 4 Belghali — Right-back, energetic, attacking crosser.
  - 5 Boudaoui — Right side of the double pivot, energetic ball-winner and carrier.
  - 6 Aouar — Left side of the double pivot, deep-lying creator, dictates rhythm.
  - 7 Gouiri — Left winger, link play and finishing.
  - 8 Maza — #10 behind the striker, advanced creator between the lines.
  - 9 Amoura — Center-forward, direct runner with elite pace.
  - 10 Mahrez — Right winger, captain, primary creator.

## Style of Play

### Build-up
- Methodical: 4-2-3-1 with Aouar dropping toward the center-backs to form a 3+2 with Boudaoui.
- Both full-backs push to the touchline; Aït-Nouri in particular bombs forward on the left.
- Zidane is comfortable receiving back passes and resetting play.
- Switches of play are common — Mahrez to Gouiri diagonal balls.

### Pressing
- Selective press in a 4-2-3-1 / 4-4-2 hybrid, Maza joining Amoura on the first line.
- Trigger: opposition center-back receives with their weaker foot exposed.
- Amoura and Maza step forward; Mahrez/Gouiri jump the full-back.
- Not a constant high press — they prefer to keep shape and force opponents wide.

### Defensive shape
- 4-4-1-1 mid-block when out of possession.
- Boudaoui and Aouar are the double screen; Mahrez and Gouiri drop to complete the midfield four while Maza shadows the opposition pivot.
- Bensebaïni and Mandi hold the line; Aït-Nouri and Belghali stay narrower when ball is opposite.

### Wide play
- Right side: Mahrez stays wide on the touchline, demands the ball, cuts inside onto left foot.
- Left side: Gouiri cuts in to combine, Aït-Nouri overlaps aggressively to supply the width.
- Crosses from Mahrez are usually whipped to the back post for Amoura or a late arriving Maza.

### Final third
- Mahrez is the chief creator — encourage him to shoot or cross from his trademark right-side half-space.
- Maza operates between the lines, slipping through balls to Amoura and arriving for cut-backs.
- Gouiri links play on the left, drops to combine, then attacks the cross.
- Amoura's pace stretches defenders vertically as the lone striker.

## Set Pieces
- Mahrez is the primary corner and free-kick taker, especially on the right.
- Bensebaïni, Mandi, and Gouiri are aerial targets; Bensebaïni is also a confident penalty taker.
- Defensive set pieces: zonal mark + Mandi on the most dangerous aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Zidane) and unpressed: always start short to the CBs (player_id ends with "_3" Mandi or "_2" Bensebaïni) — Algeria never wastes goal kicks.
2. If player_id ends with "_6" (Aouar, #8; pass 16): face the play, recycle through the back four, and progress with line-breaking passes; rarely shoots from deep.
3. If player_id ends with "_8" (Maza, #10/#22): receive between the lines, turn forward, look for a through ball to the CF (player_id ends with "_9", Amoura) or a give-and-go with the LW (player_id ends with "_7", Gouiri).
4. If player_id ends with "_10" (Mahrez, RW #7; skill 17, dribbling 18, pass 17): receive on the right touchline, take on the full-back, or whip a cross to the back post.
5. If player_id ends with "_4" (Belghali, RB #17): overlap when Mahrez (player_id ends with "_10") cuts inside; provide width.
6. If player_id ends with "_9" (Amoura, CF #18): attack space behind defenses when through balls are on; attack the box when ball is wide.
7. If player_id ends with "_7" (Gouiri, LW #9): drop to combine when team is building up; cut inside to finish when ball is on the right.
8. If defending: maintain 4-4-1-1 distance, the double pivot Boudaoui (player_id ends with "_5") and Aouar (player_id ends with "_6") screens, never break shape to dive in.
9. If turnover in own half: counter-press for 4 seconds, then drop into mid-block.
10. If holding a lead in the final 15 minutes: keep the ball — possession is the defensive plan.
11. If Mahrez (player_id ends with "_10") is doubled: switch play to Gouiri (player_id ends with "_7") within 2-3 touches; do not force the right side.
12. If trailing late: push Aït-Nouri (player_id ends with "_1", LB) high, push Maza (player_id ends with "_8") up alongside Amoura (player_id ends with "_9") as a second striker, throw extra numbers forward.

## Key Player Notes
- **Mahrez (skill 17, dribbling 18, pass 17, shoot 16)** is the talisman and captain; he's also 35 — manage his defensive workload, give him the ball as often as possible.
- **Aouar (skill 16, pass 16, dribbling 16)** is the metronome, installed in the double pivot — he is not a primary goal threat; his job is rhythm and progression from deep.
- **Maza (#22, skill 16, dribbling 16)** is the breakout #10 — encourage him to drive between the lines and feed Amoura.
- **Amoura (speed 17, shoot 17)** is the lead striker; great pace for runs in behind and the first outlet in transition.
- **Aït-Nouri (speed 17, dribbling 16)** is a Manchester City-grade attacking full-back — his overlaps power the left side, so cautious cover from Aouar is essential.
- **Bentaleb and Chaïbi** drop to the bench in the new double-pivot setup — fresh legs to close out games.

## Tournament Mindset
Algeria wants to play the prettiest football in the group; they expect to dominate possession against most opponents and trust Mahrez's quality to unlock low blocks.
