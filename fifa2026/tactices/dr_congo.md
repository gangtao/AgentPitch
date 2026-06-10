# DR Congo — Tactical Profile

## Identity & Philosophy
Sébastien Desabre's DR Congo is athletic, transitional, and built around individual brilliance in the front players. Their 4-4-1-1 leverages the defensive solidity of Mbemba and Wan-Bissaka with the explosive wide pace of Meschak Elia and Nathanaël Mbuku, and the pace and finishing of Yoane Wissa playing off veteran striker Cédric Bakambu. The Leopards will not dominate possession against top sides — they will defend in mid-block and break with venom.

## Formation
- Shape: 4-4-1-1, transitional with a strong defensive spine.
- Role mapping (roster index -> tactical role):
  - 0 Mpasi — Goalkeeper.
  - 1 Masuaku — Left-back, attacking, technical.
  - 2 Tuanzebe — Left center-back, physical.
  - 3 Mbemba — Right center-back, captain, defensive leader.
  - 4 Wan-Bissaka — Right-back, world-class 1v1 defender.
  - 5 Elia — Left midfielder, explosive direct carrier.
  - 6 Moutoussamy — Central midfielder, defensive anchor.
  - 7 Sadiki — Central midfielder, balanced ball-winner.
  - 8 Mbuku — Right midfielder, pacy dribbler.
  - 9 Wissa — Second striker off the front, primary pace-and-finishing threat.
  - 10 Bakambu — Center-forward, veteran finisher.

## Style of Play

### Build-up
- Direct under pressure — Mpasi often goes long.
- Short build-up when uncontested: Mbemba steps forward with the ball.
- Moutoussamy and Sadiki form the central pair, splitting to receive from center-backs.
- Wan-Bissaka stays conservative; Masuaku pushes higher on the left.

### Pressing
- Mid-block press; selective high-press.
- Trigger: opposition CB receives back-to-goal or with a weak first touch.
- Bakambu and Wissa front the press; Elia and Mbuku jump the full-backs.
- Moutoussamy and Sadiki cover the central screen aggressively.

### Defensive shape
- 4-4-1-1 mid-block, two flat banks of four.
- Tuanzebe and Mbemba hold a balanced line.
- Wan-Bissaka shuts down opposing left-wingers 1v1 — exceptional defender in this matchup.
- Moutoussamy and Sadiki form the central screen.

### Wide play
- Left: Elia carries the ball at pace into the half-space, shoots or combines.
- Right: Mbuku drives inside to shoot or stretches in behind; Wan-Bissaka rarely overlaps far.
- Crosses target Bakambu near-post and Wissa arriving late.

### Final third
- Bakambu attacks the box; Wissa drops to combine then bursts in behind.
- Elia's dribbling is the principal half-space threat.
- Counter-attacks are typically 4-second sequences: turnover -> Wissa -> Bakambu or Elia.

## Set Pieces
- Mbemba and Tuanzebe are aerial targets.
- Masuaku and Bakambu share set-piece duties.
- Defensive set pieces: mixed marking, Mbemba on the biggest aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mpasi) under pressure: long ball to the CF channel (player_id ends with "_10", Bakambu) — do not attempt risky short pass.
2. If player_id ends with "_3" (Mbemba, RCB #22; skill 15, strength 16) and unpressed: drive forward into midfield with the ball.
3. If player_id ends with "_4" (Wan-Bissaka, RB #2) and opposition winger is 1v1 against him: stay tight, tackle when committed — he is the team's elite 1v1 defender.
4. If player_id ends with "_6" (Moutoussamy) or "_7" (Sadiki), the central pair: simple lateral passes; vertical pass to the second striker (player_id ends with "_9", Wissa) when he drops between lines.
5. If player_id ends with "_9" (Wissa, SS #20; speed 16, shoot 16): receive between lines, combine with the CF (player_id ends with "_10", Bakambu) or burst in behind, shoot from the half-space.
6. If player_id ends with "_5" (Elia, LM #13; speed 16, dribbling 15): take on the full-back from the left, shoot from the half-space.
7. If player_id ends with "_10" (Bakambu, CF #17; skill 14, shoot 15): constantly check the offside line; attack the box on crosses and cut-backs.
8. If player_id ends with "_8" (Mbuku, RM #7; speed 16, dribbling 15): dribble inside from the right, sprint in behind on through balls, shoot from the half-space.
9. If turnover in own half: outlet long to Wissa (player_id ends with "_9") or Elia (player_id ends with "_5") within 2 passes.
10. If defending: 4-4-1-1 mid-block, Wan-Bissaka (player_id ends with "_4") 1v1 anchors the right.
11. If trailing late: push Masuaku (player_id ends with "_1", LB) to wingback, Tuanzebe (player_id ends with "_2") and Mbemba (player_id ends with "_3") absorb the central duties, throw Wissa (player_id ends with "_9") and Mbuku (player_id ends with "_8") higher.
12. If leading 1-0: drop block 10m deeper, defend the box collectively, exploit Wan-Bissaka's (player_id ends with "_4") recovery defending.

## Key Player Notes
- **Mbemba** is the captain and defensive leader — his composure on the ball is unusual for a CB of his physicality.
- **Wan-Bissaka (speed 16)** is the elite 1v1 defender — match him against the opposition's primary winger.
- **Bakambu (shoot 15)** is the experienced reference striker; his movement in the box converts the counters.
- **Wissa (speed 16, shoot 16)** is the Leopards' dangerman — a Premier League finisher with pace playing off Bakambu; send him in behind or let him shoot from the half-space.
- **Elia (speed 16, dribbling 15)** is the principal left-side dribbler; encourage 1v1s.
- **Mbuku (speed 16, dribbling 15)** offers direct right-side pace; isolate him against full-backs on transitions.

## Tournament Mindset
DR Congo believes athleticism and individual quality can beat better-organized teams. They are happy to absorb pressure for 70 minutes if it means three or four clean counter-attacking chances.
