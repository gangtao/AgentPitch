# Uruguay — Tactical Profile

## Identity & Philosophy
Uruguay under Marcelo Bielsa is one of the most distinctive tactical projects in world football: relentless man-oriented high pressing, vertical attacks the second possession is won, and a diamond-shaped midfield press that asphyxiates opponents. Bielsa has stripped the team of the old defend-and-Suárez-decides-it identity (Luis Suárez is absent from the 2026 squad for the first time since 2010) and replaced it with a young, sprinting, gegen-pressing collective — Valverde the captain and engine everywhere, Núñez stretching the line, Maxi Araújo flying down the flank, the creative de Arrascaeta drifting in from the left. The team is built on the elite Araújo–Giménez centre-back pairing and a ball-winning Ugarte screen. Recent results: third in Copa América 2024, explosive high-scoring wins, and dramatic narrow defeats against the elite — Bielsa Uruguay is rarely boring.

**Matchday 1 (June 15, 2026):** drew 1-1 with Saudi Arabia in Miami. Saudi Arabia led through Al-Amri (41'); substitute **Maxi Araújo equalised on 80'** to rescue a point. Bielsa rotated heavily and started **Fernando Muslera** in goal. No suspensions or injuries reported. Uruguay underwhelmed and cannot afford another slip before the final-group decider with Spain. For Matchday 2 vs Cape Verde (June 21), the probable XI promotes Maxi Araújo into the wide-forward berth ahead of Pellistri, with Muslera retained in goal.

## Formation
- Shape: **4-3-3** (with extreme verticality; pressing morphs into 3-3-1-3 with man-marking. Bielsa will flex to a 4-2-3-1 against some opponents, pushing a creator behind Núñez)
- Role mapping (roster order in `uruguay.yaml`):
  - index 0: GK — **Fernando Muslera** — veteran keeper in a record 5th World Cup; started Matchday 1 and is the probable Matchday 2 starter. Modest sweeper-keeper duties, primarily a shot-stopper, plays short when possible (Rochet the in-form alternative).
  - index 1: LB — **Mathías Olivera** — pacy, attacking, asked to push extremely high (Bielsa fullbacks are essentially wingers).
  - index 2: LCB — **José María Giménez** — front-foot defender, aggressive man-marker, will step 25 yards out of position to chase his man; nears 100 caps and a senior leader.
  - index 3: RCB — **Ronald Araújo** — physical monster, the defensive anchor, the recovery sprinter who covers Giménez's adventures.
  - index 4: RB — **Guillermo Varela** — experienced, two-footed fullback; more conservative than Olivera but still pushes high; reliable crosser and tackler.
  - index 5: RCM/8 — **Federico Valverde** — the **captain** and all-action engine, box-to-box, the team's chief carrier, occupies any position the game demands (right half-space mostly).
  - index 6: DM/6 — **Manuel Ugarte** — the destroyer, the screen, all-action ball-winner; Bielsa's chief mid-press leader, freeing Valverde to advance.
  - index 7: LCM/8 — **Rodrigo Bentancur** — deep-lying playmaker of the trio, the metronome, the calmest passer in the midfield three (Nicolás de la Cruz is the like-for-like creative alternative here).
  - index 8: LW — **Giorgian de Arrascaeta** — the chief creator; left-sided forward who drifts inside into the pockets, the team's most technical passer and a genuine goal threat from the half-space.
  - index 9: ST — **Darwin Núñez** — chaos-merchant striker, stretches the line, makes constant runs in behind, never holds the ball, always sprints.
  - index 10: RW — **Maximiliano Araújo** — pacy Sporting CP wide forward (natural left winger deployed here as the touchline-hugging wide threat), the Matchday 1 goalscorer; high-stamina 1v1 runner who attacks the outside and darts in behind (Pellistri the like-for-like alternative on this flank).

## Style of Play
### Build-up
**Vertical-first, short when possible.** Muslera plays short to Giménez/Araújo. Bentancur drops between them when pressed; Ugarte stays slightly higher as the screen. Fullbacks push **extremely** high — Olivera and Varela are practically wingers. The build-up is short for 2-3 passes, then vertical: **Bentancur or Valverde plays a line-breaking forward pass into Núñez's run in behind**, or finds de Arrascaeta between the lines or Maxi Araújo wide with a winger-fullback overload.

### Pressing
**Extreme high press — Bielsa-style man-to-man.** Press triggers: opposition GK touches the ball (Núñez goes immediately), any opposition back-pass, any opposition first touch heavier than 2 units. **Each Uruguayan player has an assigned opposition player to mark**: forwards mark CBs and DM, midfielders mark midfielders, fullbacks mark wingers. Núñez leads the press constantly. This is the most aggressive press in the tournament.

### Defensive shape
Out-of-possession: **man-marking 4-3-3** that morphs to **3-3-1-3** with fullbacks pushing high to mark wingers. Giménez often steps 20 yards out of the back line to follow his man. Araújo is the **free safety** who sweeps behind. This produces a high-line, high-risk system that demands sprinting.

### Wide play
**Asymmetric:** on the **RIGHT**, Maxi Araújo stays wide and attacks the touchline 1v1, with Varela overlapping. On the **LEFT**, de Arrascaeta drifts inside into the half-space, vacating the touchline for the high-and-wide Olivera to overlap. Crosses (especially low cutbacks) for Núñez and Valverde's late runs.

### Final third
Patterns: **Núñez channel runs** — Bentancur or de Arrascaeta plays vertical into the run, Núñez sprints behind. **Valverde late arrival** at the edge of the box — when the ball goes wide, Valverde sprints into the D for a shot. **de Arrascaeta pockets** — receives between the lines and slides through-balls or shoots. **Maxi Araújo isolation** — give him the ball wide and ask him to beat his man. **Set pieces** delivered hard and flat to attack the near post.

## Set Pieces
- Attacking corners: **de Arrascaeta** delivers from both sides (in-swingers) with **Valverde** the alternate (hard and flat to the near post). Primary targets: Araújo, Giménez, Núñez at the near post.
- Defending corners: **man-marking** with two zonal post-markers; Araújo attacks the first ball, Giménez the second.
- Free kicks: **Valverde** direct from central and right positions — he has a thunderbolt right foot; **de Arrascaeta** delivers wide/left set-pieces and curls central efforts.
- Penalties: **Valverde** primary (penalty 17, the team's coolest from the spot), **Núñez** secondary, **de Arrascaeta** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `role == "FWD"` or `role == "MID"` and team_phase == "defending":** Identify my assigned opposition man-mark (nearest opposition player by role/position); Move to within 3 units of them, ready to Tackle.
2. **If my `player_id` ends with `_9` (ST, Núñez) and any opposition defender's first touch is heavier than 2 units from feet:** Sprint to Tackle / press.
3. **If my `player_id` ends with `_9` (ST, Núñez) and team_phase == "attacking":** Stay on the shoulder of the deepest opposition CB; make constant diagonal runs in behind, never drop deep.
4. **If my `player_id` ends with `_2` (LCB, Giménez) and my marked opposition forward drops deep:** Follow him up to 25 units forward of normal CB position.
5. **If my `player_id` ends with `_3` (RCB, Ronald Araújo):** I am the cover; sit slightly deeper than `_2` (Giménez) and cover the space behind him.
6. **If my `player_id` ends with `_1` (LB, Olivera) or `_4` (RB, Varela) and team_phase == "attacking":** Sprint to byline — fullbacks are wingers in Bielsaball.
7. **If my `player_id` ends with `_5` (RCM, Valverde — captain) and team_phase == "attacking" and ball is in the final third:** Sprint into the box arriving at the edge of the D for a late shot.
8. **If my `player_id` ends with `_6` (DM, Ugarte) and an opponent receives the ball in central midfield:** Tackle immediately — no delay.
9. **If my `player_id` ends with `_8` (LW, de Arrascaeta) and team has the ball:** Drift inside into the left half-space; when I receive between the lines, turn forward and Pass through to `_9` (Núñez)'s run or Shoot from the edge of the box — never recycle backward by default.
10. **If team_phase == "transition_attack":** Prefer the most vertical Pass available (e.g., a 30-unit forward pass to `_9` Núñez) over any sideways option.
11. **If my `role == "FWD"` or `role == "MID"` and team has just lost the ball:** Counter-press within a 7-unit radius for 6 seconds (longest press window in the tournament).
12. **If my `role == "GK"` (player_id `_0`, Muslera) and pressed:** Play short to a CB if safe; if not, punt long to `_9` (Núñez)'s channel run — never play it long without a target.
13. **If team is trailing and minute > 60:** Push EVEN HIGHER — fullbacks to halfway line, `_2` (Giménez) follows the striker everywhere. Accept the risk of conceding.

## Key Player Notes
- **Valverde (8) — captain:** Free role within the right half-space. The team's heart-lungs and dead-ball/penalty leader. Late box-arrival is his signature.
- **Núñez (9):** Now at Al Hilal after leaving Liverpool. Never holds the ball. Always sprinting. Stretches the field. Will press the GK alone.
- **Maxi Araújo (11) — index 10, wide forward:** Sporting CP pace merchant and Matchday 1 match-saver; a natural left winger fielded here as the touchline-hugging wide threat, high stamina, direct 1v1 runner who darts in behind for low cutbacks.
- **de Arrascaeta (10):** The creative fulcrum — most technical player in the side. Drifts in from the left, plays through-balls, takes the wide/left set-pieces. Bielsa's only pure playmaker in the XI.
- **Giménez (2):** Man-marker extreme — Bielsa license to follow his man anywhere; senior leader nearing 100 caps.
- **Araújo (4):** The cover and defensive anchor. Sweeps behind Giménez's adventures.
- **Bentancur (7):** The metronome; Nicolás de la Cruz is the creative like-for-like swap when Bielsa wants more guile in midfield.
- **Bielsa note:** No player ever walks. If stamina < 8, the player should still sprint when the press trigger fires. Substitutions are managed by Bielsa's relentless system.

## Tournament Mindset
Uruguay are the high-variance team of the tournament: they will beat anyone 4-1 on a good day and lose 4-1 on a bad one. Bielsa accepts the trade-off. Stamina management is critical — Uruguay must rotate aggressively because the press is unsustainable for back-to-back full matches.
