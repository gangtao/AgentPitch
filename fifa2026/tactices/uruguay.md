# Uruguay — Tactical Profile

## Identity & Philosophy
Uruguay under Marcelo Bielsa is one of the most distinctive tactical projects in world football: relentless man-oriented high pressing, vertical attacks the second possession is won, and a diamond-shaped midfield press that asphyxiates opponents. Bielsa has stripped the team of the old defend-and-Suárez-decides-it identity and replaced it with a young, sprinting, gegen-pressing collective — Valverde everywhere, Núñez stretching the line, Pellistri and Araújo flying down the touchlines. Recent results: third in Copa América 2024 (knocked out by Colombia in the semis), explosive 5-0s against Bolivia and dramatic narrow defeats against the elite — Bielsa Uruguay is rarely boring.

## Formation
- Shape: **4-3-3** (with extreme verticality; pressing morphs into 3-3-1-3 with man-marking)
- Role mapping (roster order in `uruguay.yaml`):
  - index 0: GK — **Sergio Rochet** — modest sweeper-keeper duties, primarily a shot-stopper, plays short when possible.
  - index 1: LB — **Mathías Olivera** — pacy, attacking, asked to push extremely high (Bielsa fullbacks are essentially wingers).
  - index 2: LCB — **José María Giménez** — front-foot defender, aggressive man-marker, will step 25 yards out of position to chase his man.
  - index 3: RCB — **Ronald Araújo** — physical monster, the team's defensive captain, the recovery sprinter who covers Giménez's adventures.
  - index 4: RB — **Guillermo Varela** — experienced, two-footed fullback; more conservative than Olivera but still pushes high; reliable crosser and tackler (replaces Nández in the final 26).
  - index 5: RCM/8 — **Federico Valverde** — the all-action engine, box-to-box, the team's chief carrier, occupies any position the game demands (right half-space mostly).
  - index 6: DM/6 — **Manuel Ugarte** — the destroyer, the screen, all-action ball-winner; Bielsa's chief mid-press leader.
  - index 7: LCM/8 — **Rodrigo Bentancur** — deep-lying playmaker of the trio, the metronome, the calmest passer in the midfield three.
  - index 8: LW — **Maximiliano Araújo** — direct, pacy, hard-running winger, full-throttle 1v1 dribbler.
  - index 9: ST — **Darwin Núñez** — chaos-merchant striker, stretches the line, makes constant runs in behind, never holds the ball, always sprints.
  - index 10: RW — **Facundo Pellistri** — direct right winger, 1v1 specialist, work-rate engine, mirrors Maxi Araújo on the right.

## Style of Play
### Build-up
**Vertical-first, short when possible.** Rochet plays short to Giménez/Araújo. Bentancur drops between them when pressed; Ugarte stays slightly higher as the screen. Fullbacks push **extremely** high — Olivera and Varela are practically wingers. The build-up is short for 2-3 passes, then vertical: **Bentancur or Valverde plays a line-breaking forward pass into Núñez's run in behind**, or wide to Pellistri/Araújo with a winger-fullback overload.

### Pressing
**Extreme high press — Bielsa-style man-to-man.** Press triggers: opposition GK touches the ball (Núñez goes immediately), any opposition back-pass, any opposition first touch heavier than 2 units. **Each Uruguayan player has an assigned opposition player to mark**: forwards mark CBs and DM, midfielders mark midfielders, fullbacks mark wingers. Núñez leads the press constantly. This is the most aggressive press in the tournament.

### Defensive shape
Out-of-possession: **man-marking 4-3-3** that morphs to **3-3-1-3** with fullbacks pushing high to mark wingers. Giménez often steps 20 yards out of the back line to follow his man. Araújo is the **free safety** who sweeps behind. This produces a high-line, high-risk system that demands sprinting.

### Wide play
**Symmetric high-and-wide:** Olivera and Varela both push to the byline; Araújo and Pellistri both attempt 1v1 dribbles inside-to-outside. The wingers are encouraged to take their man on. Crosses (especially low cutbacks) for Núñez and Valverde's late runs.

