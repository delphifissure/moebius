# S48 — The two things taken from S47, and Sprint 25 finished (2026-09-21)

Three pieces of work, in the order the user asked for them: the unpainted-pixel assertion, the reveal-per-cell field as
the bake's cliff criterion, and the rest of Sprint 25 — the return path, so depth comes back as well as colour.

The plan that follows from all of it is `S49_plan.md`, which supersedes S41.

---

## 1. The unpainted-pixel assertion

> **No pixel should be both unpainted and surrounded by painted neighbours closer than T.**

`moebiusv2/harness/unpainted.js`, wired into the standing envelope instrument `harness/s44_envelope.js`.

### Why it is worth more than it looks

Every hole number this project has ever reported is **the sum of two different failures**:

- a **gap we should have covered** — a crack between two displaced texels that are still adjacent on the surface. Nothing
  was revealed there; the representation simply failed to span its own sample spacing. This is a renderer bug.
- a **genuine disocclusion** — the eye has moved far enough to see past an edge and there is nothing behind it in the
  picture. This is work for the fill stage.

"Dark %", "hole area at 45°", the a220 hole counts and every tear-law A/B in the project add the two together, so a change
that halves the cracks and a change that halves the reveals read identically. The assertion separates them mechanically,
and S47 was right that **we could not make that distinction before under any representation.**

### The test

On a rendered frame, a pixel is *unpainted* if the backdrop shows through (nothing was drawn). Take the maximal unpainted
run through it along the row and along the column. If either run has painted pixels at **both** ends and is at most T
pixels long, the pixel is a **leak**: painted neighbours sit closer than T on both sides, so a spanning rule of reach T
would have closed it. Anything wider is genuine.

A third class falls out for free and had to be separated or it would have inflated the second: a run that reaches the edge
of the measured rectangle on **both** axes is **unbounded** — there is no painted neighbour on either side, so the
assertion says nothing about it. With the margin strips off, that is the beyond-frame region, which is not a disocclusion
at all. Reporting it inside "genuine" would have made the fill stage look like it owed content for the letterbox.

T is not a tuning constant. It is the reach of whatever rule is being asserted about: 1 for "adjacent samples must stay
adjacent", 2 and 4 for the splat sizes S47 priced.

### Measured, at the shipped defaults

The troll, the panel's own defaults (`far plane / fill wash / margin off / band 35 / seams stretched / rules new`),
measured inside the rest-pose content rectangle.

| pose | unpainted % of frame | unbounded (beyond the frame) | leak T=1 | leak T=2 | leak T=4 |
|---|---|---|---|---|---|
| rest | 0.001 % | 0.0 % | 100 % of bounded (1 px) | 100 % | 100 % |
| 45° right | 2.005 % | **99.1 %** | 100 % of bounded (15 px) | 100 % | 100 % |
| 45° right + up | 1.498 % | **97.8 %** | 96.6 % of bounded (28 px) | 100 % | 100 % |
| down-left corner | 21.254 % | **95.5 %** | 3.6 % of bounded (30 px) | 9.7 % (80 px) | 21.1 % (174 px) |

### The first measurement corrects the headline it was added to

S44's result for this picture was "at the worst envelope corner, 27.7 % placeholder and **21.3 % dark**", and the second
of those numbers has been carried since as the size of the hole the fill stage owes content for. **It is not.** At that
corner 95.5 % of the unpainted set reaches the rectangle edge on both axes: with the margin strips off, the picture
simply does not extend that far. The actual disocclusion hole is 21.254 % × 4.5 % ≈ **0.96 % of the frame**, and 3.6 % to
21.1 % of *that* is a crack a spanning rule of reach 1 to 4 px would have closed.

The horizontal poses are starker. At 45° right the frame is 8.900 % invented colour, 1.99 % beyond-frame, and **0.018 %
actual hole — every pixel of which is a one-texel crack.** The covering is essentially complete there; all of the mess is
colour.

**This sharpens S47's standing conclusion rather than contradicting it.** S47 said two thirds of what reads as messy is
the placeholder colour. Once the frame edge is taken out of the dark number, at the horizontal poses it is not two thirds
— it is very nearly all of it. Every hole-count A/B in the project's history was scored on a quantity that is
predominantly letterbox at off-axis poses, which is exactly the conflation the assertion was added to catch, and it
caught it on its first run.

