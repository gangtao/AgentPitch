# Uzbekistan — Tactical Profile

## Identity & Philosophy
Uzbekistan, coached by **Timur Kapadze** (succeeding Srečko Katanec; Fabio Cannavaro briefly involved at federation level), are **first-time World Cup qualifiers** and the most physically modern Asian side outside Japan. The identity is **athletic, organized, pragmatic counter-attacking football** built around two genuine European-quality players — **Abdukodir Khusanov** (Manchester City CB) and **Abbosbek Fayzullaev** (CSKA Moscow AM) — supported by veteran striker Eldor Shomurodov. Uzbekistan's tactical model is closest to a **mid-table Eredivisie or Russian Premier League** side: compact mid-block, vertical counter-attacks, set-piece danger, and growing belief from a decade of producing genuine European-level prospects. Recent form: qualified second in their AFC third-round group behind UAE/Iran, ending a 16-attempt drought to reach a World Cup; the side has won 11 of its last 18 matches.

## Formation
- Shape: **4-2-3-1** in possession (drops to **4-4-1-1** out of possession, **4-5-1** against superior opposition).
- Role mapping (roster order in `uzbekistan.yaml`):
  - index 0: GK — **Utkir Yusupov** — traditional shot-stopper, less of a sweeper; commands his box with the back four sitting in front.
  - index 1: LCB or RCB — **Abdukodir Khusanov** — the star defender, Manchester City's CB signing (speed 16, skill 15, strength 16). The team's defensive anchor and ball-progressor — he carries the ball into midfield, wins every duel, and his speed (16) lets Uzbekistan hold a higher line than other AFC second-tier sides.
  - index 2: CB — **Rustam Khojimatov** — Khusanov's calmer partner, the aerial duel-winner.
  - index 3: CB — **Umar Eshmurodov** — third CB in rotation; covers when Khusanov steps forward.
  - index 4: LB or RB — **Sherzod Nasrullaev** — the most attacking of the back four; overlapping fullback, provides the natural width.
  - index 5: DM — **Otabek Shukurov** — the destroyer, the screen, the disciplined ball-winner.
  - index 6: DM — **Odiljon Hamrobekov** — Shukurov's box-to-box partner, the late-arriving runner, stamina 16.
  - index 7: LW or AM — **Jaloliddin Masharipov** — the veteran creator, dribbles inside, the team's secondary playmaker after Fayzullaev.
  - index 8: AM/RW — **Abbosbek Fayzullaev** — the star attacker, CSKA Moscow's #10. Skill 15, dribbling 15, pass 14. Drifts to the right half-space; the team's chief creator.
  - index 9: RW or AM — **Igor Sergeev** — pacy, direct attacker, shoot 14; the team's third forward in transitions.
  - index 10: CF — **Eldor Shomurodov** — captain, the lone 9, Roma/Spezia veteran, the team's leading scorer. Strength 14, shoot 14, hold-up player and channel-runner.

(Note: with three natural CBs in the roster, the engine may rotate Eshmurodov and Khojimatov as the regular CB pair while Khusanov shifts wide or remains the dominant central anchor; treat Khusanov as the on-pitch leader of the defensive third.)

## Style of Play

### Build-up
Pragmatic, hybrid short-and-long. Uzbekistan builds short from the back when uncontested — Khusanov's comfort on the ball (skill 15) makes him the chief progressor. When pressed, the team goes long to Shomurodov for a knock-down, with Fayzullaev and Masharipov gambling on the second ball. The first instinct is **find Fayzullaev between the lines** — he is the team's creative outlet. Uzbekistan is happy with 45-50% possession against equal opposition.

### Pressing
**Mid-block, athletic, trigger-based.** Uzbekistan drops to the halfway line and waits. Triggers: opposition GK takes a heavy touch, back-pass under duress, opposition midfielder receives on the half-turn. Shomurodov leads the front press; Fayzullaev and Masharipov jump from the wide positions; Shukurov is the central duel-winner. The press is hard-running but not constant — Uzbekistan conserves stamina (most of the squad rated 13-15) for the final third.

### Defensive shape
Compact **4-4-1-1** with Masharipov dropping to LM and Sergeev dropping to RM. Fayzullaev tucks alongside Shomurodov as a second forward in pressing situations, dropping into a midfield five against elite opposition. The back four sits 22-25 units off goal — but Khusanov's speed (16) allows the line to push higher than most AFC sides, which is a tactical advantage. Against top-eight opposition Uzbekistan drops to **4-5-1**.

### Wide play
**Asymmetric.** Right side: Fayzullaev drifts inside, Nasrullaev (or the right-back) overlaps for natural width. Left side: Masharipov dribbles inside, the left-back stays deeper as cover. Uzbekistan crosses from deep when crossing — Shomurodov attacks the near post. The wide play is functional, not the chief attacking pattern.

