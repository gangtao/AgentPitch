# Ivory Coast — Tactical Profile

## Identity & Philosophy
The reigning 2023 AFCON champions, the Elephants under Emerse Faé combine elite physicality with technical front-line quality. Their 4-3-3 is possession-comfortable, midfield-controlled and defensively robust, anchored by a fast, powerful back line and Kessié's industrial midfield. After a 12-year absence they returned to the World Cup and emerged from Group E in second place behind Germany: a gritty 1-0 win over Ecuador (Yan Diomande's late winner), a narrow 2-1 loss to Germany to a stoppage-time goal, and a 2-0 win over Curaçao — a Nicolas Pépé brace — that sealed the knockout berth. Famous for late comebacks at AFCON 2023, they believe no match is over until the final whistle. Faé is pragmatic: the 4-3-3 can compress into a 4-1-4-1 or a low block depending on the opponent, leaning on organization, midfield control and transition play. Their one weakness all tournament has been finishing — clinical end-product is the difference in a one-off knockout.

## Round of 32 Lineup (vs Norway, June 30 — AT&T Stadium, Arlington TX, win-or-go-home)
This is a single-elimination knockout: lose and the World Cup is over. Faé fields his strongest available spine, with two changes forced by form and fitness:
- **Nicolas Pépé** starts at center-forward ahead of Ange-Yoan Bonny after his match-winning brace vs Curaçao — more mobile and a sharper finisher to address the finishing problem.
- **Ousmane Diomande** partners Kossounou at center-back (Emmanuel Agbadou drops to the bench); **Wilfried Singo remains doubtful** with a hamstring problem.
- Full-backs swap sides from the opener: **Guéla Doué at LB**, **Ghislain Konan at RB** — both attacking outlets tasked with width and defensive coverage against Norway's wide threats.
- Front three otherwise unchanged: **Yan Diomande** LW (the main 1v1 threat, age 19), **Amad Diallo** RW (primary creator), **Pépé** through the middle.
- Note: Norway carry Erling Haaland and Antonio Nusa — the wide and aerial duels will be decisive; Kessié captains and the back line must dominate the air.

## Formation
- Shape: 4-3-3, balanced and progressive; compacts to a 4-1-4-1 / low block out of possession.
- Role mapping (roster order in `ivory_coast.yaml`):
  - index 0: GK — **Yahia Fofana** — Goalkeeper, first choice, shot-stopper and short distributor.
  - index 1: LB — **Guéla Doué** — Left-back this game, quick energetic overlapper providing width on the left (speed 16, stamina 16).
  - index 2: LCB — **Ousmane Diomande** — Left center-back, fast ball-playing CB who steps out to win duels (strength 16).
  - index 3: RCB — **Odilon Kossounou** — Right center-back, fast, aggressive duel-winner who carries the ball into midfield (speed 16).
  - index 4: RB — **Ghislain Konan** — Right-back, attacking outlet who underlaps and provides width (stamina 16).
  - index 5: DM/#6 — **Ibrahim Sangaré** — Anchor, ball recycler and screen in front of the back four.
  - index 6: CM/#8 — **Franck Kessié** — Captain, defensive enforcer and aerial threat, arrives in the box; first-choice penalty taker.
  - index 7: RCM — **Christ Inao Oulaï** — Young box-to-box midfielder, powerful carrier and duel-winner.
  - index 8: LW — **Yan Diomande** — Left winger, direct pace and 1v1 threat (speed 17, dribbling 17); scored the MD1 winner vs Ecuador.
  - index 9: CF — **Nicolas Pépé** — Center-forward, mobile finisher cutting in from either side (shoot 16); scored a brace vs Curaçao.
  - index 10: RW — **Amad Diallo** — Right winger, dribbler, creator and matchwinner.

## Style of Play

### Build-up
- Patient but pragmatic; Kossounou steps forward as a ball-carrier into midfield.
- Sangaré drops between center-backs to form a 3+2 when needed.
- Full-backs push high; both Doué and Konan are energetic overlappers.
- Goalkeeper Fofana plays out short whenever possible, long to a forward if pressed hard.

### Pressing
- Mid-block, selectively aggressive — picking moments rather than a sustained high press against Norway's direct, transition-heavy game.
- Trigger: opposition CB receives with their back to goal or takes a heavy touch.
- Pépé and the wingers jump the back line and full-backs; Sangaré steps on the pivot.
- Kessié is the second-line presser — he hunts the pivot if the first wave is bypassed.

### Defensive shape
- 4-3-3 / 4-1-4-1 hybrid mid-block; drops into a compact low block to protect a lead.
- Sangaré shields the back four.
- Center-backs Ousmane Diomande and Kossounou are physical and step into midfield to win duels — they must win the aerial battle with Haaland and Sørloth.
- Wide players track Norway's wingers and overlapping full-backs deep when needed.

### Wide play
- Right: Amad Diallo cuts inside, Konan overlaps to provide the byline threat.
- Left: Yan Diomande runs in behind and hugs the touchline; Doué overlaps and provides width.
- Crosses are mixed — early balls and cutbacks for Pépé and arriving midfielders, cutbacks when Amad gets to the byline.

