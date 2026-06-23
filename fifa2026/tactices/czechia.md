# Czechia — Tactical Profile

## Identity & Philosophy
Czechia under Miroslav Koubek are a pragmatic, compact, set-piece reliant team that maximizes a limited talent pool through organization and aerial dominance. They are not a glamour side — they are a physical mid-block that becomes vertical and direct in transition, with Patrik Schick and Tomáš Souček as the dual aerial reference points. The Czech identity is grit, second balls, and one quality moment in the final third.

**Matchday 3 update (24 June, vs Mexico — must win):** Czechia sit third in Group A on **1 point** after a 1-1 draw with South Africa, and only a win against the hosts at the Estadio Azteca (Mexico City) will keep their qualification hopes alive. This is a do-or-die game and Koubek has shifted to a more aggressive **3-5-2** with **two strikers** — Schick partnered by Adam Hložek — to chase the result. The structural blow is the loss of first-choice left wingback **David Jurásek**, who suffered a tournament-ending thigh injury in training; veteran Slavia Prague defender **Jaroslav Zelený** comes in at left wingback. Lukáš Červ takes the box-to-box role alongside Souček, with Pavel Šulc pushed up as the lone advanced playmaker (#10) feeding the front two. The intent is clear: stay compact when needed, but commit numbers forward and win it on the night.

## Formation
- Shape: 3-5-2 (becomes a back five / 5-3-2 defending, with the wingbacks dropping into the back line)
- Role mapping (roster order in `czechia.yaml`):
  - index 0 (`czechia_0`, Kovář): GK — solid, traditional, good on crosses.
  - index 1 (`czechia_1`, Holeš): left center-back — converted midfielder, positionally intelligent, comfortable stepping into midfield.
  - index 2 (`czechia_2`, Krejčí): central center-back / captain — comfortable in possession, organizes the back three, can step out and carry.
  - index 3 (`czechia_3`, Hranáč): right center-back — physical, aerial, holds the line.
  - index 4 (`czechia_4`, Zelený): left wingback — experienced, disciplined, provides the width on the left in place of the injured Jurásek; defends first, supports the attack second.
  - index 5 (`czechia_5`, Červ): box-to-box CM — energetic shuttler, carries through midfield, arrives late, covers ground for the two strikers.
  - index 6 (`czechia_6`, Souček): CM/box-arrival — aerial monster, late runs into the box, the team's primary dead-ball striker.
  - index 7 (`czechia_7`, Coufal): right wingback — overlapper, set-piece deliverer from the right.
  - index 8 (`czechia_8`, Šulc): advanced #10 — chief creator, links midfield to the front two, plays between the lines.
  - index 9 (`czechia_9`, Hložek): striker — direct, mobile second striker, runs the channels off Schick, shoots early.
  - index 10 (`czechia_10`, Schick): striker — primary target, aerial threat, clinical finisher.

## Style of Play

### Build-up
Direct. Kovář frequently goes long toward Schick or Souček; Czechia win the second ball and attack the chaos. When build-up is short, Krejčí carries from the centre of the back three and Červ drops to receive. Possession averages are low — this is not a possession-first team — but with two strikers and a must-win mandate, Czechia commit more bodies forward than usual.

### Pressing (block height + trigger)
Mid block, willing to press higher than normal given the must-win situation. Press triggers on poor opposition touches in the build phase and on backward passes from the Mexican center-backs. When the block sits, Czechia drops into a compact 5-3-2 and compresses when the ball enters their third. Schick and Hložek lead the line as a front two, screening the central lanes.

### Defensive shape
Settled defense is a back five: wingbacks Zelený and Coufal drop alongside the three center-backs, with Souček and Červ shielding in front and Šulc tucking into the midfield line. Lines compact (~10m apart), block narrow, force the opposition to play wide and cross. The two strikers stay forward as a counter outlet rather than chasing back fully.

### Wide play
Coufal and Zelený provide the width from wingback; Coufal overlaps with set-piece-quality delivery on the right, Zelený attacks the left channel more cautiously and prioritizes his defensive duties. Crosses target Schick (back-post run), Hložek (channel runs), and Souček (near-post bullet headers).

### Final third
Crosses, set pieces, second balls, and direct combinations between Schick and Hložek. With two strikers, the near-post / back-post double threat on crosses is the core pattern. Schick's movement against tiring CBs in the second half is the X-factor; Šulc's between-the-lines passing is the chief supply line.

## Set Pieces
- Corners: Coufal delivers from the right (inswinger), Zelený from the left. Souček (near post bullet), Schick (back post), Hranáč (mid-box) are the primary targets. **Set pieces are Czechia's most reliable goal source — they scored more set-piece goals than any other European nation in 2026 qualifying.**
- Direct free kicks: Souček is the primary striker of dead balls; Hložek (shoot 15) is the secondary option.
- Penalties: Souček first; Schick second.

## decide() Decision Priorities
1. If my player_id ends with "_0" (GK, Kovář): if Czechia is pinned in own half for >15 seconds, kick long toward "_10" (Schick) on the next opportunity — Plan B is always active.
2. If my player_id ends with "_10" (striker, Schick): when GK has the ball, position centrally between CBs for a flick-on; after flicking, sprint into the channel. In the box, this is the finisher — shoot 16.
3. If my player_id ends with "_6" (CM, Souček): on every wide attack, sprint toward the near post for a header. You are a SECOND striker in attacking phases and the primary dead-ball striker.
4. If my player_id ends with "_7" (RWB, Coufal): primary right-side crosser — when receiving wide right with space, CROSS to the back post immediately.
5. If my player_id ends with "_8" (advanced #10, Šulc): receive between lines, then play a quick vertical ball to "_10" (Schick) or "_9" (Hložek); release "_7" (Coufal) on the overlap when the right channel opens.
6. If my player_id ends with "_9" (striker, Hložek): play off "_10" (Schick) — attack the channels and the right half-space and SHOOT early from 20m if the angle exists.
7. If my player_id ends with "_4" (LWB, Zelený): provide width on the left but DEFEND FIRST — only commit forward when the ball is settled in the opposition half; you are the more conservative of the two wingbacks. Recover fast.
8. If my player_id ends with "_1" or "_3" (CBs, Holeš/Hranáč): clear LONG and HIGH when defending crosses — second balls are Czechia's friend.
9. If my player_id ends with "_5" (CM, Červ): shuttle and carry — when ball is on the right flank, support "_7" (Coufal); when on the left, support "_4" (Zelený). Always offer a recycling option in front of the back three, and arrive late into the box on attacks.
10. On opposition corner: "_6" (Souček) marks tallest attacker; "_10" (Schick) and "_9" (Hložek) stay high near halfway as counter outlets.
11. Counter-attack rule: on regain in own half, FIRST PASS must go forward (to "_10" Schick, "_9" Hložek, or "_8" Šulc). No recycling allowed.
12. When chasing a goal late (must-win): push "_7" (Coufal) and "_4" (Zelený) high, commit "_5" (Červ) and "_6" (Souček) into the box on crosses, and overload the penalty area around the front two.

## Key Player Notes
- **Patrik Schick (index 10):** primary striker, shoot 16. Operates almost exclusively in the box — minimize his wandering. Top finisher when given chances; the man Czechia need to come alive in a must-win game.
- **Adam Hložek (index 9):** mobile second striker (shoot 15) — direct him to run the channels off Schick and shoot early rather than over-elaborate. Czechia's two-striker shift is built around this partnership.
- **Tomáš Souček (index 6):** dual-role — CM in defense, second striker on every set piece and wide cross. His aerial presence is half of Czechia's attacking plan, and he is the team's primary dead-ball striker.
- **Vladimír Coufal (index 7):** right wingback and primary set-piece deliverer from the right. His crosses are weapon-grade.
- **Pavel Šulc (index 8):** the team's chief creator, now pushed up as the lone advanced #10 supplying the front two; two-way distance covered.
- **Lukáš Červ (index 5):** the new box-to-box engine alongside Souček — covers ground, carries, and arrives late.
- **Jaroslav Zelený (index 4):** experienced replacement at left wingback for the injured David Jurásek — defensively reliable, provides width without over-committing.
- **Ladislav Krejčí (index 2):** captain and central center-back — the most press-resistant of the back three, steps out to carry into midfield.

## Tournament Mindset
Czechia are the team nobody wants in the knockouts — but right now they are staring at the exit. Returning to the World Cup after a 20-year absence via back-to-back penalty-shootout playoff wins, they sit third in Group A on 1 point and must beat hosts Mexico at the Estadio Azteca to survive. The plan is unchanged in spirit — sit compact, score from a corner, lean on Schick — but the situation forces ambition: a two-striker 3-5-2, a higher press in spells, and numbers committed forward. Their floor is high because of organizational discipline; their ceiling, and their tournament, now depends on one big night in Mexico City against South Korea's group rivals and the unbeaten hosts.
