# Switzerland — Tactical Profile

## Identity & Philosophy
Switzerland under Murat Yakin are a disciplined, low-risk side built around a deep block, a tenacious midfield core, and clinical finishing on the counter. They rarely chase possession but suffocate space, keep clean sheets through positional discipline, and lean on a golden generation that reached the knockout stages at Euro 2024 and the 2022 World Cup — and famously knocked out world champions France on penalties at Euro 2020. Their identity is "compact first, creative second" — the team is more than the sum of its parts, and they are supremely comfortable grinding a tie into the fine margins of extra time and shootouts. That identity just delivered again: a goalless 120 minutes against Colombia in Vancouver, then a 4-3 shootout win — Kobel saving from Cucho Hernández, Davinson Sánchez rattling the bar, and Ruben Vargas burying the decisive fifth kick to send Switzerland to a **first World Cup quarter-final since 1954**, when they hosted the tournament.

**Quarter-final context (Saturday 11 July, vs Argentina — GEHA Field at Arrowhead Stadium, Kansas City):** the reigning world champions await, but they are wobbling — Argentina drew 1-1 with Cape Verde before winning in extra time in the Round of 32, then trailed Egypt 2-0 with 11 minutes left before a 3-2 comeback in the Round of 16. Yakin's headache is **Johan Manzambi**: the breakout #10 scored three goals in the tournament but a knee injury kept him out of the Colombia tie and he faces a race against time — **Ardon Jashari**, the AC Milan midfielder who deputised in Vancouver, keeps the shirt, converting the 4-2-3-1 into a **4-3-3** with Xhaka as the single pivot flanked by Freuler and Jashari. **Ruben Vargas is fit to start again** after his own fitness scare (he was only a stoppage-time substitute vs Colombia — and still scored the winning penalty). Michel Aebischer and Luca Jaquez are still training individually and are not expected to feature. Kobel remains the undisputed No.1. Discipline is now a live constraint: **Xhaka and Zakaria were both booked against Colombia and are one yellow card away from missing a potential semi-final** (cards are wiped only after the quarter-finals).

