# FIFA 2026 World Cup — Group-Stage Simulation Accuracy Analysis

*How well did Agent Pitch's AI simulation predict the real 2026 World Cup group stage?*

**Analysis date:** June 28, 2026 · **Scope:** All 72 group-stage matches (Matchdays 1–17, Groups A–L) · **Tracking:** [issue #77](https://github.com/gangtao/AgentPitch/issues/77)

---

## TL;DR

| Metric | Result |
|---|---|
| Matches compared | **72 / 72** (complete) |
| **Correct outcome** (W/D/L) | **34 / 72 = 47.2%** |
| **Exact scoreline** | **4 / 72 = 5.6%** |
| Mean goal-difference error | **1.67 goals** |
| Mean total-goals error | **1.86 goals** |
| **Knockout qualifiers called correctly** | **25 / 32 = 78%** |
| Group winners correct | **7 / 12** |
| Exact top-2 (both teams) correct | **2 / 12** |

**Headline finding:** the simulation is far better at picking *who advances* (78%) than at predicting *individual match outcomes* (47%), and it has one large, systematic bias — **it scores far too few goals**. The sim produced **1.99 goals/match vs. the real 2.99/match**, suppressing roughly a third of all scoring and flattening every blowout into a 1–0 or draw. That single bias drives most of the per-match errors.

---

## Methodology

- **Simulated results** were extracted from the Day 1–17 prediction blogs in `fifa2026/matches/*-ai-prediction.md` (the AgentPitch engine output; betting lines ignored).
- **Real results** were sourced from Wikipedia's per-group 2026 World Cup pages (cross-verified against NBC Sports standings and the MediaWiki raw wikitext; group stage confirmed complete as of June 27, 2026).
- Each of the 72 fixtures was matched by group + team pair. Outcome = sign of goal difference. "Exact" = identical scoreline in the same orientation. Goal-difference / total-goals error = absolute difference between sim and real.
- Final standings (and the 8 best third-placed qualifiers) were computed from scratch under FIFA tiebreakers (points → goal difference → goals for). The computed real qualifiers reproduce the official Round-of-32 field exactly, validating the standings logic.

Group compositions were identical between sim and reality (both follow the real draw), so every fixture has a 1:1 counterpart.

---

## 1. Accuracy metrics

### Overall (n = 72)

| Metric | Value |
|---|---|
| Correct outcome (W/D/L) | 34 (47.2%) |
| Exact scoreline | 4 (5.6%) |
| Mean \|goal-difference error\| | 1.67 |
| Mean \|total-goals error\| | 1.86 |
| Sim draws vs real draws | 18 vs 20 |
| **Sim goals/match vs real** | **1.99 vs 2.99** |

A 47% outcome hit-rate is only modestly better than naive baselines: betting-favourite models typically land ~50–55% on World Cup group games, and "always pick the higher-ranked side" would score similarly. The exact-scoreline rate (5.6%) is *below* the ~8–10% you'd expect from a decent Poisson model — a direct consequence of the goal-suppression bias.

The 4 exact hits are telling — **three of four were low-scoring/draws**: South Africa 1–0 South Korea (A), Ecuador 0–0 Curaçao (E), Egypt 1–1 Iran (G), Cape Verde 0–0 Saudi Arabia (H). The engine nails tight, cagey games and misses goal-fests.

### Per-group breakdown

| Group | Outcome | Exact | GD err | Total-goals err |
|---|---|---|---|---|
| A | 3/6 | 1/6 | 1.50 | 1.17 |
| B | **1/6** | 0/6 | 2.67 | 3.00 |
| C | 3/6 | 0/6 | 1.33 | 1.67 |
| D | 2/6 | 0/6 | 1.33 | 1.33 |
| E | 4/6 | 1/6 | 1.50 | 1.83 |
| F | 2/6 | 0/6 | 2.67 | 2.67 |
| G | 2/6 | 1/6 | 1.83 | 2.17 |
| H | 3/6 | 1/6 | 1.17 | 1.17 |
| I | 4/6 | 0/6 | 2.00 | 1.67 |
| J | **5/6** | 0/6 | 0.83 | 2.50 |
| K | 2/6 | 0/6 | 1.33 | 1.67 |
| L | 3/6 | 0/6 | 1.83 | 1.50 |

- **Best group: J (5/6 outcomes).** The sim read Argentina's dominance and the Algeria/Austria scrap for second almost perfectly — only the Argentina–Algeria opener (sim 3–3, real 3–0) broke.
- **Worst group: B (1/6).** A near-total miss: the sim ranked Switzerland *last* and Qatar *second*; reality inverted that almost exactly (Switzerland won the group, Qatar finished last with −8 GD). Groups B and F also carry the largest goal errors — both featured real blowouts (Canada 6–0 Qatar, Switzerland 4–1 Bosnia, Sweden 5–1 Tunisia, Netherlands 5–1 Sweden) that the engine compressed to one-goal margins.

---

## 2. Full match-by-match comparison

Legend: ✅✅ exact scoreline · ✅ correct outcome · ❌ wrong outcome

#### Group A
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Mexico v South Africa | 1–0 | 2–0 | ✅ outcome |
| South Korea v Czech Republic | 4–1 | 2–1 | ✅ outcome |
| Czech Republic v South Africa | 0–1 | 1–1 | ❌ |
| Mexico v South Korea | 0–1 | 1–0 | ❌ |
| Czech Republic v Mexico | 0–0 | 0–3 | ❌ |
| South Africa v South Korea | 1–0 | 1–0 | ✅✅ exact |

#### Group B
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Canada v Bosnia & Herz. | 3–1 | 1–1 | ❌ |
| Qatar v Switzerland | 1–0 | 1–1 | ❌ |
| Switzerland v Bosnia & Herz. | 0–1 | 4–1 | ❌ |
| Canada v Qatar | 1–0 | 6–0 | ✅ outcome |
| Switzerland v Canada | 0–0 | 2–1 | ❌ |
| Bosnia & Herz. v Qatar | 0–1 | 3–1 | ❌ |

#### Group C
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Brazil v Morocco | 1–0 | 1–1 | ❌ |
| Haiti v Scotland | 1–0 | 0–1 | ❌ |
| Scotland v Morocco | 1–2 | 0–1 | ✅ outcome |
| Brazil v Haiti | 2–0 | 3–0 | ✅ outcome |
| Scotland v Brazil | 1–1 | 0–3 | ❌ |
| Morocco v Haiti | 1–0 | 4–2 | ✅ outcome |

#### Group D
| Fixture | Sim | Real | Match |
|---|---|---|---|
| United States v Paraguay | 2–2 | 4–1 | ❌ |
| Australia v Turkey | 1–1 | 2–0 | ❌ |
| United States v Australia | 2–1 | 2–0 | ✅ outcome |
| Turkey v Paraguay | 0–0 | 0–1 | ❌ |
| Turkey v United States | 1–0 | 3–2 | ✅ outcome |
| Paraguay v Australia | 1–0 | 0–0 | ❌ |

#### Group E
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Germany v Curaçao | 2–0 | 7–1 | ✅ outcome |
| Ivory Coast v Ecuador | 1–1 | 1–0 | ❌ |
| Germany v Ivory Coast | 1–0 | 2–1 | ✅ outcome |
| Ecuador v Curaçao | 0–0 | 0–0 | ✅✅ exact |
| Curaçao v Ivory Coast | 0–1 | 0–2 | ✅ outcome |
| Ecuador v Germany | 1–3 | 2–1 | ❌ |

#### Group F
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Netherlands v Japan | 0–2 | 2–2 | ❌ |
| Sweden v Tunisia | 0–0 | 5–1 | ❌ |
| Netherlands v Sweden | 1–1 | 5–1 | ❌ |
| Tunisia v Japan | 2–1 | 0–4 | ❌ |
| Japan v Sweden | 2–2 | 1–1 | ✅ outcome |
| Tunisia v Netherlands | 1–2 | 1–3 | ✅ outcome |

#### Group G
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Belgium v Egypt | 4–1 | 1–1 | ❌ |
| Iran v New Zealand | 2–0 | 2–2 | ❌ |
| Belgium v Iran | 3–1 | 0–0 | ❌ |
| New Zealand v Egypt | 0–0 | 1–3 | ❌ |
| Egypt v Iran | 1–1 | 1–1 | ✅✅ exact |
| New Zealand v Belgium | 2–4 | 1–5 | ✅ outcome |

#### Group H
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Spain v Cape Verde | 1–0 | 0–0 | ❌ |
| Saudi Arabia v Uruguay | 0–2 | 1–1 | ❌ |
| Spain v Saudi Arabia | 2–0 | 4–0 | ✅ outcome |
| Uruguay v Cape Verde | 1–0 | 2–2 | ❌ |
| Cape Verde v Saudi Arabia | 0–0 | 0–0 | ✅✅ exact |
| Uruguay v Spain | 0–2 | 0–1 | ✅ outcome |

#### Group I
| Fixture | Sim | Real | Match |
|---|---|---|---|
| France v Senegal | 2–1 | 3–1 | ✅ outcome |
| Iraq v Norway | 1–3 | 1–4 | ✅ outcome |
| France v Iraq | 2–0 | 3–0 | ✅ outcome |
| Norway v Senegal | 0–2 | 3–2 | ❌ |
| Norway v France | 1–1 | 1–4 | ❌ |
| Senegal v Iraq | 4–2 | 5–0 | ✅ outcome |

#### Group J
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Argentina v Algeria | 3–3 | 3–0 | ❌ |
| Austria v Jordan | 1–0 | 3–1 | ✅ outcome |
| Argentina v Austria | 1–0 | 2–0 | ✅ outcome |
| Jordan v Algeria | 0–1 | 1–2 | ✅ outcome |
| Algeria v Austria | 1–1 | 3–3 | ✅ outcome |
| Jordan v Argentina | 0–2 | 1–3 | ✅ outcome |

#### Group K
| Fixture | Sim | Real | Match |
|---|---|---|---|
| Portugal v DR Congo | 2–1 | 1–1 | ❌ |
| Uzbekistan v Colombia | 0–1 | 1–3 | ✅ outcome |
| Portugal v Uzbekistan | 4–0 | 5–0 | ✅ outcome |
| Colombia v DR Congo | 0–1 | 1–0 | ❌ |
| Colombia v Portugal | 0–1 | 0–0 | ❌ |
| DR Congo v Uzbekistan | 0–0 | 3–1 | ❌ |

#### Group L
| Fixture | Sim | Real | Match |
|---|---|---|---|
| England v Croatia | 2–1 | 4–2 | ✅ outcome |
| Ghana v Panama | 3–0 | 1–0 | ✅ outcome |
| England v Ghana | 2–0 | 0–0 | ❌ |
| Panama v Croatia | 1–0 | 0–1 | ❌ |
| Panama v England | 0–1 | 0–2 | ✅ outcome |
| Croatia v Ghana | 0–2 | 2–1 | ❌ |

---

## 3. Qualification divergence — who advances

The simulation correctly identified **25 of the 32** Round-of-32 qualifiers (**78%**). It got the *easy* calls (every top seed advanced in both) but missed on the fine margins for second place and best-third spots.

### Teams the sim sent through that reality eliminated (7)

| Team | Sim finish | Real fate |
|---|---|---|
| Qatar | Sim 2nd, Grp B | Real **last** (1 pt, −8) |
| South Korea | Sim 1st, Grp A | Real 3rd, eliminated |
| Turkey | Sim 2nd (tie), Grp D | Real **last** |
| Uruguay | Sim 2nd, Grp H | Real 3rd, eliminated |
| Tunisia | Sim 3rd→R32, Grp F | Real **last** (0 pts, −10) |
| Iran | Sim 2nd, Grp G | Real 3rd, eliminated (lost best-third tiebreak to Senegal) |
| Haiti | Sim 3rd→R32, Grp C | Real **last** (0 pts) |

### Teams reality sent through that the sim eliminated (7)

| Team | Real finish | Sim had them |
|---|---|---|
| Switzerland | Real **1st**, Grp B | Sim **last** (1 pt) — biggest single miss |
| Australia | Real 2nd, Grp D | Sim last |
| Cape Verde | Real 2nd, Grp H | Sim 3rd, out |
| Ecuador | Real 3rd→R32, Grp E | Sim 3rd, out |
| Egypt | Real 2nd, Grp G | Sim 3rd, out |
| Sweden | Real 3rd→R32, Grp F | Sim **last** |
| Croatia | Real 2nd, Grp L | Sim **last** (0 pts) |

### Structural accuracy

- **Group winners:** 7/12 correct (C, E, G, H, I, J, L). Missed: A (sim S. Korea / real Mexico), B (sim Canada / real Switzerland), D (sim Paraguay / real USA), F (sim Japan / real Netherlands), K (sim Portugal / real Colombia).
- **Exact top-2 set:** only 2/12 groups had both qualifiers correct — the sim frequently got the *pair* of advancing teams right in aggregate but swapped their order or one slot.

The pattern: the sim is reliable on **dominant favourites** and **clear minnows**, but its compressed scorelines make the **2nd/3rd-place races** — which hinge on goal difference and the odd blowout — close to coin-flips.

---

## 4. Gap analysis — where the sim diverges, and why

### Gap #1 — Goal suppression (the dominant bias)

The engine scored **143 goals vs. the real 215** — it under-produces by **~33%**. Every real blowout was flattened:

| Real result | Sim said |
|---|---|
| Germany 7–1 Curaçao | 2–0 |
| Canada 6–0 Qatar | 1–0 |
| Sweden 5–1 Tunisia | 0–0 |
| Netherlands 5–1 Sweden | 1–1 |
| Portugal 5–0 Uzbekistan | 4–0 (closest blowout) |
| France 4–1 Norway | 1–1 |

**Why:** this is the engine-level realism gap tracked in **issue #30** and the **zero-shot dead zone** documented in **issue #71** — dominated teams release the ball before the shoot gate and stronger teams convert too few of their chances, so the model regresses hard toward 1–0 / 1–1 / 0–0. The fix shipped for #71 helped low-shot games but the *ceiling* on goals for dominant sides remains too low. **This bias alone explains the sub-par exact-scoreline rate and most of the goal-difference error, and it's why goal-difference-decided table positions (2nd/3rd place) are so often wrong.**

### Gap #2 — No real squad form, fitness, or motivation

The sim plays every team at a constant strength derived from squad attributes. It cannot model:
- **Switzerland's** real surge (the engine had no signal for their actual form),
- **Qatar / Tunisia / Haiti** collapsing under tournament pressure,
- dead-rubber rotation, injuries, suspensions, or must-win urgency.

These are exactly the teams whose real results most diverged from the sim.

### Gap #3 — Upsets compress toward draws

Where reality produced decisive shocks (Switzerland 4–1 Bosnia, USA 4–1 Paraguay, Morocco 4–2 Haiti), the sim hedged toward narrow wins or draws (18 sim draws is close to the real 20, but the sim's draws land on the *wrong* matches). The engine rarely commits to a lopsided result, so it leaves goal-difference points on the table that decide real standings.

### Gap #4 — Ranking knife-edges amplify small errors

Because the engine clusters scorelines, many groups finish with teams level on points, throwing the decision onto goal difference — precisely the quantity the sim measures worst. Group B (1/6) and the Iran-vs-Senegal best-third tiebreak are textbook cases.

---

## 5. Recommendations

1. **Raise the scoring ceiling for dominant sides** (highest priority). Re-tune the shot/finishing knobs so favourites convert closer to real xG; target ~2.8–3.0 goals/match in baseline calibration. Track against this analysis's 1.99 → 2.99 gap. (Extends #30 / #71.)
2. **Add a strength-gap-aware blowout path** so a clearly superior side can run up 4+ goals, instead of capping at 1–2. Validate that Germany-vs-Curaçao-type fixtures produce 4+ goal margins.
3. **Introduce per-matchday form/motivation modifiers** (or seed variance from real pre-tournament form) to break the constant-strength assumption that misses surgers like Switzerland and collapses like Qatar.
4. **Report goal-difference calibration as a standing metric** in every match-day report, since GD is what decides the knockout field — and is currently the engine's weakest output.
5. **Re-run this comparison after the knockout rounds** to see whether qualifier accuracy (78%) compounds or self-corrects deeper in the bracket.

---

## Appendix — data sources

- **Simulated:** `fifa2026/matches/*-ai-prediction.md` (Days 1–17), AgentPitch engine output.
- **Real:** Wikipedia *2026 FIFA World Cup* group pages A–L + knockout-stage page; cross-checked vs. NBC Sports standings and MediaWiki raw wikitext. Group stage confirmed complete (final June 27, 2026).
- Metrics computed in `/tmp/wc_analysis.py` (reproducible; standings logic validated by reproducing the official 32-team Round-of-32 field exactly).
