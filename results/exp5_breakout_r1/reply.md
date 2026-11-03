**Design**

The policy predicts where the paddle must be when the ball reaches row 8, moves the paddle into that window, and then waits.

**What layer 1 computes (8 units used)**

- **Units 0–3: comparators.** Each computes tanh(T − p), where p is the paddle column. T is a lookup table over the ball cell. It holds the centre of the catch window {Z, next x}, where Z is the ball's column when it reaches row 8.
  - Z is computed by unfolding the walls with period 20, which reproduces the one-step pause at a wall.
  - All T values are half-integers. So |T − p| = 0.5 means "already in the window" and |T − p| ≥ 1.5 means "move".
  - When the window is a single wall cell, T is set to −0.5 or 9.5.
  - There are four tables: descending/right, descending/left, ascending/right, ascending/left.
  - The ascending tables assume the ball bounces off the nearest possible brick (row 3 from below, the next row up when inside the brick area, or the ceiling from rows 0–1). If that brick is missing, the prediction shifts as the ball moves, and the paddle can still keep up.
- **Unit 4: paddle just hit the ball.** This is the state where ball and trail are both in row 8. The unit computes sign(bx + tx − 2p). It moves the paddle toward the trail cell if the bounce reversed the ball, or toward the ball if it did not. The wall cells are adjusted.
- **Unit 5:** the ball is ascending (vertical velocity = −1), computed linearly from ball row minus trail row.
- **Unit 6:** the paddle-hit state (ball and trail both in row 8).
- **Unit 7: horizontal direction.** It uses parity-adjusted column weights so the direction is ±1 even during the wall pause and at the start of an episode.

**What layer 2 computes (10 units used)**

Each unit is an AND gate: (regime active) AND (direction matches) AND (comparator says move right / move left).
- The descending regime is "not ascending and not the paddle-hit state".
- For the comparators, |tanh| > 0.68 means move. This separates tanh(1.5) = 0.905 from tanh(0.5) = 0.462.

**Output layer**

- The right and left logits are +12 when one of their gates is on, and −12 otherwise.
- The four no-op actions (no-op, up, down, fire) stay at logit 0, so the paddle waits when no gate is on.

```edits
# ---- L1 unit 0: descending, moving right: T = window centre ----
W1[3:600:6, 0] = [8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5, 7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5, 6.5,7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5, 5.5,6.5,7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5, 4.5,5.5,6.5,7.5,8.5,9.5,8.5,7.5,6.5,5.5,
  3.5,4.5,5.5,6.5,7.5,8.5,9.5,8.5,7.5,6.5, 2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,8.5,7.5, 1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,8.5, 0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5, 0,0,0,0,0,0,0,0,0,0]
# ---- L1 unit 1: descending, moving left ----
W1[3:600:6, 1] = [7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5, 6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5, 5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5,2.5, 4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5,2.5,3.5, 3.5,2.5,1.5,0.5,-0.5,0.5,1.5,2.5,3.5,4.5,
  2.5,1.5,0.5,-0.5,0.5,1.5,2.5,3.5,4.5,5.5, 1.5,0.5,-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5, 0.5,-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5, -0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5, 0,0,0,0,0,0,0,0,0,0]
# ---- L1 unit 2: ascending, moving right ----
W1[3:600:6, 2] = [9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5, 8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5, 7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5, 6.5,7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5, 5.5,6.5,7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,
  6.5,7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5, 7.5,8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5, 8.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5, 9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5, 0,0,0,0,0,0,0,0,0,0]
# ---- L1 unit 3: ascending, moving left ----
W1[3:600:6, 3] = [8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5, 9.5,8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5, 6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5, 5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5,2.5, 4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5,2.5,3.5,
  5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5,2.5, 6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5,1.5, 7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5,0.5, 8.5,7.5,6.5,5.5,4.5,3.5,2.5,1.5,0.5,-0.5, 0,0,0,0,0,0,0,0,0,0]
# paddle column (-p) for comparators 0..3
W1[540:600:6, 0] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 1] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 2] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 3] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
# ---- L1 unit 4: just-hit (row 8) rule: 4*(bx + tx - 2p) ----
W1[483:543:6, 4] = [2,4,8,12,16,20,24,28,32,34]
W1[484:544:6, 4] = [0,4,8,12,16,20,24,28,32,36]
W1[540:600:6, 4] = [0,-8,-16,-24,-32,-40,-48,-56,-64,-72]
# ---- L1 unit 5: ascending indicator, 6*(trail_row - ball_row) - 3 ----
W1[63:120:6, 5] = -6
W1[123:180:6, 5] = -12
W1[183:240:6, 5] = -18
W1[243:300:6, 5] = -24
W1[303:360:6, 5] = -30
W1[363:420:6, 5] = -36
W1[423:480:6, 5] = -42
W1[483:540:6, 5] = -48
W1[543:600:6, 5] = -54
W1[64:120:6, 5] = 6
W1[124:180:6, 5] = 12
W1[184:240:6, 5] = 18
W1[244:300:6, 5] = 24
W1[304:360:6, 5] = 30
W1[364:420:6, 5] = 36
W1[424:480:6, 5] = 42
W1[484:540:6, 5] = 48
W1[544:600:6, 5] = 54
b1[5] = -3
# ---- L1 unit 6: ball and trail both in row 8 ----
W1[483:543:6, 6] = 6
W1[484:544:6, 6] = 6
b1[6] = -9
# ---- L1 unit 7: horizontal direction (parity trick), +3 right / -3 left ----
W1[3:600:60, 7] = 1.5
W1[9:600:60, 7] = 1.5
W1[15:600:60, 7] = 7.5
W1[21:600:60, 7] = 7.5
W1[27:600:60, 7] = 13.5
W1[33:600:60, 7] = 13.5
W1[39:600:60, 7] = 19.5
W1[45:600:60, 7] = 19.5
W1[51:600:60, 7] = 25.5
W1[57:600:60, 7] = 25.5
W1[4:600:60, 7] = 1.5
W1[10:600:60, 7] = -4.5
W1[16:600:60, 7] = -4.5
W1[22:600:60, 7] = -10.5
W1[28:600:60, 7] = -10.5
W1[34:600:60, 7] = -16.5
W1[40:600:60, 7] = -16.5
W1[46:600:60, 7] = -22.5
W1[52:600:60, 7] = -22.5
W1[58:600:60, 7] = -28.5
# ---- L2: AND gates ----
# descending (not up, not just-hit), dir right
W2[0, 0] = 20
W2[0, 1] = -20
W2[1, 2] = 20
W2[1, 3] = -20
W2[5, 0:4] = -5
W2[6, 0:4] = -5
W2[7, 0:4] = [5, 5, -5, -5]
b2[0:4] = -28.6
# ascending
W2[2, 4] = 20
W2[2, 5] = -20
W2[3, 6] = 20
W2[3, 7] = -20
W2[5, 4:8] = 5
W2[7, 4:8] = [5, 5, -5, -5]
b2[4:8] = -23.6
# just-hit
W2[4, 8] = 5
W2[4, 9] = -5
W2[6, 8:10] = 5
b2[8:10] = -5
# ---- output: even L2 units -> right, odd -> left ----
W3[0:10:2, 3] = 12
W3[1:10:2, 1] = 12
b3[3] = 48
b3[1] = 48
```