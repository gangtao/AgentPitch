# Egypt — Tactical Profile

## Identity & Philosophy
Hossam Hassan's Egypt is built around one indisputable truth: feed Mohamed Salah. Their 4-3-3 — shifting to a 4-2-3-1 when chasing a game — is patient in build-up, defensively organized, and explosive in transition: a side that will absorb pressure for 70 minutes if it means Salah and Omar Marmoush get four clean 1v1 chances. Veteran spine, structured mid-block, devastating on the counter. Returning to the World Cup for the first time since 2018, Egypt land in Group G with Belgium, Iran and New Zealand; the manager has said the side is "90%" settled with no late tactical revolution. The blueprint is simple and deliberate: tight games, deep stretches without the ball, quick release into Salah or Marmoush.

## Formation
- Shape: 4-3-3, defensively organized with Salah floating in from the right; becomes a 4-2-3-1 when chasing.
- Role mapping (roster order in `egypt.yaml`):
  - index 0: GK — Mohamed El Shenawy (first-choice shot-stopper at 37; conservative distribution, goes long when pressed)
  - index 1: LB — Ahmed Fatouh (conservative, rarely overlaps; tucks in to make a back three when Hany stays high)
  - index 2: LCB — Yasser Ibrahim (aerial commander, strength 16; wins the box)
  - index 3: RCB — Mohamed Abdelmonem (Nice; mobile, the line organizer who steps out)
  - index 4: RB — Mohamed Hany (holds width, stays deep as cover behind Salah)
  - index 5: DM/#6 — Marwan Attia (deep-lying playmaker, screens the back four, dictates tempo — the unsung glue of the side)
  - index 6: LCM/#8 — Hamdi Fathi (ball-winning shuttler, stamina 17; also a center-back option, so reads danger well)
  - index 7: RCM/#10 — Emam Ashour (advanced roaming #8/#10; drives forward to support Salah, arrives late at the back post)
  - index 8: LW — Mahmoud Trezeguet (Al Ahly; fast, direct left-side outlet, runs in behind)
  - index 9: CF — Omar Marmoush (Manchester City; pace + hold-up, the second weapon, runs in behind)
  - index 10: RW — Mohamed Salah (Liverpool; captain and talisman, drifts inside onto the left foot)

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
- Marmoush and Trezeguet do the bulk of the front-line work.

### Defensive shape
- 4-5-1 / 4-1-4-1 mid-block, compact and disciplined.
- Attia screens the back four; Fathi and Ashour cover the half-spaces.
- Trezeguet tracks back to a left-midfielder role when defending.
- Abdelmonem is the line organizer.

### Wide play
- Right side: Salah cuts in onto left foot, Ashour underlaps, Hany rarely overlaps (he stays as cover).
- Left side: Trezeguet has pace to run in behind on direct balls from Attia or Salah.
- Egypt cross less than most 4-3-3 sides — they prefer cutbacks and shots from the half-space.

### Final third
- Salah is the primary shooter and creator — every attack must include a check for "can Salah receive here?"
- Marmoush pins center-backs and runs in behind to free Salah's cut inside.
- Trezeguet's runs in behind stretch defenses vertically.
- Ashour arrives late at the back post.

## Set Pieces
- Yasser Ibrahim and Abdelmonem are aerial targets; Marmoush attacks the near post on his run.
- Salah takes most attacking set pieces (corners and free kicks within 25m); Trezeguet is the secondary corner taker and a left-foot dead-ball alternative.
- Penalties: Salah is the captain and primary taker, Marmoush the backup.
- Defensive corners: zonal with Yasser Ibrahim on the near-post; Attia screens the edge of the box.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", El Shenawy) and the press is moderate: short pass to the CBs (player_id ends with "_2" Yasser Ibrahim or "_3" Abdelmonem); only go long if pressed hard.
2. If player_id ends with "_5" (Attia, #6): lateral and backward passes are fine — primary job is to find the RW (player_id ends with "_10", Salah) between lines.
3. If holding the ball and the RW (player_id ends with "_10", Salah) is visible: pass to him unless it's a clearly suicidal pass.
4. If player_id ends with "_10" (Salah, RW #10) and 1v1 on the right with inside space: cut inside onto left foot, shoot from 18-22m.
5. If player_id ends with "_10" (Salah) and double-teamed: lay off to the advanced #8 (player_id ends with "_7", Ashour) or LW (player_id ends with "_8", Trezeguet), then continue the run to receive again.
6. If player_id ends with "_8" (Trezeguet, LW) and pass is on for him to run in behind: sprint immediately; do not check back to feet.
7. If defending in own half: maintain 4-5-1, Attia (player_id ends with "_5") screens, never break shape for a speculative tackle.
8. If a turnover happens in own half: outlet immediately to Salah (player_id ends with "_10") if visible — long diagonal if needed.
9. If player_id ends with "_1" (Fatouh, LB) has the ball: pass back inside; never carry past the halfway line.
10. If player_id ends with "_9" (Marmoush, CF): run in behind onto direct balls; otherwise hold up and lay off to Salah's (player_id ends with "_10") run.
11. If trailing in the final 20 minutes: push Salah (player_id ends with "_10") more central as a second striker, Ashour (player_id ends with "_7") becomes the right winger.
12. If leading by 1+: drop the block 8 meters deeper, defend the lead with numbers behind the ball.

## Key Player Notes
- **Salah (skill 18, dribbling 18, shoot 18)** is the captain and the entire team's identity — and the emotional infrastructure of the side. He turns 34 on the day of the opener against Belgium, so manage his minutes, but every tactical choice still routes around getting him the ball in a dangerous area.
- **Attia** is the tempo-setter — patient, screens the back four, never forces a forward pass.
- **Yasser Ibrahim (strength 16)** is the aerial anchor at the back; treat all crosses into the box as his to win.
- **Marmoush's pace (17) and shooting (16)** — now a Manchester City forward — is the second weapon; leading the line, he pins center-backs and runs in behind to give defenses two simultaneous threats with Salah.
- **Ashour** is the creative engine from the advanced #8 spot — late runs into the box and the link between midfield and Salah.
- **Trezeguet** offers a direct, pacey left-wing outlet who stretches defenses vertically.
- **El Shenawy** is a strong shot-stopper but distribution is conservative — accept that build-up will not start from his feet.

## Tournament Mindset
Egypt expects to be the underdog in raw possession but believes they have the world's best winger; one moment of Salah magic is worth 70 minutes of organized defending.
