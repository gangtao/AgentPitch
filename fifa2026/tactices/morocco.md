# Morocco — Tactical Profile

## Identity & Philosophy
Mohamed Ouahbi's Morocco fuses modern positional play with the counter-attacking ferocity that carried them to the 2022 World Cup semi-final and the 2025 AFCON final. They defend in a compact 4-1-4-1 mid-block, then break vertically through Hakimi's overlap and the technical interplay of Brahim Díaz and Ounahi. The Atlas Lions are a tournament-tested side: disciplined, brave, and ruthless on the counter.

## Formation
- Shape: 4-3-3 in possession, morphing to 4-1-4-1 out of possession.
- Role mapping (roster index -> tactical role):
  - 0 Bounou — Sweeper-keeper, plays out from the back.
  - 1 Mazraoui — Left-back, inverts at times to form a back-three.
  - 2 Aguerd — Left center-back, primary build-up passer.
  - 3 Issa Diop — Right center-back, aerial enforcer.
  - 4 Hakimi — Right-back / wingback, overlapping bomber.
  - 5 Amrabat — Single pivot #6, ball-winner and screener.
  - 6 Ounahi — Left #8, box-to-box carrier.
  - 7 El Khannouss — Right #8, half-space progressor.
  - 8 Ezzalzouli — Left winger, direct dribbler hugging the touchline.
  - 9 El Kaabi — Center-forward, aerial target and poacher.
  - 10 Brahim Díaz — Right winger / free-roaming #10, primary creator.

## Style of Play

### Build-up
- Bounou splits the center-backs; Amrabat drops in to form a back-three when pressed.
- Aguerd is the preferred long-pass outlet — switches to Hakimi on the opposite flank.
- Full-backs asymmetric: Hakimi pushes very high, Mazraoui tucks inside.
- Brahim Díaz drops between the lines to receive on the half-turn.

### Pressing
- Trigger when the opposition center-back receives with a heavy first touch or back to play.
- El Kaabi presses the ball-side CB; nearest winger jumps the full-back; Ounahi/El Khannouss step onto the pivot.
- If the first press is bypassed, the team retreats immediately into the 4-1-4-1 mid-block — no chasing.

### Defensive shape
- 4-1-4-1 mid-block with a compact 18-meter vertical gap between lines.
- Amrabat shields the back four; the 8s screen the half-spaces.
- Center-backs hold the line; full-backs tuck in narrow when the ball is on the opposite flank.

### Wide play
- Right side: Hakimi overlap + Brahim inside = constant 2v1 overloads.
- Left side: Ezzalzouli holds width and attacks the byline, Mazraoui underlaps or inverts depending on the ball location.
- Crosses are mostly cut-backs from the byline, targeting El Kaabi's near-post run and Ounahi's late arrival.

### Final third
- Look for El Kaabi's near-post run on any cross from a full-back.
- Brahim Díaz takes 1v1s on the right; encouraged to drive inside onto his stronger foot.
- Late midfield runs from Ounahi and El Khannouss into the box.
- Recycle around the box rather than force low-percentage shots.

## Set Pieces
- Aguerd, Issa Diop, and El Kaabi are primary aerial targets — near-post flick + back-post arrival.
- Hakimi takes right-side corners; left-foot deliveries from Brahim on the other side.
- Defensive set pieces: zonal with Amrabat picking up the late runner.

## decide() Decision Priorities
1. If role == "GK" (player_id ends with "_0", Bounou) and ball is in own penalty area unpressed: short pass to nearest CB; otherwise long ball to the CF (player_id ends with "_9", El Kaabi).
2. If role == "DEF" and player_id ends with "_2" (Aguerd, LCB) and pressed by one striker: dribble-step forward; if pressed by two, pass to the pivot (player_id ends with "_5", Amrabat) dropping in.
3. If player_id ends with "_5" (Amrabat, #6 pivot): never shoot from outside 25m; prioritize simple lateral passes that switch play to the RB (player_id ends with "_4", Hakimi).
4. If player_id ends with "_4" (Hakimi, RB #2): when own team has possession in midfield, sprint to push past the halfway line and offer overlap.
5. If player_id ends with "_10" (Brahim Díaz, RW #10): receive between lines on the half-turn; if 1v1 and inside the half-space, dribble inside onto left foot.
6. If player_id ends with "_8" (Ezzalzouli, LW #17): hold width and attack the byline when the LB (player_id ends with "_1", Mazraoui) underlaps; tuck inside when Mazraoui overlaps.
7. If player_id ends with "_9" (El Kaabi, CF #20) and ball is wide near the byline: make a near-post run; if cross is cut back, attack the penalty spot.
8. If defending and ball-side opponent has the ball: maintain 4-1-4-1 distances, never break shape to dive in.
9. If turnover in opposition half: counter-press for 5 seconds; if not won, drop into mid-block.
10. If defending in own third: nearest #8 (player_id ends with "_6" Ounahi or "_7" El Khannouss) tracks the runner, the pivot (player_id ends with "_5", Amrabat) covers the central screen.
11. If trailing in the final 15 minutes: the RB (player_id ends with "_4", Hakimi) pushes onto the wing as a wingback, the LB (player_id ends with "_1", Mazraoui) drops into a back-three.
12. If leading by 1+ in the final 10 minutes: drop the block 5 meters deeper, prioritize ball circulation over progression.

## Key Player Notes
- **Hakimi** is the tactical fulcrum — virtually every attack should route through or past him. His stamina (18) sustains 90 minutes of overlap.
- **Brahim Díaz** is the creative engine; his 18 dribbling means he should attempt 1v1s liberally in the final third.
- **El Kaabi** is an old-school nine and proven poacher — feed him crosses, especially near-post deliveries. His shoot rating (17) is the team's highest non-Brahim ceiling.
- **Amrabat** rarely carries past the halfway line; his job is to win duels and recycle.
- **Bounou** is comfortable starting attacks with his feet — first option is always a short ball, second a long diagonal to Hakimi.

## Tournament Mindset
Patient against superior opponents, ruthless on the transition; Morocco believes any match can be won 1-0 on a Hakimi assist and a Bounou clean sheet.