Two things to keep honest about this. The content rectangle is the *rest* pose's bounding box, so as the picture shifts
within it the beyond-frame share necessarily grows — "unbounded" is measuring a real thing, but it is a framing artefact,
not a defect, and turning the margin strips on is what removes it. And 30 to 174 leaked pixels is a small absolute
number; the value here is the *separation*, not the magnitude.

Per-pose leak maps are written next to the frames (`leak_plain_*.png`): **red** = leaks at the tightest T, **amber** =
leaks only at a wider T, **blue** = a bounded genuine disocclusion, **grey-blue** = unbounded (beyond the frame).

---

## 2. The reveal-per-cell field as the cliff criterion

> reveal(a, b) = | Z_a/(D + Z_a) − Z_b/(D + Z_b) | · |ex| · pxPerWorld,  Z = −z(d),  ex = D·tan(half-angle)

`window._revealLaw` / `_revealPxField` / `_armRevealLaw` in `moebius.js`, with the identical law in GLSL (`_revealZofD`,
`_revealPx`) so the conversion is exact per fragment rather than linearised at one depth. `z(d)` is the app's own
`viewSpaceDisplacement` law, not a re-derivation.

### The problem it fixes

The bake states its cliff criteria in **three unrelated proxies**:

| where | criterion | unit |
|---|---|---|
| S46 near-extent rule | `u_plateNearOnly` | source quanta (a89) |
| A212 / Sprint 17a fold | `u_fragTearFactor` | a fraction of a texel's own extent |
| the tear law | `fgTearStep` | a normalised-depth step |

None of them is the unit the artefact appears in, and none survives the one thing that varies most between our test data
and our product: **the truth kit renders at relief 3.2 and the app ships relief 0.1, thirty-two times shallower.** A
threshold in quanta means two different visible gaps in those two worlds. A threshold in pixels of reveal means the same
gap in both, by construction.

### What shipped

- **`window._plateNearOnlyPx = T`** (negative for the green check view) runs S46's rule with its tolerance in **screen
  pixels at the rim**, and takes precedence over the quantum form when set. The law travels to the shader as
  `u_revealLaw = (outer, inner, pn, D)` and `u_revealScale = |ex| · pxPerWorld`.
- **`plane_reveal_px.png`** in the SD bundle carries the field per texel in **plate texels** — the same currency
  `research/s35/bleed/subpixel.py` measures offline, so the exported field and the S47 kit measurement are directly
  comparable. `meta.plane.reveal` carries the law, the percentiles, the counts over 1, 2 and 4 texels, and the
  screen-pixels-per-texel scale.

Two currencies on purpose: the live rule is a fragment test and must be in screen pixels, which depend on the canvas; the
exported field is a property of the bake and must not.

### The field, and the check that it is the right field

The troll at the shipped defaults, from `meta.plane.reveal` of the bundle the round trip exported. The law it reports:
`D = 0.2`, `exH = 0.2`, `exV = 0.1155`, layer width 0.0749 m, **11 366 plate texels per world metre** and **3 575 screen
pixels per world metre** — so at this viewport one plate texel is **0.3145 screen pixels**, and a live threshold of 1
screen pixel is about 3.2 plate texels. Sprint 26's sweep has to be read in that light.

| | p50 | p90 | p99 | max | mean | > 1 texel | > 2 | > 4 |
|---|---|---|---|---|---|---|---|---|
| **app** (`meta.plane.reveal`) | 0.3700 | 1.7289 | 14.7580 | 143.605 | 1.2591 | 153 376 | 79 865 | 52 277 |
| **independent Python**, same law, same input | 0.3700 | 1.7292 | 14.7580 | 143.605 | 1.2592 | 153 390 | 79 869 | 52 281 |

The two agree to the printed precision on every percentile and exactly on the maximum. The count columns differ by 14 of
153 376 (0.009 %), which is float32-against-float64 landing either side of the threshold on ties. The exported 16-bit PNG
round-trips to within **0.008 texels** of the unclipped field — larger than the file's own 0.000244-texel step, and
correctly so: the PNG's input is the *quantised* source depth, and 1/131070 in d is worth about 0.005 texels here. The
field is what it claims to be.

**The field spans three orders of magnitude on one photograph** — median 0.37 texels, p99 14.8, max 143.6. That is the
case against a single threshold in quanta better than any argument: no fixed depth step means the same thing at both ends
of this range, and this is one picture, before the 32× relief difference between the kit and the app is applied.

