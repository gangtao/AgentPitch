# Switzerland — Tactical Profile

## Identity & Philosophy
Switzerland under Murat Yakin are a disciplined, low-risk side built around a deep block, a tenacious midfield core, and clinical finishing on the counter. They rarely chase possession but suffocate space, keep clean sheets through positional discipline, and lean on a golden generation that reached the knockout stages at Euro 2024 and the 2022 World Cup — and famously knocked out world champions France on penalties at Euro 2020. Their identity is "compact first, creative second" — the team is more than the sum of its parts, and they are supremely comfortable grinding a tie into the fine margins of extra time and shootouts.

**Round of 16 context (Tuesday 7 July, vs Colombia — BC Place, Vancouver):** Win or go home. After topping the group and dispatching Algeria 2-0 in the Round of 32, Switzerland now face a dangerous Colombia — a side with elite attacking quality in Luis Díaz, James Rodríguez and Jhon Durán, plus overlapping full-backs (Daniel Muñoz). Yakin keeps his first-choice spine intact: **Elvedi–Akanji** at centre-back (Luca Jaquez still training individually and not expected to feature). The key change from the Algeria win: **Denis Zakaria comes in at right-back** in place of Silvan Widmer, giving Switzerland a bigger, more physical body to contain Luis Díaz cutting infield from Colombia's left. The shape stays a **4-2-3-1**: a **Freuler–Xhaka double pivot** shields the back four, with **Johan Manzambi** — one of the breakout performers of the tournament — as the advanced #10 feeding Embolo. Michel Aebischer is a midfield doubt (training individually). Kobel remains the undisputed No.1.

