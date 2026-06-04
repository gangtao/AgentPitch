# New Zealand — Tactical Profile

## Identity & Philosophy
New Zealand under Darren Bazeley are the World Cup's archetypal physical underdog: a direct, hard-working, route-one side built entirely around the aerial dominance and physical presence of Chris Wood, with second-ball pickup by hard-running midfielders and compact defensive shape out of possession. Bazeley — an Englishman with no pretensions to tiki-taka — has accepted what the All Whites are good at and doubled down on it. Recent results: dominant OFC qualification (no surprise), modest friendly results against European mid-tier sides, arriving as the OFC representatives who will compete for 90 minutes through sheer organization and Wood's presence.

## Formation
- Shape: **4-4-2** (compact, narrow, defensively-disciplined, classic British 4-4-2)
- Role mapping (roster order in `new_zealand.yaml`):
  - index 0: GK — **Max Crocombe** — shot-stopper, modest with feet, content to punt long toward Wood.
  - index 1: LB — **Liberato Cacace** — by far the team's best ball-playing defender, modern overlapping LB, the team's only real progressive carrier from defense.
  - index 2: LCB — **Michael Boxall** — physical, aerial duel-winner, no-nonsense defender; primarily a stopper.
  - index 3: RCB — **Tyler Bindon** — younger CB, slightly more progressive on the ball, partners Boxall as the cover.
  - index 4: RB — **Tim Payne** — experienced, conservative, defensive RB; rarely overlaps.
  - index 5: LCM — **Marko Stamenic** — the team's most progressive central midfielder, attempts to thread vertical passes; less of a destroyer.
  - index 6: RCM — **Joe Bell** — captain (or vice), the screen, the disciplined sitter, ball-winner.
  - index 7: AM/RM-CM hybrid — **Matthew Garbett** — the team's most creative midfielder, drifts to support Wood, the closest thing to a #10.
  - index 8: LM/LW — **Elijah Just** — the team's fastest wide player, direct runner, gets in behind, secondary outlet on counters.
  - index 9: ST — **Chris Wood** — the focal point, target striker, aerial dominator, the entire offensive plan revolves around him.
  - index 10: ST/RM — **Kosta Barbarouses** — experienced support striker / wide forward, plays off Wood, picks up knock-downs.

## Style of Play
### Build-up
**Long and direct.** Crocombe punts long toward Wood as the default. Short build-up is attempted only when the press is light, and even then it's a 3-4 pass sequence before going long. **Cacace** is the only defender comfortable carrying the ball; Boxall and Bindon defer to Wood as the outlet. Bell drops between the CBs only when truly pressed. **Route 1 is not a plan B — it is plan A.**

### Pressing
**Low-block by default, occasional high-press in opposition build-up phases.** Press triggers: opposition GK passes short to a CB with no easy outlet (Wood and Barbarouses jump). Otherwise New Zealand sits in a 4-4-2 mid-block and lets the opposition come. The wingers (Just and a wide MID) tuck narrow to support; the fullbacks rarely step out aggressively.

### Defensive shape
Out-of-possession: **classic 4-4-2 compact mid-low block**, two banks of four within 20-25 units of each other. Wood and Barbarouses cover-shadow the opposition pivot but do not chase. The wide midfielders (Just, Garbett/another) tuck in to make the midfield narrow; **the wide channels are conceded** — let them cross, win the aerial duel.

### Wide play
**Limited width in attack.** Cacace overlaps from the left selectively (the only fullback that does so); Payne stays. Crosses come from Cacace's overlap and from Just cutting outside before whipping in. Long throws are a weapon — both Cacace and Payne deliver long throw-ins into Wood at the near post.

### Final third
Patterns: **Long ball into Wood, second ball pickup** by Stamenic, Garbett, or Bell arriving from deep. **Wood flick-on** for Just running the channel. **Cacace overlap-crosses** to Wood at the back post. **Set-pieces** — biggest goal source by a distance. **Long throw-ins** into the box treated as a corner.

## Set Pieces
- Attacking corners: **Stamenic** delivers from both sides (in-swingers to the near post). **Garbett** alternate. Primary targets: **Chris Wood** (penalty spot), Boxall, Bindon attacking the near post.
- Defending corners: **man-marking** — physical CBs handle aerial duels, all hands on deck.
- Free kicks: **Stamenic** direct from central positions, **Garbett** delivers wide free kicks toward Wood.
- Long throw-ins: **Cacace** and **Payne** both have long-throw capability — treated as corner deliveries to Wood.
- Penalties: **Wood** primary, **Barbarouses** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `role == "GK"` (player_id `_0`, Crocombe):** Default action with the ball is a long Pass toward `_9` (Chris Wood)'s vertical channel. Short build-up only if no opposition player within 15 units of any defender.
2. **If my `player_id` ends with `_9` (ST, Wood) and a long ball is incoming:** Hold position centrally, contest aerial duel, attempt flick-on (Pass) toward `_8` (Just) or `_10` (Barbarouses)' run.
3. **If my `role == "MID"` and a long ball is being played toward `_9` (Wood):** Sprint forward to within 8 units of `_9` to win the second ball.
4. **If my `role == "DEF"` (any):** Stay in the back four. `_1` (Cacace) MAY overlap on the left when team_phase == "attacking" AND ball is in opposition half. All others hold position.
5. **If team_phase == "defending":** Drop into 4-4-2 compact block — no player past halfway except `_9` (Wood) and `_10` (Barbarouses). Vertical compactness < 22 units between defensive and midfield lines.
6. **If my `player_id` ends with `_6` (RCM, Joe Bell):** Sit in front of the back four — the screen. Never venture past halfway in open play.
7. **If my `player_id` ends with `_8` (LM, Just) and team_phase == "transition_attack":** Sprint diagonally into the left channel behind the opposition RB.
8. **If team_phase == "transition_defense":** Drop straight back into the 4-4-2 block — New Zealand does NOT counter-press. Get behind the ball.
9. **If my `player_id` ends with `_7` (Garbett) or `_8` (Just) and team_phase == "defending":** Tuck inside narrow, denying central passes. Concede the wide channel.
10. **If team_phase == "attacking" and I am in the opposition third with the ball but no clear pass forward:** Recycle long-Pass back to defense — do NOT attempt to dribble through traffic.
11. **If a throw-in is awarded in the opposition half within 30 units of goal:** Defer to `_1` (Cacace) or `_4` (Payne) — whichever is nearer — for a long throw delivery.
12. **If team is leading 1-0 at minute > 60:** Drop deeper, kill the game; `_9` (Wood) stays high as a counter-attack outlet only.

## Key Player Notes
- **Chris Wood (9):** The entire game plan. Every long ball goes to him. Every set-piece is delivered to his head. Captain of the attack.
- **Cacace (13):** The team's only modern player — overlapping LB, long-throw specialist, the one defender comfortable on the ball.
- **Bell (6):** The disciplined sitter — protects the back four.
- **Just (11):** The pace outlet — the team's only player who can stretch a tired defense.
- **Stamenic (8):** The set-piece specialist — every dead ball delivery within 35 yards is his.

## Tournament Mindset
New Zealand are the World Cup's underdog cliché in the best way: they will play three 90-minute defensive grinds, nick a goal from a set-piece or a Wood flick-on, and try to make it 1-0 ugly. They are realistic — group-stage points are the goal, knockout dreams are a bonus. Stamina-managed: the low block requires discipline more than fitness, but the front two (Wood especially) will tire — Wood at <10 stamina is significantly less threatening, so the long-ball game collapses.
