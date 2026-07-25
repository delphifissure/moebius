# Handoff brief — read this before your next change to moebius

You have been iterating on the disocclusion pipeline for 116 addenda. Your
measurement discipline is genuinely good and should not change. The problem is
that it is being applied **downstream of an unexamined parameter**, so each fix
is correct, lands, verifies — and the image does not improve. Your own Addendum
116 says it: *"A large slice of this arc changed no rendered pixel."*

Everything below is derived from numbers already in `REVIEW.md`, so none of it
requires you to trust an outside claim. Where I cite literature I say so.

Do not start work until you have read §1 and §2. They change what every later
measurement is taken against.

---

## 1. One parameter is generating the whole defect stream

`k` = the screen displacement, in source texels, between the near and far ends
of the depth range, at the rim of the supported view cone. **You already compute
it**: `max(|m0|,|m1|)` from `bgShiftLUTFor(pw,ph)` (`REVIEW.md`:6270). Addendum
110 already measured it:

```
source            k        fold limit √2/k    in 8-bit levels
851 x 1023       775          0.00182              0.47
1920 x 1080      818          0.00173              0.44
2047 x 1200      909          0.00156              0.40
3000 x 1688     1279          0.00111              0.28          (all at the 45° cone)
```

At 851 px wide, a surface spanning the depth range sweeps **775 px — 91% of the
image width — across the cone.** And `k(θ) = k(45°)·tan θ`, so at the current
60° half-angle it is **1342 px, 1.58× the image width.**

### Eight "separate" open threads are one inequality

| open thread | the inequality | source |
|---|---|---|
| 8-bit depth unusable | `q·k ≥ √2` | A110, `:5746` |
| fold test drops 40% of the mesh | `Δδ·k ≥ √2` | a117 / A116 |
| "tears must pay for themselves" | `Δδ·k ≥ 2` | A47 item 2 |
| **v2 ghosting / banding** | MPI needs `N_planes ≳ k`. **20 planes vs k=775 → a 39 px parallax step per plane** | A116 |
| band always too narrow (D2, D3) | extent `= Δδ·k` → **388 px** for a 0.5 step; the cap was 28 | D2, D3 |
| a113 margin blow-up, 0.87 → 7.8 Mtexel | same | A115 |
| backstop sweep, 60 s = 65% of the v1 bake | policing a plate whose extent is set by `k` | A116 |
| hidden-depth precision required | `1/k` px — at k=775, **one 8-bit level of hidden-depth error = 3 px of misplacement** | derived |

**Consequence that retires a line of inquiry:** 20 flat MPI planes need
`k ≲ 20`, i.e. a 1.5° cone. Flat planes at 20 bins were never going to work at
any usable cone. **v2's ghosting is not a binning problem and no binning
decision fixes it** — it needs the depth-displaced layers you already designed
in Addendum 3.

---

## 2. The cone

### 2.1 It is a budget, not a render

`bgViewFadeEndDeg` sets `ex = D·tan(bgViewFadeEndDeg)` — the excursion the
geometry is *budgeted* for. The shift applied at a live head angle θ is
`−D·tan(θ)·z/(D−z)`. **`bgViewFadeEndDeg` does not appear in it.** At any pose
inside the cone the image is byte-identical whether the cone is 45° or 60°.

So there is **no depth-impression trade here.** Depth impression in a
head-coupled display comes from parallax *gain* per unit head motion. The knob
that would flatten the image is depth relief, and nobody is proposing you touch
it. Cone is free; relief is not.

### 2.2 a109's premise is contradicted by A33's own table

a109 widened the cone to 120° because *"~120 degrees is becoming the horizontal
FOV of front-facing cameras"* (`:6141`). A33's per-device LUT says:

| device | camera FOV H×V | head trackable to | fade fires from |
|---|---|---|---|
| **mac** | 54 × 32 | **±27° / ±16°** | **±17° / ±6°** |
| iphone | 65 × 50 | ±32.5° / ±25° | ±22.5° / ±15° |
| ipad / Center Stage | 105 × 80 | ±52.5° / ±40° | ±42.5° / ±30° |
| generic | 60 × 40 | ±30° / ±20° | ±20° / ±10° |

