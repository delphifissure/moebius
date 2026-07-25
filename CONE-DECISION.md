# The cone decision

Answering `HANDOFF-DIRECTION.md` §2. The short version is that this decision is
much smaller than it feels, because **the thing you are afraid of losing is not
attached to the knob you would be turning.**

Everything below comes from `REVIEW.md` itself unless marked otherwise.

---

> **CORRECTION, added after review — read §9 before acting on §6.** The first
> draft of this document under-weighted the **gyro** pose source. On a phone or
> tablet the gyro takes over where the front camera loses the face, and device
> tilt genuinely reaches 45–60°+. a109's intent was therefore not baseless, and
> the claim in item 1 below that narrowing is "free at any pose a viewer can
> reach" is **only true up to the reachable limit of the pose source** — which is
> ~27° on a Mac webcam but much larger on a handheld gyro. §9 restates the
> analysis with the gyro path included and revises §6's recommendation. The
> other four items below are unaffected.

## 0. Short answer

1. **Narrowing the cone does not reduce the sense of depth at any pose inside
   the new cone.** `bgViewFadeEndDeg` is a *budget* parameter — it sizes how
   much geometry and completion get built. It does not appear in the per-frame
   shift. At any head angle θ the rendered image is byte-identical whether the
   cone is 45° or 60°. Narrowing changes only where the fade fires and how much
   you pay. *(Caveat per §9: on a device whose pose source can reach past the
   new cone — i.e. gyro on mobile — narrowing IS visible, as an earlier fade.
   It is free on desktop, not free on mobile.)*
2. **a109's premise does not survive contact with a109's own sibling addendum.**
   The 120° cone was adopted because "~120 degrees is becoming the horizontal
   FOV of front-facing cameras." But A33's own per-device FOV table says
   **mac 54×32, iphone 65×50, ipad/Center-Stage 105×80, generic 60×40**. Not
   one device in the app's own LUT has a 120° horizontal FOV. On a Mac the head
   exits the camera at **±27°**, and the fade already fires from **±17°**.
3. **The last envelope at which this system was measured working is 45°**, and
   A32 explicitly flagged 60° as the boundary where flat planes stop being
   adequate — then a109 moved the envelope to exactly 60° and A32's warning was
   not revisited.
4. **The geometry budget is sized at the fade END — the pose where the screen is
   already black.** It should be sized at fade START. On a Mac that alone is a
   5.7× reduction in `k`.
5. **A wide render cone does nothing for untracked viewers on a shared panel.**
   §5 — this may be the actual confusion behind a109.

**Recommendation: `bgViewFadeEndDeg` ← per-device, from the FOV LUT you already
have, sized at fade-start. Mac → 17°, iPhone → 22°, iPad → 42°, capped at 45°.**
Then measure real head poses (§7) and set it from data rather than argument.

---

## 1. What a109 assumed vs. what the record says

a109's stated reason (`REVIEW.md`:6141):

> *"~120 degrees is becoming the horizontal FOV of front-facing cameras, so that
> is the range over which the head is trackable and the portal has to hold up."*

Three problems, all checkable against the repo:

**(a) The app's own device table contradicts the premise.** Addendum 33 shipped a
per-device front-camera FOV LUT:

| device | camera FOV (H×V) | head trackable to | fade fires from (last 10°) |
|---|---|---|---|
| mac | 54 × 32 | **±27° / ±16°** | **±17° / ±6°** |
| iphone | 65 × 50 | ±32.5° / ±25° | ±22.5° / ±15° |
| ipad / Center Stage | 105 × 80 | ±52.5° / ±40° | ±42.5° / ±30° |
| generic | 60 × 40 | ±30° / ±20° | ±20° / ±10° |

The widest entry is 105°, on a Center Stage camera — a digitally panned
ultra-wide where a face at the extreme edge sits in the worst-corrected part of
the lens and the head-position estimate is least trustworthy. **On the device
A33 was written for, the geometry is being built for poses the tracker cannot
see, by 2.2× horizontally and 3.75× vertically.**

Vertical is the binding axis and it is also where D4 said the problems were:
*"Vertical offsets (the user's actual head motion) are worse than horizontal."*

**(b) Camera FOV bounds where a face can be *detected*, not where a panel can be
*viewed*.** At 60° off-axis a laptop panel is foreshortened to cos 60° = 50% of
its width, its angular subtense collapses, and the panel is at 60° incidence
where LCD contrast and luminance degrade well beyond the geometric term. That is
not a viewing position. The proposed simulated-viewer mode (§8) will show this
directly and is the right way to settle it.

