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

## The three arms, rendered: the strategy matters half as much as the decision

| arm | differs from the wash | mean abs difference |
|---|---|---|
| A — band mask, occluder removed | 4.24 % | 85.1 |
| B — band + occluder (PACO c) | 4.37 % | 87.8 |
| C — band on the raw wash (PACO a) | 4.45 % | 88.7 |

And from **each other**:

| | differ | mean abs |
|---|---|---|
| A vs B | 2.35 % | 22.9 |
| A vs C | 2.74 % | 27.1 |
| B vs C | 2.47 % | 26.8 |

**Each arm differs from the wash about twice as much as the arms differ from one another.** PACO's three strategies do
produce visibly different results on our data — they are not equivalent — but **the choice of strategy matters roughly
half as much as the choice to inpaint at all**, and none of them fails the way PACO's figures do. That is consistent
with the task mismatch recorded in the R7 errata: their distinctions are about recovering the *occludee*, and we do not
want the occludee.

On this evidence there is no reason to prefer B (PACO's own choice) over A (what Sprint 25 built). The errata's
recommendation to make (c) an arm was right; the arm does not win.

## The depth half is blocked, and the reason is a wrong model — ours, not the model's

`harness/s52_depth.py` runs Amodal-DAV2 on the bundle and emits the contract's absolute and gradient encodings. It
produced a return. **The return is worthless, and a guard in the script says so:**

```
median |model - observed occluder|   0.0832
median |model - plane background|    0.2607     <- three times further
!! THE PREDICTION TRACKS THE OCCLUDER, NOT THE BACKGROUND
```

The prediction is three times closer to the **occluder's own depth** than to the background the band needs. I first
suspected the guide mask — the band rather than the occluder — and re-ran with the occluder. **Same verdict.** So it is
not the mask, it is the model's task. From the two papers, in their own words:

> **Amodal Depth Anything** (2412.02336): *"predicting the depth of **invisible parts of objects**"* — the amodal depth
> of the *target object*, including the parts hidden behind an occluder.
>
> **Counterfactual Depth** (1909.00915): *"a depth map that describes the scene **when a masked object is removed** — we
> call this 'counterfactual depth'… the depth you would see if an object had been removed."*

**Counterfactual Depth is our task. Amodal-DAV2 is a different one.** It answers "how deep is the troll's hidden arm";
we are asking "what is the depth of the cave behind the troll". No guide mask converts one into the other.

**This is bigger than Sprint 28, and it is recorded rather than quietly parked.** S39, S40 and S43 all used Amodal-DAV2
as *the learned prior for band depth* and scored it against band truth. If the model predicts the occludee's amodal
depth, then those comparisons were not measuring what they were captioned as measuring. That does not automatically
invalidate their rankings — on kit scenes the occluder and the surface behind it are sometimes close, and S43's
headline was that **doing nothing often beat the model anyway**, which is what one would expect from a model answering
a different question. But the premise needs re-examination before any of those numbers is quoted again.

**What Sprint 28 can and cannot deliver.** Colour: delivered, and it is a clear visible win. Depth: blocked on a model
we do not have — Counterfactual Depth is a 2019 paper with no cached weights here, and this environment has no GPU. The
shipped plane far field stays, which is what arm A already renders. The contract itself is not implicated: S48 verified
the return path against a corrupted return and it held; what failed is the supplier, not the pipe.
