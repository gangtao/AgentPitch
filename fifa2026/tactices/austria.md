# Austria — Tactical Profile

## Identity & Philosophy
Austria under Ralf Rangnick are the modern heirs to the Bielsa/Klopp pressing school — aggressive, vertical, ferocious in transition, and tactically uncompromising. Rangnick's gegenpress and "win it back within seconds" doctrine define them: they provoke the opponent into building out, swarm the carrier, and attack the vacated space the instant they regain. They stunned Euro 2024 by topping a group containing France and the Netherlands, and reached the knockout rounds of the World Cup as one of the most cohesive, drilled sides in the field — built around captain David Alaba, record scorer Marko Arnautović, and a German-Bundesliga spine (Seiwald, X. Schlager, Laimer, Sabitzer).

**Route to the Round of 16:** Austria came through Group J in second place — a 3-1 win over tournament debutants Jordan (their first World Cup win in 36 years, Schmid opening the scoring and Arnautović sealing it from the spot), a competitive 0-2 loss to eventual group winners Argentina, and a decisive result over Algeria to qualify. They now face Spain, the tournament's heaviest favourite, in a win-or-go-home last-16 tie at Los Angeles on 2 July.

**Selection watch (R16 vs Spain):** Both David Alaba (muscular tightness) and Marko Arnautović (withdrawn as a precaution in the group finale) picked up knocks late in the group stage, but Rangnick has played down the severity of both and both are on course to start. If either fails a fitness test, Kevin Danso is the ready-made central-defensive replacement and Michael Gregoritsch / Saša Kalajdžić are the alternate target men. Stefan Posch continues to wear a protective mask following the jaw fracture he suffered against Jordan. Alexander Schlager remains the undisputed No.1 (Pentz is the clear No.2).

## Formation
- Shape: 4-2-3-1 with a double pivot; FBs jump-press and push high (effectively 2-4-4 in the press). A back-three switch remains in Rangnick's locker if he wants extra central bodies against Spain.
- Role mapping (roster order in `austria.yaml`):
  - index 0: GK — Alexander Schlager (composed No.1, comfortable with the ball, plays short when the press is light)
  - index 1: LB — Phillipp Mwene (pressing fullback; leaves the line to attack wide receivers, jumps into midfield)
  - index 2: LCB — David Alaba (captain & ball-playing leader; highest-skill defender, pass 16 — the build-up brain who steps into midfield)
  - index 3: RCB — Philipp Lienhart (composed, aerially strong Freiburg centre-half; steps in for the injured/rotated Danso and defends the high line)
  - index 4: RB — Stefan Posch (physical, versatile pressing fullback; strength 16, aerial presence, wears a protective mask post jaw fracture)
  - index 5: LW — Romano Schmid (tireless wide worker; presses, combines inside, drifts into the half-space)
  - index 6: DM — Nicolas Seiwald (disciplined holder; the safety net behind X. Schlager, screens the back four)
  - index 7: DM/box-to-box — Xaver Schlager (all-action duel machine; wins it, carries 10m, releases Sabitzer)
  - index 8: AM/#10 — Marcel Sabitzer (creative hub; the transitions trigger man and second striker in the press, pass 16)
  - index 9: RW — Konrad Laimer (the engine repurposed wide-right; speed 16 / stamina 18, presses, overlaps and carries relentlessly)
  - index 10: CF — Marko Arnautović (target man; ageing but holds up play, leads the first press, primary penalty taker)

## Style of Play

### Build-up
- From Alexander Schlager: short to a CB only when the press is light; otherwise go long into Arnautović or clip a diagonal to a winger.
- The DM pair (Seiwald, X. Schlager) split either side of the CB pairing; Alaba steps into midfield to recycle and progress.
- Build-up is deliberately brief — the aim is to provoke the opponent's press, win the ball back high, and attack the vacated space, not to hold possession for its own sake. Against Spain, expect longer spells without the ball: the plan is to compress, wait for the pressing trigger, and strike vertically on the regain.