**(c) The cost was paid three addenda later and was not attributed back.**
a109 predicted its own cost honestly — reveal width, mask area and plate reach
all ×1.73, fold limit tightened by the same factor, torn fraction 33.63% →
37.60% on the troll, one 8-bit level going from 2.2–3.5× to **3.7–6.1× the fold
limit**. It then measured the *mask* and found it barely moved (0 → 1.8 points),
and the change landed.

Then a117, in Addendum 116, found the fold tear dropping **692,469 of 1,737,400
triangles (40%)** and shipping the debris as a 1px comb — the user's "banded to
oblivion". a117's own diagnosis: *"the fold limit at 851px is 0.47 of ONE 8-bit
level… the smallest step the source can express already folds."* That is a109's
predicted cost arriving, and it was diagnosed as a tear-mode bug rather than as
the cone's bill.

**And the envelope that was working:** A30 measured *"zero holes at all nine
poses across the 35-degree support cone"*; A32 measured the full 45° 12-pose scan
at *"SW 0 hole px at every pose, frazetta 74k → 10–42px"* (0.01% of a frame) and
concluded:

> *"The declared envelope (A29) is a 45-degree cone with fade from 35; within
> it, flat planes with world-sized skirts are measurably hole-free. An
> equirect/dome projection buys curvature only useful past ~60 degrees… If the
> envelope ever widens toward the 'gyro past face-cam FOV' regime, revisit."*

The envelope widened to exactly 60° and the revisit did not happen.

---

## 2. Why this is an easy decision: the knob is not the one you think

The parallax law is `shift(z) = −ex·z/(D−z)` with `ex = D·tan(bgViewFadeEndDeg)`.

Read carefully: `bgViewFadeEndDeg` sets **`ex`, the excursion the geometry is
*budgeted* for**. The shift actually applied at a live head angle θ is
`−D·tan(θ)·z/(D−z)`. **`bgViewFadeEndDeg` does not appear in it.**

So:

| what you change | effect on the image at a given head pose | effect on `k` and the artifact stream |
|---|---|---|
| **cone angle** (`bgViewFadeEndDeg`) | **none** — identical pixels at every θ inside the new cone | ∝ tan θ — this is the whole artifact stream |
| **depth relief** (world depth range ÷ portal distance) | proportional — this *is* the depth impression | ∝ relief |

Depth impression in a head-coupled display comes from the *gain* — image shift
per unit head movement — not from total excursion. Narrowing the cone leaves the
gain untouched. The only thing a viewer can perceive is that the fade starts
sooner, and on a Mac the fade already starts at 17° while the cone is budgeted
for 60°, so nobody has ever seen the difference.

**Cone is free. Relief is not.** Turn the free knob first, all the way to the
physical bound. Only touch relief if `k` is still too large after that.

---

## 3. The numbers

From A110's measured `k = 775` at 851×1023 **at the 45° cone**, and
`k(θ) = 775·tan θ`:

| θ (half-angle) | what it is | k @ 851px | k / W |
|---|---|---|---|
| **60°** | **current (a109)** | **1342** | **1.58** |
| 52.5° | iPad camera edge | 1010 | 1.19 |
| **45°** | **A29/A30/A32 envelope — measured hole-free** | **775** | **0.91** |
| 35° | A29 full-support edge | 543 | 0.64 |
| 32.5° | iPhone camera edge | 494 | 0.58 |
| **27°** | **Mac camera edge — head physically undetectable past here** | **395** | 0.46 |
| 25° | iPhone vertical edge | 361 | 0.42 |
| **17°** | **Mac fade start — last fully-supported pose** | **237** | 0.28 |
| 16° | Mac vertical camera edge | 222 | 0.26 |
| 10° | — | 137 | 0.16 |
| **6°** | **Mac vertical fade start** | **81** | 0.096 |

Thresholds worth having on the same axis:

- **8-bit depth fold-safe** needs `k ≤ √2·255 = 361` → **θ ≤ 25°**. The original
  45° design sat just outside this, which is why a99's float ingest was needed;
  at 60° it is not close.
- **20 flat MPI planes artifact-free** needs `k ≲ 20` → **θ ≤ 1.5°**.
  **Consequence: flat planes at 20 bins were never going to work at any usable
  cone. v2's ghosting is not a binning problem and no binning decision fixes
  it.** It needs depth-displaced layers — the Addendum 3 design. This retires a
  line of inquiry.
