# S32 — the frame edge with margin off, and the 2-D clamped plate as the far-field construction (2026-09-15)

The user's answer to S31 ("ok, try that") asked for two things: tear the frame edge under the fold rule now that the
margin strips are off, and put the 2-D clamped plate (S25 §4's offline construction) behind a select as the far-field
construction, with shots against the per-line law on the troll and vermeer. Both are built. The first needed a second
reading of what the streaks are; the second converges and changes a third of the band, and the instrument says it does
not remove the row structure the eye reads. Numbers below; nothing here changes a start-up default.

## 1. The frame-edge streaks: what they are

S31's edge probe (foreground alone clean, plate alone streaked) placed the streaks on the plate. The first reading of *which*
plate fragments — "the border cells, stretched across the gap the margin used to fill" — was wrong, and the first build of
the tear (`u_plateFold == 3`, fragments within 1.5 texels of the texture border) proved it: armed and logged on the troll at
the user's 26.5° pose, the frame differed from the untorn arm in 1 636 of 184 184 pixels and the streaks stood
(`troll_plate_edge/live_user26.png` against `troll_line/live_user26.png`).

The second reading, from the geometry: the plate mesh has one cell per texel (`MESH_DENSITY_FACTOR = 1`). Where two
adjacent rows of the picture's left edge differ in depth, every cell between those rows — in every column, not only the
first — is a ramp sheared sideways by the parallax difference of the two depths. Inside the picture footprint those ramps
are the skins the panel's "seams: stretched" choice keeps (they close holes). Past the picture's edge the same ramps spill
by their full shear into the letterbox bar beside a picture narrower than the window, over nothing. A one-row-deep edge
row has no unstretched cell at all — the whole streak is ramps. The border cell is one texel of a streak several hundred
pixels long; tearing it alone is invisible, which is what the measurement showed.

Under margin = picture the plate never reached the bars: A245 clips the plate to the picture's rest footprint in NDC
(`u_restClip`), with the argument "outside that footprint there is nothing to cover at any pose — the outpaint class is the
SD stage's". Turning the margin off (the user's word on the strips) also turned that clip off, because it lived inside
the margin block. That is the regression the user's sheets showed.

## 2. What is built

- **Default with margin off:** the plate keeps A245's clip to the picture's rest footprint (the same uniform, the same
  argument; set after the margin block, logged `[S32] margin off: plate clipped to the picture's rest footprint`). Plate
  colour and depth passes both honour it (the depth pass already did). Nothing changes inside the footprint.
