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
