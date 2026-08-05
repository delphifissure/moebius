# moebius.js — Roadmap

**State as of:** `v3.13.44-a213e` (moebiusv2/main `de0b303`), 2026-08-05.
**Audience:** any agent joining or resuming this project. This file says where
we ARE, what is SETTLED (do not relitigate without new evidence), what is IN
FLIGHT, and where we are HEADED. The evidence behind every claim here lives in
`REVIEW.md` (Addenda 1–155, same branch) — this file is the map, that one is
the territory.

---

## 1. What this project is

A single-file THREE.js renderer (`moebius.js`, ~21k lines, repo
`delphifissure/moebiusv2`, branch `main`) that turns ONE image + ONE depth map
into a head-tracked 2.5D portal: the screen is a **window into a static
world**, not a fishtank. Face tracking moves the eye; a fixed-rect
off-axis (Kooima) frustum does the projection; parallax reveals content the
source image never had — **disocclusions** — which are filled by a baked
background plate (**"the plug"**). A Stable Diffusion inpaint/outpaint stage
will eventually supply real texture for those reveals; everything current is
the geometry and placeholder-texture layer underneath that.

## 2. Prime rules (from the user; non-negotiable)

1. Generalize to **ANY image with ZERO per-image tuning**.
2. Every "magic number" must be **cited or derived**; "a constant is only safe
   if its units are invariant to the thing you're about to vary."
3. **Trust the depth map.** SD inpainting is a later texture stage.
4. The background is a **PLUG**: it fills disocclusions only. No background
   cloning, no figure clones, "a single perfect plug."
5. **Falsified premises get REMOVED from the code and recorded** (rule 7) —
   never left behind flags.
6. Never widen a failing test range to make it green.
7. When two statistics contradict, **look at the buffer** — stop inferring
   (a196). A/B arms must actually diverge downstream of the flag before
   numbers are read (a134).
8. The **user's screen is the final authority on aesthetic trades**. Smoothness
   /energy metrics cannot price a semantic artifact (phantom figure) against a
   texture artifact (striping) — recorded instrument limitation (Add. 153/154).
9. Deliverables: numbered plain-language summaries + test shots; never
   over-claim. "We want a window more than a fishtank."

## 3. Settled ground (verified; reopening needs new evidence)

- **The projection law (the goodgaps reference):** static world + fixed-rect
  Kooima frustum = correct dolly zoom on-axis AND off-axis, with the
  portal-plane subject pinned exactly for ANY eye. Restored by a208/a209 after
  two historical degradations (a60 live-refEye reprojection, a167 embed).
  refEye is **frozen unconditionally during dolly**. Dolly maps 18–144mm:
  `dist(f) = (terrariumWidth/2)·(f/18)`, rest = 45mm-equivalent. The
  `regress.js` suite dolly checks (subject pin ≤ 1px over the full sweep at
  gain 3.2, world stretch ≥ 8px) ALL PASS. (Add. 147–148.)
- **Immersive/embed mode is OFF by default** (white pillarboxes gone);
  simulated-viewer is the only extra mode. (a209.)
- **The shipped bake is the quick path:** dequantize → directional plate
  (a62) → wash → FG pre-tear (a212 + a213e: fold + scan-touch + **v1 far-side
  gate** `|plateQ[far] − farDepth| ≤ fgTearStep`, so only silhouette walls the
  plate genuinely backs are torn — figure interiors are protected; troll
  rest-delta 0.26% px > 8 luma) → plug takes the torn footprint (a160b) →
  ordering clamps (a135 same-texel, a162 cross-texel closed-form) → slope
  limit (a126) → skirt at the a113 shift envelope (a149).
- **The depth test is the gate; the mask cannot be.** The a58 source-space
  mask gate is falsified and removed (a161/a169); the mask survives only as
  the SD export region.
- **SD regions mark correctly in all modes** (a210): in-frame disocclusions =
  cyan (inpaint), anything outside the source frame = orange (outpaint), with
  a far backdrop plane so outpaint demand is visible.
- **View fade:** radial 35–45° cone + per-axis face-frame band whose edge is
  the learned detection-loss boundary (seeded from the device FOV LUT; Mac
  entry user-measured at 80°×60°). Learner tightens on losses AND recovers on
  healthy detections (a213b) — pure-min learning is falsified (conflates
  occlusion with frame edge).
- **Falsified this arc — do not retry as-is:** a211 (removing the uvRate mask
  gate: staff unchanged −0.1%, ground speckle +30.7%); a213 row-colour fill
  (+93% ghost, 35% of band missed reach → figure clone); a213c nearest-flood
  fill **as default** (ghost dead, but striping — user verdict). The uvRate
  classifier itself (max Jacobian axis) is known blind to 1–2px one-axis
  filaments; fixing taffy via that classifier is a dead end until the
  classifier changes.
- **Known instrument gaps (recorded, unbuilt):** no shader-compile watchdog
  (an undeclared uniform = silent black material — bit us in a189 and a213d);
  debug stamp `mode=` shows the selected, not active, mode; suite letterbox
  lit% measurement (pre-existing deliberate failures).

## 4. The active thread: taffy (stretching artifacts)

