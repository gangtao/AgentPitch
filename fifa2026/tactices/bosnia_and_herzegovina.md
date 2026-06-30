# Bosnia-Herzegovina — Tactical Profile

## Identity & Philosophy
Sergej Barbarez's Bosnia-Herzegovina are a veteran-led, physical, high-energy side built on defensive organization, set-piece danger and devastating directness when they win the ball. They will not dominate possession; they out-organize and out-muscle opponents, sit in a compact mid-block, and strike on quick transitions toward their 40-year-old talisman Edin Džeko. They reached the knockouts the hard way — grinding results out of Group B alongside Canada, Switzerland and Qatar — and arrive at the Round of 32 as battle-hardened underdogs who relish being underestimated. The DNA: tough to break down, dangerous from dead balls, and lethal when the captain gets one chance in the box.

## Round of 32 Lineup (vs USA, July 1 — Levi's Stadium, Santa Clara — win-or-go-home, away vs host nation)
This is the biggest game in the nation's young history, played in front of a hostile home crowd backing the USMNT. Barbarez reverts to his trusted, pragmatic **4-4-2** — two solid banks of four protecting the veterans up top and Džeko as the focal point. Key team news:
- **Tarik Muharemović (23) returns from suspension** at centre-back — a huge boost that re-stabilizes a back line that looked exposed during the group stage; he partners the aerial enforcer Nikola Katić.
- **Amar Dedić (RB) is questionable** — the team's usual creative full-back is doubtful, so the pacey **Amar Memić deputizes at right-back**, a more conservative, athletic option than the missing overlapping Benfica man.
- **Edin Džeko (40) starts** as the central reference and captain, with **Ermedin Demirović** as his mobile foil doing the dirty work so the talisman stays in the box.
- **Esmir Bajraktarević** (PSV, 21) is the team's spark from the right of midfield — highest dribbling and pace in the XI — with teenager **Kerim Alajbegović** providing energy on the left and **Šunjić + Bašić** as the combative central pair.
- USA context: the hosts are quicker and more technical, will dominate the ball, and carry crowd momentum. Bosnia must defend deep, win the aerial and physical battles, kill the game's tempo, and punish on transitions and set pieces. Win or go home — there is no second chance.

## Formation
- Shape: 4-4-2 (two compact banks of four; Demirović and Džeko up top). Out of possession it becomes a deep 4-4-2 / 4-4-1-1 mid-block; Demirović drops to screen while Džeko leads the line alone.
- Role mapping (roster order in `bosnia_and_herzegovina.yaml`):
  - index 0 (`bosnia_and_herzegovina_0`, Vasilj): GK — solid, traditional shot-stopper; distributes long to Džeko when pressed.
  - index 1 (`bosnia_and_herzegovina_1`, Kolašinac): LB — veteran, very physical, attacking instincts but disciplined in a knockout.
  - index 2 (`bosnia_and_herzegovina_2`, Katić): LCB — dominant aerial stopper (strength 16), wins the duel, heads clear.
  - index 3 (`bosnia_and_herzegovina_3`, Muharemović): RCB — returning from suspension; mobile, composed, the back line's stabilizer.
  - index 4 (`bosnia_and_herzegovina_4`, Memić): RB — pacey deputy for the questionable Dedić; conservative, athletic, defends first.
  - index 5 (`bosnia_and_herzegovina_5`, Alajbegović): LM — young, energetic wide midfielder; carries forward and tucks into a bank of four when defending.
  - index 6 (`bosnia_and_herzegovina_6`, Šunjić): LCM — combative destroyer; shields the back four and breaks up play.
  - index 7 (`bosnia_and_herzegovina_7`, Bašić): RCM — disciplined two-way midfielder; build-up brain and set-piece deliverer.
  - index 8 (`bosnia_and_herzegovina_8`, Bajraktarević): RM — the spark; explosive dribbler and pace (speed 16, dribbling 16) who drives at the USA left-back.
  - index 9 (`bosnia_and_herzegovina_9`, Demirović): CF — the mobile foil; channel runner and presser who frees Džeko; secondary penalty taker.
  - index 10 (`bosnia_and_herzegovina_10`, Džeko): CF — the captain and aerial reference point; hold-up, near-post finish, primary penalty taker.

