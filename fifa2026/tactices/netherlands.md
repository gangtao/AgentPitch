# Netherlands — Tactical Profile

## Identity & Philosophy
Ronald Koeman's Netherlands is modern Total Football: positional, vertical, and built on technical CBs and a creative midfield. Possession is purposeful — not for its own sake but to verticalize through Frenkie de Jong and reach Gakpo / Malen in the final third. The team is comfortable with risk: high line, aggressive overlaps, asymmetric width. Recent results: Euro 2024 semifinal, strong qualifying campaign — Dutch football confidence is back. **Matchday 1 (June 14, 2026): Netherlands 2-2 Japan** — Van Dijk (51') and Summerville (64') gave the Oranje a 2-1 lead, but Japan equalised twice (Nakamura at 57', then Kamada off an Ito corner at 88'). A disappointing draw that exposed the high line's fragility on transitions and a soft second goal conceded at a set piece. **Matchday 2 (June 20, 2026): Netherlands 1-1 Sweden (sim)** — Gakpo struck but the Oranje were pegged back and dropped two more points, leaving qualification still open going into the final group game. With Xavi Simons ruled out for the tournament (ruptured ACL) and Jeremie Frimpong omitted, and with **Memphis Depay** still working back from a thigh problem (unavailable), Koeman has reverted to his preferred **4-3-3**: a de Jong–Reijnders–Gravenberch midfield three, Gakpo and Malen flanking **Brian Brobbey**, who keeps the No.9 shirt. Crysencio Summerville (who carried a head knock) drops to the bench, and the back four is settled — van de Ven at left-back, Van Hecke alongside Van Dijk, Dumfries overlapping on the right.

## Formation
- Shape: 4-3-3 (de Jong + Reijnders + Gravenberch midfield three; Brobbey leads, Gakpo & Malen wide)
- Role mapping (roster order in `netherlands.yaml`):
  - index 0: GK — Bart Verbruggen (ball-playing keeper; pass 16)
  - index 1: LB — Micky van de Ven (converted CB → LB; recovery pace 19 — covers the high line from the left; conservative going forward)
  - index 2: LCB — Virgil van Dijk (captain; strength 19, discipline 19 — the standard at CB)
  - index 3: RCB — Jan Paul van Hecke (front-foot Brighton stopper; calm distribution, pass 15; preferred over Aké)
  - index 4: RB — Denzel Dumfries (overlapping bomber; stamina 18, speed 17 — relentless up the right)
  - index 5: LCM — Frenkie de Jong (left of the midfield three; pass 18, dribble 18 — the deep playmaker who drops to build)
  - index 6: CM/#8 — Tijjani Reijnders (central runner of the three; late box arrivals; pass 17, stamina 18)
  - index 7: RCM — Ryan Gravenberch (right of the three; powerful two-way carrier; stamina 18 — covers behind Dumfries)
  - index 8: LW — Cody Gakpo (left winger / inside-forward hybrid; shoot 17)
  - index 9: ST — Brian Brobbey (physical No.9; strength 17, shoot 16 — holds, occupies CBs and finishes inside the box)
  - index 10: RW — Donyell Malen (speed 18; from the right cuts in and runs the channel — a sprinter, not a touchline winger)

## Style of Play

### Build-up
- Verbruggen short to Van Dijk or Van Hecke. Frenkie de Jong drops to the left of the CBs or beside them (forming a 3-build); Gravenberch and Reijnders stagger ahead.
- Dumfries pushes high; van de Ven stays slightly deeper as a balancer (he is a converted CB).
- Reijnders offers the between-lines option as the most advanced of the three, drifting across both half-spaces.
- Tempo: medium-high. Netherlands is willing to verticalize when the lane opens — not pure tiki-taka.

### Pressing
- Coordinated mid-to-high block. Brobbey leads, presses CB; Gakpo cuts the back-pass option; Reijnders jumps the opposition #6.
- Aggressive when ball is on the opponent's flank: Dumfries jumps the LB high; CBs slide.
- Counter-press: 4-second rule near the opponent's box.

### Defensive shape
- 4-3-3 → 4-1-4-1 / 4-3-3 mid-block. de Jong and Gravenberch sit deeper as the screen; Reijnders shuttles forward to press.
- High line — Van Dijk is the offside-trap conductor; CBs step in sync; van de Ven's pace sweeps behind from LB.
- Wingers (Gakpo, Malen) drop to wide-mid heights; Brobbey shadows the deepest opposition pivot.

### Wide play
- Asymmetric:
  - **LEFT**: Gakpo holds width on the touchline; van de Ven tucks inside or stays deep; de Jong / Reijnders underlap from the left half-space.
  - **RIGHT**: Malen and Dumfries combine — Malen drifts inside off the right onto his runs, Dumfries overlaps outside; Gravenberch covers the space behind.
- Crosses from Dumfries → Brobbey/Gakpo arriving in the box is a Dutch signature.

### Final third
- Patterns:
  1. **de Jong line-break pass** — through the lines from deep into Gakpo / Malen / Brobbey.
  2. **Dumfries cross → Brobbey/Gakpo** — runners and a target attacking the box.
  3. **Gakpo cut-in shot** — onto right foot from left.
- Late arrivals from Reijnders into the box (signature runs from the three); Gravenberch picks his moments from deep.
- Brobbey occupies and pins the CBs (strength 17), holds for runners and finishes first-time inside the box (shoot 16); Malen attacks the last line in behind (speed 18).

## Set Pieces
- Corners: Gakpo or Reijnders takes (Depay when on); targets Van Dijk (back post), Brobbey (near post — aerial No.9), Van Hecke, Dumfries (penalty spot — aerial threat).
- Direct FKs: Reijnders primary, Gakpo curling onto his right foot, de Jong central low-driven (Depay is first choice once on the pitch).
- Penalties: Gakpo is the on-pitch designated taker (penalty 17); Depay takes over as first choice whenever he is on. Reijnders/de Jong are alternates.
- Defending: Van Dijk + Van Hecke are the centre-back duo — zonal back post, man-marked at near post; van de Ven's pace covers any deep restart. **MD1 fix:** tighten the near-post zone and back-post man-marking after conceding the late Kamada flick-on from a corner.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; commit to the build, don't go long unless triple-pressed.
2. When my `player_id` ends with `_5` (LCM — de Jong): drop to the left of / between the CBs to receive when pressed; otherwise hold the left of the midfield three. Pass 18 — primary distributor.
3. When my `player_id` ends with `_2` (LCB — Van Dijk): set the line; offside trap when opponent plays backward; long diagonal switch to the `_4` (Dumfries) when right side is open.
4. When my `player_id` ends with `_1` (LB — van de Ven): stay disciplined; tuck inside to form back-3 when the `_4` (Dumfries) goes very high; use speed 19 to sweep behind the high line.
5. When my `player_id` ends with `_4` (RB — Dumfries): overlap outside the `_10` (Malen) when ball is on the right side; cross to the `_9` (Brobbey) and `_8` (Gakpo).
6. When my `player_id` ends with `_6` (CM — Reijnders): operate as the advanced central runner; underlap into either half-space; late box arrivals are my goal-scoring pattern.
7. When my `player_id` ends with `_7` (RCM — Gravenberch): hold the right of the midfield three; carry forward from deep when a lane opens; cover behind the `_4` (Dumfries) overlap.
8. When my `player_id` ends with `_8` (LW — Gakpo): stay wide first, then cut inside onto right foot for Shoot when ball arrives at my feet 22m+ central; Move forward at LCB-LB seam when the `_9` (Brobbey) pulls them.
9. When my `player_id` ends with `_9` (ST — Brobbey): pin and hold off the last CB (strength 17); attack `_4` (Dumfries) crosses at the near post; finish first-time inside the box (shoot 16); link for runners.
10. When my `player_id` ends with `_10` (RW — Malen): run in behind the last line from the right (speed 18) — channel runs over touchline link play; attack crosses and through-balls; finish first-time.
11. When team_phase is "defending" in mid-block: 4-1-4-1 / 4-3-3, the `_5` (de Jong) and `_7` (Gravenberch) screening. Hold high line. The `_8` (Gakpo) and `_10` (Malen) drop to wide-mid.
12. When ball is lost in opp half: 4-second counter-press; nearest 3 close down; if not won back, retreat.
13. When opponent has the ball in their half and is recycling: the `_9` (Brobbey) presses CB only on triggers (back-pass to GK or square ball); otherwise hold the mid-block line.
14. Shoot from outside the box only if my `player_id` ends with `_8`, `_6`, or `_5` (Gakpo/Reijnders/de Jong) — free shots from distance permitted for these three.

## Key Player Notes
- **Van Dijk (idx 2)** — captain, standard-setter. Long diagonal switches are his signature. Set-piece header threat.
- **van de Ven (idx 1)** — elite recovery pace (19) now deployed at LB; the insurance behind the high line. Steps aggressively, sprints back when beaten.
- **Van Hecke (idx 3)** — the front-foot RCB who won the shirt off Aké; brave stepping into midfield, tidy on the ball.
- **Frenkie de Jong (idx 5)** — the brain and vice-captain. Drops to the left of the back line to build; carries the ball into midfield.
- **Reijnders (idx 6)** — the advanced runner of the three; between-the-lines threat and late box arrivals.
- **Gravenberch (idx 7)** — powerful two-way pivot; ball progression from deep and the cover behind Dumfries.
- **Dumfries (idx 4)** — the overlap engine on the right; combines with Malen for 2v1s and feeds Brobbey in the box.
- **Brobbey (idx 9)** — the physical No.9 who scored twice in the real Sweden rout; holds, pins CBs (strength 17) and finishes inside the box. Keeps the shirt ahead of the recovering Depay; Malen is the pace alternative through the middle.
- **Gakpo (idx 8)** — left inside-forward, the team's most consistent scorer (struck again vs Sweden); cut-in shooter and on-pitch penalty taker.
- **Malen (idx 10)** — pure pace in behind (speed 18) from the right; the high line's worst nightmare on the counter. Can shift to ST if Brobbey's knock flares.
- **Summerville (bench)** — the 1v1 specialist (dribbling 17); scored vs Japan but drops out for the 4-3-3 and a recent head knock; impact option late.
- **Depay (bench)** — captain-in-spirit and all-time top scorer, still unavailable with a thigh problem; once fit he is the designated penalty / free-kick / corner deliverer and the most likely game-changer from the bench.

## Tournament Mindset
Aggressive, technical, ambitious. Koeman trusts the Dutch tradition of attack — Netherlands won't park the bus, even when leading. Vulnerable to fast counter-attackers exploiting the high line (Japan twice punished transitions in MD1) and to set pieces. Going into the final group game, Netherlands sit **top of Group F on 4 points (+4 GD)** and need only a draw against an already-eliminated Tunisia (0 points, −8) at Arrowhead Stadium to guarantee passage to the knockout round — and a win likely secures top spot. Expect a controlled, front-foot performance: keep the ball, use Brobbey to pin and Malen to stretch, but manage minutes and tighten the defensive set pieces. On their best day a top-4 team.
