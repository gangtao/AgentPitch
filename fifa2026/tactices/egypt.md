# Egypt — Tactical Profile

## Identity & Philosophy
Hossam Hassan's Egypt is built around one indisputable truth: feed Mohamed Salah. The whole campaign has been set up in a 4-2-3-1 — a double pivot screening the back four, three behind a lone striker — patient in build-up, defensively organized, and explosive in transition: a side that will absorb pressure for 70 minutes if it means Salah and Omar Marmoush get four clean 1v1 chances. Veteran spine, structured mid-block, devastating on the counter. That blueprint carried Egypt out of Group G as winners (a 1-1 draw with Belgium, a 3-1 win over New Zealand — their first-ever World Cup victory — and a controlled result against Iran) and then through a nervy Round of 32 against Australia in Texas, won on a **penalty shootout**. Now comes the biggest test: **Round of 16 vs Argentina, Tue July 7, Atlanta.** Egypt are the clear underdog against the reigning champions of Messi, Lautaro and Enzo Fernandez. Captain Mohamed Salah — who carried a hamstring niggle from the group finale but recovered to start against Australia and is fit again — remains the entire plan: soak up Argentine possession, stay compact, and win the tie in the transition moments when Salah or Marmoush get isolated. Injury/availability watch: first-choice LB Ahmed Fatouh (hamstring tear) and CB Mohamed Abdelmonem are out; Karim Hafez carried a knock into the week but is expected to start at left-back. Mohanad Lasheen is back from his R32 suspension but Hamdy Fathy retains the left of the pivot. The plan is unchanged: tight game, deep stretches without the ball, quick release into Salah or Marmoush.

## Formation
- Shape: 4-2-3-1. Double pivot (Attia + Fathy) shields the back four; Ashour is the central #10 behind lone striker Marmoush, with Salah from the right and Zico from the left. **R16 update:** first-choice LB Ahmed Fatouh (hamstring tear) and CB Mohamed Abdelmonem remain out injured, so Karim Hafez continues at left-back with Ramy Rabia partnering Yasser Ibrahim at centre-back. Mohanad Lasheen has served his R32 ban but Hamdy Fathy keeps the left of the pivot alongside Attia. Against Argentina the block sits deeper still — expect long spells of 4-5-1/4-1-4-1 defending with Ashour dropping onto Enzo Fernandez.
- Role mapping (roster order in `egypt.yaml`):
  - index 0: GK — Mostafa Shobeir (Al Ahly; preferred to El Shenawy for the opener; conservative distribution, goes long when pressed)
  - index 1: LB — Karim Hafez (in for the injured Fatouh; conservative, rarely overlaps; tucks in to make a back three when Hany stays high)
  - index 2: LCB — Ramy Rabia (experienced Al Ahly centre-back drawn into the XI; aerially strong, steps out to screen)
  - index 3: RCB — Yasser Ibrahim (aerial commander, strength 16; wins the box, the line organizer who steps out)
  - index 4: RB — Mohamed Hany (holds width, stays deep as cover behind Salah)
  - index 5: DM/#6 — Marwan Attia (deep-lying playmaker, the right side of the pivot; screens the back four, dictates tempo)
  - index 6: DM/#6 — Hamdy Fathy (a defensive midfielder by trade; kept the left of the pivot even with Lasheen back from suspension; ball-winner, stamina 17)
  - index 7: CAM/#10 — Emam Ashour (the central creative engine; drives forward to support Salah, arrives late at the back post — scored vs Belgium)
  - index 8: LAM/LW — Mostafa Zico (Pyramids; right-footed wide forward from the left, cuts in and shoots, secondary set-piece taker)
  - index 9: CF — Omar Marmoush (Manchester City; pace + hold-up, leads the line, runs in behind)
  - index 10: RAM/RW — Mohamed Salah (Liverpool; captain and talisman, drifts inside onto the left foot from the right)

## Style of Play

### Build-up
- Patient, slow tempo. Attia is always the first option from the back four.
- Goal kicks: short to the CBs unless Salah signals for a long diagonal switch.
- Full-backs hold width and stay deep — Egypt rarely commits more than 6 players in build-up.
- Salah inverts from right to receive between lines.

### Pressing
- Mid-block press at the halfway line, not a high press.
- Trigger: opposition full-back receives with limited options.
- Salah usually does NOT press hard — he hovers to receive the turnover and break.
- Marmoush and Zico do the bulk of the front-line work.

### Defensive shape
- 4-2-3-1 dropping to a deep 4-5-1/4-1-4-1 mid-block vs Argentina, compact and disciplined.
- Attia and Fathy sit as a double pivot screening the back four; Ashour drops onto the central pocket to deny the Argentine #8s space between the lines.
- Zico tracks back to a left-midfielder role when defending; Salah screens the passing lane to Argentina's left-back rather than pressing hard.
- Yasser Ibrahim is the line organizer; Rabia reads danger from LCB — both must stay tight to Lautaro and manage runs in behind.

