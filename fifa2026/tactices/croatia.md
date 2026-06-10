# Croatia — Tactical Profile

## Identity & Philosophy
Zlatko Dalić's Croatia remains a masterclass in possession-based tournament football — the smallest nation that consistently outplays its weight class. The team's identity is built around **midfield superiority**: Modrić (40 years old, still the captain) and Kovačić form one of the most technical midfield pairings in world football history, now deployed as the double pivot of a 4-2-3-1. Croatia will out-pass opponents, slow tempos, and break through patient build-up. Recent results: World Cup 2022 third place, Euro 2024 group exit (early sign of generational decline), but qualifying for 2026 has been positive. This is a transitional squad — the old heroes (Modrić, Perišić, Kramarić) leading one last time while the next wave (Luka Vušković, Marco Pašalić) integrates.

## Formation
- Shape: 4-2-3-1 (Modrić and Kovačić as the double pivot; Kramarić as the #10 behind Budimir)
- Role mapping (roster order in `croatia.yaml`):
  - index 0: GK — Dominik Livaković (penalty-shootout specialist; reflex keeper; save 17)
  - index 1: LB — Joško Gvardiol (the captain-in-waiting; speed 16, strength 17 — modern ball-playing defender deployed at left-back; overlaps and carries)
  - index 2: LCB — Duje Ćaleta-Car (physical; strength 17 — aerial duels, no-frills clearances)
  - index 3: RCB — Luka Vušković (the teenage Tottenham prodigy; strength 17 — aerial monster, front-foot defending, surprisingly composed feet)
  - index 4: RB — Josip Stanišić (versatile; can play CB or RB; defensively responsible)
  - index 5: DM — Mateo Kovačić (left side of the double pivot; ball-carrier; dribble 17 — escapes pressure and does the running)
  - index 6: DM (free) — Luka Modrić (captain, 40 years old; pass 19, skill 19 — the metronome AND the dagger, dictating from deep)
  - index 7: LAM — Ivan Perišić (veteran wide attacker; crosses with left and right; physical)
  - index 8: AM/#10 — Andrej Kramarić (intelligent #10; drops short; creative finisher behind the striker)
  - index 9: RAM — Marco Pašalić (speed 15 — direct young wide threat, stretches play on the right, runs in behind)
  - index 10: ST — Ante Budimir (penalty-box target striker; strength 16, shoot 16 — attacks crosses, finishes first-time)

## Style of Play

### Build-up
- Livaković short to Gvardiol or Ćaleta-Car (long-balls only if pressed).
- Kovačić drops between the CBs in a 3-1 build; Modrić stays a line higher, with Kramarić dropping from the 10 to receive between lines.
- Gvardiol pushes high on the left as a carrier/overlapper; Stanišić more conservative on the right.
- **Croatia's build-up is slow on purpose** — they want to draw the opponent's midfield out, then escape via Modrić's dribble (dribble 17) into open space.

### Pressing
- Mid-block, not high press. Croatia's age profile (Modrić 40, Perišić 36) precludes intense pressing — but Pašalić adds younger pressing legs in the attacking band.
- Triggers: opponent long-ball wins by Ćaleta-Car/Vušković; back-pass to opp GK; Kramarić curve-runs to cut switch.
- More often, Croatia sits in a 4-2-3-1 mid-block and lets opponents have territory, knowing midfield superiority means they can win the ball back in midfield.

### Defensive shape
- 4-2-3-1 → 4-4-1-1. The Kovačić–Modrić pivot shields the CBs; Perišić and Pašalić drop onto the wide midfield slots.
- Modrić's defensive contribution is minimal (age, energy preservation) — Kovačić does the running for him.
- Gvardiol is the line-setter and best athlete; Ćaleta-Car physical; Vušković aggressive in the air; Stanišić conservative.
- Vulnerable to pace in behind and direct play around their midfield.

### Wide play
- Asymmetric width:
  - **LEFT**: Perišić wide, Gvardiol overlaps from left-back to deliver crosses; Perišić's late-career role is now near-post header arrivals AND cross delivery.
  - **RIGHT**: Pašalić holds genuine width and runs in behind; Modrić drifts to the right half-space from the pivot to find the pocket; Stanišić rarely overlaps.
- Long, accurate crosses from Gvardiol → Budimir, Kramarić, Perišić.

### Final third
- Three termination patterns:
  1. **Modrić line-break pass** — vertical through-ball into Kramarić's feet or in behind for Pašalić's run.
  2. **Gvardiol overlap cross** — left-side delivery to Budimir attacking the near post or back post.
  3. **Modrić late shot** — outside the box, top corner (career signature).
- Kramarić is the 10; he drops to combine with Modrić; Budimir pins the CBs and lives on crosses and cutbacks.
- Croatia does not high-tempo their final-third entries — they prefer 4-5 passes inside the box to disorganize.

## Set Pieces
- Corners: Modrić (right-side outswing) is the primary taker; Kovačić as the left-side alternative.
- Targets: Gvardiol (back post header), Vušković, Ćaleta-Car, Budimir.
- Direct FKs: Modrić centered (15+ years of practice); Perišić for power.
- Penalties: Modrić is the designated taker; Kramarić and Budimir as alternates.
- Defending: man-mark biggest threats; Livaković is elite under crosses — punches more than catches.

## decide() Decision Priorities
1. When my role is GK: always pass short to a CB; only long under triple pressure. In shootouts I am the difference — but in open play I am a distributor first.
2. When my `player_id` ends with `_1` (LB — Gvardiol): be the modern defender — carry the ball forward when the lane opens (speed 16 helps); overlap on the left for Perišić; switch to the right with long diagonals.
3. When my `player_id` ends with `_4` (RB — Stanišić): stay conservative on the right; tuck in to protect the half-space; only join attacks when safe.
4. When my `player_id` ends with `_5` (DM — Kovačić): be the runner of the double pivot — cover for the `_6` (Modrić); carry the ball through pressure (dribble 17); protect the CBs; do the defensive work for both sides of midfield.
5. When my `player_id` ends with `_6` (DM/free — Modrić) and team has the ball: take the most touches; pace the tempo; through-ball when an opportunity opens; Shoot from 22-28m with right foot if lane opens. Free role from deep.
6. When my `player_id` ends with `_6` (DM/free — Modrić) and team_phase is "defending": stay around the halfway line; do not press; conserve energy; intercept passes via positioning, not running.
7. When my `player_id` ends with `_7` (LAM — Perišić): wide on the left; veteran role — make near-post runs on `_1` (Gvardiol) overlaps; crosses with either foot; tackle back is acceptable (stamina 15).
8. When my `player_id` ends with `_8` (AM/#10 — Kramarić): drop short into the #10 pocket to combine; late runs into the box; clever finisher (skill 16) — Shoot accuracy over power.
9. When my `player_id` ends with `_9` (RAM — Pašalić): hold width on the right; run in behind with pace (speed 15); track the opposition LB diligently — the youngest legs in the band do the most pressing.
10. When my `player_id` ends with `_10` (ST — Budimir): penalty-box target; near-post or penalty-spot runs on crosses; physical battle with CBs (strength 16); finish first-time (shoot 16).
11. When team_phase is "defending" in mid-block: 4-2-3-1 → 4-4-1-1; the `_5` (Kovačić) protects and covers a lot of ground; the `_6` (Modrić) walks; `_7` (Perišić) and `_9` (Pašalić) drop to the wide midfield slots.
12. When ball is lost in own half: counter-press DOES NOT apply — Croatia retreats and reorganizes; first action is to deny verticality.
13. Shoot from outside the box only if my `player_id` ends with `_6`, `_5`, or `_7` (Modrić/Kovačić/Perišić).
14. Tackle: only the `_5`, `_2`, and `_3` players (Kovačić/Ćaleta-Car/Vušković) are licensed; others contain.

## Key Player Notes
- **Modrić (idx 6)** — captain, 40 years old, FREE ROLE at his sixth and final World Cup. Allowed to drift anywhere from the pivot to the #10 pocket. Energy preservation in defense, full license in attack. Primary set-piece and penalty taker. Croatia's tactical center of gravity.
- **Kovačić (idx 5)** — the runner of the double pivot. Covers ground that Modrić cannot. Ball-carrier under pressure. (Returning from Achilles trouble — monitor minutes.)
- **Vušković (idx 3)** — the teenage Tottenham centre-back fast-tracked into the XI. Aerial monster (strength 17), aggressive, a set-piece weapon at both ends.
- **Gvardiol (idx 1)** — the future captain and best athlete in the side; deployed at left-back. Carries, overlaps, and delivers from the left. (Returning from a tibia fracture — monitor sharpness.)
- **Perišić (idx 7)** — veteran with energy issues but reliable in big moments.
- **Budimir (idx 10)** — the penalty-box poacher; lives on Gvardiol and Perišić crosses; shoot 16, strength 16.

## Tournament Mindset
Outplay opponents in midfield. Croatia knows it cannot run with the press-heavy teams — so it slows the game, controls tempo, and trusts Modrić's vision to find the moment. Dalić has hinted at a more conservative, even three-at-the-back setup against stronger opponents (e.g. England in the group opener), but the default identity remains the 4-2-3-1 midfield-control model. Penalty shootouts are a Croatian comfort zone (Livaković saved 4 in 2022). Tournament knockouts are where this team thrives.
