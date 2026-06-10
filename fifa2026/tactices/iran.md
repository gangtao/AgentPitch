# Iran — Tactical Profile

## Identity & Philosophy
Amir Ghalenoei's Iran is the physical, set-piece-laden, counter-attacking heavyweight of Asia — the antithesis of Japan's possession game. Where Japan wants 65% of the ball, Iran is happy with 40% if they can run hard, foul cleverly, win every aerial duel, and bury one Mehdi Taremi half-chance per match. The identity is **physicality, organization, and clinical counter-attacks** built around the talisman and lone striker **Mehdi Taremi**, supported by the wide creativity of captain Alireza Jahanbakhsh and the technical control of Saman Ghoddos. Iran's defensive culture is unmatched in the region: they will defend a 1-0 lead with eleven men behind the ball for 70 minutes and never panic. Recent form: qualified comfortably from the AFC third round, regularly the toughest matchup for Japan and South Korea, with the 2022 Wales match still proving they can win World Cup games against second-tier European sides. For 2026, Ghalenoei built a domestic-heavy, defensively disciplined squad with Jahanbakhsh as captain.

## Formation
- Shape: **4-2-3-1** in possession (collapses to a **4-5-1 / 4-2-3-1 low block** out of possession; can slide to **5-4-1** when defending a lead). The double pivot screens the back four; Taremi is the lone striker with a three-man band behind him.
- Role mapping (roster order in `iran.yaml`):
  - index 0: GK — **Alireza Beiranvand** — physically dominant (strength 16), long-throw weapon (he is famous for hurling the ball into the opposition box), traditional shot-stopper rather than a sweeper.
  - index 1: LB — **Milad Mohammadi** — veteran left-back, positionally disciplined, rarely overlaps deep, underlaps to support the cutting-inside winger.
  - index 2: LCB — **Shojae Khalilzadeh** — the aerial monster (strength 17), the duel-winner, the focal point of set-piece defending.
  - index 3: RCB — **Ali Nemati** — physical, no-frills stopper (strength 16), wins the duels alongside Khalilzadeh.
  - index 4: RB — **Ramin Rezaeian** — most attacking of the back four, gets forward on the right when Jahanbakhsh tucks inside.
  - index 5: DM (pivot) — **Saeid Ezatolahi** — the destroyer, the screen, the foul-merchant, the player who breaks up every opposition attack 30 yards from goal. The defensive heartbeat of the double pivot.
  - index 6: DM (pivot) — **Rouzbeh Cheshmi** — towering pivot partner (strength 16), a CB-midfield hybrid who holds the screen, plus a long-range strike and set-piece goal threat (shoot 13).
  - index 7: LW / left of the three — **Mehdi Ghaedi** — pacy wide-left runner in the attacking band (speed 15, dribbling 15), direct dribbler, the counter-attack outlet.
  - index 8: CAM / #10 — **Saman Ghoddos** — the central attacking midfielder behind Taremi, the connector and the most technical midfielder (pass 15), links the pivots to the striker and sprays diagonals to the wide players.
  - index 9: RW / right of the three — **Alireza Jahanbakhsh** — **captain**, experienced winger, the team's chief creator and dead-ball specialist, cuts inside on his left foot.
  - index 10: CF — **Mehdi Taremi** — talisman and lone striker, drops into the #10 space to receive between the lines, the team's leading scorer, the clinical finisher. Strength 16, skill 16, shoot 16.

## Style of Play

### Build-up
Direct and pragmatic. Iran does NOT play out from the back when pressed — Beiranvand will launch a long ball to Taremi or into the channel for Ghaedi/Jahanbakhsh to chase. When time permits, Khalilzadeh plays it short to Nemati or out to Mohammadi, who passes to Ezatolahi, who recycles to Cheshmi. The first instinct is always **find Taremi between the lines** — he is the pivot. The team is comfortable being patient when not pressed, but the moment a press arrives, the ball goes long. Beiranvand's long throw is a weapon — when Iran wins a throw-in inside the opposition half, Beiranvand sprints up to launch it into the box.

### Pressing
**Mid-block, selective triggers.** Iran does not press the opposition GK. They drop into the **4-5-1** at the halfway line and wait for the ball to enter midfield. Ezatolahi steps to the opposition pivot; Cheshmi and Ghoddos jump the inside-midfielders; Taremi cover-shadows the deepest CB to deny the back-pass. Once the ball enters the wide channels, the fullback (Mohammadi or Rezaeian) and winger (Ghaedi or Jahanbakhsh) double-team. The press is not high; it is mid-block compression.

### Defensive shape
Compact **4-5-1** with Taremi as the lone front presser, Ghaedi and Jahanbakhsh dropping wide into a flat midfield five alongside the double pivot Ezatolahi and Cheshmi, with Ghoddos tucking in centrally. The back four sits deep — 25-30 units off goal — denying space in behind. The CBs (especially Khalilzadeh) win every aerial duel inside the box. Against elite opponents, Iran will shift to **5-4-1** with Rezaeian becoming a third CB. The shape is famously stable: hard to break down, low-line, organized.

### Wide play
Both wingers cut inside, which means the fullbacks are the natural width-givers. Mohammadi underlaps on the left; Rezaeian overlaps on the right. Iran's crosses come from **deep** (35-40 yards from goal) and are aimed at Taremi at the near post. Ghaedi's pace down the left is the chief counter-attack outlet — Ghoddos's diagonals find him every time.

