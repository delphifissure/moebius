# S69 — Scene scale without heads: what sizes can and cannot fix, the app's Set Scale tool, and the edge cases

Date: 2026-09-25. User: "heads are not enough, as not every shot has a head. There's a tool in the app to define
distance, maybe you can explore that too. Think through edge cases."

## 1. What the per-shot geometry needs

Under the true-window mappings (S67 §8, C and Cm), each shot is the real scene scaled by m so that the frame at the
subject (pin) plane fills the portal, with the shot's centre of projection at D_i = m·Z_s. A point at camera distance
Z sits at portal depth

    z = m·(Z − Z_s) = D_i·(Z/Z_s − 1).

A depth model gives affine-invariant disparity d: 1/Z = a·d + b, with a and b unknown. So a shot has three unknowns:
the scale a, the shift b (where infinity sits), and D_i (the lens / camera distance).

## 2. What a size reference gives

An object of real size S at disparity d_k, seen s_k wide on the portal, gives

    s_k / S = D_i / Z_k = (D_i·a)·d_k + (D_i·b) = α·d_k + β,

which is linear in α = D_i·a and β = D_i·b.
- **One reference** gives m at its own depth. If it sits at the pin plane, that is the subject's scale, and with it the
  subject's size and its relief (z ≈ m·ΔZ near the pin plane). This is the "feels head-sized" part, and it needs no lens.
- **Two or more references at different depths** give α and β. That fixes every depth ratio Z/Z_s = (α·pn + β)/(α·d + β),
  i.e. how the scene recedes. S68's head line is this case.
- **Sizes never give D_i alone.** α and β are products with D_i: sizes measure angles, and angles do not say how far
  away the camera was. D_i is the lens / camera-distance ambiguity, and it scales everything behind the subject:
  z = D_i·(Z/Z_s − 1).
