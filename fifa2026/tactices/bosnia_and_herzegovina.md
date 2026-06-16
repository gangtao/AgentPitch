# Bosnia and Herzegovina — Tactical Profile

## Identity & Philosophy
Bosnia and Herzegovina are a veteran-led, defensively organized team built around a disciplined low block and set-piece danger. They have qualified by grinding out results — limited possession, set-piece danger, and a willingness to absorb pressure for long periods. The identity is "veteran nous and direct attacking" — they will not impose tempo, but they punish opponents who underestimate them. Under Sergej Barbarez they play a compact 4-4-2 so that in-form striker Ermedin Demirović can do the running alongside a target man. With 40-year-old talisman Edin Džeko nursing a persistent shoulder injury (a late omission against Canada, his June 18 availability touch-and-go), 27-year-old Jovo Lukić — who headed the opener against Canada — leads the line in his place.

## Formation
- Shape: 4-4-2 (becomes a flat 4-4-2 mid/low block defending)
- Role mapping (roster order in `bosnia_and_herzegovina.yaml`):
  - index 0 (`bosnia_and_herzegovina_0`, Vasilj): GK — solid, traditional, distributes long.
  - index 1 (`bosnia_and_herzegovina_1`, Kolašinac): LB — veteran, physical, attacking instincts.
  - index 2 (`bosnia_and_herzegovina_2`, Muharemović): LCB — aerial, physical, first-choice ball-player.
  - index 3 (`bosnia_and_herzegovina_3`, Katić): RCB — pure stopper, dominant in the air, slow but very strong.
  - index 4 (`bosnia_and_herzegovina_4`, Dedić): RB — the team's main creative outlet, modern overlapping FB.
  - index 5 (`bosnia_and_herzegovina_5`, Bajraktarević): LM — young winger, the team's dribbler and spark.
  - index 6 (`bosnia_and_herzegovina_6`, Tahirović): LCM — young technician, build-up brain, deep playmaker.
  - index 7 (`bosnia_and_herzegovina_7`, Šunjić): RCM — combative central screen, the destroyer of the pair.
  - index 8 (`bosnia_and_herzegovina_8`, Memić): RM — energetic wide runner, tracks back to keep the bank of four.
  - index 9 (`bosnia_and_herzegovina_9`, Demirović): CF — mobile striker, does the dirty work and channel running.
  - index 10 (`bosnia_and_herzegovina_10`, Lukić): CF — target man, the team's aerial reference point (deputizing for the injured captain Džeko).

*Note: in midfield, Tahirović (index 6) is the creative deep playmaker and Šunjić (index 7) is the defensive screen — together they form the central pair, with Bajraktarević (index 5) and Memić (index 8) as the wide midfielders. In settled defense the shape stays a compact, flat 4-4-2 with Demirović dropping to press alongside Tahirović while Lukić holds the line.*

## Style of Play

### Build-up
Slow, direct, with a long-ball Plan B. Vasilj plays to Muharemović or Katić; Tahirović drops alongside the CBs forming a 3-build. If pressed, Vasilj goes LONG to Lukić (strength 15, aerially strong — he wins flick-ons) and the team chases the second ball. Tahirović is the creative outlet between the lines.

### Pressing (block height + trigger)
Mid/low block. Bosnia do not press high — they retreat to a flat 4-4-2 around the edge of their own half and force the opposition to break them down. Press triggers only when opposition takes a heavy touch within 30m of Bosnia's goal AND Demirović or Tahirović is within 8m.

### Defensive shape
Flat 4-4-2 — compact, narrow, deep. Šunjić screens in front of the back four; Tahirović tucks in. Wingers (Bajraktarević, Memić) drop to form a tight midfield bank of four. Demirović pressures the ball while Džeko screens the opposition pivot. Distance between lines minimized (~8m). Force opposition wide; defend crosses with aerial CBs.

### Wide play
Creativity flows down the right: Dedić (RB) overlaps aggressively, the team's most reliable supply line, with Memić providing the wide runner ahead of him. On the left, Bajraktarević is the dribbler who carries and cuts inside; Kolašinac is more conservative behind him. Crosses are aimed at Lukić's near-post run.

### Final third
Crosses to Lukić's near-post run; set pieces; Tahirović's through-balls when transitions open up. Demirović makes channel runs across the back line and combines with Lukić. Bajraktarević's dribbling on the left and long shots are a tertiary option.

