# DR Congo — Tactical Profile

## Identity & Philosophy
Sébastien Desabre's DR Congo is athletic, transitional, and built around defensive solidity plus individual brilliance in the front two. The Leopards do not chase possession against better sides — they sit in a compact block, win the ball back, and break with venom. A back three anchored by captain Chancel Mbemba is shielded by hard-running wing-backs Aaron Wan-Bissaka and Arthur Masuaku, with a three-man central engine (Mukau, Moutoussamy, Sadiki) feeding the pace-and-finishing partnership of Yoane Wissa and veteran Cédric Bakambu. Discipline out of possession, ruthlessness in transition.

**Matchday 1 update (17 June, vs Portugal — 1-1 draw):** A creditable point against Roberto Martínez's side. Desabre shifted to a back-three / wing-back shape (3-4-1-2), bringing **Steve Kapuadi (#3)** into the central defence and pushing **Wan-Bissaka** and **Masuaku** to wing-back. **Théo Bongonda dropped out** of the XI; the front line became the **Wissa–Bakambu** two with a midfield three behind them. No DR Congo injuries, suspensions, or red cards were reported from the match. For Matchday 2 vs Colombia (23 June, Estadio Akron, Guadalajara), the same XI is expected to stand — "no need to make changes" — with Noah Sadiki holding the third midfield slot ahead of Edo Kayembe. The chief tactical watch point is containing Luis Díaz down DR Congo's right flank.

