# Cape Verde — Tactical Profile

## Identity & Philosophy
The Blue Sharks are the smallest nation ever to qualify for a World Cup, and under Bubista (Pedro Leitão Brito) they punch above their weight through obsessive organization, set-piece danger, and quick vertical transitions. Their football is unfashionable but functional — every player works, every block is collective, and every set piece is rehearsed.

## Formation
- Shape: 4-2-3-1, defensively compact, dropping into a narrow 4-5-1 out of possession (the wide attacking midfielders tuck back alongside the double pivot).
- Role mapping (roster index -> tactical role):
  - 0 Vozinha — Veteran goalkeeper, vice-captain.
  - 1 João Paulo — Left-back, steady and hard-working.
  - 2 Roberto Lopes (Pico) — Left center-back, physical.
  - 3 Logan Costa — Right center-back, ball-playing anchor.
  - 4 Steven Moreira — Right-back, balanced.
  - 5 Kevin Pina — Right-sided holding midfielder, ball-winner and connector.
  - 6 Yannick Semedo — Left-sided holding midfielder, positional shield.
  - 7 Willy Semedo — Left attacking midfielder, direct runner with a goal threat.
  - 8 Jamiro Monteiro — Central attacking midfielder (#10), technical engine.
  - 9 Ryan Mendes — Right attacking midfielder, captain.
  - 10 Dailon Livramento — Lone center-forward.

## Style of Play

### Build-up
- Direct under pressure; Vozinha plays long to Livramento or into the channels for the wide attacking midfielders frequently.
- Short build-up reserved for unpressed moments — Costa is the lead passer.
- Full-backs Moreira and João Paulo hold width but rarely push past halfway in build-up.
- Kevin Pina drops between center-backs against pressure; Yannick Semedo holds the pivot spot.

### Pressing
- Mid-block press, occasional triggered high press in coordinated waves.
- Trigger: bad first touch or backward pass under pressure.
- Livramento and the wide attacking midfielders (Mendes, Willy Semedo) lead the press; Monteiro harasses the pivot.
- Cape Verde does not chase if first wave is broken — drops immediately into compact 4-5-1.

### Defensive shape
- 4-5-1 deep block: a back four with the double pivot and Monteiro flanked by the dropping wide men Willy Semedo and Mendes.
- Lopes and Costa hold a deep line; full-backs tuck inside.
- Wide attackers Willy Semedo and Mendes track back to make banks of five in midfield.
- Total team width when defending is roughly 30 meters.

### Wide play
- Right: Mendes (captain) is the principal attacking outlet — drifts inside off the wing to create and finish.
- Left: Willy Semedo runs direct at his fullback; João Paulo overlaps when fresh.
- Crosses target Livramento and Costa arriving on set pieces.

### Final third
- Monteiro is the creative engine — receives between lines, plays through balls.
- Livramento finishes inside the box; Willy Semedo shoots from the left half-space.
- Mendes (captain, all-time top scorer) drifts inside from the right to combine and finish.
- Cape Verde scores a high proportion of goals from set pieces and crosses.
- They will not over-commit in attack — typically 4-5 players in the opponent's half.

## Set Pieces
- Costa, Lopes, and Livramento are aerial targets.
- Mendes takes most attacking set pieces; Monteiro for the left side.
- Defensive set pieces: man-marking with Lopes on the biggest threat. Cape Verde's set-piece defending is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Vozinha) and pressed: clear long to the CF (player_id ends with "_10", Livramento) or right AM (player_id ends with "_9", Mendes) — never risk passes near own box.
2. If the CBs (player_id ends with "_2" Roberto Lopes or "_3" Logan Costa) and unpressed: short pass to nearest midfielder; only carry forward if completely uncontested.
3. If player_id ends with "_5" (Kevin Pina, MID #6): drop between center-backs to facilitate build-up against pressure; player_id "_6" (Yannick Semedo, MID #16) holds the pivot spot.
4. If player_id ends with "_8" (Monteiro, MID #10; skill 14, dribbling 14, pass 14): receive between lines, play through balls or simple lay-offs.
5. If player_id ends with "_9" (Mendes, right AM #20): drift inside off the right wing to combine, or attack the byline.
6. If player_id ends with "_10" (Livramento, CF #19): run channels, attack near-post crosses, hold up play under pressure.
7. If defending in own half: maintain 4-5-1 compactness, never break shape for a speculative tackle.
8. If turnover in own half: clear long to Livramento (player_id ends with "_10") or Mendes (player_id ends with "_9") — get the ball away from danger.
9. If a set piece is awarded: send Lopes (player_id ends with "_2"), Costa (player_id ends with "_3"), and Livramento (player_id ends with "_10") forward; this is a key scoring opportunity.
10. If trailing late: push the full-backs Moreira (player_id ends with "_4") and João Paulo (player_id ends with "_1") higher, send Costa (player_id ends with "_3") forward for set pieces, throw extra runners forward.
11. If leading: drop block 12m deeper, defend the box collectively, kill time on every dead ball.
12. If counter-attack opportunity: maximum 3-4 passes, vertical and direct — Mendes (player_id ends with "_9"), Willy Semedo (player_id ends with "_7"), or Livramento (player_id ends with "_10") is the target.

## Key Player Notes
- **Logan Costa** is the most technically gifted defender — he can both head crosses away and start attacks.
- **Roberto Lopes (Pico)** is an on-field leader; his experience steadies the back four.
- **Ryan Mendes** (captain, all-time top scorer and most-capped player) is the talisman — he drifts inside off the right to create and finish.
- **Jamiro Monteiro (skill 14)** is the creative engine; almost all attacking moments run through him.
- **Kevin Pina (discipline 14, stamina 15)** is the midfield ball-winner who lets the attacking band stay forward.
- **Willy Semedo (shoot 12)** is the direct left-sided runner who arrives in the box late.
- **Livramento (shoot 14)** was the top scorer in qualifying — a mobile forward who works the channels and holds up clearances.

## Tournament Mindset
Cape Verde believes their organization and set-piece prowess can level the playing field against vastly more talented opponents. They will defend stubbornly, take their chances on the counter, and back themselves to steal points.
