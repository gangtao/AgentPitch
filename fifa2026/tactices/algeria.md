# Algeria — Tactical Profile

## Identity & Philosophy
Under Vladimir Petković, Algeria embraces a possession-based 4-3-3 with North African technical flair. The Desert Foxes prize ball circulation, half-space combinations, and Mahrez's right-foot whip; they will attempt to control matches with the ball rather than counter from a defensive shell. Tactically continental, technically silky, vulnerable in transition.

## Formation
- Shape: 4-3-3, possession-oriented with a single pivot.
- Role mapping (roster index -> tactical role):
  - 0 Mandrea — Goalkeeper, comfortable with the ball at his feet.
  - 1 Bensebaini — Left-back, technical, supports build-up.
  - 2 Mandi — Right center-back, experienced organizer.
  - 3 Tougaï — Left center-back, physical anchor.
  - 4 Atal — Right-back, attacking, energetic crosser.
  - 5 Bentaleb — #6, deep playmaker, dictates rhythm.
  - 6 Aouar — Left #8, creative half-space operator.
  - 7 Boudaoui — Right #8, energetic carrier.
  - 8 Amoura — Left winger, direct dribbler with pace.
  - 9 Gouiri — Center-forward, link play and finishing.
  - 10 Mahrez — Right winger, captain, primary creator.

## Style of Play

### Build-up
- Methodical: 4-3-3 with Bentaleb dropping between center-backs to form a 3+2.
- Both full-backs push to the touchline; one (usually Atal) goes higher.
- Mandrea is comfortable receiving back passes and resetting play.
- Switches of play are common — Mahrez to Amoura diagonal balls.

### Pressing
- Selective press in a 4-3-3 / 4-4-2 hybrid.
- Trigger: opposition center-back receives with their weaker foot exposed.
- Gouiri and one #8 step forward; Mahrez/Amoura jump the full-back.
- Not a constant high press — they prefer to keep shape and force opponents wide.

### Defensive shape
- 4-1-4-1 mid-block when out of possession.
- Bentaleb is the screen; Aouar and Boudaoui drop to form the central five.
- Tougaï and Mandi hold the line; Bensebaini and Atal stay narrower when ball is opposite.

### Wide play
- Right side: Mahrez stays wide on the touchline, demands the ball, cuts inside onto left foot.
- Left side: Amoura attacks the byline, Bensebaini overlaps.
- Crosses from Mahrez are usually whipped to the back post for Gouiri or a late arriving Boudaoui.

### Final third
- Mahrez is the chief creator — encourage him to shoot or cross from his trademark right-side half-space.
- Gouiri links play, drops to combine, then attacks the cross.
- Aouar arrives at the edge of the box for second balls and cut-backs.
- Amoura's pace stretches defenders vertically.

## Set Pieces
- Mahrez is the primary corner and free-kick taker, especially on the right.
- Tougaï, Mandi, and Gouiri are aerial targets.
- Defensive set pieces: zonal mark + Mandi on the most dangerous aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mandrea) and unpressed: always start short to the CBs (player_id ends with "_3" Tougaï or "_2" Mandi) — Algeria never wastes goal kicks.
2. If player_id ends with "_5" (Bentaleb, #6): face the play, recycle through the back four; rarely shoots, rarely dribbles past opponents.
3. If player_id ends with "_6" (Aouar, left #8): receive on the left half-space, turn forward, look for a through ball to the LW (player_id ends with "_8", Amoura) or a give-and-go with the CF (player_id ends with "_9", Gouiri).
4. If player_id ends with "_10" (Mahrez, RW #7; skill 17, dribbling 18, pass 17): receive on the right touchline, take on the full-back, or whip a cross to the back post.
5. If player_id ends with "_4" (Atal, RB #2): overlap when Mahrez (player_id ends with "_10") cuts inside; provide width.
6. If player_id ends with "_9" (Gouiri, CF #13): drop to combine when team is building up; attack the box when ball is wide.
7. If player_id ends with "_8" (Amoura, LW #11): attack space behind defenses when through balls are on; otherwise hold width.
8. If defending: maintain 4-1-4-1 distance, Bentaleb (player_id ends with "_5") screens, never break shape to dive in.
9. If turnover in own half: counter-press for 4 seconds, then drop into mid-block.
10. If holding a lead in the final 15 minutes: keep the ball — possession is the defensive plan.
11. If Mahrez (player_id ends with "_10") is doubled: switch play to Amoura (player_id ends with "_8") within 2-3 touches; do not force the right side.
12. If trailing late: push Bensebaini (player_id ends with "_1", LB) high, drop Aouar (player_id ends with "_6") deeper alongside Bentaleb (player_id ends with "_5"), throw extra numbers forward.

## Key Player Notes
- **Mahrez (skill 17, dribbling 18, pass 17, shoot 16)** is the talisman; he's also 34 — manage his defensive workload, give him the ball as often as possible.
- **Bentaleb** is the metronome — he is not a goal threat; his job is rhythm and recycling.
- **Aouar's 16 skill / 16 dribbling** makes him a half-space dribbler — encourage him to drive into the box.
- **Amoura (speed 17, shoot 17)** is the secondary striker option; great pace for runs in behind.
- **Atal's attacking instincts** mean defensively cautious cover from Boudaoui is essential.

## Tournament Mindset
Algeria wants to play the prettiest football in the group; they expect to dominate possession against most opponents and trust Mahrez's quality to unlock low blocks.
