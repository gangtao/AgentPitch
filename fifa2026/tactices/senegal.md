# Senegal — Tactical Profile

## Identity & Philosophy
The 2022 AFCON champions are the most physical, athletic side in African football. Under Pape Thiaw, Senegal play a high-tempo, direct 4-3-3 built on aggressive pressing, vertical transitions, and brutal duel-winning across every line. Where Morocco controls, Senegal attacks — they want the game played at 100 mph.

## Formation
- Shape: 4-3-3, aggressive and vertical, pressing high.
- Role mapping (roster index -> tactical role):
  - 0 Mendy — Goalkeeper, dominant in the air, distributes long.
  - 1 Diouf — Left-back, attacking, raw pace.
  - 2 Niakhaté — Left center-back, mobile, second-ball winner.
  - 3 Koulibaly — Right center-back, captain, physical leader.
  - 4 Diatta — Right-back, converted winger, surges forward.
  - 5 Pape Gueye — Left #8, physical screen, progressive carrier.
  - 6 Idrissa Gueye — #6, ball-winner, ruthless pressing trigger.
  - 7 Camara — Right #8, dynamic box-to-box shuttler.
  - 8 Mané — Left winger / inside-forward, talisman.
  - 9 Jackson — Center-forward, runner-in-behind.
  - 10 Sarr — Right winger, direct pace and finishing.

## Style of Play

### Build-up
- Short when uncontested, but Mendy is encouraged to go long to Jackson's channel run if pressed.
- Koulibaly is the calmest passer — first option from goal kicks.
- Idrissa Gueye drops between center-backs only against high pressure.
- Build-up is shorter and faster than Morocco's — fewer touches, more vertical.

### Pressing
- High press is the default identity. Trigger: any opponent receiving in their own third with their back to play.
- Jackson presses the center-back; Mané and Sarr press the full-backs; Pape Gueye and Camara step on the pivot.
- Idrissa Gueye sweeps and hunts second balls.
- The press is aggressive enough to risk being broken — counter-press immediately if first wave fails.

### Defensive shape
- 4-1-4-1 if forced to drop, but the team prefers to stay 4-3-3 and press.
- Koulibaly aggressively steps out to win duels in midfield.
- Niakhaté covers behind, especially against runners in behind.
- Diatta tucks into midfield as an extra runner; Diouf stays wide.

### Wide play
- Mané is the focal point: receive on the left touchline, drive inside, shoot or combine with Pape Gueye.
- Diatta surges from right-back to create 2v1s with Sarr.
- Crosses are early and direct — to Jackson's near-post run.

### Final third
- Jackson runs the channels constantly — every transition looks for him in behind first.
- Mané takes 1v1s and shoots from the left half-space.
- Sarr is the direct, pacy threat from the right — runs at defenders and finishes.
- Camara makes the late box arrival on cutbacks.

## Set Pieces
- Koulibaly and Niakhaté dominate attacking corners — far-post target plus near-post flick.
- Mané takes left-side corners; Diatta or Pape Gueye from the right.
- Defensive set pieces: man-marking on the biggest threats, Koulibaly on the most dangerous aerial opponent.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Mendy) and pressed: long ball to the CF (player_id ends with "_9", Jackson) channel run rather than risky short pass.
2. If player_id ends with "_3" (Koulibaly, RCB #3) and unpressed in own half: step into midfield with the ball; release the #6 (player_id ends with "_6", Idrissa Gueye) or LCM (player_id ends with "_5", Pape Gueye) in space.
3. If player_id ends with "_6" (Idrissa Gueye, MID #5) and opponent receives with back to goal in the middle third: tackle immediately.
4. If player_id ends with "_8" (Mané, LW #10): when receiving on the left wing with space inside, dribble inside onto right foot and shoot if range is good (<22m).
5. If player_id ends with "_9" (Jackson, CF #11) and ball is with a midfielder facing forward: sprint behind the last defender; demand the through ball.
6. If player_id ends with "_4" (Diatta, RB #15) and ball is on the right half-space: overlap aggressively.
7. If turnover anywhere on the field: counter-press for at least 6 seconds before retreating.
8. If defending and the RCB (player_id ends with "_3", Koulibaly) is engaged in a duel: the LCB (player_id ends with "_2", Niakhaté) drops 5m to cover the space behind him.
9. If the LCM (player_id ends with "_5", Pape Gueye) is between lines unmarked: any midfielder should pass forward to him to progress play immediately.
10. If trailing in the second half: Koulibaly (player_id ends with "_3") steps higher, Idrissa Gueye (player_id ends with "_6") becomes a second #8, Niakhaté (player_id ends with "_2") plays as a lone CB with Diouf (player_id ends with "_1") and Diatta (player_id ends with "_4") as wingbacks.
11. If player_id ends with "_10" (Sarr, RW #18) is 1v1 on the right: run at the defender with pace, drive inside or shoot early.
12. If leading by 2+: maintain high press but allow opposition to play in own third; pick off the long ball.

## Key Player Notes
- **Mané (skill 17, dribbling 17)** is the senior leader — when in doubt, give him the ball on the left.
- **Koulibaly** is still the defensive talisman; trust him in duels but cover his pace with Niakhaté.
- **Jackson's pace (17)** is best weapon against high lines — repeatedly target the channel behind the opposition full-back.
- **Pape Gueye** is the physical left #8 — a screen in front of the back four and a progressive carrier; he shields rather than crashing the box, leaving the late runs to Camara.
- **Idrissa Gueye** is the destroyer; never expect him to drive the team forward, but he wins everything in the middle third.

## Tournament Mindset
Senegal believes they will out-run and out-physical anyone. They will accept open games and trade chances, confident in Mendy's saves and Mané's moments.
