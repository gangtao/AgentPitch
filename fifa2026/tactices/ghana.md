# Ghana — Tactical Profile

## Identity & Philosophy
Carlos Queiroz's Ghana is the most direct, transitional side in this group. The Portuguese veteran took the job in April 2026 with little preparation time, and the group stage has forced a pragmatic, defence-first shape on him. After a chaotic build-up to Matchday 1 — Thomas Partey was denied a Canadian visa and several first-choice options were unavailable — Ghana set up in a compact, double-pivot **4-2-3-1** and ground out a 1-0 win over Panama through a stoppage-time Caleb Yirenkyi winner. They then frustrated England to a 0-0 draw on Matchday 2. The Black Stars play on the front foot in transition — long carries, sharp through balls, and shots from the break — while staying compact and disciplined out of possession behind two screening midfielders. Verticality the instant the ball is won is the whole idea, and the relentless pace of Semenyo, Fatawu, Sulemana and captain Jordan Ayew is the weapon.

**Matchday 1 (17 June, vs Panama — 1-0 win):** Ghana ground out three points, with first-choice keeper **Lawrence Ati-Zigi withdrawn at half-time with discomfort**; substitute **Benjamin Asare** came on and made three crucial saves to preserve the clean sheet, then Caleb Yirenkyi scored the stoppage-time winner.

**Matchday 2 (23 June, vs England — 0-0 draw, Gillette Stadium):** With **Thomas Partey back** in the double pivot after his visa fiasco and **Asare keeping the gloves**, Ghana shut England out in a disciplined, low-block masterclass — the double pivot screening centrally, the wide forwards tracking back into a flat midfield band, and Ayew leading the line as a lone counter outlet. No goals, no suspensions, and a hugely valuable point banked. The result leaves the group wide open.

**Into Matchday 3 (27 June, vs Croatia, Lincoln Financial Field, Philadelphia):** Ghana sit **2nd in Group L on 4 points (GD +1)**, level with leaders England (+2) and one clear of Croatia (3). The maths is simple and favourable — **a draw guarantees Ghana's progress to the Round of 32**, while Croatia must win. Expect Queiroz to set up to frustrate Modric's Croatia exactly as they did England, then strike in transition. The XI and shape are unchanged from the MD2 draw: Asare in goal, the same back four, Partey–Yirenkyi double pivot, Fatawu/Semenyo/Sulemana behind Ayew.

## Formation
- Shape: 4-2-3-1 with a flat back four, a **double pivot** (Partey + Yirenkyi) shielding the defence, a roaming central #10, two pacey wide forwards, and a lone striker; full-backs push high in possession.
- Role mapping (roster order in `ghana.yaml`):
  - index 0: GK — **Benjamin Asare** — promoted to No. 1 after Ati-Zigi's MD1 injury; brave shot-stopper (save 15), keeps distribution simple.
  - index 1: LB — **Gideon Mensah** — left-back, attacking, provides all the left-side width and overlaps Semenyo.
  - index 2: LCB — **Jonas Adjetey** — left-centre of the back four; young, physical, calm positional anchor.
  - index 3: RCB — **Jerome Opoku** — right-centre of the back four, physical aerial presence.
  - index 4: RB — **Marvin Senaya** — right-back, quick and aggressive, recovers and overlaps Fatawu.
  - index 5: DM/#6 — **Caleb Yirenkyi** — right side of the double pivot, ball-winner and box-arriving runner who scored the MD1 winner.
  - index 6: DM/#6 — **Thomas Partey** — deeper of the two pivots and the deep-lying conductor; sets every tempo (pass 16).
  - index 7: RW — **Abdul Fatawu** — right of the front three; vertical, direct dribbler who beats his man wide or cuts in (speed 17, dribbling 16).
  - index 8: CAM/#10 — **Kamaldeen Sulemana** — central attacking midfielder off the striker; drives at the back line, links the wide runners, shoots from the half-spaces.
  - index 9: LW — **Antoine Semenyo** — left of the front three but a forward by instinct; drives infield from the left half-space, direct and powerful, the primary scorer threat.
  - index 10: CF — **Jordan Ayew** — lone centre-forward and veteran captain; links play, holds for runners, drifts wide and arrives late in the box.

## Style of Play

### Build-up
- Short when uncontested, but very direct under pressure — Asare often launches long into the channels for the wide runners.
- Partey is the primary first-pass option, dropping between or beside the centre-backs to receive; Yirenkyi stays slightly higher.
- The full-backs Mensah and Senaya push high quickly to stretch the pitch.
- Sulemana or Ayew drops between the lines to receive on the half-turn between the opposition midfield and defence.

### Pressing
- Aggressive but not constant — high-press in coordinated waves rather than 90-minute intensity.
- Trigger: opposition full-back receives near the touchline with limited options.
- Ayew presses the CB; Fatawu and Semenyo jump the full-backs; Sulemana steps onto the opposition pivot while Partey and Yirenkyi screen behind.
- If the first wave is broken, retreat fast into a compact 4-4-1-1 / 4-2-3-1 mid-block.

### Defensive shape
- 4-2-3-1 mid-block: Partey and Yirenkyi double-screen the back four, the wide forwards Fatawu and Semenyo drop onto the midfield line, Sulemana tucks in onto the opposition pivot.
- The double pivot covers the half-spaces and screens centrally — this is the security the single-pivot shape lacked.
- Senaya's and Mensah's speed lets them recover deep then surge again.
- Wide forwards track back to make a flat midfield band when the ball is on the opposite flank.

