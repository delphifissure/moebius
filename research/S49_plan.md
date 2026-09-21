# S49 — The plan after S43–S48 (2026-09-21). Supersedes S41.

S41 set Sprints 23–29 eight days ago. Five of them are now spent, two of its premises have been falsified by its own first
sprint, and S47 added two items that did not exist when it was written. This restates the whole order of operations.

**What changed, in one paragraph each.**

- **Sprint 23 ran and invalidated the tables that motivated Sprint 27.** The do-nothing baseline — predict the visible
  depth, ignore the band — beats *both* the construction and the learned prior on the thing class in two of five field
  scenes (L5 0.0314 against 0.2633 and 0.0395; L6 0.0641 against 0.0732 and 0.0686). S41 justified the gate with
  "arbitration already beat direct prediction on L5 (0.022 against 0.060 m)". In d, with a baseline, that comparison does
  not survive. The gate moves down the order and its brief changes: it is no longer "pick the better of two good answers",
  it is "notice that neither is better than doing nothing".
- **Sprint 24 ran, and S48's assertion has already corrected half of its headline.** The input contract, the consolidated
  defaults and the rest-versus-envelope instrument all shipped (S44): at the worst envelope corner the troll is **27.7 %
  placeholder colour and 21.3 % dark**, against 0.17 % and 0.001 % at rest. The placeholder figure stands. **The dark
  figure does not mean what it has been taken to mean**: 95.5 % of it reaches the frame edge on both axes — with the
  margin strips off the picture does not extend that far — so the real disocclusion hole is about **0.96 % of the frame**,
  and at the horizontal poses it is **0.018 %, every pixel a one-texel crack**. The fill stage's debt is the placeholder
  number alone; the dark number was mostly letterbox.
- **Sprint 25's contract was measured before it was built** (S45) and is now built and round-tripped (S48). Depth comes
  back as well as colour, and it comes back as a screened Poisson solve rather than a paste.
- **S46 answered the streak report** with the near-extent rule, and **S47 answered the splat proposal** with a
  measurement: splats close a twentieth to a third of the *edge* of the hole and none of its content, so the renderer is
  not rewritten. S47 also produced the two items below, which are now built and which change what the bake's criteria are
  written in.

---

## The two things taken from S47, now in the work

These were the user's instruction, and they are done rather than planned. Both are in `moebiusv2` at this commit.

### 1. The unpainted-pixel assertion

> No pixel should be both unpainted and surrounded by painted neighbours closer than T.

`harness/unpainted.js`, wired into the standing envelope instrument (`harness/s44_envelope.js`). On a rendered frame, a
maximal unpainted run of at most T pixels **with painted pixels at both ends** is a gap a spanning rule of reach T would
have closed; anything wider is a genuine disocclusion. A pixel that qualifies on either axis is a leak.

Why it matters more than it looks: **every hole number this project has ever reported is the sum of two different
failures.** "Dark %", "hole area at 45°", the a220 hole counts — all of them add cracks the renderer should have spanned
to reveals the fill stage owes content. A change that halves the first and a change that halves the second read
identically. They are not the same problem and they do not have the same fix. The assertion separates them mechanically,
which no representation in this project could do before, and the split is now printed at every envelope pose with a
per-pose leak map (red = leaks at the tightest T, amber = leaks only at a wider T, blue = genuine).

T is not a tuning constant. It is the reach of whichever rule is being asserted about: 1 for "adjacent samples must stay
adjacent", 2 and 4 for the splat sizes S47 priced.

### 2. The reveal-per-cell field as the cliff criterion

> reveal = |Z_a/(D+Z_a) − Z_b/(D+Z_b)| · |ex| · pxPerWorld,  Z = −z(d),  ex = D·tan(half-angle)

`window._revealLaw` / `_revealPxField` / `_armRevealLaw` in `moebius.js`, with the same law in GLSL (`_revealZofD`,
`_revealPx`) so the conversion is exact per fragment rather than linearised at one depth.

The bake currently states its cliff criteria in **three different proxies**: source quanta (S46's near-extent rule, a89),
a fraction of a texel's own extent (A212's fold factor), and a normalised-depth step (`fgTearStep`). None of them is the
unit the artefact appears in, and none is invariant to the thing that varies most between our test data and our product —
the relief is 3.2 in the kit and 0.1 in the shipped app, thirty-two times shallower. A threshold in pixels of reveal at
the rim means the same visible gap in both.

Shipped this turn:
- `window._plateNearOnlyPx = T` (negative for the green check view) runs S46's rule with its tolerance in **screen pixels
  at the rim**, and wins over the quantum form when set;
- `plane_reveal_px.png` in the bundle carries the field per texel in **plate texels**, the same currency
  `research/s35/bleed/subpixel.py` measures offline, so the exported field and the kit measurement are directly
  comparable; `meta.plane.reveal` carries the law, the percentiles, and the counts over 1, 2 and 4.

