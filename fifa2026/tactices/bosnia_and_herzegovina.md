# Bosnia and Herzegovina — Tactical Profile

## Identity & Philosophy
Bosnia and Herzegovina are a veteran-led, defensively organized team built around a disciplined block and set-piece danger. They qualified by grinding out results — limited possession, set-piece threat, and a willingness to absorb pressure for long periods. The identity is "veteran nous and direct attacking": they will not impose tempo, but they punish opponents who underestimate them. Under Sergej Barbarez they have leaned on experience throughout the group stage.

**Matchday 3 update (24 June, vs Qatar — Lumen Field, Seattle):** Bosnia sit on 1 point and MUST win to keep their round-of-16 hopes alive — and as heavy favourites (-245) against a Qatar side thrashed 6-0 by Canada, Barbarez goes more attacking. The big news: **captain Edin Džeko (40) is fit and STARTS** as the central reference, with Jovo Lukić dropping out. The shape shifts from the cautious 4-4-2 of earlier games to a more front-footed **4-3-3** to chase the win. Forced change at the back: **Tarik Muharemović is suspended** (red card vs Switzerland), so **Dennis Hadžikadunić** comes in at centre-back. In midfield a three of Tahirović, Šunjić and the young **Kerim Alajbegović** sits behind a front three of Demirović (left), Džeko (centre) and Memić (right). Esmir Bajraktarević is a high-impact option off the bench.

## Formation
- Shape: 4-3-3 (a more attacking setup for the must-win finale; reverts to a compact 4-5-1 / 4-1-4-1 mid-block when protecting a lead)
- Role mapping (roster order in `bosnia_and_herzegovina.yaml`):
  - index 0 (`bosnia_and_herzegovina_0`, Vasilj): GK — solid, traditional, distributes long when pressed.
  - index 1 (`bosnia_and_herzegovina_1`, Kolašinac): LB — veteran, physical, attacking instincts.
  - index 2 (`bosnia_and_herzegovina_2`, Hadžikadunić): LCB — physical deputy in for the suspended Muharemović; keep it simple, head clear.
  - index 3 (`bosnia_and_herzegovina_3`, Katić): RCB — pure stopper, dominant in the air, slow but very strong.
  - index 4 (`bosnia_and_herzegovina_4`, Dedić): RB — the team's main creative outlet, modern overlapping FB.
  - index 5 (`bosnia_and_herzegovina_5`, Tahirović): LCM — young technician, build-up brain, deep playmaker and set-piece deliverer.
  - index 6 (`bosnia_and_herzegovina_6`, Šunjić): DM — combative central screen, the destroyer who shields the back four.
  - index 7 (`bosnia_and_herzegovina_7`, Alajbegović): RCM — young, energetic box-to-box #8 who arrives late and carries forward.
  - index 8 (`bosnia_and_herzegovina_8`, Demirović): LW/inside-forward — mobile, hard-working, channel runner who combines with Džeko.
  - index 9 (`bosnia_and_herzegovina_9`, Džeko): CF — the captain and aerial reference point; hold-up, near-post finish, the team's spiritual leader.
  - index 10 (`bosnia_and_herzegovina_10`, Memić): RW — energetic wide runner who stretches the right and feeds Džeko's runs.

*Note: in midfield Tahirović (index 5) is the creative deep playmaker, Šunjić (index 6) is the defensive screen, and Alajbegović (index 7) is the runner. Out of possession the front three drop and the shape becomes a compact 4-5-1 / 4-1-4-1: Demirović and Memić tuck back to form a bank of five with the midfield three, while Džeko leads the line alone and screens the opposition pivot.*

## Style of Play

### Build-up
Slow, direct, with a long-ball Plan B. Vasilj plays to Hadžikadunić or Katić; Tahirović drops alongside the CBs forming a 3-build. If pressed, Vasilj goes LONG to Džeko (skill 16, strength 15 — he wins flick-ons even at 40) and the team chases the second ball. Tahirović is the creative outlet between the lines.

### Pressing (block height + trigger)
Selective. Bosnia do not press high for long stretches — they retreat to a compact 4-5-1 / 4-1-4-1 around the edge of their own half and force the opposition to break them down. BUT in this must-win game, with the lead or a draw insufficient, Demirović and Alajbegović step up earlier. Press triggers when opposition takes a heavy touch within 30m of Bosnia's goal AND Demirović or Alajbegović is within 8m.

### Defensive shape
Compact 4-1-4-1 — narrow, deep, disciplined. Šunjić screens in front of the back four; the front-three wide men (Demirović, Memić) drop to form a midfield bank of five with Tahirović and Alajbegović. Džeko pressures the opposition pivot up top. Distance between lines minimized (~8m). Force opposition wide; defend crosses with aerial CBs Hadžikadunić and Katić.

### Wide play
Creativity flows down the right: Dedić (RB) overlaps aggressively, the team's most reliable supply line, with Memić as the wide runner ahead of him. On the left, Demirović drifts inside off the shoulder of the last defender while Kolašinac provides the more conservative overlap behind. Crosses are aimed at Džeko's near-post run.

### Final third
Crosses to Džeko's near-post run; set pieces; Tahirović's through-balls when transitions open up. Demirović makes channel runs across the back line and combines with Džeko. Alajbegović arrives late from midfield. Memić's pace stretches the right.

