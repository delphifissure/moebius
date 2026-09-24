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

1. **Ramps.** The colour-guided ramp collapse (S61, the safe version; the strong one striped faceted shapes, §4) turns
   DA3's blurred silhouettes into one-texel cliffs at the picture's own colour edge where it is sure.
2. **Rims.** Every 4-neighbour pair, in rows and columns alike, is tested by the rim law as the app has it: the
   ratio on eye distance, unless the pair continues the straight slope of the texels beside it. A run of torn steps of one sign across an edge is one rim, from the run's top texel (the object) to its bottom
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
   - Anchor points more than two steps from the consensus of a first solve with soft anchors are the blur's
     leftovers, and are dropped.
   - A hole texel whose fill is not behind its own source depth by two steps is not uncovered: it leaves the hole
     and the fill is solved again (clamping it copied the object's relief into the plate).
   - A component with no pin is flat at its farthest border depth, and counted.
5. **Wash.** The same membrane per RGB channel, with the same pins, each taking its own source colour.
6. **Outside the hole,** the plate is the source depth (after the safe collapse, as the app draws it) and the source
   colour.

Every constant is the visible step, the rim law's t, or the envelope (45°/30°).

## 4. Four pictures, in the app (2026-09-23, 18:30; app `53f526c`)

**How they were run.** Each picture was baked by the app with `ramps: safe`. Then the whole plate was replaced by
`srcfill.py`'s plate and wash (`harness/srcfill.js`) and shot at the S59 poses. The page shows them next to today's
app (S59 arm A): https://claude.ai/artifact/9bvULpNisSaMWba6bkpZoW.

**What changed on the way here** (each one found by looking at the result, and recorded here):
1. The first version grew the "ramp" beside the hole through any surface steeper than one step per texel. It ran up
   the ground and the trees for 345 texels. It was replaced by rims as whole runs of torn steps.
2. Envelope rectangles around each rim spilled onto neighbouring objects. The reach now spreads only through the
   object, across pairs the rim law joins.
3. Anchor points that were leftovers of the blur made small cone-shaped dimples. They are dropped by a first solve
   with soft anchors (two-step margin).
4. The ratio test alone tore every texel of a steep receding ground. The rim law's straight-slope join (the app's own)
   now applies in both axes.
5. Clamping not-behind texels copied the object's relief into the plate, which striped starwatcher's crystal
   mountain. Instead those texels leave the hole and the fill is solved again.
6. `ramps: strong` striped the crystal mountain in the foreground itself (v1's known misfire on faceted shapes,
   S61 §7). `ramps: safe` is used instead.

| picture | hole texels | pieces | anchors kept / dropped | left the hole (not behind) | kinks in the hole | fill (s) |
|---|---|---|---|---|---|---|
| troll | 192 432 | 19 | 2 036 / 1 197 | 26 260 | 278 | 132 |
| vermeer | 305 447 | 6 | 915 / 1 613 | 1 167 | 266 | 96 |
| sunflowers | 165 547 | 26 | 1 066 / 7 777 | 7 840 | 18 694 | 44 |
| starwatcher | 69 371 | 6 | 603 / 2 320 | 3 569 | 3 595 | 17 |

*Correction (same evening).* The sunflowers and starwatcher rows above were run with the wrong step. `srcfill.py`
read `meta.quantum`, which on those two 16-bit maps is the 16-bit grid (1/65 535), not the visible step
(2.68e-3, 2.57e-3). Every two-step test was about 170× too strict there, hence the dropped anchors and the kinks. Fixed
in app `b353e18`; §6 has the corrected numbers.

A kink is a second difference over one visible step: a comb or a spike makes one, a smooth slope does not. The
per-line arms' holes were measured in walls (S59), not kinks. For comparison, the new holes have 3 102 walls (troll)
and 11 867 (vermeer), against 67 k–163 k and 57 k–176 k for the per-line arms.

**Seen.**
- The shaded depth has no lattice on any picture. The figures are lifted out and the background continues smoothly
  behind them.
- In the troll frames, the areas uncovered next to the woman and the leg show a smooth wash with clean edges.

**Open, in order of visibility.**
1. **Starwatcher's ground.** The ground's top edge tears from the sky, because DA3 puts the far ground well in front
   of the sky. The reach then spreads down the ground in the envelope's rectangle shape, and the fill there is flat
   where the ground slopes. The result is a boxy plateau with straight edges.