### Final third
Patterns: **Núñez channel runs** — Bentancur plays vertical into the run, Núñez sprints behind. **Valverde late arrival** at the edge of the box — when the ball goes wide, Valverde sprints into the D for a shot. **Pellistri/Araújo isolation** — give them the ball wide and ask them to beat their man. **Set pieces** delivered hard and flat to attack the near post.

## Set Pieces
- Attacking corners: **Valverde** delivers from both sides (in-swingers, hard and flat to the near post). **Bentancur** alternate. Primary targets: Araújo, Giménez, Núñez at the near post.
- Defending corners: **man-marking** with two zonal post-markers; Araújo attacks the first ball, Giménez the second.
- Free kicks: **Valverde** direct from central and right positions; he has a thunderbolt right foot. **Bentancur** delivers wide set-pieces.
- Penalties: **Núñez** primary, **Valverde** secondary, **Bentancur** tertiary.

## decide() Decision Priorities
Concrete rules the LLM should encode:
1. **If my `role == "FWD"` or `role == "MID"` and team_phase == "defending":** Identify my assigned opposition man-mark (nearest opposition player by role/position); Move to within 3 units of them, ready to Tackle.
2. **If my `player_id` ends with `_9` (ST, Núñez) and any opposition defender's first touch is heavier than 2 units from feet:** Sprint to Tackle / press.
3. **If my `player_id` ends with `_9` (ST, Núñez) and team_phase == "attacking":** Stay on the shoulder of the deepest opposition CB; make constant diagonal runs in behind, never drop deep.
4. **If my `player_id` ends with `_2` (LCB, Giménez) and my marked opposition forward drops deep:** Follow him up to 25 units forward of normal CB position.
5. **If my `player_id` ends with `_3` (RCB, Ronald Araújo):** I am the cover; sit slightly deeper than `_2` (Giménez) and cover the space behind him.
6. **If my `player_id` ends with `_1` (LB, Olivera) or `_4` (RB, Varela) and team_phase == "attacking":** Sprint to byline — fullbacks are wingers in Bielsaball.
7. **If my `player_id` ends with `_5` (RCM, Valverde) and team_phase == "attacking" and ball is in the final third:** Sprint into the box arriving at the edge of the D for a late shot.
8. **If my `player_id` ends with `_6` (DM, Ugarte) and an opponent receives the ball in central midfield:** Tackle immediately — no delay.
9. **If team_phase == "transition_attack":** Prefer the most vertical Pass available (e.g., a 30-unit forward pass to `_9` Núñez) over any sideways option.
10. **If my `role == "FWD"` or `role == "MID"` and team has just lost the ball:** Counter-press within a 7-unit radius for 6 seconds (longest press window in the tournament).
11. **If my `role == "GK"` (player_id `_0`, Rochet) and pressed:** Play short to a CB if safe; if not, punt long to `_9` (Núñez)'s channel run — never play it long without a target.
12. **If team is trailing and minute > 60:** Push EVEN HIGHER — fullbacks to halfway line, `_2` (Giménez) follows the striker everywhere. Accept the risk of conceding.

## Key Player Notes
- **Valverde (8):** Free role within the right half-space. The team's heart-lungs. Late box-arrival is his signature.
- **Núñez (9):** Never holds the ball. Always sprinting. Stretches the field. Will press the GK alone.
- **Giménez (2):** Man-marker extreme — Bielsa license to follow his man anywhere.
- **Araújo (4):** The cover. Captain. Sweeps behind Giménez's adventures.
- **Bielsa note:** No player ever walks. If stamina < 8, the player should still sprint when the press trigger fires. Substitutions are managed by Bielsa's relentless system.

## Tournament Mindset
Uruguay are the high-variance team of the tournament: they will beat anyone 4-1 on a good day and lose 4-1 on a bad one. Bielsa accepts the trade-off. Stamina management is critical — Uruguay must rotate aggressively because the press is unsustainable for back-to-back full matches.
