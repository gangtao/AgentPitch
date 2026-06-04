# Egypt — Tactical Profile

## Identity & Philosophy
Hossam Hassan's Egypt is built around one indisputable truth: feed Mohamed Salah. Their 4-3-3 is patient in build-up, defensively organized, and explosive in transition — a side that will absorb pressure for 70 minutes if it means Salah gets four clean 1v1 chances. Veteran spine, structured mid-block, devastating on the counter.

## Formation
- Shape: 4-3-3, defensively organized with Salah floating in from the right.
- Role mapping (roster index -> tactical role):
  - 0 El Shenawy — Goalkeeper, shot-stopper, distributes long.
  - 1 Fatouh — Left-back, conservative, rarely overlaps.
  - 2 Abdelmonem — Left center-back, mobile.
  - 3 Rabia — Right center-back, aerial commander.
  - 4 Hany — Right-back, holds width, stays deep.
  - 5 Attia — #6, deep-lying playmaker, dictates tempo.
  - 6 Hamdi Fathi — #8, ball-winning shuttler.
  - 7 Ashour — Advanced #8 / roaming #10, drives forward to support Salah.
  - 8 Trezeguet — Left winger, fast direct outlet.
  - 9 Marmoush — Center-forward, pace + hold-up, runs in behind.
  - 10 Salah — Right winger drifting central, talisman.

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
- Rabia is the line organizer.

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
- Rabia and Abdelmonem are aerial targets.
- Salah takes most attacking set pieces (corners and free kicks within 25m); Trezeguet is the secondary corner taker.
- Penalties: Salah is the primary taker, Marmoush the backup.
- Defensive corners: zonal with Rabia on the near-post.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", El Shenawy) and the press is moderate: short pass to the CBs (player_id ends with "_3" Rabia or "_2" Abdelmonem); only go long if pressed hard.
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
- **Salah (skill 18, dribbling 18, shoot 18)** is the entire team's identity. Every tactical choice routes around getting him the ball in a dangerous area.
- **Attia** is the tempo-setter — patient, screens the back four, never forces a forward pass.
- **Rabia** is the aerial anchor at the back; treat all crosses into the box as his to win.
- **Marmoush's pace (17) and shooting (16)** is the second weapon; leading the line, he pins center-backs and runs in behind to give defenses two simultaneous threats with Salah.
- **Ashour** is the creative engine from the advanced #8 spot — late runs into the box and the link between midfield and Salah.
- **Trezeguet** offers a direct, pacey left-wing outlet who stretches defenses vertically.
- **El Shenawy** is a strong shot-stopper but distribution is conservative — accept that build-up will not start from his feet.

## Tournament Mindset
Egypt expects to be the underdog in raw possession but believes they have the world's best winger; one moment of Salah magic is worth 70 minutes of organized defending.
