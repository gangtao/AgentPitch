# Ghana — Tactical Profile

## Identity & Philosophy
Carlos Queiroz's Ghana is the most direct, transitional side in this cohort. The Portuguese veteran took the job in April 2026 (replacing Otto Addo after the Austria/Germany friendly defeats) with little preparation time, so he leans on a simple, organised 4-3-3 built around what he inherited: a Thomas Partey-anchored midfield and the relentless pace of Iñaki Williams, Antoine Semenyo and Abdul Fatawu. The Black Stars play on the front foot in transition — long carries, sharp through balls, and shots from the break — while staying compact and disciplined out of possession. Ghana arrive without Mohammed Kudus (injured, omitted from the 26) and without Alexander Djiku (also injured), forcing Queiroz to rebuild the spine around Partey, captain Jordan Ayew, and the wide runners. Verticality the instant the ball is won is the whole idea.

## Formation
- Shape: 4-3-3 with a flat back four, a Partey-anchored midfield three, and a pacey, interchangeable front three; full-backs push high in possession.
- Role mapping (roster order in `ghana.yaml`):
  - index 0: GK — **Lawrence Ati-Zigi** — experienced No. 1 reinstated for the opener; commanding shot-stopper (save 15), keeps distribution simple.
  - index 1: LB — **Gideon Mensah** — left-back, attacking, provides all the left-side width and overlaps Semenyo.
  - index 2: LCB — **Abdul Mumin** — left-centre of the back four; calm positional anchor after Djiku's injury withdrawal.
  - index 3: RCB — **Jerome Opoku** — right-centre of the back four, physical aerial presence.
  - index 4: RB — **Alidu Seidu** — right-back, quick and aggressive, recovers and overlaps Fatawu.
  - index 5: LCM/#8 — **Antoine Semenyo** — left of the midfield three but a forward by instinct; drives infield from the left half-space, direct and powerful.
  - index 6: DM/#6 — **Thomas Partey** — single pivot and deep-lying conductor; sets every tempo (pass 16).
  - index 7: RCM/#8 — **Elisha Owusu** — right of the three, ball-winner and tempo-setter who shields the back four.
  - index 8: LW — **Abdul Fatawu** — left of the front three (cuts in off either flank); vertical, direct dribbler, beats his man wide (speed 17, dribbling 16).
  - index 9: CF — **Iñaki Williams** — lone centre-forward, runner-in-behind, focal point of the counter.
  - index 10: RW — **Jordan Ayew** — right of the front three, veteran captain; links play, drifts inside, arrives late in the box.

## Style of Play

### Build-up
- Short when uncontested, but very direct under pressure — Ati-Zigi often launches long to Williams's channel run.
- Partey is the primary first-pass option, dropping between or beside the centre-backs to receive.
- The full-backs Mensah and Seidu push high quickly to stretch the pitch.
- Semenyo or Ayew drops between the lines to receive on the half-turn between the opposition midfield and defence.

### Pressing
- Aggressive but not constant — high-press in coordinated waves rather than 90-minute intensity.
- Trigger: opposition full-back receives near the touchline with limited options.
- Williams presses the CB; Fatawu and Ayew jump the full-backs; Owusu and Semenyo step onto the opposition pivot.
- If the first wave is broken, retreat fast into a 4-5-1 / 4-1-4-1 mid-block.

### Defensive shape
- 4-1-4-1 mid-block: Partey shields the back four, the wide forwards Fatawu and Ayew drop onto the midfield line, Semenyo and Owusu tuck in.
- Partey covers the half-spaces and screens centrally.
- Seidu's and Mensah's speed lets them recover deep then surge again.
- Wide forwards track back to make a flat midfield band when the ball is on the opposite flank.

### Wide play
- Right side: Ayew's intelligence + Seidu's pace create a combinational, overlapping threat.
- Left side: Semenyo's physicality drifting inside + Mensah's overlap form a direct attacking force; Fatawu hugs the touchline.
- Crosses target Williams's near-post run and the far-side forward arriving late.

### Final third
- Williams runs the channels constantly; Ghana plays a lot of long diagonals to him.
- Semenyo cuts inside from the left half-space for shots and drives at defenders 1v1.
- Fatawu attacks the byline and the far post; Ayew links play and arrives late in the box from the right.
- Counter-attacks are 4-5 second sequences: win ball, Partey forward, Williams runs in behind.

