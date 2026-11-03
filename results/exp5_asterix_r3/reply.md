# Hand-written policy for MinAtar Asterix: hold column 5 and dodge vertically

## Strategy

The player never moves left or right. Those logits, and fire, are fixed at −60. It stays in its starting column, x = 5, and only chooses between staying, moving up and moving down.

Every entity moves horizontally across the whole board, so each enemy and each treasure crosses column 5 exactly once. Each row holds at most one entity. This turns the game into a 1-D problem: dodge enemies by switching rows, and catch treasure by being in its row when it reaches column 5.

Column 5 is also far from the edges, so a newly spawned entity can never hit the player without warning.

## What the hidden units compute

**Layer 1: per-row features plus the player's row.** Units 19–31 are unused.

- **Units 0–7 (`R_r`): danger at cell (row r, column 5).** Each row has at most one entity, so the trail cell next to an enemy tells which way it is moving. A linear combination of enemy and trail inputs gives five tanh levels:

  | Situation | Output |
  |---|---|
  | Safe, or enemy moving away | −0.95 |
  | Enemy 3 cells away and approaching | −0.83 |
  | Enemy 2 cells away and approaching | −0.60 |
  | Enemy adjacent and approaching | 0 |
  | Enemy at column 5 | +0.95 |

- **Units 8–15 (`A_g`): treasure in row g that is approaching column 5 (or is at column 5).** The treasure weights fall off with distance from column 5, while the trail weights become less negative with distance. Together these give exactly 1 for approaching treasure and 0 for receding treasure, and enemies only produce negative values. A threshold then gives an output of about ±1.

- **Units 16–18: the player's row as 3 binary bits, ±1.**

**Layer 2: values gated by the player's row.** Units 22–31 are unused.

Each unit gets `8·(bits matching its row) − 24`. This turns it fully off (−1) unless the player is in that row, in which case it outputs tanh of a value:

- **`H2_r` (stay), units 0–7:** 0.4 − 1.6·danger(r) + 1.2·[treasure approaching in row r]. Rows 1 and 8 use a base of 0.1 instead of 0.4.
- **`U2_r` (up), units 8–14, r = 2..8:**
  - −1.0·danger(r−1), and −0.3·danger(r−2) as a look-ahead against the risk of a repeated (sticky) move.
  - Treasure pull of 1.2 if it is in the target row, 0.9 if two rows up, and 0.7 for each treasure further up.
  - −3 for leaving a row whose treasure is still approaching.
  - +0.25 extra from row 8, to push the player back toward the middle.
- **`D2_r` (down), units 15–21, r = 1..7:** the mirror image of `U2_r`.

**Output.** Each logit is 20 × the active unit of its group; the biases cancel the −1 from the units that are off.

Resulting behaviour:
- When nothing is happening, the player stays put.
- It moves away early once an enemy in its row is two cells away.
- It never steps into an adjacent enemy or an enemy at column 5.
- It goes after approaching treasure and waits in that row until it arrives.

