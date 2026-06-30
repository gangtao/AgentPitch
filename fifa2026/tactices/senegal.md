# Senegal — Tactical Profile

## Identity & Philosophy
The 2022 AFCON champions are the most physical, athletic side left in the tournament. Under Pape Thiaw, Senegal play a high-tempo, transition-led 4-3-3 built on duel-winning, defensive solidity, and lethal pace in behind. They will not chase possession against superior ball-players — they soak pressure, win the second ball, and break at speed through Mané, Sarr and Jackson. The group stage was a scare: beaten by France and Norway, they roared back with a 5-0 demolition of Iraq to sneak through as one of the best third-placed teams. They arrive at the knockouts dangerous, quick, and error-prone enough to keep every game open — a side nobody wanted to draw.

## Round of 32 Lineup (vs Belgium, July 1 — Lumen Field, Seattle, win-or-go-home)
Senegal name their strongest available spine for a do-or-die last-32 tie against a Belgium side that won Group G but remains a misfiring, top-heavy outfit:
- **Mory Diaw** continues in goal — Édouard Mendy is out with a left-knee medial-ligament injury (landed awkwardly claiming a cross vs Norway, Matchday 2). Diaw is less commanding but steady; keep his distribution simple and screen him.
- **Kalidou Koulibaly** captains the back four after rotation in the group decider; his experience and physicality anchor the duel against De Bruyne-fed runners.
- **Midfield three** of Pape Gueye, Idrissa Gueye and Pape Matar Sarr — a ball-winning, high-stamina engine built to flood the half-spaces and counter-press.
- **Front three**: Mané left, Jackson central, Ismaïla Sarr right — pure pace and directness, instructed to attack the channels behind Belgium's full-backs the instant the ball is regained.
- Belgium context: De Bruyne pulls the strings, Doku and Trossard carry the wide threat, Courtois behind a back line that can be turned. Senegal must deny De Bruyne time, win the aerial battles, and punish Belgium's high line in transition. It is open, end-to-end, and Senegal back their athleticism to settle it.

## Formation
- Shape: 4-3-3, compact and physical out of possession, vertical and explosive in transition.
- Role mapping (roster order in `senegal.yaml`):
  - index 0: GK — Mory Diaw (deputising for the injured Mendy; shot-stopper, distributes long to the channels)
  - index 1: LB — El Hadji Malick Diouf (attacking left-back, raw pace, overlaps hard)
  - index 2: LCB — Moussa Niakhaté (mobile cover defender, sweeps behind, wins second balls)
  - index 3: RCB — Kalidou Koulibaly (captain, physical leader, steps out to win duels)
  - index 4: RB — Krépin Diatta (converted winger; surges forward to make 2v1s with Sarr)
  - index 5: LCM/#8 — Pape Gueye (physical left shuttler, progressive carrier, screen in front of the back four)
  - index 6: DM/#6 — Idrissa Gueye (the destroyer; ball-winner and pressing trigger, sits deepest)
  - index 7: RCM/#8 — Pape Matar Sarr (dynamic box-to-box engine, late runs, progressive passer)
  - index 8: LW — Sadio Mané (talisman, inside-forward, drives in onto the right foot)
  - index 9: CF — Nicolas Jackson (runner-in-behind, attacks the channels relentlessly)
  - index 10: RW — Ismaïla Sarr (direct pace and finishing, isolated 1v1 on the right)

## Style of Play

### Build-up
- Short when uncontested, but Diaw (in for the injured Mendy) is encouraged to go long to Jackson's channel run if pressed — he is less assured on the ball, so simplify his options under pressure.
- Koulibaly is the calmest passer — first option from goal kicks.
- Idrissa Gueye drops between center-backs only against high pressure.
- Build-up is short and fast — fewer touches, more vertical; Senegal will gladly cede possession (40-50%) and play on the counter against Belgium.

### Pressing
- Selective high press rather than relentless — Senegal pick their moments and otherwise sit in a compact mid-block to deny De Bruyne the line-splitting pass.
- Trigger: opponent receiving with their back to play, or a heavy touch / loose square pass in the middle third.
- Jackson presses the center-back; Mané and Sarr jump the full-backs; Pape Gueye and Pape Matar Sarr step on the pivot.
- Idrissa Gueye sweeps and hunts second balls. Counter-press immediately if the first wave is broken.

### Defensive shape
- 4-1-4-1 / 4-5-1 mid-block when forced to drop; stay compact and force Belgium wide.
- Koulibaly aggressively steps out to win duels; Niakhaté covers behind, especially against runners in behind from De Bruyne's passes.
- Diatta tucks into midfield as an extra runner; Diouf stays wide on the left and tracks Doku.
- Win the aerial battles — clear long, second balls swept by Idrissa Gueye.

