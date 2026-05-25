# Paraguay — Tactical Profile

## Identity & Philosophy
Paraguay under Gustavo Alfaro are the archetypal South American dark horse: physical, disciplined, defensively organized, and built around set-piece danger and counter-attacking moments. Alfaro — the Argentine pragmatist who took Ecuador to the 2022 World Cup knockouts — has revived Paraguayan football by hammering home defensive shape, demanding a midfield that wins every duel, and using Almirón's pace as the chief outlet. Recent results: their CONMEBOL qualification campaign showed dramatic improvement, with Paraguay rising from also-rans to a team that nobody wants to face. Expect a tournament team that ties giants 0-0 and steals one off a set-piece.

## Formation
- Shape: **4-4-2** (low/mid-block defensive, two banks of four; morphs to 4-2-3-1 in possession with Almirón pushing high)
- Role mapping (roster order in `paraguay.yaml`):
  - index 0: GK — **Roberto Fernández** — traditional shot-stopper, stays in the box, modest with feet.
  - index 1: LB — **Junior Alonso** — actually a converted CB playing fullback in this listing; very defensive, rarely overlaps, prioritizes shape.
  - index 2: LCB — **Omar Alderete** — physical, aerial dominator, left-footed.
  - index 3: RCB — **Gustavo Gómez** — captain, the defensive talisman, the leader, aggressive aerial duel-winner.
  - index 4: RB — **Juan José Cáceres** — disciplined, conservative, supports Almirón rather than overlapping.
  - index 5: DM/LCM — **Andrés Cubas** — destroyer, the screen, ball-winning enforcer; Paraguay's primary defensive midfielder.
  - index 6: DM/RCM — **Mathías Villasanti** — box-to-box partner, slightly more progressive than Cubas, the legs of the pivot.
  - index 7: RM — **Miguel Almirón** — pacy, direct, the team's chief outlet on counter-attacks; gets the ball and runs.
  - index 8: LM — **Diego Gómez** — work-rate, two-way midfielder, less explosive than Almirón.
  - index 9: ST — **Antonio Sanabria** — target / second-striker hybrid, holds the ball up, finishes set-pieces.
  - index 10: ST — **Julio Enciso** — the creative spark, drops between the lines, the team's chief carrier and shooter from distance.

## Style of Play
### Build-up
**Direct.** Paraguay does NOT play short for the sake of it. Fernández often goes long toward Sanabria. When playing short, Alderete and Gustavo Gómez go to the CBs, but the ball doesn't linger — Cubas receives and looks vertical. Long diagonals to Almirón on the right are a primary release valve. Paraguay is happy to be **30% possession** and route 1.

### Pressing
**Low-block by default.** Paraguay rarely presses high. Press triggers: opposition takes a heavy first touch in their own half. Sanabria and Enciso are not aggressive pressers — they conserve energy for counters. The pressing is **reactive**, not proactive; Paraguay wants the opposition to play it long and lose the second ball to Cubas/Villasanti.

### Defensive shape
Out-of-possession: **4-4-2 low block**, two compact banks of four, no more than 25 units between defense and midfield lines. Sanabria and Enciso are the front pair, cutting passing lanes to the opposition #6 rather than pressing. Almirón and Diego Gómez tuck in narrow to deny central penetration. The wide channels are conceded; aerial duels in the box are won.

### Wide play
**Conservative fullbacks, wingers stay narrow.** Almirón and Diego Gómez tuck inside on counter-attacks to combine with Enciso, leaving width to be created by the wide midfielder's late underlap or by a Sanabria flick. Cáceres and Alonso almost never get past the halfway line.

### Final third
Patterns: **Almirón counter-attack carries** — get him the ball in space, let him drive 40 yards. **Enciso pulling the trigger** from 22+ yards (he loves to shoot). **Set-pieces** — Paraguay's biggest scoring source, deliveries from Cubas or Villasanti to Gustavo Gómez, Alderete, Sanabria. Crosses to the back post for Gustavo Gómez are a signature.

## Set Pieces
- Attacking corners: **Cubas** delivers from the right (in-swinger), **Villasanti** from the left (in-swinger). Primary targets: **Gustavo Gómez** (back post), Alderete (near post), Sanabria (penalty spot).
- Defending corners: **man-marking** — Paraguay's CBs dominate aerially; Gustavo Gómez attacks the first ball.
- Free kicks: **Enciso** direct from central positions; **Almirón** delivers from wide.
- Penalties: **Enciso** primary, **Sanabria** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If team_phase == "defending":** Drop into the 4-4-2 low block — no player past halfway except `_9` (Sanabria) and `_10` (Enciso). Stay compact (vertical distance between back four and midfield four < 25 units).
2. **If my `role == "GK"` (player_id `_0`, Fernández) and pressed by any opponent:** Punt long toward `_9` (Sanabria) — do NOT play short under pressure.
3. **If my `player_id` ends with `_7` (RM, Almirón) and team_phase == "transition_attack":** Sprint into the right channel; demand the ball in space.
4. **If my `player_id` ends with `_10` (ST, Enciso) and I have the ball within 25 units of goal:** Shoot — Paraguay values low-percentage shots over recycling possession.
5. **If my `role == "DEF"` and team_phase == "attacking":** Stay deep — Paraguay's CBs and fullbacks do NOT push past halfway in open play.
6. **If my `player_id` ends with `_5` (DM, Cubas) and an opponent receives the ball within 8 units in central midfield:** Tackle immediately.
7. **If team_phase == "transition_defense":** Drop straight back into the 4-4-2 block — Paraguay does NOT counter-press. Recovery > pressure.
8. **If my `player_id` ends with `_9` (ST, Sanabria) and a long ball is incoming:** Hold position, contest the aerial duel, flick on toward `_7` (Almirón) or `_10` (Enciso).
9. **If my `player_id` ends with `_7` (RM, Almirón) or `_8` (LM, Diego Gómez) and team_phase == "defending":** Tuck inside narrow — concede the wide channel, deny the central pass.
10. **If team_phase == "attacking" and my `player_id` ends with `_9` (Sanabria) or `_10` (Enciso) and I am in the box:** Prefer Shoot over Pass — Paraguay's attacks must end with a shot, not a recycle.
11. **If the match minute > 75 and team is drawing or leading:** Drop the defensive line 5 units deeper, slow down the game (Hold > Move).
12. **Attacking set-piece in opposition box:** `_3` (Gustavo Gómez) and `_2` (Alderete) sprint forward immediately — both target men.

## Key Player Notes
- **Gustavo Gómez (2):** Captain, set-piece talisman, the team's heartbeat. Attacks every attacking corner.
- **Almirón (7):** The outlet. The pace. Every counter starts with finding him in space.
- **Enciso (20):** The wildcard creator. License to shoot from distance and dribble in tight areas.
- **Cubas (5):** The destroyer — never crosses the halfway line.
- **Sanabria (9):** Set-piece finisher and aerial reference point.

## Tournament Mindset
Paraguay are the perfect 0-0 specialist: defensive, organized, set-piece dangerous, content to grind out one point and try to nick three from an opposition mistake. In a tournament they thrive on tight, ugly, low-scoring games. They will lose against a team that scores early; they will draw or win when the opponent is sloppy. Stamina-managed: low-block requires less running, so fitness is sustainable across the group stage.
