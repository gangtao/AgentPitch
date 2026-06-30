# DR Congo — Tactical Profile

## Identity & Philosophy
Sébastien Desabre's DR Congo is athletic, transitional, and built around defensive solidity plus individual brilliance in attack. The Leopards do not chase possession against better sides — they sit in a compact block, win the ball back, and break with venom. Having reached the World Cup knockouts for the first time in their history (and for the first time in 52 years of trying), Desabre shelves the attacking group-stage gamble and returns to the **5-3-2 / 3-5-2** that frustrated Portugal and Colombia: a back three shielded by two hard-running wing-backs, a disciplined midfield trio anchored by the young Sunderland engine Noah Sadiki, and two strikers — captain-class veteran Cédric Bakambu paired with the Leopards' tournament dangerman Yoane Wissa — to spring the counter. Discipline out of possession, ruthlessness in transition.

**Matchday 1 (17 June, vs Portugal — 1-1 draw):** A creditable point against Roberto Martínez's side; **Wissa scored** DR Congo's first goal of the tournament. Desabre set up in a compact block and frustrated Portugal.

**Matchday 2 (23 June, vs Colombia — 0-1 loss):** A narrow, disciplined defeat. DR Congo absorbed pressure for long spells before **Daniel Muñoz struck in the 76th minute** to settle it; Colombia sealed qualification, DR Congo were left on a single point.

**Matchday 3 (27 June, vs Uzbekistan — 3-1 win, Atlanta):** A must-win decider, and the Leopards delivered. Eldor Shomurodov put Uzbekistan ahead inside ten minutes, but DR Congo completed a sensational comeback: **Wissa's 68th-minute penalty**, **Fiston Mayele** in the 78th, and **Wissa again in the 90+1** sealed a 3-1 win — their first-ever World Cup victory — and clinched **third in Group K** and a Round-of-32 ticket as one of the best third-placed sides.

