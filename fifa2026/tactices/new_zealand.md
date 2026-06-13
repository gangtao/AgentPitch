# New Zealand — Tactical Profile

## Identity & Philosophy
New Zealand under Darren Bazeley are the World Cup's archetypal physical underdog — and the lowest-ranked side in the tournament. This is a direct, hard-working side built around the aerial dominance and physical presence of captain Chris Wood (NZ's all-time top scorer, 45 goals in 88 caps), with second-ball pickup by hard-running midfielders and a compact, disciplined block out of possession. Bazeley — an Englishman in his first tournament as head coach — has accepted what the All Whites are good at and doubled down on it: route-one delivery into Wood, set-piece threat, and ugly 1-0 organization. They reached USA/Canada/Mexico via a flawless OFC qualification campaign (their first World Cup in 16 years) and land in Group G alongside Belgium, Egypt and Iran. Recent friendlies have seen Bazeley adopt an even more defensive stance.

## Formation
- Shape: **4-3-3** (a deep, mid-block-leaning 4-3-3; collapses into a **4-5-1 / 4-4-1-1 block** out of possession with the wide forwards dropping in and Singh shuttling back)
- Role mapping (roster order in `new_zealand.yaml`):
  - index 0: GK — **Max Crocombe** (Millwall) — first-choice keeper, beat Alex Paulsen for the No. 1 jersey; shot-stopper, modest with feet, content to punt long toward Wood.
  - index 1: LB — **Liberato Cacace** (Wrexham) — by far the team's best ball-playing defender, modern overlapping LB, long-throw specialist, the only real progressive carrier from defense.
  - index 2: LCB — **Michael Boxall** (Minnesota United) — physical, aerial duel-winner, no-nonsense defender; the senior stopper of the pair.
  - index 3: RCB — **Finn Surman** (Portland Timbers) — younger, mobile CB; partners Boxall and provides cover and recovery pace.
  - index 4: RB — **Tyler Bindon** (Nottingham Forest) — strong, athletic young defender deployed at right-back; comfortable stepping into a CB if needed.
  - index 5: LCM — **Joe Bell** (Viking FK) — the screen, the disciplined sitter and ball-winner; protects the back four, sits deepest of the three.
  - index 6: CM — **Marko Stamenic** (Swansea City) — the more progressive central midfielder, attempts vertical passes, primary set-piece deliverer; box-to-box engine.
  - index 7: RCM/#10 — **Sarpreet Singh** (Wellington Phoenix) — the team's most creative player (pass 15, dribbling 14); plays off Wood, finds pockets between the lines, feeds the wide forwards.
  - index 8: LW — **Ben Old** (Saint-Étienne) — the team's fastest player (speed 15), direct runner, gets in behind, the main outlet in transition.
  - index 9: ST — **Chris Wood** (Nottingham Forest) — captain and focal point, target striker, aerial dominator; the entire offensive plan revolves around him.
  - index 10: RW — **Matthew Garbett** (Peterborough United) — energetic wide forward / advanced runner on the right; runs the channel off Wood's flick-ons and picks up knock-downs.

## Style of Play

### Build-up
**Long and direct.** Crocombe punts long toward Wood as the default. Short build-up is attempted only when the press is light, and even then it is a 3-4 pass sequence before going long. **Cacace** is the only defender comfortable carrying the ball; Boxall and Surman defer to Wood as the outlet. Bell drops between the CBs only when truly pressed. **Route 1 is not a plan B — it is plan A.**

### Pressing
**Low-to-mid block by default, occasional high-press in opposition build-up phases.** Press triggers: opposition GK passes short to a CB with no easy outlet (Wood and Singh jump). Otherwise New Zealand sits deep in its block and lets the opposition come. The wide forwards (Old and Garbett) tuck narrow to support; the fullbacks rarely step out aggressively.

### Defensive shape
Out-of-possession: **compact 4-5-1 / 4-4-1-1 mid-low block** — the wide forwards drop into a midfield line of four/five, within 20-25 units of the back line. Wood stays highest; Singh and Stamenic cover-shadow the opposition pivots but do not chase. The wide forwards (Old, Garbett) tuck in to make the midfield narrow; **the wide channels are conceded** — let them cross, win the aerial duel.

### Wide play
**Limited width in attack.** Cacace overlaps from the left selectively (the only fullback that does so); Bindon stays disciplined on the right. Crosses come from Cacace's overlap and from Old cutting outside before whipping in. Long throws are a weapon — Cacace in particular delivers long throw-ins into Wood at the near post.