### Pressing
- **High block, gegenpress.** Press triggers (any of): opponent CB takes a touch oriented sideways or backward; a pass goes to the opposition fullback near the touchline (wide trap); the opposition GK plays short.
- The line of confrontation sits ~10m inside the opposition half. Arnautović triggers; the wingers (Schmid, Laimer) curve runs to lock the CBs; Sabitzer pushes up as a second striker.
- The instant Austria lose the ball, the nearest players swarm the carrier — Austria do NOT retreat first; they counter-press.
- Against Spain's positional possession, the press must be selective — spring the trap on the wide/backward pass, but avoid being pulled apart in central rotations. Discipline in the double pivot (Seiwald screening) is critical.

### Defensive shape
- 4-4-2 with Sabitzer alongside Arnautović during the press; settles to 4-2-3-1 when defending deeper.
- High line, accepting the risk in behind for the sake of compression and a short pitch — managed carefully against Spain's runners.
- Mwene and Posch are jump-pressers — they leave the back line to attack opposition wide receivers, with Lienhart/Alaba sliding across to cover.

### Wide play
- Asymmetric energy: **RIGHT** Posch (_4) overlaps and presses behind Laimer (_9), who carries and cuts inside. **LEFT** Schmid (_5) drifts inside into the half-space while Mwene (_1) provides the wide push.
- Half-space combinations around Sabitzer (_8) are Austria's most dangerous pattern; wingers arriving inside, not hugging the byline.

### Final third
- Quick combinations on the edge of the box. Arnautović holds up, Sabitzer arrives late between the lines, the wingers make near-post and back-post runs.
- Crosses are low and driven into the 6-yard box; cutbacks target Sabitzer arriving from deep.
- Against a superior side, transition moments and set pieces are Austria's likeliest source of goals — be ruthless with the few clear chances that come.

## Set Pieces
- Corners: Sabitzer and Seiwald deliver — inswingers, varied near-/far-post targets. Arnautović, Posch, Lienhart and Alaba are the primary aerial threats; Gregoritsch attacks the near post when on.
- Direct FKs: Alaba (left-footed from the right), Sabitzer (right-footed from the left); Arnautović for power central efforts.
- **Penalties (in-play):** Arnautović is first taker; Sabitzer is the alternate; Alaba third.
- **Penalty SHOOTOUT order (knockout — memorise this, a level tie goes to ET then spot-kicks):**
  1. Marko Arnautović (penalty 15) — ice-cold from the spot, scored the MD1 clincher vs Jordan
  2. Marcel Sabitzer (penalty 15) — the alternate first-taker, equally reliable
  3. David Alaba (penalty 14) — captain, will take a high-pressure kick
  4. Romano Schmid (penalty 13)
  5. Xaver Schlager (penalty 12) / Nicolas Seiwald (penalty 12) / Konrad Laimer (penalty 12) — next in line
  - If Arnautović has been substituted (fatigue/injury management late), Sabitzer steps up as No.1.
- Defending: man-orient on the biggest aerial threats; the holder (Seiwald) patrols the edge of the box for second balls.