*Note: the central pair is Šunjić (index 6) the destroyer and Bašić (index 7) the more disciplined two-way passer. Out of possession the wide midfielders Alajbegović (index 5) and Bajraktarević (index 8) drop into a flat bank of four; Demirović tucks back so the shape is effectively 4-4-1-1 with Džeko alone up top.*

## Style of Play

### Build-up
Slow, direct, with a long-ball Plan B. Vasilj plays to Katić or Muharemović; Bašić drops to help circulate. If pressed, Vasilj goes LONG to Džeko (skill 16, strength 15 — he wins flick-ons even at 40) and the team chases the second ball. Bosnia accept low possession against the technically superior hosts and look to play forward early rather than build through midfield.

### Pressing (block height + trigger)
Selective. Bosnia do not press high for long — they retreat into a compact 4-4-2 / 4-4-1-1 around the edge of their own half and force the USA to break them down. Demirović and Bajraktarević step up to harry only on clear triggers: when a USA defender takes a heavy touch within 35m of Bosnia's goal AND Demirović or Bajraktarević is within 8m. Otherwise stay disciplined and deny the space behind.

### Defensive shape
Compact 4-4-2 / 4-4-1-1 — narrow, deep, disciplined. Šunjić and Bašić screen in front of the back four; Alajbegović and Bajraktarević drop to form a flat midfield four. Distance between lines minimized (~8m). Force the USA wide; defend crosses with aerial CBs Katić and Muharemović. Džeko screens the opposition pivot up top while Demirović covers the other.

### Wide play
The threat now flows down the right through **Bajraktarević** — the team's spark, isolated 1v1 to drive at the USA left-back, cut inside and shoot or cross. Memić (RB) backs him conservatively rather than overlapping (deputizing for the questionable Dedić). On the left, Alajbegović works hard and tucks in, with Kolašinac providing the more measured overlap behind. Crosses are aimed at Džeko's near-post run and Demirović's late channel run.

### Final third
Crosses to Džeko's near-post run; set pieces; Bajraktarević's dribbles and Bašić's deliveries when transitions open up. Demirović makes channel runs across the back line and combines with Džeko. Alajbegović arrives late from the left. The plan is few chances, taken well — one Džeko header or one transition can win it.

## Set Pieces
- Corners: Bašić delivers everything — inswingers toward Džeko (back post) and Katić (near post), outswingers toward Muharemović.
- Direct free kicks: Bašić from central/left; Bajraktarević curls from the right.
- Penalties: Džeko first (penalty 15, the captain takes responsibility); Demirović second (penalty 14); Bajraktarević third.

