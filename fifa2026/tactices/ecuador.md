# Ecuador — Tactical Profile

## Identity & Philosophy
Sebastián Beccacece's Ecuador are a compact, athletic, defence-first side built on the foundation of one of the world's best defensive midfielders (Moisés Caicedo) and a generation of young, European-based talent (Hincapié, Pacho, Ordóñez, Plata). Beccacece's philosophy is pragmatic and vertical: deny space centrally, win the ball through midfield, then transition quickly with long diagonals to the wide runners. They prize defensive solidity over expansive possession — a low-error, high-intensity unit that conceded just five goals across 18 CONMEBOL qualifiers (fewest in the confederation) and frustrates better opponents before breaking them in transition. They arrived in USA/Canada/Mexico as a dangerous outsider but their group has gone badly: **Ivory Coast 1-0 Ecuador (Amad Diallo, 90')** in the opener (Ecuador dominated but couldn't finish), followed by a flat **Ecuador 0-0 Curaçao**. Zero goals in two games leaves them third in Group E on 1 point. Now, in the final group game, they must **beat already-qualified Germany at MetLife Stadium** to have any chance of advancing — and hope Ivory Coast slip against Curaçao. For this must-win, Beccacece shifts to a more aggressive **3-5-2**: a back three behind attacking wing-backs, a packed midfield, and a front two to commit numbers forward.

## Formation
- Shape: **3-5-2** (back three; Estupiñán and Yeboah as wing-backs; Caicedo anchors a midfield trio; Plata and Valencia as a front two)
- Role mapping (roster order in `ecuador.yaml`):
  - index 0: GK — **Hernán Galíndez** — experienced first-choice keeper, shot-stopper, modest with feet; not a sweeper.
  - index 1: LCB — **Piero Hincapié** — aggressive, left-footed ball-progressor on the left of the back three; steps into midfield to break lines.
  - index 2: CCB — **Willian Pacho** — left-footed, calm, fast across the ground; the central recovery defender and the spine's anchor.
  - index 3: RCB — **Joel Ordóñez** — young, physical, dominant in the air; the more conservative stopper on the right of the three.
  - index 4: LWB — **Pervis Estupiñán** — elite overlapping wing-back; the team's primary attacking width on the left and top dead-ball delivery.
  - index 5: LCM — **Pedro Vite** — circulates possession beside Caicedo, lets the anchor screen and the wing-backs push on; the build-up metronome and box-arriver.
  - index 6: CM (anchor) — **Moisés Caicedo** — the world-class screen, wins the duel, recycles to the forwards; the engine of the side.
  - index 7: RCM — **Alan Franco** — disciplined two-way midfielder; covers behind the right wing-back, shields the back three, recycles simply.
  - index 8: RWB — **John Yeboah** — direct, pacy wing-back; stretches the line, overlaps and arrives at the back post.
  - index 9: SF — **Gonzalo Plata** — the chief carrier and creator dropping off the front; a 1v1 dribbler who drives transitions.
  - index 10: ST — **Enner Valencia** — captain, holds the ball up, makes intelligent runs in behind, the experienced focal point, set-piece and penalty taker.

## Style of Play

### Build-up
**Mixed: short out of the back three, vertical as soon as the pivot turns.** Galíndez plays short to Pacho or the wide CBs. Caicedo drops to receive between/beside the centre-backs when pressed. The wing-backs (Estupiñán and Yeboah) push high and wide to provide all the width. Once Caicedo or Vite receives facing forward, the ball goes vertical — a long diagonal to a wing-back or into Plata between the lines, with Valencia pinning the CBs. Ecuador will go long quickly under pressure; they do not force the build-up. Against Germany they must be braver in possession and commit the front two.

### Pressing
**Mid-block with selective high-press in transition moments.** Press triggers: opposition GK passing short, opposition CM receiving with back to play. Valencia and Plata lead by cover-shadowing the deepest pivot; the wing-backs jump onto the opposition full-backs. Caicedo aggressively jumps onto the opposition #10. Ecuador are **not** a sustained 90-minute high-press team — they pick their moments and otherwise drop into shape. Needing a win, they will press higher and longer than usual against Germany.

### Defensive shape
Out-of-possession: **5-3-2** — the wing-backs (Estupiñán, Yeboah) drop to make a back five; Vite, Caicedo and Franco form a compact midfield three; Plata and Valencia stay high as the counter outlet. The back three holds a **medium-deep line**, with Caicedo screening in front. Franco tucks to cover the right side, Vite the left.

### Wide play
**Wing-back driven:** Estupiñán bombs forward from the left as the primary attacking outlet; Yeboah provides direct pace and overlap on the right. With no natural wingers, all width comes from the wing-backs — the front two stay central and the midfielders feed the channels.

### Final third
Patterns: **wing-back overlap into a cutback** for Valencia or the arriving Vite/Plata. **Plata drops and drives 1v1** — let him cook on the carry. **Long diagonal switch** to the far wing-back. Ecuador are most dangerous in **transition** — a Caicedo turnover into a quick vertical move ending with a Plata drive or an Estupiñán cross to Valencia and the back-post runner.

## Set Pieces
- Attacking corners: **Estupiñán** delivers (left-footed in-swingers from the right, out-swingers from the left). Aerial targets: Pacho, Ordóñez, Hincapié, Valencia.
- Defending corners: **hybrid** — four zonal markers, three man-markers, two short-corner watchers. Pacho/Ordóñez attack the first ball.
- Free kicks: **Estupiñán** delivers from set positions. **Plata** direct from central positions.
- Penalties: **Valencia** primary (all-time leading scorer, ice-cold), **Plata** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_6` (CM anchor, Caicedo) and team_phase == "defending":** Position centrally just ahead of the back three; never venture past the halfway line.
2. **If my `player_id` ends with `_6` (CM anchor, Caicedo) and an opponent has the ball within 8 units in central midfield:** Tackle (this is his primary action).
3. **If my `player_id` ends with `_5` (LCM, Vite) and team has the ball:** Stay beside Caicedo, circulate to keep possession; if a vertical lane is open, drive it forward, else recycle to a CB. Vite and Franco do not both advance at once.
4. **If my `player_id` ends with `_4` (LWB, Estupiñán) and team_phase == "attacking":** Sprint to the byline; prefer cross Pass to `_10` (ST Valencia) at the near post or cutback to `_9` (Plata).
5. **If my `role == "GK"` (player_id `_0`, Galíndez) and pressed by 1 forward:** Play short to `_2` (Pacho); **if pressed by 2 forwards:** punt long toward `_10` (Valencia).
6. **If my `player_id` ends with `_9` (SF, Plata) and I receive between the lines:** Face forward; carry at the defence 1v1 or look for `_8` (RWB Yeboah) / `_4` (LWB Estupiñán) overlapping runs and `_10` (Valencia)'s movement before recycling.
7. **If team_phase == "defending":** Both wing-backs (`_4` Estupiñán, `_8` Yeboah) drop to form a back five; `_5` Vite, `_6` Caicedo and `_7` Franco hold a midfield three ahead of them.
8. **If my `player_id` ends with `_10` (ST, Valencia) and team_phase == "transition_attack":** Sprint into the channel between the opposition CBs; act as the outlet with `_9` (Plata) supporting underneath.
9. **If my `player_id` ends with `_1` (LCB, Hincapié) and no opponent within 10 units in midfield:** Step forward with the ball to break the line.
10. **If team_phase == "transition_defense":** Both wing-backs (`_4` Estupiñán, `_8` Yeboah) drop into the back line within 6 ticks; `_6` (Caicedo) holds central position immediately, `_7` (Franco) covers the right half-space, `_5` (Vite) the left.
11. **If team is trailing and minute > 60:** Push the wing-backs (`_4`, `_8`) higher and commit `_5` (Vite) into the box; chase the win — they must beat Germany to advance.
12. **If my `player_id` ends with `_8` (RWB Yeboah) and carrying in the attacking third with no clear pass:** Shoot if in range, else cut back to `_9` (Plata) or `_10` (Valencia).
13. **Set-piece in attacking third with `_4` (Estupiñán) available:** Defer delivery to `_4`.

## Key Player Notes
- **Caicedo (23):** The world-class anchor. Never leaves the central screen position in front of the back three. Every defensive recovery in midfield is his first.
- **Vite (8):** The left-of-centre midfielder — circulates possession, frees Caicedo to screen and the wing-backs to push; arrives in the box late.
- **Franco (5):** The right-of-centre midfielder — disciplined two-way shuttler who shields the back three and covers behind Yeboah; keeps it simple on the ball.
- **Estupiñán (7):** Primary attacking wing-back on the left — provides width and all the dead-ball delivery.
- **Yeboah (11):** Direct, pacy right wing-back — pace and overlap on the right flank, a back-post threat.
- **Plata (19):** The chief creator and transition carrier, dropping off the front two — license to take on his man 1v1; secondary penalty taker.
- **Valencia (13):** Captain, focal point, set-piece outlet and primary penalty taker; Ecuador's all-time top scorer, one strike from a fresh milestone.
- **Pacho, Hincapié & Ordóñez:** The European-based defensive spine (PSG / Arsenal / Club Brugge) — two left-footed line-breakers plus a physical aerial stopper, now a back three.

## Tournament Mindset
Ecuador are the wounded outsiders: athletic, disciplined, and capable of frustrating anyone, but with zero goals in two games they have left themselves needing to **beat already-qualified Germany** to survive — and even then they need Ivory Coast to drop points against Curaçao. Beccacece has gone bold with a 3-5-2 to commit a front two and overload midfield; the wing-backs are vital to both width and defensive cover. Finishing has been the fatal flaw — chances created, none taken. Against Germany's ruthless attack (nine goals in two games) they cannot afford to fall behind, but they also cannot sit and settle: only a win keeps them alive, so they must take their chances when they come.