## decide() Decision Priorities
1. **Counter-press trigger:** when Austria loses possession AND the ball is within 35m of where it was lost, ALL players within 15m of the ball must Tackle or close down immediately — swarm, do not retreat.
2. When my role is GK (`_0` — A. Schlager): pass short to a CB only if the press is light; otherwise go long to the `_10` player (Arnautović) or clip wide to a winger.
3. When my `player_id` ends with `_10` (CF — Arnautović): when the opposition GK has the ball, sprint diagonally to block the pass into the nearest CB — lead the first press; if play breaks down, drop to the halfway line as the emergency outlet.
4. When my `player_id` ends with `_5` or `_9` (wingers — Schmid/Laimer): on the press, curve runs to cut off the back-pass while approaching the wide CB; when isolated 1v1 with the fullback, Dribble inside — half-space arrival beats a wide cross.
5. When my `player_id` ends with `_7` (DM — X. Schlager): shadow the opposition #6; the moment they receive, Tackle. After winning it, carry forward and release the `_8` player (Sabitzer).
6. When my `player_id` ends with `_6` (DM — Seiwald): never venture forward of the halfway line — the safety net for `_7` (X. Schlager); shield the back four and recycle. Against Spain, hold this discipline even when the team is chasing the game.
7. When my `player_id` ends with `_8` (AM — Sabitzer): in possession, demand the ball facing forward in the half-space and turn forward — never backward (pass 16); out of possession, push up to become a second striker.
8. When my `player_id` ends with `_2` (LCB — Alaba, captain): if Austria win the ball in the opposition third, immediately Pass forward (no recycling); step into midfield to progress when the press is beaten.
9. When my `player_id` ends with `_1` (LB — Mwene): jump-press the opposition right winger when the ball is on Austria's left; a high line is acceptable, with `_2` (Alaba) covering behind.
10. When my `player_id` ends with `_4` (RB — Posch): jump-press the opposition left winger, with `_3` (Lienhart) sliding over to cover; overlap behind Laimer in attack. Physical strength 16 — win the aerial and shoulder duels.
11. On regain: nearest player to the ball Move forward into space; second-nearest demands the ball as a vertical pass option — go fast and vertical.
12. Shoot from outside the box only if my `player_id` ends with `_8` or `_10` (Sabitzer/Arnautović) AND there is a clear lane.
13. Against a heavy favourite: keep the structure, do NOT chase the game recklessly. If it is 0-0 or level late, protect the draw — a knockout tie level after 90 goes to extra time, and Austria back themselves in a shootout. Never park the bus, but do not gamble the tie away.

## Key Player Notes
- **David Alaba (idx 2, captain)** — the build-up brain and defensive organiser; primary left-side set-piece deliverer, steps into midfield to recycle. Highest-skill defender (skill 17, pass 16). Carrying muscular tightness into the tie but expected to start; Danso ready if he fails a fitness test.
- **Marcel Sabitzer (idx 8)** — the creative leader with maximum positional freedom; the #10 in possession and a second striker in the press. Corners/free-kicks, alternate in-play penalty taker and No.2 in the shootout order.
- **Marko Arnautović (idx 10)** — ageing but irreplaceable target man; leads the first press despite low speed, holds up play, and is the primary penalty taker (both in-play and first in the shootout). Withdrawn as a precaution in the group finale but on course to start; conserve his off-the-ball running for the press triggers.
- **Konrad Laimer (idx 9)** — the engine, deployed wide-right in the front band; speed 16 / stamina 18 make him both a press trigger and a relentless carrier who cuts inside off the right. Posch overlaps behind him.
- **Stefan Posch (idx 4)** — physical, versatile pressing right back; strength 16 and a major aerial threat at both boxes. Wearing a protective mask after fracturing his jaw against Jordan.
- **Philipp Lienhart (idx 3)** — composed, aerially strong Freiburg centre-half stepping in alongside Alaba; defends the high line and covers the jump-pressing fullbacks.
- **Xaver Schlager (idx 7)** — the duel machine in the double pivot: wins the ball, carries it forward, and releases Sabitzer.
- **Nicolas Seiwald (idx 6)** — the disciplined holding screen; the structural balance that lets the rest press without leaving the back four exposed. His discipline against Spain's rotations is pivotal.
- **Romano Schmid (idx 5)** — the tireless left-sided worker; opened the scoring on MD1, presses and combines into the half-space.

## Tournament Mindset
This is win-or-go-home. Austria reached the Round of 16 as Group J runners-up and now face Spain — the tournament's heaviest favourite — with no margin for error and no second leg. The maths of the group are behind them; there are no standings to manage, only 90 minutes (and, if level, 30 more of extra time and then a penalty shootout) that decide whether the campaign continues.

The plan is not to out-play Spain but to out-organise and out-fight them. Austria will not abandon the gegenpress — the press IS their identity — but they will press with discipline rather than abandon, springing the trap on the wide and backward passes and refusing to be pulled apart by Spain's central rotations. Concede possession, stay compact, protect the high line intelligently, and back the transition and set-piece moments to produce the one or two clear chances a game like this offers. If Austria can keep it level, they take heart from the knockout format: a tie level after 90 goes their way as often as not, and with Arnautović, Sabitzer and Alaba on the spot they are a genuinely dangerous shootout side. Identity, structure, and belief — punch above your weight, take the tie to the wire, and trust the shootout if it comes to that.
