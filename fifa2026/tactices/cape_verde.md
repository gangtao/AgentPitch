# Cape Verde — Tactical Profile

## Identity & Philosophy
The Blue Sharks (Tubarões Azuis) are the smallest nation by population ever to reach a World Cup, qualifying for their debut in 2026 by topping their CAF group ahead of Cameroon. Under Pedro Leitão Brito — universally known as **Bubista** — they punch far above their weight through obsessive organization, set-piece danger, and quick vertical transitions. The football is unfashionable but functional: every player works, every block is collective, and every restart is rehearsed. Drawn in Group H with Spain, Uruguay and Saudi Arabia, Cape Verde have already shocked the tournament — a 0-0 draw with Spain on Matchday 1 (Vozinha keeping out a barrage of shots) and a thrilling 2-2 fightback against two-time champions Uruguay on Matchday 2. They sit on 2 points and travel to Houston knowing a win over Saudi Arabia could carry the smallest qualifying nation in history into the knockout rounds.

## Formation
- Shape: 4-2-3-1, defensively compact, collapsing into a narrow 4-5-1 out of possession (the wide attacking midfielders tuck back alongside the double pivot).
- Role mapping (roster index -> tactical role):
  - 0 Vozinha — Veteran goalkeeper (40), vice-captain; commands the box, distributes long. Man of the match vs Spain.
  - 1 João Paulo — Left-back, steady and hard-working; deputizing for the suspended Sidny Lopes Cabral.
  - 2 Diney — Left center-back, physical stopper who partners Pico in the heart of the deep block.
  - 3 Roberto Lopes (Pico) — Right center-back, on-field organizer and leader; man-marks the biggest aerial threat.
  - 4 Steven Moreira — Right-back, balanced and athletic; provides controlled width.
  - 5 Kevin Pina — Right-sided holding midfielder, ball-winner and connector; big stamina, scored vs Uruguay.
  - 6 Marco Duarte — Left-sided holding midfielder, positional shield who holds the pivot spot.
  - 7 Garry Rodrigues — Left attacking midfielder, direct runner with a real goal threat off the left.
  - 8 Jamiro Monteiro — Central attacking midfielder (#10), the technical engine and chief creator.
  - 9 Ryan Mendes — Right attacking midfielder, captain, all-time top scorer; set to win his 100th cap.
  - 10 Gilson Benchimol — Lone center-forward; mobile attacking reference who works the channels.

## Style of Play

### Build-up
- Direct under pressure: Vozinha plays long to Benchimol or into the channels for the wide attacking midfielders frequently.
- Short build-up is reserved for unpressed moments — Pico (Roberto Lopes) and Diney step out and start play.
- Full-backs Moreira and João Paulo hold width but rarely advance past halfway in build-up.
- Kevin Pina drops between center-backs against pressure; Marco Duarte holds the pivot spot.

### Pressing
- Mid-block press, with an occasional triggered high press in coordinated waves.
- Trigger: a bad first touch or a backward pass under pressure.
- Benchimol and the wide attacking midfielders (Mendes, Rodrigues) lead the press; Monteiro harasses the opposing pivot.
- Cape Verde does not chase once the first wave is broken — they drop immediately into a compact 4-5-1.

### Defensive shape
- 4-5-1 deep block: a back four with the double pivot and Monteiro flanked by the dropping wide men Rodrigues and Mendes.
- Lopes and Diney hold a deep, disciplined line; full-backs tuck inside to keep the block narrow.
- Wide attackers Rodrigues and Mendes track back to form banks of five in midfield.
- Total team width when defending is roughly 30 meters — they protect the center first.

### Wide play
- Right: Mendes (captain) is the principal attacking outlet — drifts inside off the wing to create and finish.
- Left: Rodrigues runs directly at his full-back; João Paulo overlaps when energy allows.
- Crosses target Benchimol and the arriving center-backs (Lopes, Diney) on set pieces.

### Final third
- Monteiro is the creative engine — receives between lines and plays through balls (pass 15, skill 15).
- Benchimol finishes inside the box; Rodrigues shoots from the left half-space.
- Mendes drifts inside from the right to combine and finish.
- Cape Verde score a high proportion of goals from set pieces and crosses.
- They will not over-commit — typically only 4-5 players in the opponent's half.

## Set Pieces
- Lopes, Diney, and Benchimol are the aerial targets.
- Mendes takes most attacking set pieces and is the primary penalty taker; Monteiro delivers from the left.
- Defensive set pieces: man-marking with Lopes on the biggest threat. Cape Verde's set-piece defending is well-drilled.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Vozinha) and pressed: clear long to the CF (player_id ends with "_10", Benchimol) or right AM (player_id ends with "_9", Mendes) — never risk passes near own box.
2. If the CBs (player_id ends with "_2" Diney or "_3" Roberto Lopes) and unpressed: short pass to nearest midfielder; only carry forward if completely uncontested (Pico, idx 3, is the trusted progressor).
3. If player_id ends with "_5" (Kevin Pina, MID #6): drop between center-backs to facilitate build-up against pressure; player_id "_6" (Marco Duarte, MID #8) holds the pivot spot.
4. If player_id ends with "_8" (Monteiro, MID #10; skill 15, dribbling 15, pass 15): receive between lines, play through balls or simple lay-offs — this is the creative hub.
5. If player_id ends with "_9" (Mendes, right AM #20): drift inside off the right wing to combine, or attack the byline.
6. If player_id ends with "_10" (Benchimol, CF #19): run channels, attack near-post crosses, hold up play under pressure.
7. If defending in own half: maintain 4-5-1 compactness, never break shape for a speculative tackle.
8. If turnover in own half: clear long to Benchimol (player_id ends with "_10") or Mendes (player_id ends with "_9") — get the ball away from danger.
9. If a set piece is awarded: send Lopes (player_id ends with "_3"), Diney (player_id ends with "_2"), and Benchimol (player_id ends with "_10") forward; this is a key scoring opportunity.
10. If trailing late: push the full-backs Moreira (player_id ends with "_4") and João Paulo (player_id ends with "_1") higher, send Lopes (player_id ends with "_3") forward for set pieces, throw extra runners forward.
11. If leading: drop the block 12m deeper, defend the box collectively, kill time on every dead ball.
12. If counter-attack opportunity: maximum 3-4 passes, vertical and direct — Mendes (player_id ends with "_9"), Rodrigues (player_id ends with "_7"), or Benchimol (player_id ends with "_10") is the target.

## Key Player Notes
- **Roberto Lopes / "Pico" (idx 3)** is the on-field leader and lead passer; his experience steadies the back four and he man-marks the biggest aerial threat — he can both head crosses away and start attacks.
- **Diney (idx 2)** is the physical stopper alongside Pico in the deep block, dominant in the air and uncompromising in the tackle.
- **Ryan Mendes (idx 9)** — captain, all-time top scorer and most-capped player, set to make his 100th appearance vs Saudi Arabia; the talisman who drifts inside off the right to create and finish, and the primary set-piece and penalty taker.
- **Jamiro Monteiro (idx 8, skill 15)** is the creative engine; almost all attacking moments run through him between the lines.
- **Kevin Pina (idx 5, stamina 16)** is the midfield ball-winner who lets the attacking band stay forward — and a goalscorer, having struck against Uruguay on Matchday 2.
- **Garry Rodrigues (idx 7, dribbling 14)** is the direct left-sided runner who carries the ball and arrives in the box late.
- **Gilson Benchimol (idx 10, shoot 14)** is the mobile lone forward who works the channels, attacks crosses, and holds up long clearances.
- **Vozinha (idx 0)** is the 40-year-old veteran keeper and vice-captain, man of the match against Spain — a calming organizer behind the deep block.

## Tournament Mindset
Cape Verde have already proven their organization and set-piece prowess can level the playing field against vastly more talented opponents — two points from Spain and Uruguay is beyond what anyone expected. On Matchday 3 against Saudi Arabia they smell a historic round-of-32 place: they will defend stubbornly, take their chances on the counter, and back themselves to win the one game in Group H where they are not the underdogs. A victory in Houston would write the smallest qualifying nation in World Cup history into the knockout rounds.
