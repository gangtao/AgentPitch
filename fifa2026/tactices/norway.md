# Norway — Tactical Profile

## Identity & Philosophy
Norway under Ståle Solbakken are a vertical, direct attacking side built almost entirely around exploiting the cataclysmic finishing ability of Erling Haaland and the conducting genius of Martin Ødegaard. They are not a possession team — they want the ball moving forward within three passes. The defensive backline is less mobile than the front line, which means midfielders must track back diligently; when the wide forwards do not recover, the back four can be stretched.

**Group stage (Group I): runners-up.** A 4-1 demolition of Iraq (Haaland brace) on Matchday 1 and a 3-2 win over Senegal (Haaland brace again) secured qualification early — though Senegal's late rally exposed how the back four suffers when the wingers stop tracking. With the knockouts booked, Solbakken rested Haaland and rotated heavily on Matchday 3, and a near-second-string Norway lost 4-1 to France, finishing behind Les Bleus.

**Round of 32 — Ivory Coast beaten 2-1**, Haaland the matchwinner.

**Round of 16 — Brazil 1-2 Norway (Sun 5 Jul, MetLife Stadium, East Rutherford NJ) — the night that changed everything.** Norway had never lost to Brazil in senior men's football, and they still haven't. Nyland saved an early Bruno Guimarães penalty to keep it level, and with the front three misfiring Solbakken made the bravest call of his career: **Nusa and Sørloth off at half-time, Oscar Bobb and Andreas Schjelderup on** — and Schjelderup set up both goals. Haaland powered a header past Alisson from Schjelderup's pinpoint cross in the 79th, then collected Schjelderup's lay-off just outside the box in the 90th and arrowed an unstoppable shot into the bottom corner. Neymar's 90+10 penalty was mere consolation. Haaland's sixth and seventh goals of the tournament put him level with Mbappé and Messi in the Golden Boot race — he has now scored in his last 14 Norway appearances. **Norway are in a World Cup quarter-final for the first time in their history.**

**Quarter-final — England (Sat 11 Jul, Hard Rock Stadium, Miami).** Team news is good: **Julian Ryerson**, back from the thigh injury that cost him the France, Ivory Coast and (from the start) Brazil games, returned in the Brazil win and keeps right-back — Pedersen drops to the bench. **David Møller Wolfe** came off late against Brazil with a knock but has resumed full training and starts. **No Norway player is suspended**, but **Antonio Nusa is one booking from missing a semi-final** — the QF is the last round in which yellows accumulate, and Norway are the least-booked side left. The selection debate is up front: Bobb and Schjelderup changed the Brazil game and push hard, but Solbakken is expected to restore his first-choice **Nusa–Haaland–Sørloth** front three and hold the game-changers in reserve. Probable XI (4-3-3): **Nyland; Wolfe, Heggem, Ajer, Ryerson; Berg, Berge, Ødegaard; Nusa, Haaland, Sørloth.**

## Formation
- Shape: 4-3-3 (shifts toward 4-2-3-1 in possession to pair Haaland and Sørloth centrally)
- Role mapping (roster order in `norway.yaml`):
  - index 0 (`norway_0`, Nyland): GK — traditional shot-stopper; penalty-saving hero vs Brazil; long distribution toward Haaland.
  - index 1 (`norway_1`, Wolfe): LB — energetic, gets forward to support Nusa; shook off a knock from the Brazil game.
  - index 2 (`norway_2`, Heggem): LCB — strong, front-foot defender, comfortable stepping out with the ball.
  - index 3 (`norway_3`, Ajer): RCB — tall ball-carrier, strides forward when space appears; his cross nearly found Haaland before the opener vs Brazil.
  - index 4 (`norway_4`, Ryerson): RB — back from his thigh injury; aggressive, tireless Dortmund full-back, more defensively secure than the deputising Pedersen and vital against Gordon/Saka.
  - index 5 (`norway_5`, Berg): CM left — disciplined, high work-rate shuttler, defensive cover and ball recycling; the press trigger from central midfield.
  - index 6 (`norway_6`, Berge): DM/CM center — anchor, screens the back four, recycles possession.
  - index 7 (`norway_7`, Ødegaard): #8/AM right — primary creator, free role between lines.
  - index 8 (`norway_8`, Nusa): LW — direct dribbler, beats fullbacks 1v1. CAUTION: one yellow from a semi-final ban.
  - index 9 (`norway_9`, Haaland): CF — target and runner, gravitational pull on defenders; 7 goals, joint Golden Boot leader.
  - index 10 (`norway_10`, Sørloth): RW/second striker — powerful, drifts inside, second aerial threat alongside Haaland.
  - bench impact: **Andreas Schjelderup** (assisted both goals vs Brazil — the half-time change that beat the Seleção; takes the `_8` slot when on) and **Oscar Bobb** (silky right-sided dribbler, the `_10` slot) are proven game-changers; Marcus Holmgren Pedersen covers the `_4` slot, Fredrik Aursnes the `_5`.

