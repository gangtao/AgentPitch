# Czechia — Tactical Profile

## Identity & Philosophy
Czechia under Ivan Hašek are a pragmatic, compact, set-piece reliant team that maximizes a limited talent pool through organization and aerial dominance. They are not a glamour side — they are a 4-4-2 mid-block that becomes vertical and direct in transition, with Patrik Schick and Tomáš Souček as the dual aerial reference points. The Czech identity is grit, second balls, and one quality moment in the final third.

## Formation
- Shape: 4-2-3-1 (becomes 4-4-2 defending, with Souček pushing onto Schick)
- Role mapping (roster order in `czechia.yaml`):
  - index 0 (`czechia_0`, Staněk): GK — solid, traditional, good on crosses.
  - index 1 (`czechia_1`, Krejčí): LB/LCB hybrid — comfortable in possession, can step out.
  - index 2 (`czechia_2`, Hranáč): LCB — physical, aerial.
  - index 3 (`czechia_3`, Holeš): RCB — disciplined, holds the line.
  - index 4 (`czechia_4`, Coufal): RB — overlapper, set-piece deliverer from the right.
  - index 5 (`czechia_5`, Souček): CM/box-arrival — aerial monster, late runs into the box.
  - index 6 (`czechia_6`, Šulc): CM — creative shuttler, links midfield to attack.
  - index 7 (`czechia_7`, Provod): LW — direct, cuts inside, shoots.
  - index 8 (`czechia_8`, Barák): AM/#10 — creator between the lines.
  - index 9 (`czechia_9`, Hložek): RW — pace, runs the channels.
  - index 10 (`czechia_10`, Schick): CF — primary target, aerial threat, clinical finisher.

## Style of Play

### Build-up
Direct. Staněk frequently goes long toward Schick or Souček; Czechia win the second ball and attack the chaos. When build-up is short, Krejčí carries from LB and Šulc drops to receive. Possession averages are low — this is not a possession-first team.

### Pressing (block height + trigger)
Low-to-mid block. Press triggers only on poor opposition touches in the build phase. Otherwise, Czechia drops into a 4-4-2 around the halfway line and waits to compress when the ball enters their third. Schick and Souček (in attacking transition) form the front two when pressing.

### Defensive shape
4-4-2 settled defense. Provod and Hložek tuck into a tight midfield bank. Barák drops alongside Souček to form a 4-4-1-1 if needed. Lines compact (~10m apart), block narrow, force opposition to play wide and cross.

### Wide play
Hložek and Provod stretch the play; Coufal overlaps with set-piece-quality delivery; Krejčí more reserved on the left. Crosses target Schick (back-post run) and Souček (near-post bullet headers).

### Final third
Crosses, set pieces, second balls. Provod cutting inside for a left-footed shot is a recurring pattern. Schick's movement against tiring CBs in the second half is the X-factor.

## Set Pieces
- Corners: Coufal delivers from the right (inswinger), Krejčí from the left (outswinger). Souček (near post bullet), Schick (back post), Hranáč (mid-box) are the primary targets. **Set pieces are Czechia's most reliable goal source.**
- Direct free kicks: Provod (left foot) from the right; Barák from the left.
- Penalties: Schick first; Souček second.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Staněk): if Czechia is pinned in own half for >15 seconds, kick long toward "_10" (Schick) on the next opportunity — Plan B is always active.
2. If my player_id ends with "_10" (CF, Schick): when GK has the ball, position centrally between CBs for a flick-on; after flicking, sprint into the channel.
3. If my player_id ends with "_5" (CM, Souček): on every wide attack, sprint toward the near post for a header. You are a SECOND striker in attacking phases.
4. If my player_id ends with "_4" (RB, Coufal): primary right-side crosser — when receiving wide right with space, CROSS to back post immediately.
5. If my player_id ends with "_7" (LW, Provod): when receiving wide left, cut inside diagonally; SHOOT from 22m if angle exists.
6. If my player_id ends with "_8" (AM, Barák): receive between lines, lay off to "_6" (Šulc) or release "_9" (Hložek) / "_7" (Provod) with quick vertical passes.
7. If my player_id ends with "_9" (RW, Hložek): make in-behind runs into the right channel; do NOT come short — stretch the back line vertically.
8. If my player_id ends with "_2" or "_3" (CBs, Hranáč/Holeš): clear LONG and HIGH when defending crosses — second balls are Czechia's friend.
9. If my player_id ends with "_6" (CM, Šulc): shuttle — when ball is on right flank, support "_4" (Coufal); when on left, support "_1" (Krejčí). Always offer a recycling option.
10. On opposition corner: "_5" (Souček) marks tallest attacker; "_10" (Schick) stays high at halfway line as counter outlet.
11. Counter-attack rule: on regain in own half, FIRST PASS must go forward (to "_10" Schick, "_9" Hložek's channel, or "_7" Provod). No recycling allowed.
12. When defending a 1-goal lead late: drop to a 5-4-1 by pushing "_1" (Krejčí) into a 3-CB shape; pack the box.

## Key Player Notes
- **Patrik Schick (index 10):** primary striker, shoot 16. Operates almost exclusively in the box — minimize his wandering. Top finisher when given chances.
- **Tomáš Souček (index 5):** dual-role — CM in defense, second striker on every set piece and wide cross. His aerial presence is half of Czechia's attacking plan.
- **Vladimír Coufal (index 4):** primary set-piece deliverer from the right. His crosses are weapon-grade.
- **Lukáš Provod (index 7):** inverted left winger — direct him to cut in and shoot rather than cross.
- **Antonín Barák (index 8):** the team's #10 creator. Free role between the lines, two-way distance covered.

## Tournament Mindset
Czechia are the team nobody wants in the knockouts. They will sit deep, score from a corner, and run down the clock. Their ceiling is limited by individual quality, but their floor is high because of organizational discipline.