```edits
# ===== Layer 1 =====
# Units 0..7: danger level at (row r, col 5), r=1..8
W1[73:110:6, 0] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[82:107:6, 0] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[92, 0] = 1.1
W1[133:170:6, 1] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[142:167:6, 1] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[152, 1] = 1.1
W1[193:230:6, 2] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[202:227:6, 2] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[212, 2] = 1.1
W1[253:290:6, 3] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[262:287:6, 3] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[272, 3] = 1.1
W1[313:350:6, 4] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[322:347:6, 4] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[332, 4] = 1.1
W1[373:410:6, 5] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[382:407:6, 5] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[392, 5] = 1.1
W1[433:470:6, 6] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[442:467:6, 6] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[452, 6] = 1.1
W1[493:530:6, 7] = [0.6, 1.1, 2.4, 4.7, 2.4, 1.1, 0.6]
W1[502:527:6, 7] = [-0.6, -1.1, -2.4, -1.1, -0.6]
W1[512, 7] = 1.1
b1[0:8] = -1.8
# Units 8..15: approaching treasure in row g=1..8
W1[62:120:6, 8] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[64:120:6, 8] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[122:180:6, 9] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[124:180:6, 9] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[182:240:6, 10] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[184:240:6, 10] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[242:300:6, 11] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[244:300:6, 11] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[302:360:6, 12] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[304:360:6, 12] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[362:420:6, 13] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[364:420:6, 13] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[422:480:6, 14] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[424:480:6, 14] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
W1[482:540:6, 15] = [6, 9, 12, 15, 18, 21, 18, 15, 12, 9]
W1[484:540:6, 15] = [-3, -6, -9, -12, -15, -18, -15, -12, -9, -6]
b1[8:16] = -3
# Units 16..18: binary code of player row (player at col 5, rows 1..8)
W1[90:511:60, 16] = [-4, 4, -4, 4, -4, 4, -4, 4]
W1[90:511:60, 17] = [-4, -4, 4, 4, -4, -4, 4, 4]
W1[90:511:60, 18] = [-4, -4, -4, -4, 4, 4, 4, 4]

# ===== Layer 2 =====
# Units 0..7: STAY value for player row r=1..8
W2[0, 0] = -1.6
W2[1, 1] = -1.6
W2[2, 2] = -1.6
W2[3, 3] = -1.6
W2[4, 4] = -1.6
W2[5, 5] = -1.6
W2[6, 6] = -1.6
W2[7, 7] = -1.6
W2[8, 0] = 0.6
W2[9, 1] = 0.6
W2[10, 2] = 0.6
W2[11, 3] = 0.6
W2[12, 4] = 0.6
W2[13, 5] = 0.6
W2[14, 6] = 0.6
W2[15, 7] = 0.6
W2[16, 0:8] = [-8, 8, -8, 8, -8, 8, -8, 8]
W2[17, 0:8] = [-8, -8, 8, 8, -8, -8, 8, 8]
W2[18, 0:8] = [-8, -8, -8, -8, 8, 8, 8, 8]
b2[0:8] = [-24.815, -24.515, -24.515, -24.515, -24.515, -24.515, -24.515, -24.815]
# Units 8..14: UP value for player row r=2..8
W2[0:16, 8] = [-1, 0, 0, 0, 0, 0, 0, 0, 0.6, -1.5, 0, 0, 0, 0, 0, 0]
W2[0:16, 9] = [-0.3, -1, 0, 0, 0, 0, 0, 0, 0.45, 0.6, -1.5, 0, 0, 0, 0, 0]
W2[0:16, 10] = [0, -0.3, -1, 0, 0, 0, 0, 0, 0.35, 0.45, 0.6, -1.5, 0, 0, 0, 0]
W2[0:16, 11] = [0, 0, -0.3, -1, 0, 0, 0, 0, 0.35, 0.35, 0.45, 0.6, -1.5, 0, 0, 0]
W2[0:16, 12] = [0, 0, 0, -0.3, -1, 0, 0, 0, 0.35, 0.35, 0.35, 0.45, 0.6, -1.5, 0, 0]
W2[0:16, 13] = [0, 0, 0, 0, -0.3, -1, 0, 0, 0.35, 0.35, 0.35, 0.35, 0.45, 0.6, -1.5, 0]
W2[0:16, 14] = [0, 0, 0, 0, 0, -0.3, -1, 0, 0.35, 0.35, 0.35, 0.35, 0.35, 0.45, 0.6, -1.5]
W2[16, 8:15] = [8, -8, 8, -8, 8, -8, 8]
W2[17, 8:15] = [-8, 8, 8, -8, -8, 8, 8]
W2[18, 8:15] = [-8, -8, -8, 8, 8, 8, 8]
b2[8:15] = [-25.847, -25.681, -25.331, -24.981, -24.631, -24.281, -23.681]
# Units 15..21: DOWN value for player row r=1..7
W2[0:16, 15] = [0, -1, -0.3, 0, 0, 0, 0, 0, -1.5, 0.6, 0.45, 0.35, 0.35, 0.35, 0.35, 0.35]
W2[0:16, 16] = [0, 0, -1, -0.3, 0, 0, 0, 0, 0, -1.5, 0.6, 0.45, 0.35, 0.35, 0.35, 0.35]
W2[0:16, 17] = [0, 0, 0, -1, -0.3, 0, 0, 0, 0, 0, -1.5, 0.6, 0.45, 0.35, 0.35, 0.35]
W2[0:16, 18] = [0, 0, 0, 0, -1, -0.3, 0, 0, 0, 0, 0, -1.5, 0.6, 0.45, 0.35, 0.35]
W2[0:16, 19] = [0, 0, 0, 0, 0, -1, -0.3, 0, 0, 0, 0, 0, -1.5, 0.6, 0.45, 0.35]
W2[0:16, 20] = [0, 0, 0, 0, 0, 0, -1, -0.3, 0, 0, 0, 0, 0, -1.5, 0.6, 0.45]
W2[0:16, 21] = [0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, -1.5, 0.6]
W2[16, 15:22] = [-8, 8, -8, 8, -8, 8, -8]
W2[17, 15:22] = [-8, -8, 8, 8, -8, -8, 8]
W2[18, 15:22] = [-8, -8, -8, -8, 8, 8, 8]
b2[15:22] = [-23.681, -24.281, -24.631, -24.981, -25.331, -25.681, -25.847]

# ===== Output =====
W3[0:8, 0] = 20
W3[8:15, 2] = 20
W3[15:22, 4] = 20
b3[0:6] = [140, -60, 120, -60, 120, -60]
```