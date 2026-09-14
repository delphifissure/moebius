# S27 — Object layers in the bundle: export the occluders as objects, import completed object layers at the object's own depth (Sprint 19, 2026-09-14)

**Premise (S26 §3b).** Behind an object the plane law is the right depth (exact on continued surfaces; a depth model cannot
be normalised where the hidden range lies outside the visible one). An object's own far side lies within its thickness of
its front, and "the far side is at the object's front depth" ties or beats a depth model + clamp on 15 of 17 kit scenes.
So the object-layer path carries **objects**, not a depth model: the bundle exports each occluder's footprint and box for a
layer model (RevealLayer takes boxes, RLD masks), and imports the completed RGBA layer the model returns, placing its hidden
part at the object's own front depth continued (or a supplied depth aligned on the visible front), behind whatever is visible
at each texel. Everything is behind the existing bundle and a new button; no default changed.

## 1. What was built (app `984cdb1` + follow-ups; CODEMAP §35)

**Export.** `plane_object_ids.png` (8-bit, native plate grid) and `meta.plane_objects` (rule, count, boxes `[x0,y0,x1,y1)`,
footprint and band-demand pixel counts, mean front and background disparity, the source-image scale, the reimport contract).
Object rule, in three steps because the first two were measured wrong:
1. *First draft*: continuous surfaces flooded from the band's far-side texels. On S2 it merged the boxes standing on the
   floor into the floor (the contact is depth-continuous) and made the floor's and ceiling's frame-border band into
   objects (238 "objects", three real). Removed.
2. *A253's rule* (`dQ − farField > fgTearStep`, the app's own cliff step; 4-connected): S2 → exactly the three boxes.
   But on S15 the hills in front of the sky are "in front of the far field" too, and the trunk, adjacent to the hill in the
   image, merged with it (one 69 k-texel object).
3. *A253 + continuity + sky*: components also require the rim law's join between neighbours (a trunk in front of a hill is
   not the hill), and band texels whose far side is sky do not count as an object's demand (they are the sky layer's).
   Objects are ranked by band demand, not area; components without demand are not exported; ids 1..254.

