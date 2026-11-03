# Hand-written Asterix policy: fixed column, vertical dodging

## Strategy
The player never moves left or right, so it stays in column 5, where it starts. Enemies and treasure move only horizontally, so the network only has to answer one question for each row r = 1…8: is something heading for column 5 in row r, and how soon?

Each step the network compares three choices: stay, move up, or move down. It scores each by the row the player would end up in:
- **Strongly avoid** rows where an enemy is approaching column 5. The penalty grows as the enemy gets closer.
- **Strongly prefer** rows where treasure is approaching. Such a row holds only that treasure, so it is safe and pays +1.
- **Pull toward treasure further away**, with a weaker attraction for rows 2–7 away.
- **Small penalties** for:
  - danger two rows ahead, because a sticky action may repeat the move;
  - entering the edge rows 1 and 8.
- **Small bonuses** for staying put and for leaving the edge rows.

Left, right and fire get very low logits, so they are never chosen.

## Hidden layer 1 (32 units)
- **D_r, units 0–7 (enemy danger in row r).** Each is a threshold unit over that row's enemy cells and trail cells. The trail is shared between enemies and treasure, but each row holds at most one entity. The weights were solved by hand so that:
  - enemy at column 5 gives about 3.5;
  - enemy approaching at distance 1, 2, 3, 4, 5 gives about 2, 0, −0.8, −1.8, −3;
  - an enemy moving away, a row with treasure, or an empty row gives −4 or less.
- **G_r, units 8–15 (treasure in row r).** Built the same way: treasure approaching or at column 5 gives about +3; treasure moving away, or no treasure, gives −3.75 or less.
- **P_r, units 16–23.** Indicates that the player is in row r.
- **X_r, units 24–31.** Indicates an enemy exactly at column 5 in row r, meaning certain death if the player enters that row.

## Hidden layer 2 (24 units used)
- There is one unit for each (player row p, action) pair, with actions stay, up and down.
- Each unit has a gate: weight 7 from P_p and bias −7. This holds the unit at −1 unless the player is in row p.
- When the gate is open, the unit is approximately tanh(½ × value of that move). The value combines the target row's danger, its treasure, X, the further-away treasure, the sticky-action risk and the biases.
- At row 1, "up" is identical to staying, and at row 8 "down" is identical to staying.

## Output
- The noop, up and down logits are each 25 × (the sum of that action's 8 units) + 175. This cancels the 7 inactive units, so each logit is about 25 × (the active unit's value).
- Left, right and fire have a fixed logit of −60.

