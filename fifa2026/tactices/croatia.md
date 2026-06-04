# Croatia — Tactical Profile

## Identity & Philosophy
Zlatko Dalić's Croatia remains a masterclass in possession-based tournament football — the smallest nation that consistently outplays its weight class. The team's identity is built around **midfield superiority**: Modrić (40 years old, still the captain) and Kovačić form one of the most technical midfield pairings in world football history, now supported by the new generation in Petar Sučić. Croatia will out-pass opponents, slow tempos, and break through patient build-up. Recent results: World Cup 2022 third place, Euro 2024 group exit (early sign of generational decline), but qualifying for 2026 has been positive. This is a transitional squad — the old heroes (Modrić, Perišić, Kramarić) leading one last time while the next wave (Petar Sučić, Pongračić, Musa) integrates.

## Formation
- Shape: 4-3-3 (Modrić as advanced #8 / #10; Petar Sučić as the single pivot inheriting Brozović's role)
- Role mapping (roster order in `croatia.yaml`):
  - index 0: GK — Dominik Livaković (penalty-shootout specialist; reflex keeper; save 17)
  - index 1: LB — Joško Gvardiol (the captain-in-waiting; speed 16, strength 17 — modern ball-playing defender shifted to left-back with Sosa retired from the setup; overlaps and carries)
  - index 2: LCB — Josip Šutalo (physical; aerial duels)
  - index 3: RCB — Marin Pongračić (physical recovery from injury concerns; strength 17 — aggressive front-foot defending)
  - index 4: RB — Josip Stanišić (versatile; can play CB or RB; defensively responsible)
  - index 5: LCM/#8 — Mateo Kovačić (left interior; ball-carrier; dribble 17 — escapes pressure)
  - index 6: RCM/#8 (free) — Luka Modrić (captain, 40 years old; pass 19, skill 19 — the metronome AND the dagger)
  - index 7: DM/#6 — Petar Sučić (single pivot; high stamina 17; positionally disciplined; box-to-box energy the veterans lack)
  - index 8: LW — Ivan Perišić (veteran wide forward; crosses with left and right; physical)
  - index 9: CF — Andrej Kramarić (intelligent #9; drops short; creative finisher)
  - index 10: RW/CF — Petar Musa (mobile target forward; strength 17 — used for direct play, channel runs, and aerial battles)

## Style of Play

### Build-up
- Livaković short to Gvardiol or Šutalo (long-balls only if pressed).
- Petar Sučić drops between CBs in a 3-2 build; Modrić and Kovačić receive between lines.
- Gvardiol pushes high on the left as a carrier/overlapper; Stanišić more conservative on the right.
- **Croatia's build-up is slow on purpose** — they want to draw the opponent's midfield out, then escape via Modrić's dribble (dribble 17) into open space.

### Pressing
- Mid-block, not high press. Croatia's age profile (Modrić 40, Perišić 36) precludes intense pressing — but Petar Sučić now adds a younger pressing engine in front of the back four.
- Triggers: opponent long-ball wins by Šutalo/Pongračić; back-pass to opp GK; Kramarić curve-runs to cut switch.
- More often, Croatia sits in a 4-3-3 mid-block and lets opponents have territory, knowing midfield superiority means they can win the ball back in midfield.

### Defensive shape
- 4-3-3 / 4-1-4-1. Petar Sučić shields the CBs.
- Modrić's defensive contribution is minimal (age, energy preservation) — Kovačić and Petar Sučić do the running for him.
- Gvardiol is the line-setter and best athlete; Šutalo physical; Pongračić aggressive; Stanišić conservative.
- Vulnerable to pace in behind and direct play around their midfield.

### Wide play
- Asymmetric width:
  - **LEFT**: Perišić wide, Gvardiol overlaps from left-back to deliver crosses; Perišić's late-career role is now near-post header arrivals AND cross delivery.
  - **RIGHT**: Modrić drifts to the right half-space; Stanišić rarely overlaps; the right side is an inside-out structure where Modrić finds the pocket.
- Long, accurate crosses from Gvardiol → Kramarić, Perišić, Musa.

### Final third
- Three termination patterns:
  1. **Modrić line-break pass** — vertical through-ball into Kramarić or wide for Perišić's run.
  2. **Gvardiol overlap cross** — left-side delivery to the back post.
  3. **Modrić late shot** — outside the box, top corner (career signature).
- Kramarić is the false-9; he drops to combine with Modrić; Musa runs the channels and stretches the line for direct ball.
- Croatia does not high-tempo their final-third entries — they prefer 4-5 passes inside the box to disorganize.

## Set Pieces
- Corners: Modrić (right-side outswing) is the primary taker; Kovačić as the left-side alternative.
- Targets: Gvardiol (back post header), Šutalo, Pongračić, Musa.
- Direct FKs: Modrić centered (15+ years of practice); Perišić for power.
- Penalties: Modrić is the designated taker; Kramarić and Perišić as alternates.
- Defending: man-mark biggest threats; Livaković is elite under crosses — punches more than catches.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only long under triple pressure. In shootouts I am the difference — but in open play I am a distributor first.
2. When my `player_id` ends with `_1` (LB — Gvardiol): be the modern defender — carry the ball forward when the lane opens (speed 16 helps); overlap on the left for Perišić; switch to the right with long diagonals.
3. When my `player_id` ends with `_4` (RB — Stanišić): stay conservative on the right; tuck in to protect the half-space; only join attacks when safe.
4. When my `player_id` ends with `_7` (DM — Petar Sučić): single pivot; recycle possession; rarely above the halfway line in open play; protect the CBs at all costs; use stamina 17 to cover ground for the veterans.
5. When my `player_id` ends with `_5` (LCM — Kovačić): be the runner — cover for the `_6` (Modrić); carry the ball through pressure (dribble 17); do the defensive work for the right side of midfield too.
6. When my `player_id` ends with `_6` (RCM/free — Modrić) and team has the ball: take the most touches; pace the tempo; through-ball when an opportunity opens; Shoot from 22-28m with right foot if lane opens. Free role.
7. When my `player_id` ends with `_6` (RCM/free — Modrić) and team_phase is "defending": stay around the halfway line; do not press; conserve energy; intercept passes via positioning, not running.
8. When my `player_id` ends with `_8` (LW — Perišić): wide on the left; veteran role — make near-post runs on `_1` (Gvardiol) overlaps; crosses with either foot; tackle back is acceptable (stamina 15).
9. When my `player_id` ends with `_9` (CF — Kramarić): drop short into the #10 pocket to combine; late runs into the box; clever finisher (skill 16) — Shoot accuracy over power.
10. When my `player_id` ends with `_10` (RW/CF — Musa): mobile target; channel runs in behind; near-post or penalty-spot runs on crosses; physical battle with CBs (strength 17).
11. When team_phase is "defending" in mid-block: 4-3-3 → 4-1-4-1; the `_7` (Petar Sučić) protects; the `_6` (Modrić) walks; the `_5` (Kovačić) covers a lot of ground.
12. When ball is lost in own half: counter-press DOES NOT apply — Croatia retreats and reorganizes; first action is to deny verticality.
13. Shoot from outside the box only if my `player_id` ends with `_6`, `_5`, or `_8` (Modrić/Kovačić/Perišić).
14. Tackle: only the `_7`, `_5`, `_2`, and `_3` players (Petar Sučić/Kovačić/Šutalo/Pongračić) are licensed; others contain.

## Key Player Notes
- **Modrić (idx 6)** — captain, 40 years old, FREE ROLE at his sixth and final World Cup. Allowed to drift anywhere from RCM to #10. Energy preservation in defense, full license in attack. Primary set-piece and penalty taker. Croatia's tactical center of gravity.
- **Kovačić (idx 5)** — the runner. Covers ground that Modrić cannot. Ball-carrier under pressure. (Returning from Achilles trouble — monitor minutes.)
- **Petar Sučić (idx 7)** — the new single pivot inheriting Brozović's role. Without him, Modrić has no protection. High stamina engine that lets the veterans conserve energy. Set the line at the halfway mark.
- **Gvardiol (idx 1)** — the future captain and best athlete in the side; deployed at left-back with Sosa gone. Carries, overlaps, and delivers from the left. (Returning from a tibia fracture — monitor sharpness.)
- **Perišić (idx 8)** — veteran with energy issues but reliable in big moments.
- **Musa (idx 10)** — the new mobile centre-forward option; strength and channel running for direct play.

## Tournament Mindset
Outplay opponents in midfield. Croatia knows it cannot run with the press-heavy teams — so it slows the game, controls tempo, and trusts Modrić's vision to find the moment. Dalić has hinted at a more conservative, even three-at-the-back setup against stronger opponents (e.g. England in the group opener), but the default identity remains the 4-3-3 midfield-control model. Penalty shootouts are a Croatian comfort zone (Livaković saved 4 in 2022). Tournament knockouts are where this team thrives.