## Style of Play

### Build-up
Short to Berge from the GK, then up to Ødegaard who orchestrates. If the press is intense, Nyland goes long for Haaland to flick on — Nusa and Sørloth chase the second ball. Build phase is intentionally brief: average 3-4 passes before a vertical entry.

### Pressing (block height + trigger)
Mid-block, situational press. Haaland triggers when an opposition CB receives with back to play; the wingers curve their runs to lock out the wide CB. Otherwise the front three drop into a 4-5-1 to protect the central spine. Berg and Berge are responsible for the press's second wave.

### Defensive shape
4-5-1 in deep settled defense, becomes 4-3-3 when ball is in opposition half. Wingers must track fullbacks all the way back — Solbakken demands it because Wolfe and Ryerson cannot defend 1v2 against England's overlaps.

### Wide play
Asymmetric. Nusa hugs the touchline LW and looks to isolate the opposition RB; Sørloth (RW) drifts inside as a second striker, allowing Ryerson to push on. Most attacks funnel down the left.

### Final third
Ødegaard receives between the lines, picks his head up, and threads passes to Haaland (between CBs) or Nusa (in behind LB). Crosses are aimed at Haaland's near-post run, with Sørloth attacking the back post — Norway have two genuine aerial targets in the box. The Brazil winner showed the alternative: a lay-off to Haaland at the edge of the area for the first-time strike. Long-range shots from Ødegaard are a tertiary option.

## Set Pieces
- Corners: Ødegaard delivers — inswingers from the right toward Haaland (back post), with Ajer and Sørloth attacking the near post.
- Free kicks: Ødegaard takes everything direct; Haaland and Sørloth position for the rebound.
- Penalties: Haaland — always (penalty 19). Sørloth is the designated backup taker.
- Shootout order (single-leg knockout — this is live): 1. Haaland, 2. Sørloth, 3. Ødegaard, 4. Berge, 5. Nusa. Nyland saved a penalty vs Brazil — he is a real shootout weapon.

