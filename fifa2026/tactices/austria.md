# Austria — Tactical Profile

## Identity & Philosophy
Austria under Ralf Rangnick are the modern heirs to the Bielsa/Klopp pressing school — aggressive, vertical, ferocious in transition, and tactically uncompromising. Rangnick's gegenpress and "win it back within seconds" doctrine define them: they provoke the opponent into building out, swarm the carrier, and attack the vacated space the instant they regain. They stunned Euro 2024 by topping a group containing France and the Netherlands, and arrive at the World Cup as one of the most cohesive, drilled sides in the field — built around captain David Alaba, record scorer Marko Arnautović, and a German-Bundesliga spine (Seiwald, X. Schlager, Laimer, Sabitzer).

**Matchday 1 (vs Jordan — 3-1 win):** Austria opened Group J with a 3-1 victory over tournament debutants Jordan, earning their first World Cup win in 36 years. Romano Schmid opened the scoring (20'), Austria added a Yazan Al-Arab own goal (76'), and Arnautović sealed it from the spot deep into stoppage time (90+12') — making the 37-year-old Austria's oldest-ever World Cup scorer.

**Matchday 2 (vs Argentina — 0-2 loss):** Austria pressed the world champions but were undone by Lionel Messi, who scored in the 38th and 90+5th minutes — surpassing Miroslav Klose to become the all-time leading men's World Cup goalscorer (18). Austria competed but Argentina's quality through and around the press told. No suspensions or major injuries carried out of the match; the squad is close to full strength for MD3.

**Matchday 3 context (vs Algeria — Group J decider):** Argentina have sealed top spot on 6 points. Austria (3 pts, GD 0) and Algeria (3 pts, GD -2) are level on points, fighting for the second qualifying place — a straight shootout for the Round of 32. Crucially, Austria's superior goal difference means a draw is enough to go through; Algeria must win. Expect Austria to press but manage risk, denying Algeria the transitions they thrive on. The chief selection watch remains the wide-forward band and fullback (Posch/Mwene), with Patrick Wimmer's pace a starting option on the right and Michael Gregoritsch the alternate target/near-post finisher.

## Formation
- Shape: 4-2-3-1 with a double pivot; FBs jump-press and push high (effectively 2-4-4 in the press)
- Role mapping (roster order in `austria.yaml`):
  - index 0: GK — Alexander Schlager (composed No.1, comfortable with the ball, plays short when the press is light)
  - index 1: LB — Phillipp Mwene (pressing fullback; leaves the line to attack wide receivers, jumps into midfield)
  - index 2: LCB — David Alaba (captain & ball-playing leader; highest-skill defender, pass 16 — the build-up brain who steps into midfield)
  - index 3: RCB — Kevin Danso (physical, aggressive; strength 16, comfortable defending the high line)
  - index 4: RB — Konrad Laimer (the engine repurposed wide; stamina 18, presses and overlaps relentlessly on the right)
  - index 5: DM — Nicolas Seiwald (disciplined holder; the safety net behind X. Schlager, screens the back four)
  - index 6: DM/box-to-box — Xaver Schlager (all-action duel machine; wins it, carries 10m, releases Sabitzer)
  - index 7: LW — Romano Schmid (tireless wide worker; presses, combines inside, drifts into the half-space)
  - index 8: AM/#10 — Marcel Sabitzer (creative hub; the transitions trigger man and second striker in the press, pass 16)
  - index 9: RW — Patrick Wimmer (direct, pacey wide threat; speed 16 / dribble 16, takes on the FB and cuts inside)
  - index 10: CF — Marko Arnautović (target man; ageing but holds up play, leads the first press, primary penalty taker)

## Style of Play

### Build-up
- From Alexander Schlager: short to a CB only when the press is light; otherwise go long into Arnautović or clip a diagonal to a winger.
- The DM pair (Seiwald, X. Schlager) split either side of the CB pairing; Alaba steps into midfield to recycle and progress.
- Build-up is deliberately brief — the aim is to provoke the opponent's press, win the ball back high, and attack the vacated space, not to hold possession for its own sake.

### Pressing
- **High block, gegenpress.** Press triggers (any of): opponent CB takes a touch oriented sideways or backward; a pass goes to the opposition fullback near the touchline (wide trap); the opposition GK plays short.
- The line of confrontation sits ~10m inside the opposition half. Arnautović triggers; the wingers (Schmid, Wimmer) curve runs to lock the CBs; Sabitzer pushes up as a second striker.
- The instant Austria lose the ball, the nearest players swarm the carrier — Austria do NOT retreat first; they counter-press.

### Defensive shape
- 4-4-2 with Sabitzer alongside Arnautović during the press; settles to 4-2-3-1 when defending deeper.
- High line, accepting the risk in behind for the sake of compression and a short pitch.
- Mwene and Laimer are jump-pressers — they leave the back line to attack opposition wide receivers, with Danso/Alaba sliding across to cover.

### Wide play
- Asymmetric energy: **RIGHT** Laimer (_4) overlaps and presses behind Wimmer (_9), who takes on the FB and cuts inside. **LEFT** Schmid (_7) drifts inside into the half-space while Mwene (_1) provides the wide push.
- Half-space combinations around Sabitzer (_8) are Austria's most dangerous pattern; wingers arriving inside, not hugging the byline.

### Final third
- Quick combinations on the edge of the box. Arnautović holds up, Sabitzer arrives late between the lines, the wingers make near-post and back-post runs.
- Crosses are low and driven into the 6-yard box; cutbacks target Sabitzer arriving from deep.

## Set Pieces
- Corners: Sabitzer and Seiwald deliver — inswingers, varied near-/far-post targets. Arnautović, Danso and Alaba are the primary aerial threats; Gregoritsch attacks the near post when on.
- Direct FKs: Alaba (left-footed from the right), Sabitzer (right-footed from the left); Arnautović for power central efforts.
- Penalties: Arnautović is first taker; Sabitzer is the alternate.
- Defending: man-orient on the biggest aerial threats; the holder (Seiwald) patrols the edge of the box for second balls.

## decide() Decision Priorities
1. **Counter-press trigger:** when Austria loses possession AND the ball is within 35m of where it was lost, ALL players within 15m of the ball must Tackle or close down immediately — swarm, do not retreat.
2. When my role is GK (`_0` — A. Schlager): pass short to a CB only if the press is light; otherwise go long to the `_10` player (Arnautović) or clip wide to a winger.
3. When my `player_id` ends with `_10` (CF — Arnautović): when the opposition GK has the ball, sprint diagonally to block the pass into the right CB — lead the first press; if play breaks down, drop to the halfway line as the emergency outlet.
4. When my `player_id` ends with `_7` or `_9` (wingers — Schmid/Wimmer): on the press, curve runs to cut off the back-pass while approaching the wide CB; when isolated 1v1 with the fullback, Dribble inside — half-space arrival beats a wide cross.
5. When my `player_id` ends with `_6` (DM — X. Schlager): shadow the opposition #6; the moment they receive, Tackle. After winning it, carry forward and release the `_8` player (Sabitzer).
6. When my `player_id` ends with `_5` (DM — Seiwald): never venture forward of the halfway line — the safety net for `_6` (X. Schlager); shield the back four and recycle.
7. When my `player_id` ends with `_8` (AM — Sabitzer): in possession, demand the ball facing forward in the half-space and turn forward — never backward (pass 16); out of possession, push up to become a second striker.
8. When my `player_id` ends with `_2` (LCB — Alaba, captain): if Austria win the ball in the opposition third, immediately Pass forward (no recycling); step into midfight to progress when the press is beaten.
9. When my `player_id` ends with `_1` (LB — Mwene): jump-press the opposition right winger when the ball is on Austria's left; a high line is acceptable.
10. When my `player_id` ends with `_4` (RB — Laimer): jump-press the opposition left winger — stamina 18 lets him press and recover, with `_3` (Danso) sliding over to cover; overlap behind Wimmer in attack.
11. On regain: nearest player to the ball Move forward into space; second-nearest demands the ball as a vertical pass option — go fast and vertical.
12. Shoot from outside the box only if my `player_id` ends with `_8` or `_10` (Sabitzer/Arnautović) AND there is a clear lane.
13. When leading with under 10 minutes, drop the line of confrontation by ~10m and stay compact — never park the bus.

## Key Player Notes
- **David Alaba (idx 2, captain)** — the build-up brain and defensive organiser; primary left-side set-piece deliverer, steps into midfield to recycle. Highest-skill defender (skill 17, pass 16).
- **Marcel Sabitzer (idx 8)** — the creative leader with maximum positional freedom; the #10 in possession and a second striker in the press. Corners/free-kicks and alternate penalty taker.
- **Marko Arnautović (idx 10)** — ageing but irreplaceable target man; leads the first press despite low speed, holds up play, and is the primary penalty taker (the late MD1 clincher vs Jordan). Conserve his off-the-ball running for the press triggers.
- **Konrad Laimer (idx 4)** — the engine, repurposed at right back; stamina 18 makes him both a press trigger and an overlapping runner behind Wimmer.
- **Xaver Schlager (idx 6)** — the duel machine in the double pivot: wins the ball, carries it forward, and releases Sabitzer.
- **Nicolas Seiwald (idx 5)** — the disciplined holding screen; the structural balance that lets the rest press without leaving the back four exposed.
- **Patrick Wimmer (idx 9)** — the direct, pacey right-sided threat (speed 16 / dribble 16); takes on the fullback and cuts inside. Starts ahead of Gregoritsch, who is the bench target/near-post alternate.
- **Romano Schmid (idx 7)** — the tireless left-sided worker; opened the scoring on MD1, presses and combines into the half-space.

## Tournament Mindset
Austria came through Group J's two opening rounds with a 3-1 win over Jordan and a 0-2 loss to champions Argentina, leaving them 2nd on 3 points and a superior goal difference into the MD3 decider against Algeria at Arrowhead Stadium. The equation is simple: a draw qualifies Austria for the Round of 32, while Algeria must win. That edge shapes the plan — Austria still press, because the press IS their identity, but with the goal-difference cushion they press to control rather than gamble: deny Algeria the chaotic transitions they thrive on, win the ball high, and kill the game in possession rather than chasing a needless goal. The danger is Algeria's pace in behind a high line if Austria over-commit; Rangnick's side will adjust the press height and stay compact when ahead or level late, but they will not abandon the gegenpress. Identity over caution, with one eye on the table.
