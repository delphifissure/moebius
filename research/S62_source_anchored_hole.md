# S62 — The per-line law dropped: a smooth hole from the source depth, in 2-D (2026-09-23, in progress)

## 1. Why (the user's verdict, and what it means)

- On the S59 review page the user found all three arms noisy: "huge chunk are look like lattice / grid in the depth.
  Not smooth." (S59 §4). Measured without opening the key, the lattice has two shared sources:
  - the per-line law's plate outside the tested hole, identical on every arm;
  - every arm anchored to the law's own values inside the hole.
- The user then withdrew both the law and the stopping rule: "drop per-line, and also the stopping law. This needs to
  work no matter what, everything else follows." And: "naturally I want smooth (disocclusions never look like
  scraggly lines)."
- S37 Phase C's rule is therefore withdrawn by the user (not satisfied, not failed). S59's key stays sealed; it no
  longer decides anything.

## 2. Why the project went per-line (checked in the notes, as the user asked)

1. **The hole's outline.** From the start, the app found what gets uncovered by warping the picture one scanline at a
   time over a 17×5 grid of eye positions (CODEMAP §5). The hole (`_qbDisocc`) is the union of those warps' uncovered
   cells, pulled back through the far field. Sprint 1 copied this into the measuring instrument (`reveal.py`, "per-scanline
   forward warp", S1 report) instead of questioning it. So the outline was streaky before any fill touched it.
2. **The fill (Sprint 3, S3 plan §2).** The membrane before it was anchored only at silhouette edges. On the synthetic
   truth kit it sagged under open floors and blended between different surfaces (a floor-to-wall ramp in front of
   the floor; sky where a hill was). Sprint 3 used an exact fact instead: a plane's disparity is affine along any image
   row or column. Continuing each line's own visible run reproduces the kit's planes exactly (precision 0.94–0.96).
3. **Why it failed on the pictures.** DA3 on paintings gives no exact planes. Each row fits its own run and
   neighbouring rows disagree: the comb (S33), the lattice (S59). Four sprints (S22, S32, S51, S58) patched the law
   instead of replacing it, because the kit kept preferring it. The kit is made of exact planes and cannot see noise
   between rows, so it was the wrong judge of cleanliness.

The lesson for what replaces it:
- Its judge is the user's screen and the picture's own smoothness, not the kit's exactness.
- The membrane's two real failures still have to be avoided: sagging where nothing anchors it, and blending across
  different surfaces.

## 3. The construction (`moebiusv2/harness/srcfill.py`)

It reads only the source depth, the picture and the app's constants. The band and far field are not read.

1. **Ramps.** The colour-guided ramp collapse (S61, the stronger version) turns DA3's blurred silhouettes into
   one-texel cliffs at the picture's own colour edge.
2. **Rims.** Every 4-neighbour pair, in rows and columns alike, is tested by the rim law's ratio on eye distance. A
   run of torn steps of one sign across an edge is one rim, from the run's top texel (the object) to its bottom
   texel (the background it reveals). The run's interior texels are the blur and join the hole.
3. **The hole.**
   - A rim's reach at the envelope's edge is the app's own shift difference between its two sides,
     R = s(near) − s(far), with s(d) = D·tan45·z/(D−z)·px/m (`bgShiftLUTFor`'s forward table). Vertically it is
     R·tan30/tan45 (the rectangular envelope).
   - The reach spreads only through the object:
     - each step must be joined by the rim law, with the tolerance scaled by the step's length for a diagonal;
     - each texel must stand in front of the background that rim reveals by more than two visible steps (S35 §47).
   - Same-depth pinholes join (S61 §10). No scanline is involved anywhere.
4. **Depth.**
   - A membrane on the hole, pinned at every neighbour outside it that lies behind the adjacent hole texel by more
     than two steps (the background), and free on the object side.
   - Not-behind texels are clamped to two steps behind and counted.
   - A component with no pin is flat at its farthest border depth, and counted.
5. **Wash.** The same membrane per RGB channel, with the same pins, each taking its own source colour.
6. **Outside the hole,** the plate is the source depth and the source colour.

Every constant is the visible step, the rim law's t, or the envelope (45°/30°).

## 4. Troll, first results (offline)

| construction | hole texels | pieces | steps over one visible step inside the hole |
|---|---|---|---|
| per-line band (S59, arms A/B/C) | 258 610 | 427 | 67 k – 163 k by arm |
| srcfill, rims on single steps, box reach | 181 198 | 37 | 26 913 |
| srcfill, reach through the object only | 281 723 | 5 | 38 177 |

- The shaded relief of the new plate shows no lattice (`troll_view.png` in the scratchpad).
- **Open 1: octagon patches.** Isolated tears whose reach spreads over a large joined surface make octagon-shaped
  patches.
- **Open 2: the ground.** The ground at the bottom tears against what is behind it, so a band of it enters the hole.
- **Open 3: the mesh.** The plate mesh's tear index is still the bake's, so it is counted as retear. The port
  rebuilds it.
- **Next:** frames in the app on the four pictures (`harness/srcfill.js`).