- **What fixes D_i:** the lens (focal length and sensor, EXIF, or the app's existing "Camera Intrinsics" inputs), a known
  length along the line of sight (a table's depth, a road marking's spacing), a known camera height above a ground plane
  with the horizon in frame (single-view metrology), or a metric depth model's absolute output.
- **Free constraints the app already has:**
  - **Sky:** the sky class (S2c) is infinity, 1/Z = 0 at the sky's disparity, which fixes the shift b. One size
    reference plus sky is a full solve up to D_i.
  - **The pin plane:** the subject's disparity pn is where z = 0 by construction.

So the cues rank as:
- **Scale at the subject:** any one size reference there.
- **Recession:** two references at different depths, or one plus sky.
- **Absolute (the lens):** the lens, a depth-axis length, or camera height plus horizon.

The S68 lens test says the estimated lens is not safe as the only source. The fallback when nothing else exists is the
lens input's default, labelled as such.

## 3. The app's Set Scale tool, audited (moebius.js `handleCanvasClickForScale`)

It takes two clicks on the rendered picture and a typed real distance. It sets `metricScaleFactor` = real / virtual,
where "virtual" is the 3-D distance between the clicked points in the app's volume.

It then derives an "estimated distance" from the clicks' vertical pixel separation and the render camera's field of
view, and sets the face-tracking scalar to (0.7 m / estimated distance) × 3.0, clamped to [0, 50].

- **The measurement mixes axes.** The volume's depth axis is not metric (the fixed 0.02 / 0.04 m law), so for two points
  at different depths "virtual distance" is not a length in any consistent unit. Only a length in the image plane, at
  one depth, is meaningful.
- **Only the vertical pixel distance is used.** A horizontal measurement gives 0, which makes the estimated distance
  infinite and the scalar 0.
- **The field of view is the render camera's**, which changes with the head position, not the photograph's.
- **0.7 m and 3.0 are uncited constants.**
- **The result is almost unused.** `u_metricScale` is declared in the shaders but never read; `metricScaleFactor` only
  moves the volume guides and a depth readout. The tool's real effect is the face-tracking scalar.
- **It uses `prompt()` and `alert()`,** and keeps one reference, not per shot.

## 4. Edge cases

| case | what goes wrong | handling |
|---|---|---|
| no object of known size (landscape, abstract, macro, space) | no size cue at all | lens input + sky; else the current fixed volume, labelled "no scale"; the user can type a length for anything |
| one reference only | m at its depth; recession unknown | sky fixes b if present; else assume d = 0 is infinity (the depth model's convention), labelled |
| reference not at the pin plane | its m is not the subject's | carried to the pin plane by the α, β line; with one reference, only through the sky or default shift |
| reference tilted (two clicks at different depths) | its image length is foreshortened | use image-plane length only; flag when the two clicks' disparities differ enough that foreshortening exceeds the measurement's own pixel precision |
| people and objects of unusual size (children, statues, giants, dolls) | the class size is wrong | robust fit (median / outlier rejection against the α, β line); per-reference override |
| pictures within the picture (posters, billboards, screens, mirrors) | a 3 m face on a billboard; a mirror's depth is the mirror's | reject references off the line; exclude mirror and glass regions (depth models are unreliable there too) |
| miniatures, tilt-shift, forced perspective | sizes and depth both lie | nothing automatic can know; the user's reference wins, and a conflict between cues is shown rather than averaged |
| zoom or dolly-zoom within a shot | D_i changes per frame | per-frame lens (zoom) or per-frame reference tracking; a dolly zoom keeps the subject's size constant, so only the background cue moves |
| crops, letterboxing, anamorphic squeeze | frame width and pixel aspect wrong | measure against the full original frame; horizontal and vertical references separately when squeezed |
| lens distortion (wide, fisheye) | straight-line metrology fails near the edges | undistort first, or use references near the centre |
| aerial and drone shots | an eye-level camera-height prior is far off | the camera-height cue only when the ground plane and horizon agree with an eye-level height, else unused |
| comics | stylised proportions (big heads), inconsistent scale across panels, no camera | identity propagation: the same character keeps the same real size across panels, which gives relative scale without any known absolute size; the absolute is set once (e.g. the lead is 1.8 m); balloons and borders excluded |
| cuts across a film | each shot solved alone drifts | the same object (a character, a car) keeps its size across shots: a cross-shot anchor |
| "life-size" is impossible | a cathedral through a 30 cm portal | not an error: the portal is a window; m ≪ 1 is right, and only close-ups approach m ≈ 1 |
| depth-model failure regions (sky edges, glass, water) | wrong d under a reference | references there are down-weighted; the sky is used only as infinity |

## 5. Proposal

- **References, per shot:**
  - Two clicks give an image-plane length, taken at the clicks' median disparity (in-panel, no `prompt()`).
  - The real length comes from typing it or from presets (person, head, door, car, step), each preset with a stated range.
  - The detected references (faces from MediaPipe for film) are candidates the user can accept.
- **Solver:**
  - α and β by a robust fit over all references, with the sky as infinity where present.
  - D_i from the lens: the existing Camera Intrinsics inputs (focal, sensor), tied to the new shot-lens select, or EXIF,
    or a depth-axis length.
  - The HUD shows each cue's answer and the residuals, and states which unknown is set by a default.
- **Output:** the per-shot metric depth law (the cut check's "prop" law: pin plane pn, slope κ, and outer/inner from
  α, β and D_i), feeding the C and Cm mappings.
- **The old tool's scalar side-effect is removed.** Under C and Cm the head gain is not a free scalar.

References for single-view metrology and the camera-height prior (Criminisi, Reid & Zisserman, "Single View Metrology",
IJCV 2000; Hoiem, Efros & Hebert, "Putting Objects in Perspective", CVPR 2006) are named for the idea only; not yet
read first-hand here.

## 6. As built (app main `5303818`, after the user's go)

(`handleCanvasClickForScale`, `bgScaleSolve`, `bgMetricLawZ`; panel: Set Scale + preset + length + Clear + readout)
- **Measuring:** Set Scale holds the view at rest. Two clicks are mapped through the rest frustum to source pixels, and
  the reference is their Euclidean pixel length in portal units, at the clicks' mean disparity, with the typed or preset
  real length. The presets are typical values, editable.
- **Foreshortening:** a pair whose app distances differ by more than the join ratio 1.05 is flagged as not one surface.
- **The solve:** α and β by least squares over all references, plus the sky as the point (d = 0, q = 0) when sky pixels
  exist.
  - One depth only and no sky: β = 0 is ASSUMED (the farthest point at infinity) and said to be wrong indoors.
  - α ≤ 0 (nearer is not larger) is reported as a conflict, and the first reference alone is used.
- **The lens:** the shot-lens select if set, else Camera Intrinsics (focal, sensor).
- **The readout:** the scale at the subject plane (1 m = x cm on the portal), the subject's distance, the farthest
  point's distance, per-reference residuals, and every assumption.
- **Geometry:** under C / Cm the per-shot metric depth law replaces the volume law in the shared GLSL displacement and
  in `volumeZOffForNormDepth`: z = D·((α·pn + β)/(α·d + β) − 1), capped at 999·D (C's parallax cap). The result is in
  the SD bundle's meta (`sceneScale`).
- **Removed:** the old tool's face-tracking scalar side-effect, its `prompt()` / `alert()`, and the axis-mixing 3-D
  division.

**Check** (`harness/scale_check.js`, a synthetic disparity field with a known line α = 0.2, β = 0.02):
- One reference: flagged assumption, β = 0.
- Two references (one horizontal, one vertical, at d = 0.8 and 0.3): α = 0.2000, β = 0.0200, residuals 0.
- A contradictory pair: reported.
- The lens from Camera Intrinsics: D = layerW·50/36, exactly.
- The metric law under Cm: z(pn) = 0, monotone, far end finite (8.2 m).
- The face-tracking scalar: unchanged.

**Not built yet** (from §5):
- Detected references offered as candidates (MediaPipe faces for film).
- EXIF and a depth-axis length as lens sources.
- Robust outlier rejection: the fit is plain least squares with conflict detection only.
- References stored per shot, and carried across cuts.