### A correction to how S47's troll row should be read

S47's troll numbers were computed from `harness/shots/a257probe/troll/dQ.f32`. That dump has **492 284 distinct depth
levels**; the depth map the app ships by default conditions to **59 525**. They are not the same estimate of the same
photograph, and they differ by a mean of 0.156 in d over 99 % of texels. So the offline and live fields can be compared
in *shape* — medians 0.364 and 0.370 — but not in the tail, where the app reads max 143.6 and S47's row reads 238.7.
Nothing in S47's conclusion depends on the tail, so it stands; but its troll row is the DA3 map, and should be labelled
that way wherever it is quoted.

### Why the pair is deliberate

The reveal field says, **before** rendering, which cells will open a gap wider than T. The assertion says, **after**
rendering, which gaps we failed to close. Same quantity, same unit, opposite ends of the frame. Sprint 26 in `S49_plan.md`
closes the loop between them: sweep the threshold, and check that raising it converts leaks into covered pixels without
growing the genuine class. If it grows the genuine class the rule is eating surface, and that is a falsification the pair
can state and neither half could.

---

## 3. Sprint 25 finished — the return path

S45 measured the contract before it was built. This is the rest: the export side, the entry point, and the round trip.

### The export additions (R7 §4 and §5)

PACO tried three inpainter contracts **with the ground-truth amodal mask** and all three failed: inpainting the hole
alone makes the model complete the occluder; greying it leaks the grey; extending the mask invents new objects. A hole
does not tell a model whose surface it is. So the bundle now states ownership rather than a region:

- **`plane_mask_context.png`** — the legal source region. White = a texel whose colour may be copied or attended to: the
  background the picture already shows. Black = an occluder footprint or a placeholder. An occluder footprint *is* the
  set of texels standing in front of the band it reveals, so black is exactly "not strictly behind the occluder". This is
  the no-clone rule written as a constraint instead of a hope, and our arrival order is a strictly better layer index
  than the depth clustering the literature uses.
- **`plane_color_occluder_removed.png`** — the plate colour with every occluder footprint and placeholder replaced by a
  **harmonic continuation of the legal background** (Laplace, Dirichlet on the context mask). Not left in, and not flat
  grey, because PACO tested grey and the fill colour leaks. It is a seed and a context, not content, and the meta says
  so: the solve is capped at 240 sweeps.
- **`meta.plane.returnContract`** — what to send back, in what encoding, and exactly what the app does with it.

### The entry point

`window._importPlaneReturn(...)`, `window._importPlaneReturnFiles(...)`, and an **Import plane return** button.

- **Colour** is written on the inpaint mask and nowhere else.
- **Depth is never pasted.** The absolute return is shifted **per band component** so each component meets its own visible
  rim, which removes any constant bias the model carries; the gradients become the guidance field; and the two are
  reconciled by the screened solve with the **observed plate depth as the Dirichlet boundary**. The seam is therefore
  exact by construction rather than by tuning — and the reimport measures it anyway, because "by construction" is a claim
  and this is the instrument that would catch it failing.

**The limitation, stated rather than hidden.** The plate's triangle index was torn at bake time from the baked depth. A
returned depth that moves a cliff does not re-tear the mesh. The reimport reports how many rim-law decisions would now
differ, so the size of that gap is a number; rebaking re-tears.

### The round trip, measured

`harness/s45_roundtrip.js` drives the whole loop headlessly: bake → export → decode the zip → synthesise a return →
reimport → score. There is no ground truth for a photograph's hidden surfaces, so what is under test is **the contract and
the plumbing, not a model**: the bake's own band depth is the target, it is corrupted the way a model's output is corrupt
(a constant bias plus per-texel noise), and the corrupted values are handed back. A contract that cannot recover a field
it was handed a noisy copy of cannot recover one it was handed a guess.

The troll at the shipped defaults. 347 177 band texels in 261 components; the return is the bake's own band depth plus a
constant bias of 0.020 and uniform noise of half-width 0.040, giving a **raw return RMSE of 0.0304 in d**. Lower is
better, and the interesting column is the ratio: below 1.0 the contract made the return *worse* than pasting it.

