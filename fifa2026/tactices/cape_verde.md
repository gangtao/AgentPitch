# Cape Verde — Tactical Profile

## Identity & Philosophy
The Blue Sharks are the smallest nation ever to qualify for a World Cup, and under Bubista (Pedro Leitão Brito) they punch above their weight through obsessive organization, set-piece danger, and quick vertical transitions. Their football is unfashionable but functional — every player works, every block is collective, and every set piece is rehearsed.

## Formation
- Shape: 4-3-3, defensively compact, dropping into a narrow 4-5-1 out of possession (the wide forwards tuck back alongside the midfield three).
- Role mapping (roster index -> tactical role):
  - 0 Vozinha — Veteran goalkeeper, vice-captain.
  - 1 Stopira — Left-back, veteran leader.
  - 2 Logan Costa — Left center-back, ball-playing anchor.
  - 3 Roberto Lopes (Pico) — Right center-back, physical.
  - 4 Steven Moreira — Right-back, balanced.
  - 5 Laros Duarte — Left central midfielder, work-rate.
  - 6 Deroy Duarte — Central / holding midfielder, controls tempo.
  - 7 Jamiro Monteiro — Right central midfielder, technical engine.
  - 8 Ryan Mendes — Left forward / wide attacker, captain.
  - 9 Dailon Livramento — Center-forward.
  - 10 Garry Rodrigues — Right winger / wide forward.

## Style of Play

### Build-up
- Direct under pressure; Vozinha plays long to Livramento or into the channels for the wide forwards frequently.
- Short build-up reserved for unpressed moments — Costa is the lead passer.
- Full-backs Moreira and Stopira hold width but rarely push past halfway in build-up.
- Deroy Duarte drops between center-backs against pressure.

### Pressing
- Mid-block press, occasional triggered high press in coordinated waves.
- Trigger: bad first touch or backward pass under pressure.
- Livramento and the wide forwards lead the press; Monteiro harasses the pivot.
- Cape Verde does not chase if first wave is broken — drops immediately into compact 4-5-1.

### Defensive shape
- 4-5-1 deep block: a back four with a midfield three flanked by the dropping wide forwards Mendes and Rodrigues.
- Lopes and Costa hold a deep line; full-backs tuck inside.
- Wide forwards Mendes and Rodrigues track back to make banks of five in midfield.
- Total team width when defending is roughly 30 meters.

### Wide play
- Right: Rodrigues is the principal attacking outlet — cuts inside or attacks the byline.
- Left: Mendes drifts inside off the wing; Stopira overlaps when fresh.
- Crosses target Livramento and Costa arriving on set pieces.

### Final third
- Monteiro is the creative engine — receives between lines, plays through balls.
- Livramento finishes inside the box; Rodrigues shoots from the half-space.
- Mendes (captain, all-time top scorer) drifts inside to combine and finish.
- Cape Verde scores a high proportion of goals from set pieces and crosses.
- They will not over-commit in attack — typically 4-5 players in the opponent's half.

## Set Pieces
- Costa, Lopes, and Livramento are aerial targets.
- Mendes takes most attacking set pieces; Monteiro for the right side.
- Defensive set pieces: man-marking with Lopes on the biggest threat. Cape Verde's set-piece defending is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Vozinha) and pressed: clear long to the CF (player_id ends with "_9", Livramento) or RW (player_id ends with "_10", Rodrigues) — never risk passes near own box.
2. If the CBs (player_id ends with "_2" Logan Costa or "_3" Roberto Lopes) and unpressed: short pass to nearest midfielder; only carry forward if completely uncontested.
3. If player_id ends with "_6" (Deroy Duarte, MID #16): drop between center-backs to facilitate build-up against pressure.
4. If player_id ends with "_7" (Monteiro, MID #12; skill 14, dribbling 14, pass 14): receive between lines, play through balls or simple lay-offs.
5. If player_id ends with "_10" (Rodrigues, RW #20): cut inside onto left foot from the right wing, or attack the byline.
6. If player_id ends with "_9" (Livramento, CF #23): run channels, attack near-post crosses, hold up play under pressure.
7. If defending in own half: maintain 4-5-1 compactness, never break shape for a speculative tackle.
8. If turnover in own half: clear long to Livramento (player_id ends with "_9") or Rodrigues (player_id ends with "_10") — get the ball away from danger.
9. If a set piece is awarded: send Costa (player_id ends with "_2"), Lopes (player_id ends with "_3"), and Livramento (player_id ends with "_9") forward; this is a key scoring opportunity.
10. If trailing late: push the full-backs Moreira (player_id ends with "_4") and Stopira (player_id ends with "_1") higher, send Costa (player_id ends with "_2") forward for set pieces, throw extra runners forward.
11. If leading: drop block 12m deeper, defend the box collectively, kill time on every dead ball.
12. If counter-attack opportunity: maximum 3-4 passes, vertical and direct — Rodrigues (player_id ends with "_10"), Mendes (player_id ends with "_8"), or Livramento (player_id ends with "_9") is the target.

## Key Player Notes
- **Logan Costa** is the most technically gifted defender — he can both head crosses away and start attacks.
- **Stopira** (veteran) is an on-field leader; his experience steadies the back four.
- **Ryan Mendes** (captain, all-time top scorer and most-capped player) is the talisman — he drifts inside off the left to create and finish.
- **Jamiro Monteiro (skill 14)** is the creative engine; almost all attacking moments run through him.
- **Garry Rodrigues (skill 14, dribbling 14)** is the dribble-and-shoot wing threat.
- **Livramento (shoot 14)** was the top scorer in qualifying — a mobile forward who works the channels and holds up clearances.

## Tournament Mindset
Cape Verde believes their organization and set-piece prowess can level the playing field against vastly more talented opponents. They will defend stubbornly, take their chances on the counter, and back themselves to steal points.
