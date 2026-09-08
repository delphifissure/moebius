# R3 — Sky and horizon: what the literature settles, and what follows for the portal

Written 2026-09-08 after the user's decision that sky reveals count as content. Purpose: decide the
sky/horizon question from the literature and the geometry rather than by asking, and set the
truth-kit accounting accordingly. Network note: in this environment arxiv.org, openaccess.thecvf.com,
ecva.net, github.io and huggingface.co are blocked by the egress proxy, so every citation below is
backed by the search layer's excerpts of the paper, not by my reading of the PDF. Where a claim is
from memory of a paper I could not re-read it is marked (memory).

## 1. What the field does with sky

1. **Sky is a geometric class, not a depth value.** Hoiem, Efros & Hebert, *Automatic Photo Pop-up*,
   SIGGRAPH 2005: a single image is labelled into ground / vertical / sky, the model is "cut and
   folded" from those labels, and the sky is not given geometry at all — it is the class that has none
   (verified excerpt: "labels regions of the input image into coarse categories: 'ground', 'sky',
   and 'vertical'"). The horizon line separates ground from sky and fixes the ground plane (memory).
   Tour Into the Picture (Horry, Anjyo & Arai, SIGGRAPH 1997) is the same idea by hand: a vanishing
   point, five planes, a rear billboard.
2. **Depth estimators put sky at infinity by segmentation, not by regression.** Depth Anything
   (Yang et al., CVPR 2024; verified excerpt): "a pre-trained semantic segmentation model is applied
   to detect the sky region, and its disparity value is set as 0 (farthest)". Depth Anything V2
   (verified excerpt): predicting affine-invariant *disparity* "allows for better representation of
   distant regions (e.g., sky) using very small values", whereas depth-space models "must predict very
   large depth values for these areas, introducing numerical difficulties … resulting in poorer
   representations of distant regions". Marigold (depth-space, [0,1]) "struggles with sky regions"
   (verified excerpt). Depth Pro outputs metric depth in metres; its handling of sky is not stated in
   the README and I could not read the paper (unverified).
3. **View synthesis systems that survive large motion treat sky as the plane at infinity.**
   InfiniteNature-Zero (Li et al., ECCV 2022; verified excerpt): "the sky … should change much more
   slowly than the foreground content since the sky is at infinity"; monocular depth "can be
   inaccurate in sky regions, leading to sky contents to quickly approach the camera in an unrealistic
   manner"; the fix determines "soft sky masks" from segmentation plus predicted disparity and
   corrects sky texture and disparity "by alpha blending the homography-warped sky content from the
   starting view (warped according to the camera rotation's effect on the plane at infinity)". The
   infinite homography H∞ = K R K⁻¹ depends on rotation only (verified excerpt), which is the
   textbook statement that content at infinity has zero translational parallax in *angle*.
   Sky-replacement work uses the same fact to warp a skybox template (Castle in the Sky, verified
   excerpt).
4. **The single-image 3D-photo line (Shih et al. CVPR 2020; Kopf et al. SIGGRAPH 2020; SLIDE ICCV
   2021) has no special sky model** that the search layer could surface; they inherit the estimator's
   far value and inpaint it like any background (unverified beyond absence of evidence — I could not
   read the PDFs).

Read together: the settled practice is (a) segment sky, (b) place it at infinity (disparity 0), (c)
render it by the rotation-only law, (d) treat the horizon as the ground/sky boundary that fixes the
ground plane. Nothing in the literature treats sky as a surface at the far end of a finite volume.

## 2. What that means for a head-tracked window (derived, no constants)

Window W×H at z = 0, eye at (e, D). A finite point at depth z < 0 behind the window appears on the
window at x = x₀ + e·z/(D − z) (the app's law, CODEMAP §3). As z → −∞ the coefficient → −1: content at
infinity moves across the window by exactly **−e** (window units), independent of D. So:

- **Sky parallax is a property of the head displacement alone**, not of the dolly distance and not of
  any depth volume. Under the dolly convention actually implemented (constant e in metres, CODEMAP
  §15) the sky's window motion is the same at every focal length — consistent with H∞ being
  translation-free in angle.
- **A finite far plane under-moves the sky by outer/(D + outer).** The app's law maps the farthest
  depth to z = −outer. At the app defaults (outer 0.02, D 0.2) sky moves at 9 % of its physical rate;
  at the truth-kit rooms' outer (0.128) at 39 %; at S15's outer (8.64 m, the true scene depth) at
  98 %. On a real photograph with an estimator's far value mapped linearly into a small volume, the
  hills and the sky move together and the whole picture reads as a relief, which is the "glued to the
  sky" look. This is the mechanism behind R1's A1 recommendation (map in disparity space): with
  z = −k/d the estimator's sky (d = 0) lands at infinity by construction and needs no volume constant.
- **How much rest-frustum sky survives at an off-axis eye** is closed-form for a rectangular window
  and pure translation: the sky directions the rest eye sees through the window form a rectangle of
  the same angular size; at eye e that rectangle is displaced by e on the window, so the surviving
  fraction is max(0, 1 − |eₓ|/W) · max(0, 1 − |e_y|/H). At the app's 45° cone rim
  (e = D·tan 45° = 0.2 > W = 0.16) it is **zero**: every sky pixel in the window is a direction the
  photograph never saw. At 22° it is 0.49, at 5.6° 0.88. Sky reveals *behind objects* therefore matter
  at small angles, and sky *outpaint* is the whole sky at large angles. The outpaint strip a bake must
  hold for sky is e_max per side in window units, i.e. D·tan θ_max / W = 1.25 window widths at 45° —
  wider than for any finite surface (a surface at depth d needs e·d/(D + d), always less than e).
- **What lies behind a vertical object is decided by the horizon**, not by a global far field. Below
  the horizon the far side is the ground plane continued (Hoiem's ground class); above it, sky at
  infinity. This is exactly S15's failure in S1 §5: the far-field membrane is anchored at the far
  rims, which on an open scene are sky, so the fill behind the tree and the post lands at sky depth
  (3 m error on an 8.6 m scene). A class-aware far side (ground below the horizon, sky above) is the
  literature's answer and needs no tuned constant; the horizon comes from a single-image estimator
  (Workman, Zhai & Jacobs, *Horizon Lines in the Wild*, BMVC 2016 / DeepHorizon; verified excerpt)
  or, for a metric estimator with focal length, from the ground plane's vanishing line.

## 3. Decisions (inferred from §1–§2; recorded, not asked)

- **D1 Sky is content and it is at infinity.** The truth kit now scores it (class 7 `sky_reveal`,
  §4). In the app it must become its own layer: a direction-indexed sky texture (the photograph's sky
  region plus an outpainted margin), rendered with x = x₀ − e, never through the depth volume.
  Source of the mask: a semantic segmentation model, as Depth Anything does internally; the
  estimator's own sky value is not a substitute (it is a regressed number, not a class).
- **D2 The far side of a vertical object is class-aware.** Ground below the horizon, sky above,
  another object where the rims say so. The far-field membrane keeps its role for room scenes (far
  rim = back wall) and is anchored only at non-sky rims on open scenes.
- **D3 Sky outpaint is a first-class demand.** At the shipped cone every sky pixel off-axis is
  new-direction sky; the bake (and later SD) must produce a sky margin of e_max per side. Until SD
  exists the margin is a continuation of the photograph's sky (InfiniteNature-Zero blends the warped
  start-view sky; a gradient continuation is the zero-parameter version).
- **D4 The second pass on sky/horizon is folded into the quick-bake sprint, not deferred.** The
  demand construction that replaces the fold tear needs the class of the far side (D2) and the sky
  layer (D1) to place its fills; doing the geometry first and the sky later would rebuild the same
  membrane twice. Envelope work for the sky is D3 and is closed-form.
- **D5 The depth law.** Mapping the estimator in disparity space (R1 A1) is what makes D1 free; the
  present linear volume cannot express infinity at any setting of `outerVolumeDepth`. This is a
  geometry change to a default and stays behind a flag until the user's live pass (standing rule).

## 4. Truth-kit accounting (implemented in this pass)

- `scope.py`: display class 6 = sky the photograph already shows in that direction (the parallel ray
  from the rest eye passes the window and hits nothing); class 7 `sky_reveal` = sky the viewer sees
  that the photograph does not (the parallel ray from the rest eye hits something, i.e. the sky was
  behind a hill or a tree at rest); sky beside the rest frustum stays class 1 outpaint like any
  surface. The rest atlas gains a sky layer: in-frame rest pixels whose ray escapes after ≥ 1 hit,
  visible from an envelope eye iff the parallel ray from that eye passes the window and hits nothing
  (sky at infinity ⇒ its identity is the direction).
- `check_app_band.py`: those sky-layer texels count as hidden truth; `recall_sky_reveal` reported.
  Their depth error in metres is undefined and excluded.
- Smoke test (S15, 200 px, eyes 0/±45°): at rest 0.289 of the display is sky; at ±45° sky reveal is
  0.000 and outpaint 0.70–0.72, as the closed form predicts (e = 0.2 > W). The env45 and full
  envelopes for S15 are rerun with the new classes; numbers go into S1 §5/§5b when they land.

## Sources (search-layer excerpts)

- Hoiem, Efros, Hebert, Automatic Photo Pop-up, SIGGRAPH 2005 — https://www.ri.cmu.edu/publications/automatic-photo-pop-up/
- Horry, Anjyo, Arai, Tour Into the Picture, SIGGRAPH 1997 — https://dl.acm.org/doi/10.1145/258734.258854
- Yang et al., Depth Anything, CVPR 2024 — https://arxiv.org/html/2401.10891v2 ; Depth Anything V2 — https://arxiv.org/html/2406.09414v1
- Li et al., InfiniteNature-Zero, ECCV 2022 — https://arxiv.org/pdf/2207.11148 ; Infinite Nature — https://arxiv.org/pdf/2012.09855
- Castle in the Sky (sky replacement via plane-at-infinity warp) — https://arxiv.org/pdf/2010.11800
- Workman, Zhai, Jacobs, Horizon Lines in the Wild, BMVC 2016 — https://arxiv.org/abs/1604.02129
- Shih et al., 3D Photography using Context-aware Layered Depth Inpainting, CVPR 2020 — https://arxiv.org/abs/2004.04727
- Kopf et al., One Shot 3D Photography, SIGGRAPH 2020 — https://facebookresearch.github.io/one_shot_3d_photography/
- Jampani et al., SLIDE, ICCV 2021 — https://arxiv.org/abs/2109.01068
- Marigold (sky limitation) — https://arxiv.org/html/2505.09358v1 ; Depth Pro README — https://github.com/apple/ml-depth-pro