## decide() Decision Priorities
1. If my player_id ends with "_9" (CF, Haaland, #9): if behind the last CB and the player ending in "_7" (Ødegaard) has the ball, sprint diagonally toward the far post — demand a through-ball.
2. If my player_id ends with "_7" (AM, Ødegaard, #10): scan every tick; if a vertical lane to "_9" (Haaland) exists within passing range (<35m) and Haaland is moving, PASS immediately, not next tick.
3. If my player_id ends with "_0" (GK, Nyland, #1): if opposition press is committed (>=3 players in own third), kick long toward "_9" (Haaland); else short to "_2" (Heggem) or "_6" (Berge).
4. If my player_id ends with "_8" (LW, Nusa, #20): when receiving in left half-space within 25m of goal, DRIBBLE inside toward the box; if double-teamed, lay off to the player ending in "_1" (Wolfe) overlapping. Do NOT make reckless tackles — one more yellow means missing the semi-final.
5. If my player_id ends with "_10" (RW/second striker, Sørloth, #7): when receiving wide right, cut inside and SHOOT if within 22m, OR attack the back post on a Nusa/Ødegaard cross — be the second aerial target alongside Haaland.
6. If my player_id ends with "_6" (DM, Berge, #8): never venture beyond the halfway line in open play unless team is trailing — stay as the defensive anchor; screen the lane to England's #10 (Bellingham).
7. If my player_id ends with "_5" (CM, Berg, #6): when Norway loses the ball in opposition half, immediately TACKLE the nearest opponent (press trigger from CM only).
8. If my player_id ends with "_8" or "_10" (wide forwards, Nusa/Sørloth): on every defensive transition, sprint back to touch the opposition fullback's shadow — non-negotiable.
9. If my player_id ends with "_2" or "_3" (CBs, Heggem/Ajer): if "_9" (Haaland) makes a pinned-CB run, PASS direct over the top (≥40m) rather than rolling it into midfield.
10. If my player_id ends with "_1" (LB, Wolfe): overlap aggressively when "_8" (Nusa) cuts in; only one of ("_1" Wolfe, "_5" Berg) goes forward at a time.
11. If my player_id ends with "_4" (RB, Ryerson): stay conservative — England attack down my side through Gordon with O'Reilly overlapping; only push on when Norway is trailing or has a clear 2v1 on the right.
12. If trailing late: the player ending in "_6" (Berge) pushes to CB, the player ending in "_2" (Heggem) goes forward as auxiliary target alongside "_9" Haaland (route-one mode).

## Key Player Notes
- **Erling Haaland (index 9):** the team is calibrated to feed him. Seven goals — joint Golden Boot leader with Mbappé and Messi — a 39% conversion rate, and a scoring streak of 14 straight Norway appearances. He should make 2 runs every attacking phase: one near-post, one in behind. Free shooting license — if within 22m and angle, SHOOT (the Brazil winner came from exactly there).
- **Martin Ødegaard (index 7, captain):** free role behind Haaland. Allowed to drift to either flank to pick up possession. All set-pieces. The creative link has sharpened round by round after his injury-plagued club season; if he fades, Norway lean harder on route-one service to Haaland/Sørloth.
- **Antonio Nusa (index 8):** primary 1v1 dribbler. Encourage taking on his man — speed 18 wins most foot-races. Subbed at half-time vs Brazil and one booking from a semi-final suspension: stay on his feet in duels.
- **Sander Berge (index 6):** the disciplined balance to the offensive front. Never out of position; his duel with Bellingham's arrivals decides the middle of the pitch.
- **Patrick Berg (index 5):** disciplined, high-stamina shuttler keeping Aursnes out of the side; covers for Ødegaard's forward bursts, recycles possession under pressure, and leads the press from central midfield.
- **Alexander Sørloth (index 10):** powerful second striker deployed wide-right who drifts inside; a genuine aerial and finishing threat that gives Norway a second focal point alongside Haaland. Under pressure for his shirt after the Brazil half-time hook.
- **Julian Ryerson (index 4):** restored at right-back after the thigh injury that kept him out since the Senegal game. Tireless (stamina 17), stronger defensively than Pedersen — picked specifically to handle Gordon/Saka 1v1.
- **Andreas Schjelderup / Oscar Bobb (bench, `_8`/`_10` when on):** the half-time substitutes who beat Brazil — Schjelderup assisted both Haaland goals. Solbakken now holds a proven Plan B: if the first-choice wide pair misfires for 45 minutes, the change comes early and without sentiment.
- **Ørjan Nyland (index 0):** saved Bruno Guimarães's penalty vs Brazil; a shootout weapon.

## Tournament Mindset
**Quarter-final — the first in Norway's history, and they arrive as the form story of the tournament.** The road: Group I runners-up (4-1 Iraq, 3-2 Senegal, 1-4 France with the reserves), 2-1 over Ivory Coast in the Round of 32, and the 2-1 felling of Brazil in the Round of 16 — Nyland's penalty save, Solbakken's double half-time substitution, Schjelderup's two assists, Haaland's two late goals. The record vs Brazil stays unbeaten; the belief is total.

The opponent is **England** at Hard Rock Stadium in Miami — beaten finalists' pedigree, but arriving rattled. They needed to survive the final 36-plus minutes with ten men to beat Mexico 3-2 in the Round of 16 after **Jarell Quansah's straight red card — he is suspended for this match**, forcing a back-line reshuffle. Their expected 4-2-3-1 (Pickford; Spence, Konsa, Guehi, O'Reilly; Anderson, Rice; Saka, Bellingham, Gordon; Kane) carries elite talent, and the headline duel writes itself: **Haaland (7 goals) vs Kane (6)**. But England are the most-booked side left — Bellingham, Rice, Guehi and O'Reilly are all one yellow from missing a semi-final — while Norway are the least-booked, with only Nusa at risk. Provoke duels, draw fouls, and let Ødegaard punish the dead balls.

The plan is unchanged because it just beat Brazil: mid-block discipline, Berge screening Bellingham's lane, the wide forwards tracking England's overlapping full-backs, and three-pass verticality toward Haaland the moment the ball turns over. Ryerson's return steadies the right side against Gordon; Wolfe is fit after his knock. And Solbakken now carries the Brazil lesson in his pocket — if Nusa and Sørloth misfire, Bobb and Schjelderup enter at the break without sentiment. If it goes the distance, Norway hold two cards: Haaland from the spot, and Nyland's penalty-saving form. Win, and a first-ever semi-final awaits. No fear — Brazil already fell.
