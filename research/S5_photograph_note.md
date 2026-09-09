# The plane far side on a photograph (estimator depth, 8 bits, no truth)

Written 2026-09-09, the night after Sprints 3 and 4. First run of the plane far side
(`window._farRule='plane'`, rim law, first arrival, plate 2) on the app's default picture: the
troll, the woman and the cave, 851 × 1023, 8-bit depth from a monocular estimator, the app's
default volume (outer 0.02 m, inner 0.04 m, portal plane at 0.5). No truth exists for this image;
every finding below is from the buffers and the shots (a196), and nothing here changes a default.

## 1. Two ground rules found on the way (both on `main` already)

The kit's scenes have a ground run in every column; the photograph does not. The ground fit
(Theil–Sen plane over the lowest horizontal run per column) found a **12-column, 209-texel plane
at the water's edge** — the pool at the woman's feet — and, since the fitted plane bounds every
candidate below the horizon, it cut nine million candidates across the whole frame and emptied
every reveal (the woman's band went from 41 texels to nothing).

- **Rule (a): the ground bounds candidates only in columns that have a ground run of their own**
  (`groundCol[x]`). On the kit nothing changes (every column has one).
- **Rule (b): the fitted plane is the ground only if it explains a majority of the columns that
  offered a pick** (`nGroundIn·2 ≥ nGroundPicks`; on the photograph 10 of 435, so "no ground").
  Justification: the plane is a global hypothesis (one vanishing line for the whole frame, R3);
  a plane that a minority of columns support is a local surface — a puddle, a table — not the
  ground, and a local surface must not bound the world. Nothing is tuned: the majority is the
  natural threshold for "the frame's ground" against "a surface in the frame". The kit's scenes
  pass with every column.

After both rules the woman's central texels get the background behind her; her band is 41 texels,
the same as the rim arm's.

## 2. The holes right of the troll's head (poses 0.25 / 0.5) and above it (0 / 0.4)

Read from the buffers (`harness/shots/a257probe/photo_plane_v1`, the run before the fix) and the
per-layer shots (`sheet: scratch hide_crops.png` — all layers, plate 2 hidden, foreground hidden,
plates hidden, on magenta = nothing drawn):

- **They are holes, not black plates**: nothing is drawn there. The plates cover the right part of
  the reveal (the band texels near the silhouette) and miss the part next to the head — the texels
  deep inside the head that should carry the cave's depth are not in the band.
- **Cause 1 — a texel's own surface named as its far side.** The head's 8-bit depth is bumpy
  (row 340: 156 155 153 153 153 152 151 146 159 158 157 …/255); runs break on curvature, so one
  joined surface is several runs. A neighbouring run of the head that sits a hair behind
  (Δ just over the tolerance) counted as a candidate, and being adjacent (gap 1–4 texels) it
  arrived first (f0 = g/(kΔ) ≈ 0.07), so the far field was the head's own depth (kind 2, "same
  plane", value within one tolerance of own) — the reach walk, whose span is
  shift(edge) − shift(far field), stopped on it. Offline (`s3_dbg2.js`): texel (380, 340), own
  0.592, far side 0.579 = its own surface; the cave (0.06) is the second run to the right.
- **Cause 2 — a notch tears the head in two.** At x 381 the estimator's map dips 13 quanta for one
  texel (151 → 146 → 159). At this depth the rim law's t (1.0125) is ~9 quanta, so the pair
  146|159 is a rim, correctly: the map says the right half of the head is 6 mm nearer than the
  left half, which is a 75-texel relative slide at the envelope rim. The right half's texels then
  see the left half through the slit on one side and the cave on the other; the two lines do not
  meet inside the gap (kind 4), and the midpoint hedge put the nearer rim's line — the head's own
  depth — on them. Same effect: reach stops, cave not carried.
- **Not the cause**: plate depths one quantum below zero (7 558 texels with source depth < 1/255 sit
  at d − q = −0.0039 by the same-texel clamp behind the source; harmless, the shader clamps);
  plate 2 (no black colours; hiding it changes nothing); the fringe (see §4).

## 3. The two rule changes (commit `b81d4ce`, flag arm only)

- **A far-side candidate must lie beyond a rim.** In `cand`, runs are skipped until the walk along
  the line has crossed a not-joined pair (`rl.joinedIdx`, the same test the reach walk and the
  mesh tear use); only runs beyond it are candidates. This is the rim law's own definition of a
  surface applied to the plane law: inside one joined stretch the mesh is continuous and nothing
  is disoccluded, so nothing there can be a far side. No constant.
- **Kind 4 becomes two layers.** Two different surfaces on a texel's two sides whose lines do not
  meet inside the gap: the boundary between them is unknowable from one view. With one plate the
  texel went to the nearer rim's side (midpoint hedge, S3 report §1). With plate 2 it carries both
  — the farther as layer 1 (its depth gives the wider reach, so the band is the superset), the
  nearer as layer 2, which occludes the first wherever it really is there; the depth test sorts
  them and no depth is invented between the two. The side's own next arrival (S4's second layer)
  is dropped for kind 4 texels — a third layer would be needed; recorded, not built.

- **The reach walk no longer stops at a rim inside the occluder** (third change, after the first
  rerun). With the two rules above the band grew from 87 628 to 111 162 texels but rows 320–360
  through the face still ended at the notch: `walkP` broke at every not-joined pair, so the internal
  tear at x 381 stopped it, although the cave's reveal at half the envelope is 154 texels wide and
  the head's right half only 28 — the head's left half must carry the cave too. The reveal is
  geometric: every rest texel within the edge's slide against *its own* far side is uncovered,
  whatever tears lie between it and the edge. The walk now stops only where a texel has no far
  side of its own (nothing behind it to carry: `farField[i] == dQ[i]`) or where the span test
  fails (its far side is not behind the edge by more than the distance walked), which bounds
  every walk by the largest relative slide in the frame. The rim arm's walk (`walk`) is untouched.

Offline on the same buffers after the change: (380, 340) far 0.061 kind 2 (the cave, by the
column); (388, 340) far 0.051 kind 4 (the cave first, the head's left half second); (360, 340)
0.155; the synthetic unit test (`s3_unit.js`) unchanged, 0 bad texels. Whole-frame candidate
counts: texels with a far side 741 361 → 712 374; midpoint 14 203 (before: n/a in the same run —
the counts are from the offline evaluator on the v1 buffers).

## 4. What the photograph's depth looks like at a silhouette (for the record, no change made)

The head's right silhouette on row 340 is a 20-texel ramp (152 → 148 → 136 → … → 115 → 106) and
then a cliff (106 → 6). The ramp is a run of its own (15 texels, sloping away) and is treated as a
surface — the cheek curving away, which it may well be. At the cliff there is a two-texel sliver at
nearly the cave's depth (d ≈ 0.02): a mixed pixel of the estimator (R1 §2.3, "every ramp pixel is
a flying pixel"). As a thin run it continues at constant depth ≈ the cave's, so it is harmless here.
The kit's degradation ladder has blur rungs (σ 1, 2, 4 within 3σ of the exact rims) built for
exactly this; the plane arm has not been scored on them yet (rungs now built for S2 and S15;
`rung_chain.sh`). Shih et al. 2020's discontinuity-aware weighted median (five passes, windows
7, 7, 5, 5, 5 at a 960-px long side) is the published treatment; its window is in pixels, i.e. not
invariant to the image size, so it is not adopted without a measurement on the rungs.

## 5. Results after the change

(filled in below from the rerun: photograph band and shots; the eight kit scenes rerun to confirm
nothing moved.)
