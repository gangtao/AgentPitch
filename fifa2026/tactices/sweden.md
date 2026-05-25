# Sweden — Tactical Profile

## Identity & Philosophy
Sweden under Jon Dahl Tomasson are rebuilding around a new generation — the strike partnership of Alexander Isak and Viktor Gyökeres represents one of the most lethal twin-9 setups in world football. Tomasson has shifted from the old Ibrahimović-era pragmatism to a 4-3-3 (effectively a 4-4-2 in possession with Gyökeres and Isak interchanging) that emphasizes counter-attacking speed, vertical passing, and defensive solidity. The identity is "two world-class forwards, supported by a hard-working unit behind them."

## Formation
- Shape: 4-3-3 (with Gyökeres often dropping/drifting wide-right to let Isak be the #9; effectively a 4-2-3-1/4-4-2 hybrid)
- Role mapping (roster order in `sweden.yaml`):
  - index 0 (`sweden_0`, Olsen): GK — experienced, long distribution toward Isak/Gyökeres.
  - index 1 (`sweden_1`, Augustinsson): LB — attacking outlet, set-piece deliverer.
  - index 2 (`sweden_2`, Lindelöf): LCB — ball-playing CB, the brain of the defense.
  - index 3 (`sweden_3`, Hien): RCB — physical destroyer, aerial.
  - index 4 (`sweden_4`, Krafth): RB — disciplined, less attacking than Augustinsson.
  - index 5 (`sweden_5`, Svanberg): DM — anchor, screens the defense.
  - index 6 (`sweden_6`, Bergvall): CM — young technician, progressive carries.
  - index 7 (`sweden_7`, Forsberg): #10/LM — primary creator, free role.
  - index 8 (`sweden_8`, Elanga): LW — speed merchant (18), runs in behind.
  - index 9 (`sweden_9`, Isak): CF — mobile, dribble + finish, drops into pockets.
  - index 10 (`sweden_10`, Gyökeres): RW/second-9 — physical runner, drifts to right or partners Isak centrally.

## Style of Play

### Build-up
Mixed. Lindelöf builds short when possible (skill 15, pass 15); Olsen goes long to Gyökeres when pressed. Svanberg drops as the deepest midfielder; Forsberg pulls left to receive between lines. Sweden are happy in transition — they don't NEED the ball to hurt opponents.

### Pressing (block height + trigger)
Mid-block. Press triggers when opposition wide CB receives — Gyökeres or Elanga curve runs to cut off the back pass. Otherwise, Sweden retreats to a 4-5-1 with Isak as the lone presser screening the central #6.

### Defensive shape
4-5-1 / 4-1-4-1 in defense. Forsberg drops to a left-midfield position to compensate for Elanga's high starting point. Svanberg shields the back four; Bergvall mirrors on the right when needed. Hien dominates aerially; Lindelöf reads the game.

### Wide play
Elanga's speed (18) on the left is Sweden's primary outlet. Augustinsson overlaps. On the right, Gyökeres drifts wide to combine with Krafth, then attacks centrally on cutbacks.

### Final third
Two-9 chaos. Isak drops into pockets, drags a CB, opening space for Gyökeres or Elanga to attack in behind. Forsberg supplies through-balls and arrives for cutbacks. Long-range Forsberg shooting is a tertiary option.

## Set Pieces
- Corners: Forsberg delivers from both sides — inswingers from the right toward Hien and Gyökeres, outswingers from the left toward Isak's near-post run.
- Direct free kicks: Forsberg from anywhere; his left foot is a weapon.
- Penalties: Isak first; Gyökeres second; Forsberg third.

## decide() Decision Priorities
1. If my player_id ends with "_9" (CF, Isak): if the ball is in midfield, drop into the pocket between the opposition DM and CB; when receiving, turn forward and DRIBBLE if 1v1.
2. If my player_id ends with "_10" (RW/second-9, Gyökeres): when "_9" (Isak) drops, sprint diagonally across the back line — depending on position, become the #9.
3. If my player_id ends with "_8" (LW, Elanga): on every regain in Sweden's half, sprint into the LEFT channel — the long ball is coming. Speed 18 wins all foot-races.
4. If my player_id ends with "_0" (GK, Olsen): if Sweden regains the ball or wins a goal kick under heavy press, kick LONG toward "_10" (Gyökeres) or down the "_8" (Elanga) channel.
5. If my player_id ends with "_7" (#10/LM, Forsberg): always demand the ball facing forward; if a vertical lane to "_9" (Isak) / "_10" (Gyökeres) exists, PASS within 1 tick. Otherwise carry the ball wide-left.
6. If my player_id ends with "_5" (DM, Svanberg): never cross halfway line. Pure screen. If opposition midfielder breaks through, TACKLE.
7. If my player_id ends with "_6" (CM, Bergvall): progressive carrier — when receiving with space ahead in midfield, DRIBBLE forward 10-15m before passing.
8. If my player_id ends with "_1" (LB, Augustinsson): overlap when "_8" (Elanga) cuts inside; primary left-side crosser.
9. If my player_id ends with "_2" (LCB, Lindelöf): if no opposition forward within 8m AND a Swedish forward makes a vertical run, PASS the line-breaking long ball (pass 15).
10. If my player_id ends with "_3" (RCB, Hien): physical CB — clear all crosses with strength; never attempt a controlled clearance under pressure.
11. On opposition corner: "_3" (Hien) marks tallest attacker; "_9" (Isak) stays high at halfway line as counter outlet (his pace is wasted in the box defensively).
12. When trailing late: "_3" (Hien) pushes forward for set pieces; switch to a 3-4-3 with "_10" (Gyökeres) on right of front 3.

## Key Player Notes
- **Alexander Isak (index 9):** technically gifted #9 — shoot 17, dribbling 16, skill 16. License to drop into midfield to receive; expect him to combine 1-2 then sprint into the box.
- **Viktor Gyökeres (index 10):** runner-finisher hybrid — shoot 17, strength 16, speed 16. Operates as second-9 / right-drifter. His ball-in-behind runs are constant.
- **Emil Forsberg (index 7):** creator-in-chief and set-piece taker. Free role on the left. Veteran calm in transitions.
- **Anthony Elanga (index 8):** pure speed asset (18). Every long ball or counter targets the channel behind opposition RB.
- **Victor Lindelöf (index 2):** brain of the defense — call him to step into midfield only when Svanberg is pulled out.

## Tournament Mindset
Sweden are not a possession team — they want to absorb pressure and then KILL on a transition with two world-class strikers. If they meet a top-heavy attacking team, the Isak-Gyökeres twin threat could be the most dangerous counter-attacking partnership in the tournament.