No device in your own table reaches 120°. On a Mac the geometry is budgeted for
poses the tracker cannot see, by **2.2× horizontally and 3.75× vertically** —
and vertical is where D4 measured the worst behaviour.

**The cost arrived three addenda later and was not attributed back.** a109
honestly predicted its bill (reach ×1.73, fold limit tightened by the same
factor, one 8-bit level going from 2.2–3.5× to 3.7–6.1× the fold limit), then
measured the *mask*, found it barely moved, and shipped. Then a117 found the
fold tear dropping **692,469 of 1,737,400 triangles (40%)** and shipping the
debris as a 1 px comb — the user's *"banded to oblivion"*.

**And A32 named this regime by name:**

> *"The declared envelope (A29) is a 45-degree cone with fade from 35; within
> it, flat planes with world-sized skirts are measurably hole-free. An
> equirect/dome projection buys curvature only useful past ~60 degrees… **If the
> envelope ever widens toward the 'gyro past face-cam FOV' regime, revisit.**"*

The envelope widened to exactly 60° and the revisit did not happen.

### 2.3 The gyro correction — the webcam is not the only pose source

On phone and tablet the **gyro** takes over exactly where the camera loses the
face, and device tilt genuinely reaches 45–60°+. So narrowing is free only up to
the reachable limit of the **pose source** — ±27° on a Mac webcam, much more on
a handheld gyro, where an earlier fade would be a real regression. a109's intent
was not baseless.

But the gyro contract is **softer** than the webcam one, which changes what
exactness is worth buying:

- Gyro measures **orientation, not position** — the eye's location is *assumed*.
  The webcam *measures* the head.
- Real tilts swing through a wrist or elbow arc, so they translate as well as
  rotate; the error grows with φ.
- People counter-rotate their heads when tilting a device.
- Integration drifts and needs re-zeroing, so "head-on" itself wanders.

At large gyro angles you are producing **a plausible parallax effect, not a
reconstruction of a specific eye's view.** Pixel-exact geometry there buys
precision the pose estimate cannot use.

### 2.4 The fix: split the budget from the fade, and degrade instead of cliff

One parameter is doing two jobs, which forces a false choice — build for 60° and
pay the a117 bill everywhere, or fade at 27° and kill the gesture on mobile.

```
bgViewBudgetDeg      // sizes ex, completion extent, plate margin, layer count
bgViewFadeStartDeg   // overlay begins to dim
bgViewFadeEndDeg     // black
     with   budget ≤ fadeStart ≤ fadeEnd
```

Then define the band between them — today undefined, which is exactly why
leaving the budget produces black holes and combs instead of a soft landing:

| zone | contract |
|---|---|
| θ ≤ budget | full completion, pixel-honest, all gates apply |
| **budget < θ ≤ fadeStart** | **graceful degradation** — the uncovered fraction crossfades toward the layer's backdrop plane and the wash widens. Never black, never comb |
| fadeStart < θ ≤ fadeEnd | brightness fade, as today |
| θ > fadeEnd | black |

**You do not need the geometry exact at 60°. You need it to fail gracefully at
60°.** Today it fails by tearing 40% of the mesh and showing the debris. A
degradation ladder gives the gyro its full reach at a fraction of the geometric
cost, and is far cheaper to build than a 60°-exact plate.

### 2.5 Budget profiles

k figures for a 1920-wide landscape asset, from A110's `k(45°) = 818`.
Per-device budgeting is **free**: the bake already runs client-side per session
(v2 at 11.7 s), so desktop never pays mobile's bill. If a server-side or cached
bake is ever introduced, that changes and should be measured separately.

