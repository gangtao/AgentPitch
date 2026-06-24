# DR Congo — Tactical Profile

## Identity & Philosophy
Sébastien Desabre's DR Congo is athletic, transitional, and built around defensive solidity plus individual brilliance in attack. The Leopards do not chase possession against better sides — they sit in a compact block, win the ball back, and break with venom. With qualification on the line in the final group game, Desabre reverts to a more orthodox **4-3-3**: a back four anchored by captain Chancel Mbemba, a hard-working midfield three (Kayembe, Pickel, Moutoussamy) that denies space, and a front three built on pace — Meschak Elia and the Premier League sharpness of Yoane Wissa flanking the experienced reference striker Cédric Bakambu. Discipline out of possession, ruthlessness in transition.

**Matchday 1 (17 June, vs Portugal — 1-1 draw):** A creditable point against Roberto Martínez's side; **Wissa scored** DR Congo's first goal of the tournament. Desabre set up in a compact block and frustrated Portugal.

**Matchday 2 (23 June, vs Colombia — 0-1 loss):** A narrow, disciplined defeat. DR Congo absorbed pressure for long spells before **Daniel Muñoz struck in the 76th minute** to settle it; Colombia sealed qualification, DR Congo were left on a single point. No DR Congo injuries, suspensions, or red cards were reported across the two games.