## Set Pieces
- Mumin, Opoku, and Williams are the main aerial targets.
- Partey and Jordan Ayew share set-piece duty depending on distance and side; Semenyo and Fatawu are options from direct free-kicks.
- Penalties: Jordan Ayew (captain) is the primary taker, with Semenyo as backup.
- Defensive set pieces: zonal, Partey screens, Mumin/Opoku on the biggest aerial threats.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Ati-Zigi) under pressure: long ball to the CF channel run (player_id ends with "_9", Williams) rather than a risky short pass.
2. If player_id ends with "_6" (Partey, #5; pass 16): face forward, look for the vertical pass into the front three — into the CF run (player_id ends with "_9", Williams) or into Semenyo (player_id ends with "_5") in the left half-space first; only recycle to a centre-back if no lane.
3. If player_id ends with "_5" (Semenyo, #11; skill 16, dribbling 16, shoot 15): when receiving in the left half-space, drive inside onto the right foot — shoot if inside 22m and the angle is open, otherwise combine or feed Williams.
4. If player_id ends with "_9" (Williams, CF #19; speed 17, stamina 17): constantly check the offside line; sprint in behind whenever a midfielder has time to play a through ball.
5. If player_id ends with "_10" (Ayew, RW #9): link play on the right, drift inside to combine, and arrive late in the box for cut-backs.
6. If player_id ends with "_8" (Fatawu, LW #7; speed 17, dribbling 16): receive wide on the touchline, take on the full-back 1v1, get to the byline or cut inside to shoot.
7. If turnover in own half: outlet long to Williams (player_id ends with "_9") if visible; counter through Semenyo (player_id ends with "_5") if not.
8. If defending: 4-1-4-1 mid-block with Partey (player_id ends with "_6") screening the back four — Williams (player_id ends with "_9") stays highest as the counter outlet.
9. If player_id ends with "_1" (Mensah, LB #14) has the ball: overlap Semenyo (player_id ends with "_5") aggressively and cross early to Williams's near-post run.
10. If player_id ends with "_7" (Owusu, MID #8): win the second ball, set the tempo, and recycle quickly to Partey (player_id ends with "_6") or spring the full-backs.
11. If player_id ends with "_4" (Seidu, RB #21): push high on the right and provide overlapping width, especially when Ayew (player_id ends with "_10") tucks inside.
12. If trailing late: push full-backs Mensah (player_id ends with "_1") and Seidu (player_id ends with "_4") to winger heights, Partey (player_id ends with "_6") alone behind, throw extra runners forward.
13. If counter-attack opportunity: maximum 4 passes before a shot or final-third entry; speed over precision.

## Key Player Notes
- **Iñaki Williams (speed 17, stamina 17)** is the running weapon and focal point of the attack; his stamina lets him sprint repeatedly for 90 minutes.
- **Antoine Semenyo (skill 16, dribbling 16, shoot 15)** is the primary creator and scorer threat — with Kudus injured, even more of the creative burden falls on him; encourage him to take on defenders and shoot from the left half-space.
- **Thomas Partey** is the calming presence and the single pivot the whole system rests on — without him, Ghana becomes too transition-dependent.
- **Jordan Ayew** is the captain and tournament intelligence — set-piece and penalty taker, links the front line.
- **Abdul Fatawu** is a pure pace-and-dribble wide threat — a 1v1 weapon against slower full-backs.
- **Lawrence Ati-Zigi** is the experienced No. 1 — solid and unflashy; keep his distribution simple.

## Tournament Mindset
Ghana open Group L against Panama in Toronto on June 17 — a game the Black Stars are quietly expected to win and need to win, given England and Croatia loom as the group's heavyweights. Ghana believes in moments: one Semenyo dribble, one Fatawu run, or one Williams sprint in behind can break Panama's organised low block. Missing Kudus and Djiku, and with Queiroz only weeks into the job, they will lean on individual quality and ruthless transitions rather than control — they prefer chaos to patience once the ball is won, and the opener is the must-win-feel start to a group they fancy escaping.