| profile | pose sources | budget (fade-start) | fade | k @1920 | vs today |
|---|---|---|---|---|---|
| **desktop** | webcam only | **17–27°**, per axis | 27–35° | 250–417 | 3.4–5.7× cheaper |
| **mobile** | webcam + gyro | **35–45°**, symmetric | 50–65° | 573–818 | 1.7–2.5× cheaper |
| inspection (drag) | — | *not a budget source* — show the fade | — | — | — |
| turntable demo | — | *not a budget source* — **clamp the slider to the budget** (A115 found the dependency running the wrong way) | — | — | — |
| export / cinematic | — | any angle — generative path, own thresholds, no pixel-fidelity contract | — | — | — |

Axis asymmetry is a property of the **pose source**, not the device: the
webcam's vertical range is far smaller than horizontal (mac 32° vs 54°), while
tilt is roughly symmetric.

**Two things the gyro correction does not touch.** The budget is still sized at
fade *end* — the pose where the canvas is already black — when the fade band
exists precisely so the rim need not be right. And a wide render cone still does
nothing for **untracked** viewers on a shared panel: one image is on screen, and
a bystander sees the tracked viewer's pre-distortion foreshortened by their own
angle. That is an argument for the simulated viewer (§5), not for a wide budget.

---

## 3. Stop-list

Freeze behind a flag, measure the delta, then delete. Every item is justified by
a measurement already in `REVIEW.md`. Deleting these is not a loss of work — the
measurements stay in the record; the code they justify is what goes.

| stop | why |
|---|---|
| **v1 bake, entirely** | Most expensive and worst-looking of three modes. **92.7 s vs v2's 11.7 s**; v2 is 0.00% black at all four of the user's poses and the only render that still reads as the painting. (A116) |
| **the backstop sweep** | **60.4 s = 65% of the v1 bake**, policing an invariant the ordering clamp (§4.4) enforces for free. |
| **the all-viewpoint / SD scan** | Pruned **0 px in all six quick bakes**, at ~2.75 s of a ~10 s bake. |
| **further precision on the tear criterion** | a101 exact vs a102 slope: **692,469 vs 692,246 triangles — 0.03%**, identical black, identical comb to 3 s.f. The envelope stays the right law for the extension margin and the SD scan; it was precision applied to the wrong quantity here. |
| **the fold-mode tear** | Cliff-only wins on every axis at once: **86× fewer dropped triangles, 51× fewer cap cards, comb energy 27–29% lower**, for +0.1–0.4 points of black. |
| **new screen-space heuristics of any kind** | Band / rind / cut / dilate / bleed / disarm is the 2005–2016 DIBR literature's known dead end — that field concluded target-view hole filling has a hard ceiling and moved to filling in the *source* view. `REVIEW.md` §4 reached the same verdict independently: *"The heuristic stack is the architecture telling you the geometry is wrong."* |
| **renderer-side repair of depth-estimator errors** | Stroke repair, adopt-map, footing rule, wire rule, ink-follows-layer. Estimator errors are unbounded across assets, so renderer-side repair cannot terminate. Fix at the depth stage or accept and document the ceiling, as A44 correctly does. |
| **any new tuned constant** | See §6. The constant count should be going *down*; A96/A97/A101 did that work — keep the ratchet. |

---

## 4. Do-list, in order

Each step is independently shippable and measurable with the existing harness.
**Do not start step N+1 until step N's number is recorded.**

### 4.1 Revert the cone to 35 / 45
Zero risk, 1.73× off `k`, and it is the last envelope **measured hole-free on
all assets** — A30: zero holes at nine poses across the 35° cone; A32: full 45°
12-pose scan, SW 0 hole px, frazetta 74k → 10–42 px (0.01% of a frame). It also
sits inside the mobile budget range, so it is not a regression for the gyro
gesture. Do this **before** taking any baseline.
**Pass:** regression suite still green, baseline re-pinned.

### 4.2 Print `k`
One line: log `bgShiftLUTFor(pw,ph)` per asset next to the fold limit and the
tear threshold. Cheapest, highest-value action available — everything in §1
becomes checkable the same afternoon.
**Pass:** the number appears in the bake log.