- **Completion ≤ 10% of image width** for a full 0.5 depth step needs
  `k ≤ 0.2W = 170` → **θ ≤ 12.4°**. Past that, disocclusions behind a major
  occluder are mostly invented content.

---

## 4. Size the budget at fade START, not fade END

`ex = D·tan(bgViewFadeEndDeg)` budgets the geometry for the pose at which the
overlay has already faded the canvas **to black**. The fade band exists
precisely so the rim does not have to be correct. Paying full completion,
margin, plate and mesh cost for content that is rendered at zero alpha is pure
waste, and it is the largest single over-build in the pipeline.

Correct form: budget at fade *start*, with the fade band absorbing progressive
degradation.

| device | current budget angle | correct budget angle | k reduction |
|---|---|---|---|
| mac | 60° | 17° (H) / 6° (V) | **5.7× / 16.5×** |
| iphone | 60° | 22.5° / 15° | 4.2× / 6.5× |
| ipad | 60° | 42.5° / 30° | 1.9× / 3.0× |

Note the axes are different and should be budgeted separately — `ex` is
currently one scalar. The vertical axis is where the head range is smallest and
where D4 measured the worst behaviour; giving it its own (smaller) budget is
free quality.

---

## 5. Untracked viewers on a shared panel do not need a wide cone

This is worth stating because it may be the real intuition behind a109.

On an ordinary panel there is **one image on screen at a time**. A tracked
viewer's off-axis frustum pre-distorts it so that *their* physical foreshortening
cancels it. Anyone else in the room sees that pre-distortion uncancelled,
foreshortened by their own angle. Widening the render cone does not help them —
it changes what the *tracked* viewer's geometry budget is, not what a bystander
sees.

So the shared-panel case is an argument for **the simulated-viewer instrument**
(§8), and possibly for a "gallery mode" that renders head-on and accepts
foreshortening for everyone. It is not an argument for a wide geometry budget.
(It *would* be, on a lenticular or light-field panel. That is a different
product.)

---

## 6. Recommendation

**Immediate, zero-risk:** revert `bgViewFadeStartDeg/EndDeg` to **35/45**. That
is the last envelope measured hole-free on all assets (A30, A32), and it is
1.73× off `k` for free. Do this before anything else in the handoff do-list;
it changes the baseline every later measurement is taken against.

**Correct, small:** derive the cone per-device from the FOV LUT that already
exists, per axis, budgeted at fade-start, capped at 45°:

```
fadeEndDeg[axis]   = min(deviceFov[axis] / 2, 45)
fadeStartDeg[axis] = fadeEndDeg[axis] − 10
budgetDeg[axis]    = fadeStartDeg[axis]          // ex is sized from THIS
```
Mac → budget 17° H / 6° V. iPhone → 22.5° / 15°. iPad → 35° / 30°.

**Then decide relief, with data.** At Mac's 17°, `k = 237 = 0.28 W`. Completion
behind a full-depth-step occluder is 119px at 851 wide — feasible but not
comfortable. If §7's measurement says heads rarely exceed 10°, `k` drops to 137
and the whole problem becomes small. If it says the effect feels too flat at
that budget, *then* consider relief — knowingly, as a depth-impression trade,
not as a side effect.

**And keep the wide look, separately.** The demo turntable, the manual drag, and
any export path can go anywhere they like. They are not head-tracked, they have
no pixel-fidelity contract, and they should route to the generative bake with
its own thresholds. Manual drag past the cone should show the fade, not force
the geometry to cover it — it is an inspection tool.

---

## 7. Stop deciding, start measuring

This project is at its best when a question becomes a number, and this one can.

**The head-pose recorder.** Device-camera head tracking already exists (A33) and
already computes the head's angular position through the tan mapping. Log
`(θ_h, θ_v)` at, say, 5 Hz during ordinary use across a few sessions and devices.
Then:

- plot the 50th / 95th / 99th percentile contours
- set the cone at the 99th percentile, or wherever the tail flattens
- report what fraction of frames the current 60° budget was ever needed for

My expectation, stated so it can be falsified: on a laptop the 99th percentile
will land under 20° horizontal and under 10° vertical, and the 60° budget will
turn out to have been exercised on **zero frames of real use**. If that is
wrong, the data says so and the cone stays wide with a reason attached.

