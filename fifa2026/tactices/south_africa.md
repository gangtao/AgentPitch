# South Africa — Tactical Profile

## Identity & Philosophy
Hugo Broos has rebuilt Bafana Bafana into a confident, technically clean 4-3-3 — a side that defends compactly, counters fluidly, and trusts its young attackers. Penalty-saving GK Ronwen Williams gives the team belief, and Relebohile Mofokeng's craft is the creative heartbeat. Modest individual quality, but excellent team structure.

## Formation
- Shape: 4-3-3, balanced mid-block with a fluid front three.
- Role mapping (roster index -> tactical role):
  - 0 Ronwen Williams — Goalkeeper, captain, penalty-saver, leader.
  - 1 Modiba — Left-back, attacking, technical.
  - 2 Mbokazi — Left center-back, physical.
  - 3 Okon — Right center-back, tall and composed.
  - 4 Mudau — Right-back, balanced.
  - 5 Mokoena — #6, deep-lying conductor and set-piece taker.
  - 6 Sithole — #8, ball-winner.
  - 7 Jayden Adams — #8, press-resistant passer, late box arrivals.
  - 8 Appollis — Left winger, direct dribbler.
  - 9 Lyle Foster — Center-forward, mobile target.
  - 10 Mofokeng — Right winger / second creator, young dribbler.

## Style of Play

### Build-up
- Patient, with Mokoena dictating tempo from deep.
- Center-backs split wide; Mokoena drops to form a 3+2 against pressure.
- Modiba pushes high on the left; Mudau more conservative on the right.
- Williams comfortable distributing short.

### Pressing
- Mid-block press, coordinated rather than constant.
- Trigger: opposition CB receives in poor body shape.
- Foster presses; Mofokeng and Appollis jump the full-backs; Sithole steps on the pivot.
- Adams's energy supplements pressing waves.

### Defensive shape
- 4-1-4-1 mid-block, compact and well-drilled.
- Mokoena screens; Sithole and Adams shuttle.
- Center-backs hold a moderate line; Modiba and Mudau tuck inside when ball is opposite.

### Wide play
- Right: Mofokeng drifts inside, Mudau overlaps minimally.
- Left: Appollis attacks the channel and takes on his man; Modiba overlaps aggressively.
- Crosses target Foster's runs and Adams arriving late.

### Final third
- Mofokeng is the creative hub — drifting in from the right, he conducts the final third like a #10.
- Foster runs the channels and attacks crosses.
- Mofokeng's dribbling (16) creates moments from the half-space; Adams arrives late for cutbacks.
- Appollis pressures and finishes secondary chances down the left.

## Set Pieces
- Mokoena takes most attacking set pieces.
- Mbokazi, Okon, and Foster are aerial targets.
- Williams's reputation makes set-piece defending a strength — he commands his box.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Ronwen Williams): comfortable starting attacks short; long balls reserved for clear channel opportunities.
2. If player_id ends with "_5" (Mokoena, #6 #6; skill 15, pass 16): always face forward, primary outlet from defense.
3. If player_id ends with "_6" (Sithole, MID #8) and opponent has ball in midfield: tackle hard; he's the ball-winner.
4. If player_id ends with "_7" (Jayden Adams, MID #23; skill 14, pass 15): link play between the lines, play forward early, and arrive late at the edge of the box for cutbacks.
5. If player_id ends with "_8" (Appollis, LW #7): attack the left channel, dribble at the full-back, and combine with the CF (player_id ends with "_9", Foster). The young creator occupies the right (player_id ends with "_10", Mofokeng), who drifts between lines to link play.
6. If player_id ends with "_9" (Foster, CF #9): run channels constantly; attack near-post on crosses.
7. If player_id ends with "_1" (Modiba, LB #3): overlap on the left; provide width and crosses.
8. If turnover in own half: counter-press for 4 seconds, then drop into mid-block.
9. If defending in own third: maintain 4-1-4-1 distances, Mokoena (player_id ends with "_5") screens.
10. If trailing late: push Mudau (player_id ends with "_4", RB) higher, drop Sithole (player_id ends with "_6") alongside center-backs, push Adams (player_id ends with "_7") higher as a second creator.
11. If leading 1-0: drop block 8m deeper, defend the box.
12. If a penalty is awarded against South Africa: trust the GK (player_id ends with "_0", Ronwen Williams) to save it — he is the team's saving grace.

## Key Player Notes
- **Ronwen Williams (save 16)** is the spine of the side — his shot-stopping and penalty saves are SA's edge in tight games.
- **Mofokeng** is the team's young star on the right — give him freedom to dribble; he sees passes others don't.
- **Oswin Appollis** is the direct left-sided threat — let him run at his marker.
- **Jayden Adams** adds composure in midfield (pass 15) — the link between Mokoena and the front three.
- **Foster** is mobile and willing — feed him through balls and channel runs.
- **Mokoena** is the metronome — without him, the team loses shape.

## Tournament Mindset
South Africa believes they're better than the world expects; they will play with confidence, trust their goalkeeper, and look to spring counter-attacks through Mofokeng and Appollis.