**Matchday 3 (27 June, vs Uzbekistan, Mercedes-Benz Stadium, Atlanta):** A **must-win** decider. Sitting third in Group K on one point, the Leopards must beat bottom side Uzbekistan to keep any hope of advancing as one of the best third-placed teams in the 48-team format. Desabre is expected to shift to a more attacking **4-3-3**, restoring **Edo Kayembe (#25)** and **Charles Pickel (#18)** to the midfield and starting **Meschak Elia (#13)** for width and pace on the right, with Wissa pushed central and Bakambu wide-left in a fluid front three. Uzbekistan have conceded eight goals across their two games (-7 GD) — DR Congo will look to take the initiative.

## Formation
- Shape: 4-3-3 — a back four, a midfield three (single pivot in front of two shuttlers), and a front three.
- Role mapping (roster order in `dr_congo.yaml`):
  - index 0: GK — Lionel Mpasi (#1; goes long under pressure)
  - index 1: LB — Arthur Masuaku (#26; attacking left-back, technical, set-piece deliverer)
  - index 2: LCB — Axel Tuanzebe (#4; physical left-sided center-back)
  - index 3: RCB — Chancel Mbemba (#22; captain, defensive leader, ball-carrier)
  - index 4: RB — Aaron Wan-Bissaka (#2; world-class 1v1 defender, athletic right-back, speed 16)
  - index 5: LCM — Edo Kayembe (#25; box-to-box engine, stamina 16, left shuttler)
  - index 6: DM — Charles Pickel (#18; combative central anchor, screens the back four)
  - index 7: RCM — Samuel Moutoussamy (#8; balanced ball-winner, vertical passer, right shuttler)
  - index 8: LW — Cédric Bakambu (#17; veteran reference striker deployed wide-left, shoot 15; attacks the box)
  - index 9: CF — Yoane Wissa (#20; pace-and-finishing threat, speed 16 / shoot 16; leads the line, bursts in behind)
  - index 10: RW — Meschak Elia (#13; pacey right winger, speed 16; stretches the line and attacks the channel)

## Style of Play

### Build-up
- Direct under pressure — Mpasi (idx 0) often goes long to the front three.
- Short build-up when uncontested: Mbemba (idx 3) steps out of the back four with the ball.
- Pickel (idx 6) drops between the center-backs to make a back-three base; Kayembe and Moutoussamy split to receive.
- Full-backs Masuaku (idx 1) and Wan-Bissaka (idx 4) provide the width and the first outlet on transition.

### Pressing
- Mid-block press; selective high-press against bottom side Uzbekistan.
- Trigger: opposition CB receives back-to-goal or with a weak first touch.
- Wissa (idx 9) fronts the press; Bakambu (idx 8) and Elia (idx 10) angle the wide CBs inside.
- Pickel (idx 6) holds the central screen aggressively in front of the back four.

### Defensive shape
- 4-3-3 collapses into a compact 4-5-1 — wingers Bakambu (idx 8) and Elia (idx 10) drop alongside the midfield three.
- Wan-Bissaka (idx 4) shuts down opposing wide threats 1v1 — exceptional recovery defender.
- Mbemba (idx 3) marshals the line; Tuanzebe (idx 2) wins the first ball.
- Pickel (idx 6) shields; Kayembe (idx 5) and Moutoussamy (idx 7) screen the half-spaces.

### Wide play
- Left: Masuaku (idx 1) overlaps as an attacking full-back; Bakambu (idx 8) drifts inside to the box, opening the flank.
- Right: Elia (idx 10) attacks the channel with pace; Wan-Bissaka (idx 4) supports with underlapping runs.
- Crosses target Wissa (idx 9) central and Bakambu (idx 8) arriving at the back post.

### Final third
- Wissa (idx 9) leads the line, dropping to combine then bursting in behind.
- Elia (idx 10) and Bakambu (idx 8) provide width and arrive in the box on cut-backs.
- Kayembe (idx 5) arrives late from midfield to support the front three.
- Counter-attacks are typically 4-second sequences: turnover -> full-back or shuttler -> Elia/Wissa -> shot.

## Set Pieces
- Mbemba (idx 3), Tuanzebe (idx 2) and Bakambu (idx 8) are aerial targets.
- Masuaku (idx 1) is the primary set-piece deliverer; Pickel (idx 6) shares duties.
- Penalties: Wissa (idx 9, penalty 16) is first taker; Bakambu (idx 8, penalty 15) is the alternate.
- Defensive set pieces: mixed marking, Mbemba on the biggest aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mpasi) under pressure: long ball toward the front three (player_id ends with "_9" Wissa or "_8" Bakambu) — do not attempt a risky short pass.
2. If player_id ends with "_3" (Mbemba, RCB #22; skill 15, strength 16) and unpressed: step out of the back four and drive forward with the ball.
3. If player_id ends with "_4" (Wan-Bissaka, RB #2; speed 16) and an opposition wide threat is 1v1 against him: tuck in, stay tight, tackle when committed — he is the team's elite 1v1 defender.
4. If player_id ends with "_6" (Pickel, DM #18): screen the back four; simple lateral passes; vertical pass to a forward (player_id ends with "_9" Wissa) when he drops between lines.
5. If player_id ends with "_9" (Wissa, CF #20; speed 16, shoot 16): lead the line, drop to combine or burst in behind, shoot from the half-space.
6. If player_id ends with "_5" (Kayembe, LCM #25; stamina 16, pass 14): drive box-to-box through the left half-space, break lines with a vertical pass to Wissa (player_id ends with "_9"), arrive late in the box.
7. If player_id ends with "_10" (Elia, RW #13; speed 16): stay wide on the right, attack the channel with pace, deliver cut-backs to Wissa (player_id ends with "_9") and the back post for Bakambu (player_id ends with "_8").
8. If player_id ends with "_1" (Masuaku, LB #26): overlap down the left, deliver crosses to the box for Wissa and Bakambu, take set-piece deliveries.
9. If player_id ends with "_7" (Moutoussamy, RCM #8): win the ball, then play vertical — feed the front three or release Wan-Bissaka (player_id ends with "_4") down the right.
10. If player_id ends with "_8" (Bakambu, LW #17; shoot 15): drift inside from the left, attack the box on crosses and cut-backs, constantly check the offside line.
11. If turnover in own half: outlet long to Wissa (player_id ends with "_9") or a winger (player_id ends with "_10" Elia / "_8" Bakambu) within 2 passes.
12. If defending: drop into a compact 4-5-1 — wingers (player_id ends with "_8" and "_10") tuck alongside the midfield three; full-backs (player_id ends with "_1" and "_4") hold the back line; Wan-Bissaka 1v1 anchors the right.
13. If trailing late: push both full-backs (player_id ends with "_1" and "_4") high, commit the front three (player_id ends with "_8", "_9", "_10") to the last line, and overload the box.
14. If leading 1-0: drop the block 10m deeper, defend the box collectively, exploit Wan-Bissaka's (player_id ends with "_4") recovery defending and Wissa/Elia's pace in transition.

## Key Player Notes
- **Mbemba (idx 3)** is the captain and defensive leader — composure on the ball is unusual for a CB of his physicality; the heart of the back four.
- **Wan-Bissaka (idx 4, speed 16)** is the elite 1v1 defender at right-back — match him against the opposition's primary winger.
- **Wissa (idx 9, speed 16 / shoot 16)** is the Leopards' dangerman and matchwinner — scored their only goal so far (vs Portugal); a Premier League finisher with pace leading the line. First-choice penalty taker.
- **Bakambu (idx 8, shoot 15)** is the experienced reference striker deployed wide-left in this shape; he drifts inside to attack the box and finish the counters.
- **Elia (idx 10, speed 16)** is the pacey right winger added for the must-win game — stretches defenses and attacks the channel in transition.
- **Kayembe (idx 5, stamina 16 / pass 14)** is the box-to-box engine restored to midfield; he covers ground, breaks lines, and arrives late in the box.
- **Pickel (idx 6, strength 15)** is the combative single pivot who screens the back four and breaks up play.
- **Masuaku (idx 1)** is the attacking left-back and key set-piece deliverer; his overlaps are DR Congo's main left-side width.

## Tournament Mindset
DR Congo are the underdogs of Group K, drawn alongside Portugal, Colombia and Uzbekistan. After a hard-earned 1-1 draw with Portugal (17 June) and a narrow 0-1 loss to Colombia (23 June), the Leopards sit **third on one point** going into Matchday 3. The Uzbekistan game (27 June, Atlanta) is a straight must-win: a victory keeps alive their hope of progressing as one of the best third-placed sides in the 48-team format, while anything less ends their tournament. Against a bottom side that has shipped eight goals, Desabre will take the initiative for once — a more attacking 4-3-3, pace through Elia and Wissa, and the experience of Bakambu and Mbemba — backing his players to finally turn discipline and athleticism into the goals that carry them out of the group.
