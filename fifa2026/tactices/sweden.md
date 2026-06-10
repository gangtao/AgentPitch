# Sweden — Tactical Profile

## Identity & Philosophy
Sweden under Graham Potter are rebuilding around a new generation — the strike partnership of Alexander Isak and Viktor Gyökeres represents one of the most lethal twin-9 setups in world football. Potter, who steadied the ship through the Nations League playoff route after replacing Jon Dahl Tomasson, has kept faith with a 4-3-3 (effectively a 4-4-2 in possession with Gyökeres and Isak interchanging) that emphasizes counter-attacking speed, vertical passing, and defensive solidity. The identity is "two world-class forwards, supported by a hard-working unit behind them."

## Formation
- Shape: 4-3-3 (with Isak drifting infield from the left to partner Gyökeres; effectively a 4-2-3-1/4-4-2 hybrid)
- Role mapping (roster order in `sweden.yaml`):
  - index 0 (`sweden_0`, Johansson): GK — first-choice keeper, long distribution toward Isak/Gyökeres.
  - index 1 (`sweden_1`, Gudmundsson): LB — attacking outlet, set-piece deliverer.
  - index 2 (`sweden_2`, Lindelöf): LCB — ball-playing CB and captain, the brain of the defense.
  - index 3 (`sweden_3`, Hien): RCB — physical destroyer, aerial.
  - index 4 (`sweden_4`, Svensson): RB — energetic, overlaps on the right.
  - index 5 (`sweden_5`, Svanberg): DM — anchor, screens the defense.
  - index 6 (`sweden_6`, Ayari): CM — box-to-box engine, ball progression.
  - index 7 (`sweden_7`, Bergvall): CM/#10 — young technician, primary creator, progressive carries.
  - index 8 (`sweden_8`, Isak): LW/second-9 — mobile, dribble + finish, drifts infield and drops into pockets.
  - index 9 (`sweden_9`, Gyökeres): CF — physical runner, leads the line, relentless in behind.
  - index 10 (`sweden_10`, Elanga): RW — speed merchant (18), runs in behind.

## Style of Play

### Build-up
Mixed. Lindelöf builds short when possible (skill 15, pass 15); Johansson goes long to Gyökeres when pressed. Svanberg drops as the deepest midfielder; Bergvall pulls forward to receive between lines. Sweden are happy in transition — they don't NEED the ball to hurt opponents.

### Pressing (block height + trigger)
Mid-block. Press triggers when opposition wide CB receives — Isak or Elanga curve runs to cut off the back pass. Otherwise, Sweden retreats to a 4-5-1 with Gyökeres as the lone presser screening the central #6.

### Defensive shape
4-5-1 / 4-1-4-1 in defense. Bergvall drops to a left-of-center midfield position to compensate for Isak's high starting point. Svanberg shields the back four; Ayari mirrors on the right behind Elanga. Hien dominates aerially; Lindelöf reads the game.

### Wide play
Elanga's speed (18) on the right is Sweden's primary outlet, with Svensson overlapping. On the left, Isak drifts infield off the touchline while Gudmundsson overlaps to keep the width.

### Final third
Two-9 chaos. Isak drops into pockets, drags a CB, opening space for Gyökeres or Elanga to attack in behind. Bergvall supplies through-balls and arrives for cutbacks. Late midfield runners (Bergvall, Ayari) are a tertiary scoring option.

## Set Pieces
- Corners: Bergvall and Gudmundsson deliver — inswingers from the right toward Hien and Gyökeres, outswingers from the left toward Isak's near-post run.
- Direct free kicks: Bergvall from central/right positions; Gudmundsson's left foot from the left.
- Penalties: Isak first; Gyökeres second; Bergvall third.

## decide() Decision Priorities
1. If my player_id ends with "_8" (LW/second-9, Isak): drift infield off the left into the pocket between the opposition DM and CB; when receiving, turn forward and DRIBBLE if 1v1.
2. If my player_id ends with "_9" (CF, Gyökeres): when "_8" (Isak) drops into the pocket, sprint diagonally across the back line — stay the #9 and attack the space in behind.
3. If my player_id ends with "_10" (RW, Elanga): on every regain in Sweden's half, sprint into the RIGHT channel — the long ball is coming. Speed 18 wins all foot-races.
4. If my player_id ends with "_0" (GK, Johansson): if Sweden regains the ball or wins a goal kick under heavy press, kick LONG toward "_9" (Gyökeres) or down the "_10" (Elanga) channel.
5. If my player_id ends with "_7" (CM/#10, Bergvall): always demand the ball facing forward; if a vertical lane to "_8" (Isak) / "_9" (Gyökeres) exists, PASS within 1 tick. Otherwise carry the ball forward through the left-center.
6. If my player_id ends with "_5" (DM, Svanberg): never cross halfway line. Pure screen. If opposition midfielder breaks through, TACKLE.
7. If my player_id ends with "_6" (CM, Ayari): box-to-box engine — when receiving with space ahead in midfield, DRIBBLE forward 10-15m before passing, then continue the run to support the front three.
8. If my player_id ends with "_1" (LB, Gudmundsson): overlap when "_8" (Isak) drifts inside; primary left-side crosser.
9. If my player_id ends with "_2" (LCB, Lindelöf): if no opposition forward within 8m AND a Swedish forward makes a vertical run, PASS the line-breaking long ball (pass 15).
10. If my player_id ends with "_3" (RCB, Hien): physical CB — clear all crosses with strength; never attempt a controlled clearance under pressure.
11. On opposition corner: "_3" (Hien) marks tallest attacker; "_8" (Isak) stays high at halfway line as counter outlet (his pace is wasted in the box defensively).
12. When trailing late: "_3" (Hien) pushes forward for set pieces; switch to a 3-4-3 with "_8" (Isak) and "_10" (Elanga) either side of "_9" (Gyökeres).

## Key Player Notes
- **Alexander Isak (index 8):** technically gifted second-9 off the left — shoot 17, dribbling 16, skill 16. License to drift infield and drop into midfield to receive; expect him to combine 1-2 then sprint into the box.
- **Viktor Gyökeres (index 9):** runner-finisher hybrid — shoot 17, strength 16, speed 16. Leads the line as the #9. His ball-in-behind runs are constant.
- **Lucas Bergvall (index 7):** creator-in-chief and set-piece taker — skill 16, pass 16, dribbling 15. Operates as the advanced central midfielder; progressive carries and through-balls to the strikers.
- **Anthony Elanga (index 10):** pure speed asset (18) on the right. Every long ball or counter targets the channel behind opposition LB.
- **Victor Lindelöf (index 2):** brain of the defense — call him to step into midfield only when Svanberg is pulled out.

## Tournament Mindset
Sweden are not a possession team — they want to absorb pressure and then KILL on a transition with two world-class strikers. If they meet a top-heavy attacking team, the Isak-Gyökeres twin threat could be the most dangerous counter-attacking partnership in the tournament.
