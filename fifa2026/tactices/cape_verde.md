# Cape Verde — Tactical Profile

## Identity & Philosophy
The Blue Sharks (Tubarões Azuis) are the smallest nation by population ever to reach a World Cup, qualifying for their debut in 2026 by topping their CAF group ahead of Cameroon. Under Pedro Leitão Brito — universally known as **Bubista** — they punch far above their weight through obsessive organization, set-piece danger, and quick vertical transitions. The football is unfashionable but functional: every player works, every block is collective, and every restart is rehearsed. Drawn in Group H with Spain, Uruguay and Saudi Arabia, Cape Verde arrive as clear underdogs and embrace it — they expect to defend deep, frustrate, and strike on the break.

## Formation
- Shape: 4-2-3-1, defensively compact, collapsing into a narrow 4-5-1 out of possession (the wide attacking midfielders tuck back alongside the double pivot).
- Role mapping (roster index -> tactical role):
  - 0 Vozinha — Veteran goalkeeper (39), vice-captain; commands the box, distributes long.
  - 1 João Paulo — Left-back, steady and hard-working; overlaps only when fresh.
  - 2 Roberto Lopes (Pico) — Left center-back, physical on-field organizer and leader.
  - 3 Logan Costa — Right center-back (Villarreal); the squad's best defender and ball-playing anchor.
  - 4 Steven Moreira — Right-back, balanced and athletic; provides controlled width.
  - 5 Kevin Pina — Right-sided holding midfielder, ball-winner and connector; big stamina.
  - 6 Yannick Semedo — Left-sided holding midfielder, positional shield who holds the pivot spot.
  - 7 Willy Semedo — Left attacking midfielder, direct runner with a real goal threat.
  - 8 Jamiro Monteiro — Central attacking midfielder (#10), the technical engine and chief creator.
  - 9 Ryan Mendes — Right attacking midfielder, captain, all-time top scorer and most-capped player.
  - 10 Dailon Livramento — Lone center-forward; qualifying breakout, the main attacking reference.

## Style of Play

### Build-up
- Direct under pressure: Vozinha plays long to Livramento or into the channels for the wide attacking midfielders frequently.
- Short build-up is reserved for unpressed moments — Logan Costa is the lead passer who can step out and start play.
- Full-backs Moreira and João Paulo hold width but rarely advance past halfway in build-up.
- Kevin Pina drops between center-backs against pressure; Yannick Semedo holds the pivot spot.

### Pressing
- Mid-block press, with an occasional triggered high press in coordinated waves.
- Trigger: a bad first touch or a backward pass under pressure.
- Livramento and the wide attacking midfielders (Mendes, Willy Semedo) lead the press; Monteiro harasses the opposing pivot.
- Cape Verde does not chase once the first wave is broken — they drop immediately into a compact 4-5-1.

### Defensive shape
- 4-5-1 deep block: a back four with the double pivot and Monteiro flanked by the dropping wide men Willy Semedo and Mendes.
- Lopes and Costa hold a deep, disciplined line; full-backs tuck inside to keep the block narrow.
- Wide attackers Willy Semedo and Mendes track back to form banks of five in midfield.
- Total team width when defending is roughly 30 meters — they protect the center first.

### Wide play
- Right: Mendes (captain) is the principal attacking outlet — drifts inside off the wing to create and finish.
- Left: Willy Semedo runs directly at his full-back; João Paulo overlaps when energy allows.
- Crosses target Livramento and the arriving center-backs (Costa, Lopes) on set pieces.

### Final third
- Monteiro is the creative engine — receives between lines and plays through balls (pass 15, skill 15).
- Livramento finishes inside the box; Willy Semedo shoots from the left half-space.
- Mendes drifts inside from the right to combine and finish.
- Cape Verde score a high proportion of goals from set pieces and crosses.
- They will not over-commit — typically only 4-5 players in the opponent's half.

## Set Pieces
- Costa, Lopes, and Livramento are the aerial targets.
- Mendes takes most attacking set pieces and is the primary penalty taker; Monteiro delivers from the left.
- Defensive set pieces: man-marking with Lopes on the biggest threat. Cape Verde's set-piece defending is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Vozinha) and pressed: clear long to the CF (player_id ends with "_10", Livramento) or right AM (player_id ends with "_9", Mendes) — never risk passes near own box.
2. If the CBs (player_id ends with "_2" Roberto Lopes or "_3" Logan Costa) and unpressed: short pass to nearest midfielder; only carry forward if completely uncontested (Costa, idx 3, is the trusted progressor).
3. If player_id ends with "_5" (Kevin Pina, MID #6): drop between center-backs to facilitate build-up against pressure; player_id "_6" (Yannick Semedo, MID #16) holds the pivot spot.
4. If player_id ends with "_8" (Monteiro, MID #10; skill 15, dribbling 15, pass 15): receive between lines, play through balls or simple lay-offs — this is the creative hub.
5. If player_id ends with "_9" (Mendes, right AM #20): drift inside off the right wing to combine, or attack the byline.
6. If player_id ends with "_10" (Livramento, CF #19): run channels, attack near-post crosses, hold up play under pressure.
7. If defending in own half: maintain 4-5-1 compactness, never break shape for a speculative tackle.
8. If turnover in own half: clear long to Livramento (player_id ends with "_10") or Mendes (player_id ends with "_9") — get the ball away from danger.
9. If a set piece is awarded: send Lopes (player_id ends with "_2"), Costa (player_id ends with "_3"), and Livramento (player_id ends with "_10") forward; this is a key scoring opportunity.
10. If trailing late: push the full-backs Moreira (player_id ends with "_4") and João Paulo (player_id ends with "_1") higher, send Costa (player_id ends with "_3") forward for set pieces, throw extra runners forward.
11. If leading: drop the block 12m deeper, defend the box collectively, kill time on every dead ball.
12. If counter-attack opportunity: maximum 3-4 passes, vertical and direct — Mendes (player_id ends with "_9"), Willy Semedo (player_id ends with "_7"), or Livramento (player_id ends with "_10") is the target.

## Key Player Notes
- **Logan Costa (idx 3)** is the most talented player in the squad — a Villarreal/LaLiga center-back who can both head crosses away and start attacks; the defensive anchor and lead passer.
- **Roberto Lopes / "Pico" (idx 2)** is the on-field leader; his experience steadies the back four and he man-marks the biggest aerial threat.
- **Ryan Mendes (idx 9)** — captain, all-time top scorer (22 goals) and most-capped player (94+ caps); at 36 he is the talisman who drifts inside off the right to create and finish, and the primary set-piece and penalty taker.
- **Jamiro Monteiro (idx 8, skill 15)** is the creative engine; almost all attacking moments run through him between the lines.
- **Kevin Pina (idx 5, stamina 16)** is the midfield ball-winner who lets the attacking band stay forward.
- **Willy Semedo (idx 7, shoot 13)** is the direct left-sided runner who arrives in the box late.
- **Dailon Livramento (idx 10, shoot 14)** was the qualifying breakout, scoring decisive goals against Cameroon and Eswatini — a mobile forward who works the channels and holds up long clearances.
- **Vozinha (idx 0)** is the 39-year-old veteran keeper and vice-captain, a calming organizer behind the deep block.

## Tournament Mindset
Cape Verde believe their organization and set-piece prowess can level the playing field against vastly more talented opponents in Group H. On their World Cup debut they will defend stubbornly, take their chances on the counter, and back themselves to steal a result that the smallest qualifying nation has no business taking.
