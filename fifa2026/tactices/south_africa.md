# South Africa — Tactical Profile

## Identity & Philosophy
Hugo Broos has rebuilt Bafana Bafana into a confident, technically clean 4-3-3 — a side that defends compactly, counters fluidly, and trusts its young attackers. Penalty-saving GK Ronwen Williams gives the team belief, and Themba Zwane's craft is the creative heartbeat. Modest individual quality, but excellent team structure.

## Formation
- Shape: 4-3-3, balanced mid-block with a fluid front three.
- Role mapping (roster index -> tactical role):
  - 0 Ronwen Williams — Goalkeeper, captain, penalty-saver, leader.
  - 1 Modiba — Left-back, attacking, technical.
  - 2 Mvala — Left center-back.
  - 3 Sibisi — Right center-back.
  - 4 Mudau — Right-back, balanced.
  - 5 Mokoena — #6, deep-lying conductor and set-piece taker.
  - 6 Sithole — #8, ball-winner.
  - 7 Mofokeng — #8 / advanced creator, young dribbler.
  - 8 Zwane — Right winger / second creator, veteran intelligence.
  - 9 Lyle Foster — Center-forward, mobile target.
  - 10 Rayners — Left winger / second striker.

## Style of Play

### Build-up
- Patient, with Mokoena dictating tempo from deep.
- Center-backs split wide; Mokoena drops to form a 3+2 against pressure.
- Modiba pushes high on the left; Mudau more conservative on the right.
- Williams comfortable distributing short.

### Pressing
- Mid-block press, coordinated rather than constant.
- Trigger: opposition CB receives in poor body shape.
- Foster presses; Zwane and Rayners jump the full-backs; Sithole steps on the pivot.
- Mofokeng's energy supplements pressing waves.

### Defensive shape
- 4-1-4-1 mid-block, compact and well-drilled.
- Mokoena screens; Sithole and Mofokeng shuttle.
- Center-backs hold a moderate line; Modiba and Mudau tuck inside when ball is opposite.

### Wide play
- Right: Zwane drifts inside, Mudau overlaps minimally.
- Left: Rayners attacks the channel; Modiba overlaps aggressively.
- Crosses target Foster's runs and Mofokeng arriving late.

### Final third
- Zwane is the creative hub — he conducts the final third like a #10.
- Foster runs the channels and attacks crosses.
- Mofokeng's dribbling (16) creates moments from the half-space.
- Rayners pressures and finishes secondary chances.

## Set Pieces
- Mokoena takes most attacking set pieces.
- Mvala, Sibisi, and Foster are aerial targets.
- Williams's reputation makes set-piece defending a strength — he commands his box.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Ronwen Williams): comfortable starting attacks short; long balls reserved for clear channel opportunities.
2. If player_id ends with "_5" (Mokoena, #6 #6; skill 15, pass 16): always face forward, primary outlet from defense.
3. If player_id ends with "_6" (Sithole, MID #8) and opponent has ball in midfield: tackle hard; he's the ball-winner.
4. If player_id ends with "_7" (Mofokeng, MID #10; skill 15, dribbling 16): in the half-space, take on the defender; shoot from 18-22m if angle is open.
5. If player_id ends with "_8" (Zwane, RW #7): drift between lines, link play between midfield and the CF (player_id ends with "_9", Foster).
6. If player_id ends with "_9" (Foster, CF #9): run channels constantly; attack near-post on crosses.
7. If player_id ends with "_1" (Modiba, LB #3): overlap on the left; provide width and crosses.
8. If turnover in own half: counter-press for 4 seconds, then drop into mid-block.
9. If defending in own third: maintain 4-1-4-1 distances, Mokoena (player_id ends with "_5") screens.
10. If trailing late: push Mudau (player_id ends with "_4", RB) higher, drop Sithole (player_id ends with "_6") alongside center-backs, push Mofokeng (player_id ends with "_7") wider.
11. If leading 1-0: drop block 8m deeper, defend the box.
12. If a penalty is awarded against South Africa: trust the GK (player_id ends with "_0", Ronwen Williams) to save it — he is the team's saving grace.

## Key Player Notes
- **Ronwen Williams (save 16)** is the spine of the side — his shot-stopping and penalty saves are SA's edge in tight games.
- **Themba Zwane** is the creative veteran; he sees passes others don't.
- **Mofokeng** is the team's young star — give him freedom to dribble.
- **Foster** is mobile and willing — feed him through balls and channel runs.
- **Mokoena** is the metronome — without him, the team loses shape.

## Tournament Mindset
South Africa believes they're better than the world expects; they will play with confidence, trust their goalkeeper, and look to spring counter-attacks through Zwane and Mofokeng.
