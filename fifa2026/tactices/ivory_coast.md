# Ivory Coast — Tactical Profile

## Identity & Philosophy
The reigning 2023 AFCON champions, the Elephants under Emerse Faé combine physical midfield presence with technical front-line quality. Their 4-3-3 is possession-comfortable and defensively robust, anchored by a brilliant CB pairing and Kessié's industrial midfield. Famous for late comebacks at home AFCON 2023 — they believe no match is over until the final whistle.

## Formation
- Shape: 4-3-3, balanced and progressive.
- Role mapping (roster index -> tactical role):
  - 0 Fofana — Goalkeeper, modern distributor.
  - 1 Konan — Left-back, attacking outlet.
  - 2 Ndicka — Left center-back, ball-playing.
  - 3 Kossounou — Right center-back, recovery pace.
  - 4 Singo — Right-back, explosive overlapping athlete.
  - 5 Seko Fofana — #8 / box-to-box, late-arriving runner.
  - 6 Kessié — #6, defensive enforcer and aerial threat.
  - 7 Sangaré — #8, ball recycler, second screener.
  - 8 Amad Diallo — Right winger, dribbler and creator.
  - 9 Bonny — Center-forward, physical focal point and box presence.
  - 10 Adingra — Left winger, direct pace and 1v1 threat.

## Style of Play

### Build-up
- Patient, with Ndicka stepping forward as a ball-carrier into midfield.
- Kessié drops between center-backs to form a 3+2 when needed.
- Full-backs push high; Singo especially likes to overlap with his power and pace.
- Goalkeeper Fofana plays out short whenever possible.

### Pressing
- Mid-to-high press, situational.
- Trigger: opposition CB receives with their back to goal.
- Bonny presses the CB; wingers jump the full-backs; Seko Fofana steps on the pivot.
- Kessié is the second-line presser — he hunts the pivot if Bonny's first wave is bypassed.

### Defensive shape
- 4-3-3 / 4-1-4-1 hybrid mid-block.
- Kessié shields the back four.
- Center-backs Ndicka and Kossounou are physical and step into midfield to win duels.
- Wide players track full-backs deep when needed.

### Wide play
- Right: Amad Diallo cuts inside, Singo overlaps.
- Left: Adingra runs in behind and hugs the touchline; Konan underlaps and provides width.
- Crosses are mixed — early balls and cutbacks for Bonny to attack in the box, cutbacks when Diallo gets to the byline.

### Final third
- Bonny is the physical focal point; he occupies center-backs and finishes crosses and cutbacks.
- Amad Diallo is the principal dribbler; encourage 1v1s in the right half-space.
- Adingra's pace stretches defenses on the left; he attacks the channel constantly.
- Amad shoots from distance — he's the wildcard creator.
- Seko Fofana makes late box arrivals; Kessié arrives on set pieces.

## Set Pieces
- Ndicka, Kossounou, and Kessié are all major aerial threats — Ivory Coast scores a high proportion of goals from corners.
- Amad Diallo takes most attacking set pieces.
- Defensive set pieces: mixed zonal-man, Kessié on the most dangerous aerial opponent.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Yahia Fofana) and pressed lightly: short to the LCB (player_id ends with "_2", Ndicka) first; long ball to the CF (player_id ends with "_9", Bonny) to hold up if pressed heavily.
2. If player_id ends with "_2" (Ndicka, LCB #4) and unpressed: drive forward with the ball into midfield up to 10m past halfway line.
3. If player_id ends with "_6" (Kessié, MID #19) and ball is in midfield: prioritize duels — tackle aggressively if opposition is carrying the ball.
4. If player_id ends with "_8" (Amad Diallo, RW #20; skill 17, dribbling 17): take on the full-back 1v1; cut inside onto left foot, shoot or pass to the CF (player_id ends with "_9", Bonny).
5. If player_id ends with "_9" (Bonny, CF #24): occupy the center-backs, hold up play, and attack crosses and cutbacks in the box; peel onto the back line for through balls when a midfielder is facing forward.
6. If player_id ends with "_4" (Singo, RB #17): overlap on the right with pace, especially when Amad (player_id ends with "_8") cuts inside.
7. If player_id ends with "_5" (Seko Fofana, MID #8): make late runs into the box on right-side cutbacks.
8. If turnover in opposition half: counter-press for 5 seconds.
9. If trailing in the second half: keep Adingra (player_id ends with "_10") high as a wide forward, push numbers forward, increase risk in possession.
10. If defending a 1-0 lead late: drop block 10m deeper, accept opposition possession, defend with 9 behind the ball.
11. If player_id ends with "_10" (Adingra, LW #7) is 1v1 on the left: encourage the dribble — his pace and skill beat the full-back to the byline.
12. If a set piece is awarded in the opposition half: send Kessié (player_id ends with "_6"), Ndicka (player_id ends with "_2"), and Kossounou (player_id ends with "_3") up; this is a major scoring source.

## Key Player Notes
- **Kessié (strength 17, skill 16)** is the team's backbone — his physicality wins the midfield battle.
- **Amad Diallo (skill 17, dribbling 17)** is the primary creator; treat him as the talisman.
- **Ndicka** is comfortable carrying the ball — encourage progressive runs.
- **Adingra's pace (17)** is the team's vertical weapon on the left; pair him with Amad's creativity.
- **Singo (speed 17, strength 17)** is an explosive right-back who doubles as an attacking outlet.
- **Bonny** gives the attack a genuine focal point after Haller's omission — play to his physicality in the box.

## Tournament Mindset
Ivory Coast believes they can come back from any deficit — they did it twice at AFCON 2023. They will not panic if behind at halftime; they trust their squad depth and quality.
