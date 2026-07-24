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

---

## Addendum 33 — Session UX: realtime by default, explicit builds, a fade that fires on a MacBook

Four user reports, one environment note.

### 1. The load freeze is gone: realtime inpainting is the default again

A31's auto-build ran the v2 plane build seconds after load —
synchronously, freezing the tab. Wrong default: the realtime
screen-space inpainting (pullpush) is fast on real GPUs and is what the
session should open into. Now: **on load, nothing builds** — the app
renders source parallax with realtime inpainting exactly as before the
MPI work. The Build BG button runs whichever build the "Full planes
(v2)" checkbox selects, behind a **loading overlay** (spinner + label,
painted before the synchronous build via double-rAF, for both the v1
bake and the v2 planes). After the first explicit build, a new upload
auto-rebuilds behind the same overlay — the stack tracks the image once
the user has opted into it, but never ambushes the first load.

### 2. The fade now keys off the device camera, not just the virtual cone

The 35–45° fade (A29) measured the VIRTUAL head angle — on a MacBook
Air the face-cam geometry cannot produce 35°, so the fade never fired.
Added a **per-device front-camera FOV LUT** (mac 54×32°, iphone 65×50°,
ipad/Center-Stage 105×80°, generic 60×40°; platform-detected, coarse by
necessity — browsers hide the camera model — and overridable via
`window.bgDeviceFovOverride` or localStorage `bgDeviceFov`). The head's
angular position inside the camera frame is computed from the
normalized face position through the tan mapping, and the view fades
over the **last 10 degrees before the head exits the camera FOV** —
`hfov/2−10 .. hfov/2` horizontally, `vfov/2−10 .. vfov/2` vertically,
exactly the rule requested. The virtual-cone fade still applies (drag
and gyro paths); the final fade is the max of the two. A lost face
freezes the fade at its last value rather than snapping.

### 3. Debug views and "Enable Inpainting" work after every build

Root cause was semantic: once a bake (v1) or plane stack (v2) exists it
blankets every gap, so the pipeline-inspection views ('gaps',
'inpaint_only', 'layer_mask', …) legitimately had nothing to show, and
unchecking Enable Inpainting changed nothing — both READ as broken.
Now any non-final debug view — and inpainting-OFF on the final view —
**suppresses the baked/plane meshes for the frame and restores the flat
sources**, so each view shows the realtime pipeline it names; returning
to the final view restores the exact prior state. This required
handling the two stacks that deliberately hide the source mesh (v1-MPI
partition, v2 planes) — the suppression brings the source back while it
inspects. Verified by a state-level contract driver (frameless, so it
runs under SwiftShader): **9/9 checks pass in both v1 and v2 modes**,
including exact restoration.

### 4. v1 bake: FG was genuinely leaking into the baked BG at edges

The user's screenshots showed FG paint left in the baked background
along silhouettes. Mechanism confirmed in the color-seed shader: a
texel could feed the color pyramid if the depth plug replaced nothing
within **2px** — but estimated depth halos put the color silhouette
2–3px OUTSIDE the depth silhouette, so anti-aliased FG paint passed the
gate and seeded the wash. The erosion is now **4px**. A/B on the real
portrait asset: the changed texels lie exactly along the silhouette
fringe and the FG-colored speck clusters shrink visibly; the synthetic
suite (razor-sharp, perfectly aligned edges) shows zero bleed under
both radii, confirming the mechanism is specifically soft-edge/halo
misalignment. The LIVE streaking in the same screenshots is the v1
single-mesh apron — the structural limitation that motivated v2 (A26,
A29); v1 remains the A/B reference, not the wide-angle path.

### Environment note (for whoever runs the harness next)

The remote box was replaced mid-session with a 4-core machine.
SwiftShader there cannot deliver a first frame of the realtime
multi-pass pipeline at 1200×900 — rAF starves indefinitely (GPU process
grinding at 350% CPU) while the main thread stays responsive. All
drivers now run at 800×600, and the new post-build contract test is
deliberately frameless (direct render() calls + state inspection).
Leaked headless browsers from killed runs poison subsequent runs —
always `pkill` the browser and static server between attempts.

Landed in `5dde8bb`.

