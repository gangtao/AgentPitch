# Bosnia and Herzegovina — Tactical Profile

## Identity & Philosophy
Bosnia and Herzegovina are a veteran-led, defensively organized team built around the lingering brilliance of Edin Džeko and a disciplined low block. They have qualified by grinding out results — limited possession, set-piece danger, and a willingness to absorb pressure for long periods. The identity is "veteran nous and direct attacking" — they will not impose tempo, but they punish opponents who underestimate them.

## Formation
- Shape: 4-2-3-1 (becomes 4-4-1-1 defending)
- Role mapping (roster order in `bosnia_and_herzegovina.yaml`):
  - index 0 (`bosnia_and_herzegovina_0`, Vasilj): GK — solid, traditional, distributes long.
  - index 1 (`bosnia_and_herzegovina_1`, Kolašinac): LB — veteran, physical, attacking instincts.
  - index 2 (`bosnia_and_herzegovina_2`, Muharemović): LCB — aerial, physical.
  - index 3 (`bosnia_and_herzegovina_3`, Mujakić): RCB — pure stopper, slow but strong.
  - index 4 (`bosnia_and_herzegovina_4`, Dedić): RB — youngest defender, modern overlapping FB.
  - index 5 (`bosnia_and_herzegovina_5`, Cimirot): DM — defensive anchor, screens.
  - index 6 (`bosnia_and_herzegovina_6`, Tahirović): CM — young technician, build-up brain.
  - index 7 (`bosnia_and_herzegovina_7`, Višća): RW — veteran, set-piece taker, crossing specialist.
  - index 8 (`bosnia_and_herzegovina_8`, Krunić): DM/CM — defensive midfielder (paired with Cimirot in double-pivot).
  - index 9 (`bosnia_and_herzegovina_9`, Demirović): LW/secondary CF — mobile, supports Džeko.
  - index 10 (`bosnia_and_herzegovina_10`, Džeko): CF/captain — target man, the team's reference point.

*Note: Krunić (index 8) is positioned as a deep midfielder forming a double-pivot with Cimirot; Tahirović (index 6) is the more advanced #10. In settled defense the shape collapses into 4-4-1-1 with Tahirović behind Džeko.*

## Style of Play

### Build-up
Slow, direct, with a long-ball Plan B. Vasilj plays to Muharemović or Mujakić; Cimirot/Krunić drop alongside the CBs forming a 4-2 build. If pressed, Vasilj goes LONG to Džeko (10 speed, but 15 strength — he wins flick-ons) and the team chases the second ball. Tahirović is the creative outlet between the lines.

### Pressing (block height + trigger)
Low block. Bosnia do not press — they retreat to a 4-4-1-1 around the edge of their own third and force the opposition to break them down. Press triggers only when opposition takes a heavy touch within 30m of Bosnia's goal AND Tahirović is within 8m.

### Defensive shape
4-4-1-1 — compact, narrow, deep. Krunić shadows the opposition #10; Cimirot screens. Wingers (Višća, Demirović) drop to form a tight midfield bank of four. Distance between lines minimized (~8m). Force opposition wide; defend crosses with aerial CBs.

### Wide play
Veteran Višća (RW) delivers crosses from deep — his quality crossing is Bosnia's most reliable attacking weapon. Dedić overlaps on the right with youthful energy. On the left, Kolašinac is more conservative, Demirović drifts inside to combine with Džeko.

### Final third
Crosses to Džeko's near-post run; set pieces; Tahirović's through-balls when transitions open up. Demirović makes channel runs across the back line. Long shots from Tahirović are a tertiary option.

## Set Pieces
- Corners: Višća delivers everything — inswingers from the right toward Džeko (back post) and Muharemović (near post), outswingers from the left.
- Direct free kicks: Višća from the right; Tahirović from the left.
- Penalties: Džeko first; Demirović second.

## decide() Decision Priorities
1. **Low-block default:** when ball is in Bosnia's half, ALL 10 outfield players within 35m of own goal vertically. Do not chase.
2. If my player_id ends with "_0" (GK, Vasilj): under press, KICK LONG toward "_10" (Džeko) every time — Plan B is the default.
3. If my player_id ends with "_10" (CF/captain, Džeko): position centrally between CBs; when long ball arrives, head/control DOWN to a runner ("_9" Demirović or "_6" Tahirović). Then re-position for the cross.
4. If my player_id ends with "_6" (CM, Tahirović): receive between lines facing forward; if "_9" (Demirović) or "_7" (Višća) makes a back-line run, slip the through-ball.
5. If my player_id ends with "_8" (DM/CM, Krunić): shadow the opposition #10; if they receive between Bosnia's lines, TACKLE immediately.
6. If my player_id ends with "_5" (DM, Cimirot): pure screen — never cross halfway line. Recycle laterally to either CB.
7. If my player_id ends with "_7" (RW, Višća): primary right-side crosser — when receiving wide right within 35m of byline, CROSS to back post immediately. Set-piece taker.
8. If my player_id ends with "_4" (RB, Dedić): overlap aggressively on the right when Bosnia attacks; recover quickly when possession is lost.
9. If my player_id ends with "_1" (LB, Kolašinac): more conservative LB — only overlap when team is trailing.
10. If my player_id ends with "_9" (LW/secondary CF, Demirović): make channel runs across the back line every time Bosnia regains possession. Combine with "_10" (Džeko).
11. If my player_id ends with "_2" or "_3" (CBs, Muharemović/Mujakić): on crosses, head clear long and high — never attempt a controlled clearance.
12. On opposition corner: 10 men in the box; "_9" (Demirović) stays high as outlet.
13. Counter-attack rule: on regain in own third, FIRST PASS forward (to "_6" Tahirović or wide to "_7" Višća) — no backward recycling allowed in transitions.
14. Discipline: Bosnia's veterans ("_10" Džeko, "_1" Kolašinac, "_7" Višća) on yellow should avoid late challenges in defensive third.

## Key Player Notes
- **Edin Džeko (index 10, captain):** the team's spiritual leader — even at his age, his hold-up play and aerial reference define everything. Strength 15, shoot 15. Limit his off-the-ball running — he must conserve energy (stamina 12) for the moments that matter.
- **Edin Višća (index 7):** primary set-piece deliverer. His crossing quality (pass 14, skill 14) is the team's most reliable creator.
- **Benjamin Tahirović (index 6):** the future. Highest-skill midfielder (15). License to roam between the lines as the team's creative outlet.
- **Sead Kolašinac (index 1):** veteran LB. Physical (strength 15) but ageing — pair him with Krunić's defensive coverage on his side.
- **Amar Dedić (index 4):** youngest defender. Modern overlapping fullback — his energy supports Višća's crossing.

## Tournament Mindset
Bosnia know they cannot outplay top teams — they must out-organize them. The plan is to keep games scoreless until 70 minutes, then steal a moment from Džeko's head or Višća's set piece. Their ceiling is limited but their nuisance value is high.