## Round of 32 Lineup (vs England, July 1 — Mercedes-Benz Stadium, Atlanta, win-or-go-home)
DR Congo go into their first World Cup knockout game with a clean bill of health and a clear plan: out-organise the favourites. Desabre is expected to revert from the Uzbekistan 4-4-2 to a defensive **5-3-2**, packing the box and springing Wissa and Bakambu on the break.
- **Steve Kapuadi (#5)** comes in to make a back three alongside Tuanzebe and captain Mbemba — five at the back to contain England's attack.
- **Wing-backs**: Aaron Wan-Bissaka (right) and Arthur Masuaku (left) provide the width and the first outlet on the counter; Wan-Bissaka's elite 1v1 defending is aimed squarely at England's wide threat.
- **Midfield three**: Noah Sadiki anchors as the destroyer, with Kayembe and Moutoussamy shuttling and screening either side.
- **Strikers**: Wissa (2 goals at the tournament — more than his entire 2025-26 Premier League season) leads the line with Bakambu, the 35-year-old reference man preferred over Fiston Mayele for his hold-up play and experience.
- **Mbemba** earns a record-extending 113th senior cap and marshals the back line; **Mpasi** was excellent in the group stage.
- England context: clear favourites, but missing Reece James (injury) at right-back and sweating on Jarell Quansah; Djed Spence likely starts wide. DR Congo will sit deep, frustrate, and hit the transition.

## Formation
- Shape: 5-3-2 — a back three, two wing-backs, a midfield three (single anchor in front of two shuttlers), and a front two.
- Role mapping (roster order in `dr_congo.yaml`):
  - index 0: GK — Lionel Mpasi (#1; goes long under pressure)
  - index 1: LWB — Arthur Masuaku (#26; attacking left wing-back, technical, set-piece deliverer, stamina 16)
  - index 2: LCB — Axel Tuanzebe (#4; physical left-sided center-back, wins the first ball)
  - index 3: CB — Chancel Mbemba (#22; captain, defensive leader, ball-carrier, central of the back three)
  - index 4: RCB — Steve Kapuadi (#5; physical right-sided center-back added for the knockout)
  - index 5: RWB — Aaron Wan-Bissaka (#2; world-class 1v1 defender, athletic right wing-back, speed 17)
  - index 6: LCM — Edo Kayembe (#25; box-to-box engine, stamina 16, left shuttler)
  - index 7: DM — Noah Sadiki (#6; combative young anchor, screens the back three, stamina 17)
  - index 8: RCM — Samuel Moutoussamy (#8; balanced ball-winner, vertical passer, right shuttler)
  - index 9: ST — Cédric Bakambu (#17; veteran reference striker, shoot 15; holds it up, attacks the box)
  - index 10: ST — Yoane Wissa (#20; pace-and-finishing threat, speed 16 / shoot 16; leads the line, bursts in behind)

## Style of Play

### Build-up
- Direct under pressure — Mpasi (idx 0) often goes long to the front two.
- Short build-up when uncontested: Mbemba (idx 3) steps out of the back three with the ball.
- Sadiki (idx 7) drops in front of the back three to offer the first pass; Kayembe and Moutoussamy split to receive.
- Wing-backs Masuaku (idx 1) and Wan-Bissaka (idx 5) provide the width and the first outlet on transition.

### Pressing
- Low-to-mid block; the Leopards rarely press high against England — they invite pressure and hit the break.
- Trigger: opposition CB receives back-to-goal or with a weak first touch near the touchline.
- Wissa (idx 10) and Bakambu (idx 9) screen the central lanes and angle the build-up wide.
- Sadiki (idx 7) holds the central screen aggressively in front of the back three.

### Defensive shape
- 5-3-2 collapses into a compact 5-3-2 / 5-4-1 — wing-backs Masuaku (idx 1) and Wan-Bissaka (idx 5) drop into a back five.
- Wan-Bissaka (idx 5) shuts down England's wide threat 1v1 — exceptional recovery defender.
- Mbemba (idx 3) marshals the line; Tuanzebe (idx 2) and Kapuadi (idx 4) win the first ball either side.
- Sadiki (idx 7) shields; Kayembe (idx 6) and Moutoussamy (idx 8) screen the half-spaces and track runners.

### Wide play
- Left: Masuaku (idx 1) overlaps as an attacking wing-back and delivers crosses; drops to a back five when defending.
- Right: Wan-Bissaka (idx 5) is defence-first but breaks forward on the counter; supports Wissa's channel runs.
- Crosses target Bakambu (idx 9) in the box and Wissa (idx 10) attacking the back post and the channel.

### Final third
- Wissa (idx 10) leads the line, dropping to combine then bursting in behind.
- Bakambu (idx 9) holds the ball up, brings runners into play, and finishes inside the box.
- Kayembe (idx 6) arrives late from midfield to support the front two.
- Counter-attacks are typically 4-second sequences: turnover -> wing-back or shuttler -> Wissa -> shot.

## Set Pieces
- Mbemba (idx 3), Kapuadi (idx 4), Tuanzebe (idx 2) and Bakambu (idx 9) are aerial targets.
- Masuaku (idx 1) is the primary set-piece deliverer; Moutoussamy (idx 8) shares duties.
- Penalties: Wissa (idx 10, penalty 16) is first taker — converted the decisive spot-kick vs Uzbekistan; Bakambu (idx 9, penalty 14) is the alternate.
- Defensive set pieces: mixed marking, Mbemba on the biggest aerial threat (England are dangerous from corners and long throws).

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mpasi) under pressure: long ball toward the front two (player_id ends with "_10" Wissa or "_9" Bakambu) — do not attempt a risky short pass.
2. If player_id ends with "_3" (Mbemba, central CB #22; skill 15, strength 16) and unpressed: step out of the back three and drive forward with the ball; otherwise marshal the line.
3. If player_id ends with "_5" (Wan-Bissaka, RWB #2; speed 17) and an opposition wide threat is 1v1 against him: stay tight, drop into the back five, tackle when committed — he is the team's elite 1v1 defender.
4. If player_id ends with "_7" (Sadiki, DM #6; stamina 17): screen the back three; simple lateral passes; vertical pass to a forward (player_id ends with "_10" Wissa) when he drops between lines.
5. If player_id ends with "_10" (Wissa, ST #20; speed 16, shoot 16): lead the line, drop to combine or burst in behind, shoot from the half-space and the box.
6. If player_id ends with "_6" (Kayembe, LCM #25; stamina 16, pass 14): drive box-to-box through the left half-space, break lines with a vertical pass to Wissa (player_id ends with "_10"), arrive late in the box.
7. If player_id ends with "_1" (Masuaku, LWB #26; stamina 16): overlap down the left on the counter, deliver crosses for Bakambu (player_id ends with "_9") and Wissa, take set-piece deliveries; drop into the back five when defending.
8. If player_id ends with "_8" (Moutoussamy, RCM #8): win the ball, then play vertical — feed the front two or release Wan-Bissaka (player_id ends with "_5") down the right.
9. If player_id ends with "_9" (Bakambu, ST #17; shoot 15): hold the ball up, bring runners in, attack the box on crosses and cut-backs, finish the counters; check the offside line.
10. If player_id ends with "_2" or "_4" (Tuanzebe / Kapuadi, wide CBs): stay compact in the back three, win the first ball, clear long balls and set-piece deliveries; do not step out unless the ball is clearly safe.
11. If turnover in own half: outlet long to Wissa (player_id ends with "_10") or Bakambu (player_id ends with "_9") within 2 passes, or release a wing-back (player_id ends with "_1" Masuaku / "_5" Wan-Bissaka).
12. If defending: drop into a compact back five — wing-backs (player_id ends with "_1" and "_5") tuck into the line; the midfield three (player_id ends with "_6", "_7", "_8") screen in front; Wan-Bissaka 1v1 anchors the right.
13. If trailing late: push both wing-backs (player_id ends with "_1" and "_5") high, commit both strikers (player_id ends with "_9" and "_10") to the last line, and overload the box.
14. If level or leading: drop the block 10m deeper, defend the box collectively, exploit Wan-Bissaka's (player_id ends with "_5") recovery defending and Wissa's pace in transition.

## Key Player Notes
- **Mbemba (idx 3)** is the captain and defensive leader — earning a record-extending 113th cap. Composure on the ball is unusual for a CB of his physicality; the heart of the back three.
- **Wan-Bissaka (idx 5, speed 17)** is the elite 1v1 defender at right wing-back — match him against England's primary wide threat; breaks forward only on the counter.
- **Wissa (idx 10, speed 16 / shoot 16)** is the Leopards' dangerman and matchwinner — scored both of their goals vs Uzbekistan (incl. the decisive penalty) and their opener vs Portugal; a Premier League finisher with pace. First-choice penalty taker.
- **Bakambu (idx 9, shoot 15)** is the 35-year-old reference striker — preferred over Fiston Mayele for hold-up play and experience; he links the front line and finishes the counters.
- **Sadiki (idx 7, stamina 17)** is the 21-year-old Sunderland anchor — a relentless ball-winner (46 tackles, 34 interceptions in the PL) who is the engine room and shield of the structure.
- **Kayembe (idx 6, stamina 16 / pass 14)** is the box-to-box midfielder; he covers ground, breaks lines, and arrives late in the box.
- **Kapuadi (idx 4, strength 16)** is the extra centre-back added for the knockout — a physical aerial presence to bolster the back three against England.
- **Masuaku (idx 1, stamina 16)** is the attacking left wing-back and key set-piece deliverer; his overlaps are DR Congo's main left-side width, but he drops into a back five out of possession.

## Tournament Mindset
DR Congo are the underdogs of the last 32 — drawn against an England side that are clear favourites. After a hard-earned 1-1 draw with Portugal (17 June), a narrow 0-1 loss to Colombia (23 June), and a sensational 3-1 comeback over Uzbekistan (27 June) that sealed third in Group K, the Leopards have reached the knockouts for the first time in their history and have nothing to lose. The plan against England (1 July, Atlanta) is simple and disciplined: sit in a compact 5-3-2, frustrate the favourites, win the first ball on set pieces, and spring Wissa and Bakambu on the counter. Desabre backs his athletes' organisation and the pace and finishing of his front two to steal a moment — and the experience of Mbemba, Bakambu and Masuaku to see out a win-or-go-home knockout against the odds.
