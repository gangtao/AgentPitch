# Egypt — Tactical Profile

## Identity & Philosophy
Hossam Hassan's Egypt is built around one indisputable truth: feed Mohamed Salah. The opener against Belgium (a 1-1 draw, Ashour scoring and Salah assisting) was set up in a 4-2-3-1 — a double pivot screening the back four, three behind a lone striker — patient in build-up, defensively organized, and explosive in transition: a side that will absorb pressure for 70 minutes if it means Salah and Omar Marmoush get four clean 1v1 chances. Veteran spine, structured mid-block, devastating on the counter. Returning to the World Cup for the first time since 2018, Egypt sit in Group G with Belgium, Iran and New Zealand. The blueprint is simple and deliberate: tight games, deep stretches without the ball, quick release into Salah or Marmoush. Expect Hassan to keep the same XI for the New Zealand game on June 21.

## Formation
- Shape: 4-2-3-1. Double pivot (Attia + Lasheen) shields the back four; Ashour is the central #10 behind lone striker Marmoush, with Salah from the right and Zico from the left.
- Role mapping (roster order in `egypt.yaml`):
  - index 0: GK — Mostafa Shobeir (Al Ahly; preferred to El Shenawy for the opener; conservative distribution, goes long when pressed)
  - index 1: LB — Ahmed Fatouh (conservative, rarely overlaps; tucks in to make a back three when Hany stays high)
  - index 2: LCB — Hamdy Fathy (a defensive midfielder by trade dropped to center-back; ball-winner, stamina 17, reads danger well)
  - index 3: RCB — Yasser Ibrahim (aerial commander, strength 16; wins the box, the line organizer who steps out)
  - index 4: RB — Mohamed Hany (holds width, stays deep as cover behind Salah)
  - index 5: DM/#6 — Marwan Attia (deep-lying playmaker, the right side of the pivot; screens the back four, dictates tempo)
  - index 6: DM/#6 — Mohanad Lasheen (Pyramids; ball-winning midfielder, the left side of the pivot; tackles and interceptions, recycles simply)
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
- 4-4-2 / 4-2-3-1 mid-block, compact and disciplined.
- Attia and Lasheen sit as a double pivot screening the back four; Ashour drops onto the central pocket.
- Zico tracks back to a left-midfielder role when defending.
- Yasser Ibrahim is the line organizer; Fathy reads danger from LCB.

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
- Penalties: Salah is the captain and primary taker, Marmoush the backup.
- Defensive corners: zonal with Yasser Ibrahim on the near-post; Attia and Lasheen screen the edge of the box.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Shobeir) and the press is moderate: short pass to the CBs (player_id ends with "_2" Fathy or "_3" Yasser Ibrahim); only go long if pressed hard.
2. If player_id ends with "_5" (Attia, #6): lateral and backward passes are fine — primary job is to find the RW (player_id ends with "_10", Salah) between lines.
3. If holding the ball and the RW (player_id ends with "_10", Salah) is visible: pass to him unless it's a clearly suicidal pass.
4. If player_id ends with "_10" (Salah, RW #10) and 1v1 on the right with inside space: cut inside onto left foot, shoot from 18-22m.
5. If player_id ends with "_10" (Salah) and double-teamed: lay off to the #10 (player_id ends with "_7", Ashour) or LW (player_id ends with "_8", Zico), then continue the run to receive again.
6. If player_id ends with "_8" (Zico, LW) and pass is on for him to run in behind: sprint immediately; do not check back to feet.
7. If defending in own half: maintain the 4-2-3-1 mid-block, Attia (player_id ends with "_5") and Lasheen (player_id ends with "_6") screen, never break shape for a speculative tackle.
8. If a turnover happens in own half: outlet immediately to Salah (player_id ends with "_10") if visible — long diagonal if needed.
9. If player_id ends with "_1" (Fatouh, LB) has the ball: pass back inside; never carry past the halfway line.
10. If player_id ends with "_9" (Marmoush, CF): run in behind onto direct balls; otherwise hold up and lay off to Salah's (player_id ends with "_10") run.
11. If trailing in the final 20 minutes: push Salah (player_id ends with "_10") more central as a second striker, Ashour (player_id ends with "_7") becomes the right winger.
12. If leading by 1+: drop the block 8 meters deeper, defend the lead with numbers behind the ball.

## Key Player Notes
- **Salah (skill 18, dribbling 18, shoot 18)** is the captain and the entire team's identity — and the emotional infrastructure of the side. He assisted Egypt's goal against Belgium; every tactical choice still routes around getting him the ball in a dangerous area on the right.
- **Attia & Lasheen** are the double pivot — patient, screen the back four, win the ball and recycle simply; neither forces a forward pass.
- **Yasser Ibrahim (strength 16)** is the aerial anchor and line organizer at the back; treat all crosses into the box as his to win.
- **Marmoush's pace (17) and shooting (16)** — now a Manchester City forward — is the second weapon; leading the line, he pins center-backs and runs in behind to give defenses two simultaneous threats with Salah.
- **Ashour** is the creative engine from the central #10 spot — scored the opener against Belgium, makes late runs into the box and links midfield to Salah.
- **Zico** offers a right-footed wide outlet from the left who cuts in to shoot and stretches defenses vertically.
- **Shobeir** got the nod over El Shenawy for the opener — a strong shot-stopper, but distribution is conservative; accept that build-up will not start from his feet.

## Tournament Mindset
Egypt expects to be the underdog in raw possession but believes they have the world's best winger; one moment of Salah magic is worth 70 minutes of organized defending.