### Final third
Patterns: Taremi drops to receive between the lines, lays off to Ghoddos (the #10) who slips through Ghaedi sprinting in behind; Jahanbakhsh's cut-inside curler from the right half-space; Taremi's hold-up play and lay-off to a late-arriving Ghoddos from the #10 slot; deep cross from Rezaeian to Taremi at the near post. Iran is a **clinical** team — they create 5-6 chances per match and need to convert one. Taremi's shoot rating of 16 is the difference.

## Set Pieces
**Iran is one of the most dangerous set-piece teams in Asia.** Beiranvand's long throw is a weapon used 5-8 times per match. Khalilzadeh wins every header.
- Attacking corners: **Jahanbakhsh** in-swingers from the right, **Ghoddos** out-swingers from the left. Targets: Khalilzadeh (near post), Cheshmi (penalty spot), Taremi (back post), Nemati lurking at the far zone.
- Defending corners: heavy man-marking. Khalilzadeh on the most dangerous striker; Beiranvand attacks any cross within his reach.
- Free kicks: Jahanbakhsh direct from any angle within 28 yards; Taremi from central range.
- Long throws: **Beiranvand** sprints up from the goal to launch throws into the box on any throw-in inside the opposition half.
- Penalties: **Taremi** primary, **Jahanbakhsh** secondary.

## decide() Decision Priorities
1. **If my role == "GK" (index 0, Beiranvand, #1) and the team wins a throw-in inside the opposition half:** Sprint forward to within 35 units of the throw-in spot to launch a long throw into the box.
2. **If my player_id ends with "_10" (CF Taremi, #9) and team_phase == "attacking":** Drop into the #10 space between the opposition lines, 10-15 units behind the back line; turn and either dribble or Pass forward to the index-7 Ghaedi sprinting in behind, or lay off to the index-8 Ghoddos arriving centrally.
3. **If my player_id ends with "_10" (CF Taremi, #9) and the ball is within 25 units of goal:** Shoot if angle < 35°; shoot rating is 16, take the chance.
4. **If my role == "DEF" and team_phase == "defending":** Stay deep — back four holds a line 25 units off goal. Do not push higher unless ball is past the halfway line.
5. **If my player_id ends with "_5" (DM Ezatolahi, #6) and the opposition has the ball within 35 units of my goal:** Step to the ball-carrier, tackle if within 4 units, foul tactically if the opposition is breaking past me. The index-6 Cheshmi holds the screen behind.
6. **If team_phase == "transition_attack":** The index-7 Ghaedi (LW) and index-9 Jahanbakhsh (RW) sprint forward immediately; index-10 Taremi stays central; index-8 Ghoddos delivers the long diagonal or supports through the middle; the pivots (index-5 Ezatolahi, index-6 Cheshmi) hold.
7. **If my player_id ends with "_7" (LW Ghaedi, #10) and team_phase == "transition_attack":** Sprint into the channel beyond the opposition RB; receive the index-8 Ghoddos's diagonal.
8. **If my player_id ends with "_2" (LCB Khalilzadeh, #4) and a cross is incoming into my box:** Attack the ball aggressively — win the header. Strength 17.
9. **If team_phase == "defending" and the ball is wide:** Fullback + wide attacker on that side double-team the opposition wide attacker.
10. **If team is leading by 1+ goals after minute 70:** Drop into **5-4-1** with the index-4 Rezaeian becoming a third CB; recycle every set-piece by taking 30 seconds.
11. **If a defensive corner is incoming:** The index-2 Khalilzadeh marks the most dangerous opposition CF; the index-3 Nemati covers the penalty spot zone; the index-0 Beiranvand attacks the cross.
12. **Set-pieces 18-30 yards from goal:** Defer to the index-9 Jahanbakhsh (right-footed in-swingers) or the index-10 Taremi (central).

## Key Player Notes
- **Taremi (index 10, #9):** Talisman and lone striker, false-9-meets-#10. Drops between the lines to receive, turns, and either finishes or slips through-balls. The attack is built around him.
- **Jahanbakhsh (index 9, #7):** Captain, dead-ball specialist and right-sided creator. Cuts inside, shoots curlers. Wears the armband and leads from wide areas.
- **Khalilzadeh (index 2, #4):** The aerial monster. Wins every header in both boxes. Strength 17.
- **Ezatolahi (index 5, #6):** The destroyer and front half of the double pivot. Tactical fouler. Sets the team's defensive aggression baseline.
- **Cheshmi (index 6, #15):** The towering second pivot (strength 16) and a set-piece goal threat — remember his thunderbolt against Wales in 2022.
- **Ghoddos (index 8, #14):** The #10 and most technical midfielder; sprays the diagonals that launch the counters.
- **Beiranvand (index 0, #1):** The long-throw weapon. Iran scores 2-3 goals per tournament from his throws.

## Tournament Mindset
Iran arrives at every World Cup with a single defined goal: **escape the group stage**. They have come close (2018, 2022) and the 2026 squad is the strongest in a decade. The mentality is **defensive solidity first, set-pieces second, Taremi third**. They will defend a 0-0 against Argentina for 88 minutes and win it on a Beiranvand long throw. They will dominate Iraq and Jordan physically. They will be a nightmare matchup for any team that doesn't have an aerial CB pair. The weakness is creativity in open play against a well-organized opponent — when Taremi is well-marked and the long throw doesn't produce, Iran can go an entire half without a clean chance. Discipline is moderate (mostly 13-14) — expect 1-2 yellow cards per match, occasionally a red against a top opponent.
