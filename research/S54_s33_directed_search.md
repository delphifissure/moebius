# S54 — a directed search for S33's 74 %, and what it found (2026-09-22)

## 0. The status of this note, stated first because it matters here more than usual

**This is search-level research, not a first-hand read.** This environment's network policy allows web *search* but
blocks fetching arxiv, CVF open-access, Wikipedia and author sites — I tried all four and got `EGRESS_BLOCKED` or a
dead connection. So everything below rests on search-result summaries and the quotations they surfaced, not on
papers read beginning to end.

R7 was a second-hand synthesis presented as a reading, and correcting that cost this project a full session. **This
note must not become R7.** It is a map of where to look, with the specific claims that would need checking, and it
should be treated as a list of hypotheses until the papers are in hand. Where I quote, the quotation came through a
search summary and is marked. **The way to make this first-hand is the way it was done last time: the papers
supplied as files.** The shortlist is in §6.

---

## 1. What is actually unfixed

S33 measured the troll's visible bends into three classes. After Sprint 27's cross-line labelling (S51), which
halved class 3 and barely moved class 1, the remaining artefact is dominated by **class 1**:

| class | what it is | count | wall length | median jump |
|---|---|---|---|---|
| **1 same surface, law disagrees** | both texels extrapolated along the **same axis**, rims **joined** — one visible surface, two answers | **77.2 %** | **38.8 %** | 3.3 steps |
| 2 real step | same axis, rims not joined — real, but drawn as a rubber ramp | 10.4 % | 26.1 % | 31 |
| 3 axis change | one texel along its row, one along its column | 12.3 % | 35.1 % | 25 |

**Class 1 is not an axis-choice problem.** Both texels already chose the same axis and their rims are joined; the
construction simply extrapolates each line independently and adjacent lines land on different answers. S51's
labelling could not touch it by construction, and two earlier attempts failed: S22 regularised the per-line law's
*parameters* across lines (slope median, value median, both) and S32 smoothed the *field* (2-D clamped plate per
run cluster), which was removed for making the row structure worse.

So the question this search was aimed at is narrow and specific:

> **How do you extrapolate a surface into an occluded region, line by line, so that adjacent lines agree — without
> smoothing away the real steps between surfaces?**

---

## 2. The direct hit: this is the classic stereo scanline-streaking artefact

Stereo matching by dynamic programming optimises each scanline independently, and the field's name for what that
produces is *streaking*. From the search summaries, near-verbatim:

> "Dynamic programming stereo matching can be implemented with less memory requirements by optimizing the global
> function along each scanline separately, but unfortunately this leads to **streaking artifacts**. Such limitation
> can introduce streaking artefacts in the depth map because **little or no regularisation is performed across
> scanlines**."

That is class 1, in someone else's vocabulary, as a known and named problem. **R8 concluded the corpus contained no
prior art for S33's blocker. That is true of the corpus we were given, and false of the field** — the corpus was
twenty amodal/DR/depth papers and none of them is a stereo paper. The prior art is in stereo matching, where this
exact artefact has been studied since the 1990s.

### The canonical fix: Semi-Global Matching

> "Semi-Global Matching minimizes a global cost function only in one dimension like Dynamic Programming, but the
> direction is **not oriented along scanlines**. Instead, it is performed symmetrically from **eight directions**
> towards all pixels in the image… SGM does not suffer from streaking artifacts like Dynamic Programming."

The per-direction costs are each solved by 1-D dynamic programming and then **summed** per pixel, which approximates
a 2-D MRF at 1-D cost. For us the analogue is direct: our far field runs the law along rows and columns; SGM says
run it along eight directions and combine, so no single line can decide a texel alone.

### And SGM's penalty shape is a second, separate finding — arguably the more useful one

SGM's smoothness term has two penalties, and the reason for the split maps exactly onto S33's class 1 / class 2
distinction:

> "**P1** is typically smaller than P2, to avoid over-penalising gradual disparity changes, e.g. on slanted or
> curved surfaces." … "The **constant penalty for all larger changes (i.e. independent of their size)** preserves
> discontinuities."