- **Arm `window._edgeTear = 1`:** instead of the clip, the fold law outside the footprint: a plate fragment whose cell is
  stretched past 2 (A212's criterion, `u_fragTearFactor`) *and* whose clip-space position lies outside the rest footprint
  (`u_restFoot`, the same half-extents) is not drawn; inside, the panel's seam choice stands; coherent deep patches at the
  edge still show their true parallax into the bar. `u_plateFold == 3` in both passes.
- The texel-border test of the first build is removed (rule 7).

Trade for the screen (§5): the clip gives straight edges at every pose and hides true parallax at the picture's edge; the
tear shows that parallax as a wavy edge and may leave floating fragments in the bar.

## 3. The 2-D clamped plate in the app (`join: far field: 2-D plate`, `window._farPlate2D`)

Port of `research/s25/sheetfield4.py` MODE=plate into `bgFarSidePlane`, after the per-line law and before the disparity →
depth step, so every downstream stage (band, plate 2, colours, bundle) sees it as the far field:

- **Domain.** Each band texel with a far side takes, per side (the two rims of its axis), its rim's continuation run;
  texels whose rims belong to the same run cluster are one unknown set. Clusters = used rims joined when they lie in the
  same run along the connecting axis (union-find on the row/column run ids). Sky rims are excluded; thin-evidence rims
  (`b − a + 1 < g + 1`) and cut texels are skipped exactly as the per-line law skips them.
- **Data.** Each rim's fit window into the visible side (the Cauchy strip: the same samples the line law fits) is fixed
  at its raw disparity — the plate is pinned to the visible surface, not to the line law's extrapolation.
- **Energy.** Bending energy: second differences along x, along y and the two √2 diagonals over the cluster's domain ∪
  strip — the discrete thin plate (Duchon 1977; Terzopoulos 1986), the same rows as sheetfield4.
- **Obstacle.** The ground plane (`ground.at`) as a one-sided bound where the scene has one (S25 §4: the obstacle
  problem); 0 obstacle texels on the troll and vermeer (no ground plane in either).
- **Solver.** Preconditioned conjugate gradient (Jacobi) on the normal equations, started from the per-line field. The first
  port stopped on step size and under-converged (vermeer: 42 % of band texels moved by a median of one quantum, the row
  anisotropy 18.4 → 14.8 and the vertical jump fraction rose 30 % → 36 %). The rule now: stop when the preconditioned
  residual falls to 1e-12 of its start, capped at 400 + 40·√n iterations per cluster (n unknowns) — a cap in the units of
  the problem's own size, not a fixed count.
- **Recombination.** Per texel, the nearer of the two sides' plates behind the texel by more than the tolerance
  (sheetfield4 lines 306–326), then the per-texel reach / arrival order as before. Where a texel has no plate (no rim with
  a run), the per-line value stands.

Cost and convergence, from the app's own log (`window._geoPlate2D`):

| picture | clusters | solved | CG iterations (sum) | at the cap | obstacle texels | band texels changed | ms |
|---|---|---|---|---|---|---|---|
| troll (851×1023, DA3-16) | 1 869 | 1 869 | 467 783 | 97 | 0 | 259 589 | 53 120 |
| vermeer (DA3-16) | 1 612 | 1 612 | 557 541 | 215 | 0 | 258 266 | 79 980 |

## 4. Against the per-line law: does it remove the row structure?

`harness/plate_compare.py` over the band texels with a far side (the reference arm's set), depth in the app's normalised
disparity; row-to-row = |d| between vertically adjacent band texels (what the eye reads as streaks), along-row = between
horizontally adjacent ones; visible step 0.00176 (the S10 quantum on the troll).

| picture | band texels with a far side | far field changed | median / p90 \|change\| | row-to-row median \|d\| | along-row median \|d\| | anisotropy row/along | vertical band edges > visible step |
|---|---|---|---|---|---|---|---|
| troll | 258 943 | 84 239 (32.5 %) | 0.00340 / 0.02227 | 0.00048 → 0.00083 | 0.00019 → 0.00030 | 2.49 → 2.78 | 40.5 % → 43.9 % |
| vermeer | 370 698 | 181 170 (48.9 %) | 0.00263 / 0.04369 | 0.00044 → 0.00081 | 0.00002 → 0.00007 | 18.42 → 11.72 | 30.3 % → 38.8 % |

The rendered plate depth (`plateF`) moves with the far field (troll 2.49 → 2.79, vermeer 18.42 → 11.43). Split by whether the
plate solved both rows of a vertical band edge, one, or neither:

| picture | edges | both rows solved | one row solved | neither |
|---|---|---|---|---|
| troll | 245 217 | 69 094: median 0.00063 → 0.00120, > step 35.4 % → 43.9 % | 23 898: 0.02227 → 0.02512, 82.7 % → 93.8 % | 152 225: unchanged |
| vermeer | 365 707 | 155 988: 0.00042 → 0.00097, 19.0 % → 37.0 % | 46 128: 0.00552 → 0.00783, 69.7 % → 76.3 % | 163 591: unchanged |

Band rows touched: troll 984 rows partly, 0 fully, 39 not at all; vermeer 804 partly, 48 fully, 1 not at all. The crops
(`s32/vermeer_p45_line_vs_plate.png`, `s32/troll_p45_line_vs_plate.png`, per-line left, plate right, 2×) show the same
row structure in both arms; 4 027 of 39 200 and 3 451 of 40 800 crop pixels differ by more than 30/255.

Reading: the plate does not remove the row structure; on the instrument it adds to it. Where it solved *both* rows of a
vertical edge the row-to-row difference doubled and the share of visible jumps rose (vermeer 19 → 37 %). The reason is the
domain, not the solver: the clusters follow the run segmentation, which fragments row to row on real depth (1 869 and
1 612 clusters for about a thousand band rows each), so adjacent rows are mostly solved as separate plates, each anchored
on its own one-sided strip. A thin plate on a one-sided strip continues that strip's own trend (its bending-free extension,
the 2-D counterpart of the line law's affine carry); neighbouring strips have different trends, and where the per-line
law at least shared one fit window per axis, the plates diverge by their strips' 2-D shape. Only inside a cluster do rows
couple, and clusters are small. The anisotropy on vermeer falls (18 → 12) because the along-row differences rise (0.00002 →
0.00007), not because the row-to-row ones fall. This was the risk named when the port was queued (the "streak-free by
construction" claim was withdrawn before the run); the measurement settles it.

## 5. Kit truth

`kit_s7b3_chain.sh` with `_farPlate2D=1` (`check_app16plane_plate.json`, S15 `planesky`) against the per-line law under the
same chain (`_pl`, run after; and the stored `check_app16plane*.json` / `_s7b3` / `_c` files):

| scene | arm | precision | recall | band px | band depth err median (m) | p90 (m) | far field changed (band texels, median \|change\|) |
|---|---|---|---|---|---|---|---|
| S2 boxes | per-line | 0.887 | 0.999 | 18 531 | 0.0000 | 0.0427 | — |
| | plate | 0.887 | 0.999 | 18 524 | 0.0000 | 0.0427 | 37.3 %, 0.00000 |
| S16 steps | per-line | 0.190 | 0.972 | 23 078 | 0.0000 | 0.0000 | — |
| | plate | 0.192 | 0.972 | 22 867 | 0.0000 | 0.0000 | 17.8 %, 0.00000 |
| S26 quads | per-line | 0.457 | 0.937 | 52 608 | 0.0000 | 0.0560 | — |
| | plate | 0.457 | 0.937 | 52 602 | 0.0000 | 0.0560 | 16.9 %, 0.00003 |
| S15 sky | per-line | 0.723 | 0.996 | 48 020 | 0.184 | 8.566 | — |
| | plate | 0.723 | 0.996 | 48 017 | 0.157 | 8.566 | 33.2 %, 0.00002 |

On truth the port is what S25 §4 measured offline: the plate equals the plane law on planar continuations (the far field
moves on 17–37 % of band texels by a rounding-level median; precision, recall and depth error unchanged to the third
digit; S15's band-depth median falls 0.184 → 0.157 m under the same chain, the p90 — the sky reveals at 8.6 m — unchanged; the other three scenes' medians are 0 in both arms).
The arms diverged (a134) — by construction the plate cannot differ from a plane where the truth is a plane, so the kit
cannot rank them; the pictures had to, and did (§4).

## 6. What this means

1. **The frame-edge streaks were a regression of turning the margin off, not a new class of stretch.** A245's clip of the plate
   to the picture's rest footprint was tied to the margin block; restoring it independently of the margin removes the spill
   (troll 26.5°: 3 383 drawn pixels outside the footprint gone, 7 added; 45°: 1 229 gone; vermeer at 45°: 0 and 1 — its
   footprint spans the window's width, nothing spilled). The fold-law arm removes only the ramps stretched past 2 (634 and
   237 of those pixels); the rest of a streak is coherent deep rows displaced by their true parallax, which the fold law
   rightly keeps and the eye still reads as dashes (`s32/troll_user26_edge_three_arms.png`).
2. **The 2-D clamped plate per run cluster is falsified as a cure for the row structure** (rule 7). It is equal on truth and
   worse on the eye's instrument on both pictures. What would be different is not a better solver but a different domain:
   one plate per *surface*, with rims joined across rows by the join law — which is S22's "consistent far field across lines"
   reopened a third time (S16 and S22 closed the per-sheet thin-plate and the cross-line medians against truth and seams).
3. **Cost of the arm:** 53 s (troll) and 80 s (vermeer) per bake on this CPU, on top of the plane bake.
4. The arm is left behind the select in this push so the user can see it on their screen against the per-line law; by rule 7
   it should be removed next (the code stays in the history and in this note).

## 7. Trades for the next decisions

**Frame edge with margin off** (the screen decides; both built):
- *Clip to the rest footprint (default).* Advantages: straight picture edges at every pose; every spilled pixel gone; A245's
  argument already on record (outside the footprint there is nothing to cover). Disadvantages: hides the true parallax of deep
  content at the picture's edges (a deep row that should slide past the frame is cut at the frame line); the reveal *inside*
  the footprint at the far edge stays a hole (beyond-frame class, W4) either way.
- *Fold tear outside the footprint (`window._edgeTear = 1`).* Advantages: keeps what is geometrically true (coherent deep
  strips move past the frame). Disadvantages: the spill is only a fifth ramps; the rest reads as dashes; the edge is wavy.

**The far-field row structure** (what the per-line law leaves, 30–40 % of vertical band edges above the visible step):
- *Remove the plate arm and go to the diffusion loop (recommended).* Advantages: rule 7; the loop (W1) is the untested stage,
  and it is the only place where the cost of a depth ripple can be seen — the inpainter is conditioned on our depth, so a
  ripple becomes a painted ripple only if the model follows it at that scale (median row-to-row difference is 0.3 of the
  visible step; the > step edges are the ones that matter). Disadvantages: the ripples stay in the bundle's depth until
  something else is measured against them.
- *One plate per surface (cross-row cluster rule).* Advantages: the only form of the plate that couples rows. Disadvantages:
  the kit cannot rank it (planes), so it would be judged on pictures by the same instrument and the eye; S16/S22 closed two
  cross-line constructions already; about a day; the risk of a third equal-on-truth arm.
- *A model for the hidden depth (DepthLab-class, S26).* Advantages: no row structure by construction. Disadvantages: S26
  measured it below the plane law on continued surfaces; GPU.

## 8. Files

- App: `moebius.js` (`bgFarSidePlane` 2-D plate block, `_farPlate2D`; `u_plateFold == 3`, `u_restFoot`, the margin-off
  clip), `moebius.html` / `harness/scratch_moebius.html` (join select option `plate`), `harness/live_repro.js` (`JOIN`,
  `FLAGS`, `POSES`, `NOSHEET`, dumps), `harness/plate_compare.py`, `harness/edge_probe.js`.
- Shots: `harness/shots/liverepro/{troll_line,troll_plate_edge,troll_clip,troll_tear,vermeer_line,vermeer_plate2,vermeer_clip}/`;
  figures copied to `research/s32/`.