### Final third
Patterns: Fayzullaev drops between the lines, receives, dribbles, slips a through-ball to Shomurodov or Sergeev. Long ball to Shomurodov's chest, knock-down to Fayzullaev or Masharipov shooting from the edge of the box. Masharipov's cut-inside curler from the left half-space. Set-pieces from Fayzullaev's delivery to Khusanov's late run.

## Set Pieces
**Uzbekistan is a set-piece-dangerous side** with Khusanov's pace and height making him an aerial weapon in both boxes.
- Attacking corners: **Fayzullaev** in-swingers from the right (left foot), **Masharipov** out-swingers from the left. Targets: Khusanov (penalty spot, primary aerial), Shomurodov (near post flick-on), Khojimatov (back post).
- Defending corners: hybrid — Khusanov attacks the first ball; Khojimatov and Eshmurodov mark the two most dangerous opposition runners; four zonal markers; Yusupov stays on his line.
- Free kicks: **Fayzullaev** direct from any angle within 27 yards; Masharipov from the left half-space.
- Penalties: **Shomurodov** primary, **Fayzullaev** secondary, **Sergeev** tertiary.

## decide() Decision Priorities
1. **If my player_id ends with "_1" (CB Khusanov, #3) and team_phase == "attacking" and no opponent within 8 units:** Carry the ball forward into midfield — skill 15, speed 16. The most progressive CB in the AFC.
2. **If my player_id ends with "_1" (CB Khusanov, #3) and team_phase == "defending":** Step up to engage any forward within 7 units — speed 16 means I can recover even if I lose the duel.
3. **If my player_id ends with "_8" (AM Fayzullaev, #7) and team_phase == "attacking":** Drop into the #10 space between the opposition lines; receive on the half-turn; dribble forward.
4. **If my player_id ends with "_8" (AM Fayzullaev, #7) and I have the ball facing forward within 25 units of goal:** Shoot if angle opens, otherwise Pass to the index-10 Shomurodov or the index-9 Sergeev.
5. **If my role == "GK" (index 0, Utkir Yusupov, #1) and the team has a goal-kick under press:** Launch long to the index-10 Shomurodov.
6. **If team_phase == "defending" and the opposition is past midfield:** Drop into **4-4-1-1** at the halfway line; collapse to **4-5-1** if ball enters my final third.
7. **If my player_id ends with "_5" (DM Shukurov, #6) and the opposition is breaking past midfield:** Tactical foul within 4 units of the ball-carrier.
8. **If team_phase == "transition_attack":** Index-10 Shomurodov runs the channel; index-9 Sergeev sprints diagonally; index-8 Fayzullaev is the trailer; index-7 Masharipov is the secondary winger.
9. **If my player_id ends with "_10" (CF Shomurodov, #9) and a long ball is incoming:** Win the aerial duel; knock down to the index-8 Fayzullaev or the index-7 Masharipov.
10. **If team is trailing by 1 in the final 15 minutes:** Push the index-1 Khusanov forward as an emergency 9 for late set-pieces and crosses.
11. **If a defensive corner is incoming:** The index-1 Khusanov attacks the first ball; the index-3 Eshmurodov and index-2 Khojimatov mark the two most dangerous opposition runners; the index-10 Shomurodov stays on the halfway line as a counter-outlet.
12. **Set-pieces 20-28 yards from goal:** Defer dead-ball to the index-8 Fayzullaev (left-footed) or the index-7 Masharipov (left half-space).

## Key Player Notes
- **Khusanov (1):** The Man City CB. Speed 16, skill 15, strength 16. The defensive anchor AND the ball-progressor. Without him Uzbekistan is a mid-table AFC side; with him, they have a defender who would start for half the World Cup field.
- **Fayzullaev (8):** The CSKA Moscow #10. The chief creator. Dribbling 15, skill 15. Drifts between the lines.
- **Shomurodov (10):** The captain. The lone 9. Roma/Spezia veteran. Aerial. Hold-up. The team's leading scorer.
- **Masharipov (7):** The veteran creator. Left-sided dribbler. Set-piece deliverer.
- **Shukurov (5):** The destroyer. Tactical fouler. The screen.

## Tournament Mindset
Uzbekistan arrives at its first-ever World Cup with a mentality of **historic underdog with European-quality individuals**. The collective belief is high — they have already drawn with Iran, beaten the UAE, and qualified in style. The realistic ceiling is escaping the group if the draw is kind. The mentality is **organize, defend, trust Khusanov, trust Fayzullaev, take one chance per match**. They will frustrate any opponent with their compact 4-4-1-1 and Khusanov's pace covering a deep line. The vulnerability is **stamina depth** — many of the squad are rated 13-14 stamina, and the third match in eight days could see legs failing. Against a top-five side, Uzbekistan will likely lose 1-0 or 2-0; against a mid-tier side they have every chance of a draw or upset win.
