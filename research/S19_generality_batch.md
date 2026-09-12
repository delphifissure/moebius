# S19 — generality: the plane recipe on the six other pictures in the repo (2026-09-12)

The law was developed on one photograph (the troll) and eight synthetic scenes. The user asked for it to be run on the
pictures already in the app repo: **bristlecone** (`assets/`), **octopus** (`assets/`), **room** (`roomImg1.png`, a
sunflower field), **silverwarrior**, **starwatcher**, and the **vermeer** milkmaid (no depth in the repo). Each has a
repo depth map except the vermeer. Inputs, scripts, the table and the sheets: `research/s19/`; the inputs also in the app
repo under `harness/batchB/` (commits `d2f813c`, `bdf6ffc`).

## 1. Arms and method

- **Depth.** DA3-Mono-Large (the S8 choice) run in-session on each original picture (`process_res` 1008, upper-bound
  resize, 12–22 s each on CPU); the **working size is DA3's processed size** (1008 on the long side: 1008×672, 1008×1008,
  1008×700, 896×1008 for the small vermeer, which DA3 upsamples), so the depth map is never resampled. The colour and the
  repo's 8-bit map are resampled to that size (Lanczos). A first attempt at a 1280-px working size with the depth
  upsampled bilinearly was thrown away: on a piecewise-linear map more than half the second differences are exactly zero,
  so the S9 noise estimator read σ = 0 by construction.
