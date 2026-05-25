# Egypt — Tactical Profile

## Identity & Philosophy
Hossam Hassan's Egypt is built around one indisputable truth: feed Mohamed Salah. Their 4-3-3 is patient in build-up, defensively organized, and explosive in transition — a side that will absorb pressure for 70 minutes if it means Salah gets four clean 1v1 chances. Veteran spine, structured mid-block, devastating on the counter.

## Formation
- Shape: 4-3-3, defensively organized with a single #10 (Salah floating in from the right).
- Role mapping (roster index -> tactical role):
  - 0 El Shenawy — Goalkeeper, shot-stopper, distributes long.
  - 1 Hany — Left-back, conservative, rarely overlaps.
  - 2 Abdelmonem — Left center-back, mobile.
  - 3 Omar Kamal — Right center-back cover / rotational.
  - 4 Hegazi — Veteran center-back, aerial commander.
  - 5 Elneny — #6, deep-lying playmaker, dictates tempo.
  - 6 Hamdi Fathi — #8, ball-winning shuttler.
  - 7 Ibrahim Adel — Attacking #8, drives forward to support Salah.
  - 8 Marmoush — Left winger, fast direct outlet.
  - 9 Mostafa Mohamed — Center-forward, hold-up + aerial.
  - 10 Salah — Right winger drifting central, talisman.

## Style of Play

### Build-up
- Patient, slow tempo. Elneny is always the first option from the back four.
- Goal kicks: short to the CBs unless Salah signals for a long diagonal switch.
- Full-backs hold width and stay deep — Egypt rarely commits more than 6 players in build-up.
- Salah inverts from right to receive between lines.

### Pressing
- Mid-block press at the halfway line, not a high press.
- Trigger: opposition full-back receives with limited options.
- Salah usually does NOT press hard — he hovers to receive the turnover and break.
- Marmoush and Mostafa Mohamed do the bulk of the front-line work.

### Defensive shape
- 4-5-1 / 4-1-4-1 mid-block, compact and disciplined.
- Elneny screens the back four; Fathi and Adel cover the half-spaces.
- Marmoush tracks back to a left-midfielder role when defending.
- Hegazi is the line organizer.

### Wide play
- Right side: Salah cuts in onto left foot, Adel underlaps, Hany rarely overlaps (he stays as cover).
- Left side: Marmoush has pace to run in behind on direct balls from Elneny or Salah.
- Egypt cross less than most 4-3-3 sides — they prefer cutbacks and shots from the half-space.

### Final third
- Salah is the primary shooter and creator — every attack must include a check for "can Salah receive here?"
- Mostafa Mohamed pins center-backs to free Salah's cut inside.
- Marmoush's runs in behind stretch defenses vertically.
- Adel arrives late at the back post.

## Set Pieces
- Hegazi and Abdelmonem are aerial targets.
- Salah takes most attacking set pieces (corners and free kicks within 25m).
- Defensive corners: zonal with Hegazi on the near-post.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", El Shenawy) and the press is moderate: short pass to the CBs (player_id ends with "_4" Hegazi or "_2" Abdelmonem); only go long if pressed hard.
2. If player_id ends with "_5" (Elneny, #6 #17): lateral and backward passes are fine — primary job is to find the RW (player_id ends with "_10", Salah) between lines.
3. If holding the ball and the RW (player_id ends with "_10", Salah) is visible: pass to him unless it's a clearly suicidal pass.
4. If player_id ends with "_10" (Salah, RW #10) and 1v1 on the right with inside space: cut inside onto left foot, shoot from 18-22m.
5. If player_id ends with "_10" (Salah) and double-teamed: lay off to the advanced #8 (player_id ends with "_7", Adel) or LW (player_id ends with "_8", Marmoush), then continue the run to receive again.
6. If player_id ends with "_8" (Marmoush, LW #11) and pass is on for him to run in behind: sprint immediately; do not check back to feet.
7. If defending in own half: maintain 4-5-1, Elneny (player_id ends with "_5") screens, never break shape for a speculative tackle.
8. If a turnover happens in own half: outlet immediately to Salah (player_id ends with "_10") if visible — long diagonal if needed.
9. If player_id ends with "_1" (Hany, LB #12) has the ball: pass back inside; never carry past the halfway line.
10. If player_id ends with "_9" (Mostafa Mohamed, CF #9): hold up the ball, lay off to Salah's (player_id ends with "_10") overlapping run.
11. If trailing in the final 20 minutes: push Salah (player_id ends with "_10") more central as a second striker, Adel (player_id ends with "_7") becomes the right winger.
12. If leading by 1+: drop the block 8 meters deeper, defend the lead with numbers behind the ball.

## Key Player Notes
- **Salah (skill 18, dribbling 18, shoot 18)** is the entire team's identity. Every tactical choice routes around getting him the ball in a dangerous area.
- **Elneny** is the tempo-setter — patient, never forces a forward pass.
- **Hegazi** is the aerial anchor at the back; treat all crosses into the box as his to win.
- **Marmoush's pace (17)** is the second weapon; pair him with Salah to give defenses two simultaneous threats.
- **El Shenawy** is a strong shot-stopper but distribution is conservative — accept that build-up will not start from his feet.

## Tournament Mindset
Egypt expects to be the underdog in raw possession but believes they have the world's best winger; one moment of Salah magic is worth 70 minutes of organized defending.
