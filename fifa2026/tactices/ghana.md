# Ghana — Tactical Profile

## Identity & Philosophy
Otto Addo's Ghana is the most direct, transitional side in this African cohort. A 4-2-3-1 built around the dazzling creativity of Mohammed Kudus and the relentless running of Iñaki Williams, the Black Stars want to play on the break — long carries, sharp through balls, and shots from anywhere. Partey anchors a double pivot that gives Kudus license to roam.

## Formation
- Shape: 4-2-3-1 with a clear #10 (Kudus) and a target-runner CF.
- Role mapping (roster index -> tactical role):
  - 0 Asare — Goalkeeper, modest distributor.
  - 1 Gideon Mensah — Left-back, attacking.
  - 2 Djiku — Left center-back, mobile.
  - 3 Opoku — Right center-back, physical.
  - 4 Lamptey — Right-back, pacey overlapper.
  - 5 Partey — Defensive midfielder, deep-lying conductor.
  - 6 Owusu — Partey's pivot partner, energetic shuttler.
  - 7 Jordan Ayew — Left winger, veteran intelligence.
  - 8 Kudus — #10, creative free-roaming talisman.
  - 9 Semenyo — Right winger, direct and powerful.
  - 10 Iñaki Williams — Center-forward, runner-in-behind.

## Style of Play

### Build-up
- Short when uncontested, but very direct under pressure — Asare often launches long to Iñaki.
- Partey is the primary first-pass option; Owusu stays alongside him.
- Center-backs split wide; full-backs push high quickly.
- Kudus drops between lines to receive on the half-turn.

### Pressing
- Aggressive but not constant — high-press in coordinated waves rather than 90-minute intensity.
- Trigger: opposition full-back receives near touchline with limited options.
- Williams presses the CB; Semenyo and Ayew jump the full-backs; Kudus harasses the pivot.
- If first wave is broken, retreat fast into 4-4-1-1.

### Defensive shape
- 4-4-1-1 mid-block: Kudus stays slightly higher to be ready for counters.
- Partey and Owusu protect the back four narrowly.
- Lamptey's speed lets him recover deep then surge again.
- Wide midfielders Semenyo and Ayew tuck inside when ball is on the opposite flank.

### Wide play
- Right side: Semenyo's physicality + Lamptey's pace create a 2-man attacking force.
- Left side: Ayew is more central and combinational; Mensah provides width.
- Crosses target Williams's near-post run and Kudus arriving late.

### Final third
- Kudus is given total freedom — he can dribble, shoot, or pass.
- Williams runs the channels constantly; Ghana plays a lot of long diagonals to him.
- Semenyo cuts inside from the right for shots.
- Counter-attacks are 4-5 second sequences: win ball, Partey/Kudus forward, Williams runs in behind.

## Set Pieces
- Djiku, Opoku, and Williams are aerial targets.
- Partey and Kudus share set-piece duty depending on distance and side.
- Defensive set pieces: zonal, Partey screens, Djiku on the biggest aerial threat.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Asare) under pressure: long ball to the CF channel run (player_id ends with "_10", Williams) rather than risky short pass.
2. If player_id ends with "_5" (Partey, #6 #4): face forward, look for the vertical pass to the #10 (player_id ends with "_8", Kudus) first, then the CF run (player_id ends with "_10", Williams).
3. If player_id ends with "_8" (Kudus, #10 #20; skill 17, dribbling 17, pass 16, shoot 16): in possession in the final third, take a touch and assess — dribble if 1v1, shoot if inside 22m and angle is open, pass to Williams (player_id ends with "_10") if he's running in behind.
4. If player_id ends with "_10" (Williams, CF #11): constantly check the offside line; sprint in behind whenever a midfielder has time to play a through ball.
5. If player_id ends with "_9" (Semenyo, RW #21): when receiving on the right wing, drive inside onto left foot, shoot or combine.
6. If player_id ends with "_4" (Lamptey, RB #2; speed 17): overlap aggressively, especially when Semenyo (player_id ends with "_9") cuts inside.
7. If turnover in own half: outlet long to Williams (player_id ends with "_10") if visible; counter through Kudus (player_id ends with "_8") if not.
8. If defending: 4-4-1-1 shape with Kudus (player_id ends with "_8") as the counter outlet — do not ask Kudus to track full-backs deep.
9. If player_id ends with "_6" (Owusu, MID #19) has the ball in midfield: vertical pass to Kudus (player_id ends with "_8") first, lateral pass to Partey (player_id ends with "_5") if not on.
10. If player_id ends with "_7" (Ayew, LW #10): when out of possession, tuck inside to form a 4-4-1-1; in possession, combine in the left half-space.
11. If trailing late: push the full-backs Mensah (player_id ends with "_1") and Lamptey (player_id ends with "_4") to wingback heights, Partey (player_id ends with "_5") alone behind, throw extra runners forward.
12. If counter-attack opportunity: maximum 4 passes before a shot or final-third entry; speed over precision.

## Key Player Notes
- **Kudus (skill 17, dribbling 17)** is the entire creative output — every attack runs through him. Give him license to drift anywhere across the front line.
- **Iñaki Williams (speed 17, stamina 17)** is the running weapon; his stamina lets him sprint repeatedly for 90 minutes.
- **Partey** is the calming presence — without him, the team becomes too transition-dependent.
- **Semenyo** is the secondary scorer threat; encourage shots from the right half-space.
- **Lamptey** is a pace match-up nightmare — exploit him against slower left-sided opponents.

## Tournament Mindset
Ghana believes in moments — one Kudus dribble or one Williams run can break any game open. They prefer chaos to control.