### Final third
Patterns: **Long ball into Wood, second ball pickup** by Stamenic, Singh, or Bell arriving from deep. **Wood flick-on** for Old or Garbett running the channels. **Cacace overlap-crosses** to Wood at the back post. **Singh's slipped pass** between the lines after a knock-down. **Set-pieces** — the single biggest goal source. **Long throw-ins** into the box treated as a corner.

## Set Pieces
- Attacking corners: **Stamenic** delivers from both sides (in-swingers to the near post). **Singh** alternate. Primary targets: **Chris Wood** (penalty spot), Boxall, Surman, Bindon attacking the near post.
- Defending corners: **man-marking** — physical CBs handle aerial duels, all hands on deck.
- Free kicks: **Stamenic** direct from central positions; **Singh** delivers wide free kicks toward Wood.
- Long throw-ins: **Cacace** delivers — treated as corner deliveries to Wood.
- Penalties: **Wood** primary, **Singh** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `role == "GK"` (player_id `_0`, Crocombe):** Default action with the ball is a long Pass toward `_9` (Chris Wood)'s vertical channel. Short build-up only if no opposition player within 15 units of any defender.
2. **If my `player_id` ends with `_9` (ST, Wood) and a long ball is incoming:** Hold position centrally, contest the aerial duel, attempt flick-on (Pass) toward `_8` (Old) or `_10` (Garbett)'s run. Wood's strength/offensive (17/16) means he wins most contests.
3. **If my `role == "MID"` and a long ball is being played toward `_9` (Wood):** Sprint forward to within 8 units of `_9` to win the second ball — `_7` (Singh) arrives closest to collect the knock-down; `_6` (Stamenic) supports.
4. **If my `role == "DEF"` (any):** Stay in the back four. `_1` (Cacace) MAY overlap on the left when team_phase == "attacking" AND ball is in opposition half. All others hold position.
5. **If team_phase == "defending":** Drop into the 4-5-1 / 4-4-1-1 compact block — no player past halfway except `_9` (Wood). Vertical compactness < 22 units between defensive and midfield lines.
6. **If my `player_id` ends with `_5` (LCM, Joe Bell):** Sit in front of the back four — the screen. Never venture past halfway in open play.
7. **If my `player_id` ends with `_8` (LW, Old) and team_phase == "transition_attack":** Sprint diagonally into the left channel behind the opposition RB — he is the fastest outlet.
8. **If team_phase == "transition_defense":** Drop straight back into the block — New Zealand does NOT counter-press. Get behind the ball.
9. **If my `player_id` ends with `_8` (Old) or `_10` (Garbett) and team_phase == "defending":** Tuck inside narrow, denying central passes. Concede the wide channel.
10. **If team_phase == "attacking" and I am in the opposition third with the ball but no clear pass forward:** Recycle long-Pass back to defense — do NOT attempt to dribble through traffic.
11. **If a throw-in is awarded in the opposition half within 30 units of goal:** Defer to `_1` (Cacace) for a long throw delivery into Wood.
12. **If team is leading 1-0 at minute > 60:** Drop deeper, kill the game; `_9` (Wood) stays high as a counter-attack outlet only.

## Key Player Notes
- **Chris Wood (9):** The captain and the entire game plan. Every long ball goes to him; every set-piece is delivered to his head. Strength 17, shoot 16, offensive 16 — physically dominant target man and the primary penalty taker.
- **Cacace (13):** The team's most modern player — overlapping LB, long-throw specialist, the one defender comfortable on the ball.
- **Singh (10):** The creative hub and the squad's best passer (15) — Bayern-schooled; turns knock-downs into chances.
- **Bell (6):** The disciplined deepest midfielder — protects the back four, rarely crosses halfway.
- **Old (19):** The pace outlet on the left (speed 15) — New Zealand's best chance of stretching a tired defense in transition.
- **Stamenic (8):** The set-piece specialist and progressive midfielder — every dead-ball delivery within 35 yards is his.
- **Garbett (17):** Energetic right-sided forward who runs the channels off Wood's flick-ons.
- **Surman / Boxall:** The physical centre-back pairing — aerial dominance is the price of conceding the wide areas.

## Tournament Mindset
New Zealand are the World Cup's underdog cliché in the best way: as the tournament's lowest-ranked side they will play three 90-minute defensive grinds, nick a goal from a set-piece or a Wood flick-on, and try to make it 1-0 ugly. They are realistic — group-stage points against Egypt and Iran are the goal; an upset of Belgium is the dream. Stamina-managed: the low block requires discipline more than fitness, but the front line (Wood especially) will tire — Wood at <10 stamina is significantly less threatening, and the long-ball game collapses with him.
