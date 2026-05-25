# DR Congo — Tactical Profile

## Identity & Philosophy
Sébastien Desabre's DR Congo is athletic, transitional, and built around individual brilliance in the front four. Their 4-2-3-1 leverages the defensive solidity of Mbemba and Wan-Bissaka with the explosive carrying of Bongonda and the finishing of Fiston Mayele. The Leopards will not dominate possession against top sides — they will defend in mid-block and break with venom.

## Formation
- Shape: 4-2-3-1, transitional with a strong defensive spine.
- Role mapping (roster index -> tactical role):
  - 0 Mpasi — Goalkeeper.
  - 1 Masuaku — Left-back, attacking, technical.
  - 2 Mbemba — Left center-back, captain, defensive leader.
  - 3 Tuanzebe — Right center-back, physical.
  - 4 Wan-Bissaka — Right-back, world-class 1v1 defender.
  - 5 Sadiki — Defensive midfielder, balanced.
  - 6 Mukau — Defensive midfielder, ball-winner.
  - 7 Bongonda — Left winger, direct carrier.
  - 8 Bakambu — Attacking midfielder / second striker, veteran finisher.
  - 9 Elia — Right winger / second creator.
  - 10 Mayele — Center-forward, channel runner and finisher.

## Style of Play

### Build-up
- Direct under pressure — Mpasi often goes long.
- Short build-up when uncontested: Mbemba steps forward with the ball.
- Sadiki and Mukau form a double pivot, splitting to receive from center-backs.
- Wan-Bissaka stays conservative; Masuaku pushes higher on the left.

### Pressing
- Mid-block press; selective high-press.
- Trigger: opposition CB receives back-to-goal or with a weak first touch.
- Mayele and Bakambu front the press; Bongonda and Elia jump the full-backs.
- Sadiki and Mukau cover the central screen aggressively.

### Defensive shape
- 4-4-1-1 / 4-2-3-1 hybrid mid-block.
- Mbemba and Tuanzebe hold a balanced line.
- Wan-Bissaka shuts down opposing left-wingers 1v1 — exceptional defender in this matchup.
- Sadiki and Mukau form a double pivot screen.

### Wide play
- Left: Bongonda carries the ball into the half-space, shoots or combines.
- Right: Elia dribbles and crosses; Wan-Bissaka rarely overlaps far.
- Crosses target Mayele near-post and Bakambu arriving late.

### Final third
- Mayele runs channels; Bakambu drifts back to combine then attacks the box.
- Bongonda's dribbling is the principal half-space threat.
- Counter-attacks are typically 4-second sequences: turnover -> Bakambu -> Mayele or Bongonda.

## Set Pieces
- Mbemba and Tuanzebe are aerial targets.
- Bakambu and Mukau share set-piece duties.
- Defensive set pieces: mixed marking, Mbemba on the biggest aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mpasi) under pressure: long ball to the CF channel (player_id ends with "_10", Mayele) — do not attempt risky short pass.
2. If player_id ends with "_2" (Mbemba, LCB #4; skill 15, strength 16) and unpressed: drive forward into midfield with the ball.
3. If player_id ends with "_4" (Wan-Bissaka, RB #2) and opposition winger is 1v1 against him: stay tight, tackle when committed — he is the team's elite 1v1 defender.
4. If player_id ends with "_5" (Sadiki) or "_6" (Mukau), the double pivot: simple lateral passes; vertical pass to the AM (player_id ends with "_8", Bakambu) when he drops between lines.
5. If player_id ends with "_8" (Bakambu, AM #11): receive between lines, lay off to the CF run (player_id ends with "_10", Mayele) or combine with the LW (player_id ends with "_7", Bongonda).
6. If player_id ends with "_7" (Bongonda, LW #7; speed 14, dribbling 14): take on the full-back from the left, shoot from the half-space.
7. If player_id ends with "_10" (Mayele, CF #9; speed 15, shoot 16): constantly check the offside line; sprint behind on through balls.
8. If player_id ends with "_9" (Elia, RW #10): dribble inside from the right, shoot from the half-space.
9. If turnover in own half: outlet long to Mayele (player_id ends with "_10") or Bongonda (player_id ends with "_7") within 2 passes.
10. If defending: 4-2-3-1 mid-block, Wan-Bissaka (player_id ends with "_4") 1v1 anchors the right.
11. If trailing late: push Masuaku (player_id ends with "_1", LB) to wingback, Mbemba (player_id ends with "_2") and Tuanzebe (player_id ends with "_3") absorb the central duties, throw Bakambu (player_id ends with "_8") and Elia (player_id ends with "_9") higher.
12. If leading 1-0: drop block 10m deeper, defend the box collectively, exploit Wan-Bissaka's (player_id ends with "_4") recovery defending.

## Key Player Notes
- **Mbemba** is the captain and defensive leader — his composure on the ball is unusual for a CB of his physicality.
- **Wan-Bissaka (speed 16)** is the elite 1v1 defender — match him against the opposition's primary winger.
- **Bakambu** is the experienced playmaker-forward; his vision unlocks low blocks.
- **Mayele (shoot 16)** is the team's top finisher — feed him runs in behind constantly.
- **Bongonda** is the principal dribbler; encourage 1v1s.

## Tournament Mindset
DR Congo believes athleticism and individual quality can beat better-organized teams. They are happy to absorb pressure for 70 minutes if it means three or four clean counter-attacking chances.
