## Design

**Strategy.** The player never moves left or right, so it stays in its starting column 5 for the whole episode. Because every entity crosses its whole row, this is enough to play the game:
- **Dodging:** the player moves up or down to keep out of the way of enemies about to pass column 5.
- **Collecting gold:** the player stands in a gold's row when that gold passes column 5.
- **Safe rows:** each row holds at most one entity, so a row that contains gold has no enemy in it.

**Per-row features.** These are computed from enemy and trail cells near column 5.
- **Danger level D_r** (enemy weights over columns 2..8 and trail weights over columns 1..9; sums are exact integers):
  - **Near (N), sum 4:** an enemy at column 5, or an enemy one cell away and moving toward column 5. Moving into this row, or staying in it, can kill the player this step.
  - **Far (F), sum 2:** an enemy 2–3 cells away and moving toward column 5. It is a warning.
  - **None, sum ≤ 1:** an enemy moving away, or no enemy. A trail at column 5 gets −4, because only an entity that has already passed leaves a trail there.
- **Gold G_r:** gold at column 5, or gold 1–3 cells away and moving toward column 5. It uses graded weights; gold nearer the centre gets more weight, so a gold moving away never crosses the threshold.

**Layer 1 (29 units).**
- **D_r, r = 1..8 (8 units):** "D_r ∧ player in row r−1, r or r+1". The output is three-level: −1 for none, exactly 0 for F (the pre-activation is exactly 0), and +1 for N.
  - D_3 also fires whenever the player is in row 1, and D_6 whenever the player is in row 8. This marks "up" at the top and "down" at the bottom as blocked.
- **G_r (8 units):** "G_r ∧ player in row r−1, r or r+1".
- **G2_r (8 units):** "G_r ∧ player exactly 2 rows away".
- **Q_k (3 units):** the player's row mod 3.
- **TOP (1 unit):** player in rows 1–3.
- **BOT (1 unit):** player in rows 6–8.

**Mod-3 decoding.** The rows y−1, y and y+1 fall into three different classes mod 3. So when the player is in class k, the active D/G unit of class (k+δ) mod 3 means "the row at offset δ" (up, here or down). For G2, rows y−2 and y+2 also fall into different classes.

**Layer 2 (26 units).** Each unit is "(an active row-unit of class c) ∧ Q_k":
- 9 danger units, which keep the three levels: off, 0, on.
- 9 gold units.
- 6 two-rows-away gold units.
- 2 pass-through units for TOP and BOT.

**Output.** Each candidate move gets a score, and the logits are:
- up / no-op / down = −30·N − 15·F + 8·(gold adjacent or here) + 6·(gold two rows away) − 3 per move, plus 4.5 toward rows 4–5 when idle at the edges.
- left / right / fire are fixed at −80.

The resulting behaviour:
- The player leaves its row early when an enemy approaches, which gives several chances to escape even with sticky actions.
- It never steps into a row with a near enemy.
- It chases gold up to two rows away and waits in gold rows, which are safe.
- When nothing is happening, it drifts back to the middle rows.

