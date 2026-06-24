# Ivory Coast — Tactical Profile

## Identity & Philosophy
The reigning 2023 AFCON champions, the Elephants under Emerse Faé combine elite physicality with technical front-line quality. Their 4-3-3 is possession-comfortable and defensively robust, anchored by a fast, powerful back line and Kessié's industrial midfield. After a 12-year absence they returned to the World Cup and opened with a gritty 1-0 win over Ecuador — Yan Diomande struck a late winner. In Matchday 2 they pushed Germany hard but conceded a stoppage-time goal to lose 2-1 at BMO Field, Toronto, leaving them second in Group E on three points. Famous for late comebacks at home AFCON 2023, they believe no match is over until the final whistle. Faé is pragmatic: the 4-3-3 can compress into a 4-2-3-1 or a low block depending on the opponent. Heading into the decisive Matchday 3 vs Curaçao (Lincoln Financial Field, Philadelphia), a draw secures qualification as runners-up — but the Elephants will press to win, forced into changes with Singo injured and Ndicka still doubtful.

## Formation
- Shape: 4-3-3, balanced and progressive; compacts to a 4-1-4-1 / low block out of possession.
- Role mapping (roster index -> tactical role):
  - index 0: GK — **Yahia Fofana** — Goalkeeper, first choice, shot-stopper and short distributor.
  - index 1: LB — **Ghislain Konan** — Left-back, attacking outlet who underlaps and provides width; deputised on the left in the opening games.
  - index 2: LCB — **Agbadou** — Left center-back, the physical anchor (strength 17).
  - index 3: RCB — **Kossounou** — Right center-back, fast, aggressive duel-winner who steps out (speed 16).
  - index 4: RB — **Guéla Doué** — Right-back, replaces the injured Singo; quick, energetic overlapper (speed 16, stamina 16).
  - index 5: LCM — **Sangaré** — #6, ball recycler and screen in front of the back four.
  - index 6: CM — **Kessié** — Captain, #8, defensive enforcer and aerial threat, arrives in the box.
  - index 7: RCM — **Inao Oulaï** — Young box-to-box midfielder, powerful carrier and duel-winner.
  - index 8: LW — **Yan Diomande** — Left winger, direct pace and 1v1 threat (speed 17, dribbling 17); scored the MD1 winner vs Ecuador.
  - index 9: CF — **Bonny** — Center-forward, physical, mobile focal point and box presence (shoot 15, strength 16).
  - index 10: RW — **Amad Diallo** — Right winger, dribbler, creator and matchwinner; first-choice penalty taker.

## Style of Play

### Build-up
- Patient but pragmatic; Kossounou steps forward as a ball-carrier into midfield.
- Sangaré drops between center-backs to form a 3+2 when needed.
- Full-backs push high; Doué especially likes to overlap with his pace.
- Goalkeeper Fofana plays out short whenever possible, long to Bonny if pressed hard.

### Pressing
- Mid-to-high press — Ivory Coast can be more aggressive against the lower-ranked Curaçao than they were vs Germany.
- Trigger: opposition CB receives with their back to goal.
- Bonny presses the CB; wingers jump the wing-backs; Sangaré steps on the pivot.
- Kessié is the second-line presser — he hunts the pivot if Bonny's first wave is bypassed.

### Defensive shape
- 4-3-3 / 4-1-4-1 hybrid mid-block; drops into a compact low block to protect a lead.
- Sangaré shields the back four.
- Center-backs Agbadou and Kossounou are physical and step into midfield to win duels.
- Wide players track wing-backs deep when needed — Curaçao's 5-4-1 pushes wing-backs high.

### Wide play
- Right: Amad Diallo cuts inside, Doué overlaps to provide the byline threat.
- Left: Yan Diomande runs in behind and hugs the touchline; Konan underlaps and provides width.
- Crosses are mixed — early balls and cutbacks for Bonny to attack in the box, cutbacks when Amad gets to the byline.

### Final third
- Bonny is the physical focal point; he occupies center-backs and finishes crosses and cutbacks (shoot 15).
- Amad Diallo is the principal creator and dribbler; encourage 1v1s in the right half-space and shots onto his left foot.
- Yan Diomande's pace stretches defenses on the left; he attacks the channel constantly and is the prime counter-attack outlet — and Ivory Coast's MD1 matchwinner.
- Inao Oulaï makes late box arrivals; Kessié arrives on set pieces.