| form | band RMSE | vs raw | seam max &#124;Δd&#124; | retear decisions changed |
|---|---|---|---|---|
| **gradient** (pure, λ = 0) | **0.01184** | **2.57×** | 0 | 4 360 / 715 009 |
| both (screened λ = 1), far-side rim | 0.03486 | 0.87× | 0 | 9 962 |
| absolute + shift, far-side rim | 0.04311 | 0.70× | 0 | 64 582 |
| both, every visible neighbour *(the first build)* | 0.17762 | 0.17× | 0 | 35 320 |
| absolute, every visible neighbour *(the first build)* | 0.18611 | 0.16× | 0 | 140 258 |
| absolute → membrane *(the mistaken call, kept as a baseline)* | 0.24444 | 0.12× | 0 | 45 052 |

**The seam is exactly zero in all six**, which is the one thing the formulation promised by construction, and the colour
path wrote 347 177 texels inside the mask and **0 outside** in all six.

### This contradicts S45's kit result, and the round trip found three defects doing it

On six kit scenes the screened combination won every row. On the one photograph, **the gradient channel alone wins by
3×, and both absolute forms are worse than not correcting at all.** Getting to that statement took three fixes, none of
which the kit could have surfaced:

1. **The shift anchored on the wrong rim.** A band component is bounded by the background it continues *and* by the
   occluder that created it. Averaging over both made the correction absorb the cliff. Filtering the rim through the rim
   law — the test the bake already uses for this question — is worth **5.1×** on the combined form (0.1776 → 0.0349) and
   **4.3×** on the absolute form. Kept as an A/B arm, not asserted.
2. **The degenerate form was never implemented.** With an anchor and no gradients the guidance field is zero, so the
   screened solve is a Laplace problem: at λ = 0 it discards the return and interpolates the rim. S45's own note said the
   degenerate case is "the per-component shift alone, no solve"; the code fell through to the solve, so the first run
   scored a membrane (0.2444) and called it the absolute contract. Now written out, with the mistaken call kept as an
   explicit baseline row because it is the do-nothing shape for this contract.
3. **The anchor is measuring the wrong quantity, and the shift statistics say so outright.** The true bias is +0.020, so
   the ideal shift is −0.020. The measured shift is **+0.016** (pixel-weighted mean; p50 +0.015, range −0.055 to +0.087).
   Wrong sign: it roughly doubles the bias rather than removing it, and 0.020 + 0.016 = 0.036 is exactly the observed MAE
   of 0.0361.

### Why the rim is a biased estimator, which is the finding

Working back from that number: the observed depth at a far-side rim neighbour is on average **0.036 in d nearer** than
the plate's far field at the band texel beside it. That is not noise. It is the geometry — a band opens onto background
that *recedes* from the rim, so the far field at the rim is systematically the shallowest part of the component. **A
constant estimated from the rim is therefore biased by construction, not by sampling.** And the median component has only
**10 rim pairs** to estimate it from, so even an unbiased version would be noisy.

The kit never showed this because its components are small, numerous and well-rimmed. The photograph's are not: **100 of
261 components have no legal far-side rim at all** — they touch only their own occluder, so nothing in the picture says
where they sit.

**The fix follows without introducing a constant.** Do not estimate an offset from the rim. The screened solve's
Dirichlet boundary already *is* the rim, applied pointwise rather than averaged, so it meets the observed depth
everywhere without assuming the offset is constant across a component. That is exactly what the pure gradient form does,
and it is why it wins.

### What is not being changed on this evidence

**The default stays λ = 1 with the absolute channel accepted.** One photograph against six kit scenes is not grounds to
flip a default, and doing so would be the per-image tuning this project forbids. What has changed is that
`meta.plane.returnContract` now carries the measured caveat, so anyone reading the contract sees both results and the
mechanism. Sprint 27 runs on real pictures and is the natural tie-breaker; `S49_plan.md` carries the specified follow-up
— gate the anchor per component on whether its rim determines anything, or drop it.

---

## What this changes about the order of work

`S49_plan.md`. In short: Sprint 26 is now half a sprint that uses the pair above to settle one cliff threshold and retire
the three proxies; Sprint 27 is one real inpaint end to end, promoted to the top because S44 measured 27.7 % placeholder
colour at the worst envelope corner and S47 established that no change of representation reaches it; the gate is demoted
because S43's do-nothing baseline removed the result that motivated it.
