# Algeria -- Tactical Profile

## Identity & Philosophy
Under Vladimir Petkovic, Algeria plays a possession-based 4-3-3 with North African technical flair. The Desert Foxes prize ball circulation, half-space combinations, and Mahrez's right-foot whip; they aim to control matches with the ball rather than counter from a defensive shell. After a chastening 0-3 opening defeat to Argentina (Messi hat-trick) in which Petkovic controversially benched Mahrez and Amoura, the manager restored his strongest XI for Matchday 2 and was rewarded: a 2-1 win over Jordan sealed by Amine Gouiri's 82nd-minute strike. That result revived the campaign. Now level on three points with Austria heading into Matchday 3, Algeria face a straight winner-takes-all shoot-out for second place and a spot in the Round of 32. Expect the same proven, full-strength attacking XI -- no suspensions, and the squad is fully available.

## Formation
- Shape: 4-3-3, possession-oriented with a single pivot and two advanced eights.
- Note: Ait-Nouri and Bensebaini both played through the Jordan win at below 100% but trained fully ahead of Austria and retain their places. Tougai (CB) and Chaibi (MID) provide the most pressing competition off the bench.
- Role mapping (roster index -> tactical role):
  - index 0: GK -- Luca Zidane (#23), comfortable with the ball at his feet.
  - index 1: DEF -- Ait-Nouri (#15), left-back, explosive and technical, drives the overlap.
  - index 2: DEF -- Bensebaini (#21), left center-back, experienced Dortmund defender, strong in the air and on the ball.
  - index 3: DEF -- Mandi (#2), right center-back, captain-grade organizer, record cap-holder (117 caps).
  - index 4: DEF -- Belghali (#17), right-back, energetic attacking crosser.
  - index 5: MID -- Bentaleb (#19), holding pivot, screens the back four and recycles possession.
  - index 6: MID -- Boudaoui (#14), box-to-box eight, tireless ball-winner with high work-rate.
  - index 7: MID -- Maza (#22), advanced eight / free no. 10, drives between the lines.
  - index 8: FWD -- Amoura (#18), left winger, direct runner with elite pace; restored to the starting XI from MD2.
  - index 9: FWD -- Gouiri (#9), center-forward, link play and finishing; scored the MD2 winner vs Jordan.
  - index 10: FWD -- Mahrez (#7), right winger, captain, primary creator; restored to the starting XI from MD2.

## Style of Play

### Build-up
- Methodical: Bentaleb drops between or beside the center-backs to form a back three in possession.
- Both full-backs push to the touchline; Ait-Nouri in particular bombs forward on the left.
- Zidane is comfortable receiving back passes and resetting play.
- Switches of play are common -- Mahrez and Boudaoui look for the diagonal to the opposite flank.

### Pressing
- Austria are organized and physical, so the press is more selective than against Jordan; pick triggers rather than chasing blindly.
- Selective press from a 4-3-3 that becomes a 4-1-4-2 hybrid, Maza stepping up alongside Gouiri.
- Trigger: opposition center-back receives with their weaker foot exposed, or a loose touch in their build-up.
- Mahrez and Amoura jump the full-backs; the front line curves passing lanes inward.
- Boudaoui's energy sustains the press when Algeria choose to go.

### Defensive shape
- 4-1-4-2 / 4-5-1 mid-block when out of possession.
- Bentaleb anchors as the lone screen; Boudaoui and Maza tuck into the line of four, the wingers dropping alongside.
- Mandi and Bensebaini hold the line; Ait-Nouri and Belghali stay narrower when the ball is on the opposite side.

### Wide play
- Right side: Mahrez stays wide on the touchline, demands the ball, cuts inside onto his left foot.
- Left side: Amoura attacks the channel with pace; Ait-Nouri overlaps aggressively to supply width.
- Crosses from Mahrez are usually whipped to the back post for Gouiri or a late-arriving Maza.

### Final third
- Mahrez is the chief creator -- encourage him to shoot or cross from his trademark right-side half-space.
- Maza operates between the lines, slipping through balls to Gouiri and arriving for cut-backs.
- Amoura's pace stretches defenders vertically and is the first outlet in transition.
- Gouiri leads the line, drops to combine, then attacks the cross -- the man for the decisive moment, as Jordan found out.

## Set Pieces
- Mahrez is the primary corner and free-kick taker, especially from the right.
- Mandi, Bensebaini, and Gouiri are aerial targets in the box.
- Penalties: Amoura (penalty 17) and Mahrez (penalty 16) are the first-choice takers.
- Defensive set pieces: zonal mark + Mandi on the most dangerous aerial threat; Austria carry an aerial threat from set plays, so stay disciplined.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Zidane) and unpressed: start short to the CBs (player_id ends with "_2" Bensebaini or "_3" Mandi) -- Algeria never wastes goal kicks; go long only under a committed press.
2. If player_id ends with "_5" (Bentaleb, pivot): drop between the center-backs in build-up, screen in defense, recycle through the back four, and progress with safe line-breaking passes; rarely shoots from deep.
3. If player_id ends with "_6" (Boudaoui, #14; stamina 17): high-energy box-to-box eight, win the ball back, drive forward, recycle possession; runs beyond the ball often.
4. If player_id ends with "_7" (Maza, advanced #8/#22): receive between the lines, turn forward, and look for a through ball to the CF (player_id ends with "_9", Gouiri) or a give-and-go with a winger.
5. If player_id ends with "_10" (Mahrez, RW #7; skill 17, dribbling 18, pass 17): receive on the right touchline, take on the full-back, cut inside, or whip a cross to the back post.
6. If player_id ends with "_4" (Belghali, RB #17): overlap when Mahrez (player_id ends with "_10") cuts inside; provide width on the right.
7. If player_id ends with "_9" (Gouiri, CF #9): lead the line, attack space behind defenses when through balls are on, and attack the box when the ball is wide -- clinical in the moment.
8. If player_id ends with "_8" (Amoura, LW #18; speed 17): attack the channel in behind with pace; first outlet on the counter; arrive at the back post on right-side crosses.
9. If defending: hold the 4-1-4-2 / 4-5-1 mid-block, Bentaleb (player_id ends with "_5") shielding the back four; press selectively against an organized Austria.
10. If turnover in own half: counter-press for 4 seconds, then drop into the mid-block.
11. If holding a lead in the final 15 minutes: keep the ball -- possession is the defensive plan, and qualification depends on it.
12. If Mahrez (player_id ends with "_10") is doubled: switch play to Amoura (player_id ends with "_8") within 2-3 touches; do not force the right side.
13. If trailing late: push Ait-Nouri (player_id ends with "_1", LB) high, push Maza (player_id ends with "_7") up alongside Gouiri (player_id ends with "_9") as a second striker, throw extra numbers forward -- a draw may not be enough depending on Austria's goal difference.

## Key Player Notes
- **Mahrez (skill 17, dribbling 18, pass 17, shoot 16)** is the talisman and captain; at 35, manage his defensive workload and give him the ball as often as possible. Reinstated from MD2 and kept his place for the decider.
- **Gouiri (#9, shoot 16, penalty 16)** delivered the 82nd-minute winner against Jordan that resuscitated the campaign -- the man Algeria look to in the decisive moment.
- **Boudaoui (#14, stamina 17, discipline 14)** is the combative left eight -- less creative flair but high pressing intensity and ball-winning energy; gives Algeria bite in midfield.
- **Maza (#22, skill 16, dribbling 16)** is the breakout advanced eight -- encourage him to drive between the lines and feed Gouiri.
- **Amoura (speed 17, shoot 17, penalty 17)** is the lead scorer and pace outlet; restored to the starting XI from MD2. Lethal on runs in behind and a first-choice penalty taker.
- **Ait-Nouri (speed 17, dribbling 16)** is a top-tier attacking full-back -- his overlaps power the left side, so cautious cover from Bentaleb is essential. Played through MD2 below 100% but is fit for Austria.
- **Bensebaini (#21)** is a significant upgrade at center-back with his aerial presence, ball-playing ability, and Dortmund-level experience; like Ait-Nouri, managed his minutes vs Jordan and is fit for the decider.

## Tournament Mindset
After the 0-3 opening defeat to Argentina (Messi hat-trick), Algeria's 2-1 Matchday 2 win over Jordan -- Gouiri striking in the 82nd minute -- put them back in control of their own destiny. They go into Matchday 3 level on three points with Austria but sit third on goal difference, so this Kansas City clash is effectively a winner-takes-all play-off for second place and a Round-of-32 berth, with Argentina already through and Jordan eliminated. Petkovic's strongest, full-strength XI is settled. The lesson from Argentina is clinical finishing: Algeria created almost nothing (0.32 xG, 1 shot on target) that day, but dominated and converted late against Jordan. Against an organized, physical Austria, they must control possession, be ruthless in the final third, and -- depending on goal difference -- recognize that a draw alone may not see them through.