### Wide play
- Right side: Fatawu's pace + Senaya's overlap create a direct, byline-hunting threat.
- Left side: Semenyo's physicality drifting inside + Mensah's overlap form a direct attacking force.
- Crosses target Ayew's near-post run and the far-side forward arriving late.

### Final third
- Ayew runs the channels and holds the ball up; Ghana plays a lot of long diagonals into the wide forwards.
- Semenyo cuts inside from the left half-space for shots and drives at defenders 1v1.
- Fatawu attacks the byline and the far post; Sulemana arrives centrally to shoot or thread the final ball.
- Counter-attacks are 4-5 second sequences: win ball, Partey forward, wide runners sprint in behind.

## Set Pieces
- Adjetey, Opoku, and Ayew are the main aerial targets.
- Partey and Jordan Ayew share set-piece duty depending on distance and side; Semenyo and Fatawu are options from direct free-kicks.
- Penalties: Jordan Ayew (captain) is the primary taker, with Semenyo as backup.
- Defensive set pieces: zonal, Partey and Yirenkyi screen, Adjetey/Opoku on the biggest aerial threats.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Asare) under pressure: long ball into a wide-forward channel run (player_id ends with "_7" Fatawu or "_9" Semenyo) rather than a risky short pass.
2. If player_id ends with "_6" (Partey, #5; pass 16): face forward, look for the vertical pass into the front three — into Sulemana (player_id ends with "_8") or Semenyo (player_id ends with "_9") in the half-spaces first; only recycle to a centre-back or to Yirenkyi (player_id ends with "_5") if no lane.
3. If player_id ends with "_9" (Semenyo, #11; skill 16, dribbling 16, shoot 15): when receiving in the left half-space, drive inside onto the right foot — shoot if inside 22m and the angle is open, otherwise combine or feed Ayew.
4. If player_id ends with "_10" (Ayew, CF #9; captain): hold up and link, drift wide to combine, and arrive late in the box for cut-backs; check the offside line for runs in behind.
5. If player_id ends with "_8" (Sulemana, #10): receive between the lines on the half-turn, drive at the back four, shoot from the edge of the box or slide the final ball to the wide runners.
6. If player_id ends with "_7" (Fatawu, RW #7; speed 17, dribbling 16): receive wide on the touchline, take on the full-back 1v1, get to the byline or cut inside to shoot.
7. If turnover in own half: outlet long to a wide forward (player_id ends with "_7" or "_9") if visible; counter through Sulemana (player_id ends with "_8") if not.
8. If defending: 4-2-3-1 mid-block with Partey (player_id ends with "_6") and Yirenkyi (player_id ends with "_5") double-screening the back four — Ayew (player_id ends with "_10") stays highest as the counter outlet.
9. If player_id ends with "_1" (Mensah, LB #14) has the ball: overlap Semenyo (player_id ends with "_9") aggressively and cross early to Ayew's near-post run.
10. If player_id ends with "_5" (Yirenkyi, DM #3): win the second ball, screen alongside Partey, and either recycle to Partey (player_id ends with "_6") or break forward late into the box.
11. If player_id ends with "_4" (Senaya, RB #26): push high on the right and provide overlapping width, especially when Fatawu (player_id ends with "_7") cuts inside.
12. If trailing late: push full-backs Mensah (player_id ends with "_1") and Senaya (player_id ends with "_4") to winger heights, Partey (player_id ends with "_6") alone behind, throw extra runners forward.
13. If counter-attack opportunity: maximum 4 passes before a shot or final-third entry; speed over precision.

## Key Player Notes
- **Antoine Semenyo (skill 16, dribbling 16, shoot 15)** is the primary creator and scorer threat — with Kudus out, the bulk of the creative burden falls on him; encourage him to take on defenders and shoot from the left half-space.
- **Thomas Partey** returns from the MD1 visa fiasco as the calming presence the system rests on; the double pivot with Yirenkyi is far more secure than a lone screen.
- **Caleb Yirenkyi** is the energetic ball-winner who arrives in the box — he scored Ghana's stoppage-time MD1 winner; pairs with Partey to shield the back four.
- **Abdul Fatawu** is a pure pace-and-dribble wide threat — a 1v1 weapon against slower full-backs (speed 17).
- **Kamaldeen Sulemana** is the dynamic #10 — direct, two-footed, drives at defenders and connects the wide runners.
- **Jordan Ayew** is the captain and tournament intelligence — set-piece and penalty taker, leads the line and links the front four.
- **Benjamin Asare** is the brave stand-in No. 1 after Ati-Zigi's injury — earned trust with three big MD1 saves; keep his distribution simple.

## Tournament Mindset
Ghana beat Panama 1-0 and held England 0-0, banking four points from two games, and arrive at the Matchday 3 decider against Croatia in Philadelphia **needing only a draw to reach the Round of 32**. Croatia (3 points) must win, so the onus to chase is on Modric's side — and that suits Queiroz perfectly. The Black Stars will set up to frustrate and strike: a compact double pivot, disciplined wide forwards dropping into a flat midfield band, and ruthless transitions when Partey wins it and the pace breaks free. Ghana believes in moments — one Semenyo dribble, one Fatawu run, one Sulemana drive — to puncture a stronger, more possession-heavy side. With Partey settled and Asare proven, they will absorb pressure, deny Croatia space between the lines, and trust their pace on the counter to either win it or hold the point that books their place in the knockouts.
