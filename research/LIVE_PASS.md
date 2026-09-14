# Live pass — how to test on your screen (2026-09-13)

Everything below is in the app repo (`moebiusv2`) as pushed. The numbers quoted are from the notes S17–S23; your screen decides.

## 1. Set-up (five minutes)

1. Serve the app folder as you normally do and open `moebius.html`.
2. The app auto-loads `defaultImgColor.png` + `defaultImgDepth.png` from the app folder. To test a picture, copy its colour and
   depth over those two names (keep your originals) and reload. 16-bit depth PNGs are read natively.
3. Depth maps ready to use, all DA3-Mono-Large at the working size (colour beside each): `harness/batchB/<picture>_color.png`
   + `harness/batchB/<picture>_da3_16.png` for bristlecone, octopus, room, silverwarrior, starwatcher, vermeer; the troll:
   `defaultImgColor.png` + `depth_da3mono16.png`. (The repo's old 8-bit maps lose to DA3 on every picture, S19; the
   bristlecone one is inverted — do not use it.)
4. Open the bake panel. Set, left to right: **far side = plane (rim law)**, **fill = wash**, **margin = picture**,
   **faces = off**, **band = tier ≤ 35°**, **sky = off** (on for bristlecone and starwatcher), **seams = stretched**,
   **join = off**, **rules = current**. Click **Build** (1–4 min). The panel remembers its values.
5. Two console flags for the check views (open the browser console, set before Build): `window._plateFoldAlpha = 2` paints
   magenta every plate pixel that is stretched past the fold (the spaghetti); `= 1` makes those pixels transparent instead
   (S25 §3: closes holes on silverwarrior, opens them on vermeer). `window._plateFoldAlpha = 0` returns to the default.

## 2. What to look at, and where

Move the head (or drag) to these five places; the harness shots used the same ones (D = 0.2 m):

| eye offset | angle | what it tests |
|---|---|---|
| 5 cm right | 14° | near-rest: nothing should change but the parallax |
| 10 cm | 27° | the first-uncover band; is the wash plausible, never a foreground clone |
| 20 cm | 45° | the envelope rim: the band's full width; holes should be none |
| 26 cm right, 9 cm up | 52° / 24° | past the rim on the diagonal: the plate's tears and the margin |
| 30 cm right, 7 cm up | 56° / 19° | past the rim: same |

At each, look at (a) the far side behind every silhouette — is it the background continued, or the thing smeared? (b) holes
(black or backdrop), (c) the frame edge — does the picture's rest rectangle end in a clean edge or a torn one, (d) with
**SD regions** ticked: cyan = to be painted inside the tier, blue = band outside the tier (wash may stay), teal = carrier-only
wash, magenta = plate 2, orange = beyond the frame. Every placeholder colour you can see should be tinted; nothing else.

## 3. The decisions, one select each (change the select; it re-bakes)

**rules = + ceiling cut** (S23; the third select from the right, added 2026-09-13). *For:* on rooms with a visible ceiling the wall is no longer continued up into the ceiling
behind anything that touches it — S7 P 0.65 → 0.86, S26 beams 0.46 → 0.82, grille 0.50 → 0.69; byte-identical on every
scene and picture without a ceiling plane (troll, vermeer, room, silverwarrior). *Against:* nothing measured; the ceiling is
found by the same majority test as the ground, so a picture with a false "ceiling" (a horizontal surface above the eye that
is not a plane) is the case to watch — the vermeer's ceiling is not found (majority test fails), so it is untouched.

**rules = + ceiling cut + line despeckle** (S20). *For:* one-texel structures survive the despeckle (S5 poles: recall 0.51 →
0.98; think wires, thin branches, railings). *Against:* a one-texel line of depth noise also survives; on the six pictures and
the troll it kept 270–1 070 texels each with no visible change and no clone; S5's precision falls because a one-texel pole's
band is a few texels wide against a truth of one.

**seams = seams + rim stretched** (S20). *For:* closes the far-pose holes that are plate rim tears (silverwarrior at 45°:
488 → 14 px; at 56°: 1 635 → 2). *Against:* a skin between every silhouette and its background wherever the band's carriers
stop short — wash on one side, source on the other, never a foreground clone, but a stretch the eye may read. Judge at 52°
and 56° on silverwarrior with and without.

**margin = window** (S20, S19). *For:* content behind a near thing at the picture's edge comes from outside the picture;
the window margin covers it (vermeer 56°: 1 336 → 229 px) and zeroes the edge-connected uncovered area. *Against:* the
margin strips are clamp-extended source colour (a placeholder for the outpaint), visible past the rim; with the picture
margin the frame's edge stays honest and open.

