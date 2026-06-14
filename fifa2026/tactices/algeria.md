# Algeria — Tactical Profile

## Identity & Philosophy
Under Vladimir Petković, Algeria plays a possession-based 4-3-3 with North African technical flair. The Desert Foxes prize ball circulation, half-space combinations, and Mahrez's right-foot whip; they aim to control matches with the ball rather than counter from a defensive shell. Tactically continental, technically silky, but vulnerable in transition — a concern against a clinical Argentina in their Group J opener. Captain Mahrez (35) gets creative license across the front line.

## Formation
- Shape: 4-3-3, possession-oriented with a single pivot and two advanced eights.
- Note: first-choice CB Ramy Bensebaïni is out with an ankle injury; Samir Chergui (Paris FC) deputizes at center-back.
- Role mapping (roster index -> tactical role):
  - index 0: GK — Luca Zidane, comfortable with the ball at his feet.
  - index 1: DEF — Aït-Nouri, left-back, explosive and technical, drives the overlap.
  - index 2: DEF — Chergui, left center-back, physical cover deputizing for the injured Bensebaïni.
  - index 3: DEF — Mandi, right center-back, experienced organizer and record cap-holder.
  - index 4: DEF — Belghali, right-back, energetic attacking crosser.
  - index 5: MID — Bentaleb, holding pivot, screens the back four and recycles possession.
  - index 6: MID — Aouar, left-sided eight, deep-lying creator who dictates rhythm.
  - index 7: MID — Maza, advanced eight / free no. 10, drives between the lines.
  - index 8: FWD — Amoura, left winger, direct runner with elite pace.
  - index 9: FWD — Gouiri, center-forward, link play and finishing.
  - index 10: FWD — Mahrez, right winger, captain, primary creator.

## Style of Play

### Build-up
- Methodical: Bentaleb drops between or beside the center-backs to form a back three in possession.
- Both full-backs push to the touchline; Aït-Nouri in particular bombs forward on the left.
- Zidane is comfortable receiving back passes and resetting play.
- Switches of play are common — Mahrez and Aouar look for the diagonal to the opposite flank.

### Pressing
- Selective press from a 4-3-3 that becomes a 4-1-4-2 hybrid, Maza stepping up alongside Gouiri.
- Trigger: opposition center-back receives with their weaker foot exposed.
- Mahrez and Amoura jump the full-backs; the front line curves passing lanes inward.
- Not a constant high press — they prefer to keep shape and force opponents wide, mindful of Argentina's pace in behind.

### Defensive shape
- 4-1-4-2 / 4-5-1 mid-block when out of possession.
- Bentaleb anchors as the lone screen; Aouar and Maza tuck into the line of four, the wingers dropping alongside.
- Mandi and Chergui hold the line; Aït-Nouri and Belghali stay narrower when the ball is on the opposite side.

### Wide play
- Right side: Mahrez stays wide on the touchline, demands the ball, cuts inside onto his left foot.
- Left side: Amoura attacks the channel with pace; Aït-Nouri overlaps aggressively to supply width.
- Crosses from Mahrez are usually whipped to the back post for Gouiri or a late-arriving Maza.

### Final third
- Mahrez is the chief creator — encourage him to shoot or cross from his trademark right-side half-space.
- Maza operates between the lines, slipping through balls to Gouiri and arriving for cut-backs.
- Amoura's pace stretches defenders vertically and is the first outlet in transition.
- Gouiri leads the line, drops to combine, then attacks the cross.

## Set Pieces
- Mahrez is the primary corner and free-kick taker, especially from the right.
- Mandi, Chergui, and Gouiri are aerial targets in the box.
- Penalties: Amoura (penalty 17) and Mahrez (penalty 16) are the first-choice takers.
- Defensive set pieces: zonal mark + Mandi on the most dangerous aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Zidane) and unpressed: start short to the CBs (player_id ends with "_2" Chergui or "_3" Mandi) — Algeria never wastes goal kicks; go long only under a committed press.
2. If player_id ends with "_5" (Bentaleb, pivot): drop between the center-backs in build-up, screen in defense, recycle through the back four, and progress with safe line-breaking passes; rarely shoots from deep.
3. If player_id ends with "_6" (Aouar, #8; pass 16): face the play, dictate tempo, and progress with line-breaking passes; rotate with Maza but stay the deeper of the two eights.
4. If player_id ends with "_7" (Maza, advanced #8/#22): receive between the lines, turn forward, and look for a through ball to the CF (player_id ends with "_9", Gouiri) or a give-and-go with a winger.
5. If player_id ends with "_10" (Mahrez, RW #7; skill 17, dribbling 18, pass 17): receive on the right touchline, take on the full-back, cut inside, or whip a cross to the back post.
6. If player_id ends with "_4" (Belghali, RB #17): overlap when Mahrez (player_id ends with "_10") cuts inside; provide width on the right.
7. If player_id ends with "_9" (Gouiri, CF #9): lead the line, attack space behind defenses when through balls are on, and attack the box when the ball is wide.
8. If player_id ends with "_8" (Amoura, LW #18; speed 17): attack the channel in behind with pace; first outlet on the counter; arrive at the back post on right-side crosses.
9. If defending: hold the 4-1-4-2 / 4-5-1 mid-block, Bentaleb (player_id ends with "_5") shielding the back four; never break shape to dive in against Argentina's runners.
10. If turnover in own half: counter-press for 4 seconds, then drop into the mid-block.
11. If holding a lead in the final 15 minutes: keep the ball — possession is the defensive plan.
12. If Mahrez (player_id ends with "_10") is doubled: switch play to Amoura (player_id ends with "_8") within 2-3 touches; do not force the right side.
13. If trailing late: push Aït-Nouri (player_id ends with "_1", LB) high, push Maza (player_id ends with "_7") up alongside Gouiri (player_id ends with "_9") as a second striker, throw extra numbers forward.

## Key Player Notes
- **Mahrez (skill 17, dribbling 18, pass 17, shoot 16)** is the talisman and captain; at 35, manage his defensive workload and give him the ball as often as possible.
- **Aouar (skill 16, pass 16, dribbling 16)** is the metronome of the midfield three — not a primary goal threat; his job is rhythm and progression from deep.
- **Maza (#22, skill 16, dribbling 16)** is the breakout advanced eight — encourage him to drive between the lines and feed Gouiri.
- **Amoura (speed 17, shoot 17, penalty 17)** is the lead scorer and pace outlet; finished top scorer in qualifying, lethal on runs in behind and a first-choice penalty taker.
- **Aït-Nouri (speed 17, dribbling 16)** is a top-tier attacking full-back — his overlaps power the left side, so cautious cover from Bentaleb is essential.
- **Bensebaïni out (ankle):** Chergui deputizes at CB — sound but less of an aerial set-piece threat, so the line leans on Mandi's organization.

## Tournament Mindset
Algeria wants to play the prettiest football in Group J; they expect to dominate possession against most opponents and trust Mahrez's quality to unlock low blocks. Against Argentina they must respect the champions' transitions — control the ball, stay compact behind it, and punish through Amoura's pace and Mahrez's set-piece quality.
