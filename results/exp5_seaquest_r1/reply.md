**Design (summary)**

**Strategy**
- The submarine stays horizontally at the centre.
  - "Home-left" is cells 4–5, front at 4, facing left (C = Σ col·player = 9).
  - "Home-right" is cells 5–6, front at 6, facing right (C = 11).
  - This means orientation can be read from C alone.
- It moves only vertically. It tracks the lowest row that holds a target (fish, enemy sub or diver). Row 1 is ignored, so it never risks a sticky "up" into the surface.
- Fire is the default action, and the net turns toward targets in its own row. Divers are picked up as they swim through the centre column.
- It dodges vertically when danger is in its own row near the centre. It never moves into an adjacent row that has known danger, and it also waits when the danger there is uncertain.
- It surfaces when oxygen is below 60 (more urgently below 40) and at least one diver is aboard. The net reads this as oxygen-bar column 2 or 1 being off while diver-bar column 8 is on.

**Layer 1**
- **Unit 0, A:** a target exists in rows 2–8.
- **Geometric "highest row" detectors:**
  - How they work: row t gets weight 4^(t+1), and the submarine's row s sets the threshold through its channel-0 weights. Each unit therefore tests "some item exists in rows ≥ s+k" exactly, assuming at most 3 items per row.
  - Units 1, 2, 4, 5 cover targets: LS (left side, cols 0–3), RS (right side, cols 6–9), T0 (k = 0) and T1 (k = 1).
  - Units 3, 6, 7, 8 cover danger in the window cols 2–8, for k = 0, 1, −1 and 2.
- **Units 9–12, "lowest row" detectors:** the same idea with weights 4^(10−t), testing "danger exists in rows ≤ s+1, s, s−1, s−2".
  - Danger in row s±1 is known when that row is the highest or the lowest danger row.
  - If there is danger both beyond and on the near side of row s±1, its status is unknown, and the net treats that as a mild veto.
- **Units 13–15:** CR (C ≤ 8), CL (C ≥ 12) and OR (C ≥ 10, which means facing right).
- **Units 16 and 27:** surface-now signals for oxygen below 60 and below 40.
- **Units 17–18:** Z (row ≤ 2) and Z8 (row = 8).
- **Units 19–26, H_r:** the submarine is in row r and there is danger at cols 2–7, or an enemy bullet at col 8.

**Layer 2 and output**
- Layer 2 computes ANDs that act as votes or vetoes:
  - dodge up or down;
  - known and unknown danger above and below;
  - surface;
  - chase down or up;
  - turn left or right;
  - re-centre;
  - an "up" veto near the top.
- The output sums these votes. In priority order:
  1. Dodge
  2. Danger veto
  3. Re-centre
  4. Surface
  5. Chase
  6. Turn
  7. Fire (the default)

