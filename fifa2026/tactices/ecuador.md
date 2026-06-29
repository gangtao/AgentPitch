# Ecuador — Tactical Profile

## Identity & Philosophy
Sebastián Beccacece's Ecuador are a compact, athletic, defence-first side built on the foundation of one of the world's best defensive midfielders (Moisés Caicedo) and a generation of young, European-based talent (Hincapié, Pacho, Ordóñez, Plata). Beccacece's philosophy is pragmatic and vertical: deny the centre, force play wide, win the ball through midfield, then transition quickly through Caicedo to the runners. They prize defensive solidity over expansive possession — a low-error, high-intensity unit that conceded just five goals across 18 CONMEBOL qualifiers (fewest in the confederation) and frustrates better opponents before breaking them on the counter. Their group campaign was a slow burn that ended in triumph: a narrow **1-0 loss to Ivory Coast** in the opener and a flat **0-0 draw with Curaçao** left them needing a result, and they delivered a famous **2-1 upset of already-qualified Germany** — **Gonzalo Plata's 77th-minute winner** sealing a third-place finish good enough to advance as one of the eight best third-placed teams. The defence-first blueprint was vindicated; now they carry that momentum into the knockouts.

## R32 Lineup (vs Mexico, June 30 — Round of 32 knockout, away at the host nation)
This is win-or-go-home, away to the co-hosts in front of a hostile Mexico City crowd at the Estadio Banorte (the former Estadio Azteca). Beccacece is not expected to overhaul the side that beat Germany, but he reverts from the bold must-win 3-5-2 to his trusted **4-4-2** — the shape that prizes structure and discipline, forces play wide, and springs Caicedo on the counter:
- **Alan Franco** shifts from midfield to **right-back**, anchoring a back four and shielding the right channel.
- **Piero Hincapié** moves out to **left-back**, his pace and ball-progression giving Ecuador's only natural attacking width on the left.
- **Pacho** and **Ordóñez** form the central defensive pairing — the physical, aerially dominant spine.
- **Nilson Angulo** comes into the **left of midfield** for his direct running and dribbling, replacing the more conservative wing-back/extra-midfielder of the Germany game.
- **Plata** drops alongside **Valencia** in the front two, free to drift and carry in transition.
- No major injuries or suspensions reported; this is close to Beccacece's first-choice knockout XI.

## Formation
- Shape: **4-4-2** (flat back four; Caicedo + Vite as the central-midfield pair; Angulo and Yeboah as wide midfielders; Plata and Valencia as a front two)
- Role mapping (roster order in `ecuador.yaml`):
  - index 0: GK — **Hernán Galíndez** — experienced first-choice keeper, shot-stopper, modest with feet; not a sweeper. Clean sheet vs Curaçao.
  - index 1: LB — **Piero Hincapié** — aggressive, left-footed full-back; overlaps to provide width and steps in to break lines; the team's primary attacking outlet on the left.
  - index 2: LCB — **Willian Pacho** — left-footed, calm, fast across the ground; the central recovery defender and the spine's anchor.
  - index 3: RCB — **Joel Ordóñez** — young, physical, dominant in the air; the more conservative stopper alongside Pacho.
  - index 4: RB — **Alan Franco** — disciplined converted midfielder at right-back; rarely overlaps, tucks in to keep the back four compact and covers behind Yeboah.
  - index 5: LM — **Nilson Angulo** — direct, pacy wide midfielder; takes on his man, stretches the line and arrives at the back post.
  - index 6: LCM — **Moisés Caicedo** — the world-class screen; wins the duel, recycles to the forwards, springs the counter; the engine of the side.
  - index 7: RCM — **Pedro Vite** — circulates possession beside Caicedo, lets the anchor screen and the wide men push on; the build-up metronome and late box-arriver.
  - index 8: RM — **John Yeboah** — direct, pacy wide midfielder on the right; stretches the line, overlaps and arrives at the far post.
  - index 9: SF — **Gonzalo Plata** — the chief carrier and creator dropping off the front; a 1v1 dribbler who drives transitions; scored the winner vs Germany.
  - index 10: ST — **Enner Valencia** — captain, holds the ball up, makes intelligent runs in behind, the experienced focal point, set-piece and penalty taker.

## Style of Play

### Build-up
**Mixed: short out of the back four, vertical as soon as the pivot turns.** Galíndez plays short to Pacho or Ordóñez; Caicedo drops between or beside the centre-backs when pressed. The full-backs (Hincapié pushing high on the left, Franco tucked on the right) and the wide midfielders provide width. Once Caicedo or Vite receives facing forward, the ball goes vertical — a long diagonal to a wide man or into Plata between the lines, with Valencia pinning the CBs. Ecuador will go long quickly under pressure; they do not force the build-up. Against the hosts they will be content to cede possession and counter.

### Pressing
**Mid-block with selective high-press in transition moments.** Press triggers: opposition GK passing short, opposition CM receiving with back to play. Valencia and Plata lead by cover-shadowing the deepest pivot; the wide midfielders jump onto the opposition full-backs. Caicedo aggressively jumps onto the opposition #10. Ecuador are **not** a sustained 90-minute high-press team — they pick their moments, otherwise drop into shape. Away at a hostile Mexico City, they will sit deeper and counter rather than chase.

### Defensive shape
Out-of-possession: **4-4-2 mid-block** — the wide midfielders (Angulo, Yeboah) drop alongside the central pair to form a flat midfield four; the full-backs hold the line; Plata and Valencia stay high as the counter outlet. The back four holds a **medium-deep line**, with Caicedo screening in front. Franco tucks to cover the right, Hincapié the left when they push on.