## Set Pieces
- Corners: Tahirović delivers everything — inswingers toward Lukić (back post) and Katić (near post), outswingers toward Muharemović. (Lukić headed in just such a corner against Canada.)
- Direct free kicks: Tahirović from central/left; Bajraktarević from the right.
- Penalties: Bajraktarević first (scored the winning playoff penalty vs Italy) with Džeko sidelined; Tahirović second.

## decide() Decision Priorities
1. **Low-block default:** when ball is in Bosnia's half, ALL 10 outfield players within 35m of own goal vertically. Do not chase.
2. If my player_id ends with "_0" (GK, Vasilj): under press, KICK LONG toward "_10" (Lukić) every time — Plan B is the default.
3. If my player_id ends with "_10" (CF, Lukić): position centrally between CBs; when long ball arrives, head/control DOWN to a runner ("_9" Demirović or "_6" Tahirović). Then re-position for the cross.
4. If my player_id ends with "_6" (LCM, Tahirović): receive between lines facing forward; if "_9" (Demirović) or "_5" (Bajraktarević) makes a back-line run, slip the through-ball.
5. If my player_id ends with "_7" (RCM, Šunjić): pure screen — never cross halfway line. Shadow the opposition #10; if they receive between Bosnia's lines, TACKLE immediately. Recycle laterally to either CB.
6. If my player_id ends with "_5" (LM, Bajraktarević): receive on the left, DRIBBLE inside at the defender, then shoot or slip "_9" (Demirović); track back to the bank of four when possession is lost.
7. If my player_id ends with "_4" (RB, Dedić): overlap aggressively on the right when Bosnia attacks — primary supply line, CROSS to Džeko's near post when wide within 35m of byline; recover quickly when possession is lost.
8. If my player_id ends with "_8" (RM, Memić): energetic wide runner ahead of Dedić; combine on the right then drop to keep the midfield four compact.
9. If my player_id ends with "_1" (LB, Kolašinac): more conservative LB — only overlap when team is trailing.
10. If my player_id ends with "_9" (CF, Demirović): make channel runs across the back line every time Bosnia regains possession. Combine with "_10" (Lukić) and do the defensive pressing dirty work.
11. If my player_id ends with "_2" or "_3" (CBs, Muharemović/Katić): on crosses, head clear long and high — never attempt a controlled clearance.
12. On opposition corner: 10 men in the box; "_9" (Demirović) stays high as outlet.
13. Counter-attack rule: on regain in own third, FIRST PASS forward (to "_6" Tahirović or wide to "_4" Dedić / "_5" Bajraktarević) — no backward recycling allowed in transitions.
14. Discipline: Bosnia's veterans ("_1" Kolašinac) and yellow-carded players ("_9" Demirović, "_3" Katić both booked vs Canada) should avoid late challenges in defensive third.

## Key Player Notes
- **Jovo Lukić (index 10):** the 27-year-old leading the line with captain Džeko injured. A 20-goal Romanian-league season earned the call; headed the opener against Canada from a corner. Strength 15, shoot 14 — an aerial target man and near-post finisher rather than a creator. Use him as the long-ball reference and corner threat.
- **Edin Džeko (index 10 understudy, captain):** the team's spiritual leader — at 40, his hold-up play and aerial reference still define everything when fit, but a persistent shoulder injury (touch-and-go for June 18) keeps him on the bench; a high-impact late substitute when chasing a goal.
- **Ermedin Demirović (index 9):** the perfect foil up top — mobile, hard-working, does the dirty work and channel running so the target man can stay in the box. Shoot 14.
- **Benjamin Tahirović (index 6):** the future. Highest-skill midfielder (15). License to roam between the lines as the team's creative outlet and deep playmaker; primary set-piece deliverer.
- **Esmir Bajraktarević (index 5):** 21-year-old PSV winger and the team's spark — highest dribbling (16) and speed (15). Scored the winning playoff penalty vs Italy; secondary penalty/free-kick taker.
- **Amar Dedić (index 4):** Benfica right-back and the team's main creative supply line — modern overlapping fullback whose energy (stamina 16) drives the right flank.
- **Nikola Katić (index 3):** dominant aerial stopper (strength 16) anchoring the back line alongside Muharemović.

## Tournament Mindset
Bosnia know they cannot outplay top teams — they must out-organize them. The plan is to keep games scoreless until 70 minutes, then steal a moment from Lukić's head, Demirović's running, a Tahirović set piece, or Džeko off the bench. Their ceiling is limited but their nuisance value is high — they aim to reach the round of 16 for the first time in Group B alongside Canada, Switzerland and Qatar.
