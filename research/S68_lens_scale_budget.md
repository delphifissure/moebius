# S68 — Film and comics groundwork: the lens estimate, the head-size scale anchor, the size of a layered format

Date: 2026-09-25. Queue items 1, 2 and 5 from the user's list (film and comics post-converted to the portal).
Instruments: `harness/fov_bench.py`, `harness/size_budget.py`, and a first head-anchor probe (below).

## 1. Field-of-view estimation has a known answer and misses it (`fov_bench.py`)

Each shot's eye distance is D = (W/2)/tan(hfov/2) (S67 §5–6), so a wrong field of view is a wrong scale for the whole
shot. The pictures here have exact intrinsics:
- the truth kit's dolly family: scene S30 through the same window from D(f), f = 18–144 mm full-frame equivalent;
- the first frame of each of the nine synthetic video shots: hfov 44°.

The model is MoGe-2 ViT-S (normal checkpoint), with fov_x unknown.

| picture | true hfov | estimated | error | eye distance off by |
|---|---|---|---|---|
| dolly 18 mm | 90.0° | 76.2° | −13.8° | ×1.27 |
| dolly 25 mm | 71.5° | 72.0° | +0.5° | ×0.99 |
| dolly 35 mm | 54.4° | 62.5° | +8.0° | ×0.85 |
| dolly 45 mm | 43.6° | 55.5° | +11.9° | ×0.76 |
| dolly 65 mm | 31.0° | 46.7° | +15.8° | ×0.64 |
| dolly 90 mm | 22.6° | 42.8° | +20.2° | ×0.51 |
| video shots, 45 mm (9) | 44.0° | 66.8–78.0° | +22.8 to +34.0° | ×0.50–0.61 |

(The 144 mm dolly render has no estimate in this run.)

- The estimates regress towards about 60–75° whatever the lens. The error grows with focal length and reaches ×0.5 on
  the eye distance.
- These are synthetic, flat-shaded pictures, which are harder than photographs for a model trained on photographs.
  The ViT-B and ViT-L checkpoints were not run (disk).
- Even so, a per-shot lens estimate from this model is not a safe scale.

## 2. The head-size anchor: the idea, and why a detector is the blocker

A recurring object of known size fixes a shot's scale without the lens. Heads are the obvious one, and "keep the head
about head-sized" is the requirement itself.
- With affine-invariant disparity d from a depth model, 1/Z = a·d + b, so a head of fixed size has an image height
  h ∝ a·d + b.
- Several heads at different depths in one picture therefore lie on a line, h = α·d + β, and the line fixes the depth
  model's unknown disparity offset: infinity sits at d = −β/α.
- This is exactly what the per-shot metric depth (S67 §8's Cm mapping) needs.

**Probe** (OpenCV's bundled Haar frontal and profile face cascades, DA3 disparity at each face):

| picture | faces found | fit R² |
|---|---|---|
| Caillebotte, Paris Street | 7 | 0.18 |
| Hunters in the Snow | 6 | 0.21 |
| La Grande Jatte | 3 | 0.51 |
| a photograph (Dandelion) | 5 | 0.88 |

Florence-2's detector found 4–24 people per painting but one face. On paintings the cascades fire on brushwork. The
photograph shows the relation holds where faces are detected properly.

**The anchor needs a real head detector:**
- For film: MediaPipe face detection, which already runs in the app.
- For comics: a detector trained on drawn faces; none is available offline here.
- The comics pilot also needs pages. The sandbox's network policy denies Wikimedia and the Library of Congress, so the
  user either uploads pages or allows those domains.

## 3. The size of a layered colour + depth format (`size_budget.py`)

Measured with x265 (bundled ffmpeg) on three synthetic video shots (480 × 270, 48 frames), scaled to 1920 × 1080 at
24 fps by pixel count (bits per pixel are roughly resolution-independent at fixed quality: an approximation).

| shot | colour (crf 20) | depth (12-bit, lossless) | foreground alpha | total |
|---|---|---|---|---|
| walker_tripod | 26 MB/min | 82 MB/min | 30 MB/min | 139 MB/min |
| truck_trunks | 20 MB/min | 118 MB/min | 9 MB/min | 147 MB/min |
| crowd_pan | 56 MB/min | 372 MB/min | 65 MB/min | 492 MB/min |

- **Depth must be lossless.** Lossy depth rings at every silhouette. Even x265's best lossy setting (crf 0) leaves a
  99th-percentile disparity error of 1.0–2.0·10⁻³, above the app's float16 precision (2⁻¹⁰ ≈ 9.8·10⁻⁴), on all three
  shots. Lossless x265 reproduces the depth exactly; FFV1 is smaller on the busiest shot.
- **Depth dominates, and the obvious saving is structural.** Store depth once per shot for static layers, and per frame
  only for the moving layers.
- **Colour here is optimistic:** flat-shaded synthetic frames compress far better than film grain.
- **Gaussian splats, derived:** 59 float32 parameters per Gaussian (position 3, scale 3, rotation 4, opacity 1,
  spherical-harmonic colour to degree 3: 48), i.e. 236 bytes. A million Gaussians is 236 MB for one static scene before
  compression. Published compression and 4D-splat sizes are not quoted here: not read first-hand.

## 4. Video: paint once, without the chain

S65's stability arms showed that carrying paint frame to frame (arm B2) removes flicker but loses quality, because the
carry is chained: each frame is a resample of the previous one. Arm B3 (`vid_exp.py`) stores the paint in world space
and reprojects it from its first painting every frame. Scores are MAE / LPIPS / frame-to-frame warp error:

| shot | A: per-frame LaMa (S65) | B2: chained carry | B3: world-space store | truth warp |
|---|---|---|---|---|
| pan | 0.0122 / 0.0048 / 0.0065 | 0.0312 / 0.0484 / 0.0004 | **0.0126 / 0.0066 / 0.0024** | 0.0008 |
| truck_trunks | 0.0150 / 0.0356 / 0.0099 | 0.0060 / 0.0633 / 0.0003 | **0.0046 / 0.0410 / 0.0010** | 0.0005 |
| push_in | 0.0145 / 0.0094 / 0.0052 | 0.0262 / 0.0803 / 0.0004 | 0.0203 / 0.0823 / 0.0092 | 0.0014 |

(B2 in this run: truck_trunks 0.0060 / 0.0633 against S65's 0.0055 / 0.0576, as the coverage now uses the
one-surface fix.)

- **Pan and truck: B3 keeps per-frame quality or better and most of the stability.** On the pan it matches per-frame
  LaMa's quality with 2.7× less flicker. On the truck it beats both other arms on MAE, with flicker at twice the truth's.
- **Push-in: B3 is worse, and the reason is structural.** The store is splatted one point per pixel, and as the camera
  pushes in, the stored points spread apart. The gaps between them are handed back to LaMa every frame, which is the
  flicker. The fix is to splat each stored point at its projected footprint (or keep the store as a mesh), so
  magnification opens no gaps. That is the next change to B3.
