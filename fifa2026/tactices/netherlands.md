# Netherlands — Tactical Profile

## Identity & Philosophy
Ronald Koeman's Netherlands is modern Total Football: positional, vertical, and built on technical CBs and a creative midfield. Possession is purposeful — not for its own sake but to verticalize through Frenkie de Jong and reach Gakpo / Malen in the final third. The team is comfortable with risk: high line, aggressive overlaps, asymmetric width. Recent results: Euro 2024 semifinal, strong qualifying campaign — Dutch football confidence is back. **Matchday 1 (June 14, 2026): Netherlands 2-2 Japan** — Van Dijk (51') and Summerville (64') gave the Oranje a 2-1 lead, but Japan equalised twice (Nakamura, then a Kamada flick-on off an Ito corner at 88'). A disappointing draw that exposed the high line's fragility on transitions and a soft second goal conceded at a set piece. With Xavi Simons ruled out for the tournament (ruptured ACL) and Jeremie Frimpong omitted, Koeman has settled on a 4-2-3-1: Micky van de Ven's recovery pace shifts to left-back, Jan Paul van Hecke partners Van Dijk at CB, a de Jong–Gravenberch double pivot sits behind Reijnders at #10, and Malen leads the line. **Memphis Depay** has recovered from his thigh injury but was not yet fit to start vs Japan — he came on for the final ~20 minutes and remains the team's designated dead-ball and penalty taker whenever he is on the pitch; off the bench he is the late-game game-changer.

## Formation
- Shape: 4-2-3-1 (de Jong + Gravenberch double pivot; Reijnders as the #10)
- Role mapping (roster order in `netherlands.yaml`):
  - index 0: GK — Bart Verbruggen (ball-playing keeper; pass 16)
  - index 1: LB — Micky van de Ven (converted CB → LB; recovery pace 19 — covers the high line from the left; conservative going forward)
  - index 2: LCB — Virgil van Dijk (captain; strength 19, discipline 19 — the standard at CB)
  - index 3: RCB — Jan Paul van Hecke (front-foot Brighton stopper; calm distribution, pass 15; preferred over Aké)
  - index 4: RB — Denzel Dumfries (overlapping bomber; stamina 18, speed 17 — relentless up the right)
  - index 5: CAM/#10 — Tijjani Reijnders (between the lines; late arrivals; pass 17, stamina 18)
  - index 6: DM/#6 — Frenkie de Jong (left side of the double pivot; pass 18, dribble 18 — the deep playmaker)
  - index 7: DM/#8 — Ryan Gravenberch (right side of the double pivot; powerful two-way carrier; stamina 18)
  - index 8: LW — Cody Gakpo (left winger / inside-forward hybrid; shoot 17)
  - index 9: ST — Donyell Malen (speed 18; leads the line with runs in behind — a sprinter's #9, not a target man)
  - index 10: RW — Crysencio Summerville (dribbling 17, speed 17; direct 1v1 winger who attacks the byline)

## Style of Play

### Build-up
- Verbruggen short to Van Dijk or Van Hecke. Frenkie de Jong drops between or beside CBs (forming a 3-build); Gravenberch holds as the second pivot.
- Dumfries pushes high; van de Ven stays slightly deeper as a balancer (he is a converted CB).
- Reijnders offers the between-lines option at #10 height, drifting across both half-spaces.
- Tempo: medium-high. Netherlands is willing to verticalize when the lane opens — not pure tiki-taka.

### Pressing
- Coordinated mid-to-high block. Malen leads, presses CB; Gakpo cuts back-pass option; Reijnders jumps the opposition #6.
- Aggressive when ball is on the opponent's flank: Dumfries jumps the LB high; CBs slide.
- Counter-press: 4-second rule near the opponent's box.

### Defensive shape
- 4-2-3-1 → 4-4-1-1 mid-block. de Jong and Gravenberch stay in front of the CBs as the double screen.
- High line — Van Dijk is the offside-trap conductor; CBs step in sync; van de Ven's pace sweeps behind from LB.
- Wingers (Gakpo, Summerville) drop to wide-mid heights; Reijnders shadows the opposition pivot behind Malen.

### Wide play
- Asymmetric:
  - **LEFT**: Gakpo holds width on the touchline; van de Ven tucks inside or stays deep; Reijnders underlaps from the #10 slot.
  - **RIGHT**: Summerville and Dumfries double up for constant 2v1 overloads — Summerville takes the 1v1, Dumfries overlaps outside; Gravenberch covers the space behind.
- Crosses from Dumfries → Malen/Gakpo arriving in the box is a Dutch signature.

### Final third
- Patterns:
  1. **de Jong line-break pass** — through the lines from the pivot into Gakpo / Malen.
  2. **Dumfries cross → Malen/Gakpo** — runners attacking the box.
  3. **Gakpo cut-in shot** — onto right foot from left.
- Late arrivals from Reijnders into the box (signature #10 runs); Gravenberch picks his moments from deep.
- Malen attacks the last line — through-balls in behind (speed 18) rather than link play; first-time finishes (shoot 15).

## Set Pieces
- Corners: Gakpo or Reijnders takes (Depay when on); targets Van Dijk (back post — scored from Gravenberch's cross vs Japan), Van Hecke (near post), Dumfries (penalty spot — aerial threat).
- Direct FKs: Reijnders primary, Gakpo curling onto his right foot, de Jong central low-driven (Depay is first choice once on the pitch).
- Penalties: Gakpo is the on-pitch designated taker (penalty 17); Depay takes over as first choice whenever he is on. Reijnders/de Jong are alternates.
- Defending: Van Dijk + Van Hecke are the centre-back duo — zonal back post, man-marked at near post; van de Ven's pace covers any deep restart. **MD1 fix:** tighten the near-post zone and back-post man-marking after conceding the late Kamada flick-on from a corner.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; commit to the build, don't go long unless triple-pressed.
2. When my `player_id` ends with `_6` (DM — de Jong): drop between CBs to receive when pressed; otherwise hold the left side of the double pivot. Pass 18 — primary distributor.
3. When my `player_id` ends with `_2` (LCB — Van Dijk): set the line; offside trap when opponent plays backward; long diagonal switch to the `_4` (Dumfries) when right side is open.
4. When my `player_id` ends with `_1` (LB — van de Ven): stay disciplined; tuck inside to form back-3 when the `_4` (Dumfries) goes very high; use speed 19 to sweep behind the high line.
5. When my `player_id` ends with `_4` (RB — Dumfries): overlap outside the `_10` (Summerville) when ball is on the right side; cross to the `_9` (Malen) and `_8` (Gakpo).
6. When my `player_id` ends with `_5` (#10 — Reijnders): operate between the lines; underlap into the left half-space; late box arrivals are my goal-scoring pattern.
7. When my `player_id` ends with `_7` (DM — Gravenberch): hold the right side of the double pivot; carry forward from deep when a lane opens; cover behind the `_4` (Dumfries) overlap.
8. When my `player_id` ends with `_8` (LW — Gakpo): stay wide first, then cut inside onto right foot for Shoot when ball arrives at my feet 22m+ central; Move forward at LCB-LB seam when the `_9` (Malen) pulls them.
9. When my `player_id` ends with `_9` (ST — Malen): run in behind the last line (speed 18) — through-balls over link play; attack `_4` (Dumfries) crosses at the near post; finish first-time.
10. When my `player_id` ends with `_10` (RW — Summerville): take the fullback on 1v1 (dribbling 17) — beat him outside to the byline or cut in and combine with the `_5` (Reijnders).
11. When team_phase is "defending" in mid-block: 4-4-1-1, the `_6` (de Jong) and `_7` (Gravenberch) shielding. Hold high line. The `_8` (Gakpo) and `_10` (Summerville) drop to wide-mid.
12. When ball is lost in opp half: 4-second counter-press; nearest 3 close down; if not won back, retreat.
13. When opponent has the ball in their half and is recycling: the `_9` (Malen) presses CB only on triggers (back-pass to GK or square ball); otherwise hold the mid-block line.
14. Shoot from outside the box only if my `player_id` ends with `_8`, `_5`, or `_6` (Gakpo/Reijnders/de Jong) — free shots from distance permitted for these three.

## Key Player Notes
- **Van Dijk (idx 2)** — captain, standard-setter. Long diagonal switches are his signature. Set-piece header threat.
- **van de Ven (idx 1)** — elite recovery pace (19) now deployed at LB; the insurance behind the high line. Steps aggressively, sprints back when beaten.
- **Van Hecke (idx 3)** — the front-foot RCB who won the shirt off Aké; brave stepping into midfield, tidy on the ball.
- **Frenkie de Jong (idx 6)** — the brain and vice-captain. Allowed to carry the ball into midfield from CB position.
- **Gravenberch (idx 7)** — powerful two-way pivot partner; ball progression from deep and the cover behind Dumfries.
- **Dumfries (idx 4)** — the overlap engine on the right; doubles up with Summerville for 2v1s.
- **Malen (idx 9)** — starts ahead of the recovering Depay; pure pace in behind (speed 18), the high line's worst nightmare. Holds the shirt until Depay is match-fit.
- **Summerville (idx 10)** — the 1v1 specialist on the right (dribbling 17); direct, fearless, byline-or-cut-in. Scored the 2-1 vs Japan with a cut-in to the far post.
- **Depay (bench)** — captain-in-spirit and all-time top scorer, back from a thigh injury but not yet 90-minutes fit; entered late vs Japan. The team's designated penalty / free-kick / corner deliverer and the most likely game-changer from the bench. Expected to push for a start once sharp.

## Tournament Mindset
Aggressive, technical, ambitious. Koeman trusts the Dutch tradition of attack — Netherlands won't park the bus, even when leading. Vulnerable to fast counter-attackers exploiting the high line (Japan twice punished transitions in MD1) and to set pieces. After the opening-day draw, the Sweden fixture is must-win territory: expect the Oranje to be more clinical at protecting a lead and tighter at defensive set pieces, while keeping the same front-foot identity. On their best day a top-4 team.