### 4.3 Build the simulated-viewer mode, then re-triage the open defect list through it
§5. A meaningful fraction of the current list is **raw pre-distortion being read
as breakage**. Re-triaging before fixing anything else is probably the cheapest
move available right now.
**Pass:** anchor pixel-stationary under ±40° scrub; the open list re-scored.

### 4.4 Add the ordering clamp
```
d_hidden(x) ≥ d_occluder_silhouette(x) + ε
```
One pass after the plug/plate depth solve. Unconditional, cannot regress
correctness. Then flag off and measure: the backstop sweep, the protrusion hunts
(A21, A41, A43, A112), the cap cards, and the 0.004-unit offset all exist to
find or paper over violations this forbids at bake time. *Searching rendered
poses for violations of an invariant is strictly worse than enforcing the
invariant.*
**Pass:** black% unchanged at rest and off-axis; bake down by the sweep's 60 s;
protrusion probes clean with the sweep off.

### 4.5 Split budget from fade; add the degradation band
§2.4. Then log real head poses **and gyro angles** at ~5 Hz during ordinary use
and set the desktop and mobile budgets from the data, at fade-start, per axis on
the webcam path.
**Pass:** a pose distribution with 50/95/99th percentiles, and a budget with a
citation instead of an argument.

### 4.6 One law, one implementation
Route tear, fold, band width, completion extent and plane placement through a
single `revealPx(Δδ) = Δδ·k`. a104 retired three private copies of the parallax
law; a113 found a fourth.
**Pass:** grep finds one implementation.

### 4.7 Fix the depth fill's operator
§7. Second-order solve replacing the first-order smoothing in the *depth* fill.
This is A63b's intent with the correct operator.
**Pass:** the §8 hold-out test improves; the ground ramp's fill no longer flattens.

### 4.8 Introduce ownership
§7. Classical and free to start: T-junction + convexity ordering over the
ink/edge maps you already compute.
**Pass:** the class-B hold-out test improves; the doppelgänger shots stop
reproducing.

### 4.9 Then layering and detail
Per-layer depth displacement to replace flat binning — kills v2's ghosting and
the ground-ramp banding together. Soft/fractional alpha at layer boundaries —
kills thin-lift, ribbons, staff taffy, filaments and confetti, which are **one
defect, not five**. Generative detail pass last, when the geometry no longer
needs it to hide anything.

---

## 5. Review of the simulated-viewer preview spec

**Verdict: build it, and build it early — it is the instrument the cone decision
needs.**

The core insight is correct and under-appreciated: an off-axis frustum
*pre-distorts* the image so a physically off-axis viewer's foreshortening
cancels it. **A tester scrubbing a virtual eye while sitting head-on to their
monitor is looking at raw pre-distortion, and it will look catastrophically
wrong while being entirely correct.**

This is very likely already contaminating the review loop. A114 records the user
reporting the render "looking broken from almost any angle", and the response
that four of five grids were outside the supported cone — *"which I said, and
which was true and beside the point."* This mode explains why it was beside the
point.

### Right, and not to be negotiated

- **Real 3D quad, not a 2D quad with displaced corners.** Per-triangle
  interpolation is affine and creases along the diagonal; the 3D quad gets
  perspective-correct interpolation free.
- **Fixed FOV, never autoscaled** — "the shrink is the signal". Autoscaling
  would hide the solid-angle collapse, which *is* the measurement.
- **1.75× supersampled pass 1**, specifically so the double resample cannot hide
  the fragment stretch the stretch net exists to catch.
- **Linear-space falloff multiply**; in sRGB the dimming would be visibly wrong.
- **Not gated on the fade cone.** Right for an instrument.
- **PiP A/B via `setViewport`/`setScissor`**, not a second canvas. Both views
  genuinely are needed.
- **The acceptance test's last clause** — *"report it rather than tuning the
  overlay to hide it"* — keep verbatim.

### Amendments

