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

*(Measurement running at this commit — the troll at the shipped defaults, 4 poses. Filled in the follow-up commit.)*

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

### Cross-check against the offline measurement

*(Measurement running at this commit. Filled in the follow-up commit.)*

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

*(Measurement running at this commit. Filled in the follow-up commit.)*

---

## What this changes about the order of work

`S49_plan.md`. In short: Sprint 26 is now half a sprint that uses the pair above to settle one cliff threshold and retire
the three proxies; Sprint 27 is one real inpaint end to end, promoted to the top because S44 measured 27.7 % placeholder
colour at the worst envelope corner and S47 established that no change of representation reaches it; the gate is demoted
because S43's do-nothing baseline removed the result that motivated it.
