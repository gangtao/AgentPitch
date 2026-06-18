# Ivory Coast — Tactical Profile

## Identity & Philosophy
The reigning 2023 AFCON champions, the Elephants under Emerse Faé combine elite physicality with technical front-line quality. Their 4-3-3 is possession-comfortable and defensively robust, anchored by a fast, powerful back line and Kessié's industrial midfield. After a 12-year absence they returned to the World Cup and opened with a gritty 1-0 win over previously-unbeaten Ecuador — Amad Diallo struck a 90th-minute winner off the bench, assisted by Singo. Famous for late comebacks at home AFCON 2023, they believe no match is over until the final whistle. Faé is pragmatic: the 4-3-3 can compress into a 4-2-3-1 or a low block depending on the opponent, and against Germany (Matchday 2, BMO Field Toronto) he will trust a deep, organised mid-block and the counter through Yan Diomande and Amad.

## Formation
- Shape: 4-3-3, balanced and progressive; compacts to a 4-1-4-1 / low block out of possession.
- Role mapping (roster index -> tactical role):
  - index 0: GK — **Yahia Fofana** — Goalkeeper, first choice, shot-stopper and short distributor.
  - index 1: LB/LCB — **Ndicka** — Left-sided defender, composed left-footed progressor (hamstring doubt; Konan deputises if unfit).
  - index 2: LCB — **Ousmane Diomande** — Left center-back, fast, aggressive duel-winner who steps out.
  - index 3: RCB — **Agbadou** — Right center-back, the physical anchor (strength 17).
  - index 4: RB — **Wilfried Singo** — Right-back, elite athlete (speed 17, stamina 17), overlaps and assisted the MD1 winner.
  - index 5: LCM — **Seko Fofana** — #8 / box-to-box, powerful carrier and late-arriving runner.
  - index 6: DM — **Sangaré** — #6, ball recycler and screen in front of the back four.
  - index 7: RCM — **Kessié** — #8, defensive enforcer and aerial threat, arrives in the box.
  - index 8: LW — **Yan Diomande** — Left winger, direct pace and 1v1 threat (speed 17, dribbling 17); Ivory Coast's best player vs Ecuador.
  - index 9: CF — **Guessand** — Center-forward, physical, mobile focal point and box presence.
  - index 10: RW — **Amad Diallo** — Right winger, dribbler, creator and matchwinner (scored the 90th-min winner vs Ecuador).

## Style of Play

### Build-up
- Patient but pragmatic; Ousmane Diomande steps forward as a ball-carrier into midfield.
- Sangaré drops between center-backs to form a 3+2 when needed.
- Full-backs push high; Singo especially likes to overlap with his pace.
- Goalkeeper Fofana plays out short whenever possible, long to Guessand if pressed hard.

### Pressing
- Mid-to-high press, situational — more conservative vs a strong build-up side like Germany.
- Trigger: opposition CB receives with their back to goal.
- Guessand presses the CB; wingers jump the full-backs; Seko Fofana steps on the pivot.
- Kessié is the second-line presser — he hunts the pivot if Guessand's first wave is bypassed.

### Defensive shape
- 4-3-3 / 4-1-4-1 hybrid mid-block; drops into a compact low block to protect a lead.
- Sangaré shields the back four.
- Center-backs Ousmane Diomande and Agbadou are physical and step into midfield to win duels.
- Wide players track full-backs deep when needed.

### Wide play
- Right: Amad Diallo cuts inside, Singo overlaps (the MD1 goal pattern).
- Left: Yan Diomande runs in behind and hugs the touchline; Ndicka underlaps and provides width.
- Crosses are mixed — early balls and cutbacks for Guessand to attack in the box, cutbacks when Amad gets to the byline.

### Final third
- Guessand is the physical focal point; he occupies center-backs and finishes crosses and cutbacks (shoot 15).
- Amad Diallo is the principal creator and dribbler; encourage 1v1s in the right half-space and shots onto his left foot.
- Yan Diomande's pace stretches defenses on the left; he attacks the channel constantly and is the prime counter-attack outlet.
- Seko Fofana makes late box arrivals; Kessié arrives on set pieces.