**A1 — Assert the shared frame convention before trusting the acceptance test.
(Load-bearing.)** The test is meaningful only if pass 1 and pass 2 use the same
`E` *and* the same panel rect. If pass 1 carries any residual "view-Z push" from
before a60's reprojection, or its portal rect is not exactly the W×H plane at
z=0, the anchor will swim for a **frame-convention reason, not a frustum bug**,
and the instrument emits a confident false positive — the A113/A115 failure mode
exactly. Log both projections; the test does not run until they agree.

**A2 — Prove the instrument can see a break.** Perturb the off-axis frustum by a
known amount and confirm the anchor swims by the predicted pixel count. An
instrument that has never detected a fault has not been shown to work.

**A3 — Scrub on a sphere, not a line.** The spec parameterises `E` but not how
the scrub maps to it. A lateral slide changes θ and `|E|` together and makes the
HUD's θ ambiguous. Scrub at constant `|E| = D_REF`, with a separate dolly.

**A4 — Put `k` on the HUD.** Highest-value addition; it turns the mode into the
cone-decision tool:
```
theta            27.0 deg
k needed here    395 px     (parallax across depth range at this pose)
k budgeted       1342 px    (bgViewBudgetDeg = 60)
completion used  30%
Omega            41% of head-on
subtense         18.3 x 11.6 deg
```

**A5 — Label the falloff "geometric", not "display".** `a = E.z/r³·refD²` is
Lambertian irradiance from a diffuse patch — correct as a geometric bound, but
real LCDs fall off faster off-axis than cos θ and OLED differs again, so the mode
will **understate** how bad 60° looks. Also make explicit that `uRefD` and
`D_REF` are the same constant, and decide whether it tracks `|E|` under dolly.

**A6 — The up-vector guard will snap.** `abs(dot(normalize(E), up)) > 0.999` is
a 2.6° window; crossing it flips the roll discontinuously. Blend over a wider
band, or derive up by projecting the panel's +y into the view plane.

**A7 — Log the supersample cap.** 1.75× linear is 3.06× the pixels. Capping is
fine; **capping silently is not** — that is the `Math.min(mx, pw)` lesson from
A115.

**A8 — Add the head-pose recorder to the same feature.** The simulated viewer
answers *"what does an off-axis viewer see?"*; the recorder answers *"does
anyone ever go there?"*. Log webcam **and gyro** angles; overlay the 95th/99th
percentile contours on the HUD. Together they close the cone question in one
screenshot.

### Scope caveat

The pixel-stationary-anchor acceptance test is a **webcam-path test**. Its
premise is that physical foreshortening exactly cancels the baked
pre-distortion, which requires the assumed eye to be the real eye. On the gyro
path the eye position is inferred, so there is no ground-truth anchor to be
stationary against — there the mode shows a plausible viewer, not a specific one.

### Expect this

When the mode is first switched on, a meaningful fraction of the artifacts
currently on the open list will look **much less severe** than in the raw scrub,
because the physical keystone puts the stretched geometry back where it belongs.
Some will look worse. Both are information.

---

## 6. Process rules

These exist because each failure mode below is in the record, several times, and
they cost more than any single bug.

1. **No change without a rendered-pixel delta.** If a change moves no pixel at
   the user's poses, it does not ship, however correct it is. a101/a102 is the
   worked example.
2. **Verify the instrument before believing a null.** Three confident nulls in
   Addenda 113–115 were instrument failures: a stale server, a probe pointed at
   a branch that returns before the code under test, and a watcher deleting the
   bake it was measuring. **Every A/B must first demonstrate it can detect a
   deliberately broken arm.**
3. **Measure what the user sees.** A47's lesson (760 px probe vs the user's
   canvas) and a117's (black% is blind to an alternating light/dark comb). Pick
   the metric from the artifact, not from convenience, and state what the metric
   cannot see.
4. **No new constant without** (a) a derivation with units, (b) a test that
   fails if it is wrong, and (c) a name that says what it means physically.
5. **One law, one implementation.** Four private copies of the parallax law were
   found across A104 and A113. Any duplicated law will drift.
