# S67 — ±90° follow-ups: poses by angle, the tolerance at 45°, the strip stored by angle; framing, the dolly-zoom head mapping, and distance

Date: 2026-09-25. Continues S64 (the design envelope is ±90° × ±90°). App changes are on the worker branch
(`moebius.js`), each identical to today's behaviour at the webcam envelope (45° × 30°) by construction and checked
headlessly; offline instruments in `harness/`.

## 1. Sweep poses spaced by angle (`window._poseByAngle`, off by default)

`bgPoseAxis(u, vertical)` places the u-th pose of a sweep grid (u ∈ [−1, 1] across the envelope) at a fraction
tan(u·A)/tan(A) of the rim offset, A the fade-end angle of that axis; with the flag off it returns u (today's grid,
uniform in eye offset). Both sweep grids read it (`_plugVisibilitySweep`, `_plugCpuSweep`). Same endpoints (−1, 0, 1)
in both, so the boundary-only mode still walks the rim.

**Identity** (`harness/pose_angle_check.js`): flag off, 103 of 103 grid coordinates (5, 17 and 81 across) returned
bit-identical; flag on, the recovered angle atan(frac·tan A)/A equals u to 1.1·10⁻¹⁶.

**Coverage** (the app's CPU sweep on the default picture, stride 2; each 17 × 5 grid scored against a dense
angle-uniform 49 × 13 reference, split by the angle at which the reference first sees each texel):

| envelope | grid | seen by 17 × 5 / dense | 0–15° | 15–30° | 30–45° | 45–60° | 60–80° |
|---|---|---|---|---|---|---|---|
| 45° × 30° | by offset (today) | 92.2 % | 94.8 | 87.0 | 73.2 | | |
| 45° × 30° | by angle | 93.5 % | 96.3 | 88.2 | 73.1 | | |
| 80° × 80° | by offset | 65.9 % | 70.8 | 66.4 | 52.8 | 52.3 | 55.1 |
| 80° × 80° | by angle | **84.7 %** | 90.7 | 87.4 | 87.3 | 59.2 | 47.0 |

At the webcam envelope the two spacings are within 1.3 points. At 80° the offset grid puts most of its poses past
45° and loses a third of what the dense grid sees in the rings where texels are seen largest (seen size ∝ cos²θ);
the angle grid recovers it and gives up only the 60–80° ring. (The 80° rows reuse a plate baked for 45°: they test the
spacing, not a bake at 80°; §3.) Also visible: even at 45° × 30° the default 17 × 5 grid finds only 92 % of what a
dense grid finds — §3 asks whether that reaches the band.

## 2. The visibility tolerance evaluated at 45° (`_revealLaw`, unconditional)

The gap a texel pair opens at head angle θ is tanθ on the glass and is seen at cos²θ of that, i.e. ∝ sin 2θ / 2,
largest at 45°. The reveal law's rim offsets are now D·tan(min(fadeEnd, 45°)) per axis: identical for every envelope
up to 45° (so today's 45 × 30 is unchanged by construction), bounded beyond it (D·tan(fadeEnd) → ∞ at 90° while the
seen gap returns to 0). This was S64's item (3).

## 3. The bake at wider envelopes, and the sweep density  *(running — `harness/envelope_bake_check.js`)*

## 4. The strip beyond the frame stored by angle — known-answer prototype (`harness/angle_strip.py`)

A wide picture stands in for the far plane: its central half is "the photograph", the quarters on either side are the
truth beyond the frame. At head angle θ the window shows the far plane shifted by s = σ·tanθ (content at one depth moves
by a translation in screen pixels), σ chosen so the truth runs out exactly at θ_max. The eye sees the screen
foreshortened (cos²θ along the offset, cosθ across), so every score is taken on the outpainted part of the view at that
**seen** size: MAE and the gradient-energy ratio (detail; < 1 smoother than the truth). The outpainted part is only ever
seen (σ/2)·sin2θ wide, never more than σ/2 — the strip is small on screen at every angle.

