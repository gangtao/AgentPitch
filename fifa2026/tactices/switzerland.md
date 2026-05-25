# Switzerland — Tactical Profile

## Identity & Philosophy
Switzerland under Murat Yakin are a disciplined, low-risk side built around a deep block, a tenacious midfield core, and clinical finishing on the counter. They rarely dominate possession but suffocate space, keep clean sheets through positional discipline, and lean on a generation that has reached the knockout stage at Euro 2024 and the 2022 World Cup. Their identity is "compact first, creative second" — the team is more than the sum of its parts.

## Formation
- Shape: 4-2-3-1
- Role mapping (roster order in `switzerland.yaml`):
  - index 0 (`switzerland_0`, Sommer): GK — sweeper-keeper. Steps off line to clear long balls, distributes short when pressed.
  - index 1 (`switzerland_1`, Rodríguez): LB — overlapping fullback, set-piece deliverer.
  - index 2 (`switzerland_2`, Akanji): LCB — ball-playing CB, comfortable stepping into midfield.
  - index 3 (`switzerland_3`, Elvedi): RCB — aerial dominator, line-leader.
  - index 4 (`switzerland_4`, Widmer): RB — disciplined, stays home more than LB.
  - index 5 (`switzerland_5`, Freuler): DM right — box-to-box shuttler, anchors second-ball areas.
  - index 6 (`switzerland_6`, Xhaka): DM left — deep-lying playmaker, captain, switches play.
  - index 7 (`switzerland_7`, Vargas): LW — direct, cuts inside onto right foot.
  - index 8 (`switzerland_8`, Rieder): AM — half-space creator, two-way runner.
  - index 9 (`switzerland_9`, Ndoye): RW — touchline winger, beat-man pace.
  - index 10 (`switzerland_10`, Embolo): CF — physical reference point, holds up play.

## Style of Play

### Build-up
Patient from the back. Sommer plays short to Akanji or out wide to Rodríguez. Xhaka drops between or beside the CBs to form a 3-2 build shape; Freuler pushes higher. Direct long balls to Embolo are a secondary option when the press is severe.

### Pressing (block height + trigger)
Mid-to-low block — defensive line sits around the halfway line out of possession. Press trigger: an opposition CB takes a heavy touch or plays sideways into a wide CB; the AM (Rieder) jumps. Otherwise, the front 4 screen passing lanes rather than chase.

### Defensive shape
Compact 4-4-1-1 without the ball. Vargas and Ndoye tuck in to form a midfield bank of four; Rieder shadows the opposition #6. Lines stay narrow (~25m horizontal between fullbacks). Distance between defensive and midfield lines never exceeds ~12 meters.

### Wide play
Asymmetric. Vargas (LW) cuts in onto his right, freeing Rodríguez to overlap. On the right, Ndoye stays wide and dribbles 1v1; Widmer underlaps.

### Final third
Quick combinations around Embolo. Look for cutbacks from the byline rather than crosses. Xhaka and Rieder arrive late at the edge of the box for second-ball shots.

## Set Pieces
- Corners: Rodríguez and Xhaka deliver inswingers from the right, outswingers from the left. Akanji and Embolo are primary targets; Elvedi crashes the back post.
- Free kicks (direct, 20-30m): Xhaka takes from the left; Rieder from the right.
- Penalties: Embolo first; Xhaka second.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Sommer, #1): if opposition through-ball detected and ball within 35m of GK, MOVE to intercept; else HOLD position on goal line.
2. If my player_id ends with "_2" or "_3" (CBs, Akanji/Elvedi): if no opposition forward within 8m AND a teammate with role "FWD" makes a vertical run, PASS line-breaking long ball; otherwise short to the player ending in "_6" (Xhaka).
3. If my player_id ends with "_6" (DM left, Xhaka, #10): always offer as a passing option laterally to whichever CB has the ball; prioritize switches of play (>30m diagonal passes) when the opposite flank has 2v1.
4. If my player_id ends with "_5" (DM right, Freuler, #8): shadow the opposition advanced midfielder; if opposition #10 receives between lines, TACKLE aggressively.
5. If my player_id ends with "_7" (LW, Vargas, #17): if receiving wide left with ball, DRIBBLE inside diagonally toward goal; if the player ending in "_1" (Rodríguez) overlaps, PASS into the channel.
6. If my player_id ends with "_9" (RW, Ndoye, #14): if isolated 1v1 with RB and within 30m of byline, DRIBBLE; if double-teamed, PASS back to the player ending in "_4" (Widmer).
7. If my player_id ends with "_8" (AM, Rieder, #15): when team regains possession, run forward into the half-space and demand a vertical PASS.
8. If my player_id ends with "_10" (CF, Embolo, #7): if ball is in opposition third and within 25m of goal, HOLD with back to goal until a midfielder arrives, then lay off.
9. Any player: if losing the ball in own third, do NOT counter-press individually — retreat into shape.
10. If my role == "DEF": when defending a cross, prioritize being goal-side over ball-side; clear with strength rather than attempting controlled pass.
11. On opposition corner: the player ending in "_2" (Akanji) marks tallest attacker; the player ending in "_0" (Sommer) commands 6-yard box; the player ending in "_10" (Embolo) stays high as outlet.
12. If trailing by 1 goal with under 15 minutes left, the player ending in "_4" (Widmer) pushes higher and the player ending in "_5" (Freuler) leaves DM duties to "_6" (Xhaka).

## Key Player Notes
- **Granit Xhaka (index 6, captain):** free role as deep playmaker. Allowed to drift into LCB position during build-up. Every long switch should go through him.
- **Manuel Akanji (index 2):** licensed to dribble out of defense — can step into midfield with ball.
- **Breel Embolo (index 10):** target-man instructions; expect to win 50% of aerial duels, lay off to runners. Not a pure poacher — drops into channels.
- **Yann Sommer (index 0):** sweeper-keeper role — high starting position (~5m off line) when team has possession in opposition half.
- **Ricardo Rodríguez (index 1):** primary set-piece taker from the left.

## Tournament Mindset
Park-the-bus pragmatism with one moment of quality from Xhaka or Embolo. Switzerland do not need to win — they need to not lose, then strike.
