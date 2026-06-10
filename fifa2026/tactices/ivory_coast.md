# Ivory Coast — Tactical Profile

## Identity & Philosophy
The reigning 2023 AFCON champions, the Elephants under Emerse Faé combine physical midfield presence with technical front-line quality. Their 4-3-3 is possession-comfortable and defensively robust, anchored by a brilliant CB pairing and Kessié's industrial midfield. Famous for late comebacks at home AFCON 2023 — they believe no match is over until the final whistle.

## Formation
- Shape: 4-3-3, balanced and progressive.
- Role mapping (roster index -> tactical role):
  - index 0: GK — **Fofana** — Goalkeeper, modern distributor.
  - index 1: LB — **Konan** — Left-back, attacking outlet.
  - index 2: LCB — **Agbadou** — Left center-back, physical duel-winner (strength 17).
  - index 3: RCB — **Kossounou** — Right center-back, recovery pace and the more comfortable carrier.
  - index 4: RB — **Guéla Doué** — Right-back, fast overlapping athlete (speed 16).
  - index 5: LCM — **Seko Fofana** — #8 / box-to-box, powerful carrier, late-arriving runner.
  - index 6: DM — **Sangaré** — #6, ball recycler and screen in front of the back four.
  - index 7: RCM — **Kessié** — #8, defensive enforcer and aerial threat, arrives in the box.
  - index 8: LW — **Yan Diomande** — Left winger, direct pace and 1v1 threat (speed 17, dribbling 17).
  - index 9: CF — **Guessand** — Center-forward, physical, mobile focal point and box presence.
  - index 10: RW — **Amad Diallo** — Right winger, dribbler and creator.

## Style of Play

### Build-up
- Patient, with Kossounou stepping forward as a ball-carrier into midfield.
- Sangaré drops between center-backs to form a 3+2 when needed.
- Full-backs push high; Doué especially likes to overlap with his pace.
- Goalkeeper Fofana plays out short whenever possible.

### Pressing
- Mid-to-high press, situational.
- Trigger: opposition CB receives with their back to goal.
- Guessand presses the CB; wingers jump the full-backs; Seko Fofana steps on the pivot.
- Kessié is the second-line presser — he hunts the pivot if Guessand's first wave is bypassed.

### Defensive shape
- 4-3-3 / 4-1-4-1 hybrid mid-block.
- Sangaré shields the back four.
- Center-backs Agbadou and Kossounou are physical and step into midfield to win duels.
- Wide players track full-backs deep when needed.

### Wide play
- Right: Amad Diallo cuts inside, Doué overlaps.
- Left: Diomande runs in behind and hugs the touchline; Konan underlaps and provides width.
- Crosses are mixed — early balls and cutbacks for Guessand to attack in the box, cutbacks when Diallo gets to the byline.

### Final third
- Guessand is the physical focal point; he occupies center-backs and finishes crosses and cutbacks (shoot 15).
- Amad Diallo is the principal dribbler; encourage 1v1s in the right half-space.
- Diomande's pace stretches defenses on the left; he attacks the channel constantly.
- Amad shoots from distance — he's the wildcard creator.
- Seko Fofana makes late box arrivals; Kessié arrives on set pieces.

## Set Pieces
- Agbadou, Kossounou, and Kessié are all major aerial threats — Ivory Coast scores a high proportion of goals from corners.
- Amad Diallo takes most attacking set pieces.
- Defensive set pieces: mixed zonal-man, Kessié on the most dangerous aerial opponent.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Yahia Fofana) and pressed lightly: short to a CB (player_id ends with "_2", Agbadou, or "_3", Kossounou) first; long ball to the CF (player_id ends with "_9", Guessand, strength 15) to hold up if pressed heavily.
2. If player_id ends with "_3" (Kossounou, RCB #7) and unpressed: drive forward with the ball into midfield up to 10m past halfway line.
3. If player_id ends with "_7" (Kessié, MID #8) and ball is in midfield: prioritize duels — tackle aggressively if opposition is carrying the ball.
4. If player_id ends with "_10" (Amad Diallo, RW #15; skill 17, dribbling 17): take on the full-back 1v1; cut inside onto left foot, shoot or pass to the CF (player_id ends with "_9", Guessand).
5. If player_id ends with "_9" (Guessand, CF #22): occupy the center-backs, hold up play, and attack crosses and cutbacks in the box; peel onto the back line for through balls when a midfielder is facing forward.
6. If player_id ends with "_4" (Guéla Doué, RB #17): overlap on the right with pace, especially when Amad (player_id ends with "_10") cuts inside.
7. If player_id ends with "_5" (Seko Fofana, MID #6): make late runs into the box on right-side cutbacks.
8. If turnover in opposition half: counter-press for 5 seconds.
9. If trailing in the second half: keep Diomande (player_id ends with "_8") high as a wide forward, push numbers forward, increase risk in possession.
10. If defending a 1-0 lead late: drop block 10m deeper, accept opposition possession, defend with 9 behind the ball.
11. If player_id ends with "_8" (Diomande, LW #11) is 1v1 on the left: encourage the dribble — his pace (17) and dribbling (17) beat the full-back to the byline.
12. If a set piece is awarded in the opposition half: send Kessié (player_id ends with "_7"), Agbadou (player_id ends with "_2"), and Kossounou (player_id ends with "_3") up; this is a major scoring source.

## Key Player Notes
- **Kessié (strength 17, skill 16)** is the team's backbone — his physicality wins the midfield battle.
- **Amad Diallo (skill 17, dribbling 17)** is the primary creator; treat him as the talisman.
- **Kossounou** is comfortable carrying the ball — encourage progressive runs.
- **Diomande's pace (17)** is the team's vertical weapon on the left; pair him with Amad's creativity.
- **Guéla Doué (speed 16)** is a fast overlapping right-back who doubles as an attacking outlet.
- **Guessand (shoot 15, strength 15)** gives the attack a genuine, mobile focal point — play to his physicality in the box.

## Tournament Mindset
Ivory Coast believes they can come back from any deficit — they did it twice at AFCON 2023. They will not panic if behind at halftime; they trust their squad depth and quality.