```edits
# ===== Layer 1 =====
# D_r: units 0-7 (enemy ch1 + trail ch4); G_r: units 8-15 (gold ch2 + trail ch4); P_r: 16-23; X_r: 24-31
# row 1
W1[61:120:6, 0] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[64:120:6, 0] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[62:120:6, 8] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[64:120:6, 8] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[60:120:6, 16] = 12
W1[91, 24] = 10
# row 2
W1[121:180:6, 1] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[124:180:6, 1] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[122:180:6, 9] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[124:180:6, 9] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[120:180:6, 17] = 12
W1[151, 25] = 10
# row 3
W1[181:240:6, 2] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[184:240:6, 2] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[182:240:6, 10] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[184:240:6, 10] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[180:240:6, 18] = 12
W1[211, 26] = 10
# row 4
W1[241:300:6, 3] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[244:300:6, 3] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[242:300:6, 11] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[244:300:6, 11] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[240:300:6, 19] = 12
W1[271, 27] = 10
# row 5
W1[301:360:6, 4] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[304:360:6, 4] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[302:360:6, 12] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[304:360:6, 12] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[300:360:6, 20] = 12
W1[331, 28] = 10
# row 6
W1[361:420:6, 5] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[364:420:6, 5] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[362:420:6, 13] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[364:420:6, 13] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[360:420:6, 21] = 12
W1[391, 29] = 10
# row 7
W1[421:480:6, 6] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[424:480:6, 6] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[422:480:6, 14] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[424:480:6, 14] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[420:480:6, 22] = 12
W1[451, 30] = 10
# row 8
W1[481:540:6, 7] = [1, 2.2, 4.2, 6, 10, 13.5, 9, 6, 3.2, 2.2]
W1[484:540:6, 7] = [0, -1, -2, -4, -6, -10, -6, -3, -2, 0]
W1[482:540:6, 15] = [7.5, 7.5, 14.25, 14.25, 21, 21, 14.25, 14.25, 7.5, 7.5]
W1[484:540:6, 15] = [0, -6.75, -6.75, -13.5, -13.5, -20.25, -13.5, -6.75, -6.75, 0]
W1[480:540:6, 23] = 12
W1[511, 31] = 10
b1[0:8] = -4
b1[8:16] = -4.5
b1[16:24] = -6
b1[24:32] = -5

# ===== Layer 2 =====  stay units 0-7, up units 8-15, down units 16-23 (unit index = offset + p - 1)
# gates from P_p (h1 16+p-1) to stay/up/down units of row p
W2[16, 0:24:8] = 7
W2[17, 1:24:8] = 7
W2[18, 2:24:8] = 7
W2[19, 3:24:8] = 7
W2[20, 4:24:8] = 7
W2[21, 5:24:8] = 7
W2[22, 6:24:8] = 7
W2[23, 7:24:8] = 7
# stay: own-row danger and gold
W2[0, 0] = -0.6
W2[1, 1] = -0.6
W2[2, 2] = -0.6
W2[3, 3] = -0.6
W2[4, 4] = -0.6
W2[5, 5] = -0.6
W2[6, 6] = -0.6
W2[7, 7] = -0.6
W2[8, 0] = 0.2
W2[9, 1] = 0.2
W2[10, 2] = 0.2
W2[11, 3] = 0.2
W2[12, 4] = 0.2
W2[13, 5] = 0.2
W2[14, 6] = 0.2
W2[15, 7] = 0.2
b2[0:8] = -7.325
# up units (target row p-1; sticky risk row p-2; far gold rows above)
W2[0, 8] = -0.6
W2[8, 8] = 0.2
b2[8] = -7.325
W2[0, 9] = -0.6
W2[8, 9] = 0.2
W2[24, 9] = -0.25
b2[9] = -7.7
W2[0:2, 10] = [-0.075, -0.6]
W2[8:10, 10] = [0.1, 0.2]
W2[25, 10] = -0.25
b2[10] = -7.625
W2[1:3, 11] = [-0.075, -0.6]
W2[8:11, 11] = [0.07, 0.1, 0.2]
W2[26, 11] = -0.25
b2[11] = -7.555
W2[2:4, 12] = [-0.075, -0.6]
W2[8:12, 12] = [0.045, 0.07, 0.1, 0.2]
W2[27, 12] = -0.25
b2[12] = -7.51
W2[3:5, 13] = [-0.075, -0.6]
W2[8:13, 13] = [0.03, 0.045, 0.07, 0.1, 0.2]
W2[28, 13] = -0.25
b2[13] = -7.48
W2[4:6, 14] = [-0.075, -0.6]
W2[8:14, 14] = [0.02, 0.03, 0.045, 0.07, 0.1, 0.2]
W2[29, 14] = -0.25
b2[14] = -7.46
W2[5:7, 15] = [-0.075, -0.6]
W2[8:15, 15] = [0.02, 0.02, 0.03, 0.045, 0.07, 0.1, 0.2]
W2[30, 15] = -0.25
b2[15] = -7.315
# down units (target row p+1; sticky risk row p+2; far gold rows below)
W2[1:3, 16] = [-0.6, -0.075]
W2[9:16, 16] = [0.2, 0.1, 0.07, 0.045, 0.03, 0.02, 0.02]
W2[25, 16] = -0.25
b2[16] = -7.315
W2[2:4, 17] = [-0.6, -0.075]
W2[10:16, 17] = [0.2, 0.1, 0.07, 0.045, 0.03, 0.02]
W2[26, 17] = -0.25
b2[17] = -7.46
W2[3:5, 18] = [-0.6, -0.075]
W2[11:16, 18] = [0.2, 0.1, 0.07, 0.045, 0.03]
W2[27, 18] = -0.25
b2[18] = -7.48
W2[4:6, 19] = [-0.6, -0.075]
W2[12:16, 19] = [0.2, 0.1, 0.07, 0.045]
W2[28, 19] = -0.25
b2[19] = -7.51
W2[5:7, 20] = [-0.6, -0.075]
W2[13:16, 20] = [0.2, 0.1, 0.07]
W2[29, 20] = -0.25
b2[20] = -7.555
W2[6:8, 21] = [-0.6, -0.075]
W2[14:16, 21] = [0.2, 0.1]
W2[30, 21] = -0.25
b2[21] = -7.625
W2[7, 22] = -0.6
W2[15, 22] = 0.2
W2[31, 22] = -0.25
b2[22] = -7.7
W2[7, 23] = -0.6
W2[15, 23] = 0.2
b2[23] = -7.325

# ===== Output =====
W3[0:8, 0] = 25
W3[8:16, 2] = 25
W3[16:24, 4] = 25
b3[0:6] = [175, -60, 175, -60, 175, -60]
```