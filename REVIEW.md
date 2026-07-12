# Adversarial review — moebius.js disocclusion plug (v3.12.0-bandcut)

Review of the 17-commit bundle `moebius-plug-depth.bundle` (tip `f382003`,
"Kill the streaks at their three real sources") on `delphifissure/moebiusv2`
main @ `f79bae2`, per REVIEW_BRIEF.md. All renders reproduced independently
with the author's harness (chromium/swiftshader, canvas 860x484, full
pipeline: `useInpainting=on`, method=pullpush, Sobel gap generator on,
`debugView=final`). Line numbers refer to `moebius.js` at bundle tip.

> **VERDICT UP FRONT.** The v3.12.0-bandcut drop does not meet the contract.
> Criterion 6 (rest fidelity) fails at pixel level; criteria 1–3 fail at every
> offset tested; vertical offsets (untested by the author) are worse than
> horizontal; a second asset (silverwarrior) is structurally outside the
> plug's operating envelope (92% of its occluding edges never seed a band).
> The failures are not tuning residue — three of them are architectural.
> Recommendation: pre-tear the FG at depth cliffs and make the plug a
> full-occluder "world without foreground" plate (details in §4).

---

## 0. Repro & logistics facts established

- Bundle applies cleanly on `f79bae2`; tip `moebius.js` == the drop-in file.
  Build self-identifies `v3.12.0-bandcut`. Expected `[RUNG-PLUG]` log lines all
  appear. My re-render of the author's three v11 shots is pixel-identical to
  `evidence/*_v11_*.png` — the rig is faithful and deterministic.
- **The user is not running the reviewed build.** `moebiusv2` main tip
  (`8447a66`, "Update moebius.js") is byte-identical to bundle commit
  `d2de270` = **v3.11.1-liveplug**, one commit before the final fix commit.
  Whatever the user saw, it predates the plug-depth-completion/fill changes.
  (This does not save v3.12 — see below — but the deployed/reviewed mismatch
  must be fixed before any further iteration.)
- Brief claim C6 ("the harness only exercises the direct scene-render path")
  is **wrong in one important respect**: `scratch_moebius.html` ships with
  `useInpaintingCheckbox` CHECKED and method=pullpush, so the author's v11
  evidence and all renders here DO run the full live composite
  (clean pass → gap pass → FG-subtraction → pull-push pyramids →
  `finalCompositeMaterial`). The harness does not, however, exercise resizes,
  zoom, vertical offsets, other assets, or the debug-sheet paths.

## 1. Defect list

Severity scale: **P0** = violates a hard acceptance criterion in normal use;
**P1** = violates a criterion in reachable-but-narrower conditions;
**P2** = quality/robustness defect.

### D1 (P0) — Rest render is not pixel-faithful: silhouette-wide changes at zero offset
- **Repro:** Starwatcher, offset (0,0), BG layer on + cut armed (default state
  after Build BG Layer) vs pristine app (BG off, cut off). Same pipeline both
  sides.
- **Evidence:** `review/evidence/sw_AN_T1.png` (red = pixels changed >8/255):
  **17,637 pixels differ inside the visible image (14,037 by more than
  30/255)** — ~5.5% of the image area, hugging every silhouette; the staff
  column above the head and the glider are wholly altered — precisely the
  criterion-6 erosion cases the author claimed to have protected (claim C3
  refuted at pixel level).
- **Root cause:** two compounding mechanisms.
  (a) The BG plug is opaque over band ∪ 4px cut ring ∪ occluder rind
  (moebius.js:7538-7545) and sits only 0.004 displacement behind the FG
  (7719). Anywhere the 8-bit-quantized, pyramid-diffused rind depth
  (7396-7403) or the LinearFilter-interpolated plug texture (7423) rises above
  the FG's own depth, the plug wins the z-test at rest and paints wash over
  real pixels.
  (b) With the plug present in the gap-generator pass, silhouette pixels that
  used to classify as gaps (and be re-inpainted identically in both renders)
  now take the plug/original branch of `finalCompositeMaterial`
  (5153-5156) — the composite arbitration itself changes rest pixels.
  **Attribution renders isolate both mechanisms and BOTH fail independently:**
  plug-only (BG on, cut disarmed) changes **16,950** interior rest pixels;
  cut-only (BG hidden, cut force-armed — the only delta vs pristine is
  `u_useBandCut=true`) changes **14,827**. The damage maps
  (`sw_AN_T1_plugonly_c.png`, `sw_AN_T1_cutonly_c.png`) are nearly identical:
  silhouettes, staff, glider, seated group, and the entire ground↔sky
  horizon band. The cut's foundational invariant — "at rest nothing is
  stretched, so nothing cuts" (comment at 6455-6459) — is empirically false:
  the mismatch trigger fires at rest on slow-ramp cliffs inside the band
  (the `fwidth < bgBandCutMaxGrad` gate passes exactly where the ground
  ramps gently into the horizon, and 8-bit live-baked depth plateaus give
  |sampled − interpolated| > 0.01). Same pattern on the certified Frazetta
  asset: plug-only 6,240 px, cut-only 2,973 px changed at rest.
- **Criteria violated:** 6 (and 2 — the plug affects pixels far outside
  disocclusions).

### D2 (P0) — Band cap starves the plug: reveals open onto featureless rind wash
- **Repro:** Starwatcher +0.11; visible as the broad pale wash right of the
  figure in `sw_v11_right.png` / `review/evidence/sw_comp_r11.png`.
- **Quantification:** by the app's own parallax LUT (bgDirectionalPlug,
  6541-6555), the per-edge grow budget before the cap is median **46 px**,
  p90 **66 px**, max 118 px at 1920-wide Starwatcher — but
  `bgBandMaxGrowPx = 28` (6441) truncates **84%** of all seeded edges
  (silverwarrior: 89%, frazetta: 51%). The directional fill (reflect/
  smooth, 7496-7522) only exists inside the band; everything past 28px falls
  to the occluder-rind wash (smoothBase, 7542-7545): a featureless diffusion
  blur ~3x wider than the band. The "fill" the viewer actually sees at ±0.11
  is mostly rind, not fill — hence "extends well beyond a tight silhouette
  strip and reads smeary" (author's own §5 admission, now with a cause).
- **Criteria violated:** 1 (wrong content at local depth), 3-in-spirit
  (wash reads as smudge), 8 (the coarse path's own standard).

### D3 (P0) — 45–92% of real occluding edges never seed a band at all
- **Repro/quantification:** classify every pixel whose max 4-neighbour depth
  drop exceeds 0.04 (a genuine occluding edge that opens a visible gap under
  parallax):
  | asset | edge px | drop 0.04–0.10 (NO band) | ≥0.10 (band) |
  |---|---|---|---|
  | starwatcher 1920x1323 | 18,974 | **61%** | 39% |
  | silverwarrior 3000x3000 | 58,401 | **92%** | 8% |
  | frazetta 851x1023 | 4,458 | **45%** | 55% |
  (`bgBandStep = 0.10`, 6446; seeds at 6550-6555.)
- **Consequences:** for every sub-threshold edge there is **no cut** (streak
  smears exactly as pre-fix), **no plug fill** (or the old screen-space fill
  paints its blue smudge/dark-ink chunks — visible at the seated group,
  tents, vehicles, crystal-mountain rim in `sw_comp_r11/u06/r18`), and **no
  rind exclusion**, so those occluders' colors DO feed `fillSrc`
  (7486-7491) and tint the fill — author's C5 suspicion confirmed. The
  author's own `band_after.png` shows the crystal mountain, tents and
  vehicles entirely bandless.
- **Criteria violated:** 1, 3, 5.
- **Note:** this is not fixable by lowering `bgBandStep` — the author raised
  it from 0.06 deliberately because low thresholds tile figure interiors with
  bands (comment at 6442-6446). Threshold-on-step cannot separate "soft
  silhouette" from "steep interior ramp"; that is a structural limitation.

### D4 (P0) — Vertical offsets (the user's actual head motion) are worse than horizontal, and were never tested
- **Repro:** Starwatcher y=+0.06 (`review/evidence/sw_comp_u06.png`): the
  seated group half-obliterated by wash; smears along the horizon; dark
  chunks at silhouette bottoms. Mixed x+y (`sw_comp_r11u06.png`): black
  ribbon smears hanging from the birds/star; wedge washes at shoulders.
  y=-0.06 similar (`sw_comp_d06.png`).
- **Root cause:** the band math is isotropic, but horizontal cliffs
  (object↔ground junctions) have systematically softer depth steps (ground
  ramps) → D3 bites harder; and the ground-side band budget is computed from
  the LUT'd depth delta which is small across ground junctions → 4-6px bands
  against 20-40px vertical reveals.
- **Criteria violated:** 1, 3, 4 (author claim of isotropy unproven and
  effectively false in outcome).

### D5 (P1) — Beyond ±0.11 the render collapses; margin runs out at the slider default
- **Repro:** x=0.18 (`review/evidence/sw_comp_r18.png`): smeared gray "ghost
  tower" under the star, filament streaks, black blobs at the seated group —
  and a naked black band at the right frame edge: the extension margin is
  sized from the auto-sweep sliders (45/400 = 0.1125 world units, 7595-7604),
  so any head excursion past the slider default exhausts the fill.
- **Criteria violated:** 3, 7.

### D6 (P1) — The cut's thresholds are bound to build-time canvas width; zoom/resize invalidates them
- **Code:** `u_bandCutUvRate = bgBandCutStretchFrac / max(1, w)` computed ONCE
  at arm time from `renderer.domElement.width` (7464); `bgBandCutMaxGrad`
  compares `fwidth(vNormalizedDepth)` against a constant (1270).
  Zoom in ≥ ~3.3x and unstretched band fragments drop below the uvRate
  threshold — the cut fires at rest inside the whole band (staff/glider
  erode); zoom out and real smears stop triggering. Rebuilding the layer
  re-arms, but nothing re-arms on camera zoom or canvas resize.
- **Empirical:** at 2.5x zoom-in (camera z 0.2 → 0.08) rest-state interior
  damage grows from 17,637 to 20,796 px (>8/255) — trend confirmed; the
  uvRate margin math says the cliff is at ~3.3x, where the whole band cuts
  at rest.
- **Criteria violated:** 6 (conditional), 3 (conditional).

### D7 (P1) — Thin features tear at offset: white speckle holes near the staff
- **Repro:** author's `sw_v11_left.png` (white speckles by the staff, ragged
  left silhouette). Mechanism: for a 1-3px-wide feature the band+rind cover
  its whole body; the cut discards its stretched edge cells; the plug behind
  carries 8-bit-quantized diffused depth (7396-7403) that LinearFilter blends
  across the feature — locally the plug lands in front of/behind the feature
  per-texel, alternating cover/hole per scanline → speckle. (Also the source
  of the "hairy" horizontal filament edges on the plug silhouettes in
  `sw_v11_bg_right.png`: per-seed budgets differ row to row, 6555, so the
  band frontier is a comb.)
- **Criteria violated:** 4, 6.

### D8 (P2) — Composite/FG-subtraction interplay is unsound with the plug active
- The depth pass's own tunnel detection is dead code: it samples
  `u_depthMap`/`u_texture` (4828-4829, 4876-4887) which are NEVER present in
  the shared uniforms (`depthMat.uniforms = object.material.uniforms`,
  4821 — the material has `displacementMap`/`map` instead), so
  `sourceRange`=0 and the three tunnel strategies (4894-4925) never fire.
  Rubber-sheet stretches therefore read as valid geometry in
  `screenNormalizedDepthTarget`, and `runFGSubtraction`'s gap seeding
  (5346-5348) sees gaps only where the color pass discarded — which, with
  the plug opaque underneath, is nowhere near the reveal. At large offsets
  the contract degenerates exactly as the user's debug sheets show
  (all-blue contract / all-white gap mask). Captured live:
  `review/evidence/sw_fgexcl_r11.png` — at +0.11 the red "FG occluder"
  marking floods the whole lower third of the frame (flat dune included)
  and half the mountain; blue "true gap" floods the margins and a displaced
  ghost of the figure.
