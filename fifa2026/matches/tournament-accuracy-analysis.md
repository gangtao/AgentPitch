# FIFA 2026 World Cup — Full-Tournament Simulation Accuracy Analysis

*How well did Agent Pitch's AI simulation predict the real 2026 World Cup — all 104 matches, group stage through the final?*

**Analysis date:** August 1, 2026 · **Scope:** All 104 matches (72 group-stage + 32 knockout, Days 1–35) · **Companion report:** [Group-stage deep dive](group-stage-accuracy-analysis.md)

---

## TL;DR

| Metric | Group stage (72) | Knockouts (32) | Tournament (104) |
|---|---|---|---|
| **Correct outcome** (W/D/L) | 34 (47.2%) | 22 (**68.8%**) | **56 (53.8%)** |
| **Exact scoreline** | 4 (5.6%) | 3 (9.4%) | 7 (6.7%) |
| Mean \|goal-difference error\| | 1.67 | 1.03 | 1.47 |
| Mean \|total-goals error\| | 1.86 | 1.66 | 1.80 |
| Sim goals/match vs real | 1.99 vs 2.99 | 2.38 vs 2.91 | 2.11 vs 2.96 |
| Advancing team called (knockouts) | — | **23 / 29 (79.3%)** | — |

**The headline: the machine called the World Cup.** The simulation picked **Spain 1–0 Argentina** for the final — and the real final finished **Spain 1–0 Argentina** (a.e.t., Ferran Torres 106'). It also went a perfect **4-for-4 in the quarter-finals**, which means it named the exact real semi-final quartet (Spain, France, England, Argentina), and it called England over France for third place. The engine's accuracy climbed steadily as the tournament sharpened: 47% correct outcomes in the group stage, 69% in the knockouts, 100% in the last four match-days' winners bar one (the England–Argentina semi).

Its systematic weakness never went away, though: **goal suppression**. Across 104 matches the sim scored 219 goals to reality's 308 — it under-shot the real total in 59 matches and over-shot in only 28 — and it produced just 5 matches decided by 3+ goals against reality's 22. The engine predicts *who*, increasingly well; it still can't predict *how much*.

At team level the spread is dramatic: the machine called **every one of Austria's four matches** correctly and 75% for three of the four real semi-finalists, but went **0-for-5 on Paraguay** — and its draw predictions landed only 31% of the time (§6–7).

---

## Methodology

- **Simulated results** are the published predictions in `fifa2026/matches/*-ai-prediction.md` and the Predicted column of [`index.html`](index.html) — the AgentPitch engine's output, one simulation per fixture, published before each real match day.
- **Real results** were backfilled from the [ESPN World Cup schedule](https://www.espn.com/soccer/schedule/_/league/fifa.world) and cross-verified with a second source per match day (group stage additionally verified against Wikipedia's per-group pages — see the [group-stage report](group-stage-accuracy-analysis.md)). The final and third-place results were confirmed via [ESPN](https://www.espn.com/soccer/match/_/gameId/760517/argentina-spain), [FIFA](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/spain-argentina-final-report-highlights), [Yahoo Sports](https://sports.yahoo.com/soccer/live/spain-argentina-world-cup-2026-score-result-schedule-live-updates-130000682.html) and [France 24](https://www.france24.com/en/sport/20260718-world-cup-2026-england-s-late-surge-ends-france-s-comeback-hopes-in-third-place-thriller).
- Because the simulation re-ran each **real** fixture day by day (it never propagated its own bracket), every one of the 104 matches has an exact 1:1 real counterpart.
- **Outcome** = sign of the printed goal difference (a shootout counts as a draw on the scoreboard). **Exact** = identical scoreline in the same orientation. Real scorelines include extra-time goals; early knockout sims (Days 18–20) played 90 minutes only, later ones simulated extra time and shootouts.
- **Advancing team called** (knockouts only) = the sim's predicted winner — by score or, for drawn sims, its simulated shootout — matches the team that really went through. The three 90-minute drawn sims of Days 19–20 (Brazil–Japan, Ivory Coast–Norway, Netherlands–Morocco) made no call and are excluded from that denominator.

---

## 1. The machine's championship run

The last five match days are the simulation's showcase:

| Stage | Fixture | Sim | Real | Verdict |
|---|---|---|---|---|
| QF | France v Morocco | 2–1 | 2–0 | ✅ winner |
| QF | Spain v Belgium | 2–1 (a.e.t.) | 2–1 | ✅✅ **exact scoreline** |
| QF | Argentina v Switzerland | 1–0 (a.e.t.) | 3–1 (a.e.t.) | ✅ winner |
| QF | Norway v England | 0–2 | 1–2 (a.e.t.) | ✅ winner |
| SF | France v Spain | 1–2 | 0–2 | ✅ winner |
| SF | England v Argentina | 0–0, England 3–1 pens | 1–2 Argentina | ❌ wrong finalist |
| 3rd | France v England | 1–3 | 4–6 | ✅ winner |
| **Final** | **Spain v Argentina** | **1–0** | **1–0 (a.e.t.)** | ✅✅ **champion + exact scoreline** |

Four-for-four in the quarters means the sim named the exact real semi-final four. It then split the semis — nailing Spain over France, but sending England through a shootout that Argentina really won in 90 minutes. Handed the real final anyway, it delivered its signature result: Spain 1–0, the same scoreline Ferran Torres produced in extra time at MetLife.

One honest caveat: the machine's Spain conviction wasn't unbroken. In the Round of 16 it had **Portugal 2–0 Spain** — it eliminated the eventual champion — and only re-boarded the Spain train when the real bracket handed it Spain–Belgium in the quarters. Day by day it got Spain right in three of the four rounds Spain played after the group stage.

---

## 2. Accuracy by stage

| Stage | n | Outcome | Exact | GD err | TG err | Sim g/m | Real g/m | Advancer called |
|---|---|---|---|---|---|---|---|---|
| Group stage | 72 | 34 (47%) | 4 | 1.67 | 1.86 | 1.99 | 2.99 | — (qualifiers: 25/32) |
| Round of 32 | 16 | 11 (69%) | 1 | 1.06 | 1.31 | 2.19 | 2.62 | 10/13 |
| Round of 16 | 8 | 4 (50%) | 0 | 1.38 | 2.12 | 3.00 | 2.88 | 6/8 |
| Quarter-finals | 4 | 4 (100%) | 1 | 0.75 | 1.25 | 2.25 | 3.00 | **4/4** |
| Semi-finals | 2 | 1 | 0 | 1.00 | 2.00 | 1.50 | 2.50 | 1/2 |
| Third place | 1 | 1 | 0 | 0.00 | 6.00 | 4.00 | 10.00 | 1/1 |
| Final | 1 | 1 | **1** | 0.00 | 0.00 | 1.00 | 1.00 | **1/1** |
| **Knockouts** | **32** | **22 (68.8%)** | **3** | **1.03** | **1.66** | **2.38** | **2.91** | **23/29 (79%)** |
| **Tournament** | **104** | **56 (53.8%)** | **7** | **1.47** | **1.80** | **2.11** | **2.96** | — |

Two clear patterns:

1. **Accuracy rose with the stakes.** Outcome accuracy jumped from 47% in the group stage to 69% in the knockouts, and the goal-difference error fell from 1.67 to 1.03. Part of this is structural — knockout fields are stronger and favourites clearer, and the group stage's 25/32 correctly-called qualifiers (78%) already showed the engine reads team strength better than single matches. Part is genuine improvement: mid-tournament engine work (extra-time/shootout support, strategy re-authoring each match day) tightened its match model.
2. **The Round of 16 was the knockout wobble.** 4/8 outcomes, 0 exact, and both of the sim's worst knockout misses (Portugal–Spain, USA–Belgium) — the only round where its goals/match *over-shot* reality.

The seven exact scorelines: South Africa 1–0 South Korea, Ecuador 0–0 Curaçao, Egypt 1–1 Iran, Cape Verde 0–0 Saudi Arabia (groups), Netherlands 1–1 Morocco (R32), Spain 2–1 Belgium (QF), and **Spain 1–0 Argentina (final)**.

---

## 3. Knockout rounds, match by match

Legend: ✅✅ exact scoreline · ✅ correct outcome · ❌ wrong outcome · **Adv** = advancing team called (– = no call: 90-minute drawn sim)

### Round of 32 (Days 18–23)

| Fixture | Sim | Real | Match | Adv |
|---|---|---|---|---|
| South Africa v Canada | 1–3 | 0–1 | ✅ | ✅ |
| Brazil v Japan | 1–1 | 2–1 | ❌ | – |
| Germany v Paraguay | 3–1 | 1–1, Paraguay pens | ❌ | ❌ |
| Netherlands v Morocco | 1–1 | 1–1, Morocco pens | ✅✅ | – |
| Ivory Coast v Norway | 1–1 | 1–2 | ❌ | – |
| France v Sweden | 2–0 | 3–0 | ✅ | ✅ |
| Mexico v Ecuador | 1–0 | 2–0 | ✅ | ✅ |
| England v DR Congo | 3–0 | 2–1 | ✅ | ✅ |
| Belgium v Senegal | 2–1 | 3–2 (a.e.t.) | ✅ | ✅ |
| United States v Bosnia & Herz. | 2–1 | 2–0 | ✅ | ✅ |
| Spain v Austria | 2–0 | 3–0 | ✅ | ✅ |
| Portugal v Croatia | 2–0 | 2–1 | ✅ | ✅ |
| Switzerland v Algeria | 1–2 (a.e.t.) | 2–0 | ❌ | ❌ |
| Australia v Egypt | 0–0, Egypt 3–2 pens | 1–1, Egypt 4–2 pens | ✅ | ✅ |
| Argentina v Cape Verde | 1–0 | 3–2 (a.e.t.) | ✅ | ✅ |
| Colombia v Ghana | 0–1 | 1–0 | ❌ | ❌ |

The Australia–Egypt call deserves a star: the sim predicted a goalless-style stalemate settled by an Egypt shootout win — reality delivered a 1–1 stalemate settled by an Egypt shootout win.

### Round of 16 (Days 24–27)

| Fixture | Sim | Real | Match | Adv |
|---|---|---|---|---|
| Canada v Morocco | 1–3 | 0–3 | ✅ | ✅ |
| Paraguay v France | 1–1, France pens | 0–1 | ❌ | ✅ |
| Brazil v Norway | 0–1 | 1–2 | ✅ | ✅ |
| Mexico v England | 0–2 | 2–3 | ✅ | ✅ |
| Portugal v Spain | 2–0 | 0–1 | ❌ | ❌ |
| USA v Belgium | 3–2 | 1–4 | ❌ | ❌ |
| Argentina v Egypt | 1–1, Argentina pens | 3–2 | ❌ | ✅ |
| Switzerland v Colombia | 3–3, Switzerland pens | 0–0, Switzerland 4–3 pens | ✅ | ✅ |

### Quarter-finals through the final (Days 29–35)

See the [championship-run table](#1-the-machines-championship-run) above — 7 of 8 winners called, two exact scorelines, one wrong finalist.

---

## 4. The one bias that wouldn't die: goal suppression

The group-stage report identified the engine's core flaw — it scores too few goals — and the full-tournament data confirms it as *the* dominant error source:

| Measure | Sim | Real |
|---|---|---|
| Total goals (104 matches) | 219 | 308 |
| Goals per match | 2.11 | 2.96 |
| Matches with 0–1 total goals | 41 | 23 |
| Matches with 4+ total goals | 18 | 36 |
| Matches with 5+ total goals | 7 | 22 |
| Highest-scoring match | 6 (Switzerland 3–3 Colombia) | 10 (France 4–6 England) |
| Winning margin of 3+ | 5 | 22 |
| Total under-predicted / over-predicted / equal | 59 / 28 / 17 | — |

The sim under-shot the real goal total in **59 of 104 matches** (57%) and produced less than a quarter as many 3+-goal margins as reality. Every real blowout got compressed: Germany 7–1 Curaçao became 2–0, Canada 6–0 Qatar became 1–0, Sweden 5–1 Tunisia became 0–0, and the 10-goal third-place thriller (France 4–6 England) became 1–3. The engine can identify the dominant side — in most of those cases it picked the right winner — but its physics/strategy stack (keeper strength, shot gating, defensive compactness) caps realistic scorelines near 2–1.

The encouraging trend: the gap narrowed as the tournament progressed and strategies were re-authored — group stage 1.99 sim vs 2.99 real (67% of real scoring), knockouts 2.38 vs 2.91 (82%). Real knockout games do also tend lower-scoring, but the sim's own output visibly rose after extra-time support and per-day strategy refreshes landed.

**Draw calibration is decent in volume, poor in placement.** The sim predicted 26 draws, reality produced 24 — but only 8 fixtures were drawn in *both* (precision ≈ 31%). The engine knows roughly how often football draws; it doesn't know which games.

---

## 5. Where the machine was wrong

The six wrong advancing-team calls, and what they share:

| Stage | Fixture | Sim said | Reality said |
|---|---|---|---|
| R32 | Germany v Paraguay | Germany 3–1 | Paraguay on pens |
| R32 | Switzerland v Algeria | Algeria (a.e.t.) | Switzerland 2–0 |
| R32 | Colombia v Ghana | Ghana 1–0 | Colombia 1–0 |
| R16 | Portugal v Spain | Portugal 2–0 | Spain 0–1 |
| R16 | USA v Belgium | USA 3–2 | Belgium 1–4 |
| SF | England v Argentina | England on pens | Argentina 2–1 |

Three threads run through them. **It overrated Germany, Portugal and the USA** — all three big-name sides the sim sent through were beaten, two of them soundly (this echoes its group-stage Group B disaster, where it ranked Switzerland last and Qatar second; reality inverted that). **It kept underrating Switzerland**, who it picked to lose to Algeria and only narrowly rated over Colombia, but who reached the real quarter-finals. And **it twice sold Argentina short in tight games** — predicting a scrape past Egypt on penalties (real: 3–2 in 90) and a semi-final exit to England (real: Argentina won 2–1) — before finally, correctly, having them lose the final by the odd goal.

Notably, half the wrong calls (Germany, Portugal, USA) came from backing a bigger name that reality knocked out — while the other half (Algeria over Switzerland, Ghana over Colombia, England over Argentina) were upsets the sim invented that never happened. The errors cut both ways, which is why the *scoreline* bias, not pick bias, remains the engine's most systematic flaw.

---

## 6. Team by team: who the machine read best — and worst

Scoring every team by how often the sim called its matches' outcomes correctly (48 teams, 3–8 matches each):

### Best-read teams (min. 4 matches)

| Team | Matches | Outcomes correct | Note |
|---|---|---|---|
| **Austria** | 4 | **4/4 (100%)** | Every result called, though reality was louder (6 real goals vs 2 simulated) |
| Morocco | 6 | 5/6 (83%) | The deep run to the quarters called almost step for step |
| Spain | 8 | 6/8 (75%) | Plus the tournament's only two knockout-exact scorelines (2–1 Belgium, 1–0 final) |
| France | 8 | 6/8 (75%) | Both misses were still France wins — just the wrong shape |
| England | 8 | 6/8 (75%) | Including third place; the semi-final call its only bad miss |
| South Africa, Senegal | 4 | 3/4 (75%) | |

It is no accident the list is top-heavy: **three of the four real semi-finalists sit at 75%** (Argentina, at 5/8 = 63%, is the exception — the sim kept under-calling their tight wins). The machine reads elite, possession-dominant teams best — their matches follow the script its engine writes.

### Worst-read teams

| Team | Matches | Outcomes correct | What the sim kept missing |
|---|---|---|---|
| **Paraguay** | 5 | **0/5 (0%)** | See below — a perfect record of being wrong |
| Japan | 4 | 1/4 (25%) | Beat Brazil in reality; the sim kept scripting draws |
| Ghana | 4 | 1/4 (25%) | The sim's most overrated attack (+1.0 g/m) — picked them over Colombia, who won |
| DR Congo | 4 | 1/4 (25%) | Reality's plucky over-achiever; sim saw a pushover |
| Bosnia & Herz. | 4 | 1/4 (25%) | Group B chaos — the sim's worst-read group |
| Switzerland | 6 | 2/6 (33%) | Ranked last in Group B by the sim; real group winners and quarter-finalists |

**Paraguay, the machine's blind spot.** Five matches, five wrong calls, and wrong in every direction: it gave them a draw against the USA (real: 1–4 loss), a draw with Türkiye (real: 1–0 win), a win over Australia (real: 0–0), a 3–1 elimination by Germany (real: Paraguay through on penalties), and a penalties-length fight with France (real: beaten 1–0 in 90). Gustavo Alfaro's counter-punching, low-block, shootout-hardened side is everything the engine's possession-flavoured model mishandles — the same profile (deep block, transitions, thin xG) that also produced the Japan and Switzerland misses.

---

## 7. Four more questions of the data

### Which attacks did the sim most underrate — and overrate?

Sim goals-for minus real goals-for, per match (min. 3 matches):

| Most underrated | Δ g/m | | Most overrated | Δ g/m |
|---|---|---|---|---|
| Netherlands | −1.75 (4 sim vs 11 real) | | Ghana | +1.00 (6 vs 2) |
| **Mexico** | −1.60 (2 vs 10) | | South Korea | +1.00 (5 vs 2) |
| Argentina | −1.25 (9 vs 19) | | Iraq | +0.67 (3 vs 1) |
| Croatia | −1.25 (1 vs 6) | | Portugal | +0.60 (11 vs 8) |
| Norway | −1.17 (6 vs 13) | | Algeria | +0.50 (7 vs 5) |

The Mexico row is the host-nation story in one number: El Tri scored ten real goals while the sim managed to give them two in five matches — it called three of their five results anyway, purely on defensive grit. And Argentina reached the real final scoring 19; the sim's Argentina scraped by on 9, which is exactly why it twice under-called them in tight knockouts.

### Which defenses did it misjudge?

The flattering errors all point one way — **the sim was far too kind to the minnows**, which is the blowout-compression bias wearing team colours: Qatar conceded 1 simulated goal vs 10 real, Tunisia 3 vs 12, Curaçao 3 vs 9, Uzbekistan 5 vs 11. In the other direction it was **too harsh on the tournament's two best real defenses**: Colombia (6 sim goals conceded vs 1 real in 5 matches) and champions Spain — who conceded exactly **one real goal in eight matches**, while the sim's Spain shipped four.

### What scoreline does the machine love too much?

| Scoreline | Sim | Real |
|---|---|---|
| **1–0** | **31** | 15 |
| 2–0 | 18 | 11 |
| 2–1 | 13 | 14 |
| 1–1 | 12 | 12 |
| 0–0 | 10 | 8 |
| 3–0 | 2 | 8 |
| 3–2 | 1 | 6 |

Nearly **30% of all the machine's predictions were 1–0** — double reality's rate. From 2–1 downward the two distributions track each other almost perfectly; everything above it (3–0, 3–2, 4–1, 4–2, 5+) is where reality lives and the sim doesn't. The engine doesn't have a wrong model of football so much as a truncated one: it predicts the front of the scoreline distribution and amputates the tail.

### How much should you trust each kind of prediction?

| When the sim said… | n | Outcome correct |
|---|---|---|
| "Team X by 2+ goals" | 33 | 64% |
| "Team X by 1" | 45 | 60% |
| "Draw" | 26 | **31%** |

And when it named a winner (78 matches): that team **won 62%**, **won or drew 82%**, and lost outright only **18%** of the time. The practical reading: the machine's *picks* are worth following — its confident picks slightly more so — but its *draws* are close to noise. A predicted draw mostly means "the engine couldn't separate them", not "these teams will share the points".

---

## 8. Conclusions

1. **As a bracket picker, the simulation earned its keep.** 78% of Round-of-32 qualifiers, 79% of knockout advancers, all four semi-finalists via a perfect quarter-final round, the correct third-place winner, the correct champion — with the exact final scoreline. If you had filled a bracket from the machine's picks, you'd have won most pools.
2. **As a scoreline predictor, it remains conservative to a fault.** 6.7% exact scorelines over 104 matches, driven almost entirely by the goal-suppression bias: 219 sim goals vs 308 real, 5 blowouts vs 22. Fixing scoring volume — keeper save rates, shot-gate thresholds, fatigue in stretched defenses — is the single highest-leverage engine change (tracked in the realism-gap issues).
3. **Accuracy compounded with iteration.** Every stage of the tournament, the sim's per-match accuracy improved — 47% → 69% outcomes, 1.67 → 1.03 GD error — as strategies were re-authored per match day and the engine gained extra-time/shootout support. The final's exact call wasn't luck arriving out of nowhere; it was the endpoint of a system getting measurably better for five weeks.
4. **Reputation still skews it — in both directions.** Half its wrong advancer calls backed a big name reality dumped out (Germany, Portugal, USA); it also chronically underrated Switzerland (picked to lose to Algeria; real quarter-finalists) all tournament — the same team it had ranked *last* in Group B while reality made them group winners. Auditing how team/tactics files translate reputation into player attributes would target both failure modes at once.
5. **It has a style-shaped blind spot, and a trust hierarchy.** The teams it read worst share one profile — deep-block counter-punchers who win ugly (Paraguay 0/5, Japan 1/4, Switzerland 2/6) — suggesting the engine under-models transition play relative to possession. And its outputs aren't equally trustworthy: a predicted winner avoided defeat 82% of the time, but a predicted draw came true just 31% — treat the sim's draws as "too close to call", not as forecasts.

---

*About this analysis: simulated results are Agent Pitch engine output published day-by-day during the tournament in `fifa2026/matches/` (every scoreline from simulation logs, never invented). Real results are sourced from the [ESPN World Cup schedule](https://www.espn.com/soccer/schedule/_/league/fifa.world) and [FIFA](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026), cross-verified per match day; group-stage methodology and per-group detail live in the [group-stage accuracy report](group-stage-accuracy-analysis.md). The two sources — machine prediction and real-world record — are never mixed.*