### Wide play
- Mané is the focal point on the left: receive on the touchline, drive inside, shoot or combine with Pape Gueye.
- Diatta surges from right-back to create 2v1s with Sarr.
- Crosses are early and direct — to Jackson's near-post run.

### Final third
- Jackson runs the channels constantly — every transition looks for him in behind first, targeting the space behind Belgium's full-backs.
- Mané takes 1v1s and shoots from the left half-space.
- Sarr is the direct, pacy threat from the right — runs at defenders and finishes early.
- Pape Matar Sarr makes the late box arrival on cutbacks.

## Set Pieces
- Koulibaly and Niakhaté dominate attacking corners — far-post target plus near-post flick.
- Mané takes left-side corners; Diatta or Pape Matar Sarr from the right.
- Mané is the primary penalty taker; Jackson and Ismaïla Sarr are alternates.
- Defensive set pieces: man-marking on the biggest aerial threats, Koulibaly on the most dangerous opponent; guard against Belgium's tall delivery to the back post.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Diaw) and pressed: long ball to the CF (player_id ends with "_9", Jackson) channel run rather than a risky short pass.
2. If player_id ends with "_3" (Koulibaly, RCB #3) and unpressed in own half: step into midfield with the ball; release the #6 (player_id ends with "_6", Idrissa Gueye) or LCM (player_id ends with "_5", Pape Gueye) in space.
3. If player_id ends with "_6" (Idrissa Gueye, MID #5) and opponent receives with back to goal in the middle third: tackle immediately.
4. If player_id ends with "_8" (Mané, LW #10): when receiving on the left wing with space inside, dribble inside onto the right foot and shoot if range is good (<22m).
5. If player_id ends with "_9" (Jackson, CF #11) and ball is with a midfielder facing forward: sprint behind the last defender; demand the through ball into the channel.
6. If player_id ends with "_4" (Diatta, RB #15) and ball is on the right half-space: overlap aggressively to create a 2v1 with Sarr.
7. If turnover anywhere on the field: counter-press for at least 6 seconds before retreating, then break vertically at pace.
8. If defending and the RCB (player_id ends with "_3", Koulibaly) is engaged in a duel: the LCB (player_id ends with "_2", Niakhaté) drops 5m to cover the space behind him.
9. If the RCM (player_id ends with "_7", Pape Matar Sarr) is between lines unmarked: any midfielder should pass forward to him to progress play immediately.
10. If trailing in the second half: Koulibaly (player_id ends with "_3") steps higher, Idrissa Gueye (player_id ends with "_6") becomes a second #8, Niakhaté (player_id ends with "_2") plays as a lone CB with Diouf (player_id ends with "_1") and Diatta (player_id ends with "_4") as wingbacks.
11. If player_id ends with "_10" (Sarr, RW #18) is 1v1 on the right: run at the defender with pace, drive inside or shoot early.
12. If leading: drop into a compact mid-block, deny the central pass, and pick off the over-the-top ball to break with Jackson and Sarr.

## Key Player Notes
- **Mory Diaw** deputises for the injured Édouard Mendy (left-knee medial-ligament strain suffered claiming a cross vs Norway). A solid but less commanding keeper — keep his distribution simple and protect him with a deeper second-ball screen.
- **Mané (skill 17, dribbling 17)** is the senior leader and primary penalty taker — when in doubt, give him the ball on the left and let him decide the game.
- **Ismaïla Sarr** is the most explosive wide threat — isolate him 1v1 on the right and feed him early into space.
- **Koulibaly** is the captain and physical anchor; back him in duels and cover his pace with Niakhaté.
- **Jackson's pace (17)** is the best weapon against Belgium's high line — repeatedly target the channel behind the opposition full-back.
- **Pape Gueye** is the physical left #8 — a screen in front of the back four and a progressive carrier; he shields rather than crashing the box.
- **Pape Matar Sarr** is the dynamic engine — the late runner who arrives on cutbacks and carries the ball through the lines; the most progressive of the midfield three.
- **Idrissa Gueye** is the destroyer; never expect him to drive the team forward, but he wins everything in the middle third.

## Tournament Mindset
Senegal survived a group-stage scare — losses to France and Norway, rescued by a 5-0 rout of Iraq — and reach the last 32 as one of the best third-placed teams. It is one game, win or go home. They are clear underdogs to nobody given their athleticism: against a misfiring Belgium, the plan is to stay compact, deny De Bruyne space, win the duels and aerial battles, and back Mané, Sarr and Jackson to punish the high line on the break. Soak it up, break at speed, and settle it in a single transition moment.