## Formation
- Shape: 4-2-3-1 (Freuler and Xhaka as a screening double pivot; Manzambi the free #10 between the lines; Embolo the lone striker with Vargas and Ndoye tucked as inside-forwards).
- Role mapping (roster order in `switzerland.yaml`):
  - index 0 (`switzerland_0`, Kobel): GK — sweeper-keeper. Steps off line to clear long balls, distributes short when pressed.
  - index 1 (`switzerland_1`, Rodríguez): LB — overlapping fullback, primary left-side set-piece deliverer.
  - index 2 (`switzerland_2`, Elvedi): LCB — aerially dominant, no-frills line-leader.
  - index 3 (`switzerland_3`, Akanji): RCB — ball-playing CB, comfortable stepping into midfield with the ball.
  - index 4 (`switzerland_4`, Zakaria): RB — a converted midfielder giving physicality and defensive solidity; tucks inside almost as a third centre-back and screens the Ndoye channel rather than bombing on. Primary job: shut down Luis Díaz.
  - index 5 (`switzerland_5`, Freuler): LDM / holding pivot — box-to-box shuttler, anchors second-ball areas, screens in front of the back four.
  - index 6 (`switzerland_6`, Xhaka): RDM / deep #8 — captain, deep-lying playmaker, drops beside the CBs and switches play.
  - index 7 (`switzerland_7`, Manzambi): AM / #10 — free-roaming creator between the lines, late runs into the box, primary link to Embolo.
  - index 8 (`switzerland_8`, Vargas): LW — direct, cuts inside onto his right foot.
  - index 9 (`switzerland_9`, Embolo): CF — physical reference point, holds up play, leads the line.
  - index 10 (`switzerland_10`, Ndoye): RW — touchline winger, beat-man pace 1v1.

## Style of Play

### Build-up
Patient from the back. Kobel plays short to Akanji or out wide to Rodríguez. Xhaka drops between or beside the CBs to form a 3-2 build shape; Freuler holds and Manzambi floats to receive between the lines. Direct long balls to Embolo are a secondary option when the press is severe.

### Pressing (block height + trigger)
Mid-to-low block — defensive line sits around the halfway line out of possession. Press trigger: an opposition CB takes a heavy touch or plays sideways into a wide CB; Manzambi or the nearest pivot jumps. Otherwise the front line screens passing lanes rather than chasing, keen to deny James Rodríguez space between the lines and to stop the ball reaching Luis Díaz in stride.

### Defensive shape
Compact 4-4-1-1 / 4-2-3-1 without the ball — Vargas and Ndoye drop to form a midfield bank of four ahead of the Freuler–Xhaka double pivot; Manzambi shadows James Rodríguez, Colombia's deepest playmaker. Lines stay narrow (~25m horizontal between fullbacks). Distance between defensive and midfield lines never exceeds ~12 meters.

### Wide play
Asymmetric. Vargas (LW) cuts in onto his right, freeing Rodríguez to overlap. On the right, Ndoye stays wide and dribbles 1v1 while Zakaria holds a more conservative, defensively-minded position behind him (guarding against Díaz and Muñoz on the counter). The right-side Ndoye–Manzambi combination is Switzerland's main progression route; Zakaria supports underneath rather than overlapping.

### Final third
Quick combinations around Embolo. Look for cutbacks from the byline rather than crosses. Manzambi and Xhaka arrive late at the edge of the box for second-ball shots.

## Set Pieces
- Corners: Rodríguez and Xhaka deliver inswingers from the right, outswingers from the left. Akanji and Embolo are primary targets; Elvedi crashes the back post.
- Free kicks (direct, 20-30m): Xhaka takes from the left; Vargas/Manzambi from the right.
- **Penalties (single spot-kick during play):** Xhaka first; Embolo second.
- **Penalty shootout order (if the tie is level after extra time):**
  1. Granit Xhaka (index 6) — first-choice taker, ice-cold under pressure.
  2. Breel Embolo (index 9) — powerful, high-conviction finisher.
  3. Ruben Vargas (index 8) — reliable from the spot in the run of play.
  4. Ricardo Rodríguez (index 1) — veteran, experienced penalty taker.
  5. Manuel Akanji (index 3) — composed fifth taker.
  - Reserve takers if it runs deep: Remo Freuler (index 5), Johan Manzambi (index 7).
  - Kobel (index 0) is a strong shot-stopper who reads penalties well — Switzerland back him to be decisive in a shootout, echoing their Euro 2020 win over France.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Kobel, #1): if opposition through-ball detected and ball within 35m of GK, MOVE to intercept; else HOLD position on goal line.
2. If my player_id ends with "_2" or "_3" (CBs, Elvedi/Akanji): if no opposition forward within 8m AND a teammate with role "FWD" makes a vertical run, PASS line-breaking long ball; otherwise short to the player ending in "_6" (Xhaka).
3. If my player_id ends with "_6" (RDM / deep #8, Xhaka, #10): always offer as a passing option laterally to whichever CB has the ball; prioritize switches of play (>30m diagonal passes) when the opposite flank has 2v1.
4. If my player_id ends with "_5" (LDM pivot, Freuler, #8): shadow the opposition advanced midfielder; if opposition #10 receives between lines, TACKLE aggressively.
5. If my player_id ends with "_8" (LW, Vargas, #17): if receiving wide left with ball, DRIBBLE inside diagonally toward goal; if the player ending in "_1" (Rodríguez) overlaps, PASS into the channel.
6. If my player_id ends with "_10" (RW, Ndoye, #11): if isolated 1v1 with the opposition LB and within 30m of byline, DRIBBLE; if double-teamed, PASS back to the player ending in "_4" (Zakaria).
7. If my player_id ends with "_7" (AM / #10, Manzambi, #15): float between the lines; when team regains possession, run forward into the box and demand a vertical PASS; if within 22m of goal with a sight of goal, SHOOT.
8. If my player_id ends with "_9" (CF, Embolo, #7): if ball is in opposition third and within 25m of goal, HOLD with back to goal until a midfielder arrives, then lay off.
9. Any player: if losing the ball in own third, do NOT counter-press individually — retreat into shape.
10. If my role == "DEF": when defending a cross, prioritize being goal-side over ball-side; clear with strength rather than attempting controlled pass.
11. On opposition corner: the player ending in "_3" (Akanji) marks tallest attacker; the player ending in "_0" (Kobel) commands 6-yard box; the player ending in "_9" (Embolo) stays high as outlet.
12. If trailing by 1 goal with under 15 minutes left, the player ending in "_4" (Zakaria) pushes higher and the player ending in "_5" (Freuler) holds as the lone screen while "_6" (Xhaka) and "_7" (Manzambi) join the attack.
13. In extra time, prioritize keeping the tie alive: hold shape, avoid needless fouls in dangerous areas, and do not over-commit — Switzerland are content to reach a shootout.

## Key Player Notes
- **Granit Xhaka (index 6, captain):** free role as deep playmaker, drops to a single pivot beside the CBs in build-up. Every long switch should go through him. Switzerland's first-choice penalty taker and shootout leader — supremely reliable from the spot.
- **Manuel Akanji (index 3):** licensed to dribble out of defense — can step into midfield with ball. Composed fifth shootout taker.
- **Nico Elvedi (index 2):** aerial dominance, win first contacts, clear decisively rather than playing out under pressure.
- **Johan Manzambi (index 7):** the breakout #10 of the tournament — dynamic runner between the lines, arrives late in the box, direct link to Embolo. A genuine goal threat.
- **Breel Embolo (index 9):** target-man instructions; win aerial duels, lay off to runners, then attack the cutback. Not a pure poacher — drops into channels. Second penalty/shootout taker.
- **Dan Ndoye (index 10):** Switzerland's main 1v1 outlet on the right — pace to beat the fullback and reach the byline.
- **Gregor Kobel (index 0):** undisputed No.1 and sweeper-keeper — high starting position (~5m off line) when team has possession in opposition half. Commanding shot-stopper, strong on crosses, and a genuine penalty-saving threat in a shootout.
- **Ricardo Rodríguez (index 1):** primary set-piece taker from the left, overlapping outlet behind Vargas, and experienced fourth shootout taker.
- **Denis Zakaria (index 4):** a powerful midfielder deployed at right-back for this tie to add physicality against Luis Díaz. Defends first, tucks inside to make a back three in build-up, and steps into midfield when Switzerland have the ball. Aggressive in the tackle — must stay disciplined to avoid cards.

## Tournament Mindset
This is win-or-go-home. Switzerland do not need to entertain — they need to survive and advance. The plan is control through compactness: pack the middle with the Freuler–Xhaka double pivot, deny James Rodríguez space between the lines, screen the supply into Luis Díaz, and strike on the counter through Ndoye's pace and one moment of quality from Manzambi, Vargas or Embolo. A clean sheet at 0-0 is a good result — Switzerland are entirely comfortable taking Colombia into extra time and, if needed, a penalty shootout, a stage where their nerve (Euro 2020 vs France) and Kobel's shot-stopping give them real belief. Avoid needless bookings and reckless fouls near the box; discipline over the full 120 minutes is the edge. If it comes down to spot-kicks, Xhaka leads them off.
