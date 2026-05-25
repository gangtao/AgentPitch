# Croatia — Tactical Profile

## Identity & Philosophy
Zlatko Dalić's Croatia remains a masterclass in possession-based tournament football — the smallest nation that consistently outplays its weight class. The team's identity is built around **midfield superiority**: Modrić (40 years old, still the captain), Kovačić, and Brozović form one of the most technical midfield triangles in world football history. Croatia will out-pass opponents, slow tempos, and break through patient build-up. Recent results: World Cup 2022 third place, Euro 2024 group exit (early sign of generational decline), but qualifying for 2026 has been positive.

## Formation
- Shape: 4-3-3 (Modrić as advanced #8 / #10; Brozović as the single pivot)
- Role mapping (roster order in `croatia.yaml`):
  - index 0: GK — Dominik Livaković (penalty-shootout specialist; reflex keeper; save 17)
  - index 1: LB — Borna Sosa (cross specialist; pass 16 — left-footed delivery from deep)
  - index 2: LCB — Joško Gvardiol (the future captain; speed 16, strength 17 — modern ball-playing CB)
  - index 3: RCB — Josip Šutalo (physical; aerial duels)
  - index 4: RB — Josip Stanišić (versatile; can play CB or RB; defensively responsible)
  - index 5: LCM/#8 — Mateo Kovačić (left interior; ball-carrier; dribble 17 — escapes pressure)
  - index 6: RCM/#8 (free) — Luka Modrić (captain, 40 years old; pass 19, skill 19 — the metronome AND the dagger)
  - index 7: DM/#6 — Marcelo Brozović (single pivot; positionally disciplined; pass 17)
  - index 8: LW — Ivan Perišić (veteran wide forward; crosses with left and right; physical)
  - index 9: CF — Andrej Kramarić (intelligent #9; drops short; creative finisher)
  - index 10: RW/CF — Ante Budimir (target option; strength 17 — used for direct play and aerial battles)

## Style of Play

### Build-up
- Livaković short to Gvardiol or Šutalo (long-balls only if pressed).
- Brozović drops between CBs in a 3-2 build; Modrić and Kovačić receive between lines.
- Sosa stays high on the left as a crosser; Stanišić more conservative on the right.
- **Croatia's build-up is slow on purpose** — they want to draw the opponent's midfield out, then escape via Modrić's dribble (dribble 17) into open space.

### Pressing
- Mid-block, not high press. Croatia's age profile (Modrić 40, Perišić 36, Brozović 32) precludes intense pressing.
- Triggers: opponent long-ball wins by Šutalo; back-pass to opp GK; Kramarić curve-runs to cut switch.
- More often, Croatia sits in a 4-3-3 mid-block and lets opponents have territory, knowing midfield superiority means they can win the ball back in midfield.

### Defensive shape
- 4-3-3 / 4-1-4-1. Brozović shields the CBs.
- Modrić's defensive contribution is minimal (age, energy preservation) — Kovačić does the running for him.
- Gvardiol is the line-setter; Šutalo physical; Stanišić conservative.
- Vulnerable to pace in behind and direct play around their midfield.

### Wide play
- Symmetric width with elderly heroes:
  - **LEFT**: Perišić wide, Sosa overlap to deliver crosses (Perišić's late-career role is now near-post header arrivals AND cross delivery).
  - **RIGHT**: Modrić drifts to the right half-space; Stanišić rarely overlaps; the right side is an inside-out structure where Modrić finds the pocket.
- Long, accurate crosses from Sosa → Kramarić, Perišić, Budimir.

### Final third
- Three termination patterns:
  1. **Modrić line-break pass** — vertical through-ball into Kramarić or wide for Perišić's run.
  2. **Sosa cross** — left-footed delivery to the back post.
  3. **Modrić late shot** — outside the box, top corner (career signature).
- Kramarić is the false-9; he drops to combine with Modrić; Budimir comes on for direct ball.
- Croatia does not high-tempo their final-third entries — they prefer 4-5 passes inside the box to disorganize.

## Set Pieces
- Corners: Modrić (right-side outswing) and Sosa (left-side inswing) are primary takers.
- Targets: Gvardiol (back post header), Šutalo, Budimir.
- Direct FKs: Modrić centered (15+ years of practice); Sosa left side; Perišić for power.
- Defending: man-mark biggest threats; Livaković is elite under crosses — punches more than catches.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only long under triple pressure. In shootouts I am the difference — but in open play I am a distributor first.
2. When my `player_id` ends with `_2` (LCB — Gvardiol): be the modern CB — carry the ball forward when lane opens (speed 16 helps); switch to the `_8` (Perišić) with long diagonals.
3. When my `player_id` ends with `_1` (LB — Sosa): stay HIGH on the left; deliver crosses with my left foot from any position; this is my primary attacking action.
4. When my `player_id` ends with `_7` (DM — Brozović): single pivot; recycle possession; never above the halfway line in open play; protect the CBs at all costs.
5. When my `player_id` ends with `_5` (LCM — Kovačić): be the runner — cover for the `_6` (Modrić); carry the ball through pressure (dribble 17); do the defensive work for the right side of midfield too.
6. When my `player_id` ends with `_6` (RCM/free — Modrić) and team has the ball: take the most touches; pace the tempo; through-ball when an opportunity opens; Shoot from 22-28m with right foot if lane opens. Free role.
7. When my `player_id` ends with `_6` (RCM/free — Modrić) and team_phase is "defending": stay around the halfway line; do not press; conserve energy; intercept passes via positioning, not running.
8. When my `player_id` ends with `_8` (LW — Perišić): wide on the left; veteran role — make near-post runs on `_1` (Sosa) overlaps; crosses with either foot; tackle back is acceptable (stamina 15).
9. When my `player_id` ends with `_9` (CF — Kramarić): drop short into the #10 pocket to combine; late runs into the box; clever finisher (skill 16) — Shoot accuracy over power.
10. When my `player_id` ends with `_10` (RW/CF — Budimir): aerial target; near-post or penalty-spot runs on crosses; physical battle with CBs.
11. When team_phase is "defending" in mid-block: 4-3-3 → 4-1-4-1; the `_7` (Brozović) protects; the `_6` (Modrić) walks; the `_5` (Kovačić) covers a lot of ground.
12. When ball is lost in own half: counter-press DOES NOT apply — Croatia retreats and reorganizes; first action is to deny verticality.
13. Shoot from outside the box only if my `player_id` ends with `_6`, `_5`, or `_8` (Modrić/Kovačić/Perišić).
14. Tackle: only the `_7`, `_5`, `_2`, and `_3` players (Brozović/Kovačić/Gvardiol/Šutalo) are licensed; others contain.

## Key Player Notes
- **Modrić (idx 6)** — captain, 40 years old, FREE ROLE. Allowed to drift anywhere from RCM to #10. Energy preservation in defense, full license in attack. Primary set-piece taker. Croatia's tactical center of gravity.
- **Kovačić (idx 5)** — the runner. Covers ground that Modrić cannot. Ball-carrier under pressure.
- **Brozović (idx 7)** — single pivot. Without him, Modrić has no protection. Set the line at the halfway mark.
- **Gvardiol (idx 2)** — the future of Croatian football. Modern ball-playing CB.
- **Sosa (idx 1)** — primary cross-delivery on the left. Most assists in qualifying.
- **Perišić (idx 8)** — veteran with energy issues but reliable in big moments.

## Tournament Mindset
Outplay opponents in midfield. Croatia knows it cannot run with the press-heavy teams (Spain, Germany, Netherlands) — so it slows the game, controls tempo, and trusts Modrić's vision to find the moment. Penalty shootouts are a Croatian comfort zone (Livaković saved 4 in 2022). Tournament knockouts are where this team thrives.
