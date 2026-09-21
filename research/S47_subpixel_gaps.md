# S47 — The sub-pixel gap measurement: splats shave the edge of the hole, they do not fill it (2026-09-21)

The user proposed replacing the displaced mesh with sized splats: one square splat per source texel, sized `1 + reveal` so it
covers exactly its own pixel at rest and grows only as much as the gap its own cell opens. The claim is that this makes
streaks structurally impossible, and that the splat size, the cliff criterion and the tear threshold become one number.

The mechanism is right. What the proposal cannot say is **how much of our band a splat would actually close**, and that is
what decides whether the rewrite is worth it. Measured here from the depth map and the app's own parallax law, with no
renderer written. Instrument: `bleed/subpixel.py`.

## The quantity

For two adjacent texels at depths giving portal-relative depths `Z1, Z2`, the gap that opens between them when the eye moves
to the envelope rim is

    reveal = |ex| · | Z_far/(D+Z_far) − Z_near/(D+Z_near) | · pxPerWorld

so their spacing goes from 1 texel to `1 + reveal`. A splat of size `1 + T` closes every gap below T and shortens every gap
above T by exactly T. That is the whole proposal, expressed as one number per cell.

## 1. The kit's depth law is not the app's, and it had to be controlled for

The truth kit renders at `outer = 0.64 m` with `D = 0.2`, a relief of **3.2**. The app ships `outer = 0.02` at the same
distance, a relief of **0.1** — thirty-two times shallower. Since this measurement needs only the depth map and the law, the
law can be overridden without re-rendering, which separates "the kit's scenes are hard" from "the kit's law is aggressive".

**The relief turns out to matter very little.** Share of the revealed area that a splat of size 2 would close, horizontal
axis at the rim:

| | kit's own law (relief 3.2) | the app's law (relief 0.1) |
|---|---|---|
| L1 | 14.95% | 16.54% |
| L5 | 2.67% | 2.23% |
| L6 | 1.13% | 0.79% |
| L7 | 7.19% | 4.24% |
| L8 | 4.47% | 2.48% |
| L9 | 4.97% | 3.85% |

**This falsifies the document's second recommendation.** It argued that a 0.5 m scene is too aggressive and that a painting
wants to be a bas-relief. We already ship a bas-relief, at relief 0.1, and making the scene shallower does not change the
shape of the problem. That dial is already at the conservative end.

## 2. What does matter is the depth map, and the effect is large

The same measurement on the troll, a real photograph with a Depth Anything estimate, against the kit's exact ray-traced
geometry at the identical depth law:

| | cells opening ≤ 1 px | area from those cells |
|---|---|---|
| exact geometry (L5–L9) | 96–99% | **0.6 – 4.1%** |
| exact geometry (L1, dense leaves) | 97.5% | 15.0% |
| **estimated depth (troll)** | 84.0% | **29.8%** |

An estimated depth map is smooth: it has gradual gradients where the real scene has cliffs. So on a photograph a large share
of the reveal comes from slopes that open sub-pixel gaps, and on exact geometry almost all of it comes from genuine
discontinuities. **The kit systematically understates what splats would buy on the actual product, and the difference is the
depth estimator, not the scene.**

## 3. The number that decides it

A torn mesh and a splat cloud are **identical everywhere except the cells above T**. Below T the mesh keeps the quad and
covers the gap exactly; the splat covers it too. Above T the mesh tears and leaves the whole reveal open; the splat leaves
`reveal − T`. So the only thing splats buy is **T pixels per torn cell**.

The first version of this table credited splats with the whole sub-T area as well. That double-counts, because a mesh is not
torn there. Corrected, and bracketed by two denominators because the truth is between them:

| | T = 1 | T = 2 | T = 4 |
|---|---|---|---|
| L1 | 5.0 – 14.2% | 4.4 – 12.3% | 5.4 – 15.2% |
| L5 | 1.2 – 8.5% | 1.5 – 10.5% | 2.7 – 18.4% |
| L6 | 0.7 – 23.9% | 1.0 – 30.9% | 1.6 – 51.4% |
| L7 | 2.6 – 14.5% | 1.9 – 10.7% | 1.7 – 9.4% |
| L8 | 2.0 – 20.4% | 1.7 – 17.4% | 2.1 – 20.8% |
| L9 | 2.6 – 20.9% | 2.3 – 18.8% | 2.9 – 24.0% |
| **troll** | **17.0 – 33.0%** | 10.5 – 20.4% | 7.0 – 13.5% |

**The bracket, stated honestly.** The low figure divides by the summed per-cell reveal, which overcounts cliffs badly: it
ignores occlusion and the frame edge, and totals 1.9× to 32× the band the bake actually produces. The high figure divides by
that measured band, which is the real revealed set but attributes all of it to the cells this model counts. The truth is
between, nearer the high end for shallow scenes where the two agree best — the troll's ratio is 1.94, the closest in the set.

## 4. What this says

**Splats close somewhere between a twentieth and a third of the hole a torn mesh leaves. They do not fill it.** On the one
case that is the actual product — a photograph with an estimated depth map — the figure is 13 to 33%, which is real but is
the *edge* of the hole, not its content.

Three further things fall out.

1. **Splats and a torn mesh are equivalent on the smooth part**, which is 84% of cells on a photograph and 96–99% on exact
   geometry. There the mesh interpolates exactly and a square splat approximates. The mesh is not worse there; it is
   slightly better.
2. **The streak problem is already solved by S46** without changing representation. The near-extent rule gives torn-mesh
   behaviour at cliffs and keeps the covering sliver, and it was measured the same day.
3. **What splats genuinely buy is the structural guarantee** that a ramp can never be kept by accident, plus the collapse of
   four thresholds into one. That is worth something for the codebase's health. It is not worth it for pixels.

Set against that: point sprites write one depth across the whole sprite, so silhouettes fatten by up to T/2, and our asset
class contains the one-texel poles that needed a dedicated despeckle to survive at all (S20, recall 0.51 → 0.98). And the
soft-edge matting problem the proposal defers to a later phase is first-order on paintings, whose silhouettes are soft over
several pixels rather than one.

## Recommendation

**Do not rewrite the renderer for this.** The measurement does not support it: the benefit is single digits to a third of
the hole's edge, the streak it targets is already addressable, and the two risks land exactly on our content.

**What the measurement does support**, and what I would take from the proposal regardless of representation:

- **The diagnostic assertion.** No pixel should be both unpainted and surrounded by painted neighbours closer than T. That
  separates "a gap I should have covered" from "a genuine disocclusion", mechanically, and we cannot make that distinction
  today under any representation.
- **The reveal-per-cell field itself.** It is cheap, it is computed here, and it is a better cliff criterion than anything
  currently in the bake because it is expressed in the units the artefact appears in — screen pixels at the rim.

And the standing conclusion is unchanged by all of this: at 45° the ramps are 3.7% of the picture and the invented colour is
10.5%, so **two thirds of what reads as messy is the placeholder colour**, which no representation change reaches.
