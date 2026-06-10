# Czechia — Tactical Profile

## Identity & Philosophy
Czechia under Miroslav Koubek are a pragmatic, compact, set-piece reliant team that maximizes a limited talent pool through organization and aerial dominance. They are not a glamour side — they are a physical mid-block that becomes vertical and direct in transition, with Patrik Schick and Tomáš Souček as the dual aerial reference points. The Czech identity is grit, second balls, and one quality moment in the final third.

## Formation
- Shape: 3-4-2-1 (becomes a back five / 5-4-1 defending, with the wingbacks dropping into the back line)
- Role mapping (roster order in `czechia.yaml`):
  - index 0 (`czechia_0`, Kovář): GK — solid, traditional, good on crosses.
  - index 1 (`czechia_1`, Holeš): left center-back — converted midfielder, positionally intelligent, comfortable stepping into midfield.
  - index 2 (`czechia_2`, Krejčí): central center-back / captain — comfortable in possession, organizes the back three, can step out and carry.
  - index 3 (`czechia_3`, Hranáč): right center-back — physical, aerial, holds the line.
  - index 4 (`czechia_4`, Jurásek): left wingback — energetic, gets forward, recovers fast.
  - index 5 (`czechia_5`, Darida): CM — deep-lying metronome, recycles and dictates tempo.
  - index 6 (`czechia_6`, Souček): CM/box-arrival — aerial monster, late runs into the box.
  - index 7 (`czechia_7`, Coufal): right wingback — overlapper, set-piece deliverer from the right.
  - index 8 (`czechia_8`, Šulc): left #10 — creative, links midfield to attack between the lines.
  - index 9 (`czechia_9`, Hložek): right #10 — direct second striker, plays off Schick, shoots early.
  - index 10 (`czechia_10`, Schick): CF — primary target, aerial threat, clinical finisher.

## Style of Play

### Build-up
Direct. Kovář frequently goes long toward Schick or Souček; Czechia win the second ball and attack the chaos. When build-up is short, Krejčí carries from the centre of the back three and Darida drops to receive. Possession averages are low — this is not a possession-first team.

### Pressing (block height + trigger)
Low-to-mid block. Press triggers only on poor opposition touches in the build phase. Otherwise, Czechia drops into a compact 5-4-1 / mid-block and waits to compress when the ball enters their third. Schick (with Souček in attacking transition) leads the line when pressing.

### Defensive shape
Settled defense is a back five: wingbacks Jurásek and Coufal drop alongside the three center-backs, with Souček and Darida shielding in front and the two #10s (Šulc, Hložek) tucking in. Lines compact (~10m apart), block narrow, force opposition to play wide and cross.

### Wide play
Coufal and Jurásek provide the width from wingback; Coufal overlaps with set-piece-quality delivery on the right, Jurásek attacks the left channel. Crosses target Schick (back-post run) and Souček (near-post bullet headers).

### Final third
Crosses, set pieces, second balls. Hložek peeling off Schick to hit an early shot is a recurring pattern. Schick's movement against tiring CBs in the second half is the X-factor.

## Set Pieces
- Corners: Coufal delivers from the right (inswinger), Jurásek from the left. Souček (near post bullet), Schick (back post), Hranáč (mid-box) are the primary targets. **Set pieces are Czechia's most reliable goal source — they scored more set-piece goals than any other European nation in 2026 qualifying.**
- Direct free kicks: Souček is the primary striker of dead balls; Hložek (shoot 15) is the secondary option.
- Penalties: Souček first; Schick second.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Kovář): if Czechia is pinned in own half for >15 seconds, kick long toward "_10" (Schick) on the next opportunity — Plan B is always active.
2. If my player_id ends with "_10" (CF, Schick): when GK has the ball, position centrally between CBs for a flick-on; after flicking, sprint into the channel.
3. If my player_id ends with "_6" (CM, Souček): on every wide attack, sprint toward the near post for a header. You are a SECOND striker in attacking phases.
4. If my player_id ends with "_7" (RWB, Coufal): primary right-side crosser — when receiving wide right with space, CROSS to back post immediately.
5. If my player_id ends with "_8" (left #10, Šulc): receive between lines, lay off to "_5" (Darida) or release "_7" (Coufal) / "_9" (Hložek) with quick vertical passes.
6. If my player_id ends with "_9" (right #10, Hložek): play off "_10" (Schick) — attack the right half-space and SHOOT early from 20m if angle exists.
7. If my player_id ends with "_4" (LWB, Jurásek): make overlapping runs down the left channel; deliver into the box, then recover fast — you are the deepest of the two wingbacks defensively.
8. If my player_id ends with "_1" or "_3" (CBs, Holeš/Hranáč): clear LONG and HIGH when defending crosses — second balls are Czechia's friend.
9. If my player_id ends with "_5" (CM, Darida): shuttle and recycle — when ball is on right flank, support "_7" (Coufal); when on left, support "_4" (Jurásek). Always offer a recycling option in front of the back three.
10. On opposition corner: "_6" (Souček) marks tallest attacker; "_10" (Schick) stays high at halfway line as counter outlet.
11. Counter-attack rule: on regain in own half, FIRST PASS must go forward (to "_10" Schick, "_8" Šulc, or "_9" Hložek). No recycling allowed.
12. When defending a 1-goal lead late: collapse the back five into a 5-4-1 low block; push "_8" (Šulc) and "_9" (Hložek) into the midfield bank and pack the box.

## Key Player Notes
- **Patrik Schick (index 10):** primary striker, shoot 16. Operates almost exclusively in the box — minimize his wandering. Top finisher when given chances.
- **Tomáš Souček (index 6):** dual-role — CM in defense, second striker on every set piece and wide cross. His aerial presence is half of Czechia's attacking plan, and he is the team's primary dead-ball striker.
- **Vladimír Coufal (index 7):** right wingback and primary set-piece deliverer from the right. His crosses are weapon-grade.
- **Adam Hložek (index 9):** direct right #10 / second striker (shoot 15) — direct him to play off Schick and shoot early rather than over-elaborate.
- **Ladislav Krejčí (index 2):** captain and central center-back — the most press-resistant of the back three, steps out to carry into midfield.
- **Pavel Šulc (index 8):** the team's chief creator between the lines, two-way distance covered.

## Tournament Mindset
Czechia are the team nobody wants in the knockouts. They will sit deep, score from a corner, and run down the clock. Returning to the World Cup after a 20-year absence via back-to-back penalty-shootout playoff wins, their ceiling is limited by individual quality, but their floor is high because of organizational discipline. They sit in Group A alongside hosts Mexico, South Korea, and South Africa.