This is a few hours of work and it permanently converts the cone from taste into
measurement — which is the only way it stops being re-litigated.

---

## 8. Review of the simulated-viewer preview spec

**Verdict: build it, and build it early — it is the instrument this decision
needs.** The core insight is correct and under-appreciated in the record: an
off-axis frustum pre-distorts the image so that a physically off-axis viewer's
foreshortening cancels it. **A tester scrubbing a virtual eye while sitting
head-on to their monitor is looking at raw pre-distortion and it will look
catastrophically wrong while being entirely correct.**

That is very likely contaminating the review loop already. A114 records the user
reporting the render "looking broken from almost any angle", and the response
that four of five grids were outside the supported cone — *"which I said, and
which was true and beside the point."* This spec explains why it was beside the
point and gives the instrument that would have settled it.

### What is right and should not be negotiated

- **Real 3D quad, not a 2D quad with displaced corners.** Correct and
  non-obvious: per-triangle interpolation is affine and creases along the
  diagonal. The 3D quad gets perspective-correct interpolation for free.
- **Fixed FOV, never autoscaled — "the shrink is the signal."** Right.
  Autoscaling would hide the solid-angle collapse, which is the measurement.
- **1.75× supersampled pass 1.** Right, and specifically protects the stretch
  net: at 1× the double resample would hide the fragment stretch the net exists
  to catch.
- **Linear-space falloff multiply.** Right; in sRGB the dimming would be
  visibly wrong.
- **Not gated on the fade cone.** Right for an instrument.
- **PiP A/B (`shift-K`) via setViewport/setScissor, not a second canvas.** Right,
  and both views genuinely are needed — raw for coverage and stretch, warped for
  perceived correctness.
- **The acceptance test, and especially its last clause.** *"If the anchor
  swims… report it rather than tuning the overlay to hide it."* That is exactly
  the right instruction for this codebase's history. Keep it verbatim.

### Amendments I would make

**A1 — Assert the shared frame convention before trusting the acceptance test.
(Important.)** The test can only be meaningful if pass 1 and pass 2 use *the
same* E and *the same* panel rect. If pass 1's projection is anything other than
a true off-axis frustum onto the W×H rect at z=0 — for example a residual
"view-Z push" from before a60's reprojection landed, or a portal rect that is
not exactly that plane — the anchor will swim for a **frame-convention reason,
not a frustum bug**, and the instrument will emit a confident false positive.
That is the A113/A115 failure mode exactly.

> Add to the spec: *before the acceptance test, log pass 1's E, panel rect and
> projection matrix alongside pass 2's, and assert they describe the same
> geometry. The test does not run until they agree.*

**A2 — Prove the instrument can see a break.** Same rule as everywhere else in
this project: deliberately perturb the off-axis frustum by a known amount, and
confirm the anchor visibly swims by the predicted number of pixels. An
instrument that has never detected a fault has not been shown to work.

**A3 — Scrub on a sphere, not a line.** The spec parameterises E but not how the
scrub maps to it. If a lateral slide is used, θ and |E| change together and the
HUD's θ becomes ambiguous. Recommend scrubbing at constant `|E| = D_REF` so θ is
the only variable, with a separate dolly control if distance is wanted.

**A4 — Put `k` on the HUD.** This is the highest-value addition and it is what
turns the mode into the cone-decision tool:

```
theta            27.0 deg
k needed here    395 px      (parallax across depth range at this pose)
k budgeted       1342 px     (bgViewFadeEndDeg = 60)
completion used  30%
Omega            41% of head-on
subtense         18.3 x 11.6 deg
```

Scrubbing then shows, in one HUD, the pose, what the geometry was built for, and
how much of it this pose actually needs. The 3.4× over-build becomes visible
rather than argued.

**A5 — Label the falloff "geometric", not "display".** `a = E.z/r³·refD²` is
Lambertian irradiance from a diffuse patch: correct as a *geometric* bound, but a
real LCD falls off faster off-axis than cos θ, and OLED differs again. The mode
will therefore **understate** how bad 60° looks, which is fine for the argument
but should not be mistaken for a calibrated display model. Also: make explicit
that `uRefD` and `D_REF` are the same constant, and decide whether it tracks
`|E|` under dolly or stays fixed at 0.45 m.

**A6 — The up-vector guard will snap.** `abs(dot(normalize(E), up)) > 0.999` is a
2.6° window, and crossing it flips the roll discontinuously. Either blend over a
wider band or derive up by projecting the panel's +y into the view plane. Only
matters near the pole, which is outside the interesting range — worth one line,
not a redesign.

