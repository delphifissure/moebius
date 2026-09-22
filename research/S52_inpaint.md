# S52 — Sprint 28: one real inpaint, end to end (2026-09-22)

Three sprints established where the visible defect is and is not. S47 measured that at 45° the ramps are 3.7 % of the
picture and the invented colour 10.5 %, so **two thirds of what reads as messy is the placeholder colour**. S50
decomposed a frame by class and put the band at ~16 % of the actual picture, with the cliff rules Sprint 26 swept worth
~0.8 points of it. S51 then built a construction that cut the plate's visible wall length by 21 % and **could not be
seen at all** underneath that wash.

So the band's colour is the thing, and this is the first time the project puts real content in it.

## The arms are PACO's taxonomy, applied to our task

PACO (2406.07706), read first-hand for the R7 errata, tried three strategies with the ground-truth amodal mask:

| | strategy | PACO's finding |
|---|---|---|
| (a) | inpaint the occluded region alone | "ambiguity, regarding which object the missing area belongs to" — the model completes the **occluder** |
| (b) | replace the occluder with uniform grey | "partly influenced by the replacement color" |
| (c) | extend the mask over the whole occluder | "may create unexpected new objects" — **and the strategy they themselves use for every comparison** |

**Their task is not ours and the difference runs our way.** Every PACO failure is about completing the *occludee* — the
album behind the teddy bear. Our band is the **background behind** the occluder, so (c) *is* our task, and "creates
unexpected new objects" is their objection from wanting the album back.

- **A** — band mask on `plane_color_occluder_removed.png`. Sprint 25's design: a harmonic continuation rather than
  grey, which is better than (b) and is supported by PACO's own finding that the fill colour leaks.
- **B** — band ∪ occluder mask, occluder removed. **PACO (c)**, added as an arm by the errata rather than taken as a
  default.
- **C** — band mask on the raw wash, occluder left in. **PACO (a)**, the control that should complete the occluder.

Inpainter: **LaMa** (big-lama), feed-forward, CPU, ~7 s per arm at 851×1023. It is one of the baselines PACO compares
against (Suvorov *et al.* 2022), so the comparison is direct rather than analogical. No GPU in this environment and
5 GB of disk, which ruled out diffusion inpainting; LaMa is 196 MB.

**All three respect the mask exactly: 0 pixels changed outside it**, so the contract's "colour on the inpaint mask and
nowhere else" holds without the app enforcing it.

## The result: the first visible change in three sprints

Reimported onto the **live plate** through the Sprint 25 return path (`window._importPlaneReturn`, 347 177 texels) and
rendered at the poses the artefact appears at, with the wash as the control.

| pose | pixels differing | mean abs difference |
|---|---|---|
| 45° horizontal | 4.24 % | 85.1 |
| down-left corner | 4.84 % | 66.3 |

At 45° the band goes from a flat streaked column to **textured, continuous scene content**. Sprints 26 and 27 measured
real improvements in the plate's geometry and changed nothing the eye could find; this changes the picture at a glance.

**What the end-to-end proves independently of LaMa's quality:** the Sprint 25 return path works on a real model's
output. Export → inpaint → reimport → render, with no manual step, colour written on the mask and nowhere else.

## Caveats, stated rather than discovered later

1. **LaMa invents a bright speckled patch at the corner** that reads as a blemish. That is PACO's "creates unexpected
   new objects" appearing on our task after all — their pessimism is not entirely inapplicable.
2. **LaMa is blur-prone.** The fill is smooth rather than detailed. For a background band in motion, plausible-and-smooth
   beats streaky-and-wrong, but it is not correct content.
3. **The occluder-removed seed is already better than the wash** before any model runs — the harmonic continuation is
   smooth where the wash is streaked. Sprint 25 built it as *context for a model* and it turns out to be a better
   fallback than what ships.
4. **B's extra region is discarded on reimport**, correctly: the return path writes colour on the band only, and the
   foreground covers the occluder's footprint. So the A-against-B comparison isolates what a larger mask does to the
   **band's own content**, which is the claim being tested.

<!--ARMS-->

<!--DEPTH-->