## Formation
- Shape: 3-4-1-2 (reads as 3-5-2 out of possession) — a back three, two athletic wing-backs, a midfield three, and a front two.
- Role mapping (roster order in `dr_congo.yaml`):
  - index 0: GK — Lionel Mpasi (#1; goes long under pressure)
  - index 1: LCB — Axel Tuanzebe (#4; physical left-of-three center-back)
  - index 2: CCB — Chancel Mbemba (#22; captain, defensive leader, ball-carrier — central of the back three)
  - index 3: RCB — Steve Kapuadi (#3; tall, physical right-of-three stopper)
  - index 4: LWB — Arthur Masuaku (#26; attacking left wing-back, technical, set-piece deliverer)
  - index 5: LCM — Ngal'ayel Mukau (#6; box-to-box engine, stamina 16, line-breaking passer)
  - index 6: DM — Samuel Moutoussamy (#8; central anchor, screens the back three)
  - index 7: RCM — Noah Sadiki (#14; balanced ball-winner, vertical passer)
  - index 8: RWB — Aaron Wan-Bissaka (#2; world-class 1v1 defender, athletic right wing-back, speed 16)
  - index 9: CF — Yoane Wissa (#20; pace-and-finishing threat, speed 16 / shoot 16; drops to combine then bursts in behind)
  - index 10: CF — Cédric Bakambu (#17; veteran reference striker, shoot 15; attacks the box)

## Style of Play

### Build-up
- Direct under pressure — Mpasi (idx 0) often goes long to the front two.
- Short build-up when uncontested: Mbemba (idx 2) steps out of the back three with the ball.
- Moutoussamy (idx 6) drops to make a back-four/diamond base; Mukau and Sadiki split to receive.
- Wing-backs Masuaku (idx 4) and Wan-Bissaka (idx 8) provide the width and the first outlet on transition.

### Pressing
- Mid-block press; selective high-press.
- Trigger: opposition CB receives back-to-goal or with a weak first touch.
- Bakambu (idx 10) and Wissa (idx 9) front the press; Mukau (idx 5) and Sadiki (idx 7) jump the pivots.
- Moutoussamy (idx 6) holds the central screen aggressively in front of the back three.

### Defensive shape
- 3-4-1-2 collapses into a back five — wing-backs Masuaku (idx 4) and Wan-Bissaka (idx 8) tuck in alongside the three CBs.
- Wan-Bissaka shuts down opposing wide threats 1v1 — exceptional recovery defender; matched against Luis Díaz vs Colombia.
- Mbemba (idx 2) marshals the line; Tuanzebe (idx 1) and Kapuadi (idx 3) win the first ball.
- Moutoussamy (idx 6) shields; Mukau (idx 5) and Sadiki (idx 7) screen the half-spaces.

### Wide play
- Left: Masuaku (idx 4) bombs forward as an attacking wing-back; Mukau (idx 5) combines through the left half-space; Wissa (idx 9) drifts wide to attack the channel.
- Right: Wan-Bissaka (idx 8) is more conservative going forward but supports Sadiki (idx 7); attacks down the right come through quick combinations rather than overlaps.
- Crosses target Bakambu (idx 10) near-post and Wissa (idx 9) arriving late.

### Final third
- Bakambu (idx 10) attacks the box; Wissa (idx 9) drops to combine then bursts in behind.
- Mukau (idx 5) arrives late from midfield to support the front two.
- Counter-attacks are typically 4-second sequences: turnover -> wing-back or Mukau -> Wissa -> Bakambu.

## Set Pieces
- Mbemba (idx 2), Tuanzebe (idx 1) and Kapuadi (idx 3) are aerial targets.
- Masuaku (idx 4) and Bakambu (idx 10) share set-piece delivery duties.
- Penalties: Wissa (idx 9, penalty 16) is first taker; Bakambu (idx 10, penalty 15) is the alternate.
- Defensive set pieces: mixed marking, Mbemba on the biggest aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mpasi) under pressure: long ball toward the front two (player_id ends with "_9" Wissa or "_10" Bakambu) — do not attempt a risky short pass.
2. If player_id ends with "_2" (Mbemba, CCB #22; skill 15, strength 16) and unpressed: step out of the back three and drive forward with the ball.
3. If player_id ends with "_8" (Wan-Bissaka, RWB #2; speed 16) and an opposition wide threat is 1v1 against him: tuck in, stay tight, tackle when committed — he is the team's elite 1v1 defender (key vs Luis Díaz).
4. If player_id ends with "_6" (Moutoussamy, DM): screen the back three; simple lateral passes; vertical pass to a forward (player_id ends with "_9" Wissa) when he drops between lines.
5. If player_id ends with "_9" (Wissa, CF #20; speed 16, shoot 16): receive between lines, combine with the other striker (player_id ends with "_10", Bakambu) or burst in behind, shoot from the half-space.
6. If player_id ends with "_5" (Mukau, LCM #6; stamina 16, pass 14): drive box-to-box through the left half-space, break lines with a vertical pass to Wissa (player_id ends with "_9"), arrive late in the box.
7. If player_id ends with "_10" (Bakambu, CF #17; skill 14, shoot 15): constantly check the offside line; attack the box on crosses and cut-backs.
8. If player_id ends with "_4" (Masuaku, LWB #26): bomb forward down the left, combine with Mukau, deliver crosses to the near post for Bakambu.
9. If player_id ends with "_7" (Sadiki, RCM #14): win the ball, then play vertical — feed the front two or release Wan-Bissaka (player_id ends with "_8") down the right.
10. If turnover in own half: outlet long to Wissa (player_id ends with "_9") or a wing-back (player_id ends with "_4" Masuaku / "_8" Wan-Bissaka) within 2 passes.
11. If defending: drop into a back five — wing-backs (player_id ends with "_4" and "_8") tuck alongside the three center-backs (player_id ends with "_1", "_2", "_3"); Wan-Bissaka 1v1 anchors the right.
12. If trailing late: push both wing-backs (player_id ends with "_4" and "_8") high, keep the back three (player_id ends with "_1", "_2", "_3") central, throw Wissa (player_id ends with "_9") and Bakambu (player_id ends with "_10") onto the last line.
13. If leading 1-0: drop the block 10m deeper, defend the box collectively as a back five, exploit Wan-Bissaka's (player_id ends with "_8") recovery defending.

## Key Player Notes
- **Mbemba (idx 2)** is the captain and defensive leader — composure on the ball is unusual for a CB of his physicality; the heart of the back three.
- **Wan-Bissaka (idx 8, speed 16)** is the elite 1v1 defender now operating as a wing-back — match him against the opposition's primary winger (Luis Díaz vs Colombia).
- **Kapuadi (idx 3, strength 16)** came into the XI for the back three vs Portugal — a tall, physical stopper who wins the first ball.
- **Wissa (idx 9, speed 16 / shoot 16)** is the Leopards' dangerman — a Premier League finisher with pace playing off Bakambu; send him in behind or let him shoot from the half-space. First-choice penalty taker.
- **Bakambu (idx 10, shoot 15)** is the experienced reference striker; his movement in the box converts the counters.
- **Mukau (idx 5, stamina 16 / pass 14)** is the box-to-box engine; he covers ground, breaks lines with vertical passes, and arrives late in the box.
- **Masuaku (idx 4)** is the attacking left wing-back and a key set-piece deliverer; his forward runs are DR Congo's main left-side width.

## Tournament Mindset
DR Congo are the clear underdogs of Group K, drawn alongside Portugal, Colombia and Uzbekistan. After opening with a hard-earned 1-1 draw against Portugal on 17 June 2026, the Leopards have belief — they sit on a point and know that athleticism, defensive discipline and individual quality can frustrate better-organized teams. Against Colombia on 23 June they will again absorb pressure, trust Wan-Bissaka to neutralize Luis Díaz, and back Wissa and Bakambu to punish any lapse in transition. A point keeps their last-16 hopes alive; a win would be a statement.