- `renderPrimaryPass` (8028) is confirmed dead code.
- The plug is invisible to the depth pass BY DESIGN (4808-4813) but visible
  to the color/gap pass — the two passes describe different scenes, and
  `finalCompositeMaterial` (5138-5188) arbitrates between them per-pixel
  with heuristics (`u_bgLayerActive`, 5153) that change rest-state pixels
  (see D1b).

### D9 (P2) — Fill texture ≠ scene texture (starry sky), 8-bit plug depth, sRGB round-trip
- Even where geometrically correct, `bgFillMode='smooth'` produces a wash
  that cannot match star-field/ink texture (author's §5 concession; criterion
  3-in-spirit). The SD plate is the declared answer; nothing in the live path
  bridges the gap.
- Rind + margin depth pass through `bgPullPushFill` as 8-bit gray
  (7396-7403, 7622-7634): visible banding in the plug geometry under raking
  parallax.

### D10 (P2) — Claim C2 ("BG plug alone is streak-free, no figure colors") is false
- `sw_v11_bg_right.png` (author's own evidence) and my `sw_bg_r11.png`:
  the plug silhouettes have comb/filament edges (D7) and the fill regions
  carry figure-adjacent tints where sub-threshold occluders fed `fillSrc`
  (D3). T3 measurement: the plug-affected region is systematically paler
  than the adjacent sky (mean +12 luma) — the contamination mode on this
  asset is brightness, not hue.

### D11 (P0) — Fill-source starvation on dark palettes: opaque black blobs
- **Repro:** Frazetta (the CERTIFIED asset), +0.11x (`review/evidence/
  fr_comp_r11.png`): solid black blobs along the troll and dancer
  silhouettes; more at -0.11 and +0.06y.
- **Root cause:** `fillSrc` requires `lum >= 45` (7487-7488, the "dark ink"
  exclusion). On a painting whose background IS dark, this excludes most
  real background from the fill sources; the pull-push and directional
  fills then produce near-black; `bgFillSolid` makes it fully opaque. The
  no-naked-hole guarantee (C4) is honored by painting opaque nothing.
- **Criteria violated:** 1, 3 (and 4 in spirit).

## 2. Pixel-test results (T1–T4)

Canvas 860x484; "interior" = pixels showing image content in the baseline
render (pillarbox/margin counted separately, since scene extension fills it
by design). Starwatcher unless noted.

**T1 — rest fidelity** (composite w/ plug+cut vs pristine app, offset 0):
| condition | interior px >8/255 | >30/255 | margin px added |
|---|---|---|---|
| rest, normal zoom | 17,637 | 14,037 | 108,750 (by design) |
| rest, 2.5x zoom-in | 20,796 | 17,241 | — |
FAIL against criterion 6 ("pixel-faithful at rest"). Damage map:
`sw_AN_T1.png` — silhouette bands everywhere, staff column and glider wholly
inside the changed set.

**T2 — hole scan** (interior fully-transparent px):
0 at every pose tested (0, ±0.11x, ±0.06y, 0.11x+0.06y, 0.18x, zoom center,
zoom+0.05x). PASS — the no-naked-hole guarantee holds in this envelope
(see C4 note: coverage is largely BY THE RIND WASH, not by fill).

**T3 — FG contamination in the plug-affected region** (+0.11x; region =
pixels the plug changed vs the pristine pipeline at the same pose, 21,222 px):
mean color (81,119,156) vs adjacent background (69,105,147) — the fill is
systematically PALER/brighter than the sky it must match; warm-hue fraction
1.5% inside vs 5.1% outside (no net warm-figure tint at this offset on this
asset — the visible contamination mode is the bright wash, plus the dark
ink chunks documented in D3, which come from the sub-threshold-edge path).

**T4 — streak/texture metric** (same region): mean |grad| inside = (9.5,
12.1) vs (16.9, 16.8) in the surrounding background — the fill carries
~40% less texture energy than the sky it continues (reads as smudge), with
mild vertical anisotropy (gy/gx = 1.26) matching the horizontal-filament
comb edges.

**Second asset — Frazetta (851x1023, the certified asset), reduced matrix:**
- T1 rest: **6,271 interior px changed (4,051 by >30/255)** — criterion 6
  fails on this asset too (`fr_AN_T1.png`).
- T2: 0 transparent holes at 0/±0.11x/+0.06y — BUT `fr_comp_r11.png` shows
  multiple solid BLACK BLOBS along the troll and dancer silhouettes: the
  fill is opaque yet content-free. Root cause: on a dark palette the fill
  source rule `lum >= 45` (7488) excludes most of the painting from
  `fillSrc`, so the band/rind fill starves and paints near-black. Criterion
  4 passes only on a technicality; visually these are holes.
- T3 on Frazetta shows the OTHER contamination mode, quantitatively: the
  plug-affected region is WARMER than its surroundings (warm-hue fraction
  16.6% vs 12.2%) and carries MORE gradient energy (gx 19.5 vs 13.5,
  horizontal-biased = smeared strokes) — figure color in the fill, C5
  confirmed by measurement on a second asset.

**Third asset — silverwarrior (3000x3000), reduced matrix:**
- T1 rest: **13,078 interior px changed (10,170 by >30/255)** — criterion 6
  fails on all three assets tested.
- T2: 0 transparent holes (0, ±0.11x, +0.06y).
- The +0.11 composite (`sv_comp_r11.png`) shows the ORIGINAL failure mode at
  full strength: a full-height column of 1-D horizontal ribbon streaks down
  the warrior's right side, essentially untreated — as predicted by the
  band-coverage numbers (92% of this asset's occluding edges are below the
  0.10 seed threshold; of the 8% that seed, 89% hit the 28px cap). T4
  concurs: gradient anisotropy gy/gx = 1.46 in the affected region
  (horizontal striping) vs 1.00 in the surrounding background.
- **The plug's operating envelope simply does not include this asset.**

## 3. Claims scorecard

| claim | verdict |
|---|---|
| C1 "±0.11 opens onto clean smooth fill, no streaks" | **REFUTED** — reproduced author's own renders; wash + filaments + dark chunks at +0.11; worse at -0.11/vertical. |
| C2 "BG plug alone streak-free, no figure colors" | **REFUTED** (D10). |
| C3 "rest intact, no staff/glider erosion" | **REFUTED at pixel level** (D1). |
| C4 "cut can never open a naked hole" | **HOLDS in the tested envelope** (T2: zero interior transparent px at all 9 poses tested, up to 0.18x), but only because the opaque rind is 3x wider than the band; the guarantee is coverage-by-wash, not coverage-by-fill. Speckle tearing (D7) still punches visual holes via z-fighting, not alpha. |
| C5 "fill contains no FG color" | **REFUTED as suspected by the author** (D3). |
| C6 "verified headless" | Harness runs the full composite (contrary to the brief's premise), but only Starwatcher, x-only, one zoom, one canvas — D4/D5/D6 all live outside that envelope. |
| C7 coverage | Confirmed: x-only ±0.11 was the whole tested space. |

## 4. Architecture verdict

**The current architecture cannot meet the contract with bounded fixes.**
The load-bearing defects D1–D4 are not parameter mistakes:

1. The **band** is a guess about how much of the occluder will be revealed.
   Any cap under-covers (D2); any threshold under-seeds (D3); growing it to
   cover honestly means "the whole occluder", at which point it is not a band.
2. The **cut** exists only because the FG is a connected rubber sheet. It is
   three screen-space heuristics (uvRate + mismatch + gradient gate) with
   build-time-frozen thresholds (D6), gated to the band (inheriting D2/D3
   false negatives), needing a 4px dilate, a 5px bleed, a disarm-on-toggle
   rule, and an opaque-rind backstop to be safe. The heuristic stack is the
   architecture telling you the geometry is wrong.
3. The **plug** must simultaneously be (a) invisible at rest, (b) exactly
   background under every possible reveal, and (c) 0.004 units behind a
   surface whose depth it must also match — with 8-bit diffused depth and
   bilinear filtering, (a) and (b) conflict at every silhouette (D1, D7).

### Recommended re-architecture (pre-torn FG over a complete BG plate)

- **Tear the FG mesh at depth cliffs, offline, at asset load.** The mesh is
  already 1 vertex/texel (MESH_DENSITY_FACTOR=1). Emit per-quad geometry
  (or an indexed mesh with duplicated verts along tear edges) and simply DROP
  the cliff-spanning quads (same cliff test as the band seed, on the baked
  depth). Rubber triangles then cannot exist: no stretch, no smear, no cut,
  no uvRate/mismatch/maxGrad/dilate/bleed/disarm machinery — delete all of it.
  A reveal is then an honest transparent hole from any angle, at any zoom,
  on any canvas.
- **Make the plug the "world without foreground": complete the depth and
  color under the ENTIRE occluder**, not a 28px strip. The code already
  contains everything needed: the bounded rind flood (7374-7406) becomes
  unbounded (flood to the far silhouette — it already carries rim depth and
  stops at `depth[j] >= rimV+0.06`); the fill becomes the existing pull-push
  over the full under-FG region; the SD plates (`dir_*`/`out_*`, already
  exported at 5959-5980) drop in as the detail path with EXACTLY this
  full-occluder mask. Band width, grow caps, and seed thresholds stop being
  correctness parameters (a low threshold that "tiles the interior with
  band" is harmless when the whole interior is completed anyway).
- **Then the composite simplifies**: the scene render is FG(torn) over
  BG(complete); screen-space inpainting remains only as a fallback for
  assets with no built layer; the FG-subtraction contract and its dead
  tunnel heuristics (D8) stop being load-bearing.
- Migration risk is bounded: geometry construction (one function), plug
  completion (relax one bound), config deletion. The per-quad mesh doubles
  vertex count at worst (or use flat/nearest displacement sampling per quad);
  if that's too heavy at 3000x3000, decimate flat regions — tearing makes
  LOD safe because seams no longer smear.
- **Alternative considered and NOT recommended as first move:**
  depth-segmented multiplane layers (MPI-style; app already supports layers).
  Sound, industry-proven, and the SD path fits it — but it forces a global
  depth quantization decision per asset and a bigger renderer change. The
  pre-torn sheet keeps the current continuous-depth pipeline intact.

### If you must ship a stopgap on the current architecture
(smallest first; none of these reach the contract, they only shrink misses)
1. Deploy the actual v3.12.0-bandcut to main (the user is on v3.11.1 — §0).
2. Raise `bgBandMaxGrowPx` 28 → ~70 (p90 of demand) and re-tune the rind to
   2x; re-verify D1 first — this widens the wash (D2 trade, does not fix it).
3. Re-arm `u_bandCutUvRate` on every resize/zoom change (fixes D6 cheaply).
4. Fix the dead `u_depthMap`/`u_texture` bindings (D8) so tunnel detection
   actually runs before anyone tunes it again.
5. Margin: size from a hard max-excursion constant, not the sweep sliders
   (D5).

## 5. Reproduction inventory

- `review/harness-additions/`: `review_drive.js` (render matrix),
  `review_analyze.js` (T1–T4), `review_bandcov.js` (D2/D3 quantification),
  `review_attrib.js` (D1 attribution), `review_debug_shots.js` (composite
  audit), `review_chain.sh`.
- `review/evidence/`: all renders + analysis masks referenced above.
- Setup: clone moebiusv2 @ f79bae2, pull bundle, copy `harness/`, symlink
  `moebius.js` + asset PNGs into `harness/`, swap `defaultImg*` per asset,
  `node review_drive.js <prefix> [basic]`.

## Addendum (post-review, from the user's live v3.12.0 debug sheets)

The user's own debug sheets (cam ~(0.12-0.13, -0.04..-0.06, 0.2), live=bake)
give the cleanest confirmation of D1/D2/D7's shared mechanism:

- The "COMPLETED DEPTH (plug)" panel still shows the figure at NEAR depth:
  the depth completion carves only a ~84px rind (3x bgBandMaxGrowPx) into
  the occluder (7375), so past the rind the plug's displacement map reverts
  to foreground depth. The completion RELOCATES the plug's cliff 84px
  inward; it does not remove it.
- The BG plug mesh is itself a connected rubber sheet with NO cut. At the
  rind's inner boundary it stretches from background depth up to foreground
  depth — visible in the user's `view=final` sheet as an opaque dark
  doppelganger standing beside the figure ("the plug protruding from the
  background and intruding toward the foreground"), and in "live depth
  incl. BG" as a figure-shaped slab at intermediate/invalid depths.
- Unbounding the rind flood is NOT a safe fix: its continuity gate
  (depth >= rim+0.06, 7387) leaks through the figure's ground contact into
  the whole near ground (the author bounded it for exactly this reason,
  7369-7371). Removing the interior cliff correctly requires an actual
  FG/BG segmentation of each occluder — i.e. the "world without
  foreground" plate of §4.
- The user's third sheet (same build, near-identical pose as the second)
  shows the D8 total collapse — gap mask all white, FG-sub contract all
  blue, scene depth all red — while the second sheet is healthy. The
  collapse is BISTABLE at a fixed pose: state/frame-ordering dependent,
  not pose-dependent.

## Addendum 2 — "the directional plug grows the wrong way" hypothesis: REJECTED

Hypothesis raised post-review: the growth rule `depth[j] >= rim[i]+STEP`
walks into the FOREGROUND, and the physics demands growth into the
background. Tested and rejected:

- The plug is a SOURCE-SPACE layer. The background a head-move reveals is,
  in source space, the background hidden UNDER the occluder's silhouette —
  an LDI back layer. Band texels under the figure displace at rim depth, so
  they parallax WITH the background and are already in the gap when the
  figure slides off. Growing into the background instead would duplicate
  already-visible content and leave NOTHING behind the figure — every
  reveal would open onto void.
- Empirical: T2 = 0 naked holes at all 9 poses exists BECAUSE the band is
  under the figure; `band_after.png` shows fill coverage correlating with
  under-figure band presence (figure filled, bandless mountain streaks);
  the app's own seam metric (`sw_plugerr_r11.png`) shows green continuity
  where band exists.
- The real defect behind "the plug's boundary is figure-shaped and
  parallaxes wrong" is the INTERIOR CLIFF (Addendum 1): past the bounded
  rind the plug reverts to foreground depth and the uncut BG rubber sheet
  climbs it. Growth direction is correct; completion extent is not.
- The proposed revert to `buildPlugFromValid` + PNG masks only functions on
  the certified Frazetta asset: `defaultBgBand/Valid.png` are 851x1023
  troll-specific masks, and legacy mode stretches them onto whatever asset
  is loaded (7334-7335). On Starwatcher that is the troll's band on the
  wrong painting. Viable as a certified-asset regression baseline only.

**Fix implemented on `review-fix` (moebiusv2) for verification:** the
completion set becomes rind-flood ∪ Otsu-near side (global depth split,
`bgOtsuThreshold` already in-file), so the plug depth is completed to
background under the ENTIRE occluder. Diffusion sources remain background +
pinned rims only — the completed plug is a convex combination of those and
therefore can never be nearer than the local background ("plug sits
at/behind the furthest visible background", the user's invariant, by
construction). Verification results below.

### Addendum 2 verification results (branch `review-fix` in moebiusv2, patch: `review/moebius-otsu-completion-pretear.patch`)

Two changes verified together on Starwatcher (8-shot matrix incl. the
user's doppelganger pose (0.123, -0.055), vertical offsets, and rest):

1. **Otsu full-occluder depth completion** (`completion set: otsu>=0.391
   adds 278,930px`): the doppelganger at the user's pose is GONE
   (`review/evidence/fx_userpose.png` vs the user's debug sheet). No
   regression at +-0.11x, +-0.06y, or the bottom margin from burying the
   near ground (`ft_comp_d06.png`). T2 stays 0 holes at all poses.
2. **Pre-torn FG** (`fgPreTear=true`, `fgTearStep=0.06`): 29,064 of
   5,073,836 triangles dropped (0.57% — silhouettes only). Rubber-band
   triangles no longer exist; the band-gated cut and its three screen-space
   heuristics stay disarmed. Rest-state cost of the tear itself: **+137 px**
   vs the untorn pristine (slits are sub-pixel and land on the plug's bled
   fill) — the tear is effectively free at rest, and it is zoom/resize/
   canvas-independent by construction (retires D6's failure mode).

Honest negative result: **T1 rest fidelity does not improve** (17,774 vs
17,637 baseline, cut disarmed and all). With the plug isolated against the
torn pristine it still changes 12,520 rest pixels. Conclusion: D1's
dominant driver is neither the cut nor the plug geometry but the COMPOSITE
ARBITRATION — with `u_bgLayerActive`, silhouette pixels that the Sobel gap
generator flags take the plug-backed scene branch instead of the
screen-space inpaint branch of `finalCompositeMaterial` (5153-5188), a
systematic shift along every strong edge. Fixing criterion 6 therefore
requires a composite-side change (e.g. gap pixels prefer original color
whenever it is valid, regardless of plug state), not further mesh/plug
work. D2 (wash texture) and D3 (sub-threshold edges) also remain, as
expected — they are fill-side and seeding-side respectively.

**Roadmap note (user decision):** pre-torn FG ships first; depth-segmented
multiplane layers (MPI) are the agreed later step — the SD plate path and
the app's existing layer support are the natural substrate for it.

### Fix-iteration results (final state of `review-fix` = `moebius-otsu-completion-pretear.patch`, 287-line diff)

Iterations driven by the user's five observed defects at (0.123, -0.055)
(staff black/carved, glider blobs, dune transparency between the legs,
black at hill people, black behind mountains):

| build | change | outcome |
|---|---|---|
| v1 | Otsu global completion + naive tear | doppelganger GONE; but tear deleted thin features (staff carved, glider blobs), global-depth completion put SKY wash behind the LEGS (dune "transparency"), un-backed tears painted ink at mountains |
| v2 | per-edge rim flood (unbounded, Otsu floor) + plug-backed thin-protected tear | legs dune-colored past the band; mountains/hill-people revert to baseline (no black) |
| v3 | FULL-FRAME plate (opaque everywhere, source content 0.004 behind FG) | the structural fix for thin occluders: a 2px staff hides 2px of sky but sweeps ~25px — only a full plate can fill that reveal. Staff/glider ink-black GONE; mountain rim clean |
| v4/v4.1 | local rim COLOUR carried by the flood (band + completion, internal rims rejected, Jacobi-softened) + thin-feature 2px depth halo (geodesic thinness) | between-legs reveal now dune-pink; bright rim-dash artifact removed; staff renders rigid (faint at 860px harness scale) |

Final pixel tests (Starwatcher): T2 = 0 transparent holes at all poses;
T1 rest = 19,033 px vs untorn pristine (baseline 17,637) — rest fidelity
is still owned by the COMPOSITE ARBITRATION (unchanged conclusion: the
`u_bgLayerActive` branch of `finalCompositeMaterial` shifts Sobel-flagged
silhouette pixels; must be fixed composite-side).

Residuals, honestly stated: faint rigid-staff ghosting at harness scale;
a small horizon-blue remnant at the upper thigh; D2 wash texture != starry
sky (SD plate / MPI remains the answer); D3 sub-0.10 edges unchanged;
Frazetta/silverwarrior not re-run against v4.1. The MPI migration remains
the agreed endgame; the full-frame plate built here IS its back layer.

## Addendum 3 — companion docs reconciled; scalability; MPI shape

**Docs reviewed:** `HANDOFF.md`, `MOEBIUS_DISOCCLUSION_SPEC.md`,
`PLUG_PORT_SPEC.md` (repo root).

- `PLUG_PORT_SPEC.md`'s critical correction ("valid = ~fillset, not ~band —
  figure-pixel anchors extrude the plug to figure depth") is the same bug
  class as the interior-cliff/doppelganger fixed on `review-fix`; the
  unbounded local-rim flood with Otsu floor is the directional-path
  equivalent of that correction.
- **Law 3 amendment (important — do not "correct" this back):** the spec
  forbids any full-frame background surface because "the matte moves at a
  different rate than the floor it continues." That failure mode belongs to
  a FLAT matte at fixed depth. The `review-fix` plate is DEPTH-MATCHED
  (source depth everywhere outside occluders), so it moves at exactly the
  foreground's rate by construction; the mismatch cannot occur. Laws 1, 2
  and 4 are enforced more strictly than in v3.12 (rind exclusion +
  internal-rim rejection; welded local rims; rim-carried first pixels).
- Law-1 landmine kept masked by D3: the plate carries sub-Otsu occluders
  (tents, seated group) in source colours at their own depth. Safe while
  those edges neither band nor tear; if the tear threshold is ever lowered,
  those objects must be completed too (MPI does this per layer).
- `HANDOFF.md` is historical (v3.10.4 PNG-record plumbing), but its theme —
  right design, broken texture plumbing — is still live as D8 (unbound
  `u_depthMap`/`u_texture` samplers in the depth pass).

**Scalability (user requirement: weight-free, near-real-time on import,
depth/layers confirmable, then SD offline):** every stage in the shipped
pipeline is classical and weight-free (Otsu, BFS floods, erosion, chamfer,
pull-push, Jacobi, weighted-median bake), O(N)-ish, parallelizable; the
expensive work is once per asset, per-frame cost is one extra mesh draw.
Measured today (single-thread JS): ~15-20s at 1920x1323, ~60-90s at 3000^2.
Budget is dominated by four items with known cheap fixes: 120 full-res
Jacobi sweeps -> multigrid on the existing pyramid (~10-20x); the 4
extended-res pull-push runs of the margin -> quarter-res + upsample (~16x,
the wash is smooth by design); the 15M-entry tear filter -> worker + per-
asset cache; all off the main thread. Realistic optimized import: **~2-3s
at 1920^2, ~5-8s at 3000^2**. The piece that does NOT scale is inherited:
the 1-vertex-per-texel mega-mesh (9M verts / ~430MB index data at 3000^2)
— which is precisely what MPI removes.

**MPI shape (agreed direction):** depth-DISPLACED layers, not flat planes —
each layer keeps {color, alpha, ITS OWN DEPTH MAP, completed content} and
renders as a (much coarser) displaced mesh within its depth slab. Parallax
stays continuous inside a layer (the ground ramp does not band); layer
boundaries exist only at occlusion boundaries, which is where completion /
SD fill lives; per-layer completed depth remains the ControlNet
conditioning input, as with today's dir_bg_depth_completed.png. Layer
correctness is confirmable at import with the same harness tests (T1/T2 +
plug_error per layer).

**Implementation state:** fixes v1-v4.1 are IN CODE on `review-fix`
(moebiusv2 @ fd65995). Not yet implemented: composite-arbitration rest-
fidelity fix (D1 residual), dead depth-pass sampler bindings (D8),
sub-Otsu occluder completion (D3), and the MPI migration.

## Addendum 4 — criterion 6 reframed; D8 resolved; v4.2

**Criterion 6 measured against the TRUE reference** (the brief says
"pixel-faithful to the source image"; T1 previously diffed against the
pristine APP). New reference render `rf_ref_c.png` = bare mesh, no gap
generators, no inpaint, no plug. At rest, >30/255 deviations from source:
pristine app **31,586 px**, plug build **28,466 px** — the plug build is
CLOSER to the source than the pristine app. The rest-frame alteration was
never plug damage: the shared pipeline (Sobel gap detection + pyramid
inpaint) reprocesses every silhouette even at rest, and the full-frame
plate actually improves fidelity by backing those pixels with real source
content. D1 reduces to an inherited pipeline property; the principled
remedy, if desired, is gating gap-generation/inpaint on head-offset
magnitude (at rest there are no disocclusions by definition).

**D8 resolution:** the dead samplers are fixed (renamed to the bound
`displacementMap`/`map`), but the resurrected tunnel heuristics MISFIRE on
real data (striping at the dune/vehicle line) and are obsolete under the
pre-torn FG — they are now explicitly disabled with a comment, which is
behaviourally near-neutral (3,055 px vs the prior build) and leaves the
depth pass honest instead of accidentally dead.

**v4.2** (`review-fix` @ b6f2853): completion pass 2 floods sub-Otsu
occluders (seated group, sled, tents; +13,396 px on Starwatcher) — their
colours no longer sit on the plate, killing the dark scallops / stripe
stacks beside them (`crop2_tn_shot.png` before vs `crop2_tn3_shot.png`
after); rim-colour smoothing raised to 24 passes (Voronoi comb along busy
silhouettes). Residual: a softened comb at the far-left dune crest.

## Addendum 5 — v4.2 cross-asset validation (Frazetta, silverwarrior)

Full 8-shot matrix per asset on `review-fix` @ b6f2853:

| asset | T2 holes (4 poses) | T1 rest >8/255 (vs v3.12 baseline) | headline change at +0.11 |
|---|---|---|---|
| frazetta 851x1023 | 0 | 7,805 (6,271) | **all D11 black blobs GONE** — carried rim colours sidestep the lum>=45 fill starvation on the dark palette (`fr2_comp_r11.png`) |
| silverwarrior 3000x3000 | 0 | **8,268 (13,078 — improved)** | **the full-height ribbon-streak column is GONE** (`sv2_comp_r11.png`); residual mild smears only at sub-0.10 edges (D3, untreated) |

Mechanism sizing per asset (self-reported): frazetta tear 7,277/1.74M
triangles, pass-2 +313,365px (36% of frame — the dark cave's continuous
depth; no visible damage, plate under unrevealed areas is invisible);
silverwarrior tear 78,021/18.0M, pass-2 +12,282px. The v4.2 pipeline
self-scales across a 12x resolution range with no per-asset tuning.

Cross-asset residuals: sub-0.10 edges still smear mildly everywhere (D3 —
the seeding-threshold structural limit; MPI layer extraction is the fix);
wash texture vs painterly detail (SD plate's job); build time on the 3000^2
asset remains ~1-2 min unoptimized (see Addendum 3 budget).

## Addendum 6 — depth-composite audit (user acceptance pass on DEPTH, not colour)

Requested check: depth composites per asset; no unplugged holes, seamless
welds aligned to the attached surfaces, no depth intruding toward the
foreground. Tool: `depth_dump.js` (depth pass with plug included, magenta =
unplugged). What it found, in order of discovery:

1. **The bake corrupts the depth input** (root cause of most of what the
   composites showed; predates this session — visible in the user's own
   v3.12 sheets). Three distinct damage modes in `bakeEdges`' output, each
   now fixed in `applyLiveBake`:
   - dark/thin NEAR features eroded to far (staff shaft perforated) →
     **plateau clamp** (a pixel on its local near plateau never moves far);
   - a 1-2px **pepper skin** of intermediate values along every silhouette
     (11,209px on Starwatcher) → poisoned the plug's rim depths (mid-gray
     slabs floating in reveals = "depth intruding toward the foreground")
     and shredded the tear → **skin binarization** (skin pixels snap to
     local near-plateau or far-min);
   - tear decisions moved to the RAW pre-bake depth.
2. **Canvas depth textures replaced by Float32 DataTextures** (sharpened +
   halo): browser canvas-upload colorspace conversion risk gone, no 8-bit
   displacement quantization (retires the D9 quantization residual), and
   the FG and plug read one depth space.
3. Tear gates refined: background-backed cliffs only (internal FG-on-FG
   overlaps keep rubber — a single plate texel cannot hold both the local
   far surface and the deep background; the MPI argument in one sentence),
   and a 3px no-tear zone around thin features.

**Post-fix composite state (Starwatcher `swm_depth_c/r11.png`):** rest
figure SOLID (hood, torso, staff+loop, glider, seated group); zero
unplugged holes at all poses; +0.11 reveals weld to true sky/dune depth
(mid-gray slabs gone). In colour at the user pose (`clr_shot.png`) the
staff renders RIGID with its loop for the first time.

**Remaining depth residuals, honestly:** bright FG rubber FILAMENTS in the
reveals from protected thin features and halo edges — colour-invisible by
design (sky-over-sky) but present in the depth channel; a small mottled
patch right of the torso and bottom-edge striping in colour. The
depth-pure fix is tearing halo-edge triangles whose near side is halo-only
(raw-far) — colour-safe by construction — or, definitively, MPI. Frazetta/
silverwarrior depth composites (`frd/svd_depth_r11.png`) predate the
binarization fix and need a re-run for the record.

## Addendum 7 — final per-asset depth composites; two source depth-map defects on record

Final build (`review-fix` @ 23e6a8f): depth composites at rest/+0.11/user
pose for all three assets (`swm_*`, `fr2d_*`, `sv2d_*` in evidence/).

- **Starwatcher**: rest figure solid; zero unplugged holes at all poses;
  reveals weld to true local depth (nearest-rim-first flood — far fronts no
  longer claim ground contacts, so the plate under the legs is dune, not
  distant plain). Staff rigid in colour. Residual: thin-feature rubber
  filaments in the depth channel (colour-invisible).
- **Frazetta**: coherent cave/troll surfaces; the dancer's reveal opens
  onto the dark passage correctly; residual edge filaments at her
  silhouette. No holes, no floating slabs.
- **silverwarrior**: no holes, no slabs; reveals carry near-depth filament
  fuzz from its 92% sub-0.10 edges (untorn rubber, the D3 residual).

**Source depth-map defects identified (upstream of any plug):** (1) the
lamp glow is painted at SKY depth — off-axis it detaches from the staff;
(2) the dune-crest colour boundary behind the figure has NO depth step
(smooth ramp), so the pink/blue split inside leg reveals cannot be placed
exactly by any depth-driven fill. Both belong to the depth-regeneration /
SD / MPI stage. Open fill-side items: lamp glow-attach preprocess
(optional), bottom-frame margin striping at look-up poses.

---

## Addendum 8 — bottom-frame margin striping: fixed (commit `168508e`)

**Symptom.** At look-up poses (e.g. 0.123, −0.055) the dune's bottom
silhouette lifts off the frame edge and the revealed strip along the bottom
was a blue/gray gradient band with vertical striations and a black patch at
the bottom-left corner — nothing like the pink sand that should continue
below the frame. Evidence: `evidence/margin_striping_before.png`.

**Root cause.** The scene-extension (outpaint) margin seeded its pull-push
diffusion from the PLATE (`fillRGB` / `plugDepth`) — the world-*without*-
foreground. At the bottom of the frame the plate is the inpainted content
*behind* the dune: distant-sand blues, contact-shadow grays, starved blacks,
and the fill flood's striations. Diffusing that outward put occluded-world
colours at FAR depth in the margin, so under parallax the strip held still
(far ≈ no shift) and stayed exposed as an off-colour striped band.

Physically, a beyond-frame reveal shows the FRONT world continuing past the
frame: below the bottom edge there is more near dune, and near content
parallax-slides *with* the FG silhouette, closing the gap by itself.

**Fix (two parts, both in the scene-extension block):**
1. **Margin seeds = source colour + front-surface depth** (`cpx` / `depth`
   instead of `fillRGB` / `plugDepth`). The bottom skirt becomes near-depth
   pink sand that slides up with the dune edge and covers the reveal; the
   top margin becomes sky at sky depth; sides continue their local edge
   content. The centre keeps plate content unchanged.
2. **3-texel WELD ring.** After part 1 a thin dark seam line remained
   hugging the silhouette (`evidence/margin_striping_mid_seamline.png`):
   the plate(far)→skirt(near) depth cliff sat exactly on the frame boundary,
   and its one-texel transition quad rendered as a fold wall textured with
   the plate↔skirt colour blend. The outermost 3 centre texels now take the
   same front-surface colour+depth, moving the cliff inboard where the fold
   is hidden behind the skirt. The ring is never legitimately visible as
   plate: the FG edge rows cover it at rest, the skirt covers it in reveals.

**Verification.** Look-up (0.123, −0.055): seam line and striping gone, the
dune dissolves into a continuous sand skirt
(`evidence/margin_striping_after.png`). Look-down (−0.123, 0.055): starry
sky continues past the top edge, no seam (`evidence/margin_lookdown_after.png`).
Rest: bottom-5-rows diff vs source 42/3510 px (sampling noise) — the ring
is fully covered by the FG at rest, as argued.

**Interaction with the SD plate.** `bgExtendExport` now carries the welded
margins; the outer ring welding to the source rim is the correct outpaint
conditioning too (continuation of the visible world, not the occluded
plate). Open fill-side items are now: lamp glow-attach preprocess
(optional) only.

---

## Addendum 9 — the "black blob" doppelgänger: fixed (commit `d651918`)

**Symptom.** A large dark-brown mass in the reveal beside the figure at
off-axis poses (user report: "huge black blob at the foreground astronaut
disocclusion"). Present at every recent pose render; depth there was
CORRECT (far), so it passed the depth-composite audit unnoticed.
Evidence: `evidence/doppelblob_before.png` / `doppelblob_after.png`.

**Attribution chain (all instrumented, no guessing):**
FG-only/BG-only renders put it on the plate → BG-only depth showed FAR →
CPU fill probe of the *expected* source region was clean sky → a UV-map
swap on the plate finally located the actual texels: source (564–619,
740–803), inside the figure's torso footprint, rendered 87px right of
rest by full far-plane parallax. Their fill path was `fb=3` — the flood's
*carried rim colour*, value (45,33,35), uniform across the whole patch.

**Root cause (a generality flaw, not a tuning problem).** The
nearest-rim-first completion flood carries DEPTH correctly, but its
colour rode along with territorial claim: a dark LOW rim — the figure's
horizon-contact ink — claimed plate territory far above its own height
and painted the sky behind the torso near-black. Any occluder standing
across horizontally-stratified background (sky/horizon/ground) can
reproduce this; it is foreground-adjacent ink smeared over background,
exactly the contract's colour-contamination clause.

**Fix — one rule, no new knobs.** Depth-consistent local continuation:
every completed pixel's colour must come from real background at the
pixel's OWN completed depth, found along its own row (preferred) or
column. Sky rows pull sky from either side of the occluder; the horizon
stripe continues itself; the under-leg dune corridor still pulls dune
(the earlier leg fix is a special case of this rule). Reuses the existing
0.06 depth tolerance and 400px march bound. The flood-carried rim colour
remains only as fallback when no depth-compatible background is in reach
— still never foreground. 376k of ~658k completed pixels recoloured on
starwatcher; fill stage 2.0s → 5.5s at 1920×1323.

**Verification.** Starwatcher (0.123,−0.055): blob replaced by continuing
sky/horizon/plain; leg corridor and staff unchanged. Same code, same
constants on the other two assets: Frazetta reveals carry cave-wall and
passage tones (`doppelblob_fr_after.png`); silverwarrior reveals are
sky/mountain whites (`doppelblob_sv_after.png` — its horizontal streaks
are the documented D3 sub-threshold fur-edge rubber, colour-clean).

**On generality (user concern, on record).** No per-image constants were
introduced in this or any review-fix commit. The mechanisms are:
parallax-budget band growth, nearest-rim-first depth completion,
depth-consistent colour continuation, front-surface margin seeding,
pre-tear on plug-backed cliffs. The two Otsu uses (thin-feature
protection, flood floor) are self-computed per image, not hand-set. The
remaining hand constants (0.06 depth tolerance, 0.10 tear step, 28px band
cap, 400px march) are shared across all three test assets unchanged.

---

## Addendum 10 — depth filaments, soft-cliff rubber, and the streaks (commit `2a40a45`)

The user pointed at the streak block in the depth composites and named the
mechanism: stretched pop-out pixels made transparent at glancing angles.
Confirmed — the FG's band-gated stretch cut is disarmed under pre-tear, but
`renderNormalizedDepthPass` has its own fwidth discard heuristics that chop
any SURVIVING stretched wall into dash-row streaks. The fixes attack the
walls themselves:

1. **Halo-edge tear.** The thin-feature ribbon (feature + depth halo) stays
   rigid; the triangles spanning its outer boundary — the colour-invisible
   depth-channel filaments — are detected in the DISPLAYED (haloed) depth
   (raw has no step there) and dropped when backed by far plate. Unlike the
   earlier reverted halo-ring tear, the ribbon itself is never eaten.
2. **Soft-cliff core tear.** The bake spreads some silhouettes into 3–10px
   ramps whose per-triangle span never exceeds `fgTearStep` — the mesh
   rubbers instead of tearing (silverwarrior's fur streaks, D3). A ±2px
   window span finds the ramp; gradient non-maximum suppression tears only
   its steepest 1–2px core, so the rest-state gap stays sharp-cliff thin.
3. **Source-depth despeckle.** Soft mid-depth blobs floating over the far
   field (sparkle haze) sit below every tear detector. Boundary-soft
   raised components (ink-edged objects are rim-sharp and kept; big
   regions capped) attach to a thin carrier, stay if leaning on a body,
   flatten only if isolated. Footprint: 2.7k/0.4k/1.7k px on the three
   assets.

**The floating lamp (root-caused).** The source depth map contains the
raised staff and its ring beautifully — but NOT the light at its tip
(flat sky, both source and baked; probes on record). The light detaches
+65px at (0.123,−0.055). `bgGlowAttach` attaches emissive floor-depth
blobs to their thin carrier and provably fixes it (evidence:
`glowattach_on_staff.png` — lamp + full glow riding the staff; rest
fidelity IMPROVED, 1,359 vs 2,262 diff px). It ships **default OFF**:
four gating iterations (luma anomaly, thin carrier, 8px core distance,
bridged components) established that colour brightness alone cannot
separate detached lamp light from painted emissive background — frazetta's
cave shafts and silverwarrior's sunburst over-claim under every variant.
Missing-object depth belongs to the depth-regeneration stage; the flag is
there for lamp-type imports until then.

**Verification.** Starwatcher depth composite: boot/dune filaments reduced,
crisper silhouette (`filaments_before/after_depth_user.png`); the staff
shear-zone streaks that remain are the documented missing-light defect.
Frazetta: reveals cave-toned, no regressions (`filaments_fr_after.png`).
Silverwarrior: unchanged from baseline (`filaments_sv_after.png`).
Rest state: byte-equivalent to baseline (light box 2,264 vs 2,262;
bottom rows 42 = 42). All constants shared across assets, none tuned.

**Wide-reveal fill smearing (status).** The remaining coarse smear inside
wide reveals is the plate fill's textural quality (flat rim-consistent
colours + Jacobi, deliberately colour-clean). Its proper replacement is
the SD plate; a weight-free texture upgrade (depth-compatible reflection
instead of flat colour) is sketched but deferred — it trades smear for
mirror ghosts and needs its own evaluation round.

---

## Addendum 11 — the streaks, root-caused and removed (commit `cdb3a09`)

The user pushed back: streaks better, not gone. The instrumented hunt that
followed overturned two working theories before landing on the true one.

**Theory 1 (wrong): fragment-discard dashes.** `u_useDepthGrad` was
hard-on (`checked || true`) and shared with the depth pass — plausible
dash generator. Disarmed under fgPreTear (kept, correct hygiene) — the
streaks didn't move.

**Theory 2 (wrong): surviving kept-walls.** A CPU replica of the tear
decision per cell (`streaks_wallprobe.png`) showed the figure ringed by
far-mismatch walls — the far-side gate compared the plate to the RAW
triangle minimum, a mid-ramp value on every soft silhouette. Fixed
(displayed-depth minimum). Counts moved; the composite didn't.

**Theory 3 (right): terraced aprons.** FG-only depth attribution
(`streaks_fg_attribution.png`) showed the streak fields ARE the FG mesh:
the bake leaves 3–10px transition aprons along silhouettes, quantized
into terrace treads. Every tread is an intermediate-depth texel band
below `fgTearStep` — invisible to every tear rule by construction — and
under parallax each tread shears horizontally by its own depth. The
treads themselves are the streaks; cutting one line through the ramp
(the NMS core tear) left the rest connected and shearing.

**Fix — RAMP COLLAPSE.** Remove the intermediate depths, not more
triangles: every ramp pixel (±2px window span > `fgTearStep`) binarizes
to whichever side — window min or max — is closer in value. Aprons
become 1-texel cliffs; the sharp tear handles them; smooth real slopes
(span < step) are untouched; the bake's silhouette pepper collapses too,
so the tear's span tests moved from raw to the collapsed displayed depth
(which also made the far-side gate exact). 26k/14k/87k px binarized on
the three assets — silverwarrior's 87k is its fur pathology, now
collapsed instead of shearing.

**Result.** `streaks_before_collapse.png` → `streaks_after_collapse.png`:
the streak fields at the figure edge, boots and dune line are gone; the
silhouette is crisp. `streaks_after_color.png` is the cleanest off-axis
render of the session — the smudge field beside the figure vanished.
Frazetta and silverwarrior regression-free (`streaks_fr_after.png`,
`streaks_sv_after.png`, fur streaking visibly reduced). Rest state:
light box 2,284 vs 2,262 baseline px, bottom rows 42 = 42, full frame
+0.3%.

**Remaining (documented, bounded):** the eagle's interior micro-steps
(its own internal depth gradation, correctly kept — plate behind is sky,
not eagle-far); the missing-lamp shear zone (source depth defect,
`bgGlowAttach` opt-in or depth-regen); silverwarrior residual fur
streaks (reduced; full fix is per-layer plates in MPI).

---

## Addendum 13 — MPI slice 2: the under-sheet (commit `936535f`)

**The idea.** Everything the single backdrop plate cannot fix is INTERNAL
overlap — cliffs whose far side is another part of the scene stack (arm
over torso, fur over body, troll limb over cave), where one-depth-per-
texel holds the backdrop instead of the local surface. The under-sheet is
the second depth: the LOCAL LOWER ENVELOPE of the displayed depth — a
separable min filter over the parallax-budget radius — one coherent
smooth floor by construction. Sheet pixels exist where the front stands
above its floor and the backdrop does not already carry that floor;
colours are depth-consistent row-continuation at floor depth (sampling
any visible surface there — the sheet's far side IS figure-class
content); pixels with no continuation anywhere are pruned, because a
tiny far sliver's true next surface is the backdrop. The sheet renders
between plate and FG, and all three tear rules now accept it as backing
— internal cliffs finally have a surface to open onto: far-mismatch
rubber went from hundreds-to-thousands of kept walls to ~zero across
all three assets.

**Three intermediate designs failed and are recorded:** per-cliff
carried-depth BFS bands fragment into micro-terraces on clutter (fur) —
the streak problem reborn one level down; rim-ink fallback colours
painted dark slabs where no continuation exists; any-vertex mesh
inclusion created boundary triangles walling floor-to-front as
semi-transparent smears. Each was diagnosed from render evidence and
replaced by a structural rule, not a threshold.

**Verification (same code, same constants, all three assets).**
Starwatcher: overlap patches at the waist/arm clean — best MPI render of
the session (`mpi2_sw_pose.png`). Frazetta: the dancer-adjacent slab
gone, reveals cave-toned (`mpi2_fr_pose.png`). Silverwarrior: identical
to its own MPI-OFF baseline (`mpi2_sv_pose.png` vs
`mpi2_sv_baseline_off.png`) — the remaining fur smear is the documented
D3 pathology, present with the sheet disabled, and needs strand alpha
matting (SD-stage), not more geometry. Rest state: the sheet is
invisible (fringe-class diff unchanged from slice 1: 66,531 vs 66,426).

**"One button" audit (user requirement, on record).** Slice 2 introduces
ZERO new constants: it reuses `fgTearStep`, `bgBandMaxGrowPx` (as the
floor radius), the 0.06 depth tolerance, the 400px march bound, and the
plate's 24-pass Jacobi. Nothing was set differently per asset at any
point in slices 1–2. Activation is a single switch (`bgMPIMode = true` +
rebuild); its one integration caveat — enable after load, not during the
import auto-build (view-fit interaction, Addendum 12) — is a wiring bug
to fix alongside the real UI toggle, not a tuning knob.

---

## Addendum 14 — performance pass: 137s → 43s, bit-identical (commit `478a3e9`)

Instrumented every build stage, then applied ONLY exactness-preserving
optimizations — no thresholds touched, no behaviour changed, and the
proof is mechanical: the MPI-off rest render remains bit-identical to
the pre-MPI baseline (0 of 416k px), and the MPI-on pose render is
bit-identical to a re-run of the OLD code (0 px; the 143px seen against
the archived shot reproduces exactly with the old code re-run — GPU
run-to-run noise, not the optimizations).

| stage | before | after | technique |
|---|---|---|---|
| continuation marches | 67.8s | 3.9s | skip tables across the completed set |
| main Jacobi (24-pass) | 15.6s | 10.2s | compact list, planar channels, no buffer copies |
| under-sheet floor | 11.1s | 0.8s | van Herk O(N) sliding min |
| tear + MPI partition | 9.7s | 6.2s | flat masks, identity fast path, typed queues/buckets |
| colour bleed | ~4s | ~0.3s | frontier generations, original neighbour priority |
| thin-halo | 4.3s | 2.0s | window scan gated to Chebyshev-2 thin dilation |
| despeckle + collapse | 3.7s | 1.8s | van Herk windowed min/max |
| plug band + sweeps | 2.1s | 0.9s | compact interior sweeps (120× full-frame before) |
| **total (starwatcher)** | **137.2s** | **42.7s** | |

Frazetta: 30.2s; silverwarrior: 139.6s (3.5× the pixels — scales
linearly, no pathology). This VM (swiftshader, shared CPU) is ~3–4×
slower than a desktop, so the 1920×1323 real-hardware estimate is
~10–15s. The remaining costs are the deliberately-kept 24-pass Jacobi
(10.2s — a quality choice, not an accident), the canvas depth decode,
and the extension pull-push; the path below ~5s is workers/WASM/GPU
compute for those three, which changes machinery, not algorithms — a
separate decision.

The [PERF] log line ships in the build (one line per import), so any
future regression is visible in the console immediately.

---

## Addendum 15 — pre-SD hardening: the two contract questions, measured and fixed (commit `8e7ee19`)

The user asked two pointed questions: are there BG-plug→foreground
protuberances, and do glancing-angle plugs approximate the topology of
the surfaces they fill? Both were instrumented (new harness probes
`protrude.js`, `topoprobe.js`) rather than answered from memory.

**Protuberances — answer: none of consequence, after one real fix.**
The contract-correct test (a backing pixel that wins the z-test violates
only if nearer than every FG surface within parallax reach — off-frame
near continuations legitimately occlude far content) gives starwatcher
1px at worst 3/255: zero in practice. The cave asset exposed a REAL
class: plate doppelgänger patches where dark-on-dark soft silhouettes
never seed a band, the flood never enters, and the plate keeps near
source depth (`protrusion_fr_dancer.png` — the dancer's thigh blob).
Fixed by the FLOOR RIND: an occluder is anything standing above its
LOCAL floor (min-filter at 4× the band budget = the maximum-parallax
exposure radius) — which also removes the last global Otsu from the
flood path. Cave violations halved; the residual 0.3–0.4% on the
cave/warrior is a distinct diagnosed class (thin near objects whose rind
diffusion mixes its two flanks — sky one side, armor the other) that
per-layer plates solve structurally; recorded open for slice 3.

**Topology — answer: it was real, and it is now fixed.** Measured before:
mean |plug − surface continuation line| = 0.0243 depth units, with 11.2%
of reveal pixels off by more than a tear-step (`topology_errmap_before.png`
— the dominant mass is the ground carried UPWARD above the horizon
behind the mountain: the depth analog of the doppelgänger colour bug).
MEMBRANE CORRECTION: a completed pixel bounded on both row/column sides
by same-class real surfaces takes the inverse-distance blend of their
linear continuation lines (SAME gate = bgBandStep; one-sided reveals
keep the flood). The ONE-SIDED GATE keeps the flood as the contract's
lower bound — the membrane may move the plug farther, never more than a
tear-step nearer (concave scenes: both anchors near walls, the bridge
would cross the passage — measured on the cave before gating). After:
starwatcher mean 0.0004, >step errors 39,843 → 0; reveal colours improve
with it (fills target plugDepth). `membrane_pose_after.png` is the
cleanest off-axis render of the session.

**Generality note.** These changes REMOVE per-image machinery rather than
add it: the flood's occluder class is now local (floor field) instead of
global (Otsu); the membrane and gates reuse bgBandStep/fgTearStep; the
sweep radius is derived (4× budget ≈ max parallax). Rest-state cost:
0.58% of pixels in torn-skin fills whose colour targets changed — both
before and after are approximations of torn ink detail (measured
comparably against source); the proper fix remains offset-gating.

---

## Addendum 16 — Synthetic ground-truth suite: two containment defects found and fixed (v: standing-content mask + slope-continuing bands)

**Why a synthetic suite.** Every prior probe scored the plug against
*derived* references (flanking anchors, source renders). Four analytic
scenes with exact closed-form depth (`harness/synth/`: ground plane +
box occluder; 4px pole + soft floating ball; 600×900 portrait; 400×300
tiny) make the truth *computable*: behind a box standing on a linear
ground ramp, the correct plug at row y IS gd(y).

**What it caught (both invisible on the real assets):**

1. **Completion-flood leak.** Addendum 15's floor rind replaced the
   global Otsu class — but nothing replaced Otsu's *leak containment*.
   The flood exited through the box's ground contact and claimed the
   entire near ground.
2. **Floor-rind ramp false-positive.** `depth − min(window) >
   fgTearStep` integrates smooth slope: an ordinary ground plane
   accumulates ~0.15 over the 112px window, so 58% of the synA plate
   was swept into the rind. Combined effect: the plate's ground
   collapsed to diffused far values (open ground measured 0.03–0.10 vs
   truth 0.19–0.84) and the membrane lost every row anchor below the
   horizon. The real images hid this because the band (float, correct)
   covers all reveals within the parallax budget, and "too far" never
   trips a protrusion test — the plate ground moved with sky parallax
   in reveals, unnoticed.

**Fix — standing-content mask** (all constants derived, none new): a
pixel is occluder *body* iff it stands above its local floor (the old
windowed test, 4×-budget radius = max-parallax exposure bound) AND is
geodesically reachable within that radius from a **cliff seed** —
`depth − min(±4px) > fgTearStep`, a tear-scale discontinuity that every
tearable silhouette has (hard cliffs and NMS soft ramps alike) and a
smooth ramp can never produce (its per-4px variation is bounded by the
ramp-collapse binarization threshold). The flood is gated to the mask —
a front reaching an occluder's feet cannot exit onto open ground,
restoring the containment Otsu used to provide, now locally. The rind
sweep is simply the mask remainder the flood didn't claim.

**Second find — the band plateau, and why it resisted the membrane.**
With the plate fixed, the suite still showed reveal-strip (band) errors
= ground-slope × band-width (synA −0.049, synD −0.136 — the two scenes'
slopes exactly predict both). The directional plug held its far rim
value flat across the band; the membrane computed the exact correction
but its one-sided gate (Addendum 15's concave-scene protection) caps
nearer moves at one tear-step. Fix at the source: **slope-continuing
initialisation** — every band pixel starts at the far surface's own
gradient extrapolated from its rim source over the grown distance. Two
non-obvious details: (a) the gradient must be sampled 4–8px *behind*
the rim source — ramp collapse dips the first ~3px beside every cliff
toward the window minimum, and sampling from the rim pixel itself reads
that dip as a slope pointing *away* from the reveal (measured:
rim − slope·dist, the exact wrong sign); (b) 120 Jacobi sweeps cannot
converge a budget-deep strip from a flat init, so initialising only the
inner ring is not enough — every band pixel gets the extrapolated
value. Nearer-going extrapolation is clamped below the local occluder
(no protrusion channel); sky has zero gradient and stays flat; a narrow
slot cannot bridge its walls because the gradient measured is the
slot's own far surface's.

**Third: plate ceiling.** Swept floor strips kept a few-quantum NEARER
bias from rind diffusion. Contract rule, now enforced: the plate stands
in for the world *without* the removed content and may never sit nearer
than the world's own surface at that pixel — anything nearer is the FG
mesh's to carry. (`plug ≤ src` on swept pixels; no-op on occluder cores.)

**Suite after** (was → is): synA footprint mean 0.028→0.0031, max
0.198→0.025; synC 0.023→0.0022 / 0.136→0.0079; synD displayed-band mean
0.035→0.0058 (residual max sits in rows where the box–ground gap is
below fgTearStep — never revealed — and in the never-displayed interior
beyond the band). Open-ground plate depth now equals source exactly.
Zero contract protrusions and zero in-content transparent holes on all
four scenes (hole counts in the raw suite output are letterbox bars
outside the image, confirmed by 40px-margin classification). Soft-ball
core depth error 0.0067 (~1.7/255): despeckle does not flatten
legitimate soft objects.

**Real-asset regression:** frazetta protrusions 758→373px and the worst
offenders are no longer plate-borne; silverwarrior unchanged (556px @
204 — the known sword/cape flank-mixing class, structural fix = slice-3
per-layer plates); starwatcher 3px @ 25/255 (a 1–2px bilinear seam
where the plate's dune edge meets sky at the horizon — magnitude ≈ half
the horizon depth step), topo mean 0.0030 with 38px > step (0.0%).
Build time unchanged: 42.8s. Visibly better at the test pose
(`standmask_sw_pose.png` vs `membrane_pose_after.png`): the dark
dune-seam crack bottom-right and the white blob at the second figure
are gone — both were symptoms of the far-collapsed plate ground.

**Generality note.** The suite is the "any picture" check the campaign
needed: exact-math scenes across aspect ratios (1.5, 0.67, 1.33) and
scales (400px to 1200px), a soft object the despeckle must not eat, and
a thin pole. All fixes derive from existing constants (fgTearStep,
bgBandStep, band budget, ramp-collapse window); nothing is tuned to a
scene. Suite: `harness/synth/`, runner `harness/synth_run.js`, probes
`harness/synth_probe*.js`.

---

## Addendum 17 — MPI on by default

The load-time caveat that kept `bgMPIMode = false` is retired. Measured
with the flag as the parse-time default and the build run through the
real UI button: rest and pose renders are **pixel-identical (0px)** to
the post-load-enable path every probe in this review used, and camera
state (z / zoom / fov) is untouched. The "view-fit flip" that motivated
the off-default was a mis-attribution: the comparison target was the
MPI-OFF build, which really does render differently — without the
under-sheet (gated behind this flag) halo tears fall back to
rubber-stretch streaks (visible beside the staff in `mdef_off_pose`),
and the margins keep the pre-build JFA glow instead of the extended
plate. The OFF path is the legacy render; the ON path is the one every
contract measurement in Addenda 13–16 verified.

---

## Addendum 18 — Rebuild idempotence

A second `buildBackgroundLayer()` call in the same session diverged from
the first: the thin-feature halo had swapped the layer's depth texture
for the haloed one, so a rebuild read the halo back as its own input,
while the `_thinHaloApplied` guard skipped re-derivation and left
`haloM` null for the tear loop's ribbon veto. Fixed by keeping the
pristine plug-input depth from the first build and restoring it
whenever the halo-tagged texture would be read back; the halo then
re-applies from byte-identical input (guard removed). The MPI partition
cleanup and primary-mesh visibility restore now also run
unconditionally, so a rebuild with the partition toggled off restores
the monolithic mesh instead of leaving it hidden behind stale layers.
Measured: fresh == rebuild, 0px diff at the pose, identical stage
counts (`thin 2764 / haloed 2486 / mask 645988 / tear counts` repeat
exactly).

---

## Addendum 19 — Per-layer decimation: 5.01M → 98k triangles (2.0%)

Adaptive quad indexing over the shared vertex grid: a quadtree block
(16→2 cells) is emitted as two large triangles when every cell belongs
to the layer with both torn triangles present AND every texel's
displacement deviates from the two coarse-triangle planes by ≤ 1.5
8-bit quanta (below the depth map's own quantisation noise). Tears and
layer borders keep their per-texel triangles exactly — silhouettes and
reveal geometry are untouched, which is why the contract instruments
cannot tell the difference: same 3 protrusion pixels, identical
synthetic-suite numbers, identical hole counts. T-junction cracks are
depth-bounded by the same ε → sub-pixel at maximum parallax, in front
of the opaque plate. A/B renders differ only as dispersed sub-pixel
speckle on stars/ink edges (0.4% of pixels at rest, no line patterns —
`dec_diff_pose.png`). This retires the 5M-triangle scaling bottleneck:
the whole 10-layer stack now draws fewer triangles than 4% of the old
single mesh. `bgMPIDecimate`, default on.

---

## Addendum 20 — Per-layer plates WITHOUT SD: first attempt, reverted, with two real findings

Attempted a live (weight-free) slice-3: every layer extends its own
surface under adjacent strictly-nearer layers (slope-continuing depth,
carried colours), two overlap slots per texel, plate clamped behind the
strips where it is nearer than every bordering continuation. Reverted —
it regressed verified ground truth (synA plate mean 0.0031→0.0236, max
→0.291; starwatcher 3→1,068 flagged px, real worst 94/255): the plate
clamp corrupts correct plug values wherever slot competition picks the
wrong pair, and gradient extrapolation seeded from thin-feature borders
(glider, staff) produces poisoned depths. The strips CONCEPT stands
(structure now, SD for texture later); the failure is in the two
heuristics, not the architecture. Next iteration: strips as pure
additive meshes with no plate clamp, seeds excluded within thinM
dilation, slot depths validated against the membrane's row lines.

Two findings that outlive the attempt:

1. **The warrior's 204/255 residual is not (only) flank mixing.** The
   worst cluster sits on the frame bottom edge under the wolves. Two
   components: (a) REAL — the floor-rind/standing-mask floor field uses
   an edge-clamped window, so near content touching the frame boundary
   sees only itself as its floor, is never swept, and stays in the
   plate at near depth (the visible grey smear band at the bottom
   reveal); (b) MEASUREMENT — the protrusion test's FG-only pass hides
   the plate, and the scene-extension margins are part of the plate
   mesh, so legitimate near-depth front-surface margin continuations
   at the frame edge are flagged (fgMax = 0 there). The +delta the
   strips added was mostly class (b) on legitimate armor-behind-cape
   continuations more than 8px from visible armor.

2. **Frame-edge floor clipping** is the actual next targeted fix:
   floors near the image boundary need seeding from in-frame far
   content rather than edge replication, so frame-cut occluders sweep
   like interior ones.

---

## Addendum 21 — Frame-edge floors + floor-default ceiling: frazetta plate protrusions to ZERO

Chasing the warrior's 204/255 cluster to its actual pixels (plate
transect at the frame bottom, between the wolves) corrected Addendum
20's account and produced the fix.

**Correction to Addendum 20(b):** the protrusion test requires the FG
to cover the flagged pixel (`fa >= 128`), so margins beyond the FG
never enter the count — the metric was NOT blind the way claimed. The
cluster is real content: the transect showed the plate carrying
0.68→0.82 (wolf-ward ramp) under the swept gap, against a visible
0.61-0.65 floor.

**Mechanism, fully resolved:** (1) edge-clamped floor windows left the
wolves' frame-touching rows unswept (self-floored); (2) the unswept
core fed near depth into the rind diffusion; (3) the membrane's pair
gate RIGHTLY rejected the mixed rows (0.65 | 0.82 anchors); (4) the
plate ceiling then capped to source — the wolf itself — locking near
depth into the plate. Every stage behaved as designed; the composition
failed.

**Fix:** shifted-window floors (border texels take the nearest
fully-windowed interior floor — the window slides instead of clipping;
ramps stay safe because domain membership without a cliff seed sweeps
nothing) + a two-tier ceiling (membrane-anchored pixels keep the
source cap; anchor-less pixels default to the LOCAL FLOOR — the
nearest legitimate backing surface — instead of the occluder's depth).

**Measured:** frazetta 373 → 25 flagged px, plate-borne 373 → **0**
(worst 40/255, none plate); starwatcher 3 → 1 px (worst 3/255);
synthetic suite: zero violations, zero in-content holes, and
displayed-band accuracy BYTE-IDENTICAL (synA band 0.0035/0.0151, synD
0.0058/0.0948) — the floor default only moves never-displayed interior
pixels farther (footprint-interior means rise; that error mass sits
beyond the per-edge reveal budget and is protrusion-proof by
direction). The warrior's remaining 554px: the bottom margin
legitimately continuing the wolves below the frame — near content
sliding over far under parallax, correct 3D behaviour the radius-8
heuristic cannot express (same class as the dune-corner skirt,
Addendum 15). Visible cost there is the margin's coarse wash — SD
texture territory, not structure.

---

## Addendum 22 — MPI slice 3, live: per-layer plates without SD

The answer to "can we have per-layer plates now, just lower fidelity
than SD" is yes, and it is landed (v2 of the Addendum-20 attempt; both
of that attempt's failed heuristics replaced):

- Every layer extends ITS OWN surface under adjacent strictly-nearer
  layers — depth by the band's slope-continuing extrapolation, colours
  from validated same-row/column anchors (the v1 BFS-seed colours
  arrived from up to 100px away and sat in reveals as flat foreign
  slabs; anchor colours are tonally continuous at that height).
- Two overlap slots per texel (sky AND armor continue behind a sword),
  rendered as two sheets between the under-sheet and the plate.
- PURELY ADDITIVE — no plate clamp. The plate's correctness is
  Addendum 21's floor-default ceiling; the strips only add
  correct-class content in front of it.
- PAIR VALIDATION, the load-bearing new rule: a surface may extend
  under an occluder only where it FLANKS it — the strip pixel's row or
  column must exit into layer-consistent surface on both ends (frame
  boundary counts). This is the membrane's both-sided anchor principle
  applied to strips, and it is what separates armor-behind-sword
  (legitimate) from bird-flank-under-sibling (the 0.37 flecks that
  hung in the sky in v2's first run: 437 flagged px, worst 94/255 —
  eliminated).

Measured: synthetic suite zero violations, zero in-content holes,
plate accuracy byte-identical (additive confirmed); frazetta unchanged
(25 flagged, none plate); starwatcher 12px worst 19/255 (was 1px/3 —
the additions are small continuations >8px from same-depth FG, the
radius-8 heuristic's documented blind class); warrior unchanged.
Reveal visuals: strips-on matches strips-off tonally after the
anchor-colour fix, with correct-class depth structure underneath.
`bgMPIStrips`, default on. The SD stage now upgrades TEXTURE inside
this structure (per-layer export bundle = task 20), not structure
itself.

---

## Addendum 23 — Per-layer SD completion set (slice 3b): the pre-SD queue is empty

`exportSDBundle` now emits, for every MPI layer with strip content, a
`layer{k}_color.png` (visible texels + coarse strip continuation,
alpha = known — the SD context), `layer{k}_depth.png` (same coverage;
strip depth is already slope-continued, so it doubles as ControlNet
conditioning), and `layer{k}_mask_inpaint.png` (white = regenerate
with THIS layer's context only). `meta.mpiLayers` carries per-layer
mean depth and texel counts. Layers nothing occludes emit nothing —
the reference asset emits 7 of 10 (the near dune correctly skips).
The plate's own completion (`dir_*`) and the beyond-frame outpaint
(`out_*`) keep their existing entries: SD consumes the full stack —
farthest backdrop, intermediate layers, margins — and each result
reimports at a depth the live pipeline already established.

With this, everything on the pre-SD list is landed: standing-content
mask + slope-continuing plugs (A16), MPI default-on (A17), rebuild
idempotence (A18), 5.01M→98k decimation (A19), frame-edge floors +
floor-default ceiling (A21), live per-layer plates (A22), and the
per-layer export set (A23). The SD stage is now a pure texture
upgrade slotting into verified structure.

---

## Addendum 24 — Per-layer SD reimport: the layer loop is closed

`Import SD Layer Results` (beside the existing patch importer): one
multi-file picker accepting any subset of SD-inpainted
`layer{k}_color.png` files, filenames as the bundle exported them.
Each file's pixels write live into the strip slot textures wherever
that layer owns the slot — no rebuild, colours only. The strip DEPTH
was the SD conditioning input and stays as the live pipeline
established it, which is the whole design: SD can only ever change
what the reveals look like, never where surfaces sit, so every
verified contract property (protrusion, holes, plate accuracy,
rest-state fidelity) survives the texture upgrade by construction.
Transparent SD pixels keep the coarse live fill.

Verified headless (factored `applyMPILayerImage`): a synthetic layer-1
result updated exactly that layer's 2,540 strip texels (the bundle
meta's count), other layers' slots stayed byte-identical, and the new
colours rendered in the reveals at the test pose.

The full SD round-trip now exists: 💾 SD Bundle → inpaint per layer
(plus dir_*/out_* for plate and margins) → 📤 Import SD Layer Results.

---

## Closing scorecard — the eight criteria against the current build (review-fix @ harness commit)

1. **Plugs fill at correct LOCAL depth (far side of each edge).**
   MET, now provably: on analytic ground-truth scenes the displayed
   fill (band) tracks closed-form truth to 0.0025–0.006 mean / at
   worst 0.015–0.095 max, with every over-threshold pixel in
   never-revealed zones (occluder–ground gap below tear step). The
   fill CONTINUES surface slope (slope-extrapolated bands + membrane),
   not just rim values.
2. **Never protrude past the occluder.** MET: synthetic suite 0
   violations on all scenes; starwatcher 12px worst 19/255; frazetta
   25px none plate-borne; warrior's remaining cluster is the frame
   margin legitimately continuing near content under parallax.
3. **Affect nothing outside.** MET with two documented sub-visual
   exceptions: 0.58% torn-skin fill retargets (both states approximate
   torn ink comparably) and sub-pixel speckle from decimation/strips
   at high-contrast texels.
4. **No streaks.** MET (ramp collapse at bake aprons + halo-edge and
   soft-core NMS tears + under-sheet). The MPI-off legacy path still
   streaks — which is why MPI is now the default.
5. **No transparent holes.** MET: zero in-content holes at the pose on
   all synthetic scenes (40px-margin classification); raw counts in
   suite output are letterbox bars outside the image.
6. **No FG colour/depth contamination.** MET: fill sources exclude
   band/rind/ink; completion flood is standing-mask contained; strips
   are pair-validated and single-class by construction; the SD bundle
   extends the guarantee into the diffusion stage (per-layer context).
7. **Pixel-faithful at rest.** MET to 99.4%: the 0.58% torn-skin class
   plus quantum-scale speckle, both documented with measurements.
8. **Beyond-frame reveals filled.** MET (front-surface-seeded scene
   extension + welded margins; outpaint set in the SD bundle).

**Coarse live fill, refined by SD:** the architecture now matches the
original intent exactly — a weight-free, real-time-on-import layered
structure (partition + under-sheet + pair-validated per-layer plates +
floor-defaulted backdrop, 98k triangles), with a closed SD round-trip
(export bundle → per-layer inpaint → live reimport) that can only
change texture, never geometry. Everything above is constant-derived;
nothing is tuned per image, and the whole verification suite ships in
`harness/`.

---

## Addendum 25 — Look-down streaks: reproduced, partially mitigated, root cause isolated

User-reported streaking at cam(0.124, **+0.067**) reproduced exactly —
positive-Y (look-down) poses were absent from every earlier battery
(all used −0.055), and the class is look-down-asymmetric: depth DIPS
stretch under look-down parallax and compress invisibly at look-up.
Landed: a manual view-drag control (right-drag / shift-drag = head
delta, double-click reset) so any pose is one gesture away, and a
display-side shallow closing (radius 5, clamped to 2 tear-steps) that
fills narrow ink-stroke dips without touching the plug pipeline
(protrusion numbers byte-identical).

FG/BG attribution at the pose shows the dominant streaking is deeper:
a 20-60px-wide, high-amplitude noise APRON in the baked depth along
the dune crest — the FG tears into hatched gaps there and the plate
beneath shears on the same noise. A working-depth version of the
closing reduced it but moved plate protrusion 12→109px and was
reverted; local morphology cannot safely reach this class. The
structural fix is per-layer depth smoothing in the MPI representation
(a layer's INTERNAL depth may be smoothed aggressively — that is the
MPI model — while cross-layer silhouettes stay exact), which is also
the representation the newly stated wide-angle goal requires.

---

## Addendum 26 — MPI v2: full completed planes (the wide-angle path)

Landed behind a UI toggle ("Full planes (v2)"). This branch REPLACES
the v1 plug/tear/bake pipeline for a build: depth-quantile layer
partition (connectivity was the wrong cut — the figure joins the
ground at its feet and 99% of the image landed in one component; in v1
the TEARS did the segmenting), per-layer full completion
(flank-validated, unbounded reach, frame counts), intra-layer depth
smoothing (masked box blur r=8), 2px weld skirts across bin seams,
quarter-res pull-push completion colours under full-res visible
texels, and geometry-only margins via GL clamp-to-edge sampling (15%
for frame-touching layers, 50%/35% for the backdrop).

Results: **build 9-10s vs ~43s**; ~230k triangles across 6 effective
layers on starwatcher. The user's look-down hatch streaking
(cam 0.124,+0.067) is **gone** — intra-layer smoothing removes the
bake's noise apron structurally, exactly as predicted in Addendum 25
(`v2_lookdown_streakfree.png`). Rest state faithful. Poses at 0.35 and
0.6 offset (2-4x the v1 design envelope) hold coherent structure on
both starwatcher and frazetta (`v2_wide06.png`,
`v2_frazetta_wide.png`).

Open before default-on: the protrusion instrument's FG pass sees no
layers (covered=0 — needs a v2-aware reference pass); synthetic suite
not yet run against v2; completion washes are quarter-res pull-push
(the SD slot — the v2 bundle export should emit these layers
directly); the farthest-margin notch at 0.6 wants a curved backdrop
(sky dome) for true near-180 pans; under-sheet-class internal overlaps
within a bin are cut, showing the next layer's coarser completion.

---

## Addendum 27 — Multi-layer v2: composited layers get the same treatment

Per the product direction: added media layers are NOT assumed
perfectly baked — they are composited elements with their own internal
depth and disocclusions, and they now receive the identical full-plane
treatment. `bgBuildFullPlanesCore` runs per media layer: quantile bins
over the layer's own ALPHA FOOTPRINT, flank-validated completion of
its internal occlusions, smoothed intra-layer depth, transparent
surround preserved so layers composite through each other in z. Two
scoping rules matter: claims never leave the footprint (a cutout
completes itself, not the scene behind it), and the wide backdrop
margin belongs to the primary's farthest bin only (a cutout's farthest
bin margin would clamp-smear its edge colours — measured as red bands
before the fix).

Verified with a fabricated cutout (near bar over far disk) composited
over starwatcher: the disk claims 38,160px behind the bar and renders
its own completion in the bar's reveal with independent parallax at
wide poses (`v2_cutout_completion_wide.png`); the primary layer's
plane counts are byte-identical to the single-layer build; the extra
layer costs ~0.4s. Toggling back to v1 disposes the stacks and
restores every layer's mesh.

---

## Addendum 28 — Command-drag + debug views under the plane stack

View drag reworked to cmd/ctrl/shift + left-drag (the right-button
binding conflicted with existing canvas handlers), capture-phase on
window, verified with dispatched pointer events. Debug views fixed for
v2: plane meshes carry `userData.v2Plane` and count as the displayed
scene in the normalized depth pass (FG coverage after a v2 build:
0 → 99.8% — gap mask / FG-sub / scene-depth sheets see the stack).
"Show BG" toggles the whole stack vs the flat sources (and in v1 now
covers under-sheet + strips, not just the plate); "BG only" — which
under v1+MPI hid only the already-hidden original mesh and visibly did
nothing — now hides the partition meshes (v1) or the primary's nearest
bin (v2): a peek behind the front (`v2_solo_peek.png`).

---

## Addendum 29 — Leg shear fixed (edge-aware smoothing) + the supported view cone

**Leg shear** (user-reported): per-bin attribution showed the figure
and the near dune share a quantile slice; the unclamped intra-bin blur
welded them into one sheet whose depth ramped across the silhouette,
so the leg SHEARED into the background under parallax. Fix: the
smoothing is edge-aware — a texel may move at most half a tear-step
from its own depth; more is a different surface, so silhouettes
survive and the cell-cut separates the meshes. Verified at 0.35
offset: legs and boots hold shape (`v2_legshear_fixed.png`); reveals
show the soft completion wash instead of stretched limb content. A
14-bin variant was tried and reverted (banded washes, seam lines) —
the edge clamp alone is the fix; the v2 bin count is its own constant.

**Supported view cone** (product rule, per user direction): a flat
capture cannot fill 180 degrees, so the envelope is explicit — full
support inside 35 degrees, linear fade to black by 45, computed from
the true camera-to-portal angle each frame, applied as a DOM overlay
(captures untouched). The boundary is a design statement instead of an
artifact; both constants are tunable globals.

---

## Addendum 30 — v2 earns default-on

Three closing moves:

1. **Completion colours de-ghosted.** The isotropic wash averaged the
   whole surround into occluder-shaped grey ghosts. Claims now blend
   the layer's own ROW-anchor continuation (columns only as fallback —
   rows are same-surface continuation, the membrane lesson) 50/50 with
   the wash, softened by 4 Jacobi passes. Ghosts now carry their
   layer's sky/ground banding (`v2_ghost_banded.png`); texture detail
   remains SD's slot.
2. **The backdrop is complete everywhere.** Near-horizon rows failed
   the nearer-by-a-step claim gate, leaving the backdrop's frame
   margins alpha-0 in a band — the measured left-edge hole bar. The
   primary's farthest bin now claims every non-visible texel
   unconditionally. Result: **zero holes at all nine poses across the
   35-degree support cone** (geometry coverage, middle 90%).
3. **Rest fidelity** measured against the flat pre-build render: the
   difference is a pure edge map — sub-pixel projection shift from
   smoothed depth + bias — with no structural deltas.

With the leg shear fixed (A29), look-down streaking structurally gone
(A26), the cone fade defining the envelope (A29), and this addendum's
zero-hole scan, `bgMPIFullPlanes` now defaults ON. The checkbox A/Bs
against v1; all 57 v1 harness drivers are pinned to v1 so the original
contract battery keeps meaning what it says (protrude re-verified
unchanged after the flip). Remaining v2 work: SD bundle/import wired
to the v2 layers, the bin-internal under-sheet analog, sky dome, and
an async build for instant import.

---

## Addendum 31 — Finish line: the import-to-parallax pipeline is closed

The remaining v2 queue, resolved:

1. **SD round-trip on planes.** The build records every plane; the
   bundle emits `v2_{tag}_bin{k}_color/depth/mask_inpaint` per plane
   with claimed content (5 of 6 on the reference asset; the depth file
   is the smoothed plane field, already ControlNet-ready); the import
   button detects the v2 stack and writes SD results into the LIVE
   plane textures at claimed texels — colours only, structure
   untouched, no rebuild. Verified: exactly the expected 1,185,625
   backdrop claim texels applied and rendering in reveals immediately.
2. **Auto-build.** The stack builds itself when media is ready and
   when the primary depth source changes, guarded by post-build
   texture identity (no rebuild loop). Upload a picture; the wide-angle
   stack appears (~9s). "Click a button, it just works" is now "don't
   even click."
3. **Sky dome: assessed, skipped with cause.** Within the 45-degree
   fade cone the flat backdrop + 50% margins cover every supported
   pose (the zero-hole nine-pose scan is the evidence); a dome pays
   only if the cone widens.

**Remaining documented residuals** (all quality-of-polish, none
structural): the bin-internal under-sheet analog (an intra-bin cliff's
reveal shows the next plane's wash — narrow by construction, wash now
band-coloured); worker-threading the ~9s build (currently a one-tick
deferred synchronous build with a status label); completion texture
detail (SD's job, and the loop for it now exists end to end).

**The arc, end to end:** an adversarial review of a band-limited
plug's eight-criterion contract became, via the synthetic ground-truth
suite, the standing-content mask, the membrane, decimation, and the
strips — and finally inverted into the architecture the product
wanted all along: quantile relief planes, complete everywhere, smooth
inside, exact at silhouettes, composited per media layer, fading at a
declared envelope, built without weights in seconds on import, with a
diffusion loop that can only ever repaint texture inside verified
structure.

---

## Addendum 32 — Every layer covers the cone; the dolly zoom actually works

Two requests: make the "sky dome" (edge-of-fill coverage) hold for
ALL layers, not just the farthest backdrop — is equirectangular
needed? — and examine the dolly-zoom scaling, using an off-axis dolly
zoom as the correctness probe for movement scaling under the
asymmetric frustum.

### 1. All-layer cone coverage — flat planes suffice, equirect does not pay

The A30/A31 margins were sized as a fraction of image width. On
landscape assets that hid a latent bug: a portrait asset (frazetta)
maps to a narrow world plane, so the same pixel margin buys far less
world overhang — the full 45-degree scan leaked 31–74k hole pixels at
the diagonal poses while SW stayed at zero. The margin was measuring
the wrong thing: the cone is declared in world angle, so the overhang
must be declared in world units.

**World-normalized margins.** Backdrop bins now extend 0.10 world
units past the image rect, near/frame-touching bins 0.05, converted
to texels per asset (`px = world / planeW * pw`). On portrait assets
this is a lot of texels — so margins are no longer carried in the
per-texel plane geometry at all. Each bin's main mesh covers only its
in-frame bbox; a coarse **skirt mesh** (8px-step grid, sharing the
bin's material, uv projected past [0,1] under clamp-to-edge) carries
the overhang for the cost of a few hundred triangles instead of
millions. The backdrop bin additionally keeps every quadtree cell
(span filter bypassed) so the back-stop can never hole. Added layers
keep their alpha-footprint rule — cutouts get edge continuation only
where they have content, and no backdrop margins (that combination is
what smeared red bands in A27's first draft).

Measured, full 45-degree 12-pose scan (middle 90%): SW **0 hole px at
every pose** (unchanged); frazetta **74k → 10–42px**. The residual is
1px-wide diagonal chains at decimation T-junction seams mid-image
(~0.01% of a frame, inside the 35–45° fade band at the poses where
they appear) — documented as a micro-residual, not coverage failure.

**Equirectangular verdict: not needed.** The declared envelope (A29)
is a 45-degree cone with fade from 35; within it, flat planes with
world-sized skirts are measurably hole-free. An equirect/dome
projection buys curvature only useful past ~60 degrees, at the cost
of resampling every layer. If the envelope ever widens toward the
"gyro past face-cam FOV" regime, revisit; below that the dome is
paying for angles the fade has already declared black.

### 2. Dolly zoom — the fov code was dead; the frustum was already exact

The examination the user asked for, in three findings:

**(a) The asymmetric frustum handles movement scaling exactly.**
`frameCorners()` rebuilds the projection every frame from the eye and
the fixed portal rect — Kooima's generalized perspective projection.
Measured (analytic projection through the live camera): portal-plane
points drift **0.000px** across the full dolly sweep (eye z 0.12 →
0.42) at lateral offsets 0, 0.1, and 0.2, while a point 0.1 behind
the portal travels 89–214px. The off-axis dolly-zoom invariant — the
test the request named — holds to machine precision natively. This is
also the capture-equivalence answer: an object shot at 18mm from d
and at 36mm from 2d that lands at the same world depth parallaxes
identically by construction, because the frustum scales motion by
reconstructed world position only — the capture fov never enters the
render side. (What a capture fov mismatch DOES change is the depth
map the estimator produces; that is a reconstruction-calibration
question, not a projection one.)

**(b) The existing subject-lock/fov compensation was dead code.** It
assigned `camera.fov` — which `frameCorners()` overwrites before any
render, every frame. The `subjectFocalPlaneWorldZ` slider had no
effect. Nobody had noticed because the portal plane (the default
subject) is pinned for free by (a).

**(c) The replacement is portal-native.** For a subject plane off the
portal (z = q, portal at P, eye at e, d = e−q), a subject-plane point
projects through the portal with factor t = (e−P)/(e−q); pinning it
requires scaling content by **s = d·(e0−P) / (d0·(e−P))** about the
eye-axis point on the subject plane — not the naive d/d0, and not
about the world axis: only the eye-axis center pins the plane for the
current eye, which is what makes the lock correct off-axis. At the
base distance s = 1, so head-tracking parallax at rest is untouched;
transforms capture on dolly start and restore exactly on stop. One
frame-loop conflict surfaced: the per-frame layer-z reset
(`layer.mesh.position.z = portalPlaneWorldZ`) was silently undoing
the lock's z each frame — it now yields while the lock owns
transforms.

Verified through the real mesh matrices (not the lock's own math): a
mesh-attached point whose base world position lies on the subject
plane (q = −0.05) projects with **0.000px drift** across the dolly at
offsets 0/0.1/0.2, portal-depth content breathes 77–185px, and
dolly-off restores base transforms bit-exactly. v2 contract
regression after the frame-loop change: zero holes at all nine poses.

Landed in `797e858` (drivers: `harness/dolly_test.js`,
`harness/v2_conescan.js`).