**sky = on** (S19 §3.5, only pictures with sky). *For:* the sky sits at infinity and does not parallax with the far plate.
*Against:* the frame edge is left uncovered from 0.2 m outward (the sky layer's own margin is missing) — a known gap, not a
choice; look at the top corners at 45°.

**band tier** (35° / 25° / 15° / all). *For a tier:* the texture stage paints only what is uncovered inside that angle; the
rest keeps the wash. *Against:* if you go past the tier the wash shows. The kit's band is the size of the truth at recall ≈ 1,
so "paint all" costs only inpaint area, not correctness.

## 4. What to send back

Per picture: which selects, a screenshot at 27° and at 45° (and 56° if it matters), and one line: keep / drop / undecided.
That is enough to set the defaults, strip the arms you drop, and re-baseline every instrument.

## 5. Object layers — how to test the import live (S27, 2026-09-14)

What it is: after a plane Build the SD Bundle now carries `plane_object_ids.png` + `meta.plane_objects` (each occluder's
footprint and box), and the button **📤 Import object layers (S27)** reads completed object layers back: `obj_<k>_color.png`
(RGBA at the plate grid, alpha = the whole object including its hidden part), `obj_<k>_visible.png` (its visible footprint,
white; recommended), optionally `obj_<k>_depth16.png` (any depth or disparity; aligned on the visible front). Visible texels
keep the source depth; hidden texels sit at the object's own front depth (or the aligned depth), behind whatever is visible
there. A new Build drops the layers. The only case where a layer changes what you see is an object hidden behind another
object (S27 §3): an object's own sides cannot live in a layer.

**A. The demo that shows the mechanism (S9, three cards behind each other) — ten minutes.**
1. `harness/objlayers_demo/S9/`: copy `S9_color.png` → `defaultImgColor.png` and `S9_depth16.png` → `defaultImgDepth.png`
   in the app folder (keep your originals), reload.
2. The kit's depth law, in the browser console before the Build (the sliders cannot reach the kit's values):
   `outerVolumeDepth = 0.112; innerVolumeDepth = 0.0001; currentNormPortalPlane = 0.5; window._rayReproject = true;`
3. Bake panel as in §1 step 4 (far side = plane, fill = wash, margin = picture, faces = off, band ≤ 35°, sky = off,
   seams = stretched, join = off, rules = current), **Build**. The console prints `[S27] objects (A253 rule …): 4 components …`.
4. Move 10–20 cm right: the wall wash sits behind the red card where the green and blue cards should continue. That is
   the "before".
5. Click **Import object layers (S27)**, multi-select the nine `obj_*.png` files in `harness/objlayers_demo/S9/` (or only
   the six `_color` + `_visible` files: the cards are flat, the depth file adds nothing and the console says so). The
   console prints one `[S27] object layer {…}` line per card: `visiblePx`, `hiddenPx` (10 094 and 16 786 for the green and
   blue cards), `depth.rule`. The first frame after the import takes a moment on a slow GPU (shader compile).
6. Same 10–20 cm right: the hidden card parts are there, at the card's depth, with the card's texture. **SD regions** ticked:
   the layer content is untinted (it is content, not a placeholder); the wash it replaced was blue/cyan.
7. **Build** again drops the layers (console: `[S27] rebuild dropped 3 imported object layer(s)`).

**B. On a photograph — what the files are and where they come from.**
1. Build, then **Export SD Bundle**. In the zip: `plane_object_ids.png` (0 = none, 1..254 objects, largest band demand
   first), `meta.json → plane_objects` (rule, boxes in plate and source pixels, footprint / band-demand counts, the reimport
   contract), `plane_source_color.png`.
2. `python3 harness/objl_starters.py <bundle.zip> <dir> [N]` writes, for the N most demanding objects, `obj_<k>_color.png`
   (the visible part cut out, transparent elsewhere), `obj_<k>_visible.png` and `obj_<k>_box.txt`. Paint or generate the
   hidden part into the transparent area (an editor, or a layer model given the box / mask), keep the names, import.
3. What to expect: only objects that hide *another* object gain anything; the plane law already carries the background
   behind every object and S26 says nothing beats it there. Where a layer is wrong (a painted part that does not match the
   scene) it shows exactly as painted — the import does not blend.

**C. What to send back:** the console's `[S27] objects` line and the per-layer lines, a screenshot at 10–20 cm right before
and after the import, and, if a layer misbehaves, the `obj_<k>_*.png` set so the harness can replay it
(`harness/objl_filetest.js` is the headless version of the button; `harness/objlayers.js S=S9` the full kit run).