## Formation
- Shape: 4-3-3 (Xhaka as the lone pivot; Freuler and Jashari as shuttling #8s; Embolo the lone striker with Vargas and Ndoye tucked as inside-forwards).
- Role mapping (roster order in `switzerland.yaml`):
  - index 0 (`switzerland_0`, Kobel): GK — sweeper-keeper. Steps off line to clear long balls, distributes short when pressed. Saved from Cucho Hernández in the R16 shootout.
  - index 1 (`switzerland_1`, Rodríguez): LB — veteran overlapping fullback, primary left-side set-piece deliverer.
  - index 2 (`switzerland_2`, Elvedi): LCB — aerially dominant, no-frills line-leader.
  - index 3 (`switzerland_3`, Akanji): RCB — ball-playing CB, comfortable stepping into midfield with the ball.
  - index 4 (`switzerland_4`, Zakaria): RB — converted midfielder giving physicality; tucks inside almost as a third centre-back. Primary job: contain the runs beyond Messi. **On a yellow — one more means a semi-final ban.**
  - index 5 (`switzerland_5`, Freuler): left #8 — box-to-box shuttler, anchors second-ball areas, drops beside Xhaka out of possession to reform the double pivot.
  - index 6 (`switzerland_6`, Xhaka): DM / single pivot — captain, deep-lying playmaker, drops beside the CBs and switches play. **On a yellow — one more means a semi-final ban.**
  - index 7 (`switzerland_7`, Jashari): right #8 — Manzambi's deputy; press-resistant AC Milan midfielder, receives on the half-turn, links to Ndoye and arrives late at the edge of the box.
  - index 8 (`switzerland_8`, Vargas): LW — direct, cuts inside onto his right foot. Fit to start again; scored the decisive shootout penalty vs Colombia.
  - index 9 (`switzerland_9`, Embolo): CF — physical reference point, holds up play, leads the line; 13 goal involvements in his last 17 internationals.
  - index 10 (`switzerland_10`, Ndoye): RW — touchline winger, beat-man pace 1v1.

## Style of Play

### Build-up
Patient from the back. Kobel plays short to Akanji or out wide to Rodríguez. Xhaka drops between or beside the CBs to form a 3-2 build shape; Freuler holds and Jashari floats to receive on the half-turn between Argentina's midfield lines. Direct long balls to Embolo are a secondary option when the press is severe — expect Argentina to press higher than Colombia did.

### Pressing (block height + trigger)
Mid-to-low block — defensive line sits around the halfway line out of possession. Press trigger: an opposition CB takes a heavy touch or plays sideways into a wide CB; Jashari or the nearest #8 jumps. Otherwise the front line screens passing lanes rather than chasing — the priority is denying Messi clean possession in the right half-space pocket and cutting the supply from De Paul and Mac Allister.

### Defensive shape
Compact 4-1-4-1 / 4-5-1 without the ball — Vargas and Ndoye drop to form a midfield bank alongside Freuler and Jashari, with Xhaka screening in front of the back four. Whoever is nearest of Freuler/Jashari picks up Messi when he drops between the lines; Xhaka never follows him out and keeps the screen. Lines stay narrow (~25m horizontal between fullbacks). Distance between defensive and midfield lines never exceeds ~12 meters.

### Wide play
Asymmetric. Vargas (LW) cuts in onto his right, freeing Rodríguez to overlap. On the right, Ndoye stays wide and dribbles 1v1 while Zakaria holds a conservative, defensively-minded position behind him (guarding the counter into the channel Messi drifts toward). The right-side Ndoye–Jashari combination is Switzerland's main progression route; Zakaria supports underneath rather than overlapping.

### Final third
Quick combinations around Embolo. Look for cutbacks from the byline rather than crosses. Jashari and Xhaka arrive late at the edge of the box for second-ball shots.

## Set Pieces
- Corners: Rodríguez and Xhaka deliver inswingers from the right, outswingers from the left. Akanji and Embolo are primary targets; Elvedi crashes the back post.
- Free kicks (direct, 20-30m): Xhaka takes from the left; Vargas from the right.
- **Penalties (single spot-kick during play):** Xhaka first; Embolo second.
- **Penalty shootout order (if the tie is level after extra time — proven route: they just beat Colombia 4-3 this way):**
  1. Granit Xhaka (index 6) — first-choice taker, ice-cold under pressure.
  2. Breel Embolo (index 9) — powerful, high-conviction finisher.
  3. Ruben Vargas (index 8) — scored the decisive kick against Colombia; nerveless.
  4. Ricardo Rodríguez (index 1) — veteran, experienced penalty taker.
  5. Remo Freuler (index 5) — composed fifth taker.
  - Reserve takers if it runs deep: Jashari (index 7), Zakaria (index 4). **Akanji (index 3) skied his kick over the bar in Vancouver and drops out of the first five.**
  - Kobel (index 0) is a proven shootout keeper — he saved from Cucho Hernández in the Round of 16, and Switzerland back him to be decisive again, echoing their Euro 2020 win over France.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Kobel, #1): if opposition through-ball detected and ball within 35m of GK, MOVE to intercept; else HOLD position on goal line.
2. If my player_id ends with "_2" or "_3" (CBs, Elvedi/Akanji): if no opposition forward within 8m AND a teammate with role "FWD" makes a vertical run, PASS line-breaking long ball; otherwise short to the player ending in "_6" (Xhaka).
3. If my player_id ends with "_6" (DM pivot, Xhaka, #10): always offer as a passing option laterally to whichever CB has the ball; prioritize switches of play (>30m diagonal passes) when the opposite flank has 2v1. Do NOT tackle recklessly — one more yellow means missing the semi-final; jockey and screen instead.
4. If my player_id ends with "_5" (left #8, Freuler, #8): shadow the opposition's advanced playmaker; if the opposition #10 receives between the lines, TACKLE aggressively — Freuler carries no card risk and does the fouling this team needs.
5. If my player_id ends with "_8" (LW, Vargas, #17): if receiving wide left with ball, DRIBBLE inside diagonally toward goal; if the player ending in "_1" (Rodríguez) overlaps, PASS into the channel.
6. If my player_id ends with "_10" (RW, Ndoye, #11): if isolated 1v1 with the opposition LB and within 30m of byline, DRIBBLE; if double-teamed, PASS back to the player ending in "_4" (Zakaria).
7. If my player_id ends with "_7" (right #8, Jashari, #16): receive on the half-turn between the lines; when team regains possession, PASS forward quickly to release "_10" (Ndoye) or "_9" (Embolo); if within 22m of goal with a sight of goal, SHOOT.
8. If my player_id ends with "_9" (CF, Embolo, #7): if ball is in opposition third and within 25m of goal, HOLD with back to goal until a midfielder arrives, then lay off.
9. Any player: if losing the ball in own third, do NOT counter-press individually — retreat into shape.
10. If my role == "DEF": when defending a cross, prioritize being goal-side over ball-side; clear with strength rather than attempting controlled pass. If my player_id ends with "_4" (Zakaria): no tactical fouls — one more yellow means a semi-final ban.
11. On opposition corner: the player ending in "_3" (Akanji) marks tallest attacker; the player ending in "_0" (Kobel) commands 6-yard box; the player ending in "_9" (Embolo) stays high as outlet.
12. If trailing by 1 goal with under 15 minutes left, the player ending in "_1" (Rodríguez) pushes higher and the player ending in "_6" (Xhaka) holds as the lone screen while "_5" (Freuler) and "_7" (Jashari) join the attack.
13. In extra time, prioritize keeping the tie alive: hold shape, avoid needless fouls in dangerous areas, and do not over-commit — Switzerland just proved in Vancouver they are content to reach a shootout.

## Key Player Notes
- **Granit Xhaka (index 6, captain):** 151 caps of authority as the lone pivot — every long switch goes through him, and he is the set-piece specialist and first shootout taker. CAUTION: booked vs Colombia, one yellow from a semi-final ban — must defend with positioning, not fouls.
- **Ardon Jashari (index 7):** Manzambi's deputy and the shape-changer — a press-resistant AC Milan midfielder who turned the 4-2-3-1 into a 4-3-3 in the Colombia win. Receives between the lines, links to Ndoye, arrives late for edge-of-box shots. Djibril Sow is the more defensive bench alternative; Manzambi (knee) is racing to make the bench.
- **Manuel Akanji (index 3):** licensed to dribble out of defense — can step into midfield with ball. NOTE: missed his shootout kick vs Colombia — no longer in the first five takers.
- **Nico Elvedi (index 2):** aerial dominance, win first contacts, clear decisively rather than playing out under pressure.
- **Breel Embolo (index 9):** target-man instructions; win aerial duels, lay off to runners, then attack the cutback. In form — 13 goal involvements in his last 17 internationals. Second penalty/shootout taker.
- **Ruben Vargas (index 8):** fit to start again after the knock that benched him in Vancouver — where he still came on in stoppage time and buried the decisive shootout penalty. Cuts inside onto his right; now third in the shootout order.
- **Dan Ndoye (index 10):** Switzerland's main 1v1 outlet on the right — pace to beat the fullback and reach the byline.
- **Gregor Kobel (index 0):** undisputed No.1 and sweeper-keeper — high starting position (~5m off line) when team has possession in opposition half. Saved from Cucho Hernández in the R16 shootout; a genuine penalty-saving threat.
- **Ricardo Rodríguez (index 1):** primary set-piece taker from the left, overlapping outlet behind Vargas, and experienced fourth shootout taker.
- **Denis Zakaria (index 4):** the converted-midfielder right-back — defends first, tucks inside to make a back three in build-up. CAUTION: booked vs Colombia, one yellow from a semi-final ban — must stay clean while marking the world champions' left side.

## Tournament Mindset
**Quarter-final — Switzerland's first since 1954, against the world champions.** The route here is pure Swiss: top of the group, 2-0 over Algeria in the Round of 32, then 120 goalless minutes and a 4-3 shootout over Colombia — Kobel the wall, Vargas the executioner. Nobody in this side needs reminding that they beat world champions France on penalties at Euro 2020; now they meet world champions Argentina at Arrowhead Stadium with the same blueprint. And Argentina are gettable: they needed extra time against Cape Verde in the Round of 32 and were 2-0 down to Egypt with 11 minutes left before escaping 3-2 — a champion's nerve, but also a defence that keeps letting games open up.

The plan is control through compactness: Xhaka screens, Freuler and Jashari alternate onto Messi the moment he drops between the lines, and the back four stays narrow so De Paul and Mac Allister find no pockets. Xhaka commands the middle third but cannot shackle Messi single-handedly — this is a collective job, done by shape, not by fouling. In possession, strike on the counter through Ndoye's pace, Vargas cutting in, and one moment from Embolo, who arrives in the form of his international career. A clean sheet at 0-0 deep into the night is a good result: Switzerland are entirely comfortable taking the champions to extra time and penalties, where Kobel and a proven taker order (Xhaka, Embolo, Vargas...) just delivered. Two constraints rule everything: no needless bookings — Xhaka and Zakaria are each one yellow from missing a semi-final that is suddenly, genuinely within reach — and no over-commitment chasing the game. Survive, suffocate, strike once.
