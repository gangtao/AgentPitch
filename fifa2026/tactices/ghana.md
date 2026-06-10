# Ghana — Tactical Profile

## Identity & Philosophy
Carlos Queiroz's Ghana is the most direct, transitional side in this African cohort. A disciplined, organised 3-4-2-1 built on a compact back three, a Thomas Partey–Kwasi Sibo double pivot, and the relentless running of Iñaki Williams and Antoine Semenyo. The Black Stars lean hard into pace and quick transitions — long carries, sharp through balls, and shots from anywhere on the break. Queiroz wants control in midfield, wing-backs supplying all the width, and verticality the instant the ball is won.

## Formation
- Shape: 3-4-2-1 with a Partey–Sibo double pivot flanked by wing-backs, two free attackers floating behind a lone, fast center-forward.
- Role mapping (roster index -> tactical role):
  - index 0: GK — **Benjamin Asare** — late-blooming No. 1 who displaced Ati-Zigi; commanding shot-stopper (save 15), keeps distribution simple.
  - index 1: LCB — **Jerome Opoku** — left of the back three, physical.
  - index 2: CCB — **Abdul Mumin** — central of the back three; stepped in after Djiku's injury withdrawal; calm positional anchor.
  - index 3: RCB — **Jonas Adjetey** — right of the back three, mobile and aggressive.
  - index 4: LWB — **Gideon Mensah** — left wing-back, attacking, provides all the left-side width.
  - index 5: CM — **Thomas Partey** — left of the double pivot, deep-lying conductor.
  - index 6: CM — **Kwasi Sibo** — right of the double pivot, ball-winner and tempo-setter.
  - index 7: RWB — **Caleb Yirenkyi** — right wing-back, energetic up-and-down runner.
  - index 8: AM (left) — **Antoine Semenyo** — left of the two behind the striker, direct and powerful.
  - index 9: AM (right) — **Jordan Ayew** — right of the two, veteran captain and intelligence.
  - index 10: CF — **Iñaki Williams** — lone center-forward, runner-in-behind.

## Style of Play

### Build-up
- Short when uncontested, but very direct under pressure — Asare often launches long to Williams.
- Partey is the primary first-pass option; Sibo offers the angle on the other side of the pivot.
- The back three split wide; wing-backs Mensah and Yirenkyi push high quickly.
- Semenyo or Ayew drops between the lines to receive on the half-turn between the opposition midfield and defense.

### Pressing
- Aggressive but not constant — high-press in coordinated waves rather than 90-minute intensity.
- Trigger: opposition full-back receives near touchline with limited options.
- Williams presses the CB; Semenyo and Ayew jump the full-backs; the pivots step onto the opposition pivot.
- If first wave is broken, retreat fast into a 5-4-1 mid-block.

### Defensive shape
- 5-4-1 mid-block: wing-backs drop beside the back three to make a five, Semenyo and Ayew tuck onto the midfield line.
- Partey and Sibo protect the back five narrowly and cover the half-spaces.
- Yirenkyi's speed lets him recover deep then surge again.
- Semenyo and Ayew track back to make a flat midfield band when the ball is on the opposite flank.

### Wide play
- Right side: Ayew's intelligence + Yirenkyi's pace create a combinational, overlapping threat.
- Left side: Semenyo's physicality + Mensah's overlap form a direct 2-man attacking force.
- Crosses target Williams's near-post run and the far-side attacker arriving late.

### Final third
- Williams runs the channels constantly; Ghana plays a lot of long diagonals to him.
- Semenyo cuts inside from the left half-space for shots and drives at defenders 1v1.
- Ayew links play and arrives late in the box from the right.
- Counter-attacks are 4-5 second sequences: win ball, Partey/Sibo forward, Williams runs in behind.

## Set Pieces
- Opoku, Mumin, Adjetey, and Williams are aerial targets.
- Partey and Jordan Ayew share set-piece duty depending on distance and side; Semenyo is an option from direct free-kicks.
- Penalties: Jordan Ayew (captain) is the primary taker, with Semenyo as backup.
- Defensive set pieces: zonal, Partey screens, Opoku/Mumin/Adjetey on the biggest aerial threats.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Asare) under pressure: long ball to the CF channel run (player_id ends with "_10", Williams) rather than risky short pass.
2. If player_id ends with "_5" (Partey, #5): face forward, look for the vertical pass into the feet of the two behind the striker (player_id ends with "_8", Semenyo, or "_9", Ayew) or directly into the CF run (player_id ends with "_10", Williams) first.
3. If player_id ends with "_8" (Semenyo, AM #11; skill 16, dribbling 16, shoot 15): when receiving in the left half-space, drive inside onto the right foot — shoot if inside 22m and angle is open, otherwise combine or feed Williams.
4. If player_id ends with "_10" (Williams, CF #19; speed 17, stamina 17): constantly check the offside line; sprint in behind whenever a midfielder has time to play a through ball.
5. If player_id ends with "_9" (Ayew, AM #9): link play on the right, drift inside to combine, and arrive late in the box for cut-backs.
6. If player_id ends with "_7" (Yirenkyi, RWB #3): push high and provide all the right-side width, especially when Ayew (player_id ends with "_9") tucks inside.
7. If turnover in own half: outlet long to Williams (player_id ends with "_10") if visible; counter through Semenyo (player_id ends with "_8") if not.
8. If defending: 5-4-1 mid-block with the wing-backs dropping into the back line — Williams (player_id ends with "_10") stays highest as the counter outlet.
9. If player_id ends with "_4" (Mensah, LWB #14) has the ball: overlap Semenyo (player_id ends with "_8") aggressively and cross early to Williams's near-post run.
10. If player_id ends with "_6" (Sibo, MID #8): win the second ball, set the tempo, and recycle quickly to Partey (player_id ends with "_5") or spring the wing-backs.
11. If trailing late: push the wing-backs Mensah (player_id ends with "_4") and Yirenkyi (player_id ends with "_7") to winger heights, Partey (player_id ends with "_5") alone behind, throw extra runners forward.
12. If counter-attack opportunity: maximum 4 passes before a shot or final-third entry; speed over precision.

## Key Player Notes
- **Iñaki Williams (speed 17, stamina 17)** is the running weapon and focal point of the attack; his stamina lets him sprint repeatedly for 90 minutes.
- **Antoine Semenyo (skill 16, dribbling 16, shoot 15)** is the primary creator and scorer threat — encourage him to take on defenders and shoot from the left half-space.
- **Thomas Partey** is the calming presence and senior half of the double pivot — without him, the team becomes too transition-dependent.
- **Jordan Ayew** is the captain and tournament intelligence — set-piece and penalty taker, links the front line.
- **Caleb Yirenkyi** is a pace match-up weapon at right wing-back — exploit him against slower left-sided opponents.
- **Benjamin Asare** earned the gloves late in qualifying — solid and unflashy; keep his distribution simple.

## Tournament Mindset
Ghana believes in moments — one Semenyo dribble or one Williams run can break any game open. Under Queiroz they are more disciplined out of possession, but they still prefer chaos to control once the ball is won.