### Final third
- Pépé is the mobile focal point; he drifts to find pockets, attacks the channels and finishes crosses and cutbacks (shoot 16) — the answer to the tournament's finishing problem.
- Amad Diallo is the principal creator and dribbler; encourage 1v1s in the right half-space and shots onto his left foot.
- Yan Diomande's pace stretches defenses on the left; he attacks the channel constantly and is the prime counter-attack outlet — and Ivory Coast's MD1 matchwinner.
- Inao Oulaï makes late box arrivals; Kessié arrives on set pieces.

## Set Pieces
- Ousmane Diomande, Kossounou, Kessié, and Pépé are aerial threats — Ivory Coast scores a high proportion of goals from corners.
- Yan Diomande and Pépé handle most attacking corners and free kicks; Sangaré and Kessié alternate as deep deliverers.
- Penalties: Franck Kessié is first taker (penalty 16, captain); Amad Diallo (penalty 15) is the alternate.
- Defensive set pieces: mixed zonal-man, Kessié and Kossounou on the most dangerous aerial opponents — double up on Haaland.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Yahia Fofana) and pressed lightly: short to a CB (player_id ends with "_2", Ousmane Diomande, or "_3", Kossounou) first; long ball to the CF (player_id ends with "_9", Pépé) or a winger if pressed heavily.
2. If player_id ends with "_3" (Kossounou, RCB #7) and unpressed: drive forward with the ball into midfield up to 10m past halfway line.
3. If player_id ends with "_6" (Kessié, MID #8, captain) and ball is in midfield: prioritize duels — tackle aggressively if opposition is carrying the ball.
4. If player_id ends with "_10" (Amad Diallo, RW #15; skill 17, dribbling 17): take on the full-back 1v1; cut inside onto left foot, shoot from 18-22m or pass to the CF (player_id ends with "_9", Pépé).
5. If player_id ends with "_9" (Pépé, CF #19): drift into pockets and the channels, attack crosses and cutbacks in the box, and shoot first-time when the chance arrives (shoot 16) — be clinical.
6. If player_id ends with "_4" (Konan, RB #3): overlap on the right with energy, especially when Amad (player_id ends with "_10") cuts inside.
7. If player_id ends with "_7" (Inao Oulaï, MID #26): make late runs into the box on right-side cutbacks.
8. If turnover in opposition half: counter-press for 5 seconds.
9. If trailing or chasing the game: keep Yan Diomande (player_id ends with "_8") high as a wide forward, push numbers forward, increase risk in possession — commit both full-backs.
10. If defending a lead late: drop block 10m deeper, accept opposition possession, defend with 9 behind the ball — guard against Norway's transition through Haaland.
11. If player_id ends with "_8" (Yan Diomande, LW #11) is 1v1 on the left: encourage the dribble — his pace (17) and dribbling (17) beat the full-back to the byline; he is also the first counter-attack outlet on transitions.
12. If a set piece is awarded in the opposition half: send Kessié (player_id ends with "_6"), Ousmane Diomande (player_id ends with "_2"), Kossounou (player_id ends with "_3"), and Pépé (player_id ends with "_9") up; this is a major scoring source.
13. When tackling: only commit if player_id ends with "_2", "_3", "_5", or "_6" (Diomande/Kossounou/Sangaré/Kessié) AND the ball-carrier has poor body shape; otherwise Hold and contain — no rash fouls in a knockout.

## Key Player Notes
- **Kessié (strength 17, skill 16, penalty 16)** is the captain and team's backbone — his physicality wins the midfield battle; first-choice penalty taker.
- **Amad Diallo (skill 17, dribbling 17, penalty 15)** is the primary creator and matchwinner — the key to unlocking Norway and the alternate penalty taker.
- **Nicolas Pépé (shoot 16, idx 9)** starts up top after his Curaçao brace — mobile finisher brought in to fix the team's finishing; cuts in from either flank.
- **Kossounou** is comfortable carrying the ball — encourage progressive runs; a key aerial threat alongside Ousmane Diomande.
- **Yan Diomande's pace (17, idx 8)** is the team's vertical weapon on the left and the principal counter-attack outlet; he scored the winner vs Ecuador in MD1.
- **Guéla Doué (idx 1) and Ghislain Konan (idx 4)** are the energetic overlapping full-backs providing width — both must balance attack with defending Norway's wide men.
- **Singo is doubtful** with a hamstring problem; **Agbadou and Bonny drop to the bench** for this knockout XI.

## Tournament Mindset
This is win-or-go-home. Ivory Coast believes they can win or rescue any match — they came back twice at AFCON 2023 and have shown knockout temperament. They will trust their organization and midfield control, break with pace out wide and aerial power at set pieces, and demand more clinical finishing from Pépé and the front three. They will not panic if behind, are equally comfortable defending a lead in a low block, and will accept extra time and penalties — Kessié leads a confident spot-kick group. Discipline matters: no rash fouls that gift Norway set pieces for Haaland.
