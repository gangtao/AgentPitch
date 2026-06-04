# Netherlands — Tactical Profile

## Identity & Philosophy
Ronald Koeman's Netherlands is modern Total Football: positional, vertical, and built on technical CBs and a creative midfield. Possession is purposeful — not for its own sake but to verticalize through Frenkie de Jong and reach Gakpo / Depay in the final third. The team is comfortable with risk: high line, aggressive overlaps, asymmetric width. Recent results: Euro 2024 semifinal (lost to England), strong qualifying campaign — Dutch football confidence is back. With Matthijs de Ligt (back surgery) and Xavi Simons (ACL) both ruled out of the tournament, Micky van de Ven's recovery pace partners Van Dijk at CB, and a three-man engine of de Jong–Reijnders–Gravenberch carries the creative load.

## Formation
- Shape: 4-3-3 (de Jong as single pivot; Reijnders + Gravenberch as #8s)
- Role mapping (roster order in `netherlands.yaml`):
  - index 0: GK — Bart Verbruggen (ball-playing keeper; pass 16)
  - index 1: LB — Nathan Aké (converted CB → LB; solid, conservative; sometimes drops into back 3)
  - index 2: LCB — Virgil van Dijk (captain; strength 19, discipline 19 — the standard at CB)
  - index 3: RCB — Micky van de Ven (recovery pace 19; covers the high line; aggressive stepper)
  - index 4: RB — Denzel Dumfries (auxiliary winger; stamina 18, speed 17 — runs the right wing alone)
  - index 5: LCM/#8 — Tijjani Reijnders (box-to-box; late arrivals; pass 17, stamina 18)
  - index 6: DM/#6 — Frenkie de Jong (single pivot; pass 18, dribble 18 — the deep playmaker)
  - index 7: RCM/#8 — Ryan Gravenberch (powerful two-way carrier; stamina 18; ball progression from the right interior)
  - index 8: LW — Cody Gakpo (left winger / inside-forward hybrid; shoot 17)
  - index 9: CF — Memphis Depay (all-time top scorer; drops to link, drifts left, finishes; shoot 17)
  - index 10: RW (option) — Donyell Malen (speed 18; impact / starter pace alternative — pure direct winger)

## Style of Play

### Build-up
- Verbruggen short to Van Dijk or van de Ven. Frenkie de Jong drops between or beside CBs (forming a 3-build).
- Both FBs push high; Aké stays slightly deeper as a balancer (he was a CB).
- Reijnders and Gravenberch offer between-lines options at half-space heights.
- Tempo: medium-high. Netherlands is willing to verticalize when the lane opens — not pure tiki-taka.

### Pressing
- Coordinated mid-to-high block. Depay leads, presses CB; Gakpo cuts back-pass option; Gravenberch jumps #6.
- Aggressive when ball is on the opponent's flank: Dumfries jumps the LB high; CBs slide.
- Counter-press: 4-second rule near the opponent's box.

### Defensive shape
- 4-3-3 → 4-1-4-1 mid-block. de Jong stays in front of CBs.
- High line — Van Dijk is the offside-trap conductor; CBs step in sync.
- Wide mids (Gakpo, Gravenberch) drop to wide-mid heights; Dumfries does the work for both right-side mid/RB jobs.

### Wide play
- Asymmetric:
  - **LEFT**: Gakpo holds width on the touchline; Aké tucks inside or stays deep; Reijnders underlaps from #8.
  - **RIGHT**: Dumfries is the *only* width source; Gravenberch carries into the right half-space; Malen subs in to give a true RW when extra direct width is needed.
- Crosses from Dumfries → Depay/Gakpo arriving in the box is a Dutch signature.

### Final third
- Patterns:
  1. **de Jong line-break pass** — through the lines from the pivot into Gakpo / Depay.
  2. **Dumfries cross → Depay/Gakpo** — late runners attacking the box.
  3. **Gakpo cut-in shot** — onto right foot from left.
- Late arrivals from Reijnders and Gravenberch into the box (signature #8 runs).
- Depay drops to link and slides left, then bends shots onto his right foot (shoot 17).

## Set Pieces
- Corners: Depay or de Jong takes; targets Van Dijk (back post), van de Ven (near post), Dumfries (penalty spot — aerial threat).
- Direct FKs: Depay primary (curling, either side), de Jong central (low driven), Aké left-foot from right side.
- Penalties: Depay is the designated taker.
- Defending: Van Dijk + van de Ven are the centre-back duo — zonal back post, man-marked at near post; van de Ven's pace covers any deep restart.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; commit to the build, don't go long unless triple-pressed.
2. When my `player_id` ends with `_6` (DM — de Jong): drop between CBs to receive when pressed; otherwise stay as single pivot. Pass 18 — primary distributor.
3. When my `player_id` ends with `_2` (LCB — Van Dijk): set the line; offside trap when opponent plays backward; long diagonal switch to the `_4` (Dumfries) when right side is open.
4. When my `player_id` ends with `_1` (LB — Aké): stay disciplined; tuck inside to form back-3 when the `_4` (Dumfries) goes very high.
5. When my `player_id` ends with `_4` (RB — Dumfries): treat the RW slot as my responsibility — sprint to RW height when ball is on right side; cross to the `_9` (Depay).
6. When my `player_id` ends with `_5` (#8 — Reijnders): underlap into left half-space; late box arrivals are my goal-scoring pattern.
7. When my `player_id` ends with `_7` (#8 — Gravenberch): carry into the right half-space; receive between lines; turn forward; drive at the box or Pass; late arrivals are a goal-scoring pattern.
8. When my `player_id` ends with `_8` (LW — Gakpo): stay wide first, then cut inside onto right foot for Shoot when ball arrives at my feet 22m+ central; Move forward at LCB-LB seam when the `_9` (Depay) pulls them.
9. When my `player_id` ends with `_9` (CF — Depay): drop to link play and drift left; receive between lines, turn, and Shoot from the box edge (shoot 17); attack `_4` (Dumfries) crosses.
10. When team_phase is "defending" in mid-block: 4-1-4-1, the `_6` (de Jong) shielding. Hold high line. The `_8` (Gakpo) and `_7` (Gravenberch) drop to wide-mid.
11. When ball is lost in opp half: 4-second counter-press; nearest 3 close down; if not won back, retreat.
12. When opponent has the ball in their half and is recycling: the `_9` (Depay) presses CB only on triggers (back-pass to GK or square ball); otherwise hold the mid-block line.
13. Shoot from outside the box only if my `player_id` ends with `_8`, `_9`, or `_6` (Gakpo/Depay/de Jong) — free shots from distance permitted for these three.

## Key Player Notes
- **Van Dijk (idx 2)** — captain, standard-setter. Long diagonal switches are his signature. Set-piece header threat.
- **van de Ven (idx 3)** — elite recovery pace; the insurance behind the high line. Steps aggressively, sprints back when beaten.
- **Frenkie de Jong (idx 6)** — the brain and vice-captain. Allowed to carry the ball into midfield from CB position.
- **Gravenberch (idx 7)** — powerful two-way #8; ball progression and late box arrivals from the right interior.
- **Dumfries (idx 4)** — auxiliary winger; treat him tactically as an RW.
- **Depay (idx 9)** — all-time top scorer; penalty and free-kick taker. Drops to link, drifts left, finishes with either foot.

## Tournament Mindset
Aggressive, technical, ambitious. Koeman trusts the Dutch tradition of attack — Netherlands won't park the bus, even when leading. Vulnerable to fast counter-attackers exploiting the high line, but on their best day a top-4 team.
