# Portugal — Tactical Profile

## Identity & Philosophy
Roberto Martínez's Portugal is a collection of elite individuals organized into a (sometimes) coherent 4-3-3. Ronaldo remains the focal point at age 41 — captain, leader, finisher — now the oldest outfield player ever to start a World Cup match (41 years, 132 days) — but the engine room is Vitinha and João Neves (the PSG Champions-League axis) controlling tempo, with Bruno Fernandes orchestrating from advanced midfield. The team can look mesmeric in one match and structurally chaotic the next. Martínez named a 27-man squad on May 19 2026 (a symbolic "plus one" in memory of the late Diogo Jota); Diogo Costa is the confirmed first-choice keeper. Recent results: Euro 2024 quarterfinal exit on penalties; comfortable qualifying campaign with the highest goals-per-game in UEFA.

**Matchday 1 (17 June, vs DR Congo — 1-1):** A shock. Portugal led inside six minutes when João Neves headed home a Pedro Neto cross, but Yoane Wissa equalised on the stroke of half-time (DR Congo's first-ever World Cup goal) and a deep, physical Leopards block held the draw. Rúben Dias missed the opener with a knock, so Martínez deputised with a makeshift back four and started Bernardo Silva, Bruno Fernandes and Pedro Neto behind Ronaldo, with Rafael Leão on the bench.

**Matchday 2 (23 June, vs Uzbekistan — 5-0):** Emphatic rebound at NRG Stadium, Houston (67% possession, 15 shots). **Cristiano Ronaldo scored twice (6', 39')** to become the first player ever to score at six different World Cups, **Nuno Mendes added a third (17')**, an own goal made it four (60'), and **Rafael Leão finished off the rout (87')**. Martínez rotated for the dead-rubber threat: **Renato Veiga partnered Dias at CB, João Félix and Pedro Neto started wide**, with Inácio, Bernardo and Leão rested into the second half. No suspensions; squad came through clean.

**For Matchday 3 vs Colombia (27 June, Hard Rock Stadium, Miami), the probable XI restores the first-choice 4-3-3** as reflected in this roster: Costa; Cancelo, Dias, Inácio, Mendes; Vitinha, Neves; Bernardo, Fernandes, Leão; Ronaldo. Inácio and Bernardo come back in for Veiga and Félix; Leão reclaims the left flank. The wide-forward rotation (Leão vs Neto vs Bernardo vs Félix) remains the chief selection watch point — Martínez has deep, interchangeable options across the front line.

## Formation
- Shape: 4-3-3 (Bruno Fernandes is technically the right #8 but plays as a #10; effectively 4-2-3-1 in attack)
- Role mapping (roster order in `portugal.yaml`):
  - index 0: GK — Diogo Costa (modern keeper, sweeper instincts, pass 16)
  - index 1: LB — Nuno Mendes (overlapping rocket; speed 18, dribbling 16 — auxiliary winger)
  - index 2: LCB — Gonçalo Inácio (ball-playing CB, left-footed for balance)
  - index 3: RCB — Rúben Dias (the leader at the back; calm, vocal, pass 17)
  - index 4: RB — João Cancelo (inverted fullback; dribble 17, pass 17 — steps into midfield, covers Bruno's wandering with positioning, not pace)
  - index 5: DM/#6 — Vitinha (single pivot variant; pass 18, dribble 17 — the metronome)
  - index 6: RCM/#8 — João Neves (box-to-box; high energy; tackles + late runs)
  - index 7: AM/#10 — Bruno Fernandes (nominal RCM but operates as a #10; primary creator)
  - index 8: LW — Rafael Leão (direct, dribble 18, speed 19 — license to take on his man)
  - index 9: CF — Cristiano Ronaldo (captain; box poacher; aerial threat; will not press)
  - index 10: RW (floating) — Bernardo Silva (the connector; drifts inside, into half-space, links every phase)

## Style of Play

### Build-up
- Diogo Costa short to Rúben Dias or Inácio.
- Vitinha drops between CBs when pressed (3-2-5 build). João Neves provides the box-to-box link.
- Nuno Mendes pushes ULTRA high on the left; Cancelo inverts into midfield on the right (asymmetric — his central position covers Bruno's roaming).
- Bruno Fernandes drifts into the right half-space pocket as the receiver between lines.

### Pressing
- **Inconsistent**. The midfield (Vitinha, Neves) wants to press; Ronaldo will not. This creates structural problems.
- When pressing high: Leão & Bernardo trigger; Bruno jumps the #6; Ronaldo half-heartedly closes the CB.
- More realistic: mid-block 4-5-1, contain rather than press, then transition through Leão's pace.

### Defensive shape
- 4-5-1 / 4-3-3 mid-block. Bruno Fernandes drops to right-mid in defense — discipline has improved under Martinez.
- Bernardo Silva is the hardest-working forward; tracks back constantly.
- Rúben Dias commands the line; Inácio steps out to intercept.
- Vulnerable to switches from their right (Mendes high on left = unbalanced).

### Wide play
- **LEFT**: Mendes overlap + Leão isolation. Sometimes both wide simultaneously — overload.
- **RIGHT**: Cancelo inverts inside; Bernardo drifts inside; Bruno arrives late. Less touchline width, more half-space combination on this side.
- Cross delivery from Mendes is the primary supply to Ronaldo.

### Final third
- Three termination patterns:
  1. **Mendes cross → Ronaldo finish** — the classic. Always available.
  2. **Leão isolation 1v1 → cut inside → shoot or pull back for Ronaldo/Bruno.**
  3. **Bruno through-ball** — into the channel for Ronaldo or Bernardo.
- Shots from distance: Bruno and Vitinha take low-percentage long-range shots; Portugal accepts this.

## Set Pieces
- Corners: Bruno Fernandes is the primary taker. Inswingers to Ronaldo near post + Rúben Dias back post + Inácio.
- Direct FKs: Ronaldo central (24-28m, knuckleball signature); Bruno from sides.
- Defending: man-marking on the biggest threats; Diogo Costa commands his area.

## decide() Decision Priorities
1. When my role is GK: pass short to a CB; sweeper-keeper instincts — push 10-15m off goal line when team is attacking.
2. When my `player_id` ends with `_3` (RCB — Dias): set the line — vocal organizer. Pass forward to the `_5` (Vitinha); long-ball to the `_8` (Leão) only if outlet is open.
3. When my `player_id` ends with `_1` (LB — Mendes) and team_phase is "attacking": sprint to LW height — overlap the `_8` (Leão) or take the touchline solo. License to be wing-back.
4. When my `player_id` ends with `_4` (RB — Cancelo): invert — step into central midfield beside the `_5` (Vitinha) in possession; occupy the `_7` (Bruno's) vacated zone; rarely overlap the touchline.
5. When my `player_id` ends with `_5` (DM — Vitinha): single pivot; recycle possession; drive forward with the ball when the line is broken (dribble 17 — the rare DM who carries).
6. When my `player_id` ends with `_6` (#8 — Neves): support the `_5` (Vitinha); arrive late in the box; tackle aggressively in midfield.
7. When my `player_id` ends with `_7` (#10 — Bruno): roam into right half-space; switch play diagonally to the `_8` (Leão); through-ball the `_9` (Ronaldo); Shoot 18-25m if lane opens.
8. When my `player_id` ends with `_10` (RW — Bernardo): drift into right half-space to receive between lines; combine with the `_7` (Bruno); rarely take touchline width.
9. When my `player_id` ends with `_8` (LW — Leão): hug LW touchline; on-ball 1v1, Move toward LB + Move diagonal inside; Shoot near post OR pass to the `_9` (Ronaldo) at the back.
10. When my `player_id` ends with `_9` (CF — Ronaldo): stay in or near the box. Move toward near post on `_1` (Mendes) crosses; Move to penalty spot on `_8` (Leão) cutbacks. Shoot whenever inside 22m at any angle — discipline 13, will shoot ambitiously.
11. When team_phase is "defending": the `_9` (Ronaldo) holds halfway as outball; all others form a 4-5-1; the `_10` (Bernardo) and `_7` (Bruno) track back.
12. When ball is lost in opp half: the `_5` (Vitinha) + `_6` (Neves) immediate counter-press; wingers may or may not join.
13. Tackle aggressively only if my `player_id` ends with `_6`, `_5`, or `_3` (Neves/Vitinha/Dias) — discipline matters. The `_1` (Mendes), `_4` (Cancelo) and `_8` (Leão) have low discipline; they can foul.

## Key Player Notes
- **Ronaldo (idx 9)** — captain, untouchable starter. Will stay near goal; will not press; lethal in the box. Set-piece role: near-post header.
- **Bruno Fernandes (idx 7)** — primary creator. Free role to roam between RCM and #10. Set-piece taker.
- **Leão (idx 8)** — license to dribble. Often Portugal's main goal threat from open play; treat him as a designated shooter from the left.
- **Mendes (idx 1)** — auxiliary LW. The team's tactical flexibility comes from his license to push.
- **Cancelo (idx 4)** — the inverted fullback. Adds a second playmaker in build-up; defensively a gamble (discipline 12).
- **Vitinha (idx 5)** — the brain. Without him, Portugal lacks rhythm.

## Tournament Mindset
Portugal go into the **Group K decider** alongside Colombia, DR Congo and Uzbekistan. After being stunned 1-1 by **DR Congo** in their opener, they crushed **Uzbekistan 5-0** to rebound, and now sit **second on 4 points with a superior goal difference (+5)** behind **Colombia (6 points, already qualified)**. The math at **Hard Rock Stadium, Miami (June 27)** is clear: a **Portugal win** lifts them level with Colombia on points and — with the GD edge — likely steals top spot and the friendlier knockout path; a **draw or defeat** still sends Portugal through but as runners-up, into a trickier Round of 32. Colombia, by contrast, only need a point to clinch first, so they can sit and counter — and unlike Uzbekistan they have genuine quality and pace in transition (this is no minnow block to break down). The trap is the same as MD1 but sharper: dominate the ball, force the issue, and get caught on the break. Portugal's plan with the first-choice spine restored: control through Vitinha + Neves, stretch the block with Mendes/Leão on the left and Cancelo/Bernardo combinations on the right, get Ronaldo and Leão onto early crosses and cutbacks, and be ruthless rather than patient. Win on talent — Bruno + Bernardo + Leão + Ronaldo will produce moments — but against a Colombia side built to counter, the counter-press of Vitinha + Neves and Dias commanding the line are the safety valves they must not switch off. Top spot is the prize; lose focus and the underdog's lesson of the opener repeats against a far better opponent.