**The pair is deliberate.** The reveal field says, before rendering, which cells will open a gap larger than T. The
assertion says, after rendering, which gaps we failed to close. One predicts and one audits, in the same unit, so the
first sprint below can close the loop between them.

---

## Sprint 26 — The tolerance made principled, then the proxies retired (half a sprint; do first)

Everything needed is built; this is a sweep and a deletion.

1. **Sweep `_plateNearOnlyPx`** over 0.5, 1, 2, 4 screen pixels on the troll and the six pictures, at rest and at the
   envelope corners, scoring with the assertion split rather than with a hole total. The prediction is checkable: raising
   T should convert leaks into covered pixels and leave the genuine class alone. If it instead grows the genuine class,
   the rule is eating surface and that is a falsification.
2. **Decide the default on screen.** The user's screen is the aesthetic authority; the sweep only narrows the candidates.
3. **Retire the proxies.** Once a pixel threshold is the default, `fgTearStep` and the A212 fold factor are two more
   spellings of the same decision in units that do not transfer. Rule 7: remove them from the code and record what they
   were.
4. **Re-baseline** the standing instruments with the assertion split, so every hole number after this is three numbers —
   leak, bounded genuine, unbounded — not one. **This is not bookkeeping.** The first run of the split showed the worst
   corner's 21.3 % dark is 95.5 % beyond-frame, which means every hole-count A/B in this project's history was scored on
   a quantity that is predominantly letterbox at off-axis poses. The historical rankings are not automatically wrong, but
   none of them is known to be right either, and the cheapest of them are worth re-running.
5. **Turn the margin strips on and measure again.** The beyond-frame class exists because `margin: off` is the shipped
   default. If the strips remove it, the dark number becomes almost entirely meaningful for the first time; if they do
   not, we have found something else.

**Done means** the bake has one cliff criterion, in screen pixels at the rim, and no hole count in the project is a sum of
unlike things again.

---

## Sprint 27 — One real inpaint, end to end (1 sprint). Now the highest-value thing we can do.

S41 put this inside Sprint 25 as item 7. It is promoted to a sprint of its own because S44 measured what it is worth and
S48 then removed its only competitor. At the worst envelope corner **27.7 % of the troll's frame is invented colour**;
the 21.3 % dark that sat beside it turns out to be 95.5 % beyond-frame, so the hole the geometry leaves is under 1 % and
at the horizontal poses it is 0.018 %. S47's standing conclusion was that two thirds of what reads as messy is the
placeholder colour. With the frame edge taken out, at the horizontal poses it is **very nearly all of it** — and no
change of representation reaches it. Only content does.

The plumbing landed this turn, so this sprint is a run and a look, not a build:

1. **Inpaint on `plane_color_occluder_removed.png`, restricted to `plane_mask_context.png`.** PACO tried three contracts
   *with the ground-truth amodal mask* and all three failed — inpainting the hole alone makes the model complete the
   occluder, greying it leaks the grey, extending the mask invents new objects. A hole does not tell a model whose
   surface it is. So the occluder is gone from the picture the model sees, and the legal source region is stated.
2. **Ask for depth as well**, per `meta.plane.returnContract`: the absolute return *and* the gradients. The app shifts
   each band component onto its own visible rim, then reconciles the two by the screened solve with the observed depth as
   the Dirichlet boundary. Measured on the kit at σ = 0.04: absolute-with-shift ≈ 0.0269, pure gradient ≈ 0.0320, both
   ≈ 0.0175.
3. **Reimport and view** through the envelope. `window._importPlaneReturn` / the Import plane return button;
   `harness/s45_roundtrip.js` drives the whole loop headlessly.
4. **Score with the instruments that exist**: rest-versus-envelope delta, the assertion split, the seam, and the retear
   count (the honest limitation — a returned depth that moves a cliff does not re-tear the bake's triangle index, and the
   reimport reports how many decisions the rim law would now make differently).
5. **Settle the anchor, which S48 left open on purpose.** On six kit scenes the screened combination wins every row; on
   the one photograph tested the pure gradient form wins by 3× and both absolute forms are *worse than pasting the raw
   return*. The mechanism is measured, not guessed: a band opens onto background that recedes from its rim, so the far
   field at the rim is the shallowest part of a component and a constant estimated there is biased by construction — the
   shift comes out +0.016 where −0.020 was wanted. The default was left at λ = 1 because one picture does not outweigh
   six scenes and flipping it would be per-image tuning. This sprint runs on real pictures, so it is the tie-breaker.
   If the photographs agree with the troll, the follow-up is specified and introduces no constant: **gate the anchor per
   component on whether its rim determines anything** (100 of 261 components on the troll have no legal far-side rim at
   all), or drop the anchor and keep the gradient contract, whose Dirichlet boundary already meets the rim pointwise.
6. **Whatever it looks like is the finding.**

---

## Sprint 28 — The sheet A/B (1 day, decides a weeks-long port)

