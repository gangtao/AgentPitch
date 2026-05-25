# Cape Verde — Tactical Profile

## Identity & Philosophy
The Blue Sharks are the smallest nation ever to qualify for a World Cup, and under Bubista (Pedro Brito) they punch above their weight through obsessive organization, set-piece danger, and a deep low block. Their 4-4-2 is unfashionable but functional — every player works, every block is collective, and every set piece is rehearsed.

## Formation
- Shape: 4-4-2, defensively narrow, occasionally shifting to 4-2-3-1 with Mendes as #10.
- Role mapping (roster index -> tactical role):
  - 0 Vozinha — Veteran goalkeeper.
  - 1 Logan Costa — Right center-back, ball-playing leader.
  - 2 Roberto Lopes — Left center-back, physical anchor.
  - 3 Moreira — Right-back, balanced.
  - 4 Stopira — Veteran left-back, captain.
  - 5 Monteiro — Right central midfielder, technical.
  - 6 Laros Duarte — Left central midfielder, work-rate.
  - 7 Deroy Duarte — Defensive midfielder when shifting to 4-2-3-1.
  - 8 Ryan Mendes — Attacking midfielder / second striker.
  - 9 Garry Rodrigues — Right winger / wide forward.
  - 10 Livramento — Center-forward.

## Style of Play

### Build-up
- Direct under pressure; Vozinha plays long to Livramento or Rodrigues frequently.
- Short build-up reserved for unpressed moments — Costa is the lead passer.
- Full-backs Moreira and Stopira hold width but rarely push past halfway in build-up.
- Deroy or Monteiro drops between center-backs against pressure.

### Pressing
- Mid-block press, occasional triggered high press in coordinated waves.
- Trigger: bad first touch or backward pass under pressure.
- Livramento and Rodrigues lead the press; Mendes harasses the pivot.
- Cape Verde does not chase if first wave is broken — drops immediately into compact 4-4-2.

### Defensive shape
- 4-4-2 deep block, two compact banks of four.
- Lopes and Costa hold a deep line; full-backs tuck inside.
- Wide midfielders Monteiro and L. Duarte sit narrow and tight.
- Total team width when defending is roughly 30 meters.

### Wide play
- Right: Rodrigues is the principal attacking outlet — cuts inside or attacks the byline.
- Left: Mendes drifts wide; Stopira overlaps when fresh.
- Crosses target Livramento and Costa arriving on set pieces.

### Final third
- Mendes is the creative reference — receives between lines, plays through balls.
- Livramento finishes inside the box; Rodrigues shoots from the half-space.
- Cape Verde scores a high proportion of goals from set pieces and crosses.
- They will not over-commit in attack — typically 4-5 players in the opponent's half.

## Set Pieces
- Costa, Lopes, and Livramento are aerial targets.
- Mendes takes most attacking set pieces; Monteiro for the right side.
- Defensive set pieces: man-marking with Lopes on the biggest threat. Cape Verde's set-piece defending is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Vozinha) and pressed: clear long to the CF (player_id ends with "_10", Livramento) or RW (player_id ends with "_9", Rodrigues) — never risk passes near own box.
2. If the CBs (player_id ends with "_1" Logan Costa or "_2" Roberto Lopes) and unpressed: short pass to nearest midfielder; only carry forward if completely uncontested.
3. If player_id ends with "_7" (Deroy Duarte, MID #6): drop between center-backs to facilitate build-up against pressure.
4. If player_id ends with "_8" (Mendes, MID #11; skill 14, dribbling 14, pass 13): receive between lines, play through balls or simple lay-offs.
5. If player_id ends with "_9" (Rodrigues, RW #17): cut inside onto left foot from the right wing, or attack the byline.
6. If player_id ends with "_10" (Livramento, CF #9): run channels, attack near-post crosses, hold up play under pressure.
7. If defending in own half: maintain 4-4-2 compactness, never break shape for a speculative tackle.
8. If turnover in own half: clear long to Livramento (player_id ends with "_10") or Rodrigues (player_id ends with "_9") — get the ball away from danger.
9. If a set piece is awarded: send Costa (player_id ends with "_1"), Lopes (player_id ends with "_2"), and Livramento (player_id ends with "_10") forward; this is a key scoring opportunity.
10. If trailing late: push the full-backs Moreira (player_id ends with "_3") and Stopira (player_id ends with "_4") higher, send Costa (player_id ends with "_1") forward for set pieces, throw extra runners forward.
11. If leading: drop block 12m deeper, defend the box collectively, kill time on every dead ball.
12. If counter-attack opportunity: maximum 3-4 passes, vertical and direct — Rodrigues (player_id ends with "_9") or Livramento (player_id ends with "_10") is the target.

## Key Player Notes
- **Logan Costa** is the most technically gifted defender — he can both head crosses away and start attacks.
- **Stopira** (captain, veteran) is the on-field leader; his experience steadies the back four.
- **Ryan Mendes (skill 14)** is the creative outlet; almost all attacking moments start with him.
- **Garry Rodrigues (skill 14, dribbling 14)** is the dribble-and-shoot wing threat.
- **Livramento (shoot 14)** is a mobile forward who works the channels and holds up clearances.

## Tournament Mindset
Cape Verde believes their organization and set-piece prowess can level the playing field against vastly more talented opponents. They will defend stubbornly, take their chances, and back themselves to steal points.