## Set Pieces
- Agbadou, Kossounou, Kessié, and Bonny are all major aerial threats — Ivory Coast scores a high proportion of goals from corners, key against Curaçao's packed box.
- Amad Diallo takes most attacking set pieces; Sangaré and Kessié alternate as deep deliverers.
- Penalties: Amad Diallo is first taker (penalty 16, ice-cold finisher); Kessié (penalty 15) is the alternate.
- Defensive set pieces: mixed zonal-man, Kessié and Agbadou on the most dangerous aerial opponents.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Yahia Fofana) and pressed lightly: short to a CB (player_id ends with "_2", Agbadou, or "_3", Kossounou) first; long ball to the CF (player_id ends with "_9", Bonny, strength 16) to hold up if pressed heavily.
2. If player_id ends with "_3" (Kossounou, RCB #7) and unpressed: drive forward with the ball into midfield up to 10m past halfway line.
3. If player_id ends with "_6" (Kessié, MID #8, captain) and ball is in midfield: prioritize duels — tackle aggressively if opposition is carrying the ball.
4. If player_id ends with "_10" (Amad Diallo, RW #15; skill 17, dribbling 17): take on the full-back 1v1; cut inside onto left foot, shoot from 18-22m or pass to the CF (player_id ends with "_9", Bonny).
5. If player_id ends with "_9" (Bonny, CF #9): occupy the center-backs, hold up play, and attack crosses and cutbacks in the box; peel onto the back line for through balls when a midfielder is facing forward.
6. If player_id ends with "_4" (Doué, RB #17, speed 16): overlap on the right with pace, especially when Amad (player_id ends with "_10") cuts inside.
7. If player_id ends with "_7" (Inao Oulaï, MID #26): make late runs into the box on right-side cutbacks.
8. If turnover in opposition half: counter-press for 5 seconds.
9. If trailing or chasing the game: keep Yan Diomande (player_id ends with "_8") high as a wide forward, push numbers forward, increase risk in possession — Curaçao will sit deep, so commit the full-backs.
10. If defending a lead late: drop block 10m deeper, accept opposition possession, defend with 9 behind the ball — this won them the Ecuador game.
11. If player_id ends with "_8" (Yan Diomande, LW #11) is 1v1 on the left: encourage the dribble — his pace (17) and dribbling (17) beat the full-back to the byline; he is also the first counter-attack outlet on transitions.
12. If a set piece is awarded in the opposition half: send Kessié (player_id ends with "_6"), Agbadou (player_id ends with "_2"), Kossounou (player_id ends with "_3"), and Bonny (player_id ends with "_9") up; this is a major scoring source against a deep block.

## Key Player Notes
- **Kessié (strength 17, skill 16)** is the captain and team's backbone — his physicality wins the midfield battle; alternate penalty taker.
- **Amad Diallo (skill 17, dribbling 17, penalty 16)** is the primary creator and matchwinner — first-choice penalty taker and the key to unlocking Curaçao's 5-4-1.
- **Kossounou** is comfortable carrying the ball — encourage progressive runs; a key aerial threat alongside Agbadou.
- **Yan Diomande's pace (17)** is the team's vertical weapon on the left and the principal counter-attack outlet; he scored the winner vs Ecuador in MD1.
- **Guéla Doué (speed 16, stamina 16)** steps in for the injured Singo at right-back — an energetic overlapping outlet on the right flank.
- **Bonny (shoot 15, strength 16)** gives the attack a genuine, mobile focal point — play to his physicality in the box.
- **Inao Oulaï (idx 7)** is the young legs in midfield, a powerful carrier and duel-winner; **Singo is out injured** and **Ndicka remains doubtful** after a thigh problem.

## Tournament Mindset
Ivory Coast believes they can win or rescue any match — they came back twice at AFCON 2023 and ground out a last-gasp win in their World Cup opener. Sitting second on three points, a draw vs Curaçao sends them through as runners-up, but they will not park the bus: they aim to win, controlling possession and breaking down a deep 5-4-1 with pace out wide and aerial power at set pieces. They will not panic if behind, and they are equally comfortable defending a lead in a low block.
