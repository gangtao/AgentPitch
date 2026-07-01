# Portugal — Tactical Profile

## Identity & Philosophy
Roberto Martínez's Portugal is a collection of elite individuals organized into a (sometimes) coherent 4-3-3 that morphs into 4-2-3-1 in attack. Ronaldo remains the focal point at age 41 — captain, leader, finisher — now the oldest outfield player ever to start a World Cup match — but the engine room is Vitinha and João Neves (the PSG Champions-League axis) controlling tempo, with Bruno Fernandes orchestrating from the #10. The team can look mesmeric in one match and structurally chaotic the next. Martínez named a 27-man squad on May 19 2026 (a symbolic "plus one" in memory of the late Diogo Jota); Diogo Costa is the confirmed first-choice keeper. The squad is fully fit heading into the knockout round — no injuries, no suspensions carried into the Croatia tie.

**Group stage recap:** Portugal were held 1-1 by DR Congo (MD1), thrashed Uzbekistan 5-0 (MD2, Ronaldo brace), then drew 0-0 with Colombia (MD3) to finish **Group K runners-up**. That second-place finish drops them into a Round-of-16 meeting with **Croatia** on **Thursday 2 July, in Toronto**.

**Round of 16 — probable XI (as reflected in this roster):** Costa; Cancelo, Dias, Veiga, Mendes; Vitinha, Neves; Neto, Fernandes, Félix; Ronaldo. Martínez is expected to keep the **rotated shape** that closed out the group stage rather than the MD1 first-choice front line: **Renato Veiga partners Dias at centre-back** (Inácio drops to the bench), and the wide forwards are **Pedro Neto (right)** and **João Félix (left)** rather than Leão and Bernardo. **João Neves returns** to the midfield two after coming off the bench vs Colombia. The wide-forward and CB rotations (Veiga vs Inácio; Neto/Félix vs Leão/Bernardo) remain the chief selection watch points — Martínez has deep, interchangeable options and may still restore Leão/Bernardo/Inácio for a knockout; treat this as the most-likely XI, not a certainty.

## Formation
- Shape: 4-3-3 (Bruno Fernandes is the advanced central midfielder; effectively 4-2-3-1 in attack)
- Role mapping (roster order in `portugal.yaml`):
  - index 0: GK — Diogo Costa (modern keeper, sweeper instincts, pass 16)
  - index 1: LB — Nuno Mendes (overlapping rocket; speed 18, dribbling 16 — auxiliary winger)
  - index 2: LCB — Renato Veiga (left-footed, physical, versatile — steps in for Inácio; strength 16)
  - index 3: RCB — Rúben Dias (the leader at the back; calm, vocal, pass 17)
  - index 4: RB — João Cancelo (inverted fullback; dribble 17, pass 17 — steps into midfield, covers Bruno's wandering with positioning, not pace)
  - index 5: DM/#6 — Vitinha (single pivot variant; pass 18, dribble 17 — the metronome)
  - index 6: RCM/#8 — João Neves (box-to-box; high energy; tackles + late runs)
  - index 7: AM/#10 — Bruno Fernandes (nominal RCM but operates as a #10; primary creator)
  - index 8: LW — João Félix (drifts inside, links play, second creator; dribble 17)
  - index 9: CF — Cristiano Ronaldo (captain; box poacher; aerial threat; will not press)
  - index 10: RW — Pedro Neto (direct touchline threat; speed 18, dribble 17 — take on his man, cut back to Ronaldo)

## Style of Play

### Build-up
- Diogo Costa short to Rúben Dias or Renato Veiga.
- Vitinha drops between CBs when pressed (3-2-5 build). João Neves provides the box-to-box link.
- Nuno Mendes pushes ULTRA high on the left; Cancelo inverts into midfield on the right (asymmetric — his central position covers Bruno's roaming).
- Bruno Fernandes drifts into the right half-space pocket as the receiver between lines.

### Pressing
- **Inconsistent**. The midfield (Vitinha, Neves) wants to press; Ronaldo will not. This creates structural problems.
- When pressing high: Neto & Félix trigger from wide; Bruno jumps the #6; Ronaldo half-heartedly closes the CB.
- More realistic: mid-block 4-5-1, contain rather than press, then transition through Neto's and Mendes's pace.

### Defensive shape
- 4-5-1 / 4-3-3 mid-block. Bruno Fernandes drops to central/right-mid in defense — discipline has improved under Martinez.
- João Félix and Pedro Neto must track their fullbacks; Modrić/Kovačić/Sučić will probe the space if they switch off.
- Rúben Dias commands the line; Veiga steps out to intercept.
- Vulnerable to switches from their right (Mendes high on left = unbalanced).

### Wide play
- **LEFT**: Mendes overlap + Félix drifting inside — Mendes provides the width, Félix the combination in the half-space.
- **RIGHT**: Cancelo inverts inside; Pedro Neto holds the touchline and drives at his fullback; Bruno arrives late.
- Cross delivery from Mendes and cutbacks from Neto are the primary supply to Ronaldo.

### Final third
- Three termination patterns:
  1. **Mendes cross → Ronaldo finish** — the classic. Always available.
  2. **Neto isolation 1v1 → touchline drive → cut back for Ronaldo/Bruno.**
  3. **Bruno through-ball** — into the channel for Ronaldo or Félix.
- Shots from distance: Bruno and Vitinha take low-percentage long-range shots; Portugal accepts this.

## Set Pieces
- Corners: Bruno Fernandes is the primary taker. Inswingers to Ronaldo near post + Rúben Dias back post + Veiga.
- Direct FKs: Ronaldo central (24-28m, knuckleball signature); Bruno from sides.
- **Penalties (in-game spot kicks AND — critically for a knockout — a shootout after extra time):**
  1. **Cristiano Ronaldo** (penalty 18) — primary taker whenever he is on the pitch.
  2. **Bruno Fernandes** (penalty 17) — takes if Ronaldo is off, and the reliable No.1 shootout kicker.
  3. **João Félix** (penalty 15) / **Vitinha** (penalty 15).
  4. **João Cancelo** (penalty 14) / **João Neves** (penalty 14) / **Pedro Neto** (penalty 14).
  5. **Nuno Mendes** (penalty 13).
  - Shootout order should front-load Ronaldo → Bruno → Félix/Vitinha → Cancelo/Neves/Neto → Mendes. If Ronaldo has been substituted late (fatigue at 41), Bruno becomes the No.1 kicker.
- Defending set pieces: man-marking on the biggest threats (Budimir, Šutalo aerially); Diogo Costa commands his area and is a shootout asset (save 18).

## decide() Decision Priorities
1. When my role is GK: pass short to a CB; sweeper-keeper instincts — push 10-15m off goal line when team is attacking.
2. When my `player_id` ends with `_3` (RCB — Dias): set the line — vocal organizer. Pass forward to the `_5` (Vitinha); long-ball to the `_10` (Neto) or `_8` (Félix) only if outlet is open.
3. When my `player_id` ends with `_1` (LB — Mendes) and team_phase is "attacking": sprint to LW height — overlap the `_8` (Félix) or take the touchline solo. License to be wing-back.
4. When my `player_id` ends with `_4` (RB — Cancelo): invert — step into central midfield beside the `_5` (Vitinha) in possession; occupy the `_7` (Bruno's) vacated zone; rarely overlap the touchline.
5. When my `player_id` ends with `_5` (DM — Vitinha): single pivot; recycle possession; drive forward with the ball when the line is broken (dribble 17 — the rare DM who carries).
6. When my `player_id` ends with `_6` (#8 — Neves): support the `_5` (Vitinha); arrive late in the box; tackle aggressively in midfield.
7. When my `player_id` ends with `_7` (#10 — Bruno): roam into right half-space; switch play diagonally to the `_10` (Neto); through-ball the `_9` (Ronaldo); Shoot 18-25m if lane opens.
8. When my `player_id` ends with `_10` (RW — Neto): hug the right touchline; on-ball 1v1, drive at the fullback; cut back to the `_9` (Ronaldo) at the spot OR shoot near post.
9. When my `player_id` ends with `_8` (LW — Félix): drift inside from the left into the half-space; combine with the `_7` (Bruno) and `_1` (Mendes); Shoot when the lane opens or slip the `_9` (Ronaldo).
10. When my `player_id` ends with `_9` (CF — Ronaldo): stay in or near the box. Move toward near post on `_1` (Mendes) crosses; Move to penalty spot on `_10` (Neto) cutbacks. Shoot whenever inside 22m at any angle — discipline 13, will shoot ambitiously.
11. When team_phase is "defending": the `_9` (Ronaldo) holds halfway as outball; all others form a 4-5-1; the `_8` (Félix) and `_10` (Neto) track back onto their fullbacks.
12. When ball is lost in opp half: the `_5` (Vitinha) + `_6` (Neves) immediate counter-press; wingers may or may not join.
13. Tackle aggressively only if my `player_id` ends with `_6`, `_5`, or `_3` (Neves/Vitinha/Dias) — discipline matters. The `_1` (Mendes), `_4` (Cancelo) have low discipline; they can foul.

## Key Player Notes
- **Ronaldo (idx 9)** — captain, untouchable starter. Will stay near goal; will not press; lethal in the box. Set-piece role: near-post header. **Primary penalty taker and No.1 shootout kicker if still on the pitch at full/extra time.**
- **Bruno Fernandes (idx 7)** — primary creator. Free role to roam between RCM and #10. Set-piece taker and the reliable shootout No.1 if Ronaldo has been subbed.
- **Pedro Neto (idx 10)** — direct right-wing threat; speed 18, dribble 17. Treat him as a touchline 1v1 merchant who cuts back for Ronaldo — a designated wide shooter from the right.
- **João Félix (idx 8)** — left-side creator who drifts inside; second playmaker in the final third; confident finisher and penalty option (15).
- **Mendes (idx 1)** — auxiliary LW. The team's tactical flexibility comes from his license to push.
- **Cancelo (idx 4)** — the inverted fullback. Adds a second playmaker in build-up; defensively a gamble (discipline 12).
- **Vitinha (idx 5)** — the brain. Without him, Portugal lacks rhythm; also a cool penalty (15).
- **Renato Veiga (idx 2)** — deputising for Inácio; left-footed, physical, comfortable stepping out. Watch point: less refined on the ball than Inácio.

## Tournament Mindset
This is the **Round of 16 — win or go home.** Portugal come in as **Group K runners-up** after a flat 0-0 with Colombia, and they meet a **Croatia** side built on tournament experience: Modrić, Kovačić and the emerging Sučić run midfields, and they defend deep and punish transitions — exactly the kind of veteran, low-block opponent that exposed Portugal's impatience against DR Congo. There is no safety net now: **if the tie is level after 90 minutes it goes to 30 minutes of extra time, and if still level, to a penalty shootout.** That changes the calculus. Portugal must (1) stay patient and disciplined for the full 90 — do not force early and get countered by Modrić/Kovačić; (2) protect against Croatia's set-piece and second-ball threat with Dias and Veiga; (3) manage Ronaldo's minutes with extra time in mind — his legs at 41 and his value as the No.1 penalty taker both argue for keeping him on unless the game demands a change; and (4) be ready for the shootout, where Diogo Costa (save 18) and a front-loaded order of Ronaldo → Bruno → Félix/Vitinha give Portugal a real edge. Win on talent — Bruno, Félix, Neto and Ronaldo will produce moments — but the tie may hinge on nerve in the 120th minute and from the spot. Control the tempo through Vitinha + Neves, keep the counter-press switched on, and do not gift Croatia the transitions they thrive on. Survive, advance, and a Round-of-16 tie against the Spain vs Austria winner awaits.
