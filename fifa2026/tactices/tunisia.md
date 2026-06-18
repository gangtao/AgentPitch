# Tunisia — Tactical Profile

## Identity & Philosophy
Tunisia arrive at the 2026 World Cup in crisis. After completing a historic qualifying campaign without conceding a single goal under Sami Trabelsi, they sacked Trabelsi post-AFCON, then hired Sabri Lamouchi — who lasted just five games and was dismissed after a brutal 5-1 opening loss to Sweden on 14 June. With no time and no preparation, the federation handed the team to French firefighter **Hervé Renard** on 16 June, four days before the Japan game. Renard is a serial salvager of derailed campaigns (Saudi Arabia's 2022 win over Argentina; two AFCON titles) and his message is simple: turn the page on Sweden, restore organization, and recover Tunisia's identity as a hard-to-beat, set-piece-dangerous side. The Eagles of Carthage are still fundamentally a defensive, work-rate team — solid back line, a Skhiri-anchored midfield, and Hannibal Mejbri as the one creator who can produce a moment of quality. The plan vs Japan: stay compact, frustrate, and steal a goal from a set piece or a transition. They effectively must win to keep alive (1 point from Sweden's 3 and Netherlands/Japan's draw).

## Formation
- Shape: 4-3-3 — a return to a back four after the 5-3-2 collapsed against Sweden. Defensively conservative with a deep block; Skhiri shields, full-backs hold position until settled.
- Role mapping (roster order in `tunisia.yaml`):
  - index 0: GK — Aymen Dahmen (first choice; kept all 10 qualifying clean sheets; conservative distributor)
  - index 1: RB — Yan Valery (energetic overlapper on the right)
  - index 2: RCB — Dylan Bronn (experienced, aerial)
  - index 3: LCB — Montassar Talbi (aerial dominance, deepest of the back line)
  - index 4: LB — Ali Abdi (balanced, overlaps, **first-choice penalty taker**)
  - index 5: CM — Ellyes Skhiri (captain, conductor and shield; pass 16, stamina 17 — first name on the sheet, 83 caps)
  - index 6: CM — Hannibal Mejbri (creative #10 dropping into midfield; dribble 16, the open-play spark)
  - index 7: CM — Anis Ben Slimane (box-to-box runner, work-rate, screens)
  - index 8: RW — Elias Achouri (pace and dribbling; carries and cuts inside)
  - index 9: CF — Firas Chaouat (focal point; runs the channels, attacks crosses, finisher)
  - index 10: LW — Elias Saad (direct, two-footed, drives at the full-back and shoots)

## Style of Play

### Build-up
- Conservative — Tunisia avoids risk in build-up, especially after the Sweden mauling.
- Dahmen often goes long if pressed even moderately; he will not be asked to play out under pressure.
- Skhiri drops between center-backs to receive against high pressure; the other two midfielders stay central.
- Full-backs hold width but don't push beyond halfway until Tunisia is settled in possession.

### Pressing
- Mid-block press, rarely high-press. Renard's first job is to make the block compact again.
- Trigger: opposition CB receives with a weak first touch.
- Chaouat and the wingers do front-line work; the midfield three stays deep.
- Tunisia is content to let opponents (especially a possession side like Japan) have the ball in their own half.

### Defensive shape
- 4-1-4-1 / 4-5-1 deep mid-block that collapses into two banks.
- Skhiri screens in front of the back four; Mejbri and Ben Slimane drop to form the midfield line; the wide attackers tuck in.
- Chaouat is the lone outlet up top.
- Center-backs hold a deep line; Tunisia prefers not to play offside.

### Wide play
- Right: Achouri carries and cuts inside; Valery overlaps to give the wide option.
- Left: Saad drives directly at his man; Abdi overlaps when Tunisia is settled.
- Crosses come from the full-backs and from the wingers cutting in.

### Final third
- Chaouat attacks crosses, runs the channels, and is the principal finisher.
- Mejbri is the creative spark — carries into the box and threads the killer pass.
- Achouri's and Saad's carries plus wide overloads create the openings.
- Goals from open play often come from second balls and transitions in the box.

## Set Pieces
- Corners: Mejbri and Abdi are the deliverers. Talbi, Bronn, and Ben Slimane attack near/back posts.
- Direct free kicks: Mejbri (primary), Abdi, and Saad.
- Penalties: **Ali Abdi** is the first taker (converted vs Namibia in qualifying); Mejbri is an alternate. (Note: Gharbi shares spot-kick duty but is a bench option here.)
- Defending: zonal + man-mark on the biggest aerial threat. Tunisia is well-drilled and treats set pieces as a major chance to score against a stronger opponent.

## decide() Decision Priorities
1. When my role is GK (`player_id` ends with `_0`, Dahmen) under pressure: clear long to the CF (`_9`, Chaouat) or the LW channel (`_10`, Saad); do not attempt risky short passes.
2. When my role is DEF and center-back (`_2` Bronn or `_3` Talbi) receives in own third: simple pass to the pivot (`_5`, Skhiri) or a long ball forward — no dribbling out of defense.
3. When my `player_id` ends with `_5` (Skhiri, captain): face forward, recycle through the back four, or play a vertical pass into Mejbri's (`_6`) feet (pass 16 — be the metronome).
4. When my `player_id` ends with `_7` (Ben Slimane) and opponent has the ball in midfield: tackle aggressively and screen; he is the legs of the midfield three.
5. When my `player_id` ends with `_6` (Mejbri): receive between lines, turn forward, look to dribble (dribble 16) or play through balls — the main open-play threat.
6. When my `player_id` ends with `_8` (Achouri, RW): receive on the right, run in behind, or combine with the overlapping right-back (`_4` is LB; right-back is `_1` Valery) and cross to the CF (`_9`, Chaouat).
7. When my `player_id` ends with `_10` (Saad, LW): drive at the full-back, cut inside and Shoot (shoot 14) from the left half-space, or run in behind on through balls.
8. When defending: maintain a compact 4-5-1 / 4-1-4-1, never break shape to chase a duel — especially against Japan's quick combinations.
9. When there is a turnover in own half: clear long rather than build through pressure.
10. When a set piece is awarded anywhere on the field: Tunisia takes its time, organizes, and treats it as a major scoring opportunity (Mejbri/Abdi deliver; Talbi/Bronn attack the ball).
11. When trailing late (likely — Tunisia need a result): push full-backs Valery (`_1`) and Abdi (`_4`) forward, drop Skhiri (`_5`) alongside the center-backs as a back three, and send Talbi (`_3`) forward for set pieces.
12. When leading: drop the block 10m deeper and defend the box with all 10 outfield players for late crosses.

## Key Player Notes
- **Skhiri (idx 5; skill 16, pass 16, stamina 17)** — captain, conductor, and shield; 83 caps and the only Tunisian playing Champions League football. First name on the sheet; never gives the ball away cheaply.
- **Mejbri (idx 6; dribble 16)** — the creative heartbeat. Beats opponents and finds the killer pass; primary free-kick and corner deliverer. Tunisia's chief open-play threat.
- **Ali Abdi (idx 4; penalty 14)** — overlapping left-back and the first-choice penalty taker; a reliable spot-kick and a dead-ball deliverer.
- **Dahmen (idx 0; save 14)** — first-choice keeper who anchored a record clean-sheet qualifying run; the target for clearances is the CF, not a risky short build-up.
- **Talbi & Bronn (idx 3, idx 2)** — aerial-dominant in both boxes; the set-piece weapons at both ends.
- **Achouri & Saad (idx 8, idx 10)** — the pace and dribbling out wide; Tunisia's transition outlets and the most likely sources of a goal-from-nothing.

## Tournament Mindset
Tunisia are in survival mode. One point from a possible six is gone, the manager has changed twice in six months, and a heavy Sweden defeat has rattled the group. Renard's brief is damage control and identity: defend deep, stay compact, frustrate Japan, and pinch a goal from a set piece or a Mejbri/Saad moment. They believe 1-0 is the perfect scoreline — but they almost certainly need to win this match to keep their World Cup alive, so expect them to commit numbers forward late if the game is level or lost.
