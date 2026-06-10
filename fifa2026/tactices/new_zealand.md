# New Zealand — Tactical Profile

## Identity & Philosophy
New Zealand under Darren Bazeley are the World Cup's archetypal physical underdog: a direct, hard-working, route-one side built entirely around the aerial dominance and physical presence of Chris Wood, with second-ball pickup by hard-running midfielders and compact defensive shape out of possession. Bazeley — an Englishman with no pretensions to tiki-taka — has accepted what the All Whites are good at and doubled down on it. Recent results: dominant OFC qualification (no surprise), modest friendly results against European mid-tier sides, arriving as the OFC representatives who will compete for 90 minutes through sheer organization and Wood's presence.

## Formation
- Shape: **4-2-3-1** (compact, narrow, defensively-disciplined; collapses into a **4-4-1-1 block** out of possession)
- Role mapping (roster order in `new_zealand.yaml`):
  - index 0: GK — **Max Crocombe** — shot-stopper, modest with feet, content to punt long toward Wood.
  - index 1: LB — **Liberato Cacace** — by far the team's best ball-playing defender, modern overlapping LB, the team's only real progressive carrier from defense.
  - index 2: LCB — **Michael Boxall** — physical, aerial duel-winner, no-nonsense defender; primarily a stopper.
  - index 3: RCB — **Tyler Bindon** — younger CB, slightly more progressive on the ball, partners Boxall as the cover.
  - index 4: RB — **Tim Payne** — experienced, conservative, defensive RB; rarely overlaps.
  - index 5: LDM — **Marko Stamenic** — left side of the double pivot, the more progressive of the two, attempts to thread vertical passes; less of a destroyer.
  - index 6: CAM — **Sarpreet Singh** — the #10, the team's most creative player (pass 15, dribbling 14); plays off Wood, finds pockets between the lines, feeds the wingers.
  - index 7: RDM — **Joe Bell** — right side of the double pivot, the screen, the disciplined sitter, ball-winner.
  - index 8: LW — **Ben Old** — the team's fastest player (speed 15), direct runner, gets in behind, secondary outlet on counters.
  - index 9: ST — **Chris Wood** — the captain and focal point, target striker, aerial dominator, the entire offensive plan revolves around him.
  - index 10: RW — **Elijah Just** — quick, direct wide forward on the right; runs the channel off Wood's flick-ons, picks up knock-downs.

## Style of Play
### Build-up
**Long and direct.** Crocombe punts long toward Wood as the default. Short build-up is attempted only when the press is light, and even then it's a 3-4 pass sequence before going long. **Cacace** is the only defender comfortable carrying the ball; Boxall and Bindon defer to Wood as the outlet. Bell drops between the CBs only when truly pressed. **Route 1 is not a plan B — it is plan A.**

### Pressing
**Low-block by default, occasional high-press in opposition build-up phases.** Press triggers: opposition GK passes short to a CB with no easy outlet (Wood and Singh jump). Otherwise New Zealand sits in a 4-4-1-1 mid-block and lets the opposition come. The wingers (Old and Just) tuck narrow to support; the fullbacks rarely step out aggressively.

### Defensive shape
Out-of-possession: **compact 4-4-1-1 mid-low block** — the wingers drop alongside the double pivot to form the second bank of four, within 20-25 units of the back line. Wood stays highest; Singh cover-shadows the opposition pivot but does not chase. The wingers (Old, Just) tuck in to make the midfield narrow; **the wide channels are conceded** — let them cross, win the aerial duel.

### Wide play
**Limited width in attack.** Cacace overlaps from the left selectively (the only fullback that does so); Payne stays. Crosses come from Cacace's overlap and from Old cutting outside before whipping in. Long throws are a weapon — both Cacace and Payne deliver long throw-ins into Wood at the near post.

### Final third
Patterns: **Long ball into Wood, second ball pickup** by Stamenic, Singh, or Bell arriving from deep. **Wood flick-on** for Just or Old running the channels. **Cacace overlap-crosses** to Wood at the back post. **Singh's slipped pass** between the lines after a knock-down. **Set-pieces** — biggest goal source by a distance. **Long throw-ins** into the box treated as a corner.