## decide() Decision Priorities
1. **Knockout posture:** win or go home, away at the host nation. Stay compact and defend first; do NOT over-commit. Transitions and set pieces are the route to goal — when possession is regained, get the ball forward to Džeko (`_10`) or Bajraktarević (`_8`) FAST.
2. If my player_id ends with "_0" (GK, Vasilj): under press, KICK LONG toward "_10" (Džeko) — he wins the flick-on. Otherwise distribute short to a CB. Position 6-8m off the line; sweep nothing risky against quick USA runners.
3. If my player_id ends with "_10" (CF, Džeko): position centrally between CBs; on the long ball, head/control DOWN to a runner ("_9" Demirović or "_8" Bajraktarević), then re-position for the cross to the near post. Primary penalty taker.
4. If my player_id ends with "_9" (CF, Demirović): the mobile foil — drift into the channels off the shoulder of the last defender; make a back-line run every time Bosnia regains possession; combine with "_10" (Džeko) and do the pressing dirty work. Secondary penalty taker.
5. If my player_id ends with "_6" (LCM, Šunjić): pure screen — never cross halfway in open play. Shadow the USA #10; if they receive between Bosnia's lines, TACKLE immediately. Recycle laterally to a CB.
6. If my player_id ends with "_7" (RCM, Bašić): the build-up brain and set-piece deliverer; receive from the CBs, circulate, and look to spring "_8" Bajraktarević or play early to "_10" Džeko. Tuck back beside Šunjić when defending.
7. If my player_id ends with "_8" (RM, Bajraktarević) and I receive isolated 1v1: drive at the USA left-back with pace, beat him outside or cut inside to shoot/cutback — Bosnia's main creative spark. Track back into the bank of four when possession is lost.
8. If my player_id ends with "_5" (LM, Alajbegović): energetic two-way runner on the left; arrive late into the box on attacks, then drop into the flat midfield four when defending — keep the left side compact.
9. If my player_id ends with "_4" (RB, Memić): conservative deputy for Dedić — defend first, support Bajraktarević without both pushing high; use pace to recover behind. Only overlap when clearly safe.
10. If my player_id ends with "_1" (LB, Kolašinac): measured overlap to support "_5" (Alajbegović), but never both full-backs high at once; physical in the duel, disciplined in the tackle.
11. If my player_id ends with "_2" or "_3" (CBs, Katić/Muharemović): on crosses, head clear long and high — never attempt a controlled clearance under pressure. Win the aerial duel with the USA forwards; do not get drawn out of the box.
12. On opposition corner: 10 men in the box; "_9" (Demirović) stays high as the transition outlet.
13. Counter-attack rule: on regain in own third, FIRST PASS forward (to "_10" Džeko, "_8" Bajraktarević, or wide to "_9" Demirović) — no backward recycling allowed in transitions.
14. Discipline: veterans ("_1" Kolašinac, "_10" Džeko) and any booked players avoid late challenges in the defensive third — a needless red in a knockout is fatal. Hold and contain rather than dive in.

## Key Player Notes
- **Edin Džeko (index 10, captain):** the team's spiritual leader and aerial reference at 40. Hold-up play and the near-post header still define everything — skill 16, shoot 16, penalty 15. Long-ball target, corner threat and primary penalty taker. Pace is gone (speed 9), so he plays as a static reference point, not a runner.
- **Ermedin Demirović (index 9):** the mobile foil — works the channels, runs the back line and does the defensive dirty work so the target man can stay central. Shoot 14; secondary penalty taker.
- **Esmir Bajraktarević (index 8):** the spark and X-factor — PSV winger with the highest dribbling (16) and pace (speed 16) in the XI. Isolated on the right to attack the USA full-back; scored the decisive playoff penalty vs Italy. The most likely individual moment-maker.
- **Ivan Bašić (index 7):** the disciplined two-way midfielder and primary set-piece deliverer; circulates in build-up and screens beside Šunjić out of possession.
- **Ivan Šunjić (index 6):** the destroyer — combative central screen who shields the back four and breaks up the USA's central play; stays disciplined, never strays forward.
- **Kerim Alajbegović (index 5):** young, energetic wide midfielder bringing running and late box arrivals on the left; tucks into the bank of four when defending.
- **Tarik Muharemović (index 3):** the enforced boost — back from suspension to stabilize the back line; mobile, composed, reads danger and clears.
- **Nikola Katić (index 2):** dominant aerial stopper (strength 16) anchoring the back line; wins the duel and heads everything clear.
- **Amar Memić (index 4):** pacey deputy at right-back for the questionable Dedić; defends first, uses his speed to recover behind the press.
- **Sead Kolašinac (index 1):** the physical veteran left-back; measured overlap, hard in the tackle, disciplined in a knockout.

## Tournament Mindset
This is the biggest game in the country's young footballing history — the Round of 32, away at the host nation, in a hostile Levi's Stadium, win or go home. Bosnia know they will see less of the ball than the quicker, more technical USA; the plan is to out-organize rather than out-play. Defend deep and compact, win the aerial and physical battles, kill the tempo, stay ruthlessly disciplined (a red card ends the dream), and strike from Džeko's head, Demirović's running, a Bašić set piece, or a Bajraktarević moment of magic. One chance taken can shock the hosts and write history.