Unchanged from S41's Sprint 26, with two additions to the scoring: the rest-versus-envelope delta (Sprint 24) and the
assertion split (S48). Bake four pictures both ways, render each through the envelope at the same poses, put them side by
side. If the sheet model is visibly better, port it; if it is a wash, shelve it with the numbers. A documented decision
either way.

---

## Sprint 29 — The meadow, reframed (small; can run any time)

Unchanged from S41's Sprint 28, and **S43 strengthened the case for it.** We have framed L5 as a labelling problem. The
do-nothing baseline says something harsher: on L5 and L6 the thing class is a region where *nothing we do beats leaving it
alone*. Counterfactual Depth's formulation does not require separating anything — one mask over any number of objects,
predict the surface behind — and it reports the hidden region as the *easier* one, because what sits behind clutter is
usually floor and wall. Behind a field of tufts is terrain. Test one mask over the whole merged field on L5 and L9. If it
works it removes the regime rather than detecting it. Caveat unchanged: their "nearby objects" factor tops out at two and
nobody has tested fifty tufts.

---

## Sprint 30 — The gate (was Sprint 27; demoted, and its brief rewritten)

S42 falsified the gate for a fifth time: no scene aggregate orders the six scenes (best ρ −0.77, p 0.07, and in the
**wrong direction**), though the opposition split is real per texel (L5 0.0027 against 0.4402 m, 162×). S43 then removed
the result that made the gate worth building.

So the question is no longer "which of the two answers is better here". It is **"is either of them better than doing
nothing here"** — a strictly easier question, with a baseline that is free to compute, and one we have never asked. Two
cheap companions stay, hours rather than days: cross-pose disagreement as a confidence signal (Amodal3R showed
independently completed views disagree and that the disagreement is harmful; nobody turns it into a signal and we already
have the envelope), and DAV2 depth as the observation channel instead of exact ray-traced depth, which S40 showed carries
all the work.

---

## Sprint 31 — Kit diversity, then a training pilot (gated on 29 and 30 both negative)

Unchanged from S41's Sprint 29: the degrees-of-freedom audit first (Infinigen's way — occluder-to-background distance,
background orientation, stacked layers, silhouette complexity, ground-versus-vertical mix), then expansion on the thin
axes, then a 200-scene pilot as a residual off the frozen sheet model with scale-and-shift-invariant plus ranking losses,
an analytic normal loss, band-plus-collar supervision, mask dropout and family-level holdout. The recorded risk is
unchanged and is the reason the audit comes first: every synthetic-to-real mechanism in the corpus depends on a
real-domain signal our task does not have.

---

## Order and size

| | sprint | size | gate | why here |
|---|---|---|---|---|
| 1 | **26 — the tolerance in pixels, proxies retired** | half | S48 (built) | one criterion, one unit; makes every later hole number mean something |
| 2 | **27 — one real inpaint, end to end** | 1 | 25 (built) | two thirds of the visible mess is invented colour; only content reaches it |
| 3 | **28 — the sheet A/B** | 1 day | 23, 24 | decides a weeks-long port with a day of work |
| 4 | **29 — the meadow reframed** | small | none | may dissolve the hardest regime rather than detect it |
| 5 | **30 — the gate, rewritten** | varies | 29 | the baseline changed the question |
| 6 | **31 — diversity audit, then a pilot** | open | 29 and 30 negative | front-loads the only defence we have |

**The single most valuable next action is Sprint 27**, and the reason has not changed since S37 said it about Phase A: the
fastest way to learn something genuinely new is to look at a picture. What changed is that S44 put a number on how much
of that picture is currently invented, and S47 established that no change of representation reaches it. Sprint 26 goes
first only because it is half a sprint and it makes Sprint 27's scoring mean something.

## Not recommended, and why (updated)

- **Rewriting the renderer for splats.** S47: the benefit is 1–33 % of the hole's *edge*, the streak it targets is already
  addressed by S46, and its two risks — fattened silhouettes from single-depth sprites, and soft mattes — land exactly on
  our content (the one-texel poles needed a dedicated despeckle to survive at all, S20: recall 0.51 → 0.98).
- **Making the scene shallower.** S47 falsified this directly: at relief 0.1 against 3.2 the share of revealed area a
  splat of size 2 would close moves by at most two points, and in both directions. We already ship a bas-relief.
- **Hunting for a confidence mechanism to adopt.** Twenty papers, none has one; the 2023 survey lists it as future work.
- **Revisiting the visible-region residual or occlusion fraction as gates.** Falsified, and nearly flat by the authors'
  own table (RMSE 3.324 easy → 3.476 hard).
- **Adopting the literature's layer orderings.** Ours is exact; theirs is estimated depth compared across boundaries at
  90 % pairwise accuracy, or histogram clustering.
- **Planning around obtainable weights.** None of the five RGB-D papers states a release with a licence. What transfers is
  contracts, masking schemes, losses and data recipes.