6. **Bound the scope of estimator repair.** Fix at the depth stage or document
   the ceiling. Renderer-side repair cannot terminate.
7. **When two modes both work, delete one.** Three bake modes were maintained
   for months; A116 priced them and one dominates on both cost and quality.
8. **No silent caps.** If a bound truncates coverage — top-N, sampling, a clamp —
   log what was dropped. Silent truncation reads as "covered everything" when it
   did not.

---

## 7. Hidden depth: three problems, not one

### 7.1 The taxonomy

| class | who owns the hidden pixels | correct hidden depth | classical? |
|---|---|---|---|
| **A. inter-object disocclusion** | the background surface | continuation of background, monotonically behind the occluder | **yes, well** |
| **B. self-occlusion** (arm over torso, cloak fold, staff across body) | **the same object** | just behind the occluding part — **not** background depth | no — needs amodal reasoning |
| **C. contact / support** | shared | the two surfaces must be *tied*, not independently extrapolated | yes, once contact is detected |

Filling a class-B hole with a background rule punches a hole through the figure
that fills with sky. That is the doppelgänger, wash-doppelganger, "seated figures
must STAND", rise-debt and troll-arm families. **The monotone constraint is still
satisfied** — the torso really is behind the arm — so no depth-domain check
catches it. It is an **ownership** error wearing a depth costume. A47 already
named it correctly as the overlap class.

### 7.2 The precision budget is `1/k`

An error ε in inpainted depth misplaces that content by `ε·k` px at the rim.

| k | precision for ≤1 px | in 8-bit levels |
|---|---|---|
| 1342 (current, 851 px) | 0.00075 | **0.19 — unrepresentable** |
| 775 (45°) | 0.0013 | **0.33 — unrepresentable** |
| 237 (Mac fade-start) | 0.0042 | 1.1 |
| 60 | 0.017 | 4.3 |

At the current cone **even a perfect depth inpainter cannot be represented.**
Land the cone before investing in a better fill.

### 7.3 First-order smoothness is the wrong prior, and it is what most fills use

Harmonic / Laplace / homogeneous diffusion minimises `∫|∇d|²` and is biased
toward **fronto-parallel plateaus** — the harmonic extension of a slanted
boundary flattens toward the boundary mean. **Telea and Navier–Stokes, the two
in OpenCV, are in this class and are the wrong tool for depth.** Pull–push is
first-order in effect too.

A second-order (biharmonic / thin-plate) prior continues the *gradient*, so a
slanted ground extends as slanted ground. Herrera & Kannala, *Depth Map
Inpainting under a Second-Order Smoothness Prior*, state the goal exactly:
*"encourages flat surfaces without favouring fronto-parallel planes."*

Recommended concrete form — same solver shape as the existing Jacobi sweeps,
multigrid on the pyramid already built (A3 already identified this as a 10–20×
win):

```
Solve   ∇²d = ∇·g            inside the hole Ω
with    d = d_bg              on the BACKGROUND boundary   (Dirichlet)
        ∂d/∂n free            on the FOREGROUND boundary   (Neumann)
where   g = the background rim's depth gradient, extended into Ω
```

Sources only from the background side by construction — no rind-exclusion
heuristic needed. Simplest `g` that works: fit a local plane to the background
rim in a small window, extend its gradient into the hole constant along the
direction away from the occluder.

**For class B, run the same solve with the owning surface's rim as the Dirichlet
boundary instead of the background's**, still clamped behind the occluder. The
reconstructed geometry is objectively wrong — a real torso is not a smooth
continuation of its own silhouette — and it does not matter, because the error
costs `ε·k` px and both terms are small. Hidden depth only needs three
properties: **ownership**, **ordering**, **smoothness**. None requires knowing
the true amodal shape.

**Do not:** run a colour inpainter on depth (depth has structure, not texture);
smooth the depth to avoid holes (that is Fehn 2004 and a86 — `:5788` measured the
trade going the *wrong* way on 2 of 4 assets); derive hidden depth from the
colour pull–push pyramid; or fill across an occluder (Neumann, not Dirichlet, on
the foreground boundary).

