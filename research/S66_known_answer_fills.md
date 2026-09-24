# S66 — fills scored against a known answer on real pictures: reveal-shaped holes and the beyond-the-frame strip

Date: 2026-09-24. Two instruments that turn our own pictures into tests with ground truth (the Geometric Reciprocity /
Invisible Stitch idea, S63c), both under the app's **default** volume (outer 0.02, inner 0.04, pn 0.5, D 0.2 —
moebius.js L2959–2960) and scored **inside the hole only**: MAE, masked LPIPS on the hole's bounding box, and the
gradient-energy ratio fill / truth inside the hole ("detail"; < 1 = smoother than the truth — blur must not win).
Scripts: `harness/grt_eval.py`, `harness/outpaint_eval.py`. Pictures: the starwatcher, the nine new pictures and
Shishkin (outputs in the session scratchpad; photographs of people are not committed).

*(A first run used outer = 0.24 by mistake — a truth-kit scene's depth, six times the app's — and is superseded.)*

## 1. Reveal-shaped holes (round trip)

Warp the picture with its own depth to a side view at ±θ (the app's shift law, both directions); the source pixels the
nearer content hides from that view are the hole. A pixel counts as hidden only when the texel that wins its cell is
nearer by more than the join ratio 1.05 (a receding surface that merely compresses is not a hole). The truth is the
picture itself. The hole has the shape of a real reveal, on the background side of every silhouette.

Painters: **LaMa**; **pp** = push-pull (Solh & AlRegib's hierarchical fill, 5×5 Gaussian over known pixels, pyramid to
no holes); **pp_far** = the same seeded only from pixels on the hole's own side (a known pixel nearer than the hole
component's nearest by more than the join ratio is excluded).

| θ | pictures | LaMa LPIPS / MAE / detail | pp | pp_far | LaMa best LPIPS |
|---|---|---|---|---|---|
| 20° | 10 | **0.021** / 0.052 / 1.03 | 0.045 / 0.073 / 0.64 | 0.040 / 0.072 / 0.64 | 10 / 10 |
| 45° | 10 | **0.030** / 0.045 / 1.09 | 0.056 / 0.057 / 0.64 | 0.050 / 0.054 / 0.59 | 8 / 10 |

(medians; hole sizes 0.7–14 % of the picture at 20°, 1.4–20 % at 45°; beach has no depth step that passes the join
test — an open scene — so it has no hole to score.)

- **LaMa wins, with the truth's own detail** (ratio ≈ 1). Push-pull is about twice the LPIPS and carries about 60 % of
  the true detail — the "wash" character, measured.
- **Seeding from the far side only helps push-pull a little** (LPIPS 0.045 → 0.040 at 20°) and never hurts.
- LaMa's two losses at 45° are lamppost (a 1.4 % hole where every painter is under 0.003 LPIPS) and dandelion (0.084
  against 0.082, a near tie).
- For the project's split — *plausible, clean wash for colour, then SD* — this says the wash is honestly a wash (smooth,
  no foreground bleed, 60 % of the detail) and that the texture must come from the painter; it does not argue for
  shipping LaMa as the wash, because the wash's job is to be a clean prior for SD, not to be the final colour.

## 2. The strip beyond the frame (outpaint)

Take the picture's outer ring as "beyond the frame", keep the inner rectangle as the photograph, fill the ring, score
against the true border. The ring is as wide as the strip the app needs beyond its frame at θ: the largest shift at θ
under the app law (σ at 45° × tan θ; S64). A ring wider than a quarter of the short side is reported as infeasible (too
little photograph left) rather than run.

At 20°: rings of 104–119 px on a 768-px picture, feasible on 8 of 11 pictures (wanderer, fence and lamppost have
pop-out content that needs 155 px). At 45°: 284–427 px, infeasible on all — at the default volume the strip at 45° is
already 37–56 % of the picture's width, i.e. the far view past ~45° is mostly outpaint (S64's θ*).

| painter | LPIPS | MAE | detail | |
|---|---|---|---|---|
| **clamp** (what the app shows today: the edge stretched) | 0.426 | 0.140 | 0.43 | streaks |
| pp (push-pull) | 0.454 | 0.130 | 0.05 | a blur |
| **LaMa** | **0.310** | **0.118** | 0.65 | plausible, murky, repeats edge detail |
| SD + depth ControlNet | *queued* | | | |

(medians over 8 pictures; LaMa beats the stretch on LPIPS on 8 / 8.)

**Reading.** Today's beyond-the-frame content is the stretched edge, and it is the worst of the three on the perceptual
score. Any painter is an improvement; LaMa is a floor for SD to beat. The SD arm uses the pipeline of `sd_return.py`
with one prompt for every picture and the clamp-extended depth that the bundle's `plane_out_depth16` carries — a flat
continuation, which is itself a thing to fix (the margin should take the far-side depth rule the holes use).

## What this does not cover

- These holes are the reveal's **mirror image** (the visible side of the edge, where truth exists). The real band lies
  under the foreground; the shape is the same family, the content statistics may differ.
- One seed and one prompt for SD (no per-picture choice), by rule.