### Wide play
- Right side: Salah cuts in onto left foot, Ashour underlaps, Hany rarely overlaps (he stays as cover).
- Left side: Zico (right-footed) drifts in off the left to shoot; runs in behind on direct balls from the pivot or Salah.
- Egypt cross less than most sides — they prefer cutbacks and shots from the half-space.

### Final third
- Salah is the primary shooter and creator — every attack must include a check for "can Salah receive here?"
- Marmoush pins center-backs and runs in behind to free Salah's cut inside.
- Zico's runs from the left stretch defenses and give a second shooting threat off the right foot.
- Ashour arrives late at the back post.

## Set Pieces
- Yasser Ibrahim and Fathy are aerial targets; Marmoush attacks the near post on his run.
- Salah takes most attacking set pieces (corners and free kicks within 25m); Zico is the secondary corner taker and a dead-ball alternative.
- Penalties: Salah is the captain and primary taker, Marmoush the backup. (Egypt won the R32 shootout vs Australia — Salah and Marmoush both converted.)
- Defensive corners: zonal with Yasser Ibrahim and Rabia on the near-post; Attia and Fathy screen the edge of the box — critical against Argentina's aerial threat from Romero and Otamendi.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Shobeir) and the press is moderate: short pass to the CBs (player_id ends with "_2" Rabia or "_3" Yasser Ibrahim); only go long if pressed hard. Against Argentina's front press, prefer the safe long clearance over a risky short build-up.
2. If player_id ends with "_5" (Attia, #6): lateral and backward passes are fine — primary job is to find the RW (player_id ends with "_10", Salah) between lines.
3. If holding the ball and the RW (player_id ends with "_10", Salah) is visible: pass to him unless it's a clearly suicidal pass.
4. If player_id ends with "_10" (Salah, RW #10) and 1v1 on the right with inside space: cut inside onto left foot, shoot from 18-22m.
5. If player_id ends with "_10" (Salah) and double-teamed: lay off to the #10 (player_id ends with "_7", Ashour) or LW (player_id ends with "_8", Zico), then continue the run to receive again.
6. If player_id ends with "_8" (Zico, LW) and pass is on for him to run in behind: sprint immediately; do not check back to feet.
7. If defending in own half: maintain the deep 4-2-3-1 / 4-5-1 mid-block, Attia (player_id ends with "_5") and Fathy (player_id ends with "_6") screen, never break shape for a speculative tackle.
8. If a turnover happens in own half: outlet immediately to Salah (player_id ends with "_10") if visible — long diagonal if needed; this is Egypt's main route to goal vs Argentina.
9. If player_id ends with "_1" (Hafez, LB) has the ball: pass back inside; never carry past the halfway line.
10. If player_id ends with "_9" (Marmoush, CF): run in behind onto direct balls; otherwise hold up and lay off to Salah's (player_id ends with "_10") run.
11. If trailing in the final 20 minutes: push Salah (player_id ends with "_10") more central as a second striker, Ashour (player_id ends with "_7") becomes the right winger.
12. If leading by 1+: drop the block 8 meters deeper, defend the lead with numbers behind the ball.

## Key Player Notes
- **Salah (skill 18, dribbling 18, shoot 18)** is the captain and the entire team's identity — and the emotional infrastructure of the side. He assisted Egypt's goal against Belgium; every tactical choice still routes around getting him the ball in a dangerous area on the right.
- **Attia & Fathy** are the double pivot — patient, screen the back four, win the ball and recycle simply; neither forces a forward pass. Fathy's stamina (17) and ball-winning are vital for the volume of defending Egypt will do against Argentina.
- **Yasser Ibrahim (strength 16)** is the aerial anchor and line organizer at the back; treat all crosses into the box as his to win.
- **Marmoush's pace (17) and shooting (16)** — now a Manchester City forward — is the second weapon; leading the line, he pins center-backs and runs in behind to give defenses two simultaneous threats with Salah.
- **Ashour** is the creative engine from the central #10 spot — scored the opener against Belgium, makes late runs into the box and links midfield to Salah.
- **Zico** offers a right-footed wide outlet from the left who cuts in to shoot and stretches defenses vertically.
- **Shobeir** got the nod over El Shenawy for the opener — a strong shot-stopper, but distribution is conservative; accept that build-up will not start from his feet.

## Tournament Mindset
Egypt is the heavy underdog against the reigning champions, and they embrace it: one moment of Salah magic is worth 70 minutes of organized defending. Argentina will dominate the ball, so the plan is to defend deep and narrow, keep the back four and double pivot intact, force Messi and the #8s into wide, low-value areas, and refuse to be pulled out of shape. Egypt's route to goal is the counter: win the ball, spring Salah or Marmoush into space before Argentina's rest-defence resets. Nothing speculative at the back — no diving tackles, no high line to be run in behind. Having already beaten Australia on penalties, Egypt are comfortable taking this to extra time and a shootout, where Salah and Marmoush give them a real edge. Stay in the tie, stay compact, take the one clean chance that comes.
