# Algeria -- Tactical Profile

## Identity & Philosophy
Under Vladimir Petkovic, Algeria plays with North African technical flair, prizing ball circulation, half-space combinations, and Mahrez's right-foot whip. For the Round of 16 the manager shifts to a **4-2-3-1** -- a double pivot behind a fluid attacking three -- to add midfield solidity for a win-or-go-home knockout while still giving his creators licence to combine. Having survived a brutal group with Argentina, Austria and Jordan to reach the last 16, the Desert Foxes now face Switzerland at BC Place, Vancouver. As underdogs they will look to be compact, control possession in spells, and hurt an organized Swiss side on the counter through Mahrez, Maza and Chaïbi. The squad is fully available bar one major doubt: lead scorer Mohamed Amoura is a serious injury concern (hamstring, picked up in the group stage) and is not expected to start; Farès Chaïbi comes into the attacking band in his place.

## Formation
- Shape: 4-2-3-1, with a double pivot (Bentaleb + Boudaoui) shielding the back four and three fluid attacking midfielders behind a lone striker.
- Note: Amoura (hamstring) is a serious doubt and is not in the probable XI; if he passes a late fitness test he can return on the left, but Chaïbi starts here. In goal Petkovic restores Luca Zidane after Benbot struggled deputizing against Austria. No suspensions -- the rest of the squad is fully available. Tougai (CB), Zerrouki (MID) and Aouar (MID) provide the most pressing competition off the bench.
- Role mapping (roster index -> tactical role):
  - index 0: GK -- Luca Zidane (#23), comfortable with the ball at his feet; restored as first choice for the knockout.
  - index 1: DEF -- Ait-Nouri (#15), left-back, explosive and technical, drives the overlap.
  - index 2: DEF -- Bensebaini (#21), left center-back, experienced Dortmund defender, strong in the air and on the ball.
  - index 3: DEF -- Mandi (#2), right center-back, captain-grade organizer, record cap-holder.
  - index 4: DEF -- Belghali (#17), right-back, energetic attacking crosser.
  - index 5: MID -- Bentaleb (#19), deep pivot, screens the back four and recycles possession.
  - index 6: MID -- Boudaoui (#14), second pivot / ball-winner, tireless high work-rate alongside Bentaleb.
  - index 7: MID -- Chaïbi (#8), left attacking midfielder, creative left-footer deputizing for Amoura; cuts inside and links play.
  - index 8: MID -- Maza (#22), central attacking midfielder / free no. 10, drives between the lines and feeds the striker.
  - index 9: MID -- Mahrez (#7), right attacking midfielder, captain, primary creator; stays wide, cuts inside onto his left.
  - index 10: FWD -- Gouiri (#9), lone center-forward, link play and finishing; the man for the decisive moment.

## Style of Play

### Build-up
- One of the two pivots (usually Bentaleb) drops between or beside the center-backs to form a back three in possession.
- Both full-backs push to the touchline; Ait-Nouri in particular bombs forward on the left.
- Zidane is comfortable receiving back passes and resetting play.
- Switches of play are common -- Mahrez and the pivots look for the diagonal to the opposite flank.

### Pressing
- Switzerland are organized and physical, so the press is selective -- pick triggers rather than chasing blindly.
- Selective press from the 4-2-3-1 that becomes a 4-4-2 hybrid, Maza stepping up alongside Gouiri.
- Trigger: opposition center-back receives with their weaker foot exposed, or a loose touch in their build-up.
- Mahrez and Chaïbi jump the full-backs; the front line curves passing lanes inward.
- Boudaoui's energy sustains the press when Algeria choose to go.

### Defensive shape
- 4-4-1-1 / 4-5-1 mid-block when out of possession.
- Bentaleb and Boudaoui form a compact double pivot; Chaïbi and Mahrez drop onto the flanks of a bank of four, Maza screening ahead.
- Mandi and Bensebaini hold the line; Ait-Nouri and Belghali stay narrower when the ball is on the opposite side.
- Against a knockout opponent, staying compact and denying central space is the priority; concede the ball rather than the space.

### Wide play
- Right side: Mahrez stays wide on the touchline, demands the ball, cuts inside onto his left foot.
- Left side: Chaïbi drifts inside from the left; Ait-Nouri overlaps aggressively to supply the width Amoura would otherwise carry.
- Crosses from Mahrez are usually whipped to the back post for Gouiri or a late-arriving Maza.

### Final third
- Mahrez is the chief creator -- encourage him to shoot or cross from his trademark right-side half-space.
- Maza operates between the lines, slipping through balls to Gouiri and arriving for cut-backs.
- Chaïbi provides left-sided creativity and a second passing brain; combine with Ait-Nouri to unlock the left channel.
- Gouiri leads the line alone, drops to combine, then attacks the cross -- the man for the decisive moment.

## Set Pieces
- Mahrez is the primary corner and free-kick taker, especially from the right.
- Mandi, Bensebaini, and Gouiri are aerial targets in the box.
- **Penalties (in-game and shootout order, with Amoura injured):** 1) Mahrez (penalty 16), 2) Gouiri (penalty 16), 3) Maza (penalty 14), 4) Ait-Nouri (penalty 12), 5) Bentaleb (penalty 12). If Amoura is passed fit and starts, he becomes the No. 1 taker (penalty 17) ahead of Mahrez.
- Defensive set pieces: zonal mark + Mandi on the most dangerous aerial threat; Switzerland carry an aerial threat (Akanji, Embolo), so stay disciplined.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Zidane) and unpressed: start short to the CBs (player_id ends with "_2" Bensebaini or "_3" Mandi) -- go long only under a committed press.
2. If player_id ends with "_5" (Bentaleb, deep pivot): drop between the center-backs in build-up, screen in defense, recycle through the back four, and progress with safe line-breaking passes; rarely shoots from deep.
3. If player_id ends with "_6" (Boudaoui, #14; stamina 17): second pivot -- win the ball back, cover the spaces Ait-Nouri vacates, and progress with short forward passes.
4. If player_id ends with "_8" (Maza, central no. 10 #22): receive between the lines, turn forward, and look for a through ball to the CF (player_id ends with "_10", Gouiri) or a give-and-go with a winger.
5. If player_id ends with "_9" (Mahrez, RW #7; skill 17, dribbling 18, pass 17): receive on the right touchline, take on the full-back, cut inside, or whip a cross to the back post.
6. If player_id ends with "_7" (Chaïbi, LW #8): drift inside from the left, combine with Ait-Nouri, and thread through balls or shift the ball back to the right for Mahrez.
7. If player_id ends with "_4" (Belghali, RB #17): overlap when Mahrez (player_id ends with "_9") cuts inside; provide width on the right.
8. If player_id ends with "_10" (Gouiri, lone CF #9): lead the line, attack space behind defenses when through balls are on, and attack the box when the ball is wide -- clinical in the moment.
9. If player_id ends with "_1" (Ait-Nouri, LB): overlap high on the left to supply width, especially when Chaïbi drifts inside.
10. If defending: hold the compact 4-4-1-1 / 4-5-1 mid-block, Bentaleb (player_id ends with "_5") and Boudaoui (player_id ends with "_6") shielding the back four; press selectively against an organized Switzerland.
11. If turnover in own half: counter-press for 4 seconds, then drop into the mid-block.
12. If a chance to counter appears: release Mahrez (player_id ends with "_9") and Gouiri (player_id ends with "_10") quickly -- transitions are Algeria's best route to goal as underdogs.
13. If Mahrez (player_id ends with "_9") is doubled: switch play to Chaïbi (player_id ends with "_7") within 2-3 touches; do not force the right side.
14. If holding a lead late: stay compact, keep the ball, and see out the knockout -- do not over-commit.
15. If trailing late: push Ait-Nouri (player_id ends with "_1", LB) high, push Maza (player_id ends with "_8") up alongside Gouiri (player_id ends with "_10") as a second striker, throw extra numbers forward -- there is no tomorrow.

## Key Player Notes
- **Mahrez (skill 17, dribbling 18, pass 17, shoot 16)** is the talisman and captain; at 35, manage his defensive workload and give him the ball as often as possible. With Amoura doubtful, he becomes even more central to the attack and is the No. 1 penalty taker.
- **Gouiri (#9, shoot 16, penalty 16)** leads the line alone and scored the group-stage winner against Jordan -- the man Algeria look to in the decisive moment and second penalty taker.
- **Chaïbi (#8, skill 16, dribbling 16, pass 16)** deputizes on the left for the injured Amoura -- a creative left-footer who drifts inside and links play; more of a playmaker than a pure pace outlet.
- **Maza (#22, skill 16, dribbling 16)** is the breakout no. 10 -- encourage him to drive between the lines and feed Gouiri; a confident third penalty taker.
- **Amoura (speed 17, shoot 17, penalty 17)** is the lead scorer and pace outlet but is a serious injury doubt (hamstring); if passed fit he restores as first-choice penalty taker and left-sided runner.
- **Bentaleb & Boudaoui** form the double pivot that gives Algeria the extra midfield body for a compact knockout shape; Boudaoui's engine covers Ait-Nouri's raids.
- **Ait-Nouri (speed 17, dribbling 16)** is a top-tier attacking full-back -- his overlaps power the left side and must supply the width Amoura's absence removes, so cover from the pivots is essential.
- **Zidane (#23)** is restored between the posts for the knockout after Benbot struggled against Austria.

## Tournament Mindset
This is win-or-go-home. Algeria reached the Round of 16 out of a brutal group with reigning champions Argentina, Austria and Jordan -- their first knockout appearance since 2014 -- and now meet Switzerland at BC Place, Vancouver, with a quarter-final place at stake. As the underdog, Algeria will not try to out-muscle an organized, physical Swiss side; they will be compact in a 4-2-3-1, control possession in spells, and strike on the counter through Mahrez, Maza, Chaïbi and Gouiri, backing their technical edge and transition speed to conjure the decisive moment. If the tie is level after 90 minutes it goes to extra time and, if still level, a penalty shootout -- so discipline, game management and a settled penalty order matter enormously. Keep eleven on the pitch, stay patient, take the half-chances the group stage showed they can (Gouiri's late Jordan winner), and be ready for the ice-cold clarity of a shootout: Mahrez, Gouiri, Maza, Ait-Nouri and Bentaleb are the designated takers.
