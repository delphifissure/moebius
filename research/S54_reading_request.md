# S54 — papers requested, to make the S33 search first-hand (2026-09-22)

`S54_s33_directed_search.md` is search-level: this environment blocks arxiv, CVF, Wikipedia and author sites, so
every claim in it came through a search summary. This is the list to make it first-hand, ordered by what it would
settle. **Tier 1 is the minimum that makes S54 safe to build on. Tier 2 is what I would want before Sprint 32.**

Two things shape the list, and both are reasons not to just grab "the stereo classics":

1. **Our problem is stereo's artefact without stereo's data term.** Stereo has a matching cost at every pixel, so
   its MRF has real evidence everywhere. Our band is *hidden* — there is no data in it at all. Our only data term
   is the extrapolation's own uncertainty (`_geoFarAxS`). So the smoothness machinery may transfer while the
   optimisation framing does not, and I need to read enough to tell which.
2. **DIBR is our actual application and I under-weighted it.** Depth-image-based rendering for 3DTV/free-viewpoint
   has been solving "holes appear when you warp a depth image sideways" since ~2004. That is literally what the
   portal does. It is a more on-target lineage than amodal completion ever was, and S54 barely touches it.

---

## Tier 1 — the six that would settle S54's specific claims

**1. Hirschmüller, "Stereo Processing by Semiglobal Matching and Mutual Information", PAMI 30(2), 2008.**
(Also the CVPR 2005 version, "Accurate and Efficient Stereo Processing by Semi-Global Matching and Mutual
Information", if the journal one is hard.)
*Settles:* the exact P1/P2 penalty structure and the aggregation recursion. S54's central actionable claim is that
S51's join cost has the wrong shape — monotone and unbounded where SGM's P2 is large but **constant** — and that
this predicts the 11% real-step damage S51 recorded. I want the formula and the stated reasoning, not a summary of
it, before changing our energy.

**2. Scharstein & Szeliski, "A Taxonomy and Evaluation of Dense Two-Frame Stereo Correspondence Algorithms",
IJCV 47, 2002.**
*Settles:* whether "streaking" means in the literature what I am assuming it means, and what the standard
taxonomy of scanline-independence artefacts is. This is the paper that named the problem space; if my mapping of
class 1 onto streaking is wrong, this is where it breaks.

**3. Bleyer, Rhemann, Rother, "PatchMatch Stereo — Stereo Matching with Slanted Support Windows", BMVC 2011.**
*Settles:* what propagation actually does, mechanically. My claim that this explains S22's failure — propagation
re-evaluates a neighbour's plane against your own data cost, a median filter cannot — is the single most useful
thing in S54 and I have it only from a summary sentence.

**4. Taniai, Matsushita, Sato, Naemura, "Continuous 3D Label Stereo Matching using Local Expansion Moves",
TPAMI 40(11), 2018.** (CVPR 2014 version: "Graph Cut Based Continuous Stereo Matching using Locally Shared
Labels". Code: github.com/t-taniai/LocalExpStereo.)
*Settles:* the per-pixel plane label space and the curvature regulariser, which is the Sprint 32 construction. Also
the only one whose code I could read if the PDF is awkward.

**5. Szeliski, Zabih, Scharstein, Veksler, Kolmogorov, Agarwala, Tappen, Rother, "A Comparative Study of Energy
Minimization Methods for Markov Random Fields with Smoothness-Based Priors", PAMI 30(6), 2008.**
*Settles:* §4 of S54, the claim that the solver is not our bottleneck. This paper measures ICM against graph cuts,
belief propagation and TRW on the same energies. S51's evidence (λ inert, five seeds converging) points the same
way, but this would confirm or kill it with published numbers — and ICM is famously the worst performer in that
study, so the claim deserves the check rather than my assertion.

**6. Zhang & Tam, "Stereoscopic image generation based on depth images for 3D TV", IEEE Trans. Broadcasting 51(2),
2005.**
*Settles:* the DIBR pre-smoothing trick — asymmetric (stronger vertical than horizontal) smoothing of the depth
map *before* warping, to shrink disocclusions at source. **This is a fundamentally different lever from anything
this project has tried**: every construction we have built fills the band after deciding it exists. This one
changes the depth map so the band is smaller. Given that our largest measured win this session was a *sharper*
depth map, a paper arguing for deliberately *blurring* it in one axis is either an important counterweight or an
instructive dead end, and I would like to know which.

---

## Tier 2 — before Sprint 32, and for the DIBR lineage I under-weighted

**7. Schönberger, Sinha, Pollefeys, "Learning to Fuse Proposals from Multiple Scanline Optimizations in
Semi-Global Matching", ECCV 2018.**
*Why:* the summary says plain summation across directions "is ineffective for images capturing weakly textured
slanted surfaces, and inadequate when the individual scanline optimizations yield inconsistent results." Our lines
disagree by construction — that is the definition of class 1 — so we may be walking into the failure case of the
fix. Worth knowing before building Sprint 31, not after.

**8. Boykov, Veksler, Zabih, "Fast Approximate Energy Minimization via Graph Cuts", PAMI 23(11), 2001.**
*Why:* α-expansion and α-β-swap, the baseline everything else is measured against. R7 and R8 both named this as
the missing literature by name; it should be in the record read rather than cited.

**9. Criminisi, Pérez, Toyama, "Region Filling and Object Removal by Exemplar-Based Image Inpainting",
IEEE TIP 13(9), 2004.**
*Why:* the confidence-and-isophote priority term. Our band fill has no notion of *what order* to fill in, and this
is the canonical answer. It is also the ancestor of the exemplar machinery InpaintFusion uses, which we read
downstream of without reading the source.

**10. Daribo & Saito, "A novel inpainting-based layered depth video for 3DTV", IEEE Trans. Broadcasting 57(2),
2011** — or Daribo & Pesquet-Popescu, "Depth-aided image inpainting for novel view synthesis", MMSP 2010.
*Why:* depth-guided exemplar inpainting specifically for disocclusions from warping. Directly our task, in our
application, and old enough to be simple enough to implement without a GPU.

**11. Ndjiki-Nya, Köppel, Doshkov, Lakshman, Merkle, Müller, Wiegand, "Depth image-based rendering with advanced
texture synthesis for 3-D video", IEEE Trans. Multimedia 13(3), 2011.**
*Why:* the other main DIBR hole-filling line, with a background-favouring rule. Between this and Daribo I should
be able to see what the DIBR field settled on, which is the question S54 never asked.

**12. Shade, Gortler, He, Szeliski, "Layered Depth Images", SIGGRAPH 1998.**
*Why:* the original LDI. Our plate-1/plate-2 is an LDI in all but name, and class 2 (a real step drawn as rubber
instead of a tear) is a connectivity question this paper defines the vocabulary for.

**13. Shih, Su, Kopf, Huang, "3D Photography using Context-aware Layered Depth Inpainting", CVPR 2020.**
*Why:* LDI with *explicit pixel connectivity*, which is the representation for saying "these two texels are not
joined". The learned inpainter is blocked for us; the representation is not.

---

## Tier 3 — if they are easy, not if they are not

**14. Sinha, Steedly, Szeliski, "Piecewise Planar Stereo for Image-based Rendering", ICCV 2009** — plane extraction
and assignment, for the "fit one surface to the rim, not one line each" framing.

**15. Gallup, Frahm, Pollefeys, "Piecewise Planar and Non-Planar Stereo for Urban Scene Reconstruction", CVPR
2010** — how to decide *where* the planar assumption applies, which is our thin-evidence rule in another guise.

**16. Bornemann & März, "Fast Image Inpainting Based on Coherence Transport", J. Math. Imaging Vis. 28, 2007** —
R4 cites it; it was never read here. The direction-of-transport idea is the closest thing to "extrapolate along
the surface" in the inpainting literature.

**17. Sun, Yuan, Jia, Shum, "Image Completion with Structure Propagation", SIGGRAPH 2005** — user-guided structure
curves first, texture second. Our rim law already knows where the structure is, which makes the manual half free.

**18. Hirschmüller & Scharstein, "Evaluation of Stereo Matching Costs on Images with Radiometric Differences",
PAMI 31(9), 2009** — only if the P1/P2 question turns into a "which cost" question.

**19. "A review and evaluation of penalty functions for Semi-Global Matching"** (surfaced twice in search; I do not
have a confident citation — possibly Hermann & Klette, or an ISPRS paper). *Why:* if the capped-penalty idea
survives Tier 1, this is where the variants are.

**20. ORCA: "Occlusion-Aware Refinement and Completion for Novel View Synthesis"** (2026, arxiv 2609.17450) —
*Why:* it independently arrives at our reveal-thresholded hybrid. I want to know whether their size threshold is
**derived or tuned**, because ours is derived and that is the part worth defending.

---

## What I will do with them

Tier 1 → rewrite S54 as a first-hand note, the way R8 was written, with quotations and numbers checked against the
source, and mark every claim that the reading changed.

Then, in order: cap the join cost (Sprint 30, needs #1), decide whether multi-direction aggregation is the right
construction or whether #7 says it fails in our regime (Sprint 31), and only then the plane-label rebuild
(Sprint 32, needs #3 and #4).

**If only one can be obtained, make it #1.** It is the one that changes a line of code we have already written and
tuned, and it has a specific prediction attached — that capping the penalty keeps S51's class-3 halving while
removing the 11% real-step damage — which is falsifiable in one bake.