```edits
# ---------------- Layer 1 ----------------
# D_r units 0..7 (row r = unit+1): enemy cols 2..8, trail cols 1..9
W1[73:110:6, 0] = [4, 4, 16, 16, 16, 4, 4]
W1[70:120:6, 0] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[133:170:6, 1] = [4, 4, 16, 16, 16, 4, 4]
W1[130:180:6, 1] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[193:230:6, 2] = [4, 4, 16, 16, 16, 4, 4]
W1[190:240:6, 2] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[253:290:6, 3] = [4, 4, 16, 16, 16, 4, 4]
W1[250:300:6, 3] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[313:350:6, 4] = [4, 4, 16, 16, 16, 4, 4]
W1[310:360:6, 4] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[373:410:6, 5] = [4, 4, 16, 16, 16, 4, 4]
W1[370:420:6, 5] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[433:470:6, 6] = [4, 4, 16, 16, 16, 4, 4]
W1[430:480:6, 6] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
W1[493:530:6, 7] = [4, 4, 16, 16, 16, 4, 4]
W1[490:540:6, 7] = [4, 4, 0, 0, -16, 0, 0, 4, 4]
# D gating (player in rows r-1..r+1)
W1[60:180:6, 0] = 16
W1[60:240:6, 1] = 16
W1[120:300:6, 2] = 16
W1[60:120:6, 2] = 48
W1[180:360:6, 3] = 16
W1[240:420:6, 4] = 16
W1[300:480:6, 5] = 16
W1[480:540:6, 5] = 48
W1[360:540:6, 6] = 16
W1[420:540:6, 7] = 16
b1[0:8] = -24
# G_r units 8..15 and G2_r units 16..23: gold cols 2..8, trail cols 1..9
W1[74:111:6, 8] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[70:120:6, 8] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[74:111:6, 16] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[70:120:6, 16] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[134:171:6, 9] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[130:180:6, 9] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[134:171:6, 17] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[130:180:6, 17] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[194:231:6, 10] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[190:240:6, 10] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[194:231:6, 18] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[190:240:6, 18] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[254:291:6, 11] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[250:300:6, 11] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[254:291:6, 19] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[250:300:6, 19] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[314:351:6, 12] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[310:360:6, 12] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[314:351:6, 20] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[310:360:6, 20] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[374:411:6, 13] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[370:420:6, 13] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[374:411:6, 21] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[370:420:6, 21] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[434:471:6, 14] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[430:480:6, 14] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[434:471:6, 22] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[430:480:6, 22] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[494:531:6, 15] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[490:540:6, 15] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
W1[494:531:6, 23] = [7.5, 12.5, 17.5, 50, 17.5, 12.5, 7.5]
W1[490:540:6, 23] = [21.25, 18.75, 12.5, 5, 0, 5, 12.5, 18.75, 21.25]
# G gating (player rows r-1..r+1)
W1[60:180:6, 8] = 50
W1[60:240:6, 9] = 50
W1[120:300:6, 10] = 50
W1[180:360:6, 11] = 50
W1[240:420:6, 12] = 50
W1[300:480:6, 13] = 50
W1[360:540:6, 14] = 50
W1[420:540:6, 15] = 50
# G2 gating (player rows r-2, r+2)
W1[180:240:6, 16] = 50
W1[240:300:6, 17] = 50
W1[60:120:6, 18] = 50
W1[300:360:6, 18] = 50
W1[120:180:6, 19] = 50
W1[360:420:6, 19] = 50
W1[180:240:6, 20] = 50
W1[420:480:6, 20] = 50
W1[240:300:6, 21] = 50
W1[480:540:6, 21] = 50
W1[300:360:6, 22] = 50
W1[360:420:6, 23] = 50
b1[8:24] = -75
# Q_k = player row mod 3 (units 24,25,26); TOP rows1-3 (27); BOT rows 6-8 (28)
W1[180:240:6, 24] = 8
W1[360:420:6, 24] = 8
W1[60:120:6, 25] = 8
W1[240:300:6, 25] = 8
W1[420:480:6, 25] = 8
W1[120:180:6, 26] = 8
W1[300:360:6, 26] = 8
W1[480:540:6, 26] = 8
W1[60:240:6, 27] = 8
W1[360:540:6, 28] = 8
b1[24:29] = -4

# ---------------- Layer 2 ----------------
# danger units 0..8: (k, up/here/down)
W2[1:8:3, 0] = 4
W2[24, 0] = 4
W2[2:6:3, 1] = 4
W2[24, 1] = 4
W2[0:7:3, 2] = 4
W2[24, 2] = 4
W2[2:6:3, 3] = 4
W2[25, 3] = 4
W2[0:7:3, 4] = 4
W2[25, 4] = 4
W2[1:8:3, 5] = 4
W2[25, 5] = 4
W2[0:7:3, 6] = 4
W2[26, 6] = 4
W2[1:8:3, 7] = 4
W2[26, 7] = 4
W2[2:6:3, 8] = 4
W2[26, 8] = 4
# gold units 9..17
W2[9:16:3, 9] = 4
W2[24, 9] = 4
W2[10:14:3, 10] = 4
W2[24, 10] = 4
W2[8:15:3, 11] = 4
W2[24, 11] = 4
W2[10:14:3, 12] = 4
W2[25, 12] = 4
W2[8:15:3, 13] = 4
W2[25, 13] = 4
W2[9:16:3, 14] = 4
W2[25, 14] = 4
W2[8:15:3, 15] = 4
W2[26, 15] = 4
W2[9:16:3, 16] = 4
W2[26, 16] = 4
W2[10:14:3, 17] = 4
W2[26, 17] = 4
# gold-two-rows units: 18..20 up, 21..23 down
W2[16:23:3, 18] = 4
W2[24, 18] = 4
W2[17:24:3, 19] = 4
W2[25, 19] = 4
W2[18:22:3, 20] = 4
W2[26, 20] = 4
W2[17:24:3, 21] = 4
W2[24, 21] = 4
W2[18:22:3, 22] = 4
W2[25, 22] = 4
W2[16:23:3, 23] = 4
W2[26, 23] = 4
# TOP / BOT pass-through
W2[27, 24] = 4
W2[28, 25] = 4
b2[0:24] = 4
b2[1] = 0
b2[3] = 0
b2[8] = 0
b2[10] = 0
b2[12] = 0
b2[17] = 0
b2[20] = 0
b2[22] = 0

# ---------------- Output ----------------
W3[0:7:3, 2] = -15
W3[1:8:3, 0] = -15
W3[2:9:3, 4] = -15
W3[9:16:3, 2] = 4
W3[10:17:3, 0] = 4
W3[11:18:3, 4] = 4
W3[18:21, 2] = 3
W3[21:24, 4] = 3
W3[24, 4] = 2.25
W3[25, 2] = 2.25
b3[0] = -33
b3[1] = -80
b3[2] = -24.75
b3[3] = -80
b3[4] = -24.75
b3[5] = -80
```