```edits
b1[0] = -2
W1[0:60:6, 1:5] = -7
W1[0:60:6, 5:7] = -7
W1[0:60:6, 7] = -7
W1[0:60:6, 8] = -31
W1[0:60:6, 9] = -131071
W1[0:60:6, 10] = -524287
W1[0:60:6, 11] = -524287
W1[0:60:6, 12] = -524287
W1[60:120:6, 1:5] = -7
W1[60:120:6, 5:7] = -31
W1[60:120:6, 7] = -7
W1[60:120:6, 8] = -127
W1[60:120:6, 9] = -32767
W1[60:120:6, 10] = -131071
W1[60:120:6, 11] = -524287
W1[60:120:6, 12] = -524287
W1[120:180:6, 1:5] = -31
W1[120:180:6, 5:7] = -127
W1[120:180:6, 7] = -7
W1[120:180:6, 8] = -511
W1[120:180:6, 9] = -8191
W1[120:180:6, 10] = -32767
W1[120:180:6, 11] = -131071
W1[120:180:6, 12] = -524287
W1[180:240:6, 1:5] = -127
W1[180:240:6, 5:7] = -511
W1[180:240:6, 7] = -31
W1[180:240:6, 8] = -2047
W1[180:240:6, 9] = -2047
W1[180:240:6, 10] = -8191
W1[180:240:6, 11] = -32767
W1[180:240:6, 12] = -131071
W1[240:300:6, 1:5] = -511
W1[240:300:6, 5:7] = -2047
W1[240:300:6, 7] = -127
W1[240:300:6, 8] = -8191
W1[240:300:6, 9] = -511
W1[240:300:6, 10] = -2047
W1[240:300:6, 11] = -8191
W1[240:300:6, 12] = -32767
W1[300:360:6, 1:5] = -2047
W1[300:360:6, 5:7] = -8191
W1[300:360:6, 7] = -511
W1[300:360:6, 8] = -32767
W1[300:360:6, 9] = -127
W1[300:360:6, 10] = -511
W1[300:360:6, 11] = -2047
W1[300:360:6, 12] = -8191
W1[360:420:6, 1:5] = -8191
W1[360:420:6, 5:7] = -32767
W1[360:420:6, 7] = -2047
W1[360:420:6, 8] = -131071
W1[360:420:6, 9] = -31
W1[360:420:6, 10] = -127
W1[360:420:6, 11] = -511
W1[360:420:6, 12] = -2047
W1[420:480:6, 1:5] = -32767
W1[420:480:6, 5:7] = -131071
W1[420:480:6, 7] = -8191
W1[420:480:6, 8] = -524287
W1[420:480:6, 9] = -7
W1[420:480:6, 10] = -31
W1[420:480:6, 11] = -127
W1[420:480:6, 12] = -511
W1[480:540:6, 1:5] = -131071
W1[480:540:6, 5:7] = -524287
W1[480:540:6, 7] = -32767
W1[480:540:6, 8] = -524287
W1[480:540:6, 9] = -7
W1[480:540:6, 10] = -7
W1[480:540:6, 11] = -31
W1[480:540:6, 12] = -127
W1[73:110:6, 3] = 16
W1[73:110:6, 6:9] = 16
W1[73:110:6, 9:13] = 262144
W1[133:170:6, 3] = 64
W1[133:170:6, 6:9] = 64
W1[133:170:6, 9:13] = 65536
W1[193:230:6, 3] = 256
W1[193:230:6, 6:9] = 256
W1[193:230:6, 9:13] = 16384
W1[253:290:6, 3] = 1024
W1[253:290:6, 6:9] = 1024
W1[253:290:6, 9:13] = 4096
W1[313:350:6, 3] = 4096
W1[313:350:6, 6:9] = 4096
W1[313:350:6, 9:13] = 1024
W1[373:410:6, 3] = 16384
W1[373:410:6, 6:9] = 16384
W1[373:410:6, 9:13] = 256
W1[433:470:6, 3] = 65536
W1[433:470:6, 6:9] = 65536
W1[433:470:6, 9:13] = 64
W1[493:530:6, 3] = 262144
W1[493:530:6, 6:9] = 262144
W1[493:530:6, 9:13] = 16
W1[122:180:6, 0] = 4
W1[122:180:6, 4:6] = 64
W1[122:144:6, 1] = 64
W1[158:180:6, 2] = 64
W1[182:240:6, 0] = 4
W1[182:240:6, 4:6] = 256
W1[182:204:6, 1] = 256
W1[218:240:6, 2] = 256
W1[242:300:6, 0] = 4
W1[242:300:6, 4:6] = 1024
W1[242:264:6, 1] = 1024
W1[278:300:6, 2] = 1024
W1[302:360:6, 0] = 4
W1[302:360:6, 4:6] = 4096
W1[302:324:6, 1] = 4096
W1[338:360:6, 2] = 4096
W1[362:420:6, 0] = 4
W1[362:420:6, 4:6] = 16384
W1[362:384:6, 1] = 16384
W1[398:420:6, 2] = 16384
W1[422:480:6, 0] = 4
W1[422:480:6, 4:6] = 65536
W1[422:444:6, 1] = 65536
W1[458:480:6, 2] = 65536
W1[482:540:6, 0] = 4
W1[482:540:6, 4:6] = 262144
W1[482:504:6, 1] = 262144
W1[518:540:6, 2] = 262144
W1[6:600:60, 13] = -4
W1[6:600:60, 14:16] = 4
W1[12:600:60, 13] = -8
W1[12:600:60, 14:16] = 8
W1[18:600:60, 13] = -12
W1[18:600:60, 14:16] = 12
W1[24:600:60, 13] = -16
W1[24:600:60, 14:16] = 16
W1[30:600:60, 13] = -20
W1[30:600:60, 14:16] = 20
W1[36:600:60, 13] = -24
W1[36:600:60, 14:16] = 24
W1[42:600:60, 13] = -28
W1[42:600:60, 14:16] = 28
W1[48:600:60, 13] = -32
W1[48:600:60, 14:16] = 32
W1[54:600:60, 13] = -36
W1[54:600:60, 14:16] = 36
b1[13] = 34
b1[14] = -46
b1[15] = -40
W1[593, 16] = 4
W1[557, 16] = -8
b1[16] = -2
W1[593, 27] = 4
W1[551, 27] = -8
b1[27] = -2
W1[0:180:6, 17] = 2
b1[17] = -2
W1[480:540:6, 18] = 2
b1[18] = -2
W1[60:120:6, 19] = 8
W1[73:104:6, 19] = 4
W1[109, 19] = 4
W1[110, 19] = -4
W1[120:180:6, 20] = 8
W1[133:164:6, 20] = 4
W1[169, 20] = 4
W1[170, 20] = -4
W1[180:240:6, 21] = 8
W1[193:224:6, 21] = 4
W1[229, 21] = 4
W1[230, 21] = -4
W1[240:300:6, 22] = 8
W1[253:284:6, 22] = 4
W1[289, 22] = 4
W1[290, 22] = -4
W1[300:360:6, 23] = 8
W1[313:344:6, 23] = 4
W1[349, 23] = 4
W1[350, 23] = -4
W1[360:420:6, 24] = 8
W1[373:404:6, 24] = 4
W1[409, 24] = 4
W1[410, 24] = -4
W1[420:480:6, 25] = 8
W1[433:464:6, 25] = 4
W1[469, 25] = 4
W1[470, 25] = -4
W1[480:540:6, 26] = 8
W1[493:524:6, 26] = 4
W1[529, 26] = 4
W1[530, 26] = -4
b1[19:27] = -18
W2[19:27, 0] = 2.5
W2[17, 0] = -2.5
b2[0] = 15
W2[19:27, 1] = 2.5
W2[18, 1] = -2.5
b2[1] = 15
W2[11, 2] = 3
W2[12, 2] = -3
b2[2] = -3
W2[7, 3] = 3
W2[3, 3] = -3
b2[3] = -3
W2[12, 4] = 3
W2[3, 4] = 3
b2[4] = -3
W2[6, 5] = 3
W2[8, 5] = -3
b2[5] = -3
W2[9, 6] = 3
W2[10, 6] = -3
b2[6] = -3
W2[8, 7] = 3
W2[10, 7] = 3
b2[7] = -3
W2[16, 8] = 3
W2[27, 9] = 3
W2[5, 10] = 3
W2[16, 10] = -3
b2[10] = -3
W2[0, 11] = 3
W2[4, 11] = -3
b2[11] = -3
W2[1, 12] = 3
W2[5, 12] = -3
W2[15, 12] = 3
b2[12] = -6
W2[2, 13] = 3
W2[1, 13] = -3
W2[5, 13] = -3
W2[15, 13] = -3
b2[13] = -9
W2[13, 14] = 3
W2[14, 15] = 3
W2[17, 16] = 3
W2[16, 16] = -3
b2[16] = -3
W3[0, 2] = 10
W3[1, 4] = 8.5
W3[2, 2] = -20
W3[3, 2] = -20
W3[4, 2] = -6
W3[5, 4] = -20
W3[6, 4] = -20
W3[7, 4] = -6
W3[8, 2] = 6.5
W3[9, 2] = 4.5
W3[10, 4] = 5.5
W3[11, 2] = 5.5
W3[12, 1] = 5
W3[13, 3] = 5
W3[14, 3] = 7
W3[15, 1] = 7
W3[16, 2] = -6
b3[0:6] = [0, 12, -25.5, 12, -32, 6]
```