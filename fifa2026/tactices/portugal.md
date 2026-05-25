# Portugal — Tactical Profile

## Identity & Philosophy
Roberto Martínez's Portugal is a collection of elite individuals organized into a (sometimes) coherent 4-3-3. Ronaldo remains the focal point at age 41 — captain, leader, finisher — but the engine room is now Vitinha and João Neves controlling tempo, with Bruno Fernandes orchestrating from advanced midfield. The team can look mesmeric in one match and structurally chaotic the next. Recent results: Euro 2024 quarterfinal exit on penalties; comfortable qualifying campaign with the highest goals-per-game in UEFA.

## Formation
- Shape: 4-3-3 (Bruno Fernandes is technically the right #8 but plays as a #10; effectively 4-2-3-1 in attack)
- Role mapping (roster order in `portugal.yaml`):
  - index 0: GK — Diogo Costa (modern keeper, sweeper instincts, pass 16)
  - index 1: LB — Nuno Mendes (overlapping rocket; speed 18, dribbling 16 — auxiliary winger)
  - index 2: LCB — Rúben Dias (the leader at the back; calm, vocal, pass 17)
  - index 3: RCB — Gonçalo Inácio (ball-playing CB, left-footed for balance)
  - index 4: RB — Nélson Semedo (more conservative than Mendes; provides right-side cover for Bruno's wandering)
  - index 5: DM/#6 — Vitinha (single pivot variant; pass 18, dribble 17 — the metronome)
  - index 6: RCM/#8 — João Neves (box-to-box; high energy; tackles + late runs)
  - index 7: AM/#10 — Bruno Fernandes (nominal RCM but operates as a #10; primary creator)
  - index 8: RW (floating) — Bernardo Silva (the connector; drifts inside, into half-space, links every phase)
  - index 9: CF — Cristiano Ronaldo (captain; box poacher; aerial threat; will not press)
  - index 10: LW — Rafael Leão (direct, dribble 18, speed 19 — license to take on his man)

## Style of Play

### Build-up
- Diogo Costa short to Rúben Dias or Inácio.
- Vitinha drops between CBs when pressed (3-2-5 build). João Neves provides the box-to-box link.
- Nuno Mendes pushes ULTRA high on the left; Semedo stays deeper on the right (asymmetric — covers Bruno's roaming).
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
- **RIGHT**: Semedo deeper; Bernardo drifts inside; Bruno arrives late. Less width on this side.
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
2. When my `player_id` ends with `_2` (LCB — Dias): set the line — vocal organizer. Pass forward to the `_5` (Vitinha); long-ball to the `_10` (Leão) only if outlet is open.
3. When my `player_id` ends with `_1` (LB — Mendes) and team_phase is "attacking": sprint to LW height — overlap the `_10` (Leão) or take the touchline solo. License to be wing-back.
4. When my `player_id` ends with `_4` (RB — Semedo): stay disciplined at RB height; cover for the `_7` (Bruno's) vacated zone; rarely overlap.
5. When my `player_id` ends with `_5` (DM — Vitinha): single pivot; recycle possession; drive forward with the ball when the line is broken (dribble 17 — the rare DM who carries).
6. When my `player_id` ends with `_6` (#8 — Neves): support the `_5` (Vitinha); arrive late in the box; tackle aggressively in midfield.
7. When my `player_id` ends with `_7` (#10 — Bruno): roam into right half-space; switch play diagonally to the `_10` (Leão); through-ball the `_9` (Ronaldo); Shoot 18-25m if lane opens.
8. When my `player_id` ends with `_8` (RW — Bernardo): drift into right half-space to receive between lines; combine with the `_7` (Bruno); rarely take touchline width.
9. When my `player_id` ends with `_10` (LW — Leão): hug LW touchline; on-ball 1v1, Move toward LB + Move diagonal inside; Shoot near post OR pass to the `_9` (Ronaldo) at the back.
10. When my `player_id` ends with `_9` (CF — Ronaldo): stay in or near the box. Move toward near post on `_1` (Mendes) crosses; Move to penalty spot on `_10` (Leão) cutbacks. Shoot whenever inside 22m at any angle — discipline 13, will shoot ambitiously.
11. When team_phase is "defending": the `_9` (Ronaldo) holds halfway as outball; all others form a 4-5-1; the `_8` (Bernardo) and `_7` (Bruno) track back.
12. When ball is lost in opp half: the `_5` (Vitinha) + `_6` (Neves) immediate counter-press; wingers may or may not join.
13. Tackle aggressively only if my `player_id` ends with `_6`, `_5`, or `_2` (Neves/Vitinha/Dias) — discipline matters. The `_1` (Mendes) and `_10` (Leão) have low discipline; they can foul.

## Key Player Notes
- **Ronaldo (idx 9)** — captain, untouchable starter. Will stay near goal; will not press; lethal in the box. Set-piece role: near-post header.
- **Bruno Fernandes (idx 7)** — primary creator. Free role to roam between RCM and #10. Set-piece taker.
- **Leão (idx 10)** — license to dribble. Often Portugal's main goal threat from open play; treat him as a designated shooter from the left.
- **Mendes (idx 1)** — auxiliary LW. The team's tactical flexibility comes from his license to push.
- **Vitinha (idx 5)** — the brain. Without him, Portugal lacks rhythm.

## Tournament Mindset
Win on talent. Portugal trusts that on any given day, Bruno + Bernardo + Leão + Ronaldo will produce three moments more than the opponent. Structural discipline second; star power first.
