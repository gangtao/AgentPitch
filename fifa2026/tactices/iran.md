# Iran — Tactical Profile

## Identity & Philosophy
Amir Ghalenoei's Iran is the physical, set-piece-laden, counter-attacking heavyweight of Asia — the antithesis of Japan's possession game. Where Japan wants 65% of the ball, Iran is happy with 40% if they can run hard, foul cleverly, win every aerial duel, and bury one Mehdi Taremi half-chance per match. The identity is **physicality, organization, and clinical counter-attacks** built around the team's captain and talisman, **Mehdi Taremi**, supported by the wide creativity of Jahanbakhsh and Ghoddos. Iran's defensive culture is unmatched in the region: they will defend a 1-0 lead with eleven men behind the ball for 70 minutes and never panic. Recent form: qualified comfortably from the AFC third round, regularly the toughest matchup for Japan and South Korea, with the 2022 Wales match still proving they can win World Cup games against second-tier European sides.

## Formation
- Shape: **4-3-3** in possession (collapses to a **4-5-1 low block** out of possession; can slide to **5-4-1** when defending a lead).
- Role mapping (roster order in `iran.yaml`):
  - index 0: GK — **Alireza Beiranvand** — physically dominant (strength 16), long-throw weapon (he is famous for hurling the ball into the opposition box), traditional shot-stopper rather than a sweeper.
  - index 1: LB — **Ehsan Hajsafi** — veteran, captain-figure, disciplined, rarely overlaps deep, set-piece deliverer.
  - index 2: LCB — **Milad Mohammadi** — converted fullback playing as a left-of-centre CB, faster than most CBs but slightly weaker in the air.
  - index 3: RCB — **Shojae Khalilzadeh** — the aerial monster (strength 17), the duel-winner, the focal point of set-piece defending.
  - index 4: RB — **Ramin Rezaeian** — most attacking of the back four, gets forward on the right when Jahanbakhsh tucks inside.
  - index 5: DM — **Saeid Ezatolahi** — the destroyer, the screen, the foul-merchant, the player who breaks up every opposition attack 30 yards from goal. The defensive heartbeat.
  - index 6: CM — **Saman Ghoddos** — the connector, deep-lying playmaker, the most technical midfielder, sprays diagonals to the wingers.
  - index 7: CM — **Mehdi Ghaedi** — energetic, runs the channel, the box-arrival threat from midfield.
  - index 8: LW — **Mohammad Mohebi** — pacy left-winger, replaces Azmoun's profile in the wide role, direct dribbler, the counter-attack runner.
  - index 9: CF — **Mehdi Taremi** — captain and talisman, drops into the #10 space to receive between the lines, the team's leading scorer, the clinical finisher. Strength 16, skill 16, shoot 16.
  - index 10: RW — **Alireza Jahanbakhsh** — experienced winger, the team's second creator, dead-ball specialist, cuts inside on his left foot.

## Style of Play

### Build-up
Direct and pragmatic. Iran does NOT play out from the back when pressed — Beiranvand will launch a long ball to Taremi or into the channel for Mohebi/Jahanbakhsh to chase. When time permits, Khalilzadeh plays it short to Mohammadi, who passes to Ezatolahi, who recycles to Ghoddos. The first instinct is always **find Taremi between the lines** — he is the pivot. The team is comfortable being patient when not pressed, but the moment a press arrives, the ball goes long. Beiranvand's long throw is a weapon — when Iran wins a throw-in inside the opposition half, Beiranvand sprints up to launch it into the box.

### Pressing
**Mid-block, selective triggers.** Iran does not press the opposition GK. They drop into the **4-5-1** at the halfway line and wait for the ball to enter midfield. Ezatolahi steps to the opposition pivot; Ghoddos and Ghaedi jump the inside-midfielders; Taremi cover-shadows the deepest CB to deny the back-pass. Once the ball enters the wide channels, the fullback (Hajsafi or Rezaeian) and winger (Mohebi or Jahanbakhsh) double-team. The press is not high; it is mid-block compression.

### Defensive shape
Compact **4-5-1** with Taremi as the lone front presser, Mohebi and Jahanbakhsh dropping into a flat midfield five alongside Ezatolahi, Ghoddos, and Ghaedi. The back four sits deep — 25-30 units off goal — denying space in behind. The CBs (especially Khalilzadeh) win every aerial duel inside the box. Against elite opponents, Iran will shift to **5-4-1** with Rezaeian becoming a third CB. The shape is famously stable: hard to break down, low-line, organized.

### Wide play
Both wingers cut inside, which means the fullbacks are the natural width-givers. Hajsafi underlaps on the left; Rezaeian overlaps on the right. Iran's crosses come from **deep** (35-40 yards from goal) and are aimed at Taremi at the near post. Mohebi's pace down the left is the chief counter-attack outlet — Ghoddos's diagonals find him every time.