Three-round attribution (Add. 150–154) convicted **the wash**: it is one-sided
in depth but **isotropic in direction**, so its pull-push pyramid mixes sky
into the ground half of figure-shaped disocclusion bands — a pale ghost baked
into the plate, read as "taffy." The FG rubber and the live fill are
exonerated (byte-identical toggles). The a212/a213e tear removes the true
rubber walls; the band CONTENT is what remains.

**In flight — a214, the plug-visibility contract (user directive, 2026-08-05):**
"the background plug should ONLY be visible in the disocclusion holes,
nowhere else. It should be transparent in any places where disocclusions
won't happen." Today the plate is a full-frame background copy that merely
relies on the depth test to stay hidden — with the FG hidden it IS a clone
(user's troll sheet), beyond the source frame the a149 skirt paints
clamp-smears, and every scan miss shows stale wash instead of an honest
hole. The fix: gate plate fragments by the **a80 all-viewpoint reveal
union** (u_sdMask — every plate texel some eye in the cone can actually
see) and discard outside the source-frame uv; remove the skirt. NOTE: this
does NOT reopen a161 — a161 falsified gating by the TORN-footprint mask
(wrong texels, source space); the reveal-union mask was never tried as the
render gate and is by construction the set the contract names. Honest cost:
where the a80 scan under-covers, holes become transparent instead of
showing stale plate — visible, debuggable, and preferred by the user.

**Then — a215:** two-sided inverse-distance blend of depth-compatible
rim sources within the depth-gated domain (the a213c BFS domain), replacing
the nearest-source flood texture that striped. Shepard (1968) weighting with
p=1 — for two opposing sources this is exactly linear interpolation across
the band, dimensionless in resolution. Must **earn the default on the user's
screen**; `window._bandFillLegacyWash` restores the wash instantly.

**Next in the arc:** audit whether the a80 all-viewpoint disocclusion scan
covers mid-dune-ridge reveals at the user's actual poses (Add. 154 open
thread) — the scan gate now aims BOTH the tear and the plug's visibility,
so its coverage is load-bearing.

## 5. Near-term queue (ordered)

1. **a214** plug-visibility contract (in flight, above).
2. **a215** two-sided blend fill (queued, above).
3. **a80 scan-coverage audit** at user poses — urgent once a214 lands.
4. **Shader-compile watchdog** — assert material compile status after bake;
   a dead debug material must not report as "everything is black."
5. Debug stamp `mode=` → show ACTIVE mode.
6. Suite letterbox lit% measurement fix (stop the deliberate failures).
7. Backlog (task list numbers): W1 fast test workflow — CPU-warp renderer +
   persistent harness (#84); A85 warrior nested-lip banding (#87); portal
   frustum overlay (#88); A107 fgTearStep invariance sweep — partially
   addressed for the quick tear by a212/a213e, other uses unaudited (#92);
   A114 quick-path scene extension (#94); A116 extension clamp silent cap
   (#95); A117 strip default path to plug depth + pull-push colour (#96).

## 6. Mid-term

- **The SD texture stage** — the reason the plate/wash are placeholders.
  Round trip: `exportSDBundle` (a210 regions: cyan inpaint + orange outpaint)
  → SD generates real texture → import → plate colour replacement. Once SD
  supplies band content, the wash-vs-fill debate dissolves; the geometry
  (tear + plug + ordering clamps) stays authoritative. Import path exists
  from the MPI era; needs re-validation against the current quick plate.
- **Device generalization:** grow the per-device FOV LUT from user
  measurements; keep the learner as the runtime refiner. Goal: any laptop or
  phone camera lands within the fade band without manual numbers.
- **Performance:** bake is ~10–26s; W1 harness makes iteration cheap; mesh
  decimation exists and can extend to the plate.

## 7. Long-term vision (as far as we can see)

- **A window, not a fishtank:** load any image → a parallax portal that
  survives any user pose with honest fades at the limits of what the source
  can know. Zero tuning, every constant derived, every reveal either truly
  backed (plug + SD texture) or honestly faded.
- **Real synthesized reveals:** SD inpaint for in-frame disocclusions and
  outpaint for beyond-frame, baked back as plate texture; possibly iterative
  (bake → SD → re-bake ordering clamps against the new content).
- **Beyond stills:** video input (per-frame depth + temporally stable
  plates), multi-layer revival (the MPI slices shipped and are parked),
  WebXR/mobile heads where the same projection law already holds.
- **Instrumentation maturity:** the regression suite covers every law we've
  proven — projection pin, tear rest-invariance, plug coverage, fade edges,
  shader compile status — so no future arc can silently re-break settled
  ground (the a60/a167 degradations went unnoticed for ~100 versions; the
  suite is how that never happens again).

## 8. Working practices for agents

- Code lands on `moebiusv2/main`; every arc gets a numbered **addendum in
  `REVIEW.md`** on `delphifissure/moebius` branch
  `claude/moebius-disocclusion-review-oa9exr`, committed and pushed.
- **Frames are the evidence; metrics are advisory.** Produce test shots.
- Harness idioms that have bitten before: never `pkill` a pattern matching
  your own shell; the goodgaps-era render loop self-schedules — probes wait
  on rAF, never call `render()`; the real `handleCanvasClick` aborts headless
  (emulate the sweet-spot instead); face-pathway calibration is 2-point
  linear.
- The user's test poses are often 1.2–2.4× outside the 45° cone; in-cone is
  the fair reference for any A/B, but report the user-pose numbers too.
