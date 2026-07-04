# Norway — Tactical Profile

## Identity & Philosophy
Norway under Ståle Solbakken are a vertical, direct attacking side built almost entirely around exploiting the cataclysmic finishing ability of Erling Haaland and the conducting genius of Martin Ødegaard. They are not a possession team — they want the ball moving forward within three passes. Group-stage form was strong: a 4-1 demolition of Iraq (Haaland brace) on Matchday 1 and a 3-2 win over Senegal (Haaland brace again) on Matchday 2 secured qualification early. With a place in the knockouts already booked, Solbakken rested Haaland and rotated heavily for Matchday 3, and a near-second-string Norway lost 4-1 to France — finishing Group I runners-up behind Les Bleus. The defensive backline is less mobile than the front line, which means midfielders must track back diligently — and the Senegal game (two goals conceded, including a 90+3 equaliser threat from Ismaïla Sarr) exposed that the back four can be stretched when the wide forwards do not recover.

## Round of 16 Knockout (vs Brazil, July 5 — MetLife Stadium, East Rutherford NJ)
The biggest test yet. Norway reached the last 16 by beating Ivory Coast 2-1 in the Round of 32 (Haaland the matchwinner), and are rewarded with a heavyweight tie against Brazil. Two forced changes shape the XI: RB **Julian Ryerson remains out** — the thigh injury he picked up against Senegal has kept him sidelined through France and Ivory Coast, and he is close to a return but not risked here — so **Marcus Holmgren Pedersen** (Torino, quick, attacking full-back) starts at right-back. In midfield **Patrick Berg** (Bodø/Glimt) comes in for **Fredrik Aursnes** as the disciplined left-shuttler alongside Berge and Ødegaard. Otherwise the first-choice spine is intact: Nyland in goal, Ajer and Heggem at centre-back, Wolfe at left-back, and the Nusa–Haaland–Sørloth front three ahead of Ødegaard. Brazil bring Vinícius Júnior and elite individual quality but arrive missing several first-choice starters (Raphinha and Paquetá ruled out); Norway must respect their transition threat, keep Berge anchored, and back Haaland to punish any Brazilian defensive lapse. Win or go home — no second leg, no points to manage. Norway will fancy their chances in a shootout because of Haaland from the spot.

## Formation
- Shape: 4-3-3
- Role mapping (roster order in `norway.yaml`):
  - index 0 (`norway_0`, Nyland): GK — traditional shot-stopper; long distribution toward Haaland.
  - index 1 (`norway_1`, Wolfe): LB — energetic, gets forward to support Nusa.
  - index 2 (`norway_2`, Heggem): LCB — strong, front-foot defender, comfortable stepping out with the ball.
  - index 3 (`norway_3`, Ajer): RCB — tall ball-carrier, strides forward when space appears.
  - index 4 (`norway_4`, Pedersen): RB — quick, attacking full-back deputising for the injured Ryerson; overlaps the right wing.
  - index 5 (`norway_5`, Berg): CM left — disciplined, high work-rate shuttler, defensive cover and ball recycling; the press trigger from central midfield.
  - index 6 (`norway_6`, Berge): DM/CM center — anchor, screens the back four, recycles possession.
  - index 7 (`norway_7`, Ødegaard): #8/AM right — primary creator, free role between lines.
  - index 8 (`norway_8`, Nusa): LW — direct dribbler, beats fullbacks 1v1.
  - index 9 (`norway_9`, Haaland): CF — target and runner, gravitational pull on defenders.
  - index 10 (`norway_10`, Sørloth): RW/second striker — powerful, drifts inside, second aerial threat alongside Haaland.

## Style of Play

### Build-up
Short to Berge from the GK, then up to Ødegaard who orchestrates. If the press is intense, Nyland goes long for Haaland to flick on — Nusa and Sørloth chase the second ball. Build phase is intentionally brief: average 3-4 passes before a vertical entry.

### Pressing (block height + trigger)
Mid-block, situational press. Haaland triggers when an opposition CB receives with back to play; the wingers curve their runs to lock out the wide CB. Otherwise the front three drop into a 4-5-1 to protect the central spine. Berg and Berge are responsible for the press's second wave.

### Defensive shape
4-5-1 in deep settled defense, becomes 4-3-3 when ball is in opposition half. Wingers must track fullbacks all the way back — Solbakken demands it because Wolfe and Pedersen cannot defend 1v2.

### Wide play
Asymmetric. Nusa hugs the touchline LW and looks to isolate the opposition RB; Sørloth (RW) drifts inside as a second striker, allowing Pedersen to bomb on. Most attacks funnel down the left.

### Final third
Ødegaard receives between the lines, picks his head up, and threads passes to Haaland (between CBs) or Nusa (in behind LB). Crosses are aimed at Haaland's near-post run, with Sørloth attacking the back post — Norway now have two genuine aerial targets in the box. Long-range shots from Ødegaard are a tertiary option.