**A7 — Log the supersample cap.** 1.75× linear is 3.06× the pixels; on a 3000px
asset at a large canvas that is real. Capping is fine — **capping silently is
not**. That is precisely the `Math.min(mx, pw)` lesson from A115. If the factor
drops, print it.

**A8 — Add the head-pose recorder to the same feature.** §7. The simulated
viewer answers *"what does an off-axis viewer see?"*; the recorder answers
*"does anyone ever go there?"* Together they close the cone question. Overlaying
the recorded 95th/99th-percentile pose contours on the simulated-viewer HUD
would make the answer visible in one screenshot.

### One thing to expect

When this mode is first switched on, a meaningful fraction of the artifacts
currently on the open list will look **much less severe than they do in the raw
scrub**, because the physical keystone puts the stretched geometry back where it
belongs. Some will get worse. Both outcomes are information, and re-triaging the
open defect list through this mode before doing any more fixing is probably the
single cheapest thing available right now.

---

## 9. Correction: the gyro path, and what it actually changes

### 9.1 What the first draft got wrong

§1–§6 sized the cone from the **front-camera FOV** and concluded the 60° budget
covers poses that cannot occur. That is true for the *webcam* pose source. It is
not the whole picture, because on phone and tablet the **gyro** takes over
exactly where the camera loses the face, and device tilt reaches well past any
camera FOV.

So a109's intent was not baseless, and this claim from §0 was overreaching:

> *"Narrowing the cone does not reduce the sense of depth, at all, at any pose a
> viewer can actually reach."*

Correct statement: **narrowing is free up to the reachable limit of the pose
source.** On a Mac webcam that limit is ±27°, so a 45° budget is already
generous and 60° is pure waste — the original conclusion holds there unchanged.
On a handheld gyro the limit is much larger, and narrowing the budget below it
**is** visible: the effect fades out at angles the user can still reach, which
is a real regression.

### 9.2 The gyro geometry, and why it is a softer contract

Hold a device at distance `D` and rotate it about its own centre by φ. The eye
stays put in world space, the panel normal rotates by φ, so the eye is now at
φ off-axis. **Device rotation maps roughly 1:1 to viewing angle**, and ±45–60°
is comfortable; people learned this gesture from AR and parallax apps.

But four things make the gyro contract weaker than the webcam one, and they
matter for how much geometric exactness is worth buying:

1. **Gyro measures orientation, not position.** The eye's location is *assumed*
   (some nominal `D`, head stationary). The webcam *measures* the head.
2. **Real tilts translate as well as rotate.** A wrist or elbow tilt swings the
   device through an arc, so the true eye→panel vector differs from the pure
   rotation the gyro reports. The error grows with φ.
3. **The head moves too.** People counter-rotate slightly when tilting a device.
4. **Drift and re-zeroing.** Gyro integration drifts and needs a decay toward a
   nominal rest pose, so "head-on" itself wanders.

Consequence: at large gyro angles you are producing **a plausible parallax
effect, not a reconstruction of a specific eye's view**. That is fine — it is
what makes the gesture feel good — but it means paying for pixel-exact geometry
at 60° buys precision the pose estimate cannot use.

This is also why the simulated-viewer acceptance test (§8) is a **webcam-path
test**. Its premise is that physical foreshortening exactly cancels the baked
pre-distortion, which requires the assumed eye to be the real eye. On the gyro
path there is no ground-truth eye to be stationary against, so the pixel-
stationary anchor criterion applies to the webcam path and to the harness, not
to gyro playback.

### 9.3 A32 named this exact regime, and asked for a different representation

The important consequence is not "so keep the wide flat-plane budget." It is
that Addendum 32 already anticipated this and asked for something a109 did not
deliver:

> *"The declared envelope (A29) is a 45-degree cone with fade from 35; within
> it, flat planes with world-sized skirts are measurably hole-free. An
> equirect/dome projection buys curvature only useful past ~60 degrees… **If the
> envelope ever widens toward the 'gyro past face-cam FOV' regime, revisit.**"*

The gyro path **is** the "gyro past face-cam FOV" regime, by name. a109 entered
it and kept flat planes. So the correct reading of "the gyro extends the range"
is:

> The gyro justifies a wider **envelope**. It does not justify serving that
> envelope with the **current representation**. Past ~60° A32 says flat planes
> need curvature, and the plane-count arithmetic (§3) says 20 flat bins were
> never enough at any usable cone regardless. The wide path is the one that
> needs depth-displaced layers, not the narrow one.

### 9.4 The move that actually resolves this: separate the budget from the fade, and degrade instead of cliff

Right now **one parameter does two jobs**: `bgViewFadeEndDeg` sets both where the
canvas dims and how much geometry gets built. That forces a false choice —
either build for 60° (and pay the a117 bill everywhere) or fade at 27° (and kill
the gesture on mobile).

Split them:

```
bgViewBudgetDeg      // sizes ex, completion extent, plate margin, layer count
bgViewFadeStartDeg   // where the overlay begins to dim
bgViewFadeEndDeg     // black
   with   budget ≤ fadeStart ≤ fadeEnd
```

Then define what happens in the band **between the budget and the fade**, which
today is undefined and is why leaving the budget produces black holes and combs
rather than a soft landing:

| zone | contract |
|---|---|
| θ ≤ budget | full completion, pixel-honest, all gates apply |
| budget < θ ≤ fadeStart | **graceful degradation**: as completion runs out, crossfade the uncovered fraction toward the layer's backdrop plane and let the wash widen. Never black, never comb |
| fadeStart < θ ≤ fadeEnd | brightness fade, as today |
| θ > fadeEnd | black |

**You do not need the geometry to be exact at 60°. You need it to fail
gracefully at 60°.** Today it fails by tearing 40% of the mesh and showing the
debris; that is what "banded to oblivion" is. A degradation ladder gives the
gyro its full reach at a fraction of the geometric cost, and it is a much
cheaper thing to build than a 60°-exact plate.

### 9.5 Per-device budgeting is free here

The bake runs **in the browser, per session** (v2 at 11.7 s, quick at 10.3 s —
A116). So the budget does not have to be a single global constant baked into a
shipped asset: a desktop session can bake to the desktop budget and a phone
session to the mobile one. Desktop never pays mobile's bill.

If a server-side or cached bake is ever introduced, that changes — and at that
point the max-budget bake becomes a real cost that should be measured
separately, not absorbed silently.

### 9.6 Revised recommendation

Replaces §6. `k` figures are for a 1920-wide landscape asset, from
A110's `k(45°) = 818`.

| profile | pose sources | budget (fade-start) | fade | k @ 1920 | vs today |
|---|---|---|---|---|---|
| **desktop** | webcam only | **17–27°**, per axis | 27–35° | 250–417 | **3.4–5.7× cheaper** |
| **mobile** | webcam + **gyro** | **35–45°**, symmetric | 50–65° | 573–818 | **1.7–2.5× cheaper** |
| inspection (drag) | — | *not a budget source* | none — show the fade | — | — |
| turntable demo | — | *not a budget source* — **clamp the slider to the budget** | — | — | — |
| export / cinematic | — | any — generative path, own thresholds | — | — | — |

Notes:

- **Per axis on webcam, symmetric on gyro.** The webcam's vertical range is far
  smaller than its horizontal (mac 32° vs 54°); tilt is roughly symmetric. So
  axis asymmetry is a property of the *pose source*, not of the device.
- **Budget at fade-start, not fade-end**, on both profiles. Unaffected by the
  gyro correction and still the single largest free win — the fade band exists
  so the rim does not have to be right.
- **The turntable slider must not set the budget.** A115 found the margin being
  sized from the demo sweep sliders; the dependency runs the wrong way. Clamp
  the slider to the budget instead.
- **Still revert to 35/45 first.** It remains the last envelope measured
  hole-free on all assets (A30, A32), it is a strictly better baseline than 50/60
  for every later measurement, and 45° sits inside the mobile budget range
  above — so it is not a regression for the gyro gesture either. Do it before
  taking any baseline, then split budget-from-fade and set the two profiles.

### 9.7 What is now the open question

Not "how wide should the cone be" — that is answered per profile above. The
open question is narrower and more useful:

> **What is the gyro path's actual reachable distribution, and what does the
> degradation band need to look like for the gesture to still feel good at
> 45–60°?**

Both are measurable with instruments already proposed: extend §7's pose recorder
to log gyro angles as well as webcam angles, and use the simulated-viewer mode
(§8) — with the §9.2 caveat that on the gyro path it shows a plausible viewer,
not a ground-truth one — to judge the degradation band by eye at 45°, 55°, 65°.
