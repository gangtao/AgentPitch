# Austria — Tactical Profile

## Identity & Philosophy
Austria under Ralf Rangnick are the modern heirs to the Bielsa/Klopp pressing school — aggressive, vertical, ferocious in transition, and tactically uncompromising. Rangnick's "12-second rule" (counter-press to win the ball back within 12 seconds of losing it) defines them. They surprised everyone by topping their Euro 2024 group above France and the Netherlands, and arrive at the World Cup as one of the most cohesive sides on the planet.

## Formation
- Shape: 4-2-3-1
- Role mapping (roster order in `austria.yaml`):
  - index 0 (`austria_0`, A. Schlager): GK — Austria's established No.1, composed shot-stopper, comfortable with the ball at his feet, expected to play short.
  - index 1 (`austria_1`, Mwene): LB — pressing fullback, jumps into midfield.
  - index 2 (`austria_2`, Danso): LCB — physical, comfortable defending high.
  - index 3 (`austria_3`, Alaba): RCB — leader, ball-playing CB (highest-skill defender).
  - index 4 (`austria_4`, Posch): RB — disciplined, less aggressive than Mwene.
  - index 5 (`austria_5`, Seiwald): DM — disciplined ball-winner, screens behind Laimer.
  - index 6 (`austria_6`, Laimer): DM/box-to-box — engine of the press, all-action.
  - index 7 (`austria_7`, Baumgartner): LW/inverted — late runs into box, scoring threat.
  - index 8 (`austria_8`, Sabitzer): AM/#10 — creative hub, transitions trigger man.
  - index 9 (`austria_9`, Wimmer): RW — direct, beats fullback wide.
  - index 10 (`austria_10`, Arnautović): CF — target man, ageing but holds up play.

## Style of Play

### Build-up
Short build-up only if the press is light. If pressed, Alaba clips diagonals to Wimmer wide or long into Arnautović. The DM pair (Seiwald, Laimer) split to either side of the CB pairing. Build-up is brief — the goal is to provoke the opposition press, win the ball back high, and attack the vacated space.

### Pressing (block height + trigger)
**High block**. Press triggers (any of):
1. Opposition CB takes a touch oriented sideways or backward.
2. Pass to the opposition fullback near the touchline — wide trap.
3. Opposition GK plays short — Arnautović triggers, wingers curve runs to lock CBs.
The line of confrontation sits ~10m inside opposition half.

### Defensive shape
4-4-2 with Sabitzer pushing alongside Arnautović during the press; 4-2-3-1 when defending deeper. Crucially, after losing the ball Austria do NOT retreat — they swarm. **Counter-press (gegenpress)** is the default reaction within 12 seconds of any turnover.

### Wide play
Mwene and Posch are jump-pressers — they leave their defensive line to attack opposition wide receivers. Wimmer hugs the right touchline; Baumgartner inverts inside to create overloads in the half-space.

### Final third
Quick combinations on edge of the box. Arnautović holds up, Sabitzer arrives late between the lines, Baumgartner makes a near-post run. Crosses are low and into the 6-yard box.

## Set Pieces
- Corners: Alaba delivers — inswingers, varied near-/far-post targets. Arnautović, Danso, Posch are the primary aerial threats.
- Free kicks (direct): Alaba left-footed from the right; Sabitzer right-footed from the left.
- Penalties: Arnautović first; Sabitzer second.

## decide() Decision Priorities
1. **Counter-press trigger:** if Austria loses possession AND ball is within 35m of where it was lost, ALL players within 15m of the ball must TACKLE or close down — within 12 simulated seconds.
2. If my player_id ends with "_10" (CF, Arnautović, #7): when opposition GK has the ball, sprint diagonally to block the pass to the right CB — never let him play centrally.
3. If my player_id ends with "_7" or "_9" (wingers, Baumgartner/Wimmer): on the press, curve runs to cut off the back-pass while approaching the wide CB.
4. If my player_id ends with "_6" (DM, Laimer, #6): shadow the opposition #6 — whenever they receive, TACKLE inside 1 tick.
5. If my player_id ends with "_8" (AM, Sabitzer, #10): in possession, demand the ball facing forward in the half-space; out of possession, push up to become a second striker.
6. If my player_id ends with "_5" (DM, Seiwald, #14): never venture forward of the halfway line — he is the safety net for "_6" (Laimer)'s adventures.
7. If my player_id ends with "_3" (RCB, Alaba, #8): if Austria wins the ball in the opposition third, immediately PASS forward (no recycling allowed).
8. If my player_id ends with "_1" (LB, Mwene): jump-press the opposition right winger when ball is on Austria's left. High line is acceptable.
9. If my player_id ends with "_4" (RB, Posch): more conservative — stay aligned with "_2" (Danso) unless team is trailing.
10. On regain: nearest player to ball MOVE forward into space, second-nearest demands ball with a vertical pass option.
11. If my player_id ends with "_7" or "_9" (Baumgartner/Wimmer): when isolated 1v1 with fullback, DRIBBLE inside — half-space arrival is more dangerous than a wide cross.
12. If my player_id ends with "_10" (Arnautović): if play breaks down, drop to halfway line as a target — he's the press's emergency outlet.
13. If leading with under 10 minutes, drop the line of confrontation by 10m but maintain compactness — never park the bus.

## Key Player Notes
- **Marcel Sabitzer (index 8):** team's creative leader. Allowed maximum positional freedom; the offensive #10 in possession, the second striker in the press.
- **Konrad Laimer (index 6):** the engine. Highest stamina (18). Carries water on both ends — press trigger AND box-to-box runner.
- **David Alaba (index 3, captain):** primary set-piece taker, build-up brain. Allowed to step into midfield to recycle.
- **Marko Arnautović (index 10):** ageing but irreplaceable. Press leader (despite low speed), target man, primary penalty taker. Limit his off-the-ball running distance — he must conserve for the press triggers.
- **Christoph Baumgartner (index 7):** late-arrival goalscoring threat — instruct him to make blindside runs into the box every time Sabitzer receives.

## Tournament Mindset
Austria will press anyone — and that includes Brazil. The risk is that an opposition team that bypasses the press cleanly (long balls, technically gifted DMs) can exploit space behind. But Austria's tactical clarity makes them deeply uncomfortable to play against in a one-off knockout match.