## Set Pieces
- Attacking corners: **Stamenic** delivers from both sides (in-swingers to the near post). **Singh** alternate. Primary targets: **Chris Wood** (penalty spot), Boxall, Bindon attacking the near post.
- Defending corners: **man-marking** — physical CBs handle aerial duels, all hands on deck.
- Free kicks: **Stamenic** direct from central positions, **Singh** delivers wide free kicks toward Wood.
- Long throw-ins: **Cacace** and **Payne** both have long-throw capability — treated as corner deliveries to Wood.
- Penalties: **Wood** primary, **Singh** secondary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `role == "GK"` (player_id `_0`, Crocombe):** Default action with the ball is a long Pass toward `_9` (Chris Wood)'s vertical channel. Short build-up only if no opposition player within 15 units of any defender.
2. **If my `player_id` ends with `_9` (ST, Wood) and a long ball is incoming:** Hold position centrally, contest aerial duel, attempt flick-on (Pass) toward `_8` (Old) or `_10` (Just)'s run.
3. **If my `role == "MID"` and a long ball is being played toward `_9` (Wood):** Sprint forward to within 8 units of `_9` to win the second ball — `_6` (Singh) arrives closest to collect the knock-down.
4. **If my `role == "DEF"` (any):** Stay in the back four. `_1` (Cacace) MAY overlap on the left when team_phase == "attacking" AND ball is in opposition half. All others hold position.
5. **If team_phase == "defending":** Drop into the 4-4-1-1 compact block — no player past halfway except `_9` (Wood) and `_6` (Singh). Vertical compactness < 22 units between defensive and midfield lines.
6. **If my `player_id` ends with `_7` (RDM, Joe Bell):** Sit in front of the back four — the screen. Never venture past halfway in open play.
7. **If my `player_id` ends with `_8` (LW, Old) and team_phase == "transition_attack":** Sprint diagonally into the left channel behind the opposition RB.
8. **If team_phase == "transition_defense":** Drop straight back into the 4-4-1-1 block — New Zealand does NOT counter-press. Get behind the ball.
9. **If my `player_id` ends with `_8` (Old) or `_10` (Just) and team_phase == "defending":** Tuck inside narrow, denying central passes. Concede the wide channel.
10. **If team_phase == "attacking" and I am in the opposition third with the ball but no clear pass forward:** Recycle long-Pass back to defense — do NOT attempt to dribble through traffic.
11. **If a throw-in is awarded in the opposition half within 30 units of goal:** Defer to `_1` (Cacace) or `_4` (Payne) — whichever is nearer — for a long throw delivery.
12. **If team is leading 1-0 at minute > 60:** Drop deeper, kill the game; `_9` (Wood) stays high as a counter-attack outlet only.

## Key Player Notes
- **Chris Wood (9):** The captain and the entire game plan. Every long ball goes to him. Every set-piece is delivered to his head.
- **Cacace (13):** The team's only modern player — overlapping LB, long-throw specialist, the one defender comfortable on the ball.
- **Singh (10):** The #10 and the team's one genuine technician — Bayern-schooled, best passer in the squad (15); turns knock-downs into chances.
- **Bell (6):** The disciplined sitter — protects the back four.
- **Old (19):** The pace outlet on the left (speed 15) — the team's best chance of stretching a tired defense.
- **Just (11):** Quick, willing channel-runner on the right — feeds off Wood's flick-ons.
- **Stamenic (8):** The set-piece specialist — every dead ball delivery within 35 yards is his.

## Tournament Mindset
New Zealand are the World Cup's underdog cliché in the best way: they will play three 90-minute defensive grinds, nick a goal from a set-piece or a Wood flick-on, and try to make it 1-0 ugly. They are realistic — group-stage points are the goal, knockout dreams are a bonus. Stamina-managed: the low block requires discipline more than fitness, but the front line (Wood especially) will tire — Wood at <10 stamina is significantly less threatening, so the long-ball game collapses.