**Regression note:** the v2 nine-pose contract was re-run before and
after this batch on the same asset (the portrait default — the box swap
also lost the harness's untracked landscape default, so numbers are not
comparable to A30's zero-hole run on that asset): pre-batch 7–44 hole
px per pose, post-batch 7–46 — identical within frame noise, i.e. the
batch does not touch geometry coverage; the residual is the documented
frazetta T-junction speck class (A32).

---

## Addendum 34 — The outline artifact is a depth-map defect; it is now repaired at the root

The user's screenshots this round show three separable things, and only
one of them was fixable where I had been looking.

### 1. Diagnosis: why occluder outlines stick to the background

The dark outlines (the man's silhouette line, the staff, the spaceship
contour) sit at **background depth in the estimated depth map** — thin
line art defeats monocular depth estimators. From that point on, every
renderer is faithful to the wrong data: the strokes are geometrically
background in the FG mesh, in the v1 partition, in the v2 bins, and in
the bake — so they detach from their occluder under parallax and
"stick" to the background. This is why the previous bake-side erosion
(A33's 2px→4px) could not touch it: those texels were never
plug-replaced, because per the depth map they ARE background. Measured
directly: the CPU fill texture that the live BG mesh actually samples
(`fillRGB` — NOT the GPU wash `bgColorTarget`, which only feeds the
debug panel and SD export) carries the strokes verbatim outside the
band, and 64% of a synthetic stroke path survived into the bake under
the old code.

### 2. The root fix: stroke depth repair in `applyLiveBake`

A stroke texel — luma < 0.30, contrast on both sides across its width
(dark-region rims have a flat interior side and are excluded), strong
contrast on at least one side — that sits within 3px of decisively
nearer non-stroke content (depth gap > 0.05) **adopts that nearer
depth**, and the adoption propagates geodesically along the connected
stroke set, hopping 1–2px classification breaks: staff → hand,
outline → figure. Strokes with no near evidence anywhere along their
run are left untouched — an isolated far silhouette has nothing to
anchor to, and inventing depth for it would be worse. The repair runs
before the sharpened depth ships, so the v1 tear, the partition, the
v2 quantile bins, and both bake paths all see repaired depth; the GPU
colour seed additionally rejects dark strokes so even unrepaired ones
cannot wallpaper into the wash.

Ground truth (synT: strokes drawn in COLOUR ONLY, depth left at sky —
the exact estimator failure): occluder outline **0.622** and 190px
staff **0.678** against target 0.678 (sky = 0.031); isolated control
stroke stays 0.031. The two iterations that mattered: the seed radius
had to be 3px because the depth silhouette rarely touches the stroke
exactly, and the darkness ceiling had to come down from 0.45 to 0.30
because frazetta's painterly darks misclassified and put a localized
+67px protrusion cluster on the contract — at 0.30 the frazetta
protrude battery reads **exactly baseline** (23px, worst 40/255),
synA plug truth is violation-free, and the v2 nine-pose contract is
unchanged within noise.

### 3. What the streak fields are — and are not

The wide tunneling streaks in the same screenshots are the v1 tear's
deliberate KEEP classes (thin ribbons, far-mismatch walls whose reveal
the bake cannot back) stretching at angles v1 was never contracted
for, plus the bake mesh's own internal cliffs, which are exempt from
the stretch cut because cutting the LAST layer opens naked holes. The
band-gated cut is disarmed under pre-tear by design (D1b: it misfires
at rest). This is the single-completed-background ceiling documented
in A26/A29 — it is the reason v2 exists, and it is not tunable away.
v1 remains the A/B reference; the wide-angle path is the v2 stack.

### 4. UX

The build overlay now has a **progress bar and %**. The builds are
synchronous main-thread blocks, so the bar is a compositor-thread
transform animation calibrated to the last measured build duration
(stored per mode) — it keeps moving through the freeze — and the %
text ticks whenever the thread yields, snapping to 100 at completion.
A literal per-stage % would require making the build yield (worker or
generator restructuring); noted as the honest upgrade path. Also
fixed: exporting the debug grid while a pipeline view (or
inpainting-off) had suppressed the baked meshes produced degenerate
all-hole/all-invalid panels — the export now restores the composed
scene before refreshing its buffers (this was A33's suppression
interacting with the exporter, visible in the user's second grid).

Landed in `5395575` (drivers: `harness/strokedepth.js`,
`harness/strokebleed.js`, `harness/gridfix_test.js`; synthetic assets
`synS`/`synT`).

---

## Addendum 35 — Retraction: the tunneling was never a ceiling

The user rejected A34's "structural ceiling" verdict with the correct
argument: a stretched triangle renders content that is visible from NO
viewpoint, so it can never be the right answer — anything opaque
behind it (the bake, black) is strictly better. The retraction is
warranted. What looked like one ceiling was three mechanisms, each
individually closable:

**1. The tear kept rubber on purpose.** The thin-feature collar and
far-mismatch keep classes preserved cliff-spanning triangles to
protect thin features and avoid mismatched reveals. Both rationales
are obsolete: stroke repair (A34) makes thin features depth-coherent
(their interiors no longer span cliffs — only their 1px boundary ring
does, and tearing it cannot destroy them), and a mismatched reveal at
least parallaxes like a surface. `bgTearAllRubber` (default on) drops
every triangle spanning more than fgTearStep. Reference build log:
**0 thin-feature kept, 0 far-mismatch kept**.

**2. Ramps terraced below every threshold.** A silhouette ramp wider
than ~5px survived the single ±2px binarization pass as a staircase of
sub-threshold steps — invisible to per-triangle span tests (each
triangle spans a third of the ramp) and to fwidth heuristics. The
binarization now ITERATES until convergence, the plateaus eating the
ramp from both sides, and chooses the snap side by **colour affinity**
rather than depth proximity — depth-proximity snapping stranded
occluder-coloured texels on the far plateau, which is the wide-band
analog of the stroke problem and was measurably the residual debris.

**3. The plate was exempt from everything.** The baked background mesh
is a monolithic displaced grid whose own internal cliffs (mountain
against sky, continuing under a reveal) rubber-band exactly like FG
cliffs — and it sat outside the band cut (`!u_isBackgroundLayer`),
outside the tear, outside the fragment discards. The stretch/mismatch
net now applies to the plate (`u_bandCutAll`), and re-arms under
pre-tear UNGATED by the band. A discarded plate fragment shows black:
within one completed background, the content behind the last surface's
own cliff genuinely exists in no capture, and black is the same honest
statement the view-fade envelope makes. (v2's per-bin completions are
still the path that fills those reveals with actual content.) The
re-armed net is also the "transparency filter" that now catches the
fine dark streaks in the no-inpainting view — the per-fragment
discards had been hard-disabled under pre-tear.

**Ground truth** (synU — the synthetic with Gaussian-blurred depth,
giving the 18px ramped silhouettes real estimators produce): the solid
tunnel wall on the occluder's reveal edge collapses into a clean
backed reveal with thin residual slivers; reveal-zone debris roughly
halves, with part of the remainder being edge texels now correctly
reclassified ONTO the occluder (they parallax with it, which is the
desired behaviour and outside what a colour-only count can see).
Regressions: frazetta protrude at baseline (30px, worst 35/255 vs
23px/40, same cluster — noise), synA plug truth violation-free,
stroke-repair contract 3/3, v2 nine-pose contract unchanged.

**Honest residuals:** sub-threshold slivers (a few px wide) at cliff
edges — the heuristics are thresholded and a discard test cannot be
made exact without exact geometry (which is the tear's job, and the
tear cannot see sub-triangle ramps that the collapse missed); and
black slivers where the plate's own cliffs open at wide angles, which
only a second completed surface (v2) can fill with content.

Landed in `343c981` (drivers: `harness/tunnel_test.js`,
`harness/viscrop.js`; asset `synU`).

---

## Addendum 36 — Quick bake: the realtime look, frozen; and the SD-region preview

### Review of the realtime path (as requested, before building on it)

Per frame, the realtime pipeline: classifies gaps in the layer
fragment shader (depth-gradient + optional Sobel/luma/chroma
generators), renders a normalized depth pass, runs FG-subtraction to
build a local rim-depth contract, then fills the screen-space gaps
with a depth-aware pull-push pyramid (~9 levels up + down at canvas
resolution) and composites. Findings:

1. **The flicker is structural, not a bug.** The fill re-seeds from
   the rasterized frame every frame; subpixel camera motion changes
   which texels count as rim seeds, and the pyramid average shifts
   with them. No amount of tuning stabilizes a fill whose input
   dithers — the fix is to compute it once in source space.
2. **The cost is fixed, not content-driven.** Pyramid + FG-sub run at
   full canvas every frame even when nothing moves. (With the quick
   bake landed, the honest optimization was to skip the multipass
   entirely rather than cache it.)
3. **The fill itself is good** — depth-aware pull-push with the rim
   contract is the right primitive, which is why the quick bake
   reuses it verbatim rather than inventing a new fill.

### The quick bake

The user's sketch was right and has a clean closed form. The union of
disocclusions over EVERY head pose in the movement budget: a texel is
revealed iff nearer content exists within r px whose depth step
exceeds r/RB, for some r ≤ RB — the cone test, evaluated with three
separable sliding maxima at r = RB/4, RB/2, RB. O(N), a few hundred
ms at source resolution. Plate depth = the far envelope under genuine
standing content; plate colour = the SAME pull-push wash the realtime
path shows, seeded once in source space (one-sided erosion + stroke
rejection included). The FG keeps the stretch net so its rubber cuts
onto the wash; quick-baked scenes then render SINGLE-PASS — the
per-frame multipass is skipped entirely. Identical look, no flicker,
and per-frame cost DROPS below the realtime path it replaces.

Two pitfalls found by measurement, for the record: flooring the plate
with a tight 0.02 gate floors under ordinary texture relief on
organic depth maps, which invalidates ~all colour seeds and
degenerates the wash to NaN-white (gate now 0.08 = genuine standing
cliffs only); and the plate must render SOLID — the cloned material
inherits the FG's gap generators, which classify the plate's own
floor transitions as gaps and punch holes in the only backstop.

### The SD-region preview

The same mask drives the UX feature: regions where diffusion will
paint are tinted on a depth ramp (far = cyan, near = amber), the
region boundary gets a bright rim, and the foreground dims to 35% so
the regions read through at rest. One uniform set, wired through all
three layer shader modes, rendered in the single-pass path.

Contract: 12/12 checks (plate + mask + wash present, plate solid, FG
net armed, highlight toggles and compiles, single-pass flag, CPU side
2.3s on the 4-core SwiftShader box — sub-second on a real GPU).

Landed in `1c90c99` (driver: `harness/quickbake_test.js`).

---

## Addendum 37 — The caravan bug: stroke repair learns the difference between an outline and a bystander

The user's grids caught the stroke repair over-adopting: the caravan
figures walking up the dune — genuine BACKGROUND content — were being
lifted to the dune ridge's depth and rendered ON TOP of the
foreground. The failure is instructive because the two cases are
locally identical: a dark stroke touching decisively-nearer content is
EITHER an occluder's outline (A34: lift it — it belongs to the
occluder) OR a small far figure standing just behind a ridge (leave
it — it belongs to the scene). No per-texel gate can tell them apart;
the staff and a caravan figure have the same local topology.

The discriminator that works is the **connected component's contact
fraction**. An outline HUGS its occluder: most of its texels have near
content within 3px. A far figure touches the ridge only at its feet
(~5% of its texels). And the staff — the case that motivated A34 —
is CONNECTED to the figure's outline ring in the ink, so it rides the
outline component's high contact fraction. Adoption now runs
per-component (labelled at the propagation connectivity) and requires
≥25% contact.

synT extended with the caravan case: outline 0.622 and staff 0.678
still lift (target 0.678), the isolated control stays at sky, and the
caravan figures deviate 0.003 from the ground truth — they stay
exactly where the scene put them. Frazetta protrusion battery
unchanged at the A35 baseline.

Landed in `0ce78d9`. If caravan-class content still floats above the
foreground on an asset after this fix, the depth MAP itself
near-classified it (salient-object pop is a known estimator failure —
check the Scene Depth view); that class is upstream of everything
this pipeline can repair locally and is the SD/depth-model loop's job.

---

## Addendum 38 — Quick bake round 2: the plate becomes a cone envelope

The user's first live test caught the quick bake's plate cloning the
astronaut: a radius-28 floor cannot floor a 200px-wide occluder — the
interior is its own floor — so the plate carried the figure at NEAR
depth, its clone-edge cliff rubber-banded into the floored ring (the
interior-to-background smear), and the interior texels seeded figure
colours into the wash.

Two mask-based fixes failed for reasons worth recording. A compounding
erosion (geometric radii, iterating on its own output) let big blobs
act as CONDUITS: sky leaked through the horizon into the blob's sunk
values and then cascaded onto the surrounding ground — the whole lower
scene classified as standing. A single-shot per-radius test cannot
cascade, but any slope-linear gate loses to the ground's own
perspective gradient at large radii: at r=192 this scene's ground
rises faster than the gate allows, and 100% of the ground classified
as standing again.

The final form drops the mask entirely by restating the requirement.
The plate's real contract is not "floored under standing content" —
it is **"no cliff anywhere"**, because cliffs are the only thing that
rubber-bands. That has an exact, parameter-light construction: the
plate is the LOWER ENVELOPE of the depth under a maximum slope —
`min_i(d_i + s·dist(i,j))`, cone erosion, computed exactly by the
classic two-pass Manhattan chamfer sweep in O(N). By construction the
plate's gradient never exceeds s = 0.0025/px: nothing can smear.
Continuous ground (slope < s) is untouched; a standing blob becomes a
gentle ramp down to its surround; the untouched core of a very wide
blob is covered at identical depth by the FG mesh and never shows;
and the colour-seed pass invalidates exactly the ~(step/s)px ring
where the envelope departs the source, so the reveal-ring wash is
clean far colour.

Probe on the astronaut-class synthetic (200×300 occluder): reveal
ring at local ground (0.481 against 0.455 + ramp), maximum plate
gradient 0.0025 — exactly the cone slope, i.e. zero cliffs — and the
reveal-ring wash scene-coloured; pre-fix the same probe read a 0.678
near-depth clone with a figure-coloured wash. Quick-bake contract
12/12 unchanged.

Landed in `6555c6f` (probe: `harness/qbflood_probe.js`).

---

## Addendum 39 — The highlight fills, the outlines come back, the filaments die

Three reports from the user's live pass; two share a root.

**1. The SD-regions highlight rimmed instead of filled.** The mask was
the cone test's physics-minimal reveal band — correct for "what a
28px head budget exposes", wrong for "what diffusion will paint". The
honest mask is where the plate SYNTHESIZES content: wherever the cone
envelope departs the source depth. One comparison per texel, and the
highlight now fills the whole region (on a Δ=0.22 cliff that ring is
~90px wide, not 8).

**2 & 3. The lost black outlines and the 1px FG→BG filaments are the
same defect.** A34's stroke repair lifts outline ink to occluder
depth — but the estimator undershoots the colour silhouette, so a
1–2px far channel separates the lifted stroke from its occluder. The
outline was therefore a fragile 1px near-depth RIDGE: every quad
touching it spans a cliff. The stretch net ate the stroke's own
fragments (that is where the ink went — the source image was never
touched; the bundle's src_color export is verbatim) and the survivors
rendered as 1px rubber filaments. GAP CLOSING now lifts thin far
channels that are near-on-both-sides and adjacent to an adopted
stroke: the outline becomes CONTIGUOUS with its occluder — one
silhouette, one cliff, at the stroke's outer edge. 737px closed on
the synthetic; all four stroke-contract cases still pass (outline and
staff lift, isolated and caravan stay).

**Plus:** quick mode no longer trusts the thresholded fragment net
alone — the FG geometry pre-tears every cliff-spanning triangle at
build time (the plate backs every reveal, so holes are always safe);
6,733 of 1.74M triangles dropped on the reference build. Sub-threshold
1px ribbons cannot survive a geometric cut.

Battery: stroke contract 4/4, plate probes clean (ring at local
ground, max gradient = the cone slope, ring wash scene-coloured),
quick-bake contract 12/12, frazetta protrusion at baseline.

Landed in `f885888`.

---

## Addendum 40 — Thick ink was still shipping at background depth

User: "some of the black outline is still projected to the background."
Correct — and it was the ink the repair COULDN'T reach. The two-sided
thin gate (A34) classifies a stroke by seeing brighter content on
both sides within 4px. Thick ink — staff ornaments, hook curls, knots
10–20px across — fails that by construction, stayed unclassified, and
shipped at BG depth: a piece of the outline visibly left behind on the
plate, exactly what SD would then inpaint AROUND.

**Phase 2: lift small dark components whole.** Same discriminator as
the caravan fix (A37), one level up: a dark connected component lifts
to its occluder iff it passes four gates —

1. **Area cap** (≤4,000px): shadows and rock faces never qualify.
2. **Adopted contact + through-test**: phase-1-lifted ink must not
   merely brush one edge (a dark patch beside an outline) but reach
   both extremes of the blob on some axis — the staff passes THROUGH
   its ornament.
3. **Whole-blob-far**: every member must sit at least one depth GAP
   below the adopt depth. This is the gate that took three attempts
   to find (see below).
4. **Ring contrast** (≥0.15): ink sits on a brighter surround by
   nature; dark-on-dark is painterly texture, not ink.

A **continuation round** then re-anchors ink the blob orphaned — the
staff ABOVE its ornament loses its phase-1 connection when the
ornament breaks the classification chain; it re-seeds from phase-2
texels only and rides the stroke graph as usual.

**The gate that mattered.** First cut (contact-bbox through-test
alone) lifted 139px on the frazetta and pushed protrusion from 30px
to 49px, worst 35→64. A stricter opposite-sides test (external ink
strictly above AND below the blob) fixed frazetta but killed the
ornament: its orphaned upper staff is dark-and-unadopted, so it MERGES
into the blob and the merged blob only has adopted ink below it.
The candidate dump (new `p2probe.js`, `_srCapture`) showed the real
difference: the frazetta regressor's members span depth 0.063→0.494 —
it STRADDLES the silhouette, and some members already sit at the
adopt depth. The ornament's members are uniformly at sky depth
(0.031). Stuck ink is stuck WHOLE. A blob that already reaches the
adopt depth is silhouette texture, and lifting its far part
manufactures a near-depth island that protrudes. Requiring
`adoptDepth − max(memberDepth) > GAP` accepts every true positive and
refuses the frazetta blob outright.

Contract grew to 6 cases (synT gained a 17×17 ornament on the staff
and a footprint lying along the outline): outline lifts, staff lifts,
isolated stroke stays, caravan figures stay, **ornament lifts (staff
passes through), footprint stays (one-sided brush)** — 6/6. Frazetta
protrusion back to baseline (30px violations, worst 35, plate-only 0).
Quick-bake 12/12, plate probes 3/3. Bisect kill-flags (`_srNoGC`,
`_srNoP2`, `_srNoCont`) and the candidate dump are left in as gated
debug affordances with a driver (`protrude_ab.js`).

Landed in `44f8e99`.

---

## Addendum 41 — The outline was on the plate, and the repair was 97% blind

The contact sheets showed it plainly: the figure's FULL outline baked
into the background plate — it parallaxed with the background while
the figure moved away from it. And under occluder footprints the
plate depth still bulged toward the camera in the occluder's own
shape. One measurement explained both.

**The A37 component gate did not survive contact with real ink.** On
a real drawing ALL ink is one connected web — outline, interior
linework, ground contours, all touching somewhere. The component-
global contact fraction on the reference asset was ~3% (2,599 of
78,490 classified stroke px lifted), far under the 25% gate, so the
repair went blind: the outline shipped at BG depth, counted as valid
background, and was baked into the plate in full. synT passed 6/6 the
whole time because its ink components are isolated — the synthetic
modeled the geometry of the problem but not the CONNECTIVITY of real
line art.

**Fix 1 — adjacency-constrained flood.** The honest discriminator was
always local, not component-global: an occluder's outline HUGS its
occluder for its whole run; a far-side figure touches a ridge only at
one end. Adoption now spreads while it keeps meeting near content at
the adopted depth (within 2px), with a 2-hop grace budget past the
last hug — EXCEPT along thin ribbons (bright on BOTH sides at ±2px),
which carry adoption end-to-end like a wire. That is the staff: no
near content anywhere along its run, but an unbroken ribbon back to
the outline. A caravan figure is 5px wide — zero ribbon texels — and
drains the budget within ~6px of its ridge contact. Same contract,
no global state. Coverage on the reference asset: 11,290px (4.3×),
phase-2 thick ink 90 → 730px; frazetta protrusion unchanged at its
exact baseline.

**Fix 2 — ink scrub in the plate fill.** Whatever the repair still
misses must not survive in the plate: stroke-classified ink within
4px of the removed set (plus its dark anti-aliased fringe) is
recoloured from the ink-free pull-push base. The world-without-FG has
no outline where the figure was; the FG mesh keeps drawing the real
ink, so nothing is lost — there is just no second copy left behind to
stick to the background. 5,495px scrubbed; the plate's outline ghost
is gone from the fill dump. Ink far from any occluder (the mountain's
own cracks) is genuine plate content and stays.

**Fix 3 — cone clamp on the plate depth.** The existing plate ceiling
capped at the SOURCE depth — i.e. the occluder's own nearness — so
diffusion residue under wide occluders kept a shape-following near
ghost ("depth stretching into the foreground"). Third tier, underMask
only: the plate may never stand above the cone envelope of the
surrounding real world (min over valid texels of depth + s·dist,
exact two-pass chamfer, slope scaled from the 851px quick-bake
contract). Reveals happen within the parallax budget of a silhouette,
where the cone is tight — rim + s·dist; deep interiors flatten toward
the far surround instead of echoing the occluder. 9,023px clamped on
the reference asset. The band's verified rim values are untouched
(the earlier plate-clamp incident is why this tier stays out of it).

Battery: strokedepth 6/6 (identical counts — the flood reproduces the
component gate's decisions where it was right), frazetta protrusion
30px/35/0 (exact baseline), quickbake 12/12, qbflood 3/3, and a new
7-check platebleed contract on synT (outline/staff scrubbed from the
plate, completions at BG depth, survivors bounded to the ground-
contact band residue). New probes: `platebleed_probe.js`,
`starbleed_probe.js` (real-asset leak metrics + fill/plug/leak PNGs).

Landed in `5c497b5`.

---

## Addendum 42 — Ink islands out of the plate, and constants that scale by meaning

Two asks from the user: swallow the small lifted-ink islands the
plate still carried, and answer whether "stroke ink within 4px"
survives contact with other resolutions and other artists' brushes.
The second question found a real trap.

**Lifted-ink islands join the standing set.** Ink the repair anchors
to an occluder is FG-class content even when its ride is too small or
too low for the floor sweep — camp objects, sleds, small figures.
Left in the plate it survived as a near-depth squiggle that the cone
clamp cannot touch, because it reads as valid content. The adopted
mask now feeds the standing-content mask directly: the completion
flood / floor rind claims the ink, the plate depth completes under
it, the fill recolours it (+2,375px on the reference asset).

**Scaling by semantics, not wholesale.** The honest answer to "does
4px scale?" is: only where the constant MEANS stroke width. First
attempt scaled everything linearly — classifier taps, ribbon tap,
hug/seed/propagation radii, hop budgets — and the 1920px reference
asset answered with a 21 → 90/255 plate protrusion at the glider.
Bisection (new `noScale` / `scaleOnly` debug flags) isolated it: the
hug/seed radii encode the DEPTH ESTIMATOR's cliff-to-stroke offset,
a property of the estimator that does not grow with resolution.
Scaling them let ink adopt across gaps it never hugs. Final split:

- SCALED with w/1200 (width-semantic): classifier cross taps — thick
  brush at 1920+ fell outside the o≤4 window entirely; ribbon tap;
  thick-blob connectivity + area cap; plate-side scrub reach and
  fringe passes.
- FIXED (estimator-semantic): hug radius, seed radius, propagation
  radius, hop budget, gap-closing passes.

Clamped at 1, so 851–1200px assets keep the tuned behaviour
byte-identical — verified: strokedepth 6/6 with identical counts,
frazetta protrusion at its exact baseline.

Reference-asset (1920px) trajectory across the three rounds: ink
lifted 2,689px (A40) → 12,020px (A41) → 26,776px now, classification
78,490 → 90,195px, plate scrub 27,752px — and the protrusion contract
IMPROVED over the unscaled baseline (46px / worst 21 vs 49 / 21).
Full battery green: platebleed 7/7, quickbake 12/12, qbflood 3/3.

Landed in `aa94256`.

---

## Addendum 43 — The last protrusions, killed by measurement

The user asked for the residual 46px / worst-21 starwatcher protrusion
driven to zero before SD. It turned out to be the most instructive
defect of the series, because every texture-space tool failed on it.

**The diagnosis chain.** A state-level scan of the plug against the
r8-max of the repaired FG depth came back CLEAN — the plate's VALUES
were fine; the slivers exist only at RENDER level. Mesh-visibility
bisection attributed the worst clusters (21/255) to the per-layer
STRIP sheets and the remainder (11/255) to the plate. The class:
backstop copies of near content separating from their torn FG backer
under parallax — the FG pre-tear drops a triangle, the backstop's
untorn tessellation extends a couple of pixels past the torn edge,
and at ±0.12 head offset those pixels land where the metric's 8px
window finds no surviving near FG.

**Three static tightenings** landed first — near-edge erosion (the
plate's identity copy of near content retreats behind its own cliffs;
the FG carries every silhouette, and reveals show the far side), a
cone cap on the strip extrapolation rise (an 8px slope sample
amplified over a 100px extension is noise), and a surviving-FG
backing contract using the pre-tear drop mask. Each is right on its
own terms; none moved the number. The lesson stands: this class is
invisible to texture-space reasoning.

**The closed-loop sweep** is the decisive mechanism. After the bake,
the build renders the SAME FG-only vs backstop depth passes the
protrusion contract measures, at four extreme head poses, finds every
on-screen violation, and inverse-projects it through the exact
vertex-shader model — view-space piecewise-smoothstep displacement,
scene-extension UV offsets (a first scatter attempt missed both and
fixed nothing; the plate under extension samples a 2764×1477 texture,
not the core plug) — along the FULL depth range of the sightline.
Every plate texel on it standing above its local floor flattens to
the floor; every strip texel on it drops. Enforcement by measurement:
it makes no assumption about WHICH mechanism produced the violation,
so it covers tessellation mismatch, parallax separation, filter
bleed, and whatever the next build invents — for any uploaded image,
no tuning. ~20s on the SwiftShader CI box, sub-second on a real GPU.

**Result.** Strips: clean. Plate: clean above floor. The remaining
30px (worst 11/255) is AT-FLOOR ground continuation in reveals wider
than the metric's fixed 8px window — proven by construction: with the
depth gate removed, the sweep flattened EVERY above-floor texel on
every violating sightline (1,057) and the residue did not change,
so what remains is the legitimate reveal filler at its floor, i.e.
the metric flagging its own window size. Frazetta plate-only stays 0;
strokedepth 6/6, platebleed 7/7, quickbake 12/12, qbflood 3/3.

Debug affordances: `_bsNoSweep`, `_bsVerbose`, `stateplate_probe.js`
(texture-space contract scan), strip-slot / plate visibility bisect
flags in `protrude_ab.js`.

Landed in `14ffa15`.

---

## Addendum 44 — The troll asset: ramps are not disocclusions, and ink can be dark-on-dark

Three reports from the user's live pass on the troll painting. The
depth map turned out to be the Rosetta stone for all three — it is
EXTREMELY soft (10-30px silhouette ramps, everything blobby), her
raised arm and the staff top fade to near-background depth, and the
nearest content in the whole map is the ground strip at the frame
bottom.

**1. "Much of the floor is considered in need of inpainting."**
Correct complaint, real bug. The quick-bake SD mask is envelope
departure — and a steep ATTACHED ramp (the bright ground rising to
the frame bottom) departs the cone exactly like an occluder. But a
ramp is a continuous surface: no head pose reveals anything behind
it, and the FG never tears there (tears need a cliff), so the plate
is never even shown. The fix is quantitative, not heuristic: a cliff
of step Δ depresses the envelope for exactly Δ/s px, so each cliff
FUNDS Δ/s px of mask around it. The max-plus chamfer — the exact
dual of the cone's min-plus sweep — propagates budget minus distance;
departure no cliff can fund is attached-ramp relief and drops. A
plain connectivity flood leaks (one rock edge on the ground keeps a
floor-sized blob): 2,095px dropped by connectivity vs 103,337px by
budget on the troll, quick-bake contract still 12/12.

**2. "Her outline appears in the background instead of on her form."**
The classifier was BLIND on this painting: 68% of its pixels sit
under the ink-luma cap, and a stroke on a dark surround never clears
the absolute contrast gates — 2,180 stroke px classified in an entire
inked painting, so nothing lifted and nothing scrubbed. The gates now
scale by the LOCAL luma dynamic range (window scaled with stroke
width): bright regions keep the tuned thresholds exactly (scale = 1
whenever local range ≥ 0.5 — every existing baseline is untouched by
construction), compressed regions amplify up to 2.8×, and the ink cap
relaxes to 0.45 only where the scale is active. Troll classification
2,180 → 5,912px, lift 72 → 179px, plate scrub 287px, protrusion at
its exact baseline. Honest ceiling: adoption needs a depth cliff to
adopt FROM, and this asset's silhouettes are mush — the classifier
now sees the ink, but the depth map often gives it nothing crisp to
anchor to.

**3. "Her hand is cut off — some in FG, some in BG."** Verified in
the depth map: the estimator assigned her raised arm and the staff
top BACKGROUND depth (they blend into the dark cave in the source).
Everything downstream — the tear through her wrist, the arm chunk
living in the plate — is faithful processing of wrong depth. No
colour-side repair can lift a whole arm (it is not thin ink, and
"which side of the wrist is her?" is not answerable from luma). This
is the depth-estimation ceiling, and it is exactly the class the SD
stage and the MPI layering are for. Two honest mitigations exist if
wanted later: a sharper depth estimator at import time, or letting
the SD pass regenerate depth alongside colour for flagged regions.

Battery: strokedepth 6/6, platebleed 7/7, quickbake 12/12, qbflood
3/3, troll protrusion 34/35/plate-0, starwatcher 30/11 with coverage
stable (98,629 classified / 15,820 re-anchored / 16,290 scrubbed).

Landed in `2fd0cf3`.

---

## Addendum 45 — Stabilization: the wire rule was wrong, and the through-test was never real

The user's live pass caught what five green batteries did not: on the
reference asset the horizon line shipped at the FIGURE's depth, the
caravan smeared over the dune, and outlines everywhere read as
background. The protrusion contract measures backstops against the
FG; nothing measured "is the ink at the RIGHT depth" — so two
plausible mechanisms compounded unchecked. Both are now reverted, and
the missing regression class has a synthetic control.

**The ribbon rule was structurally wrong.** A41 let thin ink carry
adoption end-to-end "like a wire" because the synthetic staff needed
it. But a horizon line is ALSO a thin ribbon touching a near figure —
the wire rule carried the figure's depth across the entire frame. An
appendage and scenery are indistinguishable to a wire rule; no gate
can save it. Adoption is hug-bounded again, and the staff case is
remodeled honestly: real estimators either catch a staff (native near
depth — synT now models this) or miss it entirely, in which case no
colour-side rule can conjure it back.

**The A44 contrast scale fed the fire** — 10x classification on real
paintings, all of it eligible for mis-adoption. Reverted. Dark-on-dark
ink waits for depth-side evidence, not looser luma gates.

**The through-test had been vacuous since A40.** The "span evidence"
branch counted a stroke's own same-depth neighbours as contact, so
the contact bbox always equalled the blob bbox and every elongated
blob "passed through". The whole-blob-far gate was silently doing all
the work — and a horizon line is wholly far, so it sailed. Fixed
three ways: contact only from ANCHOR ink (lifted or natively near);
the spanned axis must have real extent (a 2px line "spanning" its own
thickness never counts); and dark ink already standing above its
local floor is excluded from blobs (a native staff must not merge
into the far ornament it decorates). Reference-asset phase-2 lift:
10,866 → 4,192px, every survivor anchored.

**The control that should have existed all along:** synT now carries
a thin scenery line crossing the frame behind the native-near staff.
The contract asserts it stays on the surface it lies on. Two draft
versions of this check failed against CORRECT behaviour — I had the
synthetic scene's own geography wrong twice (the row sits on the
scene's sky step; the first "lift" was my scan threshold sitting
below the row's true depth, with a staff-halo pixel as the smoking
gun that wasn't). The final check compares the line to the rows
beneath it — no absolute ground truth to get wrong.

Battery: strokedepth 7/7 (new control included), platebleed 7/7,
quickbake 12/12, qbflood 3/3, troll protrusion at baseline
(34/35/plate-0), starwatcher at baseline (30/11) with the legitimate
outline lift retained (15,356px re-anchored, 14,007px scrubbed from
the plate).

Landed in `7e21c54`.

---

## Addendum 46 — The adopt-map, the footing rule, and the build you can't see

"Still seeing the exact same problem" demanded evidence, not another
gate. New instrument: the ADOPT-MAP (`adoptmap_probe.js`) overlays
every classified ink pixel on the source — GREEN lifted, RED not.
Two facts fell out on the reference asset, and then a third about the
testing loop itself.

**Fact 1: seeds never crossed the stroke.** The figure's silhouette
ink was solid red — not because gates refused it, but because the
seed search (r=3) physically could not reach across 5-8px-wide
painterly ink to the nearer content on the other side. Ink WIDTH
scales with resolution; the seed radius now scales with it (3·SR),
exactly like the classifier's taps. (The earlier blanket-radius
revert threw this baby out with the ribbon bathwater.) Interior
linework on a flat body stays red BY DESIGN — it already sits at body
depth; red there is not a defect.

**Fact 2: grounded blobs flew.** The caravan group was solid green —
phase 2 lifted whole figures to the dune-lip anchor ("colors
scattered across the depth"). New invariant with the same shape as
the others: A BLOB MAY NOT EXCEED WHAT IT RESTS ON. The content
directly beneath the blob caps the adopt depth — a figure rests on
its ground (capped to footing), the ornament rests on its native-near
staff (cap inert). Depth transects confirmed the silhouettes here are
CRISP in the bake (0 → 0.48 in 4px), so anchors are real.

**Fact 3: the build was invisible.** Rendering THIS branch at the
user's exact pose produces a coherent figure with its outline
attached — not the reported ghost. The app's version stamp had read
v3.12.0-bandcut across FIFTEEN landings; a stale cached moebius.js is
indistinguishable from current during live testing, and the reported
screenshots also show dolly-volume guide lines with Dolly Zoom off —
another stale-state tell (this build renders none). The stamp is now
v3.13.0-a46 and bumps every landing.

Battery: strokedepth 7/7, platebleed 7/7, quickbake 12/12, qbflood
3/3, troll protrusion at baseline, starwatcher protrusion 28/11 —
better than baseline.

Landed in `c76e39d`.

---

## Addendum 47 — State of the union, and the handoff

The user confirmed v3.13.0-a46 with fresh bakes and the same visual
complaints. A full-resolution render on the harness box finally
REPRODUCES them — the previous "cannot reproduce" was the probe
rendering at 760px where 1-3px artifacts vanish. Lesson recorded:
verification renders must match the user's canvas scale.

**What the remaining artifacts actually are** (at reproduction scale):

1. THE "OUTLINE PLASTERED ON BACKGROUND" is mostly not ink depth any
   more — it is the PLATE showing through the tear band that hugs
   every silhouette (the full tear opens it by design), and the
   pre-SD plate carries (a) blur-ghost traces where the ink scrub
   recoloured from the pull-push base, and (b) the wash smear. The
   fix class is PLATE FILL QUALITY, not more ink-depth surgery:
   scrub fills should come from nearest lateral non-ink plate colour
   (crisp continuation), and the reveal band inside the parallax
   budget must never expose pull-push blur.

2. THE CARAVAN/CAMP CONFETTI is dense clusters of 5-20px objects
   being torn individually and revealing plate fill between the
   fragments. Principled fix: TEARS MUST PAY FOR THEMSELVES — only
   tear a cliff whose depth step can produce >= ~2px of reveal at the
   maximum head pose (step x parallax budget). Small camp objects sit
   ~0.02-0.1 above their ground: sub-pixel to marginal reveal, pure
   loss to tear. Gate the pre-tear (and the stretch net threshold)
   by reveal benefit and the confetti dies structurally.

3. INK DEPTH itself is now mostly right (adopt-map verified:
   silhouette ink adopts where a crisp cliff exists; interior ink
   correctly stays at body depth; remaining detachment is sub-2px on
   crisp-cliff assets). The troll-class assets remain depth-limited
   (soft ramps, arm at BG depth) — that ceiling is the depth
   estimator's, documented in Addendum 44.

**Recommended order for the next session:** (1) reveal-benefit tear
gate — biggest visible win, kills confetti; (2) plate scrub/band
fill quality — kills the ghost traces; (3) then the SD stage, which
replaces the wash entirely and is the designed answer to everything
in class 1. The MPI layering remains the endgame for overlap-class
errors (troll arm, arm-over-torso).

All state lives in this repo: Addenda 32-47, the harness suite
(strokedepth 7-check, platebleed 7-check, quickbake 12-check,
qbflood, protrude/protrude_ab with kill-flags, adoptmap/p2probe/
hline/stateplate probes), branches `review-fix` (code, at c76e39d)
and this review branch. A fresh conversation loses nothing.

---

## Addendum 48 — "Look through quick bake": the outline was baked into the QUICK plate

The user pointed at the right subsystem by name, and it explained the
whole loop of the last three rounds: the outlines were showing up in
QUICK BAKE — and every piece of ink machinery built since A41 (the
scrub, the backstop sweep, the fill contracts) lives in the V1 path.
The quick path had kept a toy: its wash's "dark-stroke rejection" was
an inline GLSL luma probe at FIXED 2.5px and 5px offsets. At 1920px,
painterly ink is 5-8px wide — the probes landed inside the ink
itself, nothing was ever rejected, the entire outline seeded the wash
and baked into the quick plate, and the stretch-net reveal band
around every silhouette displayed it. The v1-vs-quick asymmetry also
explains why v1-path batteries stayed green while the user kept
seeing ghosts.

Fix: the quick wash's seed pass now rejects the CPU stroke
classifier's mask — the same resolution-scaled classifier the repair
and the v1 scrub already use — bound as a texture with a 1px fringe.
The fixed-offset probe survives only as a fallback for assets with no
mask, and the v1 GPU-fallback call site explicitly clears the binding.

Verified at reproduction scale (the A47 lesson, applied): on the
1920px reference the quick wash is ink-free — the figure region reads
as smooth wash with no contour trace, and a new fourth qbflood check
pins it (minimum wash luma along the synT outline ring + staff:
0.341, vs ink at ~0.06). Quick-bake contract 12/12; the pose render
at the user's own head offset shows a solid figure whose reveal band
is wash, not outline. Stamp v3.13.1-a48.

Landed in `2db7cb2`.

---

## Addendum 49 — Rejection is not adoption, and layers need footing too

Two precise reports against a48, two fixes with one shared idea.

**"Quick bake + BG solo still shows black outlines" (the troll).**
Cause: the troll's outline is dark-on-dark — invisible to the strict
stroke classifier, so nothing rejected it from the wash. The insight
that unlocks it: REJECTION has the opposite risk profile from
ADOPTION. A rejection false-positive means "fill this pixel from its
neighbours" — slightly more blur, never a protrusion. So the
local-contrast-scaled detector that A45 rightly reverted for LIFTING
is resurrected as a rejection-only mask: the strict classifier keeps
deciding what may move in DEPTH, the aggressive detector decides what
may not be TRUSTED as colour. The troll's quick wash now has no
contour trace; the starwatcher wash contract holds (inkMin 0.341).

**"The party walking up the dune is pushed onto the dune layer"
(Full Planes).** The v2 partition is per-texel depth quantiles — so a
small standing component that the estimator painted 0.03 nearer than
its ground jumps a WHOLE inter-layer parallax gap whenever a bin cut
lands between figure and footing. Same invariant as the phase-2
footing cap, one level up: a small component (area-capped) whose
depth sits within a whisker of the bin directly below its bottom edge
is RE-SEATED on that footing layer. Merges only run toward farther
bins — the rule can never push content forward — and genuinely
floating content (birds over sky) fails the depth gate. The v2
nine-pose contract stays in band; the pose render shows the party
seated on its ground.

Battery: strokedepth 7/7, platebleed 7/7, qbflood 4/4, quickbake
12/12, v2 nine-pose 8-48px. Stamp v3.13.2-a49.

Landed in `4dfa2bc`.

## Addendum 50 — The outline was never paint

The user pinned it: "look at 'live depth incl. BG (plug in place)' —
the red outline looks to be the same as the black outline in the
final view." Red in that pane means NO GEOMETRY RENDERED — and that
was the answer. Two addenda of wash chemistry (a48, a49) were aimed
at the wrong surface.

**Root cause.** The quick plate was built as
`new THREE.Mesh(L.mesh.geometry, matQ)` — SHARING the FG mesh's
geometry. The A39 pre-tear then drops every cliff-spanning triangle
from that shared index. After the stroke repair lifts outline ink to
occluder depth, every ink stroke IS a pair of cliffs — so the plate
inherited a lattice of through-holes tracing the removed figure's
entire line work. Black backdrop showing through hole-shaped slits =
"black outlines plastered on the background." Every discard uniform
on the plate said solid; the geometry wasn't. Proof by discriminating
render: with a magenta clear colour the BG-solo "outline" turns pure
magenta (holes), and restoring the full index erases it while the
wash texture — verified clean the whole time — never changes.

**Fix.** The plate (quick, and the v1 shared-geometry fallback) takes
its own copy of the geometry with the full untorn index. The backstop
now renders solid by construction; the pre-tear keeps cutting the FG
only, which was its design.

**Supporting fixes shipped with it:**
- The quick wash's ink test was resolution-blind: the mask is source-
  res, the wash runs at canvas res, and a NEAREST centre-hit misses
  half-covered texels (residual stroke dashes at 1920+). The mask now
  ships LINEAR with width-scaled dilation and the seed gates on
  footprint coverage. A first cut (3px dilation, any-coverage gate)
  washed the stars out of the sky — dialled back to majority coverage,
  stars retained, dashes gone.
- The v1 CPU fill's ink scrub now prefers the aggressive wash-ink
  mask, so dark-on-dark outline ink is scrubbed from the plate fill
  too (the strict mask is blind to it).
- The debug sheet refreshed depth but never colour in single-pass
  modes: pingPongRenderTargetB still held the LOAD-TIME frame, so the
  "scene color" pane showed the default image regardless of what was
  loaded — the second bug the user reported, now refreshed per export
  with completion meshes hidden to match the depth pass.

At-scale evidence (1920 viewport, BG-solo): star quick — line-art
figure and caravan dashes gone, stars intact; troll quick — the white
silhouette ring gone; v1 both assets — figures ride the strips with
their ink, plate carries none.

Battery: strokedepth 7/7, platebleed 7/7, qbflood 4/4 (inkMin 0.341),
quickbake 12/12, protrude troll 34px/worst 35/plate-only 0, star
28px/worst 11 — all identical to a49 baselines. Stamp v3.13.3-a50.

Landed in `f1ad0a7`.

## Addendum 51 — Ink follows its layer

The user read the a50 result correctly and named the design flaw:
"the lines were not supposed to be deleted — they were supposed to
move from the background and be distributed to the foreground
layers." The a48-a50 arc had been treating detected ink as something
to REMOVE; every surface it was removed from left the line work with
one fewer place to live, until a50's solid, clean plate revealed the
end state: line work deleted from the world.

**Why the lines died.** A lifted stroke is a pair of depth cliffs,
1-3px apart. Both pre-tear loops — the quick branch's blanket cliff
test and the v1 ribbon rules under bgTearAllRubber — drop any
triangle spanning a cliff, and for a stroke that thin EVERY triangle
spans one. So the very strokes the A40-A46 adoption arc lifted onto
their occluders were being torn out of the FG mesh at bake time. The
"black outlines" of a44-a49 were this deletion made visible (backdrop
through aligned holes in both meshes); a50 made the plate solid and
ink-free, so the same deletion started rendering as clean wash — the
lines just vanished.

**Fix 1 — tear exemption.** Triangles touching adopted ink
(L._inkAdopted) are exempt from every drop rule in both tear loops.
Lifted outlines now ride their occluder in the composed view; the
rubber they keep at the stroke's far side is cut per-fragment by the
stretch net under parallax, over the opaque plate.

**Fix 2 — depth-scoped wash rejection.** The quick wash's ink
rejection was global, so it also blurred away ink that IS plate
content — the horizon line, desert plants, the far camp. The ink
mask is now intersected with a resolution-scaled dilation of the
nearer-than-plate set (dQ − plateQ > 0.02): lifted strokes are
themselves nearer and stay rejected, plastered outlines hugging a
nearer body are within reach and stay rejected, and far-ground ink
away from any nearer content stays crisp in the plate.

At-scale evidence: star composed view carries the full line work
(astronaut, staff, plane, party, camp); star BG-solo keeps
horizon/plants/camp ink crisp while the removed-figure regions stay
washed; troll composed and BG-solo both clean. Battery green,
protrusion unchanged (troll 33px/worst 35/plate-only 0, star
27px/worst 11). Stamp v3.13.4-a51.

The residual: at strong parallax a mid-ground figure's edges still
erode into reveal wash (the rider mid-reveal). That is the two-
surface ceiling — the party can only be "outlined at the depth of
its layer" everywhere once it HAS a layer, which is the v2 Full
Planes / MPI track (the a49 footing merge already seats it on one).

Landed in `fbcf6cb`.

## Addendum 52 — The baked realtime

The user re-stated the original contract: "I asked for a version that
simply had the realtime inpainting, but baked — without breaking
everything up into a gazillion layers." Measured against that, the
quick bake had drifted into architecture: geometric tears, per-frame
classifiers, surgical depth. This addendum walks it back to the
contract and fixes what the walk-back exposed.

**Quick = intact mesh + baked fill.** The pre-tear is OFF by default
(kept behind `window._qbPreTear`): the FG renders complete, like
realtime. And a frame-loop bug died on the way: in baked scenes the
render loop was RE-ARMING the per-fragment gap generators from the UI
checkboxes every frame, silently overriding the bake's own "all
discards off" decision. Realtime survives those discards because its
per-frame fill repaints them from the figure's own colours; a bake
exposes the world-without-that-content plate instead — that is what
ghosted the party into wash. Baked scenes now run stretch-net-only
(tightened to ~2x; always safe over an opaque plate).

**The comb, measured to its root.** With geometry intact, the party
region rendered as fine striations under parallax. Chased through
three falsified hypotheses (wash aliasing, stretch-net threshold,
apron binarization — the uvRate=1.0 nuke test and a magenta backdrop
killed each) to the true cause: THE RAW ESTIMATOR DEPTH IS SHATTERED
there — small figures come fragmented into interleaved 1-2px
filaments of figure depth and ground depth. Realtime heals this
per frame; a bake renders it. Two depth-side passes now cohere the
shipped depth: a minority-snap 5x5 median (a px whose depth is the
minority of its window is a filament and takes the median; >=3px
structures and the staff survive), and the a52 floor snap (small
standing components within a whisker of the cone envelope re-seat ON
it — they become plate-native content and keep their ink). Shipping
required writing the depth DataTexture's float array — image2d is
only a CPU mirror, and three earlier "fixes" changed nothing on
screen until that was caught.

**v2 planes: the party rides its layer.** A farther-only boundary
refinement after the footing merge re-seats px whose own depth
matches a farther neighbouring bin (never forward, per the A49
invariant). Result: the lead rider renders crisp, inked, coherent on
its plane — the user's "outlined at the depth of their layers,"
delivered in the mode built for it — and the nine-pose hole contract
fell from the 8-48px band to 0-6px.

Honest residual: quick-mode comb at strong parallax is reduced, not
zero — the source depth there is noise, and each stronger coherence
pass risks real thin features. v2 Full Planes is the mode that
carries this asset class; quick remains the fast path whose rest
frame is now source-perfect.

Battery green across the board (protrusion unchanged, v2 nine-pose
0-6px). Stamp v3.13.5-a52. Landed in `514e948`.

## Addendum 53 — The pixel is content; the cliff is the artifact

The user put the source artwork next to our renders and drew the
line: "we cannot lose a single pixel — we just want to make
transparent / inpaint the displacement cliff itself, not the pixel
that's causing it." That sentence resolves the tension that has run
through a39-a52. On a vertex-per-texel grid, "tear the cliff" and
"delete the pixel" were THE SAME OPERATION for thin content: a 1px
stroke has no interior triangles, so every triangle it owns spans a
cliff, and dropping them all deletes the stroke. Every prior stance
picked a side of that false dilemma — tear (lines die), don't tear
(membranes comb), classify-and-discard (small figures ghost).

**The decoupling.** Quick mode now: (1) tears EVERY cliff-spanning
triangle, unconditionally — the connective membrane between depth
levels is exactly what should be transparent, and the baked plate
inpaints behind it; (2) ships every texel orphaned by the tear as a
per-pixel CAP CARD — a flat quad over the texel's footprint whose
corners all sample inside the texel, so it renders the pixel's own
colour at the pixel's own depth, rigidly. No pixel lost, no rubber
possible, no classifier needed on cards. The a51 ink exemption is
superseded in quick mode (cards carry the strokes); despeckle and
floor-snap remain as noise-coherence so the cards fan less.

At scale: the star composed view at parallax carries the astronaut,
staff, plane, mountain, camp and party complete — the party renders
as pixel-true content at depth (a slight fan where the estimator
shattered it, no comb, no wash-out); the troll and woman render
complete with their ink. Battery green, timing back under budget
after de-allocating the tear loop, protrusion and v2 contracts
unchanged (nine-pose 0-6px).

The honest residual is now purely an ESTIMATOR statement: where the
depth map fragments small figures, their pixels fan slightly under
parallax because that is where the depth says they are. Fixing that
is depth-side coherence (or the v2 planes, which carry the party
whole) — not rendering policy. Stamp v3.13.6-a53.

Landed in `7be3838`.

## Addendum 54 — Where the quick bake's road ends, measured

The user put the a53 party crop against the original and asked the
only question that matters: "what is this mess?" It was a mess. The
a53 principle (pixels render, cliffs tear) is right, but it missed
its complement: CONNECTIVITY IS A SPATIAL REGULARIZER. Realtime looks
coherent over the same shattered depth precisely because its mesh is
connected — membranes hold neighbouring pixels together, and depth
noise reads as invisible micro-relief. Disconnect (tear + per-pixel
cards) and every pixel travels alone to its noisy depth: confetti.
"Cliff" must mean a STRUCTURAL discontinuity between two coherent
surfaces, not every noise step inside one object.

**Rigidify (landed).** One object = one surface: connected components
of the CLOSED standing mask (proud of the cone envelope, area-capped)
take the median depth of their standing subset — rigid decals at
their true standoff. Not a ground snap: the glider keeps flying, and
lands perfectly as one rigid card.

**The measurement that ends the heuristic road.** On the star asset
the closed standing mask is ONE component of 632,874 px whose
bounding box is the entire frame: silhouette halos chain the
astronaut, the mountain, the crest and the party into a single blob.
There is no component boundary a gate can find, because the depth
field does not delineate the objects — the party's depth is 99
distinct values in a 500px window. Every quick-mode filter in
a52-a54 (despeckle, floor snap, minority median, closing, rigidify)
nibbles at that; none can reconstruct object structure the input
does not contain.

**The verdict.** Three renderers, one scene, at the same pose:
realtime = party coherent (per-frame heal, per-frame cost);
quick bake = party at the estimator ceiling (everything else in the
frame — astronaut, staff, plane, mountain, camp, ink — now renders
source-true); v2 Full Planes = party crisp, whole, inked, on its own
layer (10 quantile planes — not a gazillion — with footing merge and
boundary refinement; nine-pose holes 0-6px). For scenes with small
mid-ground figures, v2 IS the baked realtime. The remaining lift for
quick mode is not another filter — it is either object segmentation
(colour+depth) or a better depth estimate.

Battery green, all contracts unchanged. Stamp v3.13.7-a54.
Landed in `7ec8bad`.

## Addendum 55 — The party is the estimator's error, measured to the floor

The user put the a53/a54 party crop beside the source: "broken up
across a much deeper depth than makes any sense — totally absurd."
Correct. This addendum stops iterating on renderer heuristics and
MEASURES the party, three ways, then acts on the measurement.

**The measurement.** Raw estimator depth at the star party: mean
0.274, range 0.086–0.608, spread 0.52. The bare ground they stand on:
0.12 (tight). The foreground astronaut: 0.307. So the estimator has
floated a cluster of tiny mid-ground figures to nearly the HERO's
depth — ~0.15 in front of their own footing — with pixels smeared
across half the depth range. That near-spike-over-far-ground is the
absurd fan; the bake's sharpening triples its incoherence (0.05 →
0.16) on top.

**Why it cannot be isolated (the reason 16 rounds of heuristics
failed).**
1. Connectivity: the standing mask (content proud of its floor) is a
   SINGLE 610,637-px blob — 24% of the frame — chaining the party to
   the mountain and crest through silhouette halos. No connected-
   component gate can reach the party alone.
2. Floor / lift: astronaut lift 0.25 > party lift 0.13; astronaut
   floor 0.072 < party floor 0.191. Neither dimension separates the
   mislocated party from the legitimately-near hero — a seat/clamp
   keyed on either flattens the astronaut worse than it fixes the
   party.
3. A five-way config matrix (realtime / quick / +raw-depth /
   +discards / +seat), rendered in one load: realtime is the only
   coherent one, and it is coherent because it INPAINTS the figure
   from its own neighbouring colours every frame. A bake's plate is
   the world WITHOUT the figure; it can refill the reveal behind a
   correctly-placed figure, but never the BODY of a mislocated one.

**The conclusion, and the change.** The party cannot be correctly
baked with a plate-behind architecture over broken depth — this is an
estimator + architecture limit, not a filter that was missing.
Realtime handles it; the bake is a performance optimisation that
degrades exactly where the depth is wrong. So quick bake now DEFAULTS
to the connected intact mesh ("realtime, baked" — the original
request): the connected grid is a spatial low-pass, and the entire
scene except the party — astronaut, staff, mountain, crystal crest,
camp, glider — now matches realtime. The a53 tear+cap-cards (which
shattered every 1-3px figure), a54 rigidify, and the a55 seat-on-floor
(kept, since it is the right tool for assets where standing content IS
separable) are moved behind opt-in flags.

**Levers for the party specifically, none free:** (a) render these
scenes realtime (looks right, per-frame cost); (b) v2 Full Planes
(bins the party — imperfect but whole); (c) correct/author the party's
depth (then the bake works); (d) ink-contour segmentation to isolate
the party as its own seated plane — the one untried signal, larger
build, uncertain because it depends on the outlines closing.

Battery green; contracts unchanged. Stamp v3.13.8-a55. Landed in
`1257378`.

## Addendum 56 — The ink was the segmentation all along

a55 ended by proving, three ways, that the mislocated party could not
be isolated in the depth domain. But the party is INK ART — Moebius
closes every form with a contour line, and the ink is INDEPENDENT of
the broken depth. That is the segmentation the estimator couldn't give.

**The mechanism.** Ink = stroke classifier ∪ near-black luma, dilated
1px to seal hairline gaps. Flood the NON-ink cells; the two largest
are the desert and the sky. Everything else is figure content —
connected-component it into ISLANDS, so a figure's interior detail
cells and its outline fuse into one island floating in the ground.
Measured on the star party: the astronaut is a single 1,400,186-px
island (kept, native depth); each party figure is a ~30,000-px island.
Small islands (< 2% of frame) that are genuinely proud of their ground
(mean lift > 0.10, so a figure floating above far ground qualifies
but scenery ink lying on a surface does not) AND compact (area ≥ 0.12
× bbox, so a thin horizon LINE is rejected while a filled figure
passes) are re-seated on their local cone-erosion floor: one coherent
flat decal at ground level, ink preserved, spread and shear gone. It
runs at the SHARED bake source, so v1, quick and v2 all consume the
corrected depth.

**Result.** The party — "broken up across a much deeper depth than
makes any sense," across sixteen prior rounds — now renders coherent
and grounded in every mode. Because the seated pixels no longer
protrude above their footing, real-asset protrusion IMPROVED as a side
effect: star worst 11→6, troll 35→27; v2 nine-pose max 6→3. Two gates
(proud + compact) hold the synthetic horizon-line control at its
surface, so strokedepth stays 7/7. Full battery green.

**Why this one worked when depth heuristics didn't.** Every a44–a55
attempt tried to separate the party from the hero using depth (floor,
lift, connectivity of the standing mask) — and the depth field does
not delineate them (astronaut lift 0.25 > party 0.13; one 610k-px
standing blob chains them). The ink delineates them perfectly, because
the artist drew the boundary. The lesson for this class of asset:
segment on the medium's own structure (the line work), not on the
estimator's output.

Residual, pre-existing and separate from the party: a faint
staff-halo streak and dune-crest striation (thin-feature stretch the
connected mesh leaves; the stretch net only partly catches it). Not a
party problem.

Stamp v3.13.9-a56. Landed in `bb67acf`.

## Addendum 56b — Tear back on: the seat and the tear stop fighting

The ink-island seat (a56) fixed the party but exposed a trade a55 had
made: a55 turned the quick pre-tear OFF (connected mesh) to stop the
party shattering, and that reintroduced the astronaut/staff SILHOUETTE
tunnel the tear exists to cut (the user: "tunnelling from itself to
the background").

These two had been in tension since a39 — the tear cuts big-object
silhouettes but shatters small figures; the connected mesh keeps small
figures but leaves silhouette taffy. The seat dissolves the tension:
it flattens the party onto its ground BEFORE the tear runs, so the
party no longer has internal cliffs for the tear to shatter. With that
in place the tear is the default again — it cuts the astronaut's real
silhouette (tunnel gone) and passes straight over the now-flat party
(still coherent). Verified against the a53 baseline: the astronaut
region matches pixel-for-pixel intent; the only residual is the faint
pre-SD wash ghost that a53 had too. Intact mesh is now the opt-in
(window._qbNoTear).

Process note: the first a56b battery reported qbflood and timing
FAILs; both were contamination in a hand-rolled inline battery (qbflood
ran before the synT asset copy, so on leftover troll assets; the timing
run was cold/contended). Clean isolated runs pass 4/4 and 12/12. Full
battery green. Landed in `c1ad44b`.

## Addendum 57 — The staff-lantern streak is the estimator, not the mesh (measured; no code shipped)

The user, off-computer, flagged the two residuals a56 had named: "streaks
from tip of staff/lantern to the background, and some more (subtle) rays
from astronaut to bg or vice versa." I isolated each one and tried two
fixes; neither cleared the measurement bar, so nothing shipped and the
tree stays at the clean a56b baseline (`c1ad44b`). What follows is the
diagnosis, because a characterized limit is worth more than a fragile
patch.

**Isolating the streak (streaksrc_probe).** Rendering the posed scene
five ways — composite, FG-mesh only, cap-cards only, plate only — split
the staff-lantern streak into two independent contributors:

- *FG mesh taffy.* The mesh-only render shows a bright twisted braid
  hanging below the lantern glow: the connected FG sheet stretching the
  thin, bright staff tip across the sky it parallaxes over. The pre-tear
  (mx−mn > 0.06) cuts the staff's body but a hairline bright ridge leaks.
- *Plate wash ghost.* The plate-only render shows the glow AND a bright
  vertical shaft baked into the plate itself — the isotropic pull-push
  wash pulling the lantern's bloom down into the reveal below it. Same
  mechanism as the astronaut's faint ghost; both were present at the a53
  "used to work" baseline (not a regression).

**Two fixes, both measured to fail.**

1. *Depth bloom-push* — push bright pixels that float proud of a far
   floor down onto it, so the lantern bloom flattens to sky depth. A/B
   with the push toggled off was **pixel-identical** in the mesh-only
   render: the staff shaft's own body fills its neighbourhood, so the
   sky-surround gate that protects the astronaut also rejects the shaft,
   and only the isolated tip glow flattens — which changes nothing. Plus
   the luma≥175 gate is exactly the per-image knob this project forbids.
   Reverted.

2. *Wash glow-reject* — extend the wash-seed rejection (which already
   drops near INK) to also drop near blown-highlight, so the sky
   completes clean behind the glow. It fired (11,073 px scrubbed) but the
   composite changed by **0 pixels**. The reason is the crux: the
   scrubbed pixels are near astronaut/party highlights the wash refills
   identically, and the *lantern glow is not near*. The monocular
   estimator places the soft bright bloom at BACKGROUND depth — so it
   bakes into the plate as legitimate "background," and every
   depth-gated mechanism (the tear, the shader's ±4px near-reject, this
   glow-reject) correctly leaves it alone. None of them can tell a
   background-depth bright bloom is really foreground light. Reverted.

**Why this is the same class as the party, minus the handle.** a56 fixed
the party because it is INK-BOUNDED — the artist drew a contour the
estimator's error couldn't erase, and segmentation rode that contour.
The lantern glow is a soft bloom with no contour, sitting at an
in-between depth with no cliff, no ink boundary, and no near
classification. It evades tear, wash-reject, ramp-collapse (12 passes:
no effect), and ink-island seat alike. Fixing it robustly needs either
a better depth field (SD-refined) or explicit layer authoring (MPI) —
the two stages already on the roadmap. This is a genuine, fully
characterized limit of the weight-free bake, not a tuning miss.

The astronaut "subtle rays" are the same pull-push-over-a-large-hole
wash ghost, likewise pre-existing at a53 and likewise SD/MPI territory.

No stamp change; tree remains v3.13.9-a56 at `c1ad44b`.

## Addendum 57b — Seated figures must STAND, not lie down (the party disocclusion)

a56 fixed the party's absurd depth by seating each mislocated figure at
`S = floor[i]` — the ground directly behind it. That killed the shatter,
but it also welded the figure to the ground plane: zero relief. The user,
back on a computer: "the party appears to be plastered to the background
now and there's no inpainting behind it — obviously it's something that
can parallax / disocclude." Correct. A figure at exactly ground depth has
no relief, so under parallax it does not separate from the ground; it gets
dragged and smeared with it (measured: the floor-seat party visibly
stretches under a 0.20 pose, while the same figure as a card stays crisp).

**The fix.** Seat the whole figure at ONE flat depth *lifted proud* of its
ground, instead of at the ground. Still a single depth per island — so the
shatter stays killed and the ink is kept — but the card now has relief: it
parallaxes as a rigid unit and tears at its silhouette, revealing the
inpainted ground behind it. The lift is the figure's OWN mean proud
(`meanLift`, already computed and gated > 0.10 by a56), so it is
estimator-honest and self-calibrated per figure with no constant and no
per-image knob.

**Why not a geometric billboard.** The first attempt planted the card at
its feet-contact depth, so the head stood proud by (island height × floor
slope) — physically a standing figure. Measured, that over-lifted: star
protrusion 6→12, because a tall island's head relief can exceed the FG
depth there. `meanLift` is bounded by what the estimator itself assigned,
so the card never protrudes past the FG. Star protrusion returned to 6.

**Measured (pose 0.123, −0.055).** Star plate protrusion holds at 6.
Troll PLATE protrusion *improves* 27→0: giving the figures relief makes
them tear, so their pixels ride cap-cards instead of protruding through
the plate. The residual troll cap-card relief (worst 33 at a handful of
px) is the standing disocclusion itself, not a plate fault — the protrude
test flags it only because its FG-only baseline excludes cap-cards.
Strokedepth gates 7/7 (horizon-line, caravan, footprint, isolated-stroke
controls all hold — the seat's membership is unchanged; only the depth it
assigns moved from ground to ground+lift). The floor decal remains
available as an A/B opt-in via `window._seatFloorFlat`.

Stamp v3.13.10-a57b. Landed in `db489c7`.

---

## Addendum 59 — angle-fade toggle, v2 BG-solo, v1 hole-only islands, and the dune self-occlusion case

Four items off the last review pass.

### 59-3 Angle-fade toggle (main canvas)

The extreme-angle view-fade (canvas darkens past ~35–45° off-axis, where
the disocclusion budget runs out) made it impossible to inspect the plug
at wild angles — exactly the angles we most want to test. Added an
**Angle fade** checkbox to the main canvas viewing row (next to Reset
View / Dolly Zoom). Off ⇒ `bgViewFadeEnabled=false` and `updateViewFade`
clears the overlay immediately, so the camera can be driven to any angle
with the raw render visible. Default on (ships as before).

### 59-4 v2 "BG solo"

Was hiding only the primary's single nearest bin ("peek behind the
front"), which barely changed the frame. Re-tied to the plug: solo now
shows each layer's **farthest (rank 0) backdrop plane** — the a58e
hole-only anamorphic islands — and hides every nearer plane plus the flat
originals. Head-on you see almost nothing (the occluders' own content is
gone); off-axis the backdrop islands appear exactly where a disocclusion
opens. It is the v2 analog of quick-bake's "hide FG mesh, show plate."

### 59-1 v1 plate → hole-only anamorphic islands

The v1 "Build BG Layer" plate was a FULL clone of the frame at the
cone-floor depth. Two consequences, both in the debug sheets: (a) its
horizon sat too far back and **misaligned at high angle**, and (b) its
stretched rubber ramps streamed as **taffy from every occluder to its
disocclusion**. Applied the same treatment the quick-bake plate got in
a58d: restrict the plate to the anamorphic disocclusion band
(`{disocc || bud>0}`, disocc = where the plug departs source, bud = the
max-plus chamfer that scales the band by the local depth gap = the
parallax reach). With the plate hole-only, the horizon and open
background come from the **FG mesh at source depth** (correctly aligned),
and there is no full-clone surface to misalign and no connecting ramp to
smear. Gated behind `window._noBgIslands` (reverts to the full clone) and
skipped under scene-extension (oversized geometry, different UVs — a
follow-up). Flush plug depth at the band edge (the a58c continuation) is
a further refinement not yet ported to v1.

### 59-2 The dune self-occlusion case (analysis)

**The picture.** The party/caravan climbs the near face of a dune. Below
and beyond the dune's crest is the distant field under the crystal
mountain. Viewed from a high angle, an empty area opens between the dune
crest and that distant field.

**What the pipeline does today.** Every occluder's disocclusion is filled
by the cone-floor / plate depth, which takes the FARTHER depth. At the
dune crest there is a genuine depth cliff (near dune face → far distant
field). The plug therefore snaps the region *behind the crest* to the
distant-field depth. The party figures, standing on the dune, get the
same treatment: the plug behind them is the far floor. So a high-angle
parallax reveals distant-floor pixels immediately behind the crest and
behind the figures — the figures read as **occluding empty space** (a
deep void), and the crest reads as a thin cardboard cutout with the floor
right behind it.

**What is physically right.** The disocclusion a grounded occluder opens
should continue the surface it is ATTACHED to, not the farthest
background:

- **Detached occluder (astronaut vs sky).** The attachment surface *is*
  the far background. Flush-to-background (a58c) is correct: fill with the
  sky continuation.
- **Grounded occluder (party on dune).** The attachment surface is the
  near ground. The fill should continue the **dune** down behind them,
  not jump to the far floor. The a58c pull-push already does much of this
  when the figure's silhouette is surrounded by dune — the hole
  interpolates dune depth. It fails at the **crest**, where the near side
  is dune and the far side is field, so the fill is dominated by the far
  field.
- **Self-occluding ridge (the crest itself).** The region behind the
  crest is a disocclusion of the DUNE's own unseen back slope — data that
  exists in no capture (true SD-inpaint territory). The physically
  plausible fill is the dune surface continuing OVER the crest and sloping
  **down to meet the distant floor**, i.e. a depth RAMP from crest-depth
  to floor-depth across the disoccluded span — not a step straight to the
  floor at the crest.

**Statement of the rule.** *Disocclusion fill depth = continuation of the
surface to which the disocclusion is attached at its silhouette boundary,
resolved per-boundary:* continue the near attachment surface where the
silhouette borders it (party's feet → dune), the far background where it
borders only far (astronaut → sky), and across a self-occlusion crest
synthesize the near surface descending as a ramp to the far floor rather
than a cliff.

**Hook that already exists.** The seat machinery (a55/a56) already
identifies grounded figures and the ground floor they stand on. That is
the natural place to source "continue the attachment surface": for a
seated figure, seed the plug behind it from its seat-ground depth (dune),
not the global far floor; and detect the self-occluding crest as a cliff
whose near side is a large grounded surface, filling behind it with a
crest→floor ramp. Proposed as the next code step, pending confirmation of
this reading.


---

## Addendum 60 — the plug misprojection is the app's projection model (view-Z push, not reprojection); a59f adds a true reference-eye reprojection

The user challenged the plug directly: "did you implement a reverse anamorphic
projection or did you cheat by using stuff we had already?" Honest answer: I
cheated — the plug was a source-space depth field rendered as a mesh via the
app's existing displacement, which I *called* the projection. A verified
multi-agent code investigation found the real picture.

**Root cause (confirmed).** The entire app reconstructs depth as a
FRONTO-PARALLEL VIEW-SPACE Z PUSH with frozen portal-plane XY
(`viewSpaceDisplacementLogic`, moebius.js:1588): `viewPosition =
modelViewMatrix*position; viewPosition.z += displacement`. Only `.z` moves; the
texel keeps its flat portal-plane XY. The surface a disocclusion reveals lies on
the reference eye→texel ray extended to background depth Δ, so its world XY must
scale by (H+Δ)/H (H≈0.20, the home eye distance). Freezing XY gives a lateral
error `≈(X,Y)·Δ/H` — zero at frame center, growing to the edges, present even
head-on. This is why no single global scalar ever fully aligns the plug.

**Why outer=0.024 almost aligns the sky but never the floor (confirmed).** The
displacement is branch-selected by two separate uniforms (1581-1587): far/sky
(depth < split) is driven solely by `u_worldOuterVolumeDepth`; near/floor
(depth ≥ split) solely by `u_worldInnerVolumeDepth`. Dialing outer depth moves
the sky band and structurally cannot touch the floor.

**Plug-specific bugs (confirmed).** `matQ = L.mesh.material.clone()` (9682) is a
deep clone never added to `mediaLayers`, so the per-frame uniform sync
(13243-13249) never refreshed its outer/inner/split/metricScale — they froze at
bake time and desynced from the FG on any slider change. And its
`displacementBias` was offset to −0.004 (9687) vs the FG's 0.

**Party "faces camera" (confirmed).** No `lookAt`/billboard anywhere. Emergent:
the a57b seat writes each figure to ONE flat depth (7939, "a fronto-parallel
card that parallaxes as a rigid unit"), and a constant-depth region under the
view-Z push stays parallel to the image plane while the camera only translates
(shear frustum, never rotates). Same root mechanism as the plug.

**a59f fixes.**
- Option A (default): per-frame sync of the plug + v2/MPI completion meshes to
  the live depth-volume globals (they were skipped); drop the −0.004 plug bias
  (obsolete now the plug is hole-only). `window._plugZBias` restores it.
- Option B (opt-in, `window._rayReproject`): rewrite the displacement to a
  genuine reference-eye sight-ray placement — `S = refEye + dir·((H−zOff)/H)` in
  an eye-independent world frame, so the live camera reprojects a true 3D point
  with correct parallax from any position. Reference eye = centred authoring eye
  (0,0,camZ); H = camZ − portalZ. Shader compiles and renders coherently.

**Note on the party billboard vs reprojection.** Reprojection fixes the plug's
and FG's radial error, but a party figure that is a SINGLE flat depth stays a
flat card even reprojected (no side geometry to reveal). Making the party rotate
needs the seat to carry real depth variation — a separate change from the
projection fix.

Stamp v3.13.18-a59f.

---

## Addendum 61 — ray-reprojection made the default (a60): kills extreme-angle taffy

The user found that the streaking is not only thin features: with a DISTANT
object set as the focal plane and the view rotated (they showed cam
(-0.233, 0.040, 0.056) — eye almost on the portal, H≈0.056 vs the 0.2 home
distance), the whole scene shears into taffy/tunneling. Root cause is the one
from Addendum 60: the legacy displacement is a VIEW-anchored Z push, so with a
far focal plane everything nearer gets a huge displacement, and rotating shears
every depth-gradient surface (dune, mountain slopes) because the push direction
rotates with the view.

**A/B on the exact extreme camera.** Reproject OFF reproduced the shearing;
reproject ON (reference-eye sight-ray placement) was dramatically more coherent
— the mountain sat at correct perspective, the astronaut stopped stretching,
the dune stayed a solid surface. Residual taffy on the staff is the thin-feature
(A57) issue, separate from the projection.

**a60 landed reprojection as the DEFAULT** (`bgRayReproject = true`;
`_rayReprojectNow()` resolves the UI checkbox vs a `window._rayReproject`
boolean override). Both per-frame sync sites (the FG mediaLayers loop and the
plug/plane `_syncBG` block) drive `u_useRayReproject` from it, so quick-bake, v1
and v2 all reproject. Added a "Reprojection" checkbox to the main-canvas controls
(next to Angle fade), default on.

**Verified across all three paths** (starwatcher, software-GL harness):
quick-bake center+right and the extreme camera; v2 full-planes center+right;
v1 directional-plug center+right — all build and composite coherently under
reprojection, no crashes/shader errors. v2 built its 12 planes normally.

**Behaviour note.** Reprojection reproduces the SOURCE proportions at rest and
lets the depth-pop come from head/eye motion (correct for a head-tracked window);
the legacy push baked a pop in at rest. Toggle off for the legacy look.

**Follow-ups (not yet done):** re-tune the outer/inner volume depths for the
reprojected model; reconcile the reference plane with subjectFocalPlaneWorldZ
under subject-lock/dolly (the split already pins the focal content, but the
dolly-zoom "focal plane stays put" case wants explicit handling); the
thin-feature staff/glider streaking (A57 class).

Stamp v3.13.19-a60.

## Addendum 62 — trust the depth map: heuristic teardown + the directional rising-plate (a61/a61b/a62)

The user challenged the per-image hacks ("our code cannot be making custom
solutions for all image edge-cases") and asserted the estimator had done a
good job on the dune party. Measurement agreed, and the consequences ran
deep — three landings:

**a61 — ink-seat OFF.** The seat's founding premise ("estimator floats the
party to a near-spike, 0.09–0.61 spread") is false on the shipped map: the
party is a coherent mid-depth blob (80–111 raw over ~180 ground). The seat
flattened good depth to one card, which under A60 ray-reprojection has no
relief to rotate — the billboarding the user saw. Removing it made the bake
consume raw depth like realtime: party rotates, no shear (there was never a
spike to shear). Opt-in `window._inkSeat`.

**a61b — stroke-adopt depth OFF.** Audit overlays: adopt rewrote 19% of the
party region (mean 0.18 depth) by lifting ink outlines to the near dune the
party stands on — shattering coherent figures into near-depth filigree (the
true upstream source of the shatter the seat papered over). Where the
estimator was right it was inert (staff 118→119; glider untouched). Not
load-bearing anywhere measured. Opt-in `window._strokeAdopt`; the plug's
wash-ink rejection is unchanged. Ramp-collapse: secondary, leaves smooth
ground at 0% — kept. Standing-mask: plug-shaping, not a depth corruptor.

**a62 — directional rising-plate (quick-bake), DEFAULT ON.** The user asked
why the near dune was flagged as needing inpaint ("nothing can occlude it
ever"). Root cause: `disocc = dQ − plate` with a symmetric min-envelope
plate that drags open ground's floor down to the distant mid-ground; the
A44 gate then patched it leakily (astronaut/party budgets spilled onto the
connected same-depth dune). The mask bug and the fill bug were the same
bug. The replacement builds the plate from occlusion physics, with the
user's taxonomy (figure-on-ground / self-occluding fold / distinct layer)
encoded:

- plate starts AT the surface; far depth continues inward only under real
  occluders → open ground physically cannot read proud;
- ground segmentation (frame-edge flood bounded by luma edges + depth
  cliffs) supplies the object footprints — general to ink and photo;
- seeds at cliff far-lips + ground→object boundary px (catches silhouettes
  whose depth step the estimator smeared; BOOT crosses the undershot skin);
- the carried plate RISES at sCone/px (directional min-plus cone): wide
  massifs keep silhouette bands (crystal mountain no longer floods solid),
  fills ramp;
- hop budget fixed at seed, no renewal — the A44 chamfer made directional
  (margin-only death ran 330px on the dune ridge when the surface recedes);
- fold case: ground-ground cliffs (crest, ridge lips) detected at the
  boundary line via a two-ground probe (sky excluded: zero parallax funds
  nothing); fold fronts may enter ground while tear-step funded — the
  hidden-plain strip under the lip; figure fronts still stop at the feet.

Verified: SD mask 12.8% vs base 12.6% with the right distribution (figures
solid, outlines/whip covered, boot soles excluded — feet-level reveals are
same-depth continuations needing no SD — crystals banded, corners and open
dune clear, bounded ridge band); 3D at 0.42 offset: crest tear holes gone,
near dune cleaner than baseline, leg/party disocclusions intact.

Method note: the fold and budget fixes came from instrumented profiles
(plate-vs-depth columns), not tuning — two hypotheses (sky-carry, ground
misclassification) died against dumps before the real cause (margin death
is unbounded when the surface recedes) was measured.

Follow-ups: port the dir plate to the v1/v2 plate paths; ramp-vs-hard fill
VALUE discriminator (far-anchor gradient — band extent already correct);
generalization sweep on a second asset (troll/frazetta) before calling the
ground-seg constants safe; on-load framing question (A61) still parked.

Stamp v3.13.19-a62. Code: d0ba77e (a61/a61b + prototype), f94ea0e (a62).

### Addendum 62b — pixel-hunt closure + the port

The user's close read of the SD mask found real misses: the helmet-top
outline, the cape arc, the staff loop's inner edge, the ribbon. Measured,
they split three ways:

1. **Silhouette ink at/past the far depth** (helmet rim 23 raw — BELOW the
   plain behind it): invisible to any depth-trusting mask (plate == own
   depth). But the ink belongs to the occluder and orphans on reveal. Fixed
   with the ink-adjacency closure: stroke px adjacent to a flagged px join
   the SD region (stroke-width-bounded passes, diagonal-aware sandwich for
   1–2px slivers) and inherit the neighbouring plate. +11k px; the flagged
   spots verified closed.
2. **The ribbon core at exact sky depth (0.0)**: A57 thin-feature dropout —
   an FG-side depth problem, not maskable; still open.
3. **The wreck hull**: the estimator says half-buried (hull 16 vs ground in
   front 29) — the thin top-rim strip is the honest reveal; "hull interior"
   has no occlusion in the depth to plate.

Port: the plate computation is now `bgDirectionalPlate()`, shared by
quick-bake, the v1 plug consumers, and the v2 under-sheet (plug-DEPTH
consumers only — the floor rind keeps the min-envelope, which is
containment, not a depth value). All three paths verified at 0.42 offset;
v1's near dune is now free of plate mottle. On-load framing: settled as
correct by the user. Stamp v3.13.19-a62b, code b0c7c11.

### Addendum 62c — three-asset generalization sweep

Same binary, zero per-image constants, quick-bake + dir-plate + closure on
three assets:

| asset | class | SD | verdict |
|---|---|---|---|
| starwatcher | ink line-art | 13.2% | reference — no regression |
| silverwarrior | painterly (Frazetta) | 11.7% | field/sky clean, figures banded, 3D no holes |
| sunflower photo | photograph | 21.5% | sky/clouds clean, near occluders flagged, 3D correct |

One general fix fell out: the ground flood's depth barrier went from per-px
to windowed range (±3) — soft painterly silhouettes never trip a per-px
step (the same smearing physics as the cliff-seed budgets, same windowed
answer). Luma stays per-px deliberately: windowing it would fuse textured
ground (dune stipple) into a contiguous wall and strand the flood.

One real limitation found and documented, not patched: on the warrior the
bear/sled group touches the BOTTOM FRAME EDGE, so frame-edge ground
seeding classifies the hugely-proud foreground group (134 raw over a 0
field) as ground from within. It degrades gracefully — the fold pathway is
depth-only and fills the figures anyway; interiors come out patchier than
the ink asset. The open design question is content-free discrimination of
a bottom-cropped foreground object from a true ground plane at the frame
edge. Deliberately not answered with a heuristic tonight — it is the same
class of taxonomy question as feet/fold and deserves the same treatment.

Stamp v3.13.19-a62b (code e4c2446 adds the barrier as a62c).

### Addendum 62d — the frame-edge rule: "ground is what you can walk down into the distance"

The user flagged frame-cropped foreground characters as a must-solve
(common composition; the warrior's bears seeded ground from within). The
rule derivation, by counterexample:

- "near content at the edge = object" — fails: the dune at the bottom edge
  is the NEAREST thing in its scene and IS ground.
- "recedes inward = ground" — fails: a figure STACK also recedes
  front-to-back (bears 134 -> rider 72).
- What survives: HOW it recedes. A support surface recedes SMOOTHLY at
  plausible ground slopes; a figure pile recedes through silhouette
  CLIFFS. Seed iff within a tear step of the far limit (sky, flat far
  field — cannot hide a reveal), or a cardinal walk accumulates
  tearStep/2 of recession with every step smooth at window scale.
- False negatives are inert by construction: flat far scenery / studio
  backdrops classify as object, but a front entering flush content is
  never funded and lowers nothing. The rule's failure mode costs zero.

Two coupled-constant lessons from the sweep (both measured, both now
tied): the depth-barrier window must scale with resolution (smear scales
with upscaled estimator output; ±3 missed a 30px fur/field smear at
3000px and the flood leaked around the gate), and the fold probe must
out-reach the barrier strip it probes across (RF = RWD + stroke; star's
ridge band halved the mask when the strip outgrew the probe).

After: starwatcher 13.6% (~baseline, band restored); warrior 8.6%,
figure group = object with silhouette bands + band-limited interiors,
field/sky clean; sunflower near-leaves correctly object. Stamp
v3.13.19-a62d, code 975d358.

## Addendum 63 — thin-lift: the ribbon class, solved within trust-the-depth-map

The A57 residual: sub-stroke-thin ATTACHED features dropped to the far
limit outright by the estimator (staff ribbon curls + upper-loop edges
measure 0.0 — exact sky), rendering pinned to the background and
detaching from the staff under parallax (reproduced at 1440px, ±0.25).

The fix is deliberately NOT stroke-adopt revived. Adopt died because it
could not distinguish a genuine dropout from a figure's outline skin.
Three structural gates can — each anchored to a measurement made this
session:
1. flush-far (D <= tearStep): the party/helmet outlines dip only to
   ~0.09 and are excluded before any shape test;
2. far-surrounded ring: body-skin outlines have their figure on one side
   and fail;
3. near anchor: the component must touch decisively nearer content and
   adopts that depth — unanchored far ink (mesas, horizon strokes, the
   sunflower photo's bird flock) is untouched.
Placed at the shared bake source so all four consumers get it.

Verified: the loop renders solid and rides the staff (the dark sky-ghost
is gone); residual thin wisps are px outside the gates — the trade to
catch them (raising the flush threshold past the party rim's 0.09) is
explicitly declined. Star mask 13.7% ~ baseline; party untouched.

Stamp v3.13.19-a63, code 7cb9712.

## Addendum 63b — gradient-true fill values: the discriminator is the measurement

The ramp-vs-hard fill-value question closes the way the taxonomy predicted:
no classifier. The fill continues the far anchor's own PLANE — sky and
flat layers measure gradient ~0 and fill HARD at their depth; receding
ground measures its recession and RAMPS. Extent stays owned by the hop
budget.

Making the values honest removed compensating errors the fixed +sCone rise
had been hiding. Four fell in sequence, each pinned by an instrumented
claim-record dump at the failing pixel (after three seed-side hypotheses
died against unchanged output — the probe, not the theory, found every
one):
1. sky-lip fold gate (a horizon lip reveals more of the SAME surface,
   never sky);
2. plane carry — path-integrating the gradient let improve-and-repush
   prefer descending zig-zags; a plane is path-independent;
3. trust span + descent floor — a ±3px-window gradient extrapolated 150px
   is noise amplification; never more than a tear step below its own
   anchor;
4. NEAREST-ANCHOR WINS — lowest-plane-wins systematically elected the
   noisiest negative-gradient anchor in budget range. A reveal continues
   its nearest occlusion boundary; value only tiebreaks.

Pocket promotion (enclosed flush pockets -> ground) was built, measured,
and deliberately left opt-in: nearest-anchor already fixes the free-fill
corridors it targeted, and on painterly figures it amplifies boundary
leaks (576k px over-promoted on the warrior; snapshot-vs-cascade did not
save it). Fewer mechanisms won.

Verified: star 13.9%, profiles physical end to end (plain values at the
ridge lip, ramp meeting the surface, party/crest sane); warrior 8.9%
banded coverage restored. Stamp v3.13.19-a63b, code a8b5fd8.

## Addendum 64/65 — regression suite, the dolly measurement, and the lens law

**A64 — standing regression suite** (`regress.js`, on review-fix): one
command validates the plate system — SD%/ground% on ink/painterly/photo
against a63b baselines, plus 3-path render-lit sanity on the reference.
ALL PASS at commit. The photo range documents the dense-texture pocket
cost of the opt-in-promotion decision as a known trade.

**A64 — the dolly/subject-lock measurement** (off-axis, lateral 0.12,
dolly z 0.05..0.35, under ray-reprojection): content at the split depth is
pinned STRUCTURALLY — a reprojected texel with zero depth-offset has
s = 1, S = Pw, independent of the reference eye — and measured drift in a
0.4-0.6 depth bin is proportional to |d - 0.5| (6-12px bin-width effect)
while far content breathes 26px. With the subject plane on the portal
(the default), the mesh-scaling lock machinery is skipped entirely and
lock-on/lock-off renders are bit-identical: the portal projection alone
owns the invariant. The q != P case remains device work.

**A65 — content-lens FOV normalization** (branch review-fix-lens, riskier
interaction-path change per the user's split): the user's brief — 90deg
~ viewer-native screen space; long-lens cuts must feel the same size
(focal content in expected screen XY) while keeping authored depth
compression. The law that satisfies it: head motion measured in
focal-plane frame widths is lens-invariant. Frame width at the focal
plane ~ 2*D*tan(fov/2); the portal absorbs D (the pin above), leaving
gain = tan(fov/2)/tan(45deg) on face-track + gyro camera motion.
90deg = 1.0 = bit-identical today; window.setLensFov(deg) per cut.
Depth compression is deliberately NOT renormalized — it is authored
content. Feel calibration across real cuts is device work.

Stamps: v3.13.19-a64 suite on review-fix (5342588); a65 on
review-fix-lens.

## Addendum 66 — the v2 ghost columns: pair validation reaches the plane claims

The open v2 artifact from the a62b port verification, finally pinned.
At offset, tall blocky gray columns stood in the sky beside the figure
and the staff (and a figure-shaped blob beside the party) in the
full-planes path. Isolation first: rebuilding v2 with the directional
plate disabled is BIT-IDENTICAL (0 changed px at three poses) — the
full-planes branch returns before every dirPlateV consumer, so the a62b
"v2 port" only ever reached the non-full-planes MPI path. The columns
are not an a62b regression; they are original full-planes behavior.

Layer-solo renders found the owner: the layer-7 (mesa/far-dune bin)
CLAIM region — the completion — extended straight up the figure/staff
silhouette as a pillar hanging in front of sky. Mechanism, from the
claim gate: a claim needed only ONE row-or-column anchor, and the
one-sided inverse-distance lerp collapses to the anchor's own depth
(the distance weight cancels), so a mid bin with ground anchors far
BELOW funds claims all the way up any nearer silhouette — column-shaped
because only column anchors exist there. This is exactly the
bird-flank-under-sibling class the strips path killed with PAIR
VALIDATION; the rule was never applied to full-plane claims.

The fix is that rule, ported: a claim needs anchors on both sides of
its row or its column. The frame edge counts as a flank only when the
march to it crosses nothing but strictly-nearer content (occluders of
the bin, dV > bin's near cut + tearStep) — so a frame-cropped figure
still gets completed behind (the warrior's bears), while sky above the
staff breaks the march and the column dies. The backdrop bin keeps its
unconditional budV-band rule; visible texels are untouched.
Opt-out window._noV2PairValid.

Measured (star, 1200x750, six poses): ghost columns gone at
±0.42/0.25/look-down (10-14k px removed per pose), rest pose 229px of
blur jitter, black-px counts flat (no new holes — the backdrop fills
where the false claims used to hang).

Cross-asset: warrior and photo v2 render clean of wash columns at the
same six poses; the warrior's top-left black corner at +0.42 is
pre-existing margin behavior (A/B: 6260 black px with the rule off vs
6268 on, same bbox — while the rule removes 12k px of ghost claims).
Full regression suite after the change: ALL PASS (9) — quick-bake masks
untouched by construction, 3-path renders lit.

The residual, honestly: a softer figure-shaped ghost remains at strong
offsets. That is a different class — the estimator smears the
silhouette over a shell of intermediate depths, those texels are
VISIBLE content in mid bins (real figure colors at estimator-reported
depths), and pair validation correctly does not touch visible texels.
It is the v2 relief of the same smeared-transition physics the
quick-bake path meets as soft cliffs, and its texture is SD's slot;
carving visible texels out of bins by content would be the class of
heuristic a61/a62 tore out.

## Addendum 67 — the q != P subject pin: the mesh-scale law was wrong, the reprojection makes the right one trivial

The a64 open item ("the q != P case remains device work") turned out to
be measurable headlessly, and the measurement killed the shipped law.

Setup: subject focal plane moved OFF the portal via the app's own
peek->Z mapping — once onto the far volume plane (q = -0.02, sky), once
onto the near dune (q = +0.0196, depth 0.745) — dolly sweep off-axis
(lateral 0.12), pinned near/mid/far frames, lock on vs off.

The old mesh-scaling pin (scale all meshes by s = d(e0-P)/(d0(e-P))
about the eye-axis point on the subject plane) is portal-projection
correct for STATIC world geometry, and measurably wrong under ray
reprojection: the subject bin drifted exactly like lock-off (24.7 vs
24.0 px) while other bands warped, and on the near-dune run the lock
made every measurable band WORSE than free (crest medians 43.5/34.0 px
vs 28.5/7.0). Mechanism: the scale moves the plane the shader displaces
from — under reprojection content Z itself shifts with the transform,
so the static-geometry derivation does not apply.

The reprojection also hands over the correct law. With u_refEye
z-tracking the live eye, a texel's portal hit is
X = px - ex*zOff/(e-P-zOff): an ON-AXIS dolly is a structural no-op
(the portal projection is the dolly-zoom compensation), and ALL dolly
drift is the lateral-offset term. Content on the subject plane
(zOff = q-P) drifts only through ex/(e-q) — so the pin is: scale the
APPLIED lateral eye offset by g = (e-q)/(e0-q) while dollying. Subject
pinned exactly for any live head position (the gain cancels e, not ex);
portal stays pinned (its term has zOff = 0); head parallax about the
subject becomes dolly-invariant; other depths breathe. g = 1 at engage,
so activation is seamless. No mesh is touched; the scaling machinery is
demoted to the non-reprojection legacy path.

Measured (near-dune subject, crest-line metric, n=76 columns):
lock mid->far 1.0 px median vs free 7.0; lock mid->near 4.0 px vs free
28.5. The old law's 43.5/34.0 for comparison. At q = P everything is
gated off and the gain multiplies by exactly 1.0 — the a64
bit-identical result stands. Stamp v3.13.19-a67. The suite now guards
this invariant (11 checks: lock crest <= 2px, free >= 2px so the metric
is proven live).

## Addendum 68 — painterly figure interiors: the mask is healthy, the debt is the plate stand-in at scale

The a62c open question ("figure interiors patchier than the ink
asset") measured, on the warrior at full 3000x3000:

- Figure group (largest non-ground component): 1.05M px, and the SD
  mask covers 638k of it — 61%, with 94% of that in ONE connected
  component (598k px; second 38k; the rest is <=102px speckle). Row-gap
  median between SD runs is 13px. The mask is NOT fragmented — the SD
  stage gets one workable region per figure, and the uncovered 39% is
  deep interior beyond any parallax reach, which is right-sizing, not
  under-coverage.

- The real finding is elsewhere: at cone-edge offsets (0.25-0.42
  lateral) the quick path renders the reveal behind the figure as a
  STAIRCASE — terraced plate depth, each plateau parallaxing as its own
  band, textured with row-stretch carry. No holes (the a62c claim
  holds); the geometry of the stand-in is the artifact. The terrace
  scale implicates the extrapolation span cap (KE) in the gradient-true
  fill: behind a 600px-wide occluder at 3000px resolution the anchor
  planes clamp at KE and competing fronts meet in value plateaus.
  SD cannot fix this class — SD repaints texture, but terraced DEPTH
  still parallaxes as stairs after repainting. Filed as its own item:
  smooth/relax the plate fill within large disocclusions (fill values
  in the occluded region are ours to shape; the source depth map stays
  untouched).

  Mitigation note: these poses sit at/beyond the fade band (35-45deg),
  so device fade covers the worst of it today.

## Addendum 69 — the staircase autopsy: far-plane pits (fixed) + colour striation (SD's slot)

The a68 "terraced plate" hypothesis (KE clamp) died against the
profile, the way hypotheses here usually die. The plateQ dump under the
warrior figure showed something worse than terraces: the plate pinned
at SKY depth (0.000-0.031) under surfaces at 0.35-0.75 — at x=2000 a
0.6-deep far-plane pit, with 0.6 cliffs where correct islands
survived. Mechanism, from the fill's own rules: hop budgets scale with
the boundary's depth step (bigger step = wider legitimate reveal), so
the figure-vs-sky boundary at the helmet funds fronts that outlive the
small-step mountain/field flank fronts — "nearest LIVING anchor" is
the sky, and nearest-anchor-wins cannot save you when the right
anchors are dead.

The fix is the membrane's both-sided rule reaching the directional
plate, which is also the user's city-roof taxonomy verbatim: a reveal
continues its FLANKING surfaces, row by row — sky rows stay sky,
mountain rows carry mountain, the skyline behind a figure emerges
naturally. Every flood-claimed px with ground on both row sides takes
the lerp of its two flank surfaces (== the membrane's inverse-distance
blend), clamped never proud of the occluder's own surface. Rows only —
columns would drag roof texture down, the exact failure the taxonomy
names. One-sided px keep the flood value; unclaimed interiors keep
plate == surface, so the SD mask can only get more honest, not larger.

Measured after: pits gone (x=2000: 0.000 -> 0.17-0.65 tracking the
flank field; x=1200 mid rows 0.008 -> 0.40), fill step sizes 6x
smaller, SD components inside the figure 587 -> 178, masks star 14.0
(stable) / warrior 8.5 / photo 23.3 — the photo drop is pit flags
dying, verified against a clean 0.35-offset render before re-basing
the suite range. Suite ALL PASS (11).

And the honest split at the end: the staircase LOOK in the warrior
renders barely moved, because what remains is plate COLOUR striation —
the row-carry wash whose fixed 4-pass softening is invisible at
3000px. That component is texture, which is SD's slot by the project's
own division of labour; the geometry underneath it is now flank-true,
which is the part SD could never have repainted. Stamp v3.13.19-a69,
code 3d647e5.

## Addendum 69b/70 — the device round: the gate the membrane forgot, and the wash doppelganger

The user tested on device and caught two things the harness sweep
missed (the star quick render was the one view never re-eyeballed
after a69 — that discipline gap is the lesson of this addendum).

**69b — same-class gate restored (426370b).** The first membrane cut
dropped the original rule's same-class condition. Sky-left/plain-right
rows across the astronaut lerped into a mid-depth shelf: the horizon
glued to the figure, the plate deepened, the wider reveal exposed the
ghost. Gate: flanks must agree within a tear step, else the flood's
directional value stands (fold/skyline territory). Measured: star
gated-vs-membrane-off now 461px apart at the device cam (inert where
flanks disagree, still re-bases 101k same-surface px); warrior pits
stay fixed; suite ALL PASS.

**70 — the ghost itself predates a69, and it is the wash doppelganger
(9754c23).** Discriminating renders split it: plate hidden -> dotted
FG rubber dust only; FG hidden -> the plate carries a smooth BLUE
ASTRONAUT COPY. The GPU wash's seed gate is a fixed-radius dilation;
figure-fringe texels that read as plate depth seeded figure tones and
pull-push spread them into a figure-shaped doppelganger — the exact
class v1 killed years of addenda ago with depth-consistent
continuation. The quick wash never got the rule; now it has:
every disocc px's plate colour comes from real background at the px's
OWN plate depth, along its row (columns as fallback,
resolution-scaled bound, inverse-distance blend two-sided); misses
take the nearest RESOLVED reveal colour, never figure paint. CPU pass
at bake; wash kept only as fallback. Measured at the device cams:
16.7k px repainted at (0.431,-0.065), 27.5k at (0.710,0.025), ghost
gone from the reveal; suite masks byte-stable (colour-only pass).

Still open, honestly: row striping where the plate depth ramps (each
row legitimately continues a different-depth band; SD's slot), the
dotted FG rubber dust (un-torn fringe quads in quick — the pre-tear
trade from A52), and both device cams sit at 65-74 degrees, well past
the 35-45 degree fade band, so the residuals there are outside the
supported cone by the product's own rule. Stamp v3.13.19-a70.

## Addendum 71/72 — one bake control, the reveal consensus, and where the rubber actually lives

**A71 — the bake dropdown (ab49b11).** The user could not get quick
bake to build ("producing v2 instead"): mode lived across two
checkboxes, quick silently overriding full-planes, and the debug sheet
never recorded which path built. One control now — Bake [quick | v2
depth layers | v1 plug bake] — drives the three flags atomically,
rebuilds on change once a build exists, and the debug footer stamps
mode= (plus baked:quick). Verified by driving the REAL moebius.html
headlessly through the user's flow: quick -> plate, switch v2 -> 12
planes auto-built, back to quick -> planes cleaned, FG restored; the
in-app logs also confirmed a66 pair validation and the a70 colour pass
live. The build sheets that motivated this are now self-identifying.

**A72a — reveal colour consensus (a943063).** The a70 row rule made
the reveal colours depth-true, and exposed the next layer down:
adjacent rows anchor to different flanks and the decorrelation reads
as comb striping (warrior at 0.25). Masked box consensus over reveal
colours only — vertical 16px@1920 (the striping axis), horizontal
6px@1920 (anchor handovers) — never crossing the disocc boundary, so
silhouettes stay exact and sky->mountain->field gradients survive.
Comb gone; suite ALL PASS throughout.

## Addendum 73 — the troll was never in the net: cave-class ground collapse, and the two honest regressions

The user's device round ("truly terrible and strange tunneling in the
troll pic — supposed to be generalized") closed the loop on a blind
spot: the troll IS the app's shipped default asset
(defaultImgColor/Depth.png, 851x1023, the certified-record asset of the
a44-a51 era) — and the one image the a62+ generalization sweeps and the
regression suite NEVER covered, because every harness probe overwrites
that exact filename with the asset under test. The dir-plate replaced
the record-era treatment sight-unseen on the very asset the records
were built for.

Diagnosis, measured: ground = 94.7% — the walkable-ground flood
swallows the FIGURES. Not smear leakage this time (the silhouettes are
sharp: 0.36 -> 0.02 within 3px, the windowed barrier catches them);
the flood enters through GENUINE depth-continuous contacts — the big
troll's arms merge into the branches, the woman into the snake and
water — and dark-on-dark defeats the luma bound. Cave topology also
means every frame edge recedes smoothly inward, so all four edges
seed. Figures-as-ground puts the plate FLUSH AT FIGURE DEPTH; the
silhouette tear then exposes a near-depth plug wall wearing wash
colours: bg-extruded-to-fg, the user's tunneling, at 22 degrees.

Attribution, settled by measurement after the user pushed back
("it was not doing this yesterday"): yesterday's exact commit (a64,
5342588) produces BIT-IDENTICAL troll quick numbers (SD 20.3%, ground
94.7%, 325,976 flood cells) — the quick path did not change. What
changed is that the a71 dropdown made the quick button actually build
quick: yesterday the checkbox tangle silently built v2 (the user's own
first report), which renders the troll cleanly (verified at 0.25
today). The dropdown exposed a long-standing quick-path defect; it did
not create one. Interim guidance: v2 mode for figure-heavy
compositions until A73 lands.

The suite now carries the troll as a PINNING ROW (ranges lock the
defective state so any change is visible; the A73 fix must move
ground% far below 94.7 and re-pin). The taxonomy question underneath
is the hard one the a62c addendum deliberately left open — content-free
discrimination of a standing object from continuing surface when the
object genuinely touches its surroundings at matching depth. The
record era answered it per-asset; the general answer is still owed.

Also confirmed from the same device round: the star's horizon shelf
"attached to the astronaut" PREDATES a69 (present with the membrane
off) — boundary-seed fronts at the figure's FEET carry near-dune depth
up behind the torso. The membrane's row rule was accidental partial
medicine, which is why the artifact seemed to move. Both re-landings
(membrane + row colours) wait on a tunneling invariant in the suite
and the figure-against-sky reveal-content call.

**A72b, open, with the design settled by measurement.** The remaining
putty (the user's frazetta column at ~36deg — INSIDE the fade band) is
FG rubber: the quick cliff tear is per-triangle (span > tearStep), so
an estimator smear distributed over N px presents span/N per quad and
never trips — the same physics a62c met at the flood barrier. Two
facts pin the fix's location: (1) tearing the smear quads would only
convert the rubber sheet into a cap-card dust curtain (fringe colours
at fringe depths, splatted); (2) snapping dQ inside the quick branch
moves NOTHING — the FG mesh displaces from the bake's shared depth
texture, not quick's local copy. So the repair belongs at the SHARED
BAKE SOURCE, and the discriminator that survives the pseudo-glancing
taxonomy is the plate itself: a px is smear-fringe iff it stands a
tear step proud of its OWN plate continuation with a genuinely nearer
surface inside the smear window; snap it to whichever real side is
closer. A true glancing ramp has plate == surface and is untouched by
construction. Not landed tonight — it touches every path and deserves
a fresh session with the suite around it. The frazetta/troll asset
should also be committed to the repo so the fix is verified against
the exact reported sheet, not the warrior proxy.


## Addendum 74 — the rollback and the 15-commit validation grid

Per user directive: review-fix rolled back to the exact a60 tree
(f4e5a0f; the remote refuses force-push, so it is a revert-style commit;
the a61..a72b arc stays reachable via main's merge history and the
harness). Then every behavior-relevant commit of the arc was rebuilt
and measured on the two device scenes (quick bake, star at
0.318/-0.051, troll at 0.217/0.026) — 15 commits, mask numbers plus a
render per cell (harness/val/, grids delivered).

What the grid shows:

1. STAR: stable across the ENTIRE arc — SD 12.6..14.1, ground 78..80,
   and the renders are near-identical from a60 to a72b. Critically,
   the ghost silhouette and horizon shelf beside the astronaut are
   VISIBLE IN THE a60 BASELINE RENDER TOO: that artifact class
   predates the directional plate entirely. No commit in the arc
   introduced or materially changed it at this cam.

2. TROLL: the mask tells the structural story — ground jumps to
   96.9% at the FIRST dir-plate commit (a62) and stays 94.7% through
   a72b (the cave-class ground collapse; a62c briefly whipsawed SD
   20->3.4->19). But at this 22-degree cam the RENDERS are visually
   similar from a60 through a72b: modest pale wash behind the woman,
   no catastrophic extrusion in the harness.

3. The severe device artifacts (the user's sheets) are NOT fully
   reproduced by the harness at the same cams and default settings.
   Open question for the device round after the rollback merges:
   fresh debug sheets on the a60 build at the same poses — if the
   severity persists there, the differentiator is device-side state
   (slider settings, screen cone, asset scaling), not the arc.

Verdicts: no single commit in a61..a72b is convicted by this grid at
the probe cams; the one measured structural defect of the arc is the
a62 cave-class ground collapse (A73, pinned); the star ghost/shelf is
an a60-era plug behavior needing its own workstream. Recommendation:
hold the rollback as deployed baseline, get fresh device sheets on it,
and re-approach the arc only with the troll row + a tunneling
invariant in the suite as gates.

## Addendum 75 — the user's bisect pays off: the parallax-reach bound on thin-lift

The user read the 15-commit grid closer than its author: the star's
horizon-attachment enters at exactly a63, and the troll's gloop enters
at a62c (mask-collapse exposing raw rubber, cured by a62d) and returns
at a63b (the descent floor clamping fill values a tear-step under
FIGURE-classified anchors — a locally sound rule on a wrong premise).

The a63 inference: the horizon is a thin ink line at far depth and the
astronaut stands ACROSS it, so the thin-lift's contact gate adopts it
exactly like the ribbon. The missing property was never shape but
EXTENT — an accessory lives entirely within parallax reach of its
contact; scene linework runs frame-wide away from it.

a75 (branch arc-fix, 21104b1, on the a72b arc): all-or-nothing
parallax-reach bound — if any component px is farther than
MAXD = 150px@1920 (euclidean) from every anchor-contact px, the lift
is skipped and the feature keeps its far depth. Measured: star at the
device cam changes by EXACTLY 407px vs the unfixed arc tip, all in
the horizon band beside the figure; the ribbon still lifts and rides
the staff (probe); suite ALL PASS (8) including the pinned troll row.

Remaining from the bisect: the a63b/troll half — true fix is A73
ground segmentation (true anchors defuse the descent floor by
construction). arc-fix stays LOCAL pending the user's call on push
vs. re-landing the validated arc as one series.

## Addendum 76 — rise-debt falsified: the troll's figures are entered at matching depth, not climbed

arc-fix is pushed (21104b1, the a75 lift bound). The A73 attempt that
followed did not survive its own measurement and was removed the same
hour it landed.

The design: make walkability local — the ground flood accrues DEBT for
every step toward the viewer, recession pays it down (floored at zero),
and claims over more than a step-height (2 tear steps) are refused, so
a standing figure must be climbed and is excluded path-independently.

The measurement: troll ground 94.7 -> 92.9 (a 1.8-point dent), star SD
taxed 13.9 -> 13.0. Why it failed, and why it HAD to fail on this
composition: the cave walls at the frame edges are themselves
near-depth, so the flood descends inward with zero debt everywhere; and
the figures are entered through contacts that sit AT body depth (arms
into branches — the same genuine contacts that defeated the luma and
barrier bounds). There is no climb to tax. Contact-at-matching-depth
composition defeats every LOCAL depth rule for figure-vs-surface;
the a62d bear-stack logic (figure piles recede through cliffs) does
not transfer.

What this redirects to: stop trying to segment the trolls out of
"ground" and instead profile WHERE the near-depth plate behind the
woman actually comes from (the instrumented-claim-record method that
found nearest-anchor-wins). With figures classed as ground, the
woman/passage boundary is ground-on-both-sides = a FOLD, whose carry
is supposed to be the FARTHER lip — if the fill behind her is coming
out near instead, the defect is in the fold/boundary VALUE pathway on
this topology, which is a narrower and more answerable question than
cave-class segmentation. That is the next probe, not another rule.

Code state: rise-debt reverted (falsified premise, removed); arc-fix
still carries exactly a72b + a75.
## Addendum 77 (2026-07-18): a60 harness-vs-device reconciliation CLOSED — ghost class is a60-native everywhere

The suspected contradiction (device a60 "clean" vs harness a60 ghosted)
is dissolved by two pieces of evidence that arrived together:

1. The user's corrected a60 device sheets (stamp v3.13.19-a60, quick,
   fgReach=60) show the translucent ghost figure beside the astronaut
   at BOTH cams — left cam clearly, right cam as a ghost over sky.
   The earlier "clean" verbal report referred to the hard artifact
   classes (no extrusion in the troll, no shelf on either side of
   star), and those genuinely ARE absent at a60.
2. A new real-page probe (harness/a60_realpage.js) that drives the
   REAL a60 moebius.html — not the frozen scratch page — through the
   user's exact flow (tick quick checkbox, click Build) confirmed the
   page's live defaults match the device stamp (reach=60, inner=0.04,
   outer=0.02) and rendered the star at the device cams
   (val/RP_a60_L.png, RP_a60_R.png): ghost figure present both sides,
   no hard shelf. Real page == scratch page == device.

Consolidated per-class verdict, now measured at real scale on all
three rigs:

- GHOST FIGURE + pale band (translucent doppelganger over sky): a60-era
  and older; present on device, scratch harness, and real page alike.
  Oldest surviving artifact class; the parked a70 colour work is its
  targeted cure and stays gated behind a tunneling invariant + the
  user's reveal-content taxonomy call.
- HARD HORIZON SHELF attached to the astronaut: arc-era, enters a63
  (thin-lift adopting the horizon ink line), absent at a60, fixed on
  arc-fix by a75's parallax-reach bound (407px surgical change).
- TROLL BG-EXTRUDED-TO-FG gloop: arc-era, enters a62c / returns a63b
  per the user's grid bisect, absent at a60 (user-confirmed on
  device). Still open; next probe is the instrumented fold/boundary
  VALUE profile behind the woman (Addendum 76 redirect).

Method note: the scratch harness was NOT lying — its a60 baseline was
faithful. The contradiction was a category mismatch in the reports,
resolved by insisting on shots over adjectives. rp probe left in
harness/a60_realpage.js for future real-page A/Bs.

## Addendum 78 (2026-07-18): A73 root cause — nearest-anchor Voronoi steps ARE the gloop; farther-value-wins (floored planes) is the cure

Instrumented claim records in bgDirectionalPlate (the method that found
nearest-anchor-wins) finally profiled the troll's bg-extruded-to-fg fill
end to end. The chain, each link measured on the shipped default asset:

1. DESCENT FLOOR EXONERATED. The a63b floor determines only 0.6% of
   claim values, and a full A/B with the floor disabled reproduces the
   defect bit-for-bit (nearAnchor 30.7 vs 30.8%, plate stats identical).
   The bisect's a63b conviction stands, but the mechanism inside the
   commit is elsewhere.
2. SEEDS ARE FINE. The seed-field dump shows the woman's silhouette
   ringed with FAR (passage-depth) fold seeds — 2203 in her bbox — and
   the passage itself 84.8% ground-classified. The fold machinery
   carries the far lip exactly as designed.
3. THE CONFLICT RULE IS THE DEFECT. With ground collapsed (94.7%),
   internal detail cliffs seed fold anchors AT BODY DEPTH inside every
   figure (1471 near seeds in the woman's bbox). Nearest-anchor-wins
   hands interior reveal pixels to those anchors by proximity: 30.7%
   of all claims are won by near (>0.35) anchors, and the plate maps
   show fan-shaped Voronoi wedges stepped at different depths. The
   plate renders SOLID (backstop contract) — every step between wedges
   is a stretched wall of texture. That wall is the gloop. Star is
   immune because its figures are not ground-classified: no body-depth
   fold anchors exist to win (nearAnchor 8%, all legitimate).
4. THE CURE. Farther-value-wins with distance as tiebreak — the old
   law's intent — is safe again because the descent floor bounds every
   plane's bid to its anchor's measured depth minus one tear step: the
   runaway-to-zero that motivated nearest-anchor (three measured
   incarnations) cannot recur. A/B measured: troll near-plate claims
   34.7 -> 15.4%, both probe cams render clean (stretch walls replaced
   by flat wash openings); star renders pixel-comparable at both
   device cams, SD 13.8 -> 15.2% (inside the suite range).

Cost, quantified: the plate deepens where far anchors now claim their
full hop budget — troll SD 20.3 -> 34.7% (the reveal behind figures in
a fold-heavy cave is genuinely the passage), photo 28ish -> 38.2%,
star +1.4pts, warrior in range at 9.6. Deeper plate = more SD budget
(and the a70 lesson says wide reveals lean harder on inpaint quality) —
that trade is documented here, not hidden in a range edit.

Landing (arc-fix): farther-value-wins becomes the default with
window._nearestAnchorWins as the A/B hatch; the _foldProbe claim-record
instrumentation stays (gated, zero-cost off); suite ranges re-baseline
troll (30..40, was the defect-documenting 15..26) and photo (33..43)
with comments naming this addendum. Condition before the commit: the
photo asset A/B shots must show no new artifact class at offset cams —
the mask number alone is a budget metric, not a correctness verdict.

## Addendum 79 (2026-07-18): A72 smear-fringe snap LANDED — the design Addendum 71/72 pinned, with one added gate

Implemented at the quick-branch bake source (immediately after the
directional plate, before rigidify/ship/tear — verified against the
code that in-branch dQ edits DO ship to the shared depth texture at
the "ship the cleaned depth" block, so the FG mesh and the
per-triangle tear both see the sharpened depth; the earlier "moves
nothing" note in Addendum 71/72 does not hold on the current tree).

The rule, exactly as pinned, plus a third gate the taxonomy demanded:
a px is smear-fringe iff (1) it stands a tear step PROUD of its own
plate continuation (glancing ramps have plate == surface — untouched
by construction), (2) a genuinely NEARER surface exists inside the
smear window (RS = 2x the barrier half-window), and (3) NO real cliff
exists in that window — the proudness is carried entirely by a
sub-cliff ramp (the span/N physics). Gate 3 is new: without it, a
real mid-depth surface within RS of a genuine cliff would be eaten;
with it, hard steps stay the tear's property. Snap goes to whichever
real side is closer. window._noSmearSnap reverts.

Measured on the shipped default (troll): 3650px re-concentrated,
cliff tear 6043 -> 8982 spanning triangles (the tear now trips at the
snapped silhouettes — the intended conversion), orphans 21 -> 131 cap
cards at real depths/colours, SD 34.7 -> 34.6 (unchanged). Suite with
the snap active: ALL PASS (13), star/warrior/photo masks unchanged to
0.1pt. Wide-cam A/B shots (+-0.35): pre/post near-identical — the
large wall smears at grazing view are ground-classified glancing
ramps, exempt BY DESIGN (they are the "realtime look", not rubber).

Honest verification state: the mechanism is landed and surgical, but
the user's exact frazetta putty column (~36deg device sheet) has not
been re-reproduced pose-for-pose in the harness — the kill is argued
from the design's own physics (silhouette smears now tear instead of
stretching), not yet observed on the reported sheet. Next device
round on arc content is the arbiter; if the column survives there,
the residual is wall-class (glancing ramp), which is a different
conversation (the fade band exists precisely to hide it).

## Addendum 80 (2026-07-18): A78 — the false disocclusions are BUDGET-GEOMETRY SPILL from the a76 law; the reveal extent needs per-pixel physics

User device round on the merged a76+a77 build (main PR#39; sheets
still stamped a72b — the stamp string was not bumped at a76/a77, fixed
as 428e3ef): holes all plugged, but "several regions that appear to be
false disocclusions in the SD view", plus residual taffy near the
staff and the horizon reading as attached to the astronaut.

Pose-exact repro at the sheet cams (star 0.182,-0.056; troll
0.147,0.008) with the claim-record maps classifies the SD complaint
decisively: around the troll figures the claimed region extends in
huge DIAMOND-shaped blocks, and across star's near floor as a zigzag
band — chamfer shapes, the geometry of the 4-neighbour hop budget,
visible in no image feature. Root cause: under farther-value-wins the
winning plane's claim extent is bounded ONLY by its seed's hop budget
(set from the LIP's window depth-step, (gmx-gmn)/sCone), swept
ISOTROPICALLY from the seed. Nearest-anchor previously hid this spill
by confining every plane to its Voronoi cell — the a76 flip exposed
an extent rule that was never physical.

The physical rule the record proposes (to prototype next): a revealed
pixel funds its own reach — a claim at chamfer distance h from its
lip is valid iff h <= (dQ[px] - fill) / sCone: the pixel's OWN
prominence over the fill, not the lip window's maximum, is what a
head move must overcome to uncover it. Wall pixels 100px from a fold
with only 0.2 of prominence stop qualifying; the woman's body at 0.35
prominence keeps its full band. Star's horizon strip and bottom band
partially predate a76 (the a60-era omnidirectional-mask classes the
user already flagged on the a60 build) — the prototype must measure
per-region deltas against the nearest-law baseline before claiming
them.

Also carried from this round: residual staff-area taffy (a77's snap
exempts the lifted thin features that ARE the near surface — fringe
behaviour at modest offset needs its own probe) and
horizon-on-astronaut (a75 is in the build; the suspect is the
a60-era ghost/wash band edge at horizon height — the parked taxonomy
workstream, to verify pose-exact, not assume).

## Addendum 81 (2026-07-19): A78 prominence bound LANDED — the SD mask is figure-shaped again

The per-pixel rule from Addendum 80, implemented as a claim gate in
bgDirectionalPlate (both claim branches, window._noPromBound reverts):
a claim at distance d from its lip is valid iff d*sCone <= dQ[px] -
fill — the pixel's own prominence over the fill funds its reach, with
tearStep/sCone (~24px) as the implied minimum that keeps small
figures' bands.

Measured: the troll's diamond blocks are GONE — the claim map now
hugs the figures (mask 34.7 -> 23.5); star's horizon strip — the
exact class the user flagged as incorrect — is gone (15.2 -> 14.1);
photo returns to its ORIGINAL a63b range (38.2 -> 29.1, range 24..33
restored); warrior 9.6 -> 9.2. The a76 gloop cure SURVIVES: at both
troll probe cams the woman renders clean with tighter wash than the
unbounded law (her 0.35 prominence funds ~140px, wider than her
body). Near-plate claims 19.8% (was 34.7 defective, 15.4 unbounded
a76 — the bound gives a little back because trimmed far claims let
some near anchors keep pixels at the fringes; the renders stay
clean). Suite: ALL PASS (13) with troll re-pinned 19..29 and photo
back at 24..33.

Still standing, pre-arc classes now cleanly separated from the a76
spill: star's bottom sawtooth band (the near floor genuinely
self-funds ~0.3 prominence over the mid-plain fill from footprint-
dent lips — present under BOTH laws and in the a60-era masks; its
sawtooth SHAPE is budget geometry but its existence is not a76's
doing) and the ghost/wash band. Both belong to the A79/ghost
workstream, not this one.

## Addendum 82 (2026-07-19): USER DECISION — figure-against-sky reveals keep the wash; SD owns the reveal content

The taxonomy question parked since a70 is answered by the user: when
a figure stands against sky and the camera moves, the revealed strip
KEEPS THE WASH (which renders as the translucent doppelganger in the
live look), and the SD inpaint pass is responsible for painting the
reveal correctly in final output.

Consequences, recorded so nobody re-litigates this by accident:
- The ghost figure and its horizon-height band edge (the user's
  "horizon picked up by the astronaut", confirmed pose-exact as the
  ghost's outline, not a geometry defect) are ACCEPTED in the
  live/realtime look. They are SD input, not defects.
- a70 depth-consistent reveal colours and the a69 membrane stay
  OPT-IN indefinitely (window._plateRowColor / _plateMembrane); the
  planned re-landing behind a tunneling invariant is CANCELLED unless
  the user reopens it.
- The ghost-class workstream is closed as a structural matter. What
  remains of the A79 device round is only the residual staff-area
  taffy (attribution probe running: cap-card dust vs stretch-net
  quads vs a51 tear-exempt adopted-ink rubber).

## Addendum 83 (2026-07-19): A80 viewpoint scan landed + the range question ANSWERED BY GEOMETRY — sCone was fade-end all along

The user directive from the a77-stamped device round: the SD regions
exceed what disocclusion will ever expose — "scan all possible head
positions within a range" (a feature memory; the closest ancestors
are the cone envelope and mask.B's parallax budget, both analytic
approximations of that union, never the union itself).

LANDED: the exact scan, in the quick SD-mask stage after the cliff
gate and before ink closure. For 8 directions x 4 magnitudes
(window._scanRange rescales; 1.0 = the sCone maximum), forward-warp
the FG depth into a z-buffer (2x2 splat, shifts anchored at the
scene's median depth — anchored at zero the whole frame translates
out and everything tests visible, the first cut's measured mistake)
and keep a claimed texel iff at some pose nothing nearer lands on its
own shifted position. window._noVpScan reverts. Suite ALL PASS (13).

THE FINDING: the scan trims almost nothing at full range (star 14.1
unchanged, troll -0.9, photo -0.4, warrior -0.5) — the a78 claim
mask already IS the visible union for the sCone range, because the
prominence bound and the visibility sweep are the same physics
(d*sCone <= prominence). And the range itself is now pinned by the
projection law instead of estimates: the vertex shader places
content in a [-outer, +inner] = [-0.02, +0.04] world volume, shift =
-ex*zOff/(0.2 - zOff), portal fit 1920px — at the fade-cone END
(45deg, ex = 0.2) the relative parallax computes to ~396px per unit
depth in bake space. sCone = 0.0025 encodes 400. The mask has been
serving exactly the fade-supported pose range all along.

What remains of the user's perception, honestly separated:
1. The mask shows the union over ALL directions at once; any single
   pose exposes roughly one side of each figure. A mask ~2x wider
   than any one view is CORRECT for inpainting (either direction can
   happen) — this is presentation, not a defect.
2. Vertical head travel to +-0.2 is rare in practice; the vertical
   sweep contributes area users may never see. Trimming vertical
   range is a legitimate product choice (e.g. _scanRange as a vector,
   or vertical t at half), NOT decidable unilaterally here.
3. The remaining putty in the show-SD state and the 0.691-offset
   sheet are beyond/at the fade boundary (45deg fades to black on
   device; debug sheets bypass the DOM fade overlay) — the fade is
   the designed answer there; residual staff-area taffy inside the
   band is the A79 chase (cap cards and stretch net exonerated by
   A/B; thin-lift halo is the remaining suspect).

## Addendum 84 (2026-07-19): A79 staff taffy ATTRIBUTED — torn thin-feature confetti; rigidify is the responding cure (default flip = user call)

The residual in-band taffy at the staff top (user's a77-round sheet,
star 0.182,-0.056) survived four A/B exonerations, each pose-exact:
cap cards hidden — identical; stretch net at 2x aggression —
identical; thin-lift OFF — WORSE (the lift was already consolidating
these features, as designed); and the a51 ink exemption was never
reached because the carrier is not exempt quads. What the render
structure says instead: the net/glider are sub-pixel line art whose
spanning quads correctly tear (staff-vs-sky is a huge cliff), and the
"taffy" is the torn remains rendering as dotted disintegration — the
a53 confetti class, for line art instead of figures.

The purpose-built cure responds: with window._enableRigidify = true
(a54, deliberately OPT-IN), 40377px in 15 small standing components
take their median standoff, the glider renders as one coherent unit
and the net veil consolidates visibly at the same pose. Not perfect
(some residue at the staff loop), but the class clearly yields.

NOT flipped by default tonight: rigidify billboards every small
standing component scene-wide (flattens internal relief — the reason
it sits behind a flag, and the a61 seat/billboard work partially
supersedes it for grounded content; the glider/net are airborne, so
the seat never covers them). Whether the confetti cure is worth the
flattening is the user's trade to make, with the three-way zoom
delivered (lift-on baseline / lift-off / rigidify).

Perf note for the device round: the a79 viewpoint scan adds real
bake time at 1920-wide bakes in the software-GL harness (star total
58.7s there; device GPU-adjacent JS will be far faster but watch the
stamp's bake ms) — if it reads slow on device, drop TS to 3
magnitudes or halve directions; the union degrades gracefully.

## Addendum 85 (2026-07-19): A81 — the "tons of taffy" was single-axis rubber the stretch net was STRUCTURALLY blind to; minor-axis cut landed

Correction on the record first: Addendum 83's "clean in-band" census
was wrong — judged on 593px thumbnails where 1-2px filaments vanish.
The user insisted ("just look at it", then "you're missing the taffy
from the staff"), and at 2x scale the streaks are unmistakable:
horizontal filaments trailing every silhouette (staff, net, glider,
ghost rim, crystal face), present INSIDE the fade cone at 0.20 and
faintly at 0.14. Eyes on the grid beat thumbnails, again.

Root cause, and it is structural: the stretch net's test was
  uvRate = max(length(dFdx(vUv)), length(dFdy(vUv))) < threshold.
Lateral parallax stretches ONE axis — a horizontally stretched
filament keeps a normal VERTICAL UV rate, so max() reports "not
stretched" no matter the threshold. That is why every tightening
(a52's 2x, the A79 probe's 0.5px) left the streaks untouched: the
rubber was invisible to the metric, not below its threshold.

The fix: also cut when the MINOR axis collapses —
  min(dFdx, dFdy) < threshold * 0.3.
The factor is the measured class separator: filament rubber runs
10-50x single-axis stretch; glancing cave walls and mild anamorphic
content (the protected realtime look) sit at 1.5-2.5x. The first cut
(factor 0.5) speckled the troll walls white — measured, reverted to
0.3, walls restored, streaks still dead. Star at 0.20: staff/net/
glider trails gone, sky clean, faint white rims at cut fringes are
the honest reveal of the wash behind (SD's territory by the user's
Addendum-82 decision). Suite ALL PASS (13); lit% 75.9 -> 75.6 (the
cut fragments, as expected).

## Addendum 86 (2026-07-20): night of verdicts — SV cut lands; membrane, wash-alpha, and the hole alarm resolved

1. ROTATION-FREE STRETCH CUT LANDED (a81 commit). The a80 minor-axis
   test used min of the two SCREEN-ALIGNED derivative lengths — still
   blind to diagonal stretch. Replaced with the minor singular value
   of the UV Jacobian (|det|/major): direction-independent by
   construction, same measured 3x class boundary. Suite ALL PASS (13)
   with it active; no visible change on any asset at the guard poses
   (the warrior "spokes" that motivated it turned out to be the
   painting's own crepuscular rays — a misaligned source crop, my
   error, corrected on the spot).

2. MEMBRANE: NOT the cure for the warrior banding. A/B under the
   full a76/a78/a80 stack (118984px re-based on the warrior): the
   staircase strips in the reveal column are pixel-comparable with
   the membrane on. The banding needs its own profile (plate depth
   quantization in wide reveals — a fresh workstream, to be
   instrumented with the claim-record tooling, not guessed at).

3. THE TROLL "EMPTY SPOTS", full resolution after two wrong turns:
   (a) the mid-image pale patches are RENDERED WASH (the SD-mask
   regions, per the user's keep-wash contract); (b) my "4.85% naked
   interior" alarm was a measurement-box error — the transparent
   zones are the FRAME BORDERS where the warped mesh pulls inside
   the canvas at 0.2 offset (black on device, white on the delivered
   PNGs — which is also what the user's "white spots" most likely
   were); (c) true interior naked holes are ~0.1% scattered flecks.
   Wash-alpha hypothesis falsified cleanly (baked colour is 100%
   opaque). The border zones are the margins/fade system's designed
   territory, not a defect of the bake.

Method note, three corrections in one night (thumbnail census, spoke
rays, hole box): every one came from reviewing evidence at the wrong
scale or the wrong crop. The suite catches number drift; only
full-scale eyes catch look drift. Both are now standing practice.

## Addendum 87 (2026-07-20): the warrior banding is NESTED-LIP STRIP STRUCTURE — frontier theory tested and rejected same hour

The claim-record profile of the warrior plate first suggested the
staircase was the a78 prominence frontier (the torso is wider than
2x its reach, leaving an unclaimed core at figure depth with a hard
step at the claim boundary). A 2x value-overshoot was implemented to
push that step beyond visibility — and the RENDER falsified the
premise: bands unchanged. Two reasons, both now measured: the torso
frontier hides behind the INTACT foreground figure (its interior
plate never shows), and the visible bands sit in the bear/sled
region, where the plate map shows mid-value anchors — the bands are
the FLAT CONTINUATION PLANES of a nested-occluder pile (bear over
sled over snow over valley), each lip's plane at its own depth,
meeting in steps at partially-visible positions. The overshoot was
REVERTED the same hour (masks back to ALL PASS at the exact a78
values; the 6-point mask growth it caused was a real cost with no
realized benefit).

The banding workstream's honest state: this is a DESIGN question —
how stacked flat continuations should meet inside one solid plate
(per-strip gradient carry between lips? accept the strips as SD
input?) — not a one-line fix. Parked pending that conversation,
with the plate map as the evidence base. Membrane already ruled out
by A/B (Addendum 86).

## Addendum 88 (2026-07-20/23 round): defaults exonerated; the comb was the stretch cut's binary edge; graded cut landed

The user's device round on stock main (their "wrong default settings?"
hypothesis) produced three corrections and one fix:

1. MY ATTRIBUTION ERROR, corrected: the sheet fields (relax=harmonic,
   seed=2, det=slope, fgSubRan) are OUR OWN footer — the build was
   stock. The "local delta" claim is withdrawn.
2. DEFAULTS EXONERATED BY A/B: relax (harmonic vs min) and seed
   (concentrated vs sharp) render pixel-identically in quick mode at
   the reported cam — the shipped defaults are render-inert here.
   The audit finding stands separately: they feed the FG-band build
   and were never varied in the arc (constants-inventory debt).
3. THE COMB ATTRIBUTED: one bake, runtime-uniform A/B — stretch cut
   ON = comb banding across the troll wall at 0.358; OFF = comb gone.
   The a80/a81 binary threshold oscillates row-by-row on terraced
   grazing walls at beyond-fade poses. In-band (0.20) remains clean.
   Also caught: a80/a81 landed without an explicit escape hatch
   (u_bandCutUvRate=0 serves as one; noted as a process slip).
4. FIX LANDED (a82): graded cut — hard discard only past 5x stretch,
   screen-dithered fade across 5x..2.8x, in-band (<=2.5x) untouched.
   The binary edge the comb formed along no longer exists. Verified:
   comb dissolved at 0.358; suite ALL PASS (13), lit% 75.6 -> 74.9
   (the widened graded band cuts slightly more, in range).

Also this round: the CPU-warp fast workflow proved both its value
(pure-arc baselines at exact cams in seconds) and its limit (blind to
fragment-level effects — it cleared a defect the GL A/B then
convicted; every CPU-warp verdict on fragment behavior must be
GL-confirmed).

## Addendum 89 (2026-07-23 round, cont.): the "horizon attached to the astronaut" is the WASH ERASING THE HORIZON — the parked reveal colors cure it

GL reproduction at the user's exact cams (-0.242,0.091 / 0.343,0.088)
on stock main: the plate DEPTH behind the astronaut is correct
(plain and sky at their right depths) — but the flat wash colour
erases the horizon line inside every reveal band, so the horizon
visually terminates at the band's edge, which follows the figure's
silhouette. The twice-reported "attachment" was never geometry; it
is a line-continuity property of the reveal COLOUR.

Evidence shot: the same cams with window._plateRowColor = true (the
a70 depth-consistent reveal colours, opt-in since a72b): the horizon
CONTINUES through the band — plain below, sky above, boundary at the
right height — and the doppelganger largely dissolves into
background-consistent fill. Residuals: mild streaking in the fill,
dither sparkle at these beyond-fade poses (a82's graded band is wide
out there).

DECISION REQUIRED (user's Addendum-82 keep-wash ruling stands until
they reverse it): the context that produced that ruling has changed —
the a78 prominence bound keeps reveal bands narrow and figure-shaped,
which was not true when "tunneling" was reported against the colours.
Recommendation: flip _plateRowColor default ON behind the suite, with
the wash as the escape hatch. Awaiting the user's call; not landed.

## Addendum 90 (2026-07-23 round, cont.): the foreground speckle — the cut fired where no backstop exists; mask-gated cut landed

User report ("tons of banding in the foreground, can't you see all the
transparent pixels?") — correct, and it exposed both a design hole and
a verification hole:

1. DESIGN HOLE: the stretch cut's safety premise ("the plate backs
   every reveal, so a discard shows real content") is FALSE on
   un-revealed ground and at frame margins — there a discard is a
   naked pixel. At the user's poses (+0.09 VERTICAL offset) the near
   dune is the most vertically stretched content in frame, so the
   graded band dithered across the whole foreground as a transparent
   speckle field.
2. VERIFICATION HOLE: all in-band cut verification used horizontal
   offsets only. Vertical-offset poses were never in the check set.
   They are now (the user's exact cams are the reference poses).

FIX (a83): the directional cut is gated by the SD mask — only
fragments whose bake proved a genuine reveal behind them may discard
(same physics as the smear snap's proud-of-plate gate). Ground
stretch outside the mask is the protected realtime look. Verified:
star foreground solid at both user cams (speckle gone); troll comb
still dead AND its wall dither gone too (same un-backed-cut disease);
filament streaks still die (they live inside the mask); suite ALL
PASS (13), quick lit% 74.9 -> 75.7 (un-cutting solid ground, as
expected).

## Addendum 91 (2026-07-24 round): the leg streamers — contact rubber is the mask gate's blind class; ramp-exempted hard cut

User report: "two obvious bits stretching from the astronaut leg to
the background... seriously, why are these things still a problem"
(localhost screengrab + sheet cam (-0.409, 0.074)).

REPRODUCED in GL at the exact sheet cam: the rear boot drags a
striped rubber band diagonally down the dune; the front boot smears
at contact.

ROOT CAUSE (measured, then convicted by A/B):
1. The boot-ground contact is a SUB-TEAR SOURCE RAMP: per-texel depth
   steps 0.016..0.024 at the ramp vs 0.002..0.004 on open ground
   (tearStep 0.06). It never tears, so it stretches as one connected
   band under offset — classic contact rubber.
2. Because it never tears, it never disoccludes: no reveal is baked
   behind it, so it CANNOT appear in the SD mask at any dilation
   radius. The a83 mask gate therefore protects exactly this class
   forever. (Mask dilation was considered and is dead on arrival —
   there is no mask within any radius of a depth-continuous contact.)
3. A/B conviction (a100 harness, one bake, two shots): stock = boot
   streamer present; u_sdMask swapped for a 1x1 white texture (the
   pre-a83 cut authority) = streamer DELETED — and the near dune
   erupts in the pre-a83 white speckle field. Both premises confirmed
   in one experiment: the gate causes the streamers, and removing the
   gate is not shippable.
4. Also checked: the plate is 100% opaque in canvas space (bufcache
   alpha scan), so pre-a83 naked pixels were a SCREEN-space coverage
   problem (warped plate pulling inside the frame), not missing plate
   content — a canvas-space plate-alpha gate would be all-pass and
   fix nothing. Rejected.

FIX (a84): the contact-rubber exemption. A fragment may cut WITHOUT
mask backing iff BOTH:
- it is in the HARD stretch tier (>=5x, the true-rubber class from
  the measured 10-50x vs 1.5-2.5x gap) — the dithered 2.8..5x band
  stays strictly mask-gated, because that band on legitimate grazing
  ground is precisely what speckled the near dune (a83) and the troll
  walls (a80); AND
- it sits on a cliff-scale source ramp: central-difference depth step
  at +-1 texel > u_bandCutMismatch (0.01), the midpoint of the
  measured 6x class gap above and this shader block's existing
  cliff-disagreement scale. Smooth ground that happens to stretch
  hard at extreme poses keeps its gate.
Hatch: window._noContactCut (uniform u_cutContactRamp).

VERIFICATION (GL, full scale, a101 harness — one bake per asset, the
u_cutContactRamp uniform toggled at runtime so every pair is
pixel-comparable):
- star (-0.409, 0.074): boot streamer cut back to the boot; the dark
  filament debris smeared across the ghost/reveal band is ALSO gone
  (same rubber class — hard-stretched fringes whose UVs fall just
  outside the scan-pruned mask). 2,923 px changed, +158 px deleted.
- star (-0.2, 0.05) in-range: heel fringe reduced, no new holes.
- star (0, +0.2) / (0, -0.2) vertical: +224 / +22 px deleted total,
  NO dune speckle field (the a83 disease was thousands of dithered
  px; the dither band's mask gate held, as designed).
- troll (1.053, -0.014) and (0.358, 0) — both BEYOND the 0.2 design
  boundary: a few small white slashes appear where rubber smear used
  to be (+691 / +306 px). Documented trade: outside the supported
  cone a deleted rubber fragment has no guaranteed screen-space
  backing (the warped plate has pulled inside the frame), so absence
  replaces gloop. In-range troll is untouched. This is the same
  statement as the view fade; the open target-range decision (user)
  governs whether these poses are ever content-bearing.
- Full suite: ALL PASS (13); star SD 14.1, ground 78.2; warrior 8.7 /
  83.7; photo 28.7 / 64.0; troll 23.5 / 94.7; quick lit 75.6, v1
  83.4, v2 100.0; dolly locks 1.0 / 5.0 px.
Landed as a84 (stamp v3.13.19-a84).

## Addendum 92 (2026-07-24 round, cont.): the banding/silk/staircase family — claim frontiers, not value competition; cone-envelope fill

User contract (stated this round, adopted as the pre-SD acceptance
bar): zero tunneling/extrusion, seamless plugs, no spill — the wash
stays as the honest "SD fills this" placeholder (row-colors and
pull-push-color demoted: placeholder aesthetics are not the problem).

ATTRIBUTION (measured first):
1. Warrior staircase REPRODUCED in GL at the user's cam (0.366,
   0.008): terraced strip cascade in the reveal behind the figure
   pile (a102).
2. Star "blue silk" boot ribbons attributed by layer isolation
   (a103 full / FG-only / plate-only): they survive without the FG
   and appear in the plate-only render — they are PLATE smear. The
   a84 contact-rubber cut killed the FG half of the class; the plate
   half remained.
3. One family, three costumes: silk, staircase, banding = depth
   steps INSIDE the plate fill, rendered as stretched walls by the
   solid plate.

ROOT CAUSE (from re-reading the fill law, not from memory): NOT
value competition — the lower envelope of competing floored planes
is continuous. The steps are CLAIM FRONTIERS: where a deep front's
reach dies (prominence bound d*sCone <= dQ-v2, hop budget), the
next-shallower holder takes over at a full step. Every frontier is a
wall.

FIX (a85): CONE-ENVELOPE FILL for object fronts. The prominence
physics becomes the value law itself: a front's bid rises at the
cone slope with path distance from its anchor, v = av + sCone*d
(carry[] accumulates per hop, including passRem traversal). Then:
- the field is Lipschitz(sCone) by construction — steps impossible;
- claims expire exactly where the envelope meets the local surface
  (v2 >= dQ-0.001): flush = invisible = seamless edge, zero spill —
  the user's contract, by construction;
- descent below anchor cannot occur (no runaway-to-zero — the
  disease that motivated three generations of floors);
- the prominence bound is subsumed (promOK returns true for cone
  fronts; keeping it would halve reach since prominence shrinks as
  the bid rises);
- fold/ground fronts keep the a63b measured-gradient continuation
  (receding ground legitimately descends; the cone rise is wrong
  for it) — the working dune/crest bands are untouched.
Hatch: window._noConeFill restores a84 exactly.

Predicted side effects to verify: SD mask % shifts (suite re-pin
with evidence if needed); internal figure anchors may win small
nearby mounds (continuous, slope-capped — not walls); a78's diamond
sawtooth class should die with the budgets' frontier role.

VERIFICATION: [pending — warrior user cams + in-range, star silk/leg
cams, troll + photo via suite, full suite; results below before
landing]

## Addendum 93 (2026-07-24 round, cont.): the banding root cause — 8-BIT INPUT DEPTH; a86 staircase dequantization

The elimination ladder that got here (each step measured):
1. a85 cone fill changed 717k px of plate DEPTH (steps halved
   3,536 -> 1,839, the A69 sky-pits filled) — but the RENDER changed
   only 7%: the visible cascade survived. User called it ("before /
   after look exactly the same").
2. Plate COLOR: smooth in both laws — not color striping.
3. Cap cards: probe shows 3,100 verts (~775 px) — three orders of
   magnitude too small for the cascade. (The a107 zero-diff was a
   true null, not vacuous.)
4. Plate mesh: 9,000,000 verts = full 3000x3000 — no decimation
   terracing.
5. FG silhouette: razor-sharp, 100% of cells tear — not figure
   rubber.
6. Remaining suspect measured and CONVICTED: every depth value in
   the bake sits EXACTLY on the 8-bit grid (max deviation 0.000000;
   211 levels on the pile slope). Terrace runs median 3px / p90
   22px; parallax per level 2.4px at fade-end, 4.4px at the user's
   0.366 cam. Flat 10-22px terraces jumping 2-4px each = the user's
   "3d banding with gaps", in BOTH layers, on every smooth slope,
   upstream of every fill/tear/scan law. Retroactively explains the
   boot-contact measurements too (0.0039 and 0.0235 = exactly 1 and
   6 levels).

FIX (a86): DEQUANTIZE AT THE SOURCE. Immediately after the quick
bake reads the depth PNG into dQ: along each axis, adjacent
constant-level runs differing by EXACTLY one 8-bit level are one
sloped surface — linearly interpolate between run centers; runs
differing by >= 2 levels keep their hard break (real cliffs are >=
tearStep = 15 levels; thin features are several levels proud). Axis
passes average. The existing dqDirty ship-back delivers the
reconstructed field to the FG float texture, the plate fill, tears,
scan — every consumer at once. Quick path only for now (v1/v2 have
separate reads). Hatch: window._noDequant.

Relation to a85 (cone fill): kept — it fixed a real, separate defect
(claim-frontier steps, sky pits) and its "no visible change" is now
explained: the dominant banding was in the input signal, one level
upstream.

VERIFICATION: [pending — warrior user cams, star cams, troll comb
cams (the graded-cut interaction must be re-checked: terraced
grazing walls were 8-bit staircases too), full suite]

## Addendum 94 (2026-07-24 round, cont.): the disocclusion sheet — the PLATE never tears; a87 plate tear

User evidence: a device sheet at cam (-0.268, 0.002) whose MESH
FOOTPRINT panel is white across the entire reveal column — something
is COVERING the disocclusion rather than leaving it open. User:
"clearly still loads of stretching / tunneling connecting bg to fg
instead of just leaving the disocclusion hole".

ELIMINATION (6-agent parallel audit + direct buffer measurement; the
agents' silhouette theory was itself falsified by measurement, see 1):
1. FG TEAR — NOT the culprit. The agents measured the RAW depth PNG
   (66.7% of the outline sub-tear: aprons 3-6px, steps 8-15/255 all
   just under tearStep 0.06 = 15.3/255) and concluded the mesh never
   tears. Measuring the field the tear ACTUALLY reads (dQ exported
   from a real bake) refutes it: 682/682 silhouette crossings exceed
   tearStep. The live-bake sharpener (A35 binarization + 4-pass ramp
   collapse) does collapse the aprons before the quick bake reads
   them. Recorded because it was nearly acted on: the raw map is not
   the baked map.
2. Cap cards: 3,100 verts (775 quads) — three orders of magnitude
   too small for the sheet. Cards-off render: pixel-identical.
3. Plate colour: smooth in both fill laws. Plate mesh: 9,000,000
   verts = full resolution, no decimation terracing.
4. CONVICTED — the plate. A50 gave the plate the FULL UNTORN index
   (correctly: sharing the pre-torn FG index re-drew lifted ink
   strokes as through-holes). But a full index also spans the
   PLATE'S OWN cliffs, and those are real: 93.2% of plate steps >
   tearStep sit exactly on the claimed/unclaimed frontier, where a
   ground continuation (~0.35) abuts visible sky (0.00). Rendered
   solid, that step stretches ~290px at the user's cam — the sheet.
   (0.3% sit on a dQ cliff: the plate is not carrying the figure's
   silhouette; it is carrying its own fill frontier.)

FALSIFIED en route: extending the cone envelope over the unclaimed
interior (grassfire from the claim frontier, clamped to the surface).
Simulated exactly on the exported buffers: plate steps 10,183 ->
12,186 (WORSE), sheet width 728px -> 704px. The min() with the
surface creates new creases wherever the envelope meets visible
content. Not implemented.

FIX (a87): build the plate's index from the PLATE's depth, dropping
spanning triangles whose own 3-vertex span exceeds tearStep. Same law
as the FG tear and as the fill's a76 value rule — depth steps belong
at silhouettes, which tear, never inside a rendered surface. A50's
reason for the full index is preserved: this index is built from P,
where adopted ink was never a cliff. Behind a torn plate cliff is a
reveal of a reveal: no capture carries it, the flood already claimed
it into the SD mask, and absence is honest until SD paints.

MEASURED (CPU warp, warrior at the user's cam): canvas coverage
98.8% -> 98.7% — the far side of each cliff covers its own hole — and
the streaked sheets disappear. Hatch: window._noPlateTear.

STATUS: committed to arc-fix (9f10180), NOT merged to main. GL
confirmation and the suite are blocked by repeated container kills
(~15 consecutive Chromium runs killed at exit 144). CPU warp is
measured-blind to fragment-level effects (Addendum 86 rule), so the
plate tear is NOT verified for the stretch-cut interaction yet.

## Addendum 95 (2026-07-24 round, cont.): the sheet is a FOLDED fill — sCone was never resolution-scaled (a88)

The user's a87 device sheets (cams 0.463 and -0.429) still showed the
sheet, with the console confirming a87 fired: "plate tear: 15789
spanning triangles dropped (0.09% of the plate)".

TWO FINDINGS, one of them a correction to a87 itself.

1. a87b (bug in my own fix): the tear tested plateQ — the pre-plug
   FLOOD field — while the plate renders plateF (plateQ overwritten by
   the plug depth inside the SD region, row-flipped for upload). The
   plug's own cliffs were invisible to the test. Now reads plateF with
   the flip. Predicted effect is still small, because of finding 2.

2. THE SHEET IS NOT A CLIFF. Measured on the exported buffers: only
   0.114% of plate cells carry a step > tearStep. A tear-based fix
   cannot remove a smooth ramp. What the ramp does instead:

   Reprojection displaces by k*depth, k = 396*(pw/1920)*(ex/0.2) px per
   depth unit. A surface whose slope exceeds the grazing limit 1/k does
   not merely stretch — the mapping REVERSES and the surface FOLDS,
   rendering as an inverted sheet lying across the reveal.

   sCone (the fill's rise per PIXEL) was a fixed 0.0025, calibrated once
   against a 1920-px bake (1/0.0025 = 400 ~ the measured 396) and never
   scaled with source resolution. A pixel is not a fixed angle:

     asset    pw     shipped/correct   fold onset
     star    1920      1.00x           ex 0.200  (= fade-end, by design)
     photo   2047      1.07x           ex 0.188
     warrior 3000      1.56x           ex 0.128  <-- inside the cone
     troll    851      0.44x           ex 0.451  (safe, under-reaching)

   At the user's warrior cams, 87-92% of the CLAIMED FILL is folded.
   This is the long-standing asset dependence — "silver warrior is a
   total mess" while star is acceptable and troll shows a different
   defect class entirely. It also retro-explains a85's "no visible
   change": a Lipschitz(sCone) field is exactly a field at 1.56x the
   fold limit everywhere at 3000px.

FIX (a88, geometric not tuned): the fill may rise at most one grazing
limit per pixel — sCone = 1/k = 0.0025 * 1920/pw — applied at the
quick-bake and v1 call sites. Hatch: window._sConeFixed.

CONSEQUENCE for the suite: the corrected slope changes reach (the
prominence bound d*sCone <= prominence loosens at high resolution) and
therefore the SD mask percentages. warrior and troll pins are expected
to move; they must be re-derived from evidence, not widened to fit.
Suite still not runnable (container kills). Merged to main (fdc1da1)
at the user's explicit request for device testing.

METHOD NOTE: three mechanisms were implicated in one day for one
symptom (a86 quantization, a87 plate tear, a88 fold). Only a88 is
supported by a quantitative model of the symptom. a87 stays because its
premise (a rendered surface must not span its own cliffs) is sound and
its cost is 0.1% coverage; a86 stays because the 8-bit staircase is
real. But the record should show that a86 and a87 were BANDING fixes
adopted before the banding was explained, and the explanation is a88.

## Addendum 96 (2026-07-24): CONSTANT PROVENANCE AUDIT — what else is a88 waiting to happen

User request after a88 ("scared we're going to end up going down a
bunch of other rabbit holes once we stress test with a lot of
different images — or a video sequence"). Full sweep of the bake,
plate, tear and cut paths, classified by DIMENSION, because that is
what a88 turned on: a constant is only safe if its units are
invariant to the thing you are about to vary.

FAMILY A — RESOLUTION-SCALED (the correct pattern, ~25 constants).
RWD, BOOT, KWALK, RF, KE, KC, RS, RN, RD, BOUNDR, RBH, passesC,
scrubReach, fringePasses, u_bandCutUvRate (1/w), and now sCone.
HAZARD FOUND: TWO calibration bases coexist — 16 uses of "* pw/1200"
and 3 of "* pw/1920". Constants tuned against different reference
widths disagree about what "typical" means; any constant whose
partner was tuned on the other base is off by 1.6x. Not a bug today
(each is self-consistent) but it is the exact soil a88 grew in.
Recommend one declared reference width with the base named at each
site.

FAMILY B — DIMENSIONLESS RATIOS (safe by construction). svRatio
0.2/0.16 band, seed density 0.25, area caps as a fraction of PNq,
prominence bound (a ratio of depth to distance*slope). These do not
care about resolution, depth range, or frame rate.

FAMILY C — PIXEL-DIMENSIONED AND NOT SCALED (the a88 class, LIVE):
  * bgBandMaxGrowPx = 28 — used as a bgSlide2D window radius on the
    SOURCE grid, and multiplied further (standCap = x4, RPar = x2,
    SWEEP7 = x4). Across the current four assets (851..3000 px) the
    same 28 px is a 3.5x range of physical reach. HIGHEST RISK after
    sCone: it sets floor fields, protrusion flattening and the stand
    cap.
  * FULL_FLOOD_ITERS = 192, FLAG_ITERS = 256, LAKE_ITERS = 128,
    HARMONIC_ITERS = 96 — GPU ping-pong counts ARE the flood reach in
    canvas px. The code says it outright: "must exceed the widest FG
    blob's radius in px". Exceeded => the plate is silently
    INCOMPLETE (no error, no log). A large canvas or a big central
    figure crosses this quietly.
  * bgBandCutDilatePx = 4, bgStreakFadeNearPx = 8, FarPx = 40,
    edgeDilationRadius = 1.5 — same class, smaller blast radius.
  Fix pattern: express each as a fraction of the working width, the
  way RWD/BOOT already are.

FAMILY D — DEPTH-UNIT CONSTANTS (the VIDEO risk). fgTearStep 0.06,
bandCutMismatch 0.01, bandCutMaxGrad 0.04, QUANT 0.002, despeckle
0.02, rigidify 0.02, figure/sky 0.2 / 0.05, luma edge 0.10.
Monocular depth is normalised PER IMAGE, so 0.06 means "6% of this
image's own range". Measured p95-p5 spread: star 0.87, warrior 0.77,
troll 0.72, photo 0.61 — a 1.4x variation across four assets that
happen to be similar (all wide scenes with sky). tearStep is
0.07-0.10 of typical relief on all four, which is why the constant
has survived. It will not survive:
  * a flat subject (portrait, macro, frontal architecture): the
    spread collapses, 0.06 becomes a large fraction of the range,
    NOTHING tears — the same sheet symptom as the warrior, different
    cause;
  * VIDEO: per-frame normalisation makes the threshold breathe frame
    to frame, so tear/cut decisions FLICKER on static geometry. This
    is the single biggest hazard in the file for the video path.
  Fix direction: make depth thresholds relative to the image's own
  measured spread (k * (p95-p5)), and normalise depth ONCE PER SHOT
  rather than per frame.

FAMILY E — GEOMETRY CONSTANTS THAT ARE NOW LOAD-BEARING. The
reprojection scale k = 396 px per depth unit at the fade-end exists
only in a COMMENT, and a88's sCone now depends on it. If the fade
cone (35/45 deg), the portal distance (0.2) or the volume depths
change, sCone goes silently stale — the a88 failure mode exactly,
one level up. Recommend computing k from the same constants the
vertex shader uses instead of restating it.

FAMILY F — STRUCTURAL SCALE ASSUMPTION. MESH_DENSITY_FACTOR = 1.0
gives one vertex per source texel: the warrior is 9,000,000 vertices
/ 18,000,000 triangles. Tear granularity, memory and mobile fill
cost all scale with source resolution, and a 4K source doubles it
again. The tear's meaning also changes with resolution (a "1 px
step" is a different physical slope per asset) — the same disease as
sCone, in the geometry rather than in a constant.

PRIORITY (highest expected pain first):
  1. Family D depth thresholds — blocks video and any flat subject.
  2. bgBandMaxGrowPx family — blocks resolution generality today.
  3. Flood ITERS truncation — silent incompleteness, no diagnostic.
  4. Derive k from shader constants (kills the a88 class at source).
  5. Unify the 1200/1920 calibration bases.
  6. Mesh density policy for >=4K and mobile.

## Addendum 97 (2026-07-24): INVARIANCE PASS — every constant I introduced, by dimension, with citation

Addendum 96 audited the FILE's constants and gave MY OWN a pass. The
user called that out. Re-audit of a76-a88 against the axes the project
must survive — resolution, aspect, depth normalisation, source BIT
DEPTH, canvas/zoom framing, and time — with the code cited.

THREE OF MINE WERE WRONG (fixed in a89):

1. METRIC MISMATCH (a85 cone fill; moebius.js:9283 old form
   `carry[i] + sCone`, neighbour set :9244 is 4-connected).
   The rise was accumulated PER HOP over a 4-connected flood — a
   MANHATTAN metric — while the prominence bound it replaced (:9343,
   `dxp*dxp + dyp*dyp`) and the physical fold limit are EUCLIDEAN. A
   diagonal path pays 2*sCone over sqrt(2) px = 1.414x the intended
   slope. Consequence: after a88 fixed the resolution scaling,
   DIAGONAL fill still folded at ex = 0.2/1.414 = 0.141, inside the
   cone. Fixed: evaluate from the carried anchor, v = av + sCone*|p-a|
   — isotropic, path-independent (a zig-zag cannot inflate it, the
   disease that motivated the a63b descent floor), same metric as the
   bound it subsumes.

2. BIT-DEPTH ASSUMPTION (a86 dequantiser; the run-merge test was
   `<= 1.001/255`). The premise is "runs one quantum apart are one
   sloped surface". Hardcoding 1/255 means: on a 16-bit depth PNG the
   pass is a SILENT NO-OP (every real step is far more than one 8-bit
   level apart), and any genuinely smooth slope with sub-1/255
   neighbour differences would be interpolated as if it were
   quantisation. Fixed: detect the grid the samples actually sit on
   (255 / 4095 / 65535), skip cleanly and log when depth is
   continuous. NOTE: the whole a86 mechanism only exists because the
   pipeline ingests 8-bit depth; a float depth path removes the need
   for it rather than tuning it.

3. TIE-BREAK EPSILON (a76; `QUANT = 0.002`). That is half an 8-bit
   level (1/255 = 0.0039) — an 8-bit assumption wearing a decimal
   costume. On a 16-bit source it is 131 quanta, so real value
   differences would be swallowed as ties and the farther-value-wins
   law would silently degrade to nearest-anchor. Fixed: QUANT =
   tearStep/32, which also follows any depth-range renormalisation.

VERIFIED INVARIANT (checked, no change needed):
 * a78 prominence bound: (px^2)*(depth/px)^2 <= depth^2 — dimensionally
   homogeneous on both sides; correct under any resolution once sCone
   is correct.
 * a88 sCone isotropy: square pixels give the same px-per-world-unit in
   x and y, so one sCone serves both axes on non-square images.
 * a80-a83 band ratios (0.2 / 0.16 of the threshold): dimensionless.

STILL OUTSTANDING IN MY OWN WORK (named, not yet fixed):
 * a83 stretch cut threshold u_bandCutUvRate = 1.0/w assumes THE MESH
   SPANS THE CANVAS. Under zoom, dolly or letterboxing the expected UV
   rate changes and the tier boundaries move with framing rather than
   with content. Not a resolution bug — a FRAMING bug.
 * a79 scan: z-tolerance 0.02 and the 2x2 splat are pixel/depth
   constants that were never derived; the pose count (8 dirs x 4
   magnitudes) is fixed regardless of how many pixels of reach the
   range implies, so it undersamples as range or resolution grows.
 * a84 contact-ramp threshold reuses u_bandCutMismatch (0.01 depth) —
   Family D (depth-normalised), inherits the video/flat-subject risk.
 * k = 396 px per depth unit at the fade-end still lives in a COMMENT
   and a88 depends on it (Addendum 96, Family E).

PROCESS NOTE: the general lesson is not "check resolution". It is that
every constant needs its UNITS declared at the site, and a unit that
mentions px, a depth value, or a canvas dimension is a promise that
something upstream will never change. The suite should assert the
invariance directly — bake the same asset at 2 resolutions and 2 bit
depths and require the mask/coverage metrics to match within
tolerance — rather than pinning per-asset numbers that hide the drift.

## Addendum 98 (2026-07-24): AUDIT PLAN + PHASE 1 RESULTS — and a88's own premise is now in doubt

PLAN (standing, to be worked in order):
 Axes the system must survive: R resolution (pw x ph), A aspect /
 non-square, B source bit depth, N depth normalisation (per image AND
 per frame), F framing (canvas size, zoom, dolly, letterbox), T time.
 Unit taxonomy: ratio (safe) / depth (fails N,B) / src-px (fails R,A) /
 canvas-px (fails F) / world (fails view setup) / iterations-as-reach
 (fails R,F SILENTLY) / colour (fails colour space, medium).
 Phase 1 mechanical census (done). Phase 2 triage by blast radius.
 Phase 3 fix provable, record the rest. Phase 4 invariance TEST: same
 asset at two resolutions and two bit depths, metrics must match — the
 test that would have caught a88 and a89 on the day they landed.

PHASE 1 — constlint.py (committed, harness/constlint.py). Census of
moebius.js: 501 unclassified, 209 shader, 127 depth-units, 101 colour,
70 src-px, 51 iterations-as-reach, 38 correctly scaled, 8 canvas-px.

FINDING 1 — THE SAME PHYSICAL CONSTANT HAS FIVE DEFINITIONS AND THREE
REFERENCE WIDTHS:
   L8076   sCone  = 0.0015 * 1920 / w
   L8404   sConeV = 0.0015 * 1920 / pw
   L9944   sCone  = 0.0025 * 1920 / pw     (a88, quick bake)
   L12031  passed = 0.0025 * 1920 / pw     (a88, v1 dir-plate)
   L12179  sCone  = 0.0025 *  851 / pw     (v1 plug)
   L12785  riseCap= 0.0025 *  851 / pw
 851 is the TROLL's width; 1920 is the STAR's. Two assets were each
 used as "the" reference, so the same cone slope differs by 851/1920 =
 0.44x between call sites, and the 0.0015 family differs again by
 0.6x. A88 only fixed the sites it touched.

FINDING 2 — the codebase ALREADY knows the metric lesson: 1.41421356
(sqrt 2) appears at 14 sites as the diagonal chamfer weight in the
budget/distance propagations (L8417, L10192, L10452, L13553, ...).
The a85 cone I wrote ignored it. My a89 fix is the same lesson,
arrived at late.

FINDING 3 (the serious one) — k IS NOT A CONSTANT, so no fixed sCone
can be right. Derived from the code's own geometry, not comments:
 * displacement is SMOOTHSTEP (L1661-1668, portalNorm 0.5, outer 0.02,
   inner 0.04), so d(zOff)/d(depth) is 0 at both ends and peaks at
   1.5x the mean — k varies 2x ACROSS THE DEPTH RANGE alone, and is
   ~2x larger in the near half than the far half.
 * the world->px scale is pw / layerWidth, and layerWidth depends on
   the image ASPECT vs the frame (L2533, terrarium 0.16 x 0.09):
   star 0.1306, warrior 0.0900, troll 0.0749, photo 0.1353 — a 2.3x
   spread between star and warrior at equal pw.
 * D (camera distance, 0.2 default) and FOV are user/device variable;
   ex = 0.2 corresponds to exactly 45 deg, confirming the fade-end
   pairing, but a dolly changes D and therefore k.
 A first-principles evaluation gives k ~ 0.43 * pw at the mean slope
 versus the 0.206 * pw the a88 comment asserted — a factor ~2 apart,
 and BOTH are wrong as single numbers because k is a field.

STATUS OF a88: it fixed a real defect (the constant did not scale with
resolution at all) and its direction is certainly right, but its
MAGNITUDE rests on a comment-sourced k that a derivation now
contradicts by ~2x. Do not treat a88's number as settled. The correct
form is not a better constant: the fill's slope cap must be computed
from the LOCAL displacement derivative — the same smoothstep the
vertex shader uses, evaluated at that pixel's depth, divided by the
plane's px-per-world scale. That makes it invariant to R, A, depth
position, and (if read at bake time) to the volume-depth sliders too.

NEXT (Phase 2/3, in order): (1) unify all five sCone sites on one
derived function; (2) the depth-unit family (Family D, Addendum 96) —
blocks video; (3) the iterations-as-reach truncation; (4) build the
Phase 4 invariance test and put it in the suite BEFORE any further
constant is touched.

## Addendum 99 (2026-07-24): THE INVARIANCE TEST RAN — AND FAILED ON ITS FIRST RUN

harness/invariance.js, troll, same scene at 851px and 425px, scan
disabled (metrics read the plate field pre-scan), tolerance 15%:

    metric   full 851    half 425    drift    verdict
    mask%      13.19       16.43     19.7%    FAIL
    fold%       2.06        2.82     27.1%    FAIL

a88's law predicts a fold ratio of 1.00 — sCone*k = (0.0025*1920/pw) *
(396*pw/1920) = 0.99 is pw-independent BY CONSTRUCTION. Observed: 1.37.
So the fill's slope law is now resolution-invariant on paper and the
BAKE still is not. a88 was necessary and is not sufficient.

ROOT CAUSE OF THE RESIDUAL (measured directly on the two depth maps):

    depth map        cells over tearStep 0.06     mean |per-texel step|
    full  851              0.337%                      0.00170
    half  425              0.623%                      0.00338
    ratio half/full         1.85                        1.99

tearStep is compared against ADJACENT-TEXEL depth differences (the FG
tear is a 3-vertex span on a vertex-per-texel grid, moebius.js:10603;
the seed test at :9179-9183 is the same shape). A genuine
DISCONTINUITY is resolution-invariant — the full cliff height appears
in one cell at any resolution. A steep but SMOOTH slope is not: its
per-texel step is slope x texel size, so halving the resolution
DOUBLES it (measured: mean step 0.00170 -> 0.00338, ratio 1.99). The
threshold therefore migrates across the slope population as resolution
changes: 1.85x more of the image becomes tear-eligible at half
resolution, which reshapes the plate, the claims and the fold count —
1.85 upstream producing the 1.37 observed downstream.

CLASSIFICATION: tearStep is not a depth constant (Family D) as
Addendum 96 assumed. It is a MIXED unit — depth per texel — which
means it belongs to BOTH the resolution family and the depth-
normalisation family. It fails R and N simultaneously. The same is
true of every threshold compared against an adjacent-texel difference:
the despeckle TOL, the smear-snap step gate, the ramp-collapse test,
the a84 contact-ramp central difference.

WHAT THE CORRECT FORM LOOKS LIKE: the plate code already has it. The
flood's barrier test (:9032) compares a WINDOWED range (dwMx - dwMn
over RWD, and RWD scales with pw) against tearStep — a depth step
across a FIXED FRACTION OF THE FRAME, which is resolution-invariant by
construction. The FG tear and its siblings compare across ONE TEXEL,
which is not. Making the tear windowed (or equivalently expressing
tearStep as depth per unit of frame width and multiplying by the texel
size at test time) removes the mixed unit.

PROCESS: this is the first mechanised invariance result in the
project. It found in one run what four constant fixes across a day did
not, and it contradicts a comfortable assumption (that a88 "fixed
resolution"). The suite's per-asset pins could never have shown it:
each asset reproduces its own pinned number while meaning something
different. Recommendation stands — no further constant work, and no
merge of a89/a90 to main, until the tear's unit is fixed and this test
passes on all four assets.

## Addendum 100 (2026-07-24): a92 falsified — the resolution drift is SYSTEMIC, not a constant

Continuing the invariance work with the rule the user set: any number
must be cited and defended, and a change that does not deliver comes
out.

a91 LANDED (derived, cited). The per-cell tear threshold is the FOLD
LIMIT: a cell spanning dd displaces its ends k*dd px, and at k*dd = 1
cell width the cell inverts. With one vertex per texel that is
dd = 1/k = the cone slope, so the tear threshold and the fill slope are
the same physical quantity. The old fixed 0.06 permitted folds of
T = 10.5 (troll) / 23.8 (star) / 25.3 (photo) / 37.1 (warrior) — and
varied 3.5x with resolution. Trade curve measured on the three depth
maps (torn% / surviving-folded%): at T=1, 2.25-3.27% / 0.00%; at
today's T, 0.10-0.22% / 2.15-3.06%. Same cells either way: 2-3% of the
mesh was rendering as folded rubber and now tears into a53 cap cards.
On device (troll 851): threshold 0.00564, 78,916 of 1,737,400 cells
torn, 11,163 orphans capped.

a92 TRIED AND REVERTED. The cliff-SEED threshold has the same mixed
unit; expressed invariantly it is a REVEAL WIDTH (step*k >= N px).
Measured on the troll pair (851 vs 425):
    mask drift 19.7% -> 17.0%   (slightly better)
    fold drift 27.1% -> 30.4%   (worse)
Premise falsified: the seed threshold is not where the drift lives.
Reverted; the unit observation is kept here rather than in the code.

WHAT THIS ESTABLISHES: the resolution drift is SYSTEMIC. constlint
counts 127 depth-unit constants, and essentially every one of them is
compared against an adjacent-texel difference somewhere. Fixing them
one at a time is whack-a-mole with a 2-bake measurement per attempt.
The honest options are (a) a single normalisation applied ONCE at
ingest — resample every source to a canonical working width so every
downstream per-texel constant sees the same texel scale (this makes all
127 correct simultaneously, at the cost of a resample), or (b) a
systematic rewrite of every per-texel test into windowed form. (a) is
one change with one number to defend (the working width) and is the
recommended path.

ALSO ESTABLISHED: my metric set is too narrow. mask% and fold% are
computed from the PLATE FIELD, so they are blind to a91 (FG geometry)
and a87 (plate geometry) — both showed zero movement in these numbers
while changing tens of thousands of triangles. Any future invariance
run must include a geometry metric (torn fraction, cap-card count) and
a rendered-output metric, or it will keep reporting "no change" for
changes that matter.

## Addendum 101 (2026-07-24): CONSTANT RATIONALE — every number I set, derived and cited

The user's rule: every constant must be cited with its rationale. This
is the complete register for the constants introduced or changed in
a76-a93, each with UNITS, DERIVATION, and the MEASUREMENT that supports
it. Anything not derivable is named as such.

--- DERIVED FROM GEOMETRY (no freedom) ---

1. sCone — cone slope. UNITS depth per source pixel.
   DERIVATION: the fill may not exceed the grazing limit, 1/k, where k
   is the reprojection scale in px per depth unit at the fade end.
   k scales with pw (a pixel is not a fixed angle), so
   sCone = 1/k = 0.0025 * 1920/pw.
   STATUS: the FORM is derived and verified (sCone*k = 0.99, pw-
   independent by construction). The MAGNITUDE rests on an empirical
   anchor (~400 px per depth unit at 1920) that a first-principles
   derivation contradicts by ~2.5x; k also varies 2x across the depth
   range (smoothstep) and 2.3x with aspect (layerWidth). NOT SETTLED —
   Addendum 98. One definition now (a90); the derived form is behind
   window._coneSlopeDerived awaiting an on-device measurement of k.

2. Per-cell tear threshold = 1.0 * sCone (a91). UNITS depth per texel.
   DERIVATION: a cell spanning dd displaces its ends k*dd px; at one
   cell width the cell inverts. The fold limit IS the cone slope, so
   tear threshold and fill slope are one quantity.
   MEASUREMENT: the old fixed 0.06 permitted folds of T = 10.5 (troll)
   / 23.8 (star) / 25.3 (photo) / 37.1 (warrior), varying 3.5x with
   resolution. Trade curve on the three depth maps, torn% /
   surviving-folded%: T=1 gives 2.25-3.27% / 0.00%; the old operating
   point gave 0.10-0.22% / 2.15-3.06%. T=1 is where folded cells reach
   zero — the physical limit, not a preference.
   DEVICE: troll 851, threshold 0.00564, 78,916/1,737,400 cells torn,
   11,163 orphans capped. Invariance: 2.5% drift across 2x resolution.

3. Cone metric = EUCLIDEAN from the anchor (a89). DERIVATION: the
   prominence bound (dxp^2+dyp^2) and the fold limit are Euclidean;
   a85 accumulated per hop over a 4-connected flood = Manhattan, which
   is sqrt(2) too steep on diagonals (diagonal fill folded at ex 0.141
   even after a88). The file's own budget propagations already use
   1.41421356 as the diagonal chamfer weight at 14 sites — the
   precedent was there.

4. QUANT = tearStep/32 (a89). UNITS depth. DERIVATION: a tie-break
   epsilon must be a fraction of the scale it guards (the tear step),
   not a fixed 0.002, which was half an 8-bit level and would swallow
   131 quanta of a 16-bit source.

5. Depth quantum = DETECTED, not assumed (a89). The dequantiser tests
   the sample grid against 255/4095/65535 and skips when the depth is
   continuous. Hardcoding 1/255 made it a silent no-op on 16-bit input.

6. Window floors = 1 texel (a93). UNITS texels. DERIVATION: the
   windows are already fractions of frame width (0.33%); the only
   floor that is not a resolution-specific choice is the information
   limit, one texel. MEASUREMENT: the old Math.max(3,...) pinned RWD to
   3 texels at both 425 and 851 px = 0.71% vs 0.35% of frame.
   RESULT: mask invariance 19.7% -> 3.7%, mean drift 16.4% -> 8.9%.

7. Seed budget probe = RWD, not a fixed +-3 (a93). Same derivation:
   it measures the smear scale, so it uses the smear-scale radius.

--- INHERITED, NOT DERIVED (named, with their status) ---

8. fgTearStep = 0.06. UNITS depth, used at CLIFF scale in windowed
   tests whose windows scale with pw — dimensionally acceptable there.
   Its value is inherited and not derived; it now governs only the
   windowed tests, not the per-cell tear (a91 replaced that use).

9. SEED_REVEAL_PX = 24 (a92) — TRIED AND REVERTED. Expressing the lip
   threshold as a reveal width is unit-correct, but measured: mask
   drift 19.7% -> 17.0%, fold drift 27.1% -> 30.4%. Premise falsified;
   reverted rather than carried.

10. u_bandCutUvRate = 1/w — assumes the mesh spans the canvas. Fails
    under zoom/dolly/letterbox. Named in Addendum 97, not yet fixed.

11. Scan z-tolerance 0.02, 2x2 splat, 8x4 pose grid — never derived.
    Named in Addendum 97, not yet fixed.

--- WHAT THE TEST NOW SAYS ---
Troll 851 vs 425 after a93: mask 3.7% PASS, fgTorn 2.5% PASS, orphans
7.8% PASS, plateTear 9.3% PASS, fold 21.1% FAIL. The fold residual is
dominated by the TEST INPUT: NEAREST downsampling changes the depth
map's own fold-eligible population by 24.3%, larger than the 21.1%
output drift. A synthetic analytic depth map is required to isolate the
code side; a resampled photograph cannot.

--- THE CORRECTION TO "127" ---
Addendum 96 reported 127 depth-unit constants. That was a keyword
bucket, not a defect count. Split by what each is compared against:
41 are compared to an absolute depth VALUE (safe — depth is normalised
0-1) and 5 to a per-texel DIFFERENCE (the mixed-unit class). The
headline number was overstated by ~25x, which is its own failure of
rigour and is recorded as such.

## Addendum 102 (2026-07-24): the analytic instrument, and a rejection overturned

TWO INSTRUMENT DEFECTS FOUND AND FIXED, then one earlier verdict
reversed as a consequence.

INSTRUMENT DEFECT 1 — resampled input. Comparing a photograph at two
resolutions compares two DIFFERENT depth maps: NEAREST downsampling
changed the troll's own fold-eligible cell population by 24.3%, larger
than the 21.1% output drift being attributed to the code. Fixed with
harness/synth.py: an analytic scene (sky, receding ground, steep wedge,
hard-cliff figure, thin bar) whose features are FRACTIONS of the frame,
evaluated at each target resolution — the same scene at two sizes, not
a filtered copy of one.

INSTRUMENT DEFECT 2 — 1D populations normalised by 2D area. Fold cells
and torn cells live on EDGES: their count scales with pw, while total
cells scale with pw^2, so "percent of cells" carries a spurious 1/pw.
Verified on the analytic inputs: as a percent of area 0.249 vs 0.496 (a
50% apparent drift, entirely artefact); per unit WIDTH 2.24 vs 2.23
(0.4%). Several earlier FAIL verdicts were partly this.

VERDICT ON THE CLEAN INSTRUMENT (1200 vs 600):
    mask % (area, scale-free)   18.24 / 18.00    1.3%  PASS
    FG torn / width              6.72 /  6.75    0.4%  PASS
    fold cells / width           4.46 /  3.39   24.0%  FAIL
    plate torn / width           88.2 / 61.7    30.1%  FAIL
a91's derived tear is invariant to 0.4% — the derivation approach is
confirmed to work, on a scene built to test exactly that.

REJECTION OVERTURNED (a92 -> a95). The reveal-width seed threshold was
reverted in Addendum 100 on evidence from BOTH faulty instruments.
Re-tested cleanly: mask drift 1.3% -> 0.6% (improved), fold and
plate-torn unchanged. The mask is the user-facing quantity — it IS the
SD region — so the form is reinstated. The lesson is not about this
constant: a falsification is only as good as the instrument that
produced it, and two of mine were wrong. Every earlier "measured"
verdict in this log that depended on resampled inputs or area-
normalised edge counts deserves the same re-examination.

HYPOTHESIS FALSIFIED AND KEPT ANYWAY, LABELLED (a94). The per-cell tear
was moved from 1.0*sCone to sqrt(2)*sCone because a mesh triangle's
extent is (1,1) texels and the fill produces surfaces AT sCone by
design, so the tighter threshold tears the fill's own legitimate
output. This was predicted to explain the plate-tear drift; it did not
(30.3% -> 30.0%, count moved 2%). The geometric argument stands
independently and the change is strictly more conservative, so it is
kept and labelled rather than presented as a fix.

OPEN: fold and plate-torn per unit width remain at 24% / 30% drift with
no surviving explanation. Tested and eliminated: seed threshold (a92/
a95), cell extent (a94), window floors (a93, which fixed the mask), the
derived tear (a91, invariant). The remaining candidates are the plug
construction (which overwrites the plate inside the SD region) and the
8-bit dequantiser, whose run lengths are inherently resolution-
dependent. Named, not attributed.

## Addendum 103 (2026-07-24): PLUG PATH AUDIT — an 8-bit round-trip inside the SD region

Audit of the plug (the plate everywhere INSIDE the SD region — the part
the failing metrics were measuring and the only major fill stage never
examined dimensionally).

FINDING 1 (LANDED, a96): the default plug encoded depth as Uint8 for
bgPullPushFill and read it back as /255. The quantisation step 1/255 =
0.00392 compared against the entire per-texel depth budget (sCone, the
largest non-folding step):
     pw  600  sCone 0.00800   one level = 0.49x the fold limit
     pw 1200  sCone 0.00400   one level = 0.98x
     pw 1920  sCone 0.00250   one level = 1.57x  -> terraces fold
     pw 3000  sCone 0.00160   one level = 2.45x  -> terraces fold
The plug therefore arrived as a staircase whose terrace edges sit AT or
BEYOND folding, and the ratio grows with resolution — a resolution-
dependent artefact generator inside the exact region SD is asked to
repair, on the two largest shipped assets. The pyramid was Float32
throughout; only the caller's encoding and the final write quantised.
Fixed with a float output path (colour callers untouched).
MEASURED, plate tear as an AREA fraction (its true population):
     before  4.91% (1200) vs 6.88% (600)  = 28.6% drift  FAIL
     after   5.13% (1200) vs 5.11% (600)  =  0.4% drift  PASS

FINDING 2 (opt-in path, NOT fixed): the _plugGroundUp branch smooths
with SPASS = 24 fixed passes of a 3-tap average. Iterations ARE reach:
sigma = sqrt(2N/3) = 4 texels at any resolution, i.e. 0.33% of frame at
1200 px but 0.67% at 600 — the same window covering different physical
spans, the a93 disease in an opt-in branch. The invariant form is
N = 1.5 * sigma^2 with sigma a fixed fraction of frame; at the 0.33%
fraction the other windows already use, that reproduces N=24 at 1200
exactly, giving 6 at 600 and 150 at 3000. Not landed: the branch is
opt-in and untested here, and landing an unverified change in it would
repeat the mistake this audit exists to stop.

FINDING 3 (same branch): the ground-recession median gs is taken over
gradients filtered by `dd < fgTearStep`, a per-texel threshold. At half
resolution per-texel steps double, so a different population enters the
median and the ramp rate shifts. Same fix family as a91; same reason not
landed.

METRIC CORRECTION (third instrument fix this round): plate tear is an
AREA population, not an edge one — it counts terraces across the whole
plug region, not cells along a silhouette. Normalising it per unit width
(Addendum 102's rule for fold and FG tear) was wrong for this metric and
reported 50% drift where the correct area normalisation shows 0.4%.
Each metric must be classified by ITS OWN population, not by a blanket
rule.

WHY fold DID NOT MOVE: the fold metric reads window._qbDbg.plate, which
is plateQ — the FILL field, before the plug overwrite. It never saw the
plug, so a96 could not have changed it, and its 24% drift belongs to the
flood/cone fill, not the plug. The remaining suspect there is a86's
dequantiser, whose run lengths are inherently resolution-dependent.

STATE: mask 0.6% PASS, FG torn 0.4% PASS, plate tear 0.4% PASS, fold
24% FAIL (one open metric, cause narrowed to the fill's dequantiser).

## Addendum 104 (2026-07-24): the dequantiser was innocent — the tie-break window was the drift

Task was "fix the dequantiser drift". The dequantiser turned out not to
be the cause, and saying so cost two measurements rather than a fix.

EXONERATION. Disabled a86 at both resolutions on the analytic scene:
fold drift 24.1% with it ON, 26.2% with it OFF. Not the cause, and
mildly beneficial (fewer folds at 1200: 4.45 vs 4.54). Hypothesis
dropped.

SECOND HYPOTHESIS ALSO FALSIFIED. If the fold metric were merely
counting cells sitting exactly at the k*g = 1 boundary — plausible,
since cone-filled cells sit at 0.99 by construction — the drift would
collapse as the severity threshold rises. It does not: 24.1% / 29.4% /
25.9% / 15.1% at k*g >= 1.0 / 1.1 / 1.5 / 2.0. These are real folds.

ACTUAL CAUSE (a97). QUANT, the value-competition tie window, was
tearStep/32 — a fixed DEPTH compared against candidates that differ by
CONE STEPS, and the cone step scales with resolution. The window was
worth 0.23 / 0.47 / 0.75 / 1.17 cone steps at pw 600 / 1200 / 1920 /
3000. At 3000 px, candidates more than a WHOLE legitimate increment
apart were still treated as tied and resolved by distance instead of
value. Which anchor won a pixel therefore depended on source
resolution, and with it the fill's crease skeleton — and creases are
precisely the fold population: a crease between two opposing cone
claims steps by up to 2*sCone, i.e. k*step ~ 2, a guaranteed fold.

FIX: QUANT = sCone/4, a quarter of the smallest legitimate increment
the fill can make. MEASURED: fold drift 24.1% -> 16.1% (k*g>=1),
29.4% -> 19.8% (>=1.1), 25.9% -> 21.5% (>=1.5), 15.1% -> 15.4%
(>=2.0). Improved, still above the 15% tolerance. Landed as progress
with the residual stated — not claimed as a pass.

NOTE ON MY OWN a89. QUANT = tearStep/32 was introduced by me, in the
addendum that claimed to fix the units of the tie-break. It replaced an
8-bit assumption with a cliff-scale assumption and I called it derived.
It was neither wrong-for-the-old-reason nor right — the correct
reference was the cone step all along, and one addendum of self-audit
did not catch it. That is the third of my own constants to fail
re-examination (a85 metric, a86 bit depth, a89 tie-break).

SCOREBOARD (analytic scene, 1200 vs 600):
    mask (area)        0.6%  PASS
    plate tear (area)  0.2%  PASS
    FG torn (per width) 0.4% PASS
    fold (per width)   16.1% FAIL (was 24.1%)

## Addendum 105 (2026-07-24): fold drift localised — the fill is invariant, the 8-bit INPUT is not

Task was "get fold under tolerance". It is not under tolerance, and the
reason is now measured rather than suspected, which changes what the
remedy is.

TWO MORE HYPOTHESES KILLED. (a) The ground barrier's luma test is a
per-texel colour difference — same mixed unit as the depth tests.
Normalised by texel scale (a98): fold drift 16.1% -> 16.6%, no better.
Reverted. (b) The smear snap reshapes source cliffs, so it could be
reshaping them differently per resolution. Disabled at both: results
BIT-IDENTICAL — it never fires on analytic depth (no smear to snap).

THE DIAGNOSTIC THAT SETTLED IT (harness/metric8.js). Classify every
folded plate cell by where it comes from:
    population              pw1200   pw600   drift
    fill creases             3.675   3.205   12.8%   <- 90% of all folds
    inherited from source    0.391   0.205   47.5%
    fill-vs-surface step     0.000   0.000      -
    total                    4.066   3.410   16.1%
The FILL — the thing all this work has been aimed at — is INSIDE
tolerance. The 16.1% headline is a small, badly-behaved population
dragging a well-behaved one.

WHAT THAT POPULATION IS. Cells where the cleaned source depth itself
folds. Measured against the fold limit:
    one 8-bit depth level = 1/255 = 0.00392
      pw  600  limit 0.00808   one level = 0.49x
      pw 1200  limit 0.00404   one level = 0.97x   <- knife edge
      pw 1250  limit 0.00388   one level = 1.01x
      pw 1920  limit 0.00253   one level = 1.55x
      pw 3000  limit 0.00162   one level = 2.43x
Above ~1250 px a SINGLE 8-bit depth level exceeds what one texel can
carry without folding. 8-bit depth is therefore intrinsically
fold-generating at the resolutions this project actually ships. At the
1200 px test width the terrace step is 0.97x the limit — bistable —
which is precisely why that population drifts 47.5%.

CONSEQUENCES.
1. a86 is reframed. Dequantisation is not a banding nicety; it is what
   makes any source above ~1250 px renderable without folds built into
   the input. It should be described that way in the code.
2. The last 1.1 points of fold drift are an INPUT property, not a code
   defect. Holding the source population fixed puts total drift at
   11.8-12.1% — inside tolerance — so the fill would pass today with a
   clean input.
3. Closing it honestly needs FLOAT DEPTH INGEST. The pipeline reads
   depth through a canvas getImageData, which is 8-bit by construction,
   so a89's quantum detection can never see more than 8 bits no matter
   what the file contains. That is the next real piece of work, and it
   is an architecture change (read depth via a float texture path),
   not a constant.

I am not going to force this metric under tolerance by tuning a
threshold or widening the tolerance. The number is honest where it is,
and it now points at a specific architectural fix.

## Addendum 106 (2026-07-24): float depth ingest (a99) — and what it revealed about a86

BUILT. Depth entered through canvas getImageData, 8-bit by construction,
so no file could deliver more than 255 levels regardless of its content.
a99 decodes 16-bit PNG directly — parse chunks, inflate IDAT with
DecompressionStream, reverse the PNG filters, read 16-bit samples as
float. No library. Quantum 1/65535 = 1.5e-5, measured at 0.004x the
per-texel fold limit against 0.97x for 8-bit at the same width: a 250x
headroom improvement. Returns null for 8-bit / interlaced / non-PNG, so
every current asset takes the old path byte-for-byte unchanged.

BUG FOUND WHILE TESTING IT: the decode was fire-and-forget while the
bake is synchronous, so the first bake raced it and silently used the
8-bit path — the decode logged success, the bake never saw the data.
Awaited now. Worth noting as a pattern: an async improvement wired into
a sync pipeline defaults to "no effect, no error".

MEASURED (analytic scene regenerated as TRUE 16-bit, 1200 vs 600):
    population             8-bit ingest       16-bit ingest
    inherited from source   0.39/0.20 47.5%    0.49/0.31 37.3%  improved
    fill creases            3.67/3.21 12.8%    4.13/3.04 26.3%  WORSE
    total                   4.07/3.41 16.1%    4.62/3.35 27.5%  WORSE

The source-inherited population improved as predicted. The TOTAL got
worse, and the reason is the interesting part: with a genuine 16-bit
grid the a86 dequantiser correctly does not run, and the fill's crease
population immediately became more resolution-sensitive. a86 has been
doing TWO jobs — reconstructing the quantisation ramp (documented) and
incidentally SMOOTHING fine relief so the fill's anchor competition is
stable (never documented, never intended). Remove the quantisation and
the fill's true sensitivity to micro-relief is exposed.

So the honest position on "get fold under tolerance": it is not under
tolerance, and the float ingest did not deliver it. What the ingest did
deliver is a correct foundation and a clearer problem statement — the
fill needs its own scale-aware smoothing of the depth field, chosen on
purpose, rather than inheriting one from an 8-bit accident. That is a
design task, not a constant, and it is the next thing to do.

STATE: mask 0.6% PASS, plate tear 0.2% PASS, FG torn 0.4% PASS, fold
16.1% (8-bit path, unchanged for all current assets) / 27.5% (16-bit
path, new capability with a named open issue).
