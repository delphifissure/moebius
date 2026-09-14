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

## 6. Object masks from SAM 2.1 and the standpoint highlight (S28, 2026-09-14)

What it is: the depth-only object rule is exact on the kit but on a photograph its footprints are DA3's steps, not
silhouettes (on the troll one 480 k-px component). `harness/segment/sam2_objects.py` segments the picture with SAM 2.1
(CPU, ~3 min with the automatic pass) from clicks / the export's boxes / automatically; **📤 Import object masks (S28)**
makes that map the app's objects; **🎯 Highlight object** + id shows one surface's standpoint (S28 §1 table): the object blue,
what it hides of *itself* orange (faint at rest on the occluding part, full in the revealed band), what *another* object hides
of it faint red at rest / red in the band; id 0 = the background's standpoint (objects red, the background's own steps orange,
the rest blue); −1 off.

1. Build (panel as §1 step 4), **Export SD Bundle**; unzip somewhere. Or headless: `IMG=<color>,<depth16> TAG=x node
   harness/objl_view.js` writes `harness/shots/objlayers/view_x/{source_plate.png, objects.json, objIds.u8}`.
2. `python3 harness/segment/sam2_objects.py harness/shots/objlayers/view_x --auto --points "300,190+300,350+250,650+330,800;470,700+455,500"`
   — clicks in plate-grid pixels (the plate grid is `objects.json → pw, ph`; open `source_plate.png` to read coordinates),
   `+` joins several clicks on one object, `;` separates objects. For a bundle: `python3 harness/objl_starters.py` is not
   needed; point the script at a folder holding `plane_source_color.png` renamed `source_plate.png` and `meta.json`'s
   `plane_objects` saved as `objects.json` (`{pw, ph, objects}`) — or run `objl_view.js`. Look at `overlay_sam.png`: one
   colour per object, ids in `objects_sam.json`. If an object came out as a part (one click on the troll = his torso), add
   clicks and rerun (seconds per prompt; the automatic pass is the slow part — drop `--auto` while iterating).
3. In the app, after the Build: **Import object masks (S28)**, multi-select `plane_object_ids_sam.png` + `objects_sam.json`.
   Console: `[S28] object map set from SAM 2.1 …: N objects; first … px, band …` and, on the first highlight,
   `[S28] band continuation: … joined … (… occluded by another surface, … a surface hiding itself), … joined nothing`.
4. **Highlight object**: id 1 (the troll), 2 (the woman), 0 (the background), −1 off. Move 10–20 cm right and left: the band
   colours are what the plate shows there; the faint marks at rest sit on the pixels that hide those band texels.
   **🧭 Object view (S27)** saves the whole picture's map (blue outlines, red/orange/grey band) as a PNG.
5. Send back: `overlay_sam.png`, the console lines, and a screenshot per highlight at rest and at 10–20 cm. What to judge:
   is the troll's outline the troll (SAM), is red where another thing stands in front, is orange only where a surface steps
   in front of itself. Orange never marks an object's sides beyond its silhouette (not in the picture; S28 §3c).

## 7. SAM 2.1 in the browser — click objects live (S29, 2026-09-14)

1. Build (panel as §1 step 4). Press **🖱️ Click objects (SAM 2.1 live)**. First time: the status line under the button
   counts the download (183 MB from Hugging Face, cached by the browser afterwards), then "encoding the picture" (seconds
   on WebGPU in Chrome/Edge; 10–40 s on WASM in Safari/Firefox), then "click an object". The view is held at rest while the
   mode is on (head tracking resumes on Esc).
2. Click the troll's chest: the mask shows blue on the picture. It will be the torso — press **Tab** to see SAM's other two
   candidates (the whole figure, a muscle), or add clicks on the belly, thigh and foot: with several clicks the best-rated
   candidate is the whole troll (S29 §3). **Alt-click** excludes a point (Shift is the app's drag). **Backspace** undoes.
3. **Enter** keeps the object: it becomes object 1, the S28 highlight comes on (blue, its own steps faint orange, revealed
   band as you move after Esc). Click the woman (two clicks), Enter → object 2. **Esc** when done: the map stays and feeds
   the export (`plane_object_ids.png`, `meta.plane_objects` with `source: "live click …"`), the Object view, the layer import
   and the Highlight-object field (ids 1, 2, …; 0 = background).
4. Console lines: `[S29] picture encoded in … s (webgpu|wasm)`, `[S29] N click(s): candidate k/3: … px, SAM iou …`, `[S29]
   object k kept …`, and the S28 lines on each accept. If it says `SAM 2.1 not available: …`, the CDN or Hugging Face is
   unreachable from your network: download `onnxruntime-web@1.22.0/dist/*` and the four `onnx/vision_encoder*.onnx*`,
   `prompt_encoder_mask_decoder*.onnx*` files into `vendor/ort/` and `vendor/sam2/` next to the app and set
   `window._ortBase = 'vendor/ort/'; window._sam2Base = 'vendor/sam2/'` in the console before pressing the button.
5. Send back: the encode time and provider from the console, one screenshot with a pending mask, one after Enter, and the
   ids you ended with. What to judge: does one click give the thing you meant (if not, how many clicks / Tabs did it take),
   and is the click landing where you pointed (the mask should start under the cursor).