### Final third
Patterns: Taremi drops to receive between the lines, lays off to Ghoddos who slips through Mohebi sprinting in behind; Jahanbakhsh's cut-inside curler from the right half-space; Taremi's hold-up play and lay-off to a late-arriving Ghaedi; cross from Hajsafi to Taremi at the near post. Iran is a **clinical** team — they create 5-6 chances per match and need to convert one. Taremi's shoot rating of 16 is the difference.

## Set Pieces
**Iran is one of the most dangerous set-piece teams in Asia.** Beiranvand's long throw is a weapon used 5-8 times per match. Khalilzadeh wins every header.
- Attacking corners: **Jahanbakhsh** in-swingers from the right, **Hajsafi** out-swingers from the left. Targets: Khalilzadeh (near post), Mohammadi (penalty spot), Taremi (back post).
- Defending corners: heavy man-marking. Khalilzadeh on the most dangerous striker; Beiranvand attacks any cross within his reach.
- Free kicks: Jahanbakhsh direct from any angle within 28 yards; Taremi from central range.
- Long throws: **Beiranvand** sprints up from the goal to launch throws into the box on any throw-in inside the opposition half.
- Penalties: **Taremi** primary, **Jahanbakhsh** secondary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Beiranvand, #1) and the team wins a throw-in inside the opposition half:** Sprint forward to within 35 units of the throw-in spot to launch a long throw into the box.
2. **If my player_id ends with "_9" (CF Taremi, #9) and team_phase == "attacking":** Drop into the #10 space between the opposition lines, 10-15 units behind the back line; turn and either dribble or Pass forward to the index-8 Mohebi sprinting in behind.
3. **If my player_id ends with "_9" (CF Taremi, #9) and the ball is within 25 units of goal:** Shoot if angle < 35°; shoot rating is 16, take the chance.
4. **If my role == "DEF" and team_phase == "defending":** Stay deep — back four holds a line 25 units off goal. Do not push higher unless ball is past the halfway line.
5. **If my player_id ends with "_5" (DM Ezatolahi, #6) and the opposition has the ball within 35 units of my goal:** Step to the ball-carrier, tackle if within 4 units, foul tactically if the opposition is breaking past me.
6. **If team_phase == "transition_attack":** The index-8 Mohebi (LW) and index-10 Jahanbakhsh (RW) sprint forward immediately; index-9 Taremi stays central; index-6 Ghoddos delivers the long diagonal.
7. **If my player_id ends with "_8" (LW Mohebi, #20) and team_phase == "transition_attack":** Sprint into the channel beyond the opposition RB; receive the index-6 Ghoddos's diagonal.
8. **If my player_id ends with "_3" (RCB Khalilzadeh, #4) and a cross is incoming into my box:** Attack the ball aggressively — win the header. Strength 17.
9. **If team_phase == "defending" and the ball is wide:** Fullback + winger on that side double-team the opposition wide attacker.
10. **If team is leading by 1+ goals after minute 70:** Drop into **5-4-1** with the index-4 Rezaeian becoming a third CB; recycle every set-piece by taking 30 seconds.
11. **If a defensive corner is incoming:** The index-3 Khalilzadeh marks the most dangerous opposition CF; the index-2 Mohammadi covers the penalty spot zone; the index-0 Beiranvand attacks the cross.
12. **Set-pieces 18-30 yards from goal:** Defer to the index-10 Jahanbakhsh (right-footed in-swingers) or the index-9 Taremi (central).

## Key Player Notes
- **Taremi (9):** Captain, talisman, false-9-meets-#10. Drops between the lines to receive, turns, and either finishes or slips through-balls. The team is built around him.
- **Khalilzadeh (3):** The aerial monster. Wins every header in both boxes. Strength 17.
- **Ezatolahi (5):** The destroyer. Tactical fouler. Sets the team's defensive aggression baseline.
- **Beiranvand (0):** The long-throw weapon. Iran scores 2-3 goals per tournament from his throws.
- **Jahanbakhsh (10):** The dead-ball specialist and right-sided creator. Cuts inside, shoots curlers.

## Tournament Mindset
Iran arrives at every World Cup with a single defined goal: **escape the group stage**. They have come close (2018, 2022) and the 2026 squad is the strongest in a decade. The mentality is **defensive solidity first, set-pieces second, Taremi third**. They will defend a 0-0 against Argentina for 88 minutes and win it on a Beiranvand long throw. They will dominate Iraq and Jordan physically. They will be a nightmare matchup for any team that doesn't have an aerial CB pair. The weakness is creativity in open play against a well-organized opponent — when Taremi is well-marked and the long throw doesn't produce, Iran can go an entire half without a clean chance. Discipline is moderate (mostly 13-14) — expect 1-2 yellow cards per match, occasionally a red against a top opponent.
