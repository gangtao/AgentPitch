# Ecuador — Tactical Profile

## Identity & Philosophy
Sebastián Beccacece's Ecuador are a compact, athletic, defence-first side built on the foundation of one of the world's best defensive midfielders (Moisés Caicedo) and a generation of young, European-based talent (Hincapié, Pacho, Ordóñez, Plata). Beccacece's philosophy is pragmatic and vertical: sit in a disciplined mid-block, deny space centrally, win the ball through the double pivot, then transition quickly with long diagonals to the wide forwards (Plata, Angulo). They prize defensive solidity over expansive possession — a low-error, high-intensity unit that frustrates better opponents and breaks them in transition. They arrive in USA/Canada/Mexico as a dangerous outsider who took a 19-game unbeaten streak into the tournament. That run ended in their opener: **Ivory Coast 1-0 Ecuador (Amad Diallo, 90')** in Group E — Ecuador dominated the first half (Yeboah and Minda both hit the bar, Valencia hit the woodwork) but were undone by a late sucker punch and now must win to revive their campaign vs Curaçao.

## Formation
- Shape: **4-2-3-1** (Caicedo + Vite as a double pivot; out of possession the wide attackers drop to form a compact 4-4-1-1 / 4-5-1 mid-block)
- Role mapping (roster order in `ecuador.yaml`):
  - index 0: GK — **Hernán Galíndez** — experienced first-choice keeper, shot-stopper, modest with feet; not a sweeper.
  - index 1: LB — **Piero Hincapié** — aggressive, left-footed ball-progressor deployed at left-back; steps into midfield to break lines.
  - index 2: LCB — **Willian Pacho** — left-footed, calm, fast across the ground; the recovery defender and the spine's anchor.
  - index 3: RCB — **Joel Ordóñez** — young, physical, dominant in the air; the more conservative stopper of the pair.
  - index 4: RB — **Pervis Estupiñán** — elite overlapping fullback (naturally left-footed but deployed right); the team's primary attacking width and top dead-ball delivery.
  - index 5: DM (anchor) — **Moisés Caicedo** — the world-class screen, wins the duel, recycles to the forwards; the engine of the side.
  - index 6: DM (deep playmaker) — **Pedro Vite** — circulates possession beside Caicedo, lets the anchor roam and the fullbacks push on; the build-up metronome.
  - index 7: LAM — **Nilson Angulo** — direct, pacy left attacker (speed 16, dribbling 15); cuts inside onto his stronger foot as Estupiñán/Hincapié provide overlap.
  - index 8: CAM (#10) — **Gonzalo Plata** — the chief carrier and creator operating off the right/central; a 1v1 dribbler who drives transitions.
  - index 9: RAM — **John Yeboah** — direct, pacy wide attacker; stretches the line and arrives at the back post.
  - index 10: ST — **Enner Valencia** — captain, holds the ball up, makes intelligent runs in behind, the experienced focal point, set-piece and penalty taker.

## Style of Play

### Build-up
**Mixed: short out of the back, vertical as soon as the pivot turns.** Galíndez plays short to Pacho or Ordóñez. Caicedo or Vite drops to receive between/beside the CBs when pressed. The fullbacks (Estupiñán especially) push high and wide. Once a pivot receives facing forward, the ball goes vertical — a long diagonal to the wide forwards (Angulo/Yeboah) or into Plata between the lines, with Valencia pinning the CBs. Ecuador will go long quickly under pressure; they do not force the build-up.

### Pressing
**Mid-block with selective high-press in transition moments.** Press triggers: opposition GK passing short, opposition CM receiving with back to play. Valencia leads by cover-shadowing the deepest pivot, Plata steps up beside him, and the wide forwards (Angulo/Yeboah) curve runs onto the fullbacks. Caicedo aggressively jumps onto the opposition #10. Ecuador are **not** a sustained 90-minute high-press team — they pick their moments and otherwise drop into shape.

### Defensive shape
Out-of-possession: **4-4-1-1 / 4-5-1** — Angulo and Yeboah tuck in alongside Caicedo and Vite to form a compact midfield bank; Plata screens just ahead, Valencia holds the line. The CBs hold a **medium-deep line**. The double pivot is the screen in front of the back four — Caicedo the ball-winner, Vite the cover.

### Wide play
**Asymmetric:** Estupiñán bombs forward from right-back as a primary attacking outlet; Hincapié is more measured but steps into midfield with the ball. The wide forwards (Angulo left, Yeboah right) cut inside, trusting the fullbacks to provide the overlap and width.

### Final third
Patterns: **fullback overlap into a cutback** for Valencia or the arriving Plata. **Plata 1v1 isolation** — let him cook on the carry. **Long diagonal switch** to the far wide forward attacking the back post. Ecuador are most dangerous in **transition** — a Caicedo turnover into a 3-4 pass move ending with a Plata drive or an Estupiñán cross to Valencia and the far-post runner.

## Set Pieces
- Attacking corners: **Estupiñán** delivers (left-footed in-swingers from the right, out-swingers from the left). Aerial targets: Pacho, Ordóñez, Hincapié, Valencia.
- Defending corners: **hybrid** — four zonal markers, three man-markers, two short-corner watchers. Pacho/Ordóñez attack the first ball.
- Free kicks: **Estupiñán** delivers from set positions. **Plata** direct from central positions.
- Penalties: **Valencia** primary (all-time leading scorer, ice-cold), **Plata** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_5` (DM, Caicedo) and team_phase == "defending":** Position centrally between the CBs and the midfield line; never venture past the halfway line.
2. **If my `player_id` ends with `_5` (DM, Caicedo) and an opponent has the ball within 8 units in central midfield:** Tackle (this is his primary action).
3. **If my `player_id` ends with `_6` (DM, Vite) and team has the ball:** Stay beside Caicedo, circulate to keep possession; if a vertical lane is open, drive it forward, else recycle to a CB. Do not both pivots advance at once.
4. **If my `player_id` ends with `_4` (RB, Estupiñán) and team_phase == "attacking":** Sprint to the byline; prefer cross Pass to `_10` (ST Valencia) at the near post or cutback to `_8` (Plata).
5. **If my `role == "GK"` (player_id `_0`, Galíndez) and pressed by 1 forward:** Play short to `_2` (Pacho); **if pressed by 2 forwards:** punt long toward `_10` (Valencia).
6. **If my `player_id` ends with `_8` (CAM, Plata) and I receive between the lines:** Face forward; carry at the defence 1v1 or look for `_9` (RAM Yeboah) / `_7` (LAM Angulo) diagonal runs and `_4` (Estupiñán)'s overlap before recycling.
7. **If team_phase == "defending":** Both wide forwards (`_7` Angulo, `_9` Yeboah) drop into the midfield four; `_8` (Plata) screens ahead of the pivot.
8. **If my `player_id` ends with `_10` (ST, Valencia) and team_phase == "transition_attack":** Sprint into the channel between the opposition CBs; act as the outlet with the wide forwards (`_7` Angulo, `_9` Yeboah) breaking either side.
9. **If my `player_id` ends with `_1` (LB, Hincapié) and no opponent within 10 units in midfield:** Step forward with the ball to break the line.
10. **If team_phase == "transition_defense":** Both wide forwards (`_7` Angulo, `_9` Yeboah) drop into the midfield bank within 6 ticks; `_5` (Caicedo) holds central position immediately, `_6` (Vite) covers the vacated pivot space.
11. **If team is leading by 1+ goals and minute > 70:** Drop to low block, deny central space, rely on counters via `_8` (Plata) and `_4` (Estupiñán).
12. **If my `role == "MID"` and I'm a wide forward (`_7` Angulo / `_9` Yeboah) carrying in the attacking third with no clear pass:** Shoot if in range, else lay it off to `_8` (Plata) or `_10` (Valencia).
13. **Set-piece in attacking third with `_4` (Estupiñán) available:** Defer delivery to `_4`.

## Key Player Notes
- **Caicedo (23):** The world-class anchor. Never leaves the central screen position. Every defensive recovery in midfield is his first.
- **Vite (8):** The second pivot — circulates possession, frees Caicedo to roam and the fullbacks to push; the deeper of the two on the ball.
- **Estupiñán (7):** Most attacking player in the back line — provides right-side width and all the dead-ball delivery despite being left-footed.
- **Plata (19):** The chief creator and transition carrier — license to take on his man 1v1; secondary penalty taker.
- **Valencia (13):** Captain, focal point, set-piece outlet and primary penalty taker; Ecuador's all-time top scorer.
- **Angulo (20) & Yeboah (11):** Direct, pacy wide forwards — pace and dribbling on the outside, the transition outlets either side.
- **Pacho, Hincapié & Ordóñez:** The European-based defensive spine (PSG / Bayer Leverkusen / Club Brugge) — two left-footed line-breakers plus a physical aerial stopper.

## Tournament Mindset
Ecuador are the wounded outsiders: athletic, disciplined, and capable of frustrating anyone, but smarting from a 90th-minute defeat to Ivory Coast that ended a 19-game unbeaten run. They must now win vs Curaçao to keep control of their Group E fate. They will not chase a game from behind well — falling behind is costly. Stamina-managed: their mid-block needs fresh legs in the wide forward positions, where Beccacece rotates Angulo, Yeboah and Páez. Against weaker opposition they will be the dominant side and must convert the chances they create — finishing was the one thing missing against Ivory Coast.