## Set Pieces
- Corners: Ødegaard delivers — inswingers from the right toward Haaland (back post), with Ajer and Sørloth attacking the near post.
- Free kicks: Ødegaard takes everything direct; Haaland and Sørloth position for the rebound.
- Penalties: Haaland — always. Sørloth is the designated backup taker.

## decide() Decision Priorities
1. If my player_id ends with "_9" (CF, Haaland, #9): if behind the last CB and the player ending in "_7" (Ødegaard) has the ball, sprint diagonally toward the far post — demand a through-ball.
2. If my player_id ends with "_7" (AM, Ødegaard, #10): scan every tick; if a vertical lane to "_9" (Haaland) exists within passing range (<35m) and Haaland is moving, PASS immediately, not next tick.
3. If my player_id ends with "_0" (GK, Nyland, #1): if opposition press is committed (>=3 players in own third), kick long toward "_9" (Haaland); else short to "_2" (Heggem) or "_6" (Berge).
4. If my player_id ends with "_8" (LW, Nusa, #20): when receiving in left half-space within 25m of goal, DRIBBLE inside toward the box; if double-teamed, lay off to the player ending in "_1" (Wolfe) overlapping.
5. If my player_id ends with "_10" (RW/second striker, Sørloth, #7): when receiving wide right, cut inside and SHOOT if within 22m, OR attack the back post on a Nusa/Ødegaard cross — be the second aerial target alongside Haaland.
6. If my player_id ends with "_6" (DM, Berge, #8): never venture beyond the halfway line in open play unless team is trailing — stay as the defensive anchor.
7. If my player_id ends with "_5" (CM, Berg, #6): when Norway loses the ball in opposition half, immediately TACKLE the nearest opponent (press trigger from CM only).
8. If my player_id ends with "_8" or "_10" (wide forwards, Nusa/Sørloth): on every defensive transition, sprint back to touch the opposition fullback's shadow — non-negotiable.
9. If my player_id ends with "_2" or "_3" (CBs, Heggem/Ajer): if "_9" (Haaland) makes a pinned-CB run, PASS direct over the top (≥40m) rather than rolling it into midfield.
10. If my player_id ends with "_1" (LB, Wolfe): overlap aggressively when "_8" (Nusa) cuts in; only one of ("_1" Wolfe, "_5" Berg) goes forward at a time.
11. If my player_id ends with "_4" (RB, Pedersen): more conservative — only overlap when Norway is trailing or has clear 2v1 numerical advantage on right.
12. If trailing late: the player ending in "_6" (Berge) pushes to CB, the player ending in "_2" (Heggem) goes forward as auxiliary target alongside "_9" Haaland (route-one mode).

## Key Player Notes
- **Erling Haaland (index 9):** the team is calibrated to feed him. He should make 2 runs every attacking phase: one near-post, one in behind. Free shooting license — if within 22m and angle, SHOOT.
- **Martin Ødegaard (index 7, captain):** free role behind Haaland. Allowed to drift to either flank to pick up possession. All set-pieces. Comes into the World Cup off an injury-plagued club season — match-sharpness is the key variable; if he fades, Norway lose their primary creative link and lean harder on route-one service to Haaland/Sørloth.
- **Antonio Nusa (index 8):** primary 1v1 dribbler. Encourage taking on his man — speed 18 wins most foot-races.
- **Sander Berge (index 6):** the disciplined balance to the offensive front. Never out of position.
- **Patrick Berg (index 5):** disciplined, high-stamina shuttler standing in for the injured/rotated Aursnes; covers for Ødegaard's forward bursts, recycles possession under pressure, and leads the press from central midfield.
- **Alexander Sørloth (index 10):** powerful second striker deployed wide-right who drifts inside; a genuine aerial and finishing threat that gives Norway a second focal point alongside Haaland.

## Tournament Mindset
Norway are dangerous in any moment but vulnerable to teams that exploit central midfield gaps when Berg pushes forward. They will trade chances; in a high-scoring shootout they back themselves to outscore anyone because of Haaland — and now carry a second aerial threat in Sørloth. This is the knockouts: a single-leg Round of 16 against Brazil with everything on the line, so the calculus is simply to win. Solbakken sends out his strongest available XI — two forced changes at RB (Pedersen for the injured Ryerson) and in central midfield (Berg for Aursnes) — and goes for it. But the lesson of the Senegal scare and the France rotation defeat is that defensive discipline wins knockouts, and Brazil's individual quality (Vinícius Júnior above all) punishes any loose step from the back four. Expect Norway to attack through Haaland and Ødegaard while keeping Berge anchored, the wide forwards honest in recovery against Brazil's transitions, and a readiness to take the tie to extra time and penalties — where Haaland from the spot is as good a card as anyone holds.