**Import.** `Import object layers (S27)` (both HTML files) reads `obj_<id>_color.png` (+ optional `obj_<id>_depth16.png`,
8/16-bit grey decoded in the browser); `window._importObjectLayersFromData(entries)` is the same path for harnesses. Per
layer: visible texels = alpha ∩ the object's footprint (or a caller mask); their depth is the source depth. Hidden texels:
the nearest visible texel's depth by breadth-first steps over the layer's alpha (zero-thickness rule), or, when a depth is
supplied, that depth aligned on the visible texels (robust affine, linear or inverse of the input, chosen on the visible
residual; **no fit when the visible front has less than three quanta of depth range** — a fronto-parallel face determines
nothing, S2's boxes "fitted" any depth with slope −0.57 and residual 1e-12 before the guard). Every hidden texel is then
clamped one quantum behind whatever is visible at it (a135). The layer is its own mesh on the source grid: plate 2's recipe
(a clone of the plate material with its own depth texture and RGBA texture, triangles kept only where all corners carry
the layer and are joined under the rim law on the layer's own depth, alpha-0 discarded in both passes by A257c/e), synced,
toggled and disposed with plate 2 (a new Build drops imported layers).

**Harness.** `harness/objlayers.js` bakes a kit scene as the panel does, dumps the object export, builds the truth's own
completed layers for those objects (`truthkit/obj_layers_from_truth.py`: app object → kit primitive by footprint majority;
the layer = the primitive's first hit along every rest ray, colour and depth), imports them under three arms — *none*,
*cont* (front continued), *truth* (the truth's depth supplied) — shoots the a257 poses, and renders the truth's own view at
the same eyes (`truthkit/truth_view.py`). `harness/objl_sheet.py` scores each shot against the truth view: uncovered pixels,
mean |RGB error| over the frame, and the fraction of pixels off by more than 64 ("wrong content"). Registration check: the
rest pose scores 4.2 mean error on S2 for every arm alike.

## 2. Results

Four kit scenes, the truth's own completed layers imported, four poses (rest; fx 0.6; fx 1, fy −0.5; fx −1, fy 0.5 of the
45° envelope). "changed" = pixels the layer arm alters against the no-layer arm; the error is the mean |RGB| against the
truth's view on exactly those pixels, before → after. Whole-frame means and hole counts are in `s27/table_<S>.json`.

| scene | objects exported (A253 + continuity) | truth layers (hidden px) | pose | arm | changed px | error on changed px |
|---|---|---|---|---|---|---|
| **S9** three cards, one behind the other | 4 (the three cards + one fragment) | card1 10 094, card2 16 786, card0 0 | 0.6, 0 | cont | 22 588 | **73 → 7** |
| | | | 1, −0.5 | cont | 26 907 | **76 → 12** |
| | | | −1, 0.5 | cont | 10 287 | **71 → 17** |
| | | | any | truth | = cont | fronto-parallel cards: no depth fit, front continued |
| **S15** tree, sign, hills, sky | 126 (crown 79 fragments, sign, trunk…) | crown 204, sign 497 | 0.6, 0 | cont / truth | 62 / 87 | 54 → 52 / 51 → 43 |
| | | | 1, −0.5 | cont / truth | 95 / 152 | 67 → 49 / 75 → 56 |
| | | | −1, 0.5 | cont / truth | 64 / 64 | 35 → 23 / 27 → 18 |
| **P2** porous canopy | 288 (34 beyond the cap) | crown 140 | 0.6, 0 | truth | 54 | 83 → 53 |
| | | | 1, −0.5 | cont / truth | 21 / 83 | 67 → 54 / 77 → 54 |
| | | | −1, 0.5 | cont / truth | 12 / 96 | 57 → 60 / 82 → 44 |
| **S2** three boxes on a floor | 6 (three boxes, their tops) | box0 1 252, box1 850, box2 1 120 (all base rows, not hidden content) | all | cont / truth | 0 | — (identical frames; whole-frame mean 4.2 / 7.3 / 12.1 / 20.6 for every arm) |

Registration: the rest pose scores 4.2 (S2), 6.9 (S15), 4.0 (S9), 2.6 (P2) mean error for every arm alike — the app frame
and the truth view line up; the residual is texture filtering. Whole-frame means move by ≤ 0.2 on S15/P2 and by 4–5 on
S9 (16.8 → 12.6 at fx 0.6; 20.9 → 16.1; 19.1 → 17.5), where the "> 64" area falls from 13.6 / 19.9 / 14.9 % to 9.5 / 15.0 /
13.5 %. The uncovered-pixel counts are the plate's and do not change (P2: 268 / 2 203 / 629 / 1 at the four poses).

## 3. What the numbers say

1. **Where an object hides another object, the imported layer does exactly what it should.** On S9 the cards behind cards
   come out where the truth has them, at the right depth (the front continued: a card is flat), with the right colour: the
   error on the 10–27 k pixels the layer touches falls from ~73 to 7–17, and the whole frame's "wrong content" area drops
   by a third. The plane law's wall wash that used to sit there is replaced by the object.
2. **Where nothing is hidden behind anything, the layer has nothing to add.** S2's boxes hide only their own sides and
   backs, which a texel layer cannot carry (§4); the frames are identical. S15's crown as a first-hit layer has 204 hidden
   texels; P2's canopy 140. Their few dozen changed pixels improve modestly (54 → 52 … 82 → 44) with two small regressions
   (S15 rest 56 → 64 on 46 px, P2 −1,0.5 cont 57 → 60 on 12 px): the continued front is not the leaf's depth at a gap
   edge. The kit's own scoring in S26 said the same in depth: the object far-side content is thin.
3. **The supplied depth is worth little on these scenes.** With the truth's depth aligned on the visible front, S15 and P2
   gain a few pixels over the front continuation; S9's and S2's fronto-parallel faces give no fit (the guard, §1) and fall
   back to continuation, correctly. A depth model's output would not do better than the truth's.
4. **What the object export is for.** `plane_object_ids` + boxes are the input a RevealLayer / RLD run needs (boxes, ≤ 8
   instances per call; masks); the import is where their layers land. On S9 the A253 + continuity rule finds the three
   cards and one fragment; on S2 the three boxes (and their top faces as separate components); on S15 and P2 porous
   crowns fragment into 79 and 241 components (P2 exceeds the 254 cap) — the grouping for a layer model is open (§4).
5. **Bugs found by looking at the buffers, all fixed before the numbers above:** the first object rule merged S2's boxes
   into the floor; the truth-layer generator multiplied an 8-bit colour by 255 (pink crowns); the app footprint was used
   as the layer's visibility and pushed 4.5 k visible crown texels behind the front (now: `obj_<id>_visible.png`, the
   layer model's visible/amodal split); a dangling `else` logged one warning per texel; a two-level visible front let any
   supplied depth "fit" with slope −0.57 (now: MAD floored at the quantum, kept set must span three quanta).

## 4. Limits, stated

- **A texel layer carries one surface per texel.** An object's *own sides* are edge-on at rest (zero texels) and its back
  faces sit under its front: neither can live in an RGBA + depth layer parametrised on the rest grid. That is why S2's
  boxes are unchanged by their own completed layers, and why the box-wall class of S24 needs geometry (a side mesh with a
  thickness nobody measures well, S26 §3b), not a layer. Object layers help where an object hides *another* object or its
  own far parts through gaps (amodal parts): S9's cards, the trunk and hills behind S15's crown, leaves behind leaves.
- **Porous objects fragment** under the continuity rule (S15's crown: 32 components map to one primitive); the harness
  groups them by the kit's primitive, a real layer model would get 32 boxes. A grouping rule without a constant is open.
- **Terrain in front of the sky is an object under A253** (hills); with sky reveals excluded from demand it ranks low or is
  dropped, and the continuity rule keeps it from swallowing the trunk. It is still exported when it hides another hill.
- **SwiftShader compiles the cloned materials on the first frame after an import** (≈ 6 minutes per arm in the headless
  harness; a real GPU does it in a second). Every previous harness paid the same for plate 2 once.

## 5. Files

App: `moebius.js` (`_planeObjects`, `_objFitDepth`, `_importObjectLayersFromData`, `_clearObjectLayers`, `_pngToRgba`,
`_png16Decode`, `importObjectLayers`, the export block, the hooks), `moebius.html` / `harness/scratch_moebius.html` (button),
`harness/objlayers.js`, `harness/objl_sheet.py`, `harness/truthkit/obj_layers_from_truth.py`, `harness/truthkit/truth_view.py`.
Research: `research/s27/` (sheets, tables, results per scene).
