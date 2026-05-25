# Netherlands — Tactical Profile

## Identity & Philosophy
Ronald Koeman's Netherlands is modern Total Football: positional, vertical, and built on technical CBs and a creative midfield. Possession is purposeful — not for its own sake but to verticalize through Frenkie de Jong and reach Xavi Simons / Gakpo in the final third. The team is comfortable with risk: high line, aggressive overlaps, asymmetric width. Recent results: Euro 2024 semifinal (lost to England), strong qualifying campaign — Dutch football confidence is back.

## Formation
- Shape: 4-3-3 (de Jong as single pivot; Reijnders + Simons as #8s)
- Role mapping (roster order in `netherlands.yaml`):
  - index 0: GK — Bart Verbruggen (ball-playing keeper; pass 16)
  - index 1: LB — Nathan Aké (converted CB → LB; solid, conservative; sometimes drops into back 3)
  - index 2: LCB — Virgil van Dijk (captain; strength 19, discipline 19 — the standard at CB)
  - index 3: RCB — Matthijs de Ligt (physical, aerial; aggressive stepper)
  - index 4: RB — Denzel Dumfries (auxiliary winger; stamina 18, speed 17 — runs the right wing alone)
  - index 5: LCM/#8 — Tijjani Reijnders (box-to-box; late arrivals; pass 17, stamina 18)
  - index 6: DM/#6 — Frenkie de Jong (single pivot; pass 18, dribble 18 — the deep playmaker)
  - index 7: RCM/#10 — Xavi Simons (drifts to RW or #10; primary creator on right side)
  - index 8: LW — Cody Gakpo (left winger / inside-forward hybrid; shoot 17)
  - index 9: CF — Wout Weghorst (target man; aerial; strength 18; will run channels for direct balls)
  - index 10: RW (option) — Donyell Malen (speed 18; impact / starter pace alternative — pure direct winger)

## Style of Play

### Build-up
- Verbruggen short to Van Dijk or de Ligt. Frenkie de Jong drops between or beside CBs (forming a 3-build).
- Both FBs push high; Aké stays slightly deeper as a balancer (he was a CB).
- Reijnders and Simons offer between-lines options at half-space heights.
- Tempo: medium-high. Netherlands is willing to verticalize when the lane opens — not pure tiki-taka.

### Pressing
- Coordinated mid-to-high block. Weghorst leads, presses CB; Gakpo cuts back-pass option; Simons jumps #6.
- Aggressive when ball is on the opponent's flank: Dumfries jumps the LB high; CBs slide.
- Counter-press: 4-second rule near the opponent's box.

### Defensive shape
- 4-3-3 → 4-1-4-1 mid-block. de Jong stays in front of CBs.
- High line — Van Dijk is the offside-trap conductor; CBs step in sync.
- Wide mids (Gakpo, Simons) drop to wide-mid heights; Dumfries does the work for both right-side mid/RB jobs.

### Wide play
- Asymmetric:
  - **LEFT**: Gakpo holds width on the touchline; Aké tucks inside or stays deep; Reijnders underlaps from #8.
  - **RIGHT**: Dumfries is the *only* width source; Simons drifts inside to half-space / #10; Malen subs in when Simons floats too far inside.
- Crosses from Dumfries → Weghorst near post is a Dutch signature.

### Final third
- Patterns:
  1. **de Jong line-break pass** — through the lines from the pivot into Simons / Gakpo.
  2. **Dumfries cross → Weghorst** — classic target-man finish.
  3. **Gakpo cut-in shot** — onto right foot from left.
- Late arrivals from Reijnders into the box (signature AC Milan-era pattern).
- Long shots welcomed from Simons (skill 18, shoot 16).

## Set Pieces
- Corners: de Jong or Simons takes; targets Van Dijk (back post), de Ligt (near post), Weghorst (penalty spot — heading machine).
- Direct FKs: Simons left side, de Jong central (low driven), Aké left-foot from right side.
- Defending: Van Dijk + de Ligt are the elite duo — zonal back post, man-marked at near post.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; commit to the build, don't go long unless triple-pressed.
2. When my `player_id` ends with `_6` (DM — de Jong): drop between CBs to receive when pressed; otherwise stay as single pivot. Pass 18 — primary distributor.
3. When my `player_id` ends with `_2` (LCB — Van Dijk): set the line; offside trap when opponent plays backward; long diagonal switch to the `_4` (Dumfries) when right side is open.
4. When my `player_id` ends with `_1` (LB — Aké): stay disciplined; tuck inside to form back-3 when the `_4` (Dumfries) goes very high.
5. When my `player_id` ends with `_4` (RB — Dumfries): treat the RW slot as my responsibility — sprint to RW height when ball is on right side; cross to the `_9` (Weghorst).
6. When my `player_id` ends with `_5` (#8 — Reijnders): underlap into left half-space; late box arrivals are my goal-scoring pattern.
7. When my `player_id` ends with `_7` (#10 — Simons): drift into right half-space; receive between lines; turn forward; Pass or Shoot from 18-22m.
8. When my `player_id` ends with `_8` (LW — Gakpo): stay wide first, then cut inside onto right foot for Shoot when ball arrives at my feet 22m+ central; Move forward at LCB-LB seam when the `_9` (Weghorst) pulls them.
9. When my `player_id` ends with `_9` (CF — Weghorst): stay central and in the box; near-post run on `_4` (Dumfries) crosses; physical battle with CBs — aerial duels are my specialty.
10. When team_phase is "defending" in mid-block: 4-1-4-1, the `_6` (de Jong) shielding. Hold high line. The `_8` (Gakpo) and `_7` (Simons) drop to wide-mid.
11. When ball is lost in opp half: 4-second counter-press; nearest 3 close down; if not won back, retreat.
12. When opponent has the ball in their half and is recycling: the `_9` (Weghorst) presses CB only on triggers (back-pass to GK or square ball); otherwise hold the mid-block line.
13. Shoot from outside the box only if my `player_id` ends with `_7`, `_8`, or `_6` (Simons/Gakpo/de Jong) — free shots from distance permitted for these three.

## Key Player Notes
- **Van Dijk (idx 2)** — captain, standard-setter. Long diagonal switches are his signature. Set-piece header threat.
- **Frenkie de Jong (idx 6)** — the brain. Allowed to carry the ball into midfield from CB position.
- **Simons (idx 7)** — primary creator. Free role on the right; floats #10 / RW / RCM.
- **Dumfries (idx 4)** — auxiliary winger; treat him tactically as an RW.
- **Weghorst (idx 9)** — target man. Aerial duels, near-post runs; finishing in the box.

## Tournament Mindset
Aggressive, technical, ambitious. Koeman trusts the Dutch tradition of attack — Netherlands won't park the bus, even when leading. Vulnerable to fast counter-attackers exploiting the high line, but on their best day a top-4 team.
