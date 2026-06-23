# Switzerland — Tactical Profile

## Identity & Philosophy
Switzerland under Murat Yakin are a disciplined, low-risk side built around a deep block, a tenacious midfield core, and clinical finishing on the counter. They rarely chase possession but suffocate space, keep clean sheets through positional discipline, and lean on a golden generation that reached the knockout stages at Euro 2024 and the 2022 World Cup. Their identity is "compact first, creative second" — the team is more than the sum of its parts.

**Matchday 3 context (24 June, vs Canada — BC Place, Vancouver):** Switzerland and Canada arrive level on points at the top of Group B; this is effectively a straight fight for first place. After beating Bosnia & Herzegovina 4-1 on MD2, Yakin shifts to a flatter **4-3-3** to add a third central midfielder and better control the middle against Canada's transitions. Two changes are forced/managed: **Nico Elvedi is on a yellow card and rested** to avoid a knockout-phase suspension, with **Luca Jaquez** stepping in alongside Akanji; and **Michel Aebischer** comes into a midfield three with Xhaka (captain) and Freuler. Embolo leads the line and is chasing the Swiss all-time World Cup goalscoring charts.

## Formation
- Shape: 4-3-3 (Xhaka as the left-sided controlling #8 dropping to a pivot; Freuler the box-to-box; Aebischer the right interior)
- Role mapping (roster order in `switzerland.yaml`):
  - index 0 (`switzerland_0`, Kobel): GK — sweeper-keeper. Steps off line to clear long balls, distributes short when pressed.
  - index 1 (`switzerland_1`, Rodríguez): LB — overlapping fullback, primary left-side set-piece deliverer.
  - index 2 (`switzerland_2`, Akanji): LCB — ball-playing CB, comfortable stepping into midfield.
  - index 3 (`switzerland_3`, Jaquez): RCB — aerial, no-frills line-leader deputizing for the rested Elvedi.
  - index 4 (`switzerland_4`, Widmer): RB — disciplined, stays home more than the LB; underlaps for Ndoye.
  - index 5 (`switzerland_5`, Xhaka): LCM / deep #8 — captain, deep-lying playmaker, drops beside the CBs and switches play.
  - index 6 (`switzerland_6`, Freuler): CM — box-to-box shuttler, anchors second-ball areas, screens in front of the back four.
  - index 7 (`switzerland_7`, Aebischer): RCM — two-way interior, late runner into the right half-space.
  - index 8 (`switzerland_8`, Vargas): LW — direct, cuts inside onto his right foot.
  - index 9 (`switzerland_9`, Embolo): CF — physical reference point, holds up play, leads the line.
  - index 10 (`switzerland_10`, Ndoye): RW — touchline winger, beat-man pace 1v1.

## Style of Play

### Build-up
Patient from the back. Kobel plays short to Akanji or out wide to Rodríguez. Xhaka drops between or beside the CBs to form a 3-2 build shape; Freuler and Aebischer stagger ahead of him. Direct long balls to Embolo are a secondary option when the press is severe.

### Pressing (block height + trigger)
Mid-to-low block — defensive line sits around the halfway line out of possession. Press trigger: an opposition CB takes a heavy touch or plays sideways into a wide CB; the nearest interior (Aebischer or Freuler) jumps. Otherwise the front three screen passing lanes rather than chase.

### Defensive shape
Compact 4-5-1 / 4-1-4-1 without the ball — Vargas and Ndoye drop to form a midfield bank of five, Freuler shielding the back four. Lines stay narrow (~25m horizontal between fullbacks). Distance between defensive and midfield lines never exceeds ~12 meters.

### Wide play
Asymmetric. Vargas (LW) cuts in onto his right, freeing Rodríguez to overlap. On the right, Ndoye stays wide and dribbles 1v1; Widmer underlaps. The right-side Ndoye-Aebischer-Widmer triangle is Switzerland's main progression route.

### Final third
Quick combinations around Embolo. Look for cutbacks from the byline rather than crosses. Xhaka and Aebischer arrive late at the edge of the box for second-ball shots.

## Set Pieces
- Corners: Rodríguez and Xhaka deliver inswingers from the right, outswingers from the left. Akanji and Embolo are primary targets; Jaquez crashes the back post.
- Free kicks (direct, 20-30m): Xhaka takes from the left; Aebischer/Vargas from the right.
- Penalties: Embolo first; Xhaka second.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Kobel, #1): if opposition through-ball detected and ball within 35m of GK, MOVE to intercept; else HOLD position on goal line.
2. If my player_id ends with "_2" or "_3" (CBs, Akanji/Jaquez): if no opposition forward within 8m AND a teammate with role "FWD" makes a vertical run, PASS line-breaking long ball; otherwise short to the player ending in "_5" (Xhaka).
3. If my player_id ends with "_5" (LCM / deep #8, Xhaka, #10): always offer as a passing option laterally to whichever CB has the ball; prioritize switches of play (>30m diagonal passes) when the opposite flank has 2v1.
4. If my player_id ends with "_6" (CM, Freuler, #8): shadow the opposition advanced midfielder; if opposition #10 receives between lines, TACKLE aggressively.
5. If my player_id ends with "_8" (LW, Vargas, #17): if receiving wide left with ball, DRIBBLE inside diagonally toward goal; if the player ending in "_1" (Rodríguez) overlaps, PASS into the channel.
6. If my player_id ends with "_10" (RW, Ndoye, #11): if isolated 1v1 with the opposition LB and within 30m of byline, DRIBBLE; if double-teamed, PASS back to the player ending in "_4" (Widmer).
7. If my player_id ends with "_7" (RCM, Aebischer, #20): when team regains possession, run forward into the right half-space and demand a vertical PASS.
8. If my player_id ends with "_9" (CF, Embolo, #7): if ball is in opposition third and within 25m of goal, HOLD with back to goal until a midfielder arrives, then lay off.
9. Any player: if losing the ball in own third, do NOT counter-press individually — retreat into shape.
10. If my role == "DEF": when defending a cross, prioritize being goal-side over ball-side; clear with strength rather than attempting controlled pass.
11. On opposition corner: the player ending in "_2" (Akanji) marks tallest attacker; the player ending in "_0" (Kobel) commands 6-yard box; the player ending in "_9" (Embolo) stays high as outlet.
12. If trailing by 1 goal with under 15 minutes left, the player ending in "_4" (Widmer) pushes higher and the player ending in "_6" (Freuler) holds as the lone screen while "_5" (Xhaka) and "_7" (Aebischer) join the attack.

## Key Player Notes
- **Granit Xhaka (index 5, captain):** free role as deep playmaker, drops to a single pivot beside the CBs in build-up. Every long switch should go through him. Chasing further entries onto the Swiss all-time World Cup scorers list.
- **Manuel Akanji (index 2):** licensed to dribble out of defense — can step into midfield with ball.
- **Luca Jaquez (index 3):** in for the rested (yellow-card) Elvedi — keep it simple, win first contacts, clear decisively rather than playing out under pressure.
- **Breel Embolo (index 9):** target-man instructions; win aerial duels, lay off to runners, then attack the cutback. Not a pure poacher — drops into channels.
- **Michel Aebischer (index 7):** the new third midfielder — two-way energy, late arrivals into the right half-space, secondary right-side set-piece taker.
- **Dan Ndoye (index 10):** Switzerland's main 1v1 outlet on the right — pace to beat the fullback and reach the byline.
- **Gregor Kobel (index 0):** sweeper-keeper — high starting position (~5m off line) when team has possession in opposition half. Commanding shot-stopper and strong on crosses.
- **Ricardo Rodríguez (index 1):** primary set-piece taker from the left and overlapping outlet behind Vargas.

## Tournament Mindset
Pragmatic control with one moment of quality from Xhaka, Ndoye or Embolo. With top spot in Group B on the line against Canada, Switzerland do not need to chase the game — they pack the midfield with a third man, stay compact, and strike on the counter. Avoid needless bookings: Elvedi is already being protected, and a clean disciplinary sheet keeps the knockout squad whole.