### 7.4 Ownership comes first, and the classical signal is better on art than on photos

You cannot fill hidden depth until you know which visible surface the hidden
pixels belong to. **T-junctions** — where a contour terminates against another,
the continuing contour is in front — build a global depth order on their own
(Palou & Salembier, *Monocular Depth Ordering Using T-Junctions and Convexity*).

A photograph's T-junctions are noisy and often ambiguous. A painter or inker
**draws** the occlusion deliberately, with a stroke that terminates at the
occluding edge. **The ink that has been fighting the depth estimator for fifteen
addenda is a hand-authored occlusion-order annotation.** That is the rigorous
form of A56's "the ink was the segmentation all along".

### 7.5 Two models worth evaluating on the four assets

- **Illustrator's Depth** (Maruani et al., Nov 2025, arXiv 2511.17454) predicts a
  discrete **layer index** per pixel — globally consistent ordering,
  piecewise-flat, trained on layered vector graphics, explicitly built to handle
  flat elements with no real depth (shadows, textures, drawn marks), stated to
  apply to illustrations and paintings. Continuous monocular depth asks a
  painting a question it does not answer ("how far is this brushstroke?"); layer
  index asks the one it was authored to answer. *Verify licence.*
- **Amodal Depth Anything** (ICCV 2025, `github.com/zhyever/Amodal-Depth-Anything`)
  takes image + amodal mask and returns relative depth of the occluded portion.
  Repo is MIT — **but its Depth-Anything-V2 Base/Large backbone is CC-BY-NC.**
  The method is unencumbered; that checkpoint is not. Rebuild on an Apache
  backbone if used commercially.

### 7.6 A documented trap

"Inpaint the colour, re-run the depth estimator, scale-shift align." Every
text-to-3D-scene pipeline tried it (Text2Room, LucidDreamer, WonderJourney).
Monocular estimators are affine-invariant *globally*, not locally, so one
scale+shift cannot make the new prediction agree at the seam; the literature
reports "depth discontinuities within the inpainted regions" and "broken
structure and misalignment near complex boundaries". Text2Room reached for a
dedicated depth-*inpainting* model (IronDepth) instead; *Invisible Stitch*
(3DV 2025) is a whole paper arguing inpainting should replace estimate-then-align.
Usable as a coarse prior into the solve; never as the final field, never with a
global alignment.

---

## 8. How this arc terminates

The arc has had no stopping condition. Here is one. Every test runs on the
existing harness.

| gate | condition | where it stands |
|---|---|---|
| **1 · rest fidelity** | at zero offset, 0 px differ by >8/255 from the bare-source reference | ~17,637 px on Starwatcher (D1) |
| **2 · cone honesty** | at the *declared* rim: black ≤ 0.1%, comb energy no worse than the no-tear baseline | v2 already 0.00% black at the user's four poses; the comb is the open half |
| **3 · hidden depth** | ≤ 1 px of misplacement at the rim, in all three classes | **no number exists yet** — the test below creates one |
| **4 · cost** | bake ≤ 10 s at 1920 px | v2 at 11.7 s with the sweeps still in it |
| **5 · complexity, monotone** | constant count, config flags and composite-shader lines all lower than the previous release | a change that raises any needs justification in the addendum |

### Gate 3 — the hold-out occlusion test (build this)

Take a region of an asset that is **not** occluded. Composite over it a mask
shaped like a real occluder from the same asset. Run the full ownership +
completion pipeline. Compare the completed depth to the depth that was actually
there.

Report **RMSE in pixels of misplacement at the cone rim** (`ε·k`), not in depth
units — that makes it directly comparable to the fold limit and the tear
threshold. Run it three times with three mask classes: background-adjacent
(class A), self-occluding (class B), contact-adjacent (class C). **For the first
time this separates the three failure modes numerically instead of by eye.**

This is exactly how the ADIW dataset was built and how SLIDE trains its
inpainter — synthetic occlusion of known content is the standard way to get
ground truth here. It needs a harness script and no new data.

