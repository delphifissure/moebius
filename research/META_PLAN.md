# Meta-plan (updated 2026-09-12, after C, D and B)

## Where we are

- **Geometry (the plate).** Rim law, plane far side per line, carriers, plate 2 from the arrival order, sky at infinity as an
  option, 16-bit sources with a σ-gated visible-step floor. On the eight kit scenes and the three rescored ones the band is
  the size of the truth at recall ≈ 1 (precision 0.94–0.96 where Sprint 1 had 0.21–0.36); depth error median 0. Nine
  designs tried and removed with numbers; seams accepted as the price of locality and handled at the plate.
- **Depth.** DA3-Mono-Large chosen by bake-off; on six repo pictures it beats every stored map (S19).
- **Hand-off.** The SD-regions view shows the true placeholder set by class; the bundle after a plane bake is the plane
  bake (native res, 16-bit, plate 2, masks, conventions meta). No reimport of that bundle exists.
- **Known gaps, measured:** thin lines erased by the despeckle (S5: 1-texel poles, S18 §2); holes at far poses on
  silverwarrior / vermeer / room (S19 §3.1); S7's ceiling over-claim (S18 §2b); the σ gate reads 0 on sky-heavy maps and the
  floor does not clearly help (S19 §3.4); the sky option leaves the frame edge uncovered from 0.2 m (S19 §3.5); no polarity
  / range check on incoming depth maps (S19 §3.3).

## Principles (unchanged)

Zero per-image tuning; every constant cited or derived from the window's own extent; trust the depth map; everything filled,
wash never clone; falsified premises removed from code and recorded; arms must diverge before numbers are read; the user's
screen is the aesthetic authority; defaults change only in the live pass.

## Order of work

1. **Sprint 13 (now).** (a) **Thin-line despeckle**: the fleck test keeps a texel through which a 1-texel line of the 5×5
   window's own length passes (all 4 along-direction neighbours within tolerance, any of 4 directions); behind
   `window._despeckleLines`; measured on S5 (recall), the troll's striation combs (the rule's reason to exist; shots), the
   kit (identity expected), the six pictures (clones, holes). (b) **Far-pose holes**: diagnose with the sweep class maps on
   silverwarrior / vermeer / room at 45°, 52°, 56°; name the class of every hole (never demanded / demanded but torn /
   beyond the envelope / beyond the frame); the fix follows the class, not before.
2. **Live pass (A), with the user.** Defaults consolidated from the option arms (plane far side, tier, seams, margin, sky),
   dead arms stripped, re-baseline of all instruments; the input contract: polarity and range check on a loaded depth map
   with a visible warning; decide the S7 ceiling blob and the sky-margin gap on screen.
3. **Reimport** of the plane bundle (plate 1 colour, plate 2, sky, margin) onto the live plate; round-trip test with the
   bundle checker.