Arms, one painter (LaMa) for all, nothing chosen per picture: **G** paint on the glass, store on the glass (full storage,
the reference); **U** paint directly in the angle store (u = σ·atan(s/σ)); **M** paint the plane ring by ring outward,
each ring on the plane downscaled by cos θ_k; **A** M's paint kept in the angle store. Five paintings (Hunters in the
Snow, La Grande Jatte, Shishkin, The Great Wave, Paris Street; Rainy Day), 1008 px wide; medians:

| θ_max = 85° (σ 22 px) | 15° | 30° | 45° | 60° | 70° | 80° | 85° |
|---|---|---|---|---|---|---|---|
| G  MAE / detail | 0.071 / 0.83 | 0.084 / 0.82 | 0.085 / 0.80 | 0.083 / 0.70 | 0.092 / 0.59 | 0.085 / 0.51 | 0.097 / 0.50 |
| U  (13 % of G's storage) | 0.069 / 0.83 | 0.082 / 0.84 | 0.086 / 0.83 | 0.086 / 0.81 | 0.093 / 0.77 | 0.090 / 0.67 | 0.101 / 0.75 |
| M | 0.073 / 0.91 | 0.085 / 0.91 | 0.088 / 0.75 | 0.095 / 0.71 | 0.118 / 0.61 | 0.158 / 0.90 | 0.192 / 1.15 |
| A | 0.073 / 0.78 | 0.082 / 0.76 | 0.086 / 0.66 | 0.095 / 0.67 | 0.118 / 0.60 | 0.158 / 0.90 | 0.192 / 1.14 |

| θ_max = 70° (σ 92 px) | 15° | 30° | 45° | 60° | 70° |
|---|---|---|---|---|---|
| G | 0.095 / 0.81 | 0.116 / 0.70 | 0.115 / 0.61 | 0.118 / 0.51 | 0.126 / 0.37 |
| U  (45 % of G's storage) | 0.094 / 0.75 | 0.115 / 0.67 | 0.116 / 0.59 | 0.119 / 0.50 | 0.123 / 0.43 |
| M | 0.094 / 0.83 | 0.116 / 0.85 | 0.113 / 0.67 | 0.176 / 0.57 | 0.216 / 0.47 |
| A | 0.091 / 0.71 | 0.111 / 0.64 | 0.112 / 0.59 | 0.176 / 0.53 | 0.216 / 0.45 |

Storage per side: 33 angle texels against 252 glass texels at 85° (and 1 263 glass texels would be needed at 89°, 34 by
angle at 90°); 113 against 252 at 70° (5 254 vs 144 at 89° / 90°).

**Reading.**
- **Store by angle and paint by angle (U).** Its seen error equals the full glass store's within 0.005 at every angle in
  both runs (per picture it wins about half the time), it keeps as much or more detail — at 85° the glass paint falls to
  0.50 of the true detail where U keeps 0.75 — and it costs 13 % (85°) and 45 % (70°) of the storage, finite at 90°.
  The squeeze the angle parametrisation applies to the painted content is undone exactly by the foreshortening at the
  angle it is seen from, which is why the seen error does not suffer.
- **The ring-by-ring plane paint fails past 60°** (MAE 0.16–0.22 against 0.09–0.13): each outer ring is painted on a
  small, downscaled canvas and upsampled, and the seams and the upsampling both show. The scheme I expected to be the
  correct one is dropped.
- For the bundle: the beyond-the-frame canvas the SD stage paints should be the angle store (width σ·θ_max per side,
  σ·π/2 at 90°), not the glass margin (σ·tanθ_max, unbounded). One painter and five paintings so far; the SD and klein
  arms belong here too once the queue reaches them.

## 5. Framing: the intended viewing distance

The original framing is exactly what the portal shows when the eye is at the picture's **centre of projection**:

    d* = (W/2) / tan(φ/2)        (W portal width, φ the picture's horizontal field of view; full frame: d* = W·f/36 mm)

At d* the portal subtends φ and every ray through it is a camera ray: no distortion. Nearer, the viewer sees past the
frame; farther, the portal crops inside it. The app already encodes this: `dollyDistForFocal(f) = (W/2)(f/18)`, rest
0.20 m with W = 0.16 m ↔ 45 mm, portal 43.6°; the ray reprojection builds the volume along rays from that reference
eye, so the reference eye *is* the intended viewing distance.

Comfort and correct perspective agree only when φ lies in the comfortable range. The comfort distance for a window
angle α is d = (W/2)/tan(α/2) (W = 0.16 m: 0.22 / 0.17 / 0.14 m at 40 / 50 / 60°; a 1 m gallery portal: 1.37 / 1.07 /
0.87 m). If the picture's φ ≠ α, reprojecting from d fans the rays at α instead of φ, and the volume is the scene with
depth stretched relative to width by k = tan(φ/2)/tan(α/2) (with laterals kept, depths from the eye scale by d/d*).

Proposed rule (general, derived): α = φ clamped to a user-adjustable comfort range [α_min, α_max] (default 40–60°);
the reference eye at (W/2)/tan(α/2); when φ was clamped, the depth volume scaled by 1/k. φ from the depth model's
camera estimate (DA3 and MoGe both return intrinsics) or EXIF.

Lean-in and sideways need the same strip: from eye distance d on axis, the strip exposed beyond the frame at depth z
is (W/2)·z·(1/d − 1/d_ref) per side; along a ray at angle ψ through the frame edge the exposure is z·(tanψ − tan(α/2)).
Both are the σ·tanθ form of S64, so one strip stored by angle serves both (face at the glass: ψ → 90°).

(The perceptual side — tolerance of wrong viewing distance, the "50 mm looks natural" practice — is in Cooper,
Piazza & Banks 2012, J. Vision; not yet read first-hand, so none of its numbers are used here.)

## 6. Cuts between focal lengths: the off-axis dolly zoom and the head mapping

Each shot i has its own centre of projection D_i = (W/2)/tan(φ_i/2). The off-axis dolly zoom puts the virtual eye at
D_i behind the fixed portal rectangle (generalised off-axis frustum, Kooima) with the shared object pinned at the
portal plane: across a cut the object keeps its size and place and only what lies in front of and behind it
re-perspectives, as the real lens change did.

The requirement: the viewer's relation to the portal is scaled per shot. The real eye vector about the portal centre
maps to E_virtual = E_real · (D_i / d_real), uniformly in x, y and z, so every viewing angle is preserved
(θ_virtual = θ_real). Consequences: the head-motion gain is ∝ focal length; parallax behind the pinned object is
smaller in the long shot — the correct compression; a head angle at the edge of the envelope in one shot is at the
edge in every shot, so the angle-based envelope work holds per shot. For the shared object to keep its 3D shape, its
depth extent in portal units must be its metric depth times the same magnification m = portal width / its world width
at the subject plane — a per-shot depth scale, which the fixed volume (outer 0.02 / inner 0.04 m) does not provide.

Where the app is (S1 report §9, read from the code): the dolly moves the eye to D(f) with the subject pinned, but the
head mapping is not angle-preserving. Under the dolly the virtual eye offset is constant in metres (convention (c):
a head move that is 45° at 45 mm becomes 17° at 144 mm and 68° at 18 mm), and the lens gain tan(φ/2) of `setLensFov`
goes the other way (∝ 1/f where ∝ f is required). The requirement is S1's convention (a), gain D_i/D_ref =
tan(φ_ref/2)/tan(φ_i/2): 0.4 at 18 mm, 3.2 at 144 mm, relative to 45 mm.

With the webcam at the portal, the face's image position measures tanθ_real directly given the webcam's field of view,
so the lateral mapping is E_virtual,x = D_i·tanθ_real and does not need the viewer's distance; the lean-in mapping is
z_virtual = D_i·d_real/d_intended and needs only the ratio.

## 7. Distance from the face mesh

d = f_px·S/s_px for a facial feature of physical size S seen s_px wide.

- In the app: MediaPipe FaceMesh (tfjs face-landmarks-detection) with `refineLandmarks: false`; lateral tracking uses
  the nose tip's normalised x/y. a148b already computes Z = f_px·IPD/ipd_px (IPD 63 mm, cited from Dodgson) but reads
  the iris-centre landmarks 468/473, which exist only with `refineLandmarks: true` — so `_headPose` is never computed.
- Features: interpupillary distance (~60 px at 60 cm on a 640-px webcam: precise; person-to-person spread of several
  per cent biases the absolute value); iris diameter (~11.7 mm, far more uniform across people, but ~11 px at 60 cm:
  a slowly averaged absolute scale). Yaw foreshortens the projected IPD by about cos(yaw) and must be corrected from
  the mesh's head pose — large under the ±90° envelope.

| quantity | needs f_px | needs the person's IPD / iris |
|---|---|---|
| lean-in ratio d / d_intended | no | no |
| viewing angle tanθ | yes | no |
| distance in metres | yes | yes |

The dolly-zoom mapping needs only a rest reference (d_intended captured automatically from settled, centred frames)
and the webcam's field of view (the a148 table; the Mac value was measured by the user); metres are needed only to
choose d_intended from a comfort angle and for the per-shot depth scale.

**Built, behind `window._headZ` (or `?headz=1`; off by default, and then nothing changes — the detector keeps
`refineLandmarks: false`).** `bgHeadZMeasure` takes the IPD as the 3-D span between the iris centres (x, y and the
mesh's z, so a head turn does not shrink it) and the iris diameter as the larger of each ring's two diameters (a circle
seen obliquely keeps its major axis), averaged over both eyes. `bgHeadZUpdate` smooths both with the lateral track's
own factor (no new constant), captures the rest reference on a145's condition (30 settled detections, face centred),
and reports r = span₀/span and, when a focal length is known (a148 resolver, else the device profile), d in metres
from IPD (63 mm) and from the iris (11.7 mm). The camera: z = z_rest·r and x, y × r, so the eye stays on the ray the
viewer is on (angles preserved); r is held to the dolly's own range (18–144 mm lens distances). A bake is made at the
rest distance (the lean must not become the bake's D; `bgShiftLUTFor` reads D live). The HUD angle stamp shows r and d.

**Check** (`harness/headz_check.js`): the real tracker (MediaPipe FaceMesh with iris landmarks, the npm build of the
packages the app loads from the CDN, served locally — the CDN itself is outside this sandbox's network policy) on
synthetic 640 × 480 frames holding one face at known scales s (true d/d₀ = 1/s); the face is the Milkmaid from the
bundled `batchB/vermeer_color.png` (87 px wide in the picture, so every frame is an upscale of a painting — harder than
a webcam):

| s (face width in frame) | 0.7 (112 px) | 0.8 | 0.9 | 1.15 | 1.3 | 1.5 (240 px) | 1.75 | 2.0 (320 px) |
|---|---|---|---|---|---|---|---|---|
| d/d₀ error, IPD span | −2.8 % | −0.1 | +0.3 | −2.2 | −3.3 | +0.4 | +11.2 | +14.7 |
| d/d₀ error, iris | −6.8 % | −0.6 | −0.1 | −0.3 | −0.6 | +3.5 | +2.8 | +8.9 |

(no face found at s = 0.6.) Within 0.67–1.43 of the rest distance both measures hold to a few per cent; closer than
that the landmark placement drifts (the 2-D span errs identically, so it is not the depth component) and the iris
holds better. Not yet tested: head turns (the frames are frontal), the frame-rate cost of the iris model, and absolute
metres — those need the user's webcam (lean to a few measured distances once, read the HUD).