## Set Pieces
- Corners: Tahirović delivers everything — inswingers toward Džeko (back post) and Katić (near post), outswingers toward Hadžikadunić.
- Direct free kicks: Tahirović from central/left; Alajbegović or Dedić from the right.
- Penalties: Džeko first (penalty 15, the captain takes the responsibility on his return); Demirović second; Tahirović third.

## decide() Decision Priorities
1. **Must-win posture:** Bosnia need the three points. When in possession in the opposition half, commit Dedić (`_4`), Memić (`_10`), Demirović (`_8`) and Alajbegović (`_7`) forward. Do not sit on a draw.
2. If my player_id ends with "_0" (GK, Vasilj): under press, KICK LONG toward "_9" (Džeko) — he wins the flick-on. Otherwise distribute short to a CB.
3. If my player_id ends with "_9" (CF, Džeko): position centrally between CBs; on the long ball, head/control DOWN to a runner ("_8" Demirović or "_5" Tahirović), then re-position for the cross to the near post. Primary penalty taker.
4. If my player_id ends with "_5" (LCM, Tahirović): receive between lines facing forward; if "_8" (Demirović) or "_10" (Memić) makes a back-line run, slip the through-ball. Primary set-piece deliverer.
5. If my player_id ends with "_6" (DM, Šunjić): pure screen — never cross halfway line in open play. Shadow the opposition #10; if they receive between Bosnia's lines, TACKLE immediately. Recycle laterally to either CB.
6. If my player_id ends with "_7" (RCM, Alajbegović): box-to-box — arrive late into the box on attacks, carry forward when space opens; track back to keep the midfield compact when possession is lost.
7. If my player_id ends with "_4" (RB, Dedić): overlap aggressively on the right — primary supply line; CROSS to Džeko's near post when wide within 35m of byline; recover quickly when possession is lost.
8. If my player_id ends with "_10" (RW, Memić): energetic wide runner ahead of Dedić; stretch the line, then combine on the right and feed Džeko; drop to the bank of five when defending.
9. If my player_id ends with "_8" (LW, Demirović): drift inside off the shoulder of the last defender; make channel runs across the back line every time Bosnia regains possession; combine with "_9" (Džeko) and do the pressing dirty work.
10. If my player_id ends with "_1" (LB, Kolašinac): more conservative — overlap to support "_8" (Demirović), but do not both push high at once with Dedić.
11. If my player_id ends with "_2" or "_3" (CBs, Hadžikadunić/Katić): on crosses, head clear long and high — never attempt a controlled clearance. Hadžikadunić (deputy) keeps it especially simple.
12. On opposition corner: 10 men in the box; "_8" (Demirović) stays high as the outlet.
13. Counter-attack rule: on regain in own third, FIRST PASS forward (to "_5" Tahirović or wide to "_4" Dedić / "_8" Demirović) — no backward recycling allowed in transitions.
14. Discipline: veterans ("_1" Kolašinac, "_9" Džeko) and any booked players avoid late challenges in the defensive third — Bosnia cannot afford a second suspension after losing Muharemović.

## Key Player Notes
- **Edin Džeko (index 9, captain):** the team's spiritual leader, fit and back in the XI at 40. His hold-up play and aerial reference still define everything — skill 16, shoot 16, penalty 15. Use him as the long-ball target, corner threat and primary penalty taker. Pace is gone (speed 9), so he plays as a static reference point, not a runner.
- **Ermedin Demirović (index 8):** the mobile foil — works the left channel, runs the back line and does the defensive dirty work so the target man can stay central. Shoot 14; secondary penalty taker.
- **Benjamin Tahirović (index 5):** the future. Highest-skill midfielder (15). License to roam between the lines as the team's creative outlet and deep playmaker; primary set-piece deliverer.
- **Kerim Alajbegović (index 7):** young, energetic box-to-box midfielder brought in to add running and forward thrust to the three; arrives late in the box and carries on the counter.
- **Amar Dedić (index 4):** Benfica right-back and the team's main creative supply line — modern overlapping fullback whose energy (stamina 16) drives the right flank.
- **Amar Memić (index 10):** pacey wide runner (speed 15) on the right; stretches the defence and feeds Džeko's near-post runs.
- **Dennis Hadžikadunić (index 2):** the enforced change — physical centre-back deputizing for the suspended Muharemović. Keep it simple: defend the box, head clear, do not get drawn out.
- **Nikola Katić (index 3):** dominant aerial stopper (strength 16) anchoring the back line alongside Hadžikadunić.
- **Esmir Bajraktarević (bench):** 21-year-old PSV winger and the team's spark — highest dribbling and speed in the squad. A game-changing option off the bench when Bosnia need to force the win; scored the winning playoff penalty vs Italy.

## Tournament Mindset
This is the knife-edge game. On 1 point and needing a win, Bosnia abandon the ultra-cautious approach of earlier matches for a more attacking 4-3-3 — but the DNA is unchanged: out-organize rather than out-play, stay compact, and strike from Džeko's head, Demirović's running, a Tahirović set piece, or an Alajbegović late arrival. Against a Qatar side smashed 6-0 by Canada, Bosnia are heavy favourites and know that anything less than three points likely ends their first-ever World Cup at the group stage. Discipline is doubly critical — with Muharemović already suspended, a second card could be fatal.