4. **SD integration test**: one real inpaint of the bundle (any model), reimported, viewed; the first end-to-end picture.
5. **After Sprint 13, in this order (user's instruction, 2026-09-12):**
   - **Per-region noise estimate for the σ gate** (S19 §3.4): σ per region rather than one global median, so a flat sky
     cannot declare a noisy foreground exact; gate the floor where the region is noisy. Measure: the four sky-heavy DA3 maps,
     the troll (must be unchanged: σ > 0 everywhere that matters), the kit (must stay byte-identical: σ = 0 on planes).
   - **Consistent far field across lines** (§16 closed the per-sheet thin-plate and local variants against truth and by
     seams; reopening means a different construction — the closure's numbers are the bar: S15 band depth 0.18 m, the
     photograph's same-sheet seams must fall, not rise).
   - **Persistent-departure segmentation** (§15 closed at step 0: 99.6 % of DA3-16's breaks are already supported by an
     adjacent line; reopening means either a different criterion or a different source where unsupported breaks exist).
   - **S7-class porous silhouettes**: a scene set of its own (canopy density, leaf size, single vs layered crowns, a fence, a
     grille) with env45 truth, then the ceiling over-claim and the between-leaf demand scored per class.
6. **Live pass (A) and reimport / SD test** follow, as in items 2–4.

## Status after item 5 (2026-09-13)

All four queue items are measured and closed (S20–S23). Built and kept as option arms for the live pass: the line-aware
despeckle (`_despeckleLines`, S20), the untorn plate seams value (S20), the **ceiling cut** (`_ceilCut`, S23 — S7 P 0.65 → 0.86,
P6 0.50 → 0.69, S26 0.46 → 0.82, inert elsewhere). Built, measured and removed: the regional noise gate (S21). Closed
offline without building: cross-line regularisation of the law (S22), persistent departure along the line (S23). The porous
set P1–P6 has env45 truth; its residual is the one-texel silhouette ring, ordered by perimeter ÷ area. Next: the live pass
(item 2) with these defaults on the table.

## Status after the horizon scan and the depth-stage test (2026-09-13, later)

S24 (horizon scan), R4 (mathematics of the plug), S25 (Sprint 17: rules select, 60° bake, fold-alpha plate, clamped plate /
AMLE offline — the field family closed a fourth time), R5 (the layered stack: RevealLayer, RLD, Amodal SAM, SAMEO, Lift3Dreamer,
DepthLab, MoGe-3 read; the stack proposed with trades) and **S26 (Sprint 18: the depth stage scored on truth)**. S26's
result fixes the shape of the stack's depth stage: **background layers → the plane law** (beats DA3 / MoGe-3 / DepthLab on
19 of 19 scenes, exact on continued surfaces, and the models cannot be normalised where the hidden range is outside the
visible one); **the object's own far side → a depth model on the completed object layer + the ordering clamp** (beats the
plane law on 17 of 17 scenes by 5–400×; thin objects excepted). DepthLab is a learned continuation of known depth: strong on
non-planar anchored backgrounds, the plane law's equal on self-occlusion. Then **S26 §3b** removed the depth model from the object path (the zero-thickness rule ties or beats it) and **S27 (Sprint 19)**
wired the object-layer path into the bundle as objects: `plane_object_ids` + `meta.plane_objects` out (A253 rule + continuity,
ranked by band demand), `Import object layers` in (visible texels keep the source depth, hidden ones continue the object's
front or an aligned depth, clamped behind what is visible). On the kit it does what it can: where an object hides another
(S9's cards) the changed pixels' error against the truth view falls 71–76 → 7–17; where nothing is hidden behind anything
(S2's boxes, S15's crown, P2's canopy as a first-hit layer) it changes almost nothing, and an object's own sides cannot live
in a texel layer at all. Queue: the live pass; RevealLayer / RLD on the six pictures when a GPU exists (60 GB) — their layers
now have a place to land; per-leaf (K-hit) layers for porous objects; labelling of the far-side choice scored by magenta area
(S25 §4); hole class X (S25 §2).

## Status after Sprint 20 (2026-09-14, later)

**S28**: SAM 2.1 visible masks replace the depth-only footprints on photographs (offline script, clicks / boxes / automatic;
`Import object masks`), and the live **standpoint highlight** reads, per band texel, its occluder and the surface its plate
depth continues (`_bandContinuation`, seeds gated so the occluder cannot seed its own band): red = hidden by another surface,
orange = a surface hiding itself at a step inside the picture, blue = visible. On the troll one click is the torso; four
clicks are the troll (speckled left arm); the woman needs two. What orange cannot mean: sides and back faces beyond a
silhouette — not in the picture, a 3D prior per object (Amodal3R) is the only source. Queue: SAM 2.1 in the browser for live
clicks (ONNX Runtime Web); amodal masks (pix2gestalt / a SAMEO reproduction) when a GPU exists; then the live pass.

## Status after Sprint 21 (2026-09-14, later)

**S29**: SAM 2.1 runs in the page (onnxruntime-web, WebGPU or WASM; the onnx-community export of hiera-small fetched once
from Hugging Face and cached). Click objects at the rest pose, Tab through SAM's three candidates, Alt-click to exclude,
Enter to keep — the kept objects are the object map and the S28 highlight comes on per object. Headless replay of the S28
clicks reproduces the offline masks (troll IoU 0.993; the woman 0.89 by SAM's own near-tie between two candidates); the
screen ↔ source mapping is exact at rest (colour check). Queue unchanged otherwise: amodal masks (pix2gestalt / SAMEO
reproduction) and per-object 3D priors when a GPU exists; the live pass.

**Video (user, 2026-09-14).** The object masks must work for video in time. SAM 2 / 2.1 is that model: the image path wired
in S29 is its per-frame half; the video half (memory encoder + memory attention + object pointers, propagating a click on
one frame through the clip) is the same weights family and exists as ONNX exports (onnx-community publishes `Sam2Video`
configs; a `sam2.1-memory-attention` export is on the Hub). When the app's video layer needs per-frame object maps, the
plan is: encode frames with the same encoder, run the memory attention graph per frame, and hand each frame's ids to the
same `_setObjectIds` path — one prompt per object per clip, not per frame. Not started; it needs a video bake first.

**Plan review (2026-09-15).** `PLAN_REVIEW.md` restates the goal and ranks the weaknesses: the diffusion loop never closed
(no inpaint run, no plane-bundle reimport), cardboard objects at wide angles, no real-scene truth, beyond-frame content,
one-pass and video not designed, the live pass not held, the untested fork to novel-view generation. It reorders the GPU
work: close the loop first, real truth second, the fork third, objects fourth, video fifth; the live pass alongside.

**Defaults set (2026-09-15).** The measured panel set is now the app's start-up default (CODEMAP §38); margin off at the
user's word. The four trades (seams, margin, fold-alpha, tier) stay panel choices until seen in motion.

**S32 (2026-09-15).** The user's sheets: the frame-edge streaks with margin off were A245's rest-footprint clip switched off
together with the strips; the clip is back by default (`_edgeTear = 1` is the fold-law alternative outside the footprint).
The 2-D clamped plate per run cluster, ported into the app behind the join select, equals the plane law on the kit and adds
to the row structure on the troll and vermeer (clusters follow the run segmentation; rows are solved apart) — falsified as a
cure, due for removal by rule 7 after the user's look. Next: the diffusion loop (plane-bundle reimport, one inpaint on a GPU).

**S33 (2026-09-15).** The user asked why the plate streaks at all. Measured on six pictures: 57–77 % of the plate's visible
bends (42–74 % of the wall length) are the far-side construction disagreeing with itself — rows of one surface given two
depths (short walls, the hatching) and the row/column arbitration flipping between neighbours (long walls); 26–58 % of the
wall length are real steps between two background surfaces drawn as rubber where the user's model wants a tear with a sheet
behind. Options ranked: the axis decided per piece (A), tear + second layer behind internal cliffs (C), the tangent-plane
carry (B). Nothing built; the user decides.

**S34 (2026-09-15).** Step A (the layered order between the row and column candidates) built, measured and removed: the
kit does not rank it and on the six pictures the wall length moved −39…+20 % with the seam count rising — the candidate
fields themselves jump, so no per-texel arbitration can be seamless. C and B in their S33 form withdrawn for the same
reason. The design the measurements point at: one continuation sheet per visible surface (rim-contour clusters by the join
law; plane + harmonic rim-residual extension; nearest sheet shows; ends are tears with the next sheet behind). Next: offline
prototype on the dumps, scored by the S33 instrument and the kit, before any app change. The S32 plate arm is removed.

**S35 (2026-09-16).** The sheet construction built offline (`s35/sheets.py`): surfaces = joined components of the visible
depth; one sheet per surface (plane in disparity, per-axis thin rule, ground plane for ground surfaces; optional rim-pinned
residual or local planes); far sides by the app's run scan; nearest sheet behind the texel shows. Kit: truth kept (S2, S9),
S26 within 1.5 cm, S15 0.184 → 0.013 m; seams halved on S9/S26. Pictures: the bare plane removes 50–92 % of the wall length
with zero within-sheet kinks but reaches only 69–84 % of the band; pinning to the rim restores 92–96 % coverage and brings
DA3's rim noise back (troll +12 %, room +29 %, vermeer −72 %). Next arm proposed: the smoothing thin-plate sheet with λ from
the discrepancy principle at the strip's own noise. Envelope corrected by the user: the target is ±90° (fishtank), the
instruments run at 45°/30°.

**S35 continued (2026-09-16).** The deformed-plane sheet (smoothing thin plate at the strip's own noise, λ by discrepancy)
is the best interior on the kit (S26 median 0, S9 p90 halved) and collapsed on the pictures — which exposed the real fault:
under the join law DA3 fuses the occluder with its background (12–18 % of the "background" strip is the occluder), so every
sheet is fitted partly to the thing in front. With S28's SAM object mask separating them, the bare-plane sheets reach 97 %
of the troll's band and cut the wall length by half. The sheet model needs the object segmentation; the interior model is
second-order. Next: thin plate + mask (running); the mask path for the other pictures; then the app.

**S35 closed (2026-09-16).** With SAM masks (troll's S28 map; vermeer and the sunflower field clicked for the test) the sheet
construction reaches 94–99.7 % of the band on the two maskable pictures and, with fragment specks dropped, cuts the per-line
law's vertical wall length by 80 % (troll, vermeer). Remaining seams: boundaries between DA3 background fragments (the
porous question, now with a measured cost both ways). Thin plate: best on the kit, 5–28 min per picture offline. Decision
for the user: take sheets (mask + flat plane per surface + specks dropped) into the app behind the far-side select, with the
thin plate as the interior once a fast solver exists.


**S35 §14, the floor (2026-09-16).** The 0.42 surface that filled the woman's lower band was not the floor but the strip of
wall seen between table and woman, which DA3 gives the objects' depth; the app's ground detector cannot fit DA3's floor for
structural reasons (wall+floor are one run; the horizon lies 10 000 rows out in the flattened world) and was removed from
the prototype. Three rules solve the floor on vermeer with no new constants: fusion by body match (a fragment whose boundary
depth is the neighbouring object's own is a hedge), no area no surface (one-texel silhouette ramps are not sheets), planar
patches with a 2-D geodesic domain (the folded wall+floor+side-wall component is split into faces; the thin plate over the
whole fold overshoot to depth 1.0 even after the solver was fixed with AMG). Behind her legs: wall to row 880, then the
floor at the visible floor's depths. Troll: faceted cave, equal seam length in smaller pieces; sunflowers worse (leaves are
curved, and one-sided background sheets win the sky's hole — the "where does a sheet end" question, now with a test picture);
kit S2/S9 unchanged, S15 0.18 → 0.07 m, S26 0 → 0.03 m. Next: the sheet's end (sky/corners), then the thin plate per face.

**S35 §17, faceting and the plate per face (2026-09-16).** 96–98 % of the far field's jump length is between facets of one
join-law component, so the patches were rejoined by a crease test (slope difference times the smaller facet's extent against
the visible step; no new constant): 19 173 → 6 853 faces on the sunflowers, 11 007 → 4 514 on vermeer. Merging alone changes
nothing because a merged face is curved; with the thin plate on merged faces S26 reaches truth 0.0000 m. The plate needed one
fix: its free boundary let a 165-texel face bulge and take 11 930 band texels on S15 (2.25 m), cured by entering the face's
own plane as a prior on the domain at weight 1/visible step (S15 0.0795 m, p90 4.25, the best tail measured). Only merged
faces need a plate, which cuts the solves to 130–190 per picture. Net: kit a wash on medians, better on S15's tail, pictures
visually unchanged. Two negatives recorded: facet-wide domains (worse) and the per-texel error budget (never fires, because
patches are selected to be planar). Vermeer's remaining "jumps" are legitimate slope (kinks down 97 %), and the sunflower
field's are real structure inside a fused foliage-sky component, not faceting.

**S35 §19–§20, speed and the reference GIF (2026-09-17).** Vermeer's plane-only bake 12 min → 74 s and the full bake with
the plate 35 min → 9.3 min, bit-identical fields: marches as C-speed slices, specks dropped before the domain pass, the
never-read extend domain no longer built, the rim-pinned residual off by default (it was the whole ordering cost and §11 had
already shown it adds noise), geodesic discs by C dilation, three forked plate workers with BLAS pinned. The Silver Warrior
GIF was measured: a horizontal pendulum of ±5 % of the width with the pivot mid-scene, so it never reveals more than a few
per cent of the picture where the app's envelope reveals 41 %; its cleanliness is amplitude and one axis, not a fill law.

**S35 §21–§22, the three items and the things/surfaces classifier (2026-09-17).** §17 was wrong: the sunflower staircase IS in
the adopted arm (unlabelled leaves extended into the sky beside the big head, 60 row jumps), the same failure as S9's 3 cm
(an unmasked quad extended). A things/surfaces classifier over every visible unit (SAM segment or depth component; a thing
iff nearer than a neighbour along their boundary and by medians, no constant) fixes S9 and S2 to 0.0000 m and the sunflowers
(197 of 211 rows sky, 0 jumps), leaves vermeer 9-click unchanged, and is wrong on the troll (x-ray: every tree is a thing,
none closes, the deep gap fills the whole band), on vermeer with the auto mask (the floor voted a thing on 2 of 470 boundary
pairs) and on S15 (8.55 m: the canopy may not fill behind its own trunk). Four closure variants aimed at S15 were falsified
and removed; one clean A/B showed three of them had broken vermeer without the classifier (v jumps 3 340 → 16 788). Default
arm restored bit-identically; classifier opt-in (`--things`). S9 alone is also fixed by the auto SAM mask under the adopted
arm. Decision for the user: classifier on/off/per picture. App-side: S10c's σ = 0 gate leaves sky-heavy maps at quantum = grid
(starwatcher; `_visStep=1` forces the floor).

**S35 §23, where the colours come from (2026-09-17).** The band's fill colour is the mean of the source colour over the depth
fit's window from the rim texel, and that window is the gap plus one texel, so next to the silhouette it is the one or two
texels straddling the edge; the membrane then carries that across the band. Measured on five pictures: the first far texel is
occluder-coloured in 52–62 % of rims (starwatcher 28 %), the colour edge lies inside the far run in a third to a half of them,
and the occluder's share of the fill is 0.2–0.5 across the band. Remedy previewed offline: the far run's median colour after a
constant-free blend skip brings the share to 0.00–0.04. The streaks are the per-line ring plus the per-line geometry; the sheet
renders still carried the per-line colour (harness). Plan: run-median colour in the app; per-sheet colour fields in the
prototype; the harness to inject colour with geometry.

**S35 §24, the colour window falsified (2026-09-17).** The §23 remedy was built in the app behind `_colorWindow` (three arms:
the fit window, the run median past a blend skip, the fit window past the blend) and baked on five pictures. The arms are
visually indistinguishable and the seam against the visible far surface gets worse (vermeer 82 → 100). The fit window is short
only for the 2–4 % of band texels within a few texels of their rim; elsewhere it already spans the whole run. §23's
"contamination across the band" measured non-locality against a local reference, not contamination, and is corrected. The
buffer shows the real cause: the far side chosen can be a different surface 400 texels away (the troll's pale arm wash), and
25–29 % of rims have runs under four texels where no clean colour exists. All of it removed from the app (rule 7); the fix is
per-sheet colour (§23 step 2), which is the same construction as the per-sheet atlas.

**S35 §25, colour folded into the sheet model (2026-09-17).** A band texel's colour is now its owning sheet's own colour,
continued: grouped by visible surface (not planar patch), harmonic extension per surface, the source's anti-aliased fringe
measured per picture (1 texel on three pictures, 0 on starwatcher) and left unanchored, and a per-surface colour plane where
the owner is not adjacent to what it owns. `sheet_render.js` injects it with the geometry, so screengrabs finally show the
sheets' own fill. Against the kit's hidden-layer colour the sheets beat the app where their depth is better (S15 54 vs 170,
S9 146 vs 177) and lose where ownership is wrong (S26 91 vs 56, S2 92 vs 86): the colour adds no error of its own, it
reports the model's ownership. Streaks inside the band drop (vermeer |dC| 1.54 → 1.06). Nearest-clean-sample fallback tried
and rejected (S9 146 → 181). The app is untouched; moving this in is item 1.

**S35 §26, starwatcher's streaking diagnosed (2026-09-17).** The band behind the figure was filled with his own body three to
four steps behind himself — without an object mask his feet join the ground, so his own surface is the one that continues
behind him, and the layered order prefers it to the sky. The classifier over the automatic SAM mask supplies the figure as a
thing and the card goes: vertical jumps 42 701 → 2 232, horizontal 3 975 → 1 161, both far under the per-line law's 12 308 /
33 531. Three pictures now need the classifier (S9, the sunflower staircase, starwatcher) against the troll's x-ray, which is
the one rule left to fix before it can be the default.