- **Arms per picture.** `da3` (DA3 16-bit, the pipeline as it is), `da3f` (the same with `window._visStep = 1`, a new
  harness flag that **forces** the S10 visible-step floor regardless of the σ gate), `repo8` (the repo's 8-bit map),
  `da3sky` (DA3 with the sky-at-infinity option, bristlecone and starwatcher only), and `repo8inv` for bristlecone (see §3).
- **Recipe.** The panel's plane bake as `bakePlate` runs it: `_tearLaw=rim, _farRule=plane`, margin = picture, tier 35°,
  seams stretched, wash fill, sky off unless the arm says so. Probe dumps by `a257_probe.js`; angle shots by `ui_path.js`
  at eye offsets 0.05, 0.1, 0.2 m and (0.301, 0.068) m, (0.26, 0.088) m — the user's drag route, 14° to 56° of head angle.
- **Measures** (no truth exists for pictures): band and carriers as % of the plate, far-side texels, thin candidates,
  layer-2 texels, band by first-uncover tier, plate triangles torn, carrier–carrier seams (`seam_audit.py` at the arm's
  effective quantum), the S5 wash check (**clones must be 0**), and **interior holes on the path** — alpha-0 pixels inside
  the picture's rest rectangle whose component does not touch the rectangle's border (`b_holes.py`; the border-connected
  ones are the frame's own edge uncovering beyond-frame space, which margin = picture leaves open on purpose).

## 2. The table (from `s19/b_table.md`; holes per offset 0.05 / 0.1 / 0.2 / 0.301,0.068 / 0.26,0.088 m)

| picture | arm | band % | carriers % | layer 2 | seams | torn | clones colour / final | interior holes on the path | q_eff |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| bristlecone | **da3** | 14.9 | 16.4 | 27 690 | 9 434 | 22 213 | 0 / 0 | 28 / 26 / 8 / 51 / 28 | grid (σ = 0) |
| bristlecone | da3f | 15.0 | 16.5 | 19 959 | 10 329 | 23 881 | 0 / 0 | 21 / 25 / 16 / 48 / 76 | 1/k |
| bristlecone | repo8 | 73.6 | 77.2 | 65 112 | 42 889 | 97 553 | 219 / 0 | 53 / 18 / 11 / 63 / 62 | 1/255 |
| bristlecone | repo8inv | 45.1 | 48.9 | 108 292 | 32 137 | 72 174 | 127 / 0 | 56 / 119 / 462 / 407 / 395 | 1/255 |
| bristlecone | da3sky | 15.0 | 16.6 | 27 567 | 9 556 | 25 836 | 0 / 0 | 0 / 0 / 206 / 90 / 46 | grid |
| octopus | **da3** | 7.5 | 10.4 | 17 523 | 6 679 | 24 853 | 0 / 0 | 26 / 35 / 73 / 103 / 66 | 1/k |
| octopus | da3f | = da3 (σ > 0: the floor was already on) | | | | | | | |
| octopus | repo8 | 38.0 | 45.5 | 43 790 | 36 934 | 123 600 | 3 / 0 | 8 / 124 / 299 / 634 / 703 | 1/255 |
| room | **da3** | 21.3 | 27.7 | 149 393 | 9 090 | 19 346 | 0 / 0 | 189 / 347 / 178 / 610 / 263 | grid (σ = 0) |
| room | da3f | 20.8 | 26.4 | 71 442 | 10 539 | 23 006 | 0 / 0 | 175 / 282 / 107 / 304 / 113 | 1/k |
| room | repo8 | 31.3 | 38.7 | 83 101 | 18 677 | 48 040 | 28 / 0 | 127 / 197 / 355 / 747 / 639 | 1/255 |
| silverwarrior | **da3** | 14.9 | 16.8 | 71 986 | 12 419 | 28 788 | 0 / 0 | 6 / 217 / 488 / 1 307 / 1 633 | grid (σ = 0) |
| silverwarrior | da3f | 14.6 | 16.8 | 65 644 | 15 530 | 35 611 | 0 / 0 | 17 / 261 / 567 / 1 398 / 1 500 | 1/k |
| silverwarrior | repo8 | 21.5 | 21.7 | 40 523 | 20 149 | 37 160 | 13 / 0 | 71 / 459 / 915 / 1 737 / 1 518 | 1/255 |
| starwatcher | **da3** | 19.6 | 20.9 | 102 135 | 13 556 | 34 354 | 0 / 0 | 0 / 0 / 21 / 84 / 91 | grid (σ = 0) |
| starwatcher | da3f | 20.3 | 21.7 | 19 805 | 15 523 | 38 253 | 0 / 0 | 0 / 3 / 45 / 160 / 139 | 1/k |
| starwatcher | repo8 | 24.4 | 27.4 | 66 871 | 16 433 | 37 602 | 6 / 0 | 0 / 14 / 51 / 17 / 38 | 1/255 |
| starwatcher | da3sky | 19.7 | 20.9 | 102 229 | 13 567 | 35 372 | 0 / 1 | 0 / 0 / 0 / 89 / 107 | grid |
| vermeer | **da3** | 41.2 | 43.3 | 101 339 | 40 633 | 92 665 | 0 / 0 | 4 / 12 / 6 / 1 336 / 334 | 1/k |
| vermeer | da3f | = da3 (σ > 0) | | | | | | | |

The plate is 677 376 texels (1008×672), 1 016 064 (silverwarrior), 705 600 (starwatcher), 903 168 (vermeer). Sheets
`s19/b_<picture>_sheet.png`: per arm the colour, the depth map, and the shots at 0.1, 0.2 and (0.301, 0.068) m.

## 3. What the batch says

1. **The recipe runs on all six without a parameter touched, and the clone count is 0 on every DA3 arm** (the one
   exception is a single final-plate texel on starwatcher with the sky option). Bands are 7.5–21 % of the plate on five
   pictures and 41 % on the vermeer (a close interior with the figure spanning the depth range; DA3 also upsampled it
   1.9×). Interior holes on the user's path stay under ~100 px on bristlecone, octopus and starwatcher; the room reaches
   610 px at the far pose; **silverwarrior (1.3–1.6 k px) and the vermeer (1.3 k px at (0.301, 0.068) m) open real holes at
   the far poses** — the sheets show them at the bottom right of the warrior (the bears' flank uncovers nothing) and at the
   milkmaid's right side. Those two are the pictures to look at on the user's screen.
2. **DA3 beats the repo's maps on every picture that has one**, by the same margins S8 measured on the troll: bands 1.5–5×
   smaller, seams 1.2–5.5× fewer, torn triangles 1.1–5× fewer, and the repo arms all put clones into the colour stage
   (3–219; the final-plate check still removes them). The repo maps are the old Space model's; nothing new.
3. **Bristlecone's repo map is stored with the opposite convention** (bright = far: the tree at 37/255, the sky at 175).
   Read as the app reads it, it makes a 73.6 % band and 219 colour clones. Inverted (`repo8inv`) it is still unusable
   (45 % band, 127 clones): its sky sits at 80/255, i.e. a third of the way into the volume, so the whole scene moves as
   near content. A map's range and polarity are part of the input contract; the app has no check for either.
4. **The σ gate reads zero on four of the six DA3 maps** (bristlecone, room, silverwarrior, starwatcher: the pictures with a
   sky or a large flat far region). The S9 estimator is the median absolute second difference; when more than half the
   texels lie in a region DA3 renders flat (the sky at the far end of the inverse depth quantises to a constant), that
   median is 0, the source is declared exact to its grid, and the S10 floor is not applied — the plane law then runs at a
   1/65535 tolerance on a map whose non-sky regions are as noisy as the troll's (the diagnostic's own "triples beyond 2×
   the grid" is 18 % on bristlecone against 47 % on the troll and 1–19 % on the exact kit, so that fraction does not
   separate noise from curvature either). **Forcing the floor (`da3f`) does not clearly help**: far-side texels fall 1–9 %,
   layer 2 falls sharply (starwatcher 102 k → 20 k, room 149 k → 71 k), seams rise 9–25 %, torn triangles rise 7–24 %, and
   the holes move both ways (room 610 → 304 at the far pose, starwatcher 84 → 160, silverwarrior 1 307 → 1 398, bristlecone
   51 → 48). On the two maps where σ > 0 (octopus, vermeer) the flag changes nothing, as it must. So the gate's failure mode
   on sky pictures costs nothing visible that the floor would recover; the tolerance question stays where S10 left it
   (a per-region estimate would be the honest fix, not a global median — not built, not needed by these numbers).
5. **The sky-at-infinity option on these two pictures**: interior holes are not reduced (bristlecone 8/51/28 → 206/90/46 at
   the three far poses; starwatcher 21/84/91 → 0/89/107), and the beyond-frame region shows 13–19 k alpha-0 pixels from
   0.2 m on where the sky-off arm shows none — with the plate's sky texels moved to the infinity plane, the A245 margin
   strips no longer cover the frame's edge there and the sky layer does not fill it in these shots. The option stays off
   by default (it was built for S15's hill-against-sky reveals, where it scored); this is recorded for the live pass.

## 4. Not done / caveats

- No truth for pictures: the numbers are the pipeline's own instruments plus the holes count; the sheets are the evidence
  for the eye. Near-black counts were dropped (meaningless on dark pictures).
- The room's DA3 map has 539 source sheets under the join law (the field of sunflower heads); its 21 % band and 149 k
  layer-2 texels are the plane law doing what a field of overlapping heads asks — plausible, unverified.
- `window._visStep = 1` is a harness flag; defaults are unchanged.
