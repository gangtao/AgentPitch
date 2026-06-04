# Ghana — Tactical Profile

## Identity & Philosophy
Carlos Queiroz's Ghana is the most direct, transitional side in this African cohort. A disciplined, organised 4-3-3 built on a compact back four, a Thomas Partey anchor, and the relentless running of Iñaki Williams and Antoine Semenyo. With talisman Mohammed Kudus ruled out injured, the Black Stars lean harder than ever into pace and quick transitions — long carries, sharp through balls, and shots from anywhere on the break. Queiroz wants control in midfield and verticality the instant the ball is won.

## Formation
- Shape: 4-3-3 with a single pivot (Partey) and two energetic eights, fronted by a fast, direct front three.
- Role mapping (roster index -> tactical role):
  - 0 Ati-Zigi — Goalkeeper, composed distributor.
  - 1 Gideon Mensah — Left-back, attacking.
  - 2 Opoku — Left center-back, physical.
  - 3 Adjetey — Right center-back, mobile and aggressive.
  - 4 Senaya — Right-back, pacey overlapper.
  - 5 Partey — Defensive midfielder / single pivot, deep-lying conductor.
  - 6 Owusu — Left central midfielder, energetic box-to-box shuttler.
  - 7 Sibo — Right central midfielder, ball-winner and tempo-setter.
  - 8 Semenyo — Left winger / forward, direct and powerful.
  - 9 Iñaki Williams — Center-forward, runner-in-behind.
  - 10 Jordan Ayew — Right winger, veteran captain and intelligence.

## Style of Play

### Build-up
- Short when uncontested, but very direct under pressure — Ati-Zigi often launches long to Williams.
- Partey is the primary first-pass option; Owusu and Sibo offer angles either side of him.
- Center-backs split wide; full-backs push high quickly.
- One of the eights (usually Owusu) breaks the lines to receive on the half-turn between the opposition midfield and defense.

### Pressing
- Aggressive but not constant — high-press in coordinated waves rather than 90-minute intensity.
- Trigger: opposition full-back receives near touchline with limited options.
- Williams presses the CB; Semenyo and Ayew jump the full-backs; the eights step onto the opposition pivot.
- If first wave is broken, retreat fast into a 4-5-1 / 4-3-3 mid-block.

### Defensive shape
- 4-5-1 mid-block: front three drop to screen, eights tuck in beside Partey.
- Partey protects the back four narrowly; Owusu and Sibo cover the half-spaces.
- Senaya's speed lets him recover deep then surge again.
- Wide forwards Semenyo and Ayew track back to make a flat midfield band when the ball is on the opposite flank.

### Wide play
- Right side: Ayew's intelligence + Senaya's pace create a combinational, overlapping threat.
- Left side: Semenyo's physicality + Mensah's overlap form a direct 2-man attacking force.
- Crosses target Williams's near-post run and the far-side winger arriving late.

### Final third
- Williams runs the channels constantly; Ghana plays a lot of long diagonals to him.
- Semenyo cuts inside from the left for shots and drives at defenders 1v1.
- Ayew links play and arrives late in the box from the right.
- Counter-attacks are 4-5 second sequences: win ball, Partey/Owusu forward, Williams runs in behind.

## Set Pieces
- Opoku, Adjetey, and Williams are aerial targets.
- Partey and Jordan Ayew share set-piece duty depending on distance and side; Semenyo is an option from direct free-kicks.
- Penalties: Jordan Ayew (captain) is the primary taker, with Semenyo as backup.
- Defensive set pieces: zonal, Partey screens, Opoku/Adjetey on the biggest aerial threats.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Ati-Zigi) under pressure: long ball to the CF channel run (player_id ends with "_9", Williams) rather than risky short pass.
2. If player_id ends with "_5" (Partey, #5): face forward, look for the vertical pass to an advancing eight (player_id ends with "_6", Owusu) or directly into the CF run (player_id ends with "_9", Williams) first.
3. If player_id ends with "_8" (Semenyo, LW #11; skill 16, dribbling 16, shoot 15): when receiving on the left wing, drive inside onto the right foot — shoot if inside 22m and angle is open, otherwise combine or feed Williams.
4. If player_id ends with "_9" (Williams, CF #19; speed 17, stamina 17): constantly check the offside line; sprint in behind whenever a midfielder has time to play a through ball.
5. If player_id ends with "_10" (Ayew, RW #9): link play on the right, drive inside to combine, and arrive late in the box for cut-backs.
6. If player_id ends with "_4" (Senaya, RB #26): overlap aggressively, especially when Ayew (player_id ends with "_10") tucks inside.
7. If turnover in own half: outlet long to Williams (player_id ends with "_9") if visible; counter through Semenyo (player_id ends with "_8") if not.
8. If defending: 4-5-1 / 4-3-3 mid-block with the front three dropping to screen — Williams (player_id ends with "_9") stays highest as the counter outlet.
9. If player_id ends with "_6" (Owusu, MID #15) has the ball in midfield: vertical pass into the front three first (Williams "_9" or Semenyo "_8"), lateral pass to Partey (player_id ends with "_5") if not on.
10. If player_id ends with "_7" (Sibo, MID #8): win the second ball, set the tempo, and recycle quickly to Partey (player_id ends with "_5") or spring the wide forwards.
11. If trailing late: push the full-backs Mensah (player_id ends with "_1") and Senaya (player_id ends with "_4") to wingback heights, Partey (player_id ends with "_5") alone behind, throw extra runners forward.
12. If counter-attack opportunity: maximum 4 passes before a shot or final-third entry; speed over precision.

## Key Player Notes
- **Iñaki Williams (speed 17, stamina 17)** is the running weapon and focal point of the attack; his stamina lets him sprint repeatedly for 90 minutes.
- **Antoine Semenyo (skill 16, dribbling 16, shoot 15)** is the primary creator and scorer threat with Kudus out — encourage him to take on defenders and shoot from the left half-space.
- **Thomas Partey** is the calming presence and lone pivot — without him, the team becomes too transition-dependent.
- **Jordan Ayew** is the captain and tournament intelligence — set-piece and penalty taker, links the front line.
- **Marvin Senaya** is a pace match-up nightmare — exploit him against slower left-sided opponents.

## Tournament Mindset
Ghana believes in moments — one Semenyo dribble or one Williams run can break any game open. Under Queiroz they are more disciplined out of possession, but they still prefer chaos to control once the ball is won.
