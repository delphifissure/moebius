# Research note R2 — the gap / inpainting atlas collection

Status: specification draft, no code. Follows R1 (§0b purpose, §1.4 envelope). The biggest problem is
filling new content; the precursor is a great collection of gap atlases. This note says what that
collection is, what "great" means in numbers, how the existing pipeline maps onto it, and which
synthetic scenes validate it first.

## 1. Definition

For one input (RGB + depth) and one viewing envelope (window W, distance range, offset range up to
~85°, vertical range), the **collection** is a set of 2-D charts, each a small image-like asset with
aligned channels. Everything a viewer can see from anywhere in the envelope is covered by exactly
one chart texel at the front-most depth along that ray; everything that was photographed is in the
foreground chart; everything else is scope.

### 1.1 Chart types

| chart | one per | geometry | scope class | comes from today |
|---|---|---|---|---|
| A0 foreground | image | the depth map, snapped ramps, torn at jump edges | none (photographed) | the plate mesh |
| A_matte | jump-edge band | alpha-weighted depth, 4-px strip (Zitnick) | boundary | nothing yet (E8) |
| A_side_i | solid thing i | closed Poisson-inflated side to the equator, in world units via focal, per part at internal cliffs, terminated on the ground plane | object side | A257 backs (replace the envelope and the scale) |
| A_hidden_k | image, k = 1..K | k-th hidden surface behind things: plane / far-rim continuation with the deeper-lip floor for solid interior steps; a positive increment behind layer k−1 | disocclusion | the plug (one layer today) |
| A_stuff_j | stuff surface j (wall, floor, ceiling, ground) | the fitted plane, chart plane-rectified, extended beyond the frame to the envelope's footprint | disocclusion inside the frame, outpaint beyond it | membrane + A245 margin + A214 orange |
| A_porous_i | porous thing i | the crown envelope as a near layer with alpha coverage | porous holes (background through them is A_hidden / A_stuff) | nothing yet (E6) |
| A_sky | image | infinity | outpaint beyond the frame only | the far value |

### 1.2 Channels per chart texel

- depth (float; or plane parameters + UV for rectified charts)
- placeholder RGB (the wash; never a clone)
- scope mask and class (photographed / disocclusion / side / outpaint / porous / matte)
- visibility weight: the fraction of the envelope from which this texel is the front-most visible
  surface through the aperture (the window model gives it in closed form per depth; the sweep is
  its Monte-Carlo estimate)
- provenance / confidence: photographed, observed (the sweep saw a real far lip there), continued
  (plane or slope), inflated, generated
- seam data: which neighbouring charts overlap this texel and by how much
- resolution: chart texels per world unit chosen from the plate's own density at that depth, so SD
  sees a consistent pixel scale across charts

### 1.3 Invariants

1. At the rest pose only A0 is visible (pixel-faithful).
2. Every envelope-visible ray hits exactly one scope texel or one photographed texel: no holes, no
   double coverage except the declared seam overlaps.
3. Nothing in any chart depends on a pose; the collection is computed once.
4. No texel in scope carries a colour copied from a nearer surface (clone-free placeholder).
5. Every depth in scope is a continuation of a photographed surface by a stated rule (plane, slope,
   deeper lip, inflation, sky), never an interpolation between a near and a far surface.
6. Every constant is one of: a physical quantity (W, D, focal, gravity), a measured quantity (ramp
   width b, depth quantum), or a cited rule (ratio t ∈ [1.05, 1.25]; Monster Mash c = 2; the 4-px
   matte band; alpha 0.1).

## 2. What "great" means, in numbers

Measured against synthetic truth (R1 §4) and, where possible, on the six photographs:

| criterion | metric | target |
|---|---|---|
| complete | visibility-weighted scope recall per class | ≥ 0.99 for disocclusion and outpaint; ≥ 0.95 for sides |
| tight | scope precision (no photographed texel in scope) | ≥ 0.99 |
| stable | change of scope / depth / placeholder along a gallery walk | 0 by construction; any nonzero is a bug |
| depth-plausible | median depth error inside scope vs peeled truth; bad-pixel rate | within one depth quantum on planes; within the inflation model's own error on sides (measured on S11) |
| clean | ghost/clone index; streak count (grazing-triangle test); skirt count | 0 skirts, 0 streaks, clone index at the wash's floor |
| small | number of charts; scope texels per chart; overlap fraction | as few charts as the scene's layers require; the artist's workload is the count |
| ranked | visibility weight present and monotone with the envelope | every scope texel weighted |
| SD-ready | chart distortion (Jacobian range of the rectification); pixel scale consistency | rectified stuff charts; sides unwrapped with bounded stretch |
| end-to-end | SD run on the collection, rendered through the envelope, masked LPIPS/DISTS vs offset-eye truth | the only number that certifies the collection for its purpose |

## 3. Build order (the bake, from R1 §3.1, in atlas terms)

1. Depth in a metric frame (Depth Pro / MoGe-2: depth + focal), float storage, gravity and horizon
   (GeoCalib), panoptic stuff/things + sky.
2. Edges: ratio test, ramp width measured, weighted-median snap, ownership to the far side, thin
   ridges restored, jump vs crease. Output: A0 and the edge graph.
3. Envelope footprint: for each depth layer the visible strip through the aperture over the envelope
   (closed form), intersected with the frame → the scope of outpaint (A_stuff beyond frame, A_sky)
   and the visibility weights.
4. Stuff charts: planes fitted on stuff pixels, rectified, extended to the footprint; ground plane
   bounds everything below the horizon.
5. Things: porosity test → A_porous or solid; solid → A_side by Poisson inflation per part, clamped
   to the ground plane; internal cliffs → per-part layers.
6. Hidden layers: for each ray behind a thing, the ordered list of continued surfaces (stuff plane
   first, then deeper things' far parts by the deeper-lip rule) → A_hidden_1..K with positive
   increments; the observed sweep remains the check that a continued depth agrees with what a real
   far lip shows.
7. Matte strips at every jump edge → A_matte.
8. Placeholder RGB per chart: depth-weighted push–pull wash from that chart's own photographed rim;
   highlight overlay per class for the artist.
9. Seams and overlaps recorded; resolution normalised; the collection written as an asset; the
   renderer composites charts front to back with alpha (three shader rules, R1 §3.2).

## 4. What of the current code survives

- The observation sweep: as the estimator of visibility weights and as the check on continued depth
  (not as the source of the plug's depth).
- The A253 classes (continuous / interior step / extent): they become scope classes and the
  deeper-lip floor for solid interior steps.
- The membrane / push–pull: the placeholder.
- The A245 margin and the A214 orange: absorbed into A_stuff beyond frame and A_sky, sized by the
  envelope footprint instead of the border shift.
- A257's inflation machinery: replaced in form (Poisson, world units) but the mesh, the alpha
  discard and the depth-pass rules stay.
- The per-fragment tear: becomes chart boundaries plus the grazing-triangle kill.
- The depth-view harness: extended to score scope precision/recall and per-chart depth error.

## 5. First validation

Synthetic (R1 §4.2): S27 the fishtank room (scope of outpaint per layer at 15–85°), S11 the rounded
solid (side size and depth vs truth), S1 room corner (plane charts), S10 thigh over calf (hidden
layers and interior step), S7 canopy (porous chart vs solid). Each has an exact ground-truth
collection: render the hidden-occluder and wider-FOV passes, peel the layers, compute the envelope
footprint from the same window model. Photographs: the six scenes, scored on invariants 1–5 and on
the cleanliness metrics, with the artist's highlighted rest view and a three-position turntable as
the screen check.

## 6. What this note does not decide

The diorama-depth lever (R1 V6) and the E4 principle remain the user's; the SD stage's own design
(model, conditioning, per-chart vs joint, seam handling) is the next note, R3, once a first
collection exists to run it on.