## Set Pieces
- Agbadou, Ousmane Diomande, Kessié, and Singo are all major aerial threats — Ivory Coast scores a high proportion of goals from corners.
- Amad Diallo takes most attacking set pieces; Seko Fofana and Kessié alternate as deep deliverers.
- Penalties: Amad Diallo is first taker (penalty 16, ice-cold finisher); Kessié (penalty 15) and Guessand (penalty 15) are alternates.
- Defensive set pieces: mixed zonal-man, Kessié and Agbadou on the most dangerous aerial opponents.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Yahia Fofana) and pressed lightly: short to a CB (player_id ends with "_2", Ousmane Diomande, or "_3", Agbadou) first; long ball to the CF (player_id ends with "_9", Guessand, strength 15) to hold up if pressed heavily.
2. If player_id ends with "_2" (Ousmane Diomande, LCB #5) and unpressed: drive forward with the ball into midfield up to 10m past halfway line.
3. If player_id ends with "_7" (Kessié, MID #8) and ball is in midfield: prioritize duels — tackle aggressively if opposition is carrying the ball.
4. If player_id ends with "_10" (Amad Diallo, RW #15; skill 17, dribbling 17): take on the full-back 1v1; cut inside onto left foot, shoot from 18-22m or pass to the CF (player_id ends with "_9", Guessand).
5. If player_id ends with "_9" (Guessand, CF #22): occupy the center-backs, hold up play, and attack crosses and cutbacks in the box; peel onto the back line for through balls when a midfielder is facing forward.
6. If player_id ends with "_4" (Singo, RB #17, speed 17): overlap on the right with pace, especially when Amad (player_id ends with "_10") cuts inside — this combination created the MD1 winner.
7. If player_id ends with "_5" (Seko Fofana, MID #6): make late runs into the box on right-side cutbacks.
8. If turnover in opposition half: counter-press for 5 seconds.
9. If trailing in the second half: keep Yan Diomande (player_id ends with "_8") high as a wide forward, push numbers forward, increase risk in possession.
10. If defending a 1-0 lead late: drop block 10m deeper, accept opposition possession, defend with 9 behind the ball — this won them the Ecuador game.
11. If player_id ends with "_8" (Yan Diomande, LW #11) is 1v1 on the left: encourage the dribble — his pace (17) and dribbling (17) beat the full-back to the byline; he is also the first counter-attack outlet on transitions.
12. If a set piece is awarded in the opposition half: send Kessié (player_id ends with "_7"), Agbadou (player_id ends with "_3"), Ousmane Diomande (player_id ends with "_2"), and Singo (player_id ends with "_4") up; this is a major scoring source.

## Key Player Notes
- **Kessié (strength 17, skill 16)** is the team's backbone — his physicality wins the midfield battle; alternate penalty taker.
- **Amad Diallo (skill 17, dribbling 17, penalty 16)** is the primary creator and matchwinner — scored the 90th-minute winner vs Ecuador; first-choice penalty taker. Was a second-half sub in MD1 and is expected to start vs Germany.
- **Ousmane Diomande** is comfortable carrying the ball — encourage progressive runs; a key aerial threat.
- **Yan Diomande's pace (17)** is the team's vertical weapon on the left and the principal counter-attack outlet; he was Ivory Coast's best player vs Ecuador.
- **Wilfried Singo (speed 17, stamina 17)** is an explosive overlapping right-back who doubles as an attacking outlet — he assisted the MD1 winner.
- **Guessand (shoot 15, strength 15)** gives the attack a genuine, mobile focal point — play to his physicality in the box.
- **Ndicka (idx 1)** carries a hamstring doubt after missing the Ecuador opener; Ghislain Konan deputises on the left if he is not fit.

## Tournament Mindset
Ivory Coast believes they can win or rescue any match — they came back twice at AFCON 2023 and ground out a last-gasp win in their World Cup opener. They will not panic if behind, and they are equally comfortable defending a lead in a low block. Against Germany they will sit deeper, stay compact, and strike on the counter through their pace.