**Also add cross-pose consistency:** content revealed at pose A and at pose B
must land on the same *source* texels. Two renders and a reprojection; it catches
rate errors no single-frame comparison can.

**When gates 1–5 pass simultaneously on all four assets, stop.**

---

## 9. Licence-clean stack (verified July 2026 — re-verify at integration; not legal advice)

**Usable**

| component | role | licence |
|---|---|---|
| classical solvers (Poisson/biharmonic fill, T-junction ordering) | fill + ownership | none — classical, training-free, style-agnostic |
| **MoGe / MoGe-2** | point map + depth + normals + **FOV** (~60 ms) | **MIT** |
| **Depth Anything 3** — Small / Base / Mono-L / Metric-L | depth | **Apache-2.0** |
| **Marigold** | depth, diffusion prior — best on stylised input | **Apache-2.0**, synthetic-only training data |
| **MiDaS 3.1 / DPT** | depth, robust off-domain by construction | **MIT** |
| **SAM 2** | region boundaries, zero-shot to unseen domains | **Apache-2.0** |
| **3D Photo Inpainting** (Shih 2020) | reference implementation — LDI with explicit connectivity | **MIT** |
| **LaMa** | colour inpainting, fast, prompt-free | **Apache-2.0** (Places2 provenance flag) |
| **hustvl/Moebius** (ECCV 2026) | colour inpainting — 0.22 B, ~26 ms/step, prompt-free, matches FLUX.1-Fill-dev | **Apache-2.0** (name collision is a coincidence) |
| **gsplat** | splat rasteriser, if ever wanted | **Apache-2.0** |

**Excluded**

Depth Anything V2 Base/Large/Giant and DA3 Large/Giant (CC-BY-NC-4.0) · Depth Pro
(Apple personal-use, no commercial grant) · 3D Ken Burns (CC BY-NC-SA) · Tiled MPI
(CC-BY-NC) · AdaMPI (non-commercial) · FLUX.1 Fill [dev] (non-commercial) · the
original Inria 3DGS rasteriser (non-commercial — use gsplat).

**On "any image — photo, painting, comic".** Learned inpainters carry a style
prior; patch-based ones carry none. Everything trained on Places2/LAION puts
photographic local statistics into a painting — continuous tone where there
should be flat colour, no line weight, wrong grain. Exemplar synthesis copies
from the same image, so halftone stays halftone and impasto stays impasto, for
free, with no training. So: **Tier 1** = background-restricted exemplar synthesis
over a pull–push base (training-free, universal); **Tier 2** = optional offline
permissive model plus a style lock (histogram/palette match against the
surrounding annulus + Poisson seam blend). Patent flag: Adobe's `US8861869B2`
covers PatchMatch's randomised search to 2030; Criminisi's term has expired, and
resynthesizer / OpenCV `xphoto` are alternatives.

---

## 10. Shortest version

1. Revert the cone to 35/45. Zero risk, and it is the last envelope measured
   hole-free. Do it before taking any baseline.
2. Print `k`.
3. Build the simulated-viewer mode and re-triage the open defect list through it.
4. Delete v1, the backstop sweep and the viewpoint scan; measure the delta.
5. Add the ordering clamp.
6. Split budget from fade; add the degradation band; log real head and gyro poses.
7. Second-order depth fill; ownership before filling.
8. Then layering and detail.
9. Gates 1–5, then stop.

Anything currently open that is not on that list is downstream of `k` and will
either disappear or become tractable once it is set.

---

*Fuller workings and citations, if you want them, are in the same branch:*
`RESEARCH-LDI-MPI-DISOCCLUSION.md` (28 years of layered representations,
licence-filtered) · `RESEARCH-DEPTH-DISOCCLUSION.md` (hidden depth in detail) ·
`CONE-DECISION.md` (the cone analysis in full, including the gyro correction) ·
`HANDOFF-DIRECTION.md` (the shorter directive version of this brief).