**Our S51 join cost does not have this shape, and the difference predicts a defect S51 actually exhibited.** S51's
pairwise term is `revealPx(v_i, v_j)` — the screen-pixel gap the two answers open — which is **monotone increasing
and unbounded** in the depth difference. So it penalises a *real step* (class 2, median jump 31 steps) far more
than a *small self-disagreement* (class 1, median 3.3), which is backwards: the real step is the thing that must
survive. S51's own note records the cost of this — it bought half the class-3 wall length "for the 11 % of
real-step wall it also costs."

**SGM's capped P2 is precisely the fix for that**, and it is a one-line change to an energy we have already built
and already tuned: cap the join cost at the reveal corresponding to the cliff tolerance, so that beyond a real
discontinuity the penalty stops growing and the solver stops trying to smooth it away.

---

## 3. The label space is the other half, and it explains why S22 failed

S51's label set is **two** per texel: the row candidate or the column candidate. The stereo literature moved past
that two decades ago.

**PatchMatch Stereo** (Bleyer, Rhemann, Rother 2011) — from the summary:

> "The implicit assumption that pixels within the support region have **constant disparity** does not hold for
> slanted surfaces and leads to a **bias towards reconstructing frontoparallel surfaces**. This work overcomes this
> bias by estimating an **individual 3D plane at each pixel**."

plus **spatial propagation**, and view/temporal propagation variants.

**Local expansion moves** (Taniai, Matsushita, Sato, Naemura; CVPR 2014 / TPAMI 2018) is the graph-cut version:

> "infers **per-pixel 3D plane labels** on a pairwise MRF that effectively combines slanted patch matching and
> **curvature regularization**" … "local expansion moves are … many α-expansions defined for **small grid
> regions**, extending traditional expansion moves by **localization and spatial propagation** … can efficiently
> infer MRF models with a **continuous label space** using randomized search" … "produces submodular moves deriving
> a subproblem optimality, helps find good **smooth piecewise linear** disparity maps, is suitable for
> parallelization."

**This explains S22's failure specifically.** S22 fitted each line's law independently and then median-filtered the
*parameters* across lines. Propagation is a different operation: you take a neighbour's plane, **re-evaluate its own
data cost at your texel**, and keep it only if it scores better. A median filter cannot do that — it has no data
term and so cannot tell a good shared plane from a bad one. The two methods look similar and are not.

For us the label would be a local **plane** (or, on a line, a slope-and-intercept) rather than a choice between two
precomputed candidates, and the propagation step is what makes adjacent lines agree *by finding that they can*,
rather than by being averaged.

---

## 4. The solver is probably not the bottleneck, and S51's own evidence says so

It would be natural to reach for graph cuts to replace S51's ICM. The search says the gap is real but modest in
practice — α-expansion "is only guaranteed to return a local minimum with respect to the moves made", though
"objective gap bounds obtained from primal-dual variants … are sometimes very close to one in practice".

More decisive is S51's own measurement: **λ is inert from 0.25 to infinity, and five structurally different seeds
converge within a few per cent.** That is the signature of an energy whose floor is being reached. Changing the
optimiser will not move a number that the optimiser is already finding.

**So the order is: fix the energy first (§2's capped penalty, §3's label space), and only then ask whether the
solver matters.** Reaching for graph cuts first would be the expensive mistake here.

---

## 5. Two incidental findings worth recording

**ORCA (2026) independently arrives at our hybrid.** From the summary: "missing regions are handled based on their
**size and structure**, with **small disocclusions repaired using RGB-D information already available** in the
reconstruction, while **generative inpainting is reserved for larger regions** that cannot be reliably recovered."
That is the reveal-thresholded hybrid S53 built and measured, published independently. It is corroboration of the
design, not of our numbers.

**3D Photography using Context-aware Layered Depth Inpainting** (Shih, Su, Kopf, Huang; CVPR 2020) states our trade
exactly: "Naïve methods either produce holes or **stretch content at disocclusions**. Color and depth inpainting
using diffusion is better, but provides a **too smooth appearance**." Their representation — a Layered Depth Image
with **explicit pixel connectivity** — is the interesting part for S33 class 2, which is a *real* step currently
drawn as rubber. Explicit connectivity is how you say "these two texels are not joined", which is the tear S33 says
class 2 should be. The learned inpainter is blocked for us; the representation idea is not.

---

## 6. What to obtain to make this first-hand

In rough order of expected value:

1. **Hirschmüller, "Stereo Processing by Semiglobal Matching and Mutual Information"** (PAMI 2008) — the P1/P2
   penalty shape and the 8/16-direction aggregation, first-hand.
2. **Taniai et al., "Continuous 3D Label Stereo Matching using Local Expansion Moves"** (TPAMI 2018) — the label
   space and propagation, with code at `github.com/t-taniai/LocalExpStereo`.
3. **Bleyer, Rhemann, Rother, "PatchMatch Stereo"** (BMVC 2011) — propagation, and the frontoparallel-bias argument.
4. **Schönberger et al., "Learning to Fuse Proposals from Multiple Scanline Optimizations in SGM"** (ECCV 2018) —
   the search summary says plain summation "is ineffective for images capturing weakly textured slanted surfaces,
   and inadequate when the individual scanline optimizations **yield inconsistent results**", which is our case
   precisely. Worth knowing what they replace summation with before we build summation.
5. **Boykov, Veksler, Zabih, "Fast Approximate Energy Minimization via Graph Cuts"** (PAMI 2001) — the α-expansion
   baseline, for §4 rather than for building.
6. **Shih et al., 3D Photography / LDI** (CVPR 2020) — for the explicit-connectivity representation.
7. **ORCA** (2026) — to check whether their size-based split threshold is derived or tuned.

A review of SGM penalty functions also surfaced twice ("A review and evaluation of penalty functions for
Semi-Global Matching"); if the P1/P2 idea survives first contact, that is where to look for the variants.

---

## 7. What this changes about R8's standing claim

R8's §"Standing" says S33's blocker "still has **no prior art in this pile**", and notes the graph-cut literature
"was never supplied and remains unchecked". Both remain literally true. What this search adds is that **the prior
art is not in the amodal literature at all — it is in stereo matching**, under the name *streaking*, and the field
has two distinct answers to it (multi-direction aggregation; per-pixel plane labels with propagation) plus a
penalty shape that our own energy is missing.

That is a better position than "no prior art", and it is worth saying plainly that the twenty-paper corpus could
not have contained it: none of those papers is about stereo.

---

## Sources

Search-level only; none of these was fetched or read first-hand (see §0).

- [Semi-global matching — Wikipedia](https://en.wikipedia.org/wiki/Semi-global_matching)
- [Learning to Fuse Proposals from Multiple Scanline Optimizations in Semi-Global Matching (ECCV 2018)](https://openaccess.thecvf.com/content_ECCV_2018/papers/Johannes_Schoenberger_Learning_to_Fuse_ECCV_2018_paper.pdf)
- [A Stereo Matching Method Based on the Dynamic Programming to Reduce the Streaking Phenomena](https://www.researchgate.net/publication/264178530_A_Stereo_Matching_Method_Based_on_the_Dynamic_Programming_to_Reduce_the_Streaking_Phenomena)
- [PatchMatch Stereo — Stereo Matching with Slanted Support Windows (BMVC 2011)](https://www.microsoft.com/en-us/research/wp-content/uploads/2011/01/PatchMatchStereo_BMVC2011_6MB.pdf)
- [Continuous 3D Label Stereo Matching using Local Expansion Moves (TPAMI 2018)](https://taniai.space/projects/stereo/) · [code](https://github.com/t-taniai/LocalExpStereo)
- [SGM-Nets: Semi-global matching with neural networks (CVPR 2017)](https://openaccess.thecvf.com/content_cvpr_2017/papers/Seki_SGM-Nets_Semi-Global_Matching_CVPR_2017_paper.pdf)
- [A review and evaluation of penalty functions for Semi-Global Matching](https://www.researchgate.net/publication/281463284_A_review_and_evaluation_of_penalty_functions_for_Semi-Global_Matching)
- [Graph cuts always find a global optimum for Potts models (with a catch)](https://arxiv.org/pdf/2011.03639)
- [3D Photography using Context-aware Layered Depth Inpainting (CVPR 2020)](https://arxiv.org/abs/2004.04727)
- [ORCA: Occlusion-Aware Refinement and Completion for Novel View Synthesis](https://arxiv.org/html/2609.17450v1)
- [Depth Completion using Piecewise Planar Model](https://arxiv.org/pdf/2012.03195)
- [Depth Map Inpainting under a Second-Order Smoothness Prior](https://link.springer.com/chapter/10.1007/978-3-642-38886-6_52)
