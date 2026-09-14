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