### Wide play
**Full-back and winger combinations:** Hincapié bombs forward from left-back as the primary attacking width on the left, supporting Angulo; Yeboah provides direct pace and overlap on the right, with Franco staying home behind him. The front two stay central and the midfielders feed the channels.

### Final third
Patterns: **wide overlap into a cutback** for Valencia or the arriving Vite. **Plata drops and drives 1v1** — let him cook on the carry. **Long diagonal switch** to the far wide man. Ecuador are most dangerous in **transition** — a Caicedo turnover into a quick vertical move ending with a Plata drive or a Hincapié/Angulo cross to Valencia and the back-post runner. The Germany winner came exactly this way: a quick break finished by Plata.

## Set Pieces
- Attacking corners: **Hincapié** delivers (left-footed; in-swingers from the right, out-swingers from the left). Aerial targets: Pacho, Ordóñez, Valencia.
- Defending corners: **hybrid** — four zonal markers, three man-markers, two short-corner watchers. Pacho/Ordóñez attack the first ball.
- Free kicks: **Hincapié** delivers from wide set positions. **Plata** direct from central positions.
- Penalties: **Valencia** primary (all-time leading scorer, ice-cold), **Plata** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `player_id` ends with `_6` (LCM anchor, Caicedo) and team_phase == "defending":** Position centrally just ahead of the back four; never venture past the halfway line.
2. **If my `player_id` ends with `_6` (LCM anchor, Caicedo) and an opponent has the ball within 8 units in central midfield:** Tackle (this is his primary action).
3. **If my `player_id` ends with `_7` (RCM, Vite) and team has the ball:** Stay beside Caicedo, circulate to keep possession; if a vertical lane is open, drive it forward, else recycle to a CB. Vite advances; Caicedo holds.
4. **If my `player_id` ends with `_1` (LB, Hincapié) and team_phase == "attacking":** Sprint to the byline; prefer cross Pass to `_10` (ST Valencia) at the near post or cutback to `_9` (Plata).
5. **If my `role == "GK"` (player_id `_0`, Galíndez) and pressed by 1 forward:** Play short to `_2` (Pacho); **if pressed by 2 forwards:** punt long toward `_10` (Valencia).
6. **If my `player_id` ends with `_9` (SF, Plata) and I receive between the lines:** Face forward; carry at the defence 1v1 or look for `_8` (RM Yeboah) / `_5` (LM Angulo) runs and `_10` (Valencia)'s movement before recycling.
7. **If team_phase == "defending":** Both wide midfielders (`_5` Angulo, `_8` Yeboah) drop alongside `_6` Caicedo and `_7` Vite to form a flat midfield four ahead of the back line.
8. **If my `player_id` ends with `_10` (ST, Valencia) and team_phase == "transition_attack":** Sprint into the channel between the opposition CBs; act as the outlet with `_9` (Plata) supporting underneath.
9. **If my `player_id` ends with `_2` (LCB, Pacho) and no opponent within 10 units in midfield:** Step forward with the ball to break the line; otherwise recycle to `_3` (Ordóñez) or `_6` (Caicedo).
10. **If team_phase == "transition_defense":** The full-backs (`_1` Hincapié, `_4` Franco) recover into the back line within 6 ticks; `_6` (Caicedo) holds central position immediately, `_7` (Vite) covers ahead, the wide mids (`_5`, `_8`) track back.
11. **If team is trailing and minute > 60:** Push `_1` (Hincapié) and `_8` (Yeboah) higher and commit `_7` (Vite) into the box; chase the winner.
12. **If my `player_id` ends with `_8` (RM Yeboah) and carrying in the attacking third with no clear pass:** Shoot if in range, else cut back to `_9` (Plata) or `_10` (Valencia).
13. **Set-piece in attacking third with `_1` (Hincapié) available:** Defer delivery to `_1`.

## Key Player Notes
- **Caicedo (23):** The world-class anchor. Never leaves the central screen position in front of the back four. Every defensive recovery in midfield is his first; the spring of every counter.
- **Vite (8):** The right-of-centre midfielder — circulates possession, frees Caicedo to screen and the wide men to push; arrives in the box late.
- **Franco (5):** Converted to right-back — disciplined, tucks in to keep the back four compact, covers behind Yeboah; keeps it simple on the ball.
- **Hincapié (3):** Now at left-back — provides width and all the dead-ball delivery, left-footed line-breaker.
- **Angulo (16):** Direct, pacy left midfielder — pace and dribbling on the left flank, a back-post threat; into the XI for his transition running.
- **Yeboah (11):** Direct, pacy right midfielder — pace and overlap on the right flank, a far-post threat.
- **Plata (19):** The chief creator and transition carrier, dropping off the front two — license to take on his man 1v1; scored the winner vs Germany; secondary penalty taker.
- **Valencia (13):** Captain, focal point, set-piece outlet and primary penalty taker; Ecuador's all-time top scorer.
- **Pacho & Ordóñez:** The central defensive pairing — Pacho the left-footed, fast line-breaker (PSG); Ordóñez the young, physical aerial stopper (Club Brugge).

## Tournament Mindset
Ecuador are the dangerous outsiders who have peaked at the right time: athletic, disciplined, and capable of frustrating anyone, they ground out the result they needed against Germany to reach the knockouts. Now they face the co-hosts away in front of a hostile Mexico City crowd — a single-elimination match where their defence-first identity is the whole game plan. Expect a deep, compact 4-4-2 block, possession ceded willingly, and everything invested in transition: win the ball through Caicedo, spring Plata and Valencia, and convert the half-chance. Finishing was the early-tournament flaw, but the Germany win showed they can take the moment that matters. They will not chase the game unless forced; they will defend the box, soak the pressure, and look to break a host nation that must come at them.