2. **Foreground smears along soft edges.** Where DA3's blur is a straight slope, the rim law joins it (correctly for a
   real steep surface), so the foreground stretches. Telling blur from steep geometry is the ramp test's job. `safe`
   catches little (troll 1 562 texels); `strong` catches more (21 606) but stripes faceted shapes. This needs a better
   blur test.
3. **Octagon- and box-shaped outlines** where one isolated edge tears.
4. **The plate mesh's tears are still the bake's** (between 13 k and 61 k rim-law decisions per picture would change).
   The port rebuilds them.
5. **Speed.** The not-behind rounds re-solve up to 29 times (troll: 132 s). Rejecting anchors once instead of per
   round was tried: it was not faster (159 s against 96 s on the vermeer, with a render sharing the CPU) and it
   changed 105 k texels by up to 48 steps, so it was backed out.

## 5. The four open items, worked (user: "fix all the 'still open'")

1. **Hole outlines** (boxes, octagons, the ground's staircase).
   - The reach is now measured in the ellipse through the envelope rectangle's corners (x² + (y/env)² ≤ 2R²), with
     16 move directions (the 8 neighbours plus the knight moves), still only across pairs the rim law joins.
   - Outlines are smooth curves that follow the silhouette. The ellipse covers the rectangle, so nothing the envelope
     uncovers is left out; it over-covers the sides by up to √2, which only makes the hole a little larger.
   - An edge that tears at a single place with a long reach now makes a round lobe (troll, the trees on the left).
     That lobe is the region the envelope can uncover through that tear, seen one line at a time.
2. **Starwatcher's "ground".** At pitch +30° the frame shows what it is: the pink foreground dune's top edge hides
   the blue plain behind it. The flat fill under the dune's edge is that plain continued, so it is correct. What was
   visibly wrong there was item 3's smear along the dune's edge.
3. **Foreground smears along soft edges.** `srcfill.py` now collapses DA3's blurred occlusion edges itself, and the
   app bakes from that depth (`depthD16.png`, ramps off). The `safe`/`strong` ramp collapse is no longer used.
   - An edge is a run of torn steps (the rim law) extended through its blurry tails. A tail step is steep (more than
     the law's tolerance tolAt) and still curving: each step outward is smaller than the last by more than that
     tolerance.
   - The first cut took every steep step as tail. On starwatcher it ran down every column of the steeply receding
     dune and striped it (163 615 texels changed). The curving condition stops a tail at a straight slope, however
     steep. After it, 8 898 texels changed, all on occlusion outlines, with the mountain and the dune surface
     untouched.
   - The cut is at the centre of the colour change across the stretch, not its peak. The peak jumped a texel or two
     between neighbouring columns and left ticks along the dune's edge.
   - A stretch is found from its steepest step, with curving tails on both sides. It is taken if it holds a torn step,
     or if it continues a taken stretch of the same sign on the next line over (one contour). Before this, the soft
     left half of starwatcher's dune edge was sharpened only on the columns that happened to tear, and the
     alternation showed as a comb of teeth at pitch +30°. With contour continuity it is one clean band.
   - A faceted surface with no occlusion on its contour (the crystal mountain that `strong` striped) has nothing to
     start from, and is left as DA3 drew it.
4. **Plate mesh tears.** `srcfill.js` rebuilds the plate's triangle index from the new plate, on the source mesh's
   full grid, with the app's own rule (a quad across an edge the rim law does not join is not drawn, S2b.4). It
   replaces the bake's index, which had been torn on the per-line plate.

## 6. In the app (panel "hole depth: source", default off; app `9e4650a` → `c84bf1d`)

**What it does.**
- At depth load (after the effective quantum is known): `bgEdgeSharpen`, so the foreground tears at the same one-texel
  cliffs the hole starts from.
- After the bake: `bgSourceHole` + `bgApplySourceHole`.
  - The whole plate is replaced: depth, colour, and triangle index (rebuilt on the full grid with the rim law's own
    rule on the new plate).
  - Plate 2 (the per-line law's second layer) is hidden.
  - `_qbPlateF`, `_qbPlateColor` and `_qbDisocc` follow, so the SD bundle carries what is on screen. The bundle's
    placeholder classes are not yet rebuilt from the new hole.
- `bgMGSolve`: the multigrid-preconditioned CG lifted out of `bgPlainFill`. It takes several right-hand sides, warm
  starts, and flat-array coarsening. `bgPlainFill` through it is byte-identical to before (107/140 iterations, every
  texel).

**Checked against `srcfill.py`** (`harness/srchole_verify.js`, the app's own functions extracted).
- Starwatcher: edge sharpening identical, hole 2 of 86 640 texels different, plate 3 texels over one step (max 1.4).
- Troll: edge sharpening identical, hole 2 349 of 252 510 different. The not-behind rounds cascade and amplify
  tie-breaks. It is the same construction.

**The quantum trap, again.**
- The first live run on the clean 16-bit maps (sunflowers, starwatcher) sharpened 90 917 texels on starwatcher
  instead of 2 080.
- The cause: the app's effective quantum there is the 16-bit grid (S10: no noise, so the grid is the precision), and
  the port had borrowed the rim law's `tolAt`, which is 170× finer than a visible step.
- `bgRimLawAtStep` takes the ratio test and the straight-slope join with the tolerance at one visible step, as the
  construction is stated.
- The offline check had missed it because it stubbed the quantum to the visible step. `QEFF=grid` now reproduces the
  app's setting.

**Speed** (troll hole, in node).
- First port: 81 s, 39 rounds, every round re-solving the whole 250 k-texel hole while the later rounds dropped 1–2
  texels.
- Rounds solving depth only, warm-started, with the wash once at the end: about 2× faster.
- **Local rounds:** after a global round, only 33×33 boxes around the dropped texels are re-solved (the texels just
  outside held at the current fill), until nothing drops. Then a global round checks the whole hole again. Troll:
  **21 s** (7 global + 89 local rounds), and the hole is the same to 10 texels. Starwatcher: about 3–6 s.
- The rest of the bake (100–245 s headless under SwiftShader) is the per-line bake, which still runs underneath and
  whose plate is then replaced. Skipping it in source mode is the next and larger saving.

**The ink outline** (user: the wash "drawing color from the dark outline of the astronaut that somehow got burned into
the background").
- A colour pin sat right at the silhouette, where the painting has its ink line.
- A colour pin now takes the per-channel median of an 8-texel run of background texels stepping away from the hole.
  Eight is over twice the widest ink line measured (about 3 texels on starwatcher), so the line is outvoted.
- The run stops at the frame edge, or at anything nearer than the pin by two steps. A thin strip of background between
  fine lines uses what it has, as the user noted there is no other option there.
- Depth pins are unchanged.

**The ink line itself joins the object** (app `cc16884`, `bgInkAdopt`, run after `bgEdgeSharpen` at depth load).
- With the pins fixed, the wash was light blue, but a faint dark trace of the astronaut stayed in the sky at every
  pose. The ink texels have the background's depth (DA3's edge lies inside the line), so they are background: they
  stay put when the figure moves, and they are not in the hole.
- The line is the figure's own outline, so it should move with the figure. At every torn step the rule walks 8 texels
  into the background. If it meets the frame edge or another torn step first, the run is left alone.
- The outer 4 texels are the background's own colour: the CIELAB median and the robust spread (1.4826 × the median
  distance).
- The leading texels that differ from that by more than 3 spreads, and by more than one just-noticeable difference
  (ΔE\*ab 2.3), take the object's depth, up to the first texel that matches. At most 4, so the background always
  outvotes the line.
- They are then part of the object. The hole's reach starts past them, so the wash covers where they were.

| picture | rims checked | rims with a line | texels adopted | hole before → after |
|---|---|---|---|---|
| starwatcher | 3 153 | 2 484 | 4 316 | 86 647 → 89 316 |
| troll | 3 999 | 2 246 | 4 241 | 252 207 → 262 722 |
| vermeer | 4 784 | 3 038 | 5 789 | 347 462 → 355 881 |
| sunflowers | 8 098 | 4 899 | 8 836 | 163 530 → 170 168 |

- The "before" column is the offline chain without the step (`NOINK=1`), not the live run.
- On the photographs and the Vermeer the same step removes the silhouette halo that the wash used to trace: the
  troll's light rim, the dark edge around the jug, the rims of the sunflower leaves. No background detail was taken
  in the crops checked.
- The step costs 0.13–0.17 s. `harness/srchole_ink.js` runs the chain offline on an A/B dump.

**Off the main thread, and the live SD view** (app branch `s62-worker`, `2e60fcb`; goes to main when the clip run ends).
- The hole solve runs in a Web Worker built from the solve's own source. The app globals it reads travel with the
  message. The new plate is applied when the result arrives, unless a newer bake has started. With no Worker it runs
  on the main thread, as before.
- The worker's result against a main-thread solve on the same inputs (starwatcher, `harness/srchole_worker_check.js`):
  hole, plate and wash identical (0 of 86 722 texels differ).
- The page still freezes for about 12.5 s during a source-mode bake. That is the per-line bake, which still runs
  underneath and whose plate is then thrown away; the hole solve itself (4–7 s) no longer adds to it. Skipping the
  per-line build in source mode is the change that would remove the freeze.
- The "SD regions" tint (the plate, its strips, and the foreground's dimming) now reads the hole. Tinted texels = hole
  texels (86 722 = 86 722, 0 differing), so the tint on screen is the bundle's inpaint mask.
- The SD bundle export waits for a hole that is still solving, instead of writing the per-line plate.

## 7. Source mode on its own (user: "do 1 and close all the gaps / features only the per-line path has"; app branch `s62-worker`)

**The per-line build is skipped in source mode.**
- In source mode the quick bake keeps only three things:
  - the depth preparation that builds the source depth (edges, ink, dequantise, despeckle, smear snap);
  - the foreground and its tear;
  - the plate's mesh and textures.
- Everything the hole replaces is skipped: the band, the plugs, the plane far side, the wash, plate 2, the step faces, the ordering clamps, the plate's own tear, and the post-bake fill. The plate's colour canvas starts as the source and the hole's wash is written into it.
- A source bake no longer inherits an earlier per-line bake's fields. `_geoFarField`, `_bandReplace`, the carriers and the rest were being read from whatever the last per-line bake left behind.
- Starwatcher before and after the skip gives the same bundle to the texel: source depth, plate depth, plate colour, inpaint mask, and occluder-removed picture.
- The bake core went from 6.0 s to 3.8 s.
- 7.3 s of the rest was an 8-bit read-back of the depth image that the 16-bit path drew and threw away. It now runs only when the 8-bit path needs it. That fix applies to per-line mode too.
- Timing on the troll: the bake core is 4.2 s. The once-per-picture live sharpen still takes 2.5 s. The hole solve runs in the worker.
- The edge sharpening never marked the foreground depth dirty. The foreground showed the sharpened edges only because later passes happened to mark it. It is marked now.

**Objects.** `bgSourceHole` returns its own far field: the reach again with no budget, so each occluder is covered whole, and each texel takes the far depth of the rim that reaches it first. Objects (`_planeObjects`) are measured against that.
- Starwatcher: 7 objects. Troll: 46.
- `plane_object_ids.png`, `meta.plane_objects`, the context mask and the occluder-removed picture are written in source mode.
- An external (SAM) object map no longer needs a far field. It was ignored whenever none existed.

**Surfaces, the second layer, and sky** (`surfaces()` inside `bgSourceHole`).
- The kept pins of each hole component are grouped by surface:
  - Runs are 8-adjacent pins that the rim law joins: the straight-slope join on the axes, the ratio test on the diagonals.
  - Runs whose median depths pass the ratio test are one surface.
  - A surface seen along fewer than `WASH_RUN` (8) pins is no wider than an ink line and cannot be told from one. Its pins are dropped, like the blur's leftovers. On the troll this removed a 3-pin "surface" that had claimed a bright disk.
- With one surface, nothing changes. Starwatcher, the Vermeer and the sunflowers have no component with two surfaces, and starwatcher's hole, plate and wash are byte-identical to before.
- With two or more surfaces, the component is split by a random walker (Grady 2006). There is one harmonic per surface, set to 1 at its own pins and 0 at the others, and each texel goes to the surface whose harmonic is largest. Each part is then filled, depth and wash, from its own surface's pins only. Before, one membrane ramped between the surfaces.
- The farthest surface continues behind the nearer parts as plate 2. This is one membrane over the whole component, pinned at that surface's pins, and it is kept where it lies behind plate 1 by two steps. It is the 2-D form of S4's arrival order.
- Plate 2 is a second mesh, built the S4/S5 way: a triangle is kept if any corner carries the layer and the rim law joins its edges, all-sky triangles are left out, and it is class 4 in the SD view. The bundle gets `plane_plate2_*`.
- Troll in the app: 3 components split, 82 679 plate-2 texels, 164 057 plate-2 triangles.
- The split costs 12.6 s of the troll's 64 s worker solve. Walker labels only need the order of the harmonics, so that solve stops at a relative residual of 1e-4. Reusing labels across rounds is the next saving.
- Sky, with sky at infinity on:
  - The step-scaled rim law now joins sky only to sky, as the app's own rim law does. It used to fall through to the straight-slope join.
  - Sky rims reach by the plane-at-infinity law.
  - Sky is its own surface, so a part of the hole that continues the sky has sky depth, and its triangles are left to the sky layer (`bgRetearPlate` skips all-sky triangles).
  - The sky layer's texture takes that part's wash.

**SD return.** In source mode, `_importPlaneReturn` rebuilds the plate index on the returned depth with the same rule (`bgRetearPlate`). Before, the plate kept the bake's tears.

**The SD stage on the new bundle** (starwatcher; SD 1.5 inpainting + depth ControlNet, CPU, 20 steps, 40 min).
- Input: the whole astronaut lies inside the mask, so SD sees the picture with the figure already gone (PACO's arm (c), the contract S52 found best).
- Colour: starry sky and the plain continue through the figure's place, with no trace of it. There are a few flaws: a faint dotted trace of the staff under the lamp, one small invented object on the plain, and a dark smudge at the frame's bottom edge.
- Depth asked back through DA3 and fitted on the legal background: the plain in the hole comes back nearer than the plain beside it. The import removes one constant per component; whether that is enough is checked by the round trip.

## 8. The hole kept to what some pose shows (user: "go ahead with the contact fix")

**The kit found it.** S2 (boxes on a floor) and S15 (tree, sign, hills, sky) were scored against their exact hidden sets at the env45 envelope (`truthkit/check_app_band.py`). Source mode missed almost nothing (recall 1.00 and 0.99), but the hole was 4–6× the hidden set (precision 0.22 and 0.16; per-line 0.89 and 0.72).
- The reach flowed off each object through the contact where it stands: the trunk on the ground, the box on the floor. The contact is joined, and the ground is in front of the far wall, hills and sky, so the reach passed. It then covered the whole floor or ground.
- The renders never showed this, because the ground covers that plate at every pose. But the SD mask carried the whole floor, and the ground no longer gave the fill its pins.
- Three repairs were tried and measured before the one that works:
  - Continuing the far side as a plane instead of a constant: no change. Here the far side is a wall or the sky.
  - Clipping the reach to the frame: no change.
  - Rerunning the reach with seen budgets: the flood came back through the same contacts.

**The rule** (`bgSourceHole`, after the reach).
- A hole texel is kept only if some pose shows it. For 32 head offsets over the envelope rectangle (8 directions × 4 magnitudes), the source mesh is moved: each texel by its own shift, stretched between the texels the rim law joins, nearest in front.
- Every uncovered screen pixel inside the frame with a surface on both sides along h (a real gap, not the outpaint band at the frame's edge) shows the plate.
- The surface on the gap's far side continues there, so the plate texel shown is g − s_far·h. It is marked seen.
- The seen set's outline carries the map's column-to-column noise. A majority over a (2·8+1)² square decides the texels: 8 is `WASH_RUN`, the ink-line scale. Texels within 8 of their own rim stay whenever they were seen, so a thin staff (all rim) is kept.
- Cost: about 3.3 s per bake, in the worker.

| scene | precision | recall | weighted recall | hole px | band depth p90 |
|---|---|---|---|---|---|
| S2 before | 0.22 | 1.000 | 1.000 | 75 937 | 0.072 m |
| S2 seen | 0.47 | 0.997 | 0.998 | 34 818 | 0.049 m |
| S15 before | 0.16 | 0.994 | 0.999 | 220 310 | 8.57 m |
| S15 seen | 0.53 | 0.967 | 0.993 | 63 395 | 8.57 m |

- Pictures (hole texels, before → after): troll 259k → 133k, starwatcher 89k → 54k, the Vermeer 342k → 246k, the sunflowers 170k → 121k.
- The outlines stay smooth. Starwatcher's staff stays in the hole, and the near dune keeps only its reveal band.

**Still open: S15's depth inside the canopy.** The median band error stays 3.5 m (per-line 0.18 m; keeping the source depth 0.02 m).
- It is not the flood. The errors sit inside the tree's canopy, where the first hidden surface is other leaves a few centimetres behind, and the source fill puts the far hills and sky there.
- The per-line law continued neighbouring leaves. A porous occluder (foliage) is its own problem for the source construction.
