# S65 — video: how much of the hole another frame already saw, and what copying buys over painting

Date: 2026-09-24. S63 §9's two experiments, run on the nine synthetic video shots (`tk_video.py`, 480×270, 24–48
frames, exact per-frame truth: K = 3 nearest hits per pixel with colour and metric depth, camera pose, the soft
foreground coverage of the blurred frames). Scripts: `harness/truthkit/vid_exp.py` (coverage + the arms),
`vid_band90.py` (coverage on the app's band over ±90°, S64), `reveal90.py`. Outputs: `truthkit/out/video_exp/`.
Everything here uses the **true** pose and depth: it is the ceiling of the copy-from-other-frames path. With estimated
pose and depth it can only lose.

## Experiment 1 — coverage

**The hole** of frame t is every pixel the foreground touches (first hit a thing, or any share of the blurred pixel's
rays hitting one). Under it the truth gives the background point. A hole pixel is **seen** in frame s when that point
projects into frame s onto a pixel no thing touches and whose depth agrees. The tolerance is derived: the depth range
over the 2×2 bilinear footprint plus float16 storage precision (2⁻¹⁰), and the footprint must be one surface (max/min
depth ≤ 1.05, the join ratio of `reveal.py`) — without that last condition a footprint straddling an edge spans both
depths and passes a hidden point as seen (found on the pan, which must read 0 %; the first run's numbers were up to
1.5 points high near edges and are superseded by those below).

| shot | what moves | seen in some other frame | seen in an earlier frame | never seen |
|---|---|---|---|---|
| walker_tripod | a person walks, camera still | **98.5 %** | 93 % | 1.5 % |
| walker_handheld | a person walks, camera shakes | **99.9 %** | 94 % | 0.1 % |
| crowd_pan | several people, camera pans | **98.8 %** | 94 % | 1.2 % |
| runner_blur | a runner, motion blur | **98.4 %** | 98.4 % | 1.6 % |
| truck_trunks | camera slides past still trunks | 72.9 % | 38 % | 27.1 % |
| push_in | camera pushes in on still figures | 18.7 % | 14 % | 81 % |
| bokeh | still figure, tiny camera move, shallow focus | 27.8 % | 14 % | 72 % |
| rack_focus | still figures, focus pull | 12.4 % | 12 % | 87.6 % |
| pan | camera rotates only, still figure | **0 %** | 0 % | 100 % |

The pan's 0 % is the sanity check: rotation about the lens centre reveals nothing.

**Near the silhouette** (distance from the hole's edge; the app's band lives here):

| shot | 0–4 px | 4–8 px | 8–16 px | 16–32 px |
|---|---|---|---|---|
| walker_tripod | 98.9 % | 99.2 % | 97.4 % | 94.8 % |
| walker_handheld | 99.9 % | 99.9 % | 99.8 % | 99.6 % |
| crowd_pan | 99.4 % | 99.3 % | 98.0 % | 93.2 % |
| runner_blur | 99.0 % | 99.1 % | 98.8 % | 95.7 % |
| truck_trunks | 81.0 % | 76.6 % | 71.7 % | 69.7 % |
| push_in | 36.4 % | 13.2 % | 4.8 % | 0.1 % |
| bokeh | 49.3 % | 14.6 % | 1.0 % | 0.0 % |
| rack_focus | 40.0 % | 1.3 % | 0.3 % | 0.2 % |
| pan | 0 % | 0 % | 0 % | 0 % |

**On the app's own band over the ±90° design envelope** (S64; every fourth frame; the app's **default** volume, outer 0.02 /
inner 0.04, with per-frame normalised disparity; each band texel weighted by its seen size cos²θ at the angle that first
reveals it). *(A first version of this table used outer 0.24, a kit scene's depth — superseded.)*

| shot | band behind a moving thing: seen in another frame | share of band pixels behind a thing | band behind STUFF: seen in another frame |
|---|---|---|---|
| walker_tripod | 98.5 % | 6 % | 0.1 % |
| walker_handheld | 99.9 % | 6 % | 2.0 % |
| crowd_pan | 98.6 % | 13 % | 0.5 % |
| runner_blur | 98.8 % | 5 % | 0.1 % |
| truck_trunks | 76.6 % | 36 % | 0.4 % |
| push_in | 20.8 % | 13 % | 2.2 % |
| bokeh | 27.2 % | 12 % | 0.0 % |
| rack_focus | 6.8 % | 15 % | 0.5 % |
| pan | 0 % | 8 % | 0.4 % |

Two facts. (1) Where a moving thing hides the band, other frames almost always saw it (98.5–99.9 % when people move).
(2) But things hide only 5–36 % of the band; the rest is **stuff behind stuff** (a near hill over a far one), and camera
motion does not cover it: 0.0–2.2 % on every shot (`vid_stuff.py`, the hidden point = the first hit behind the visible
one on a different primitive), against a method floor measured on the pure pan (true value zero) of 0.4 %. The app's
±90° head motion is a far larger baseline than any camera move here, so that part is paint, as for a still picture.

**Reading.** When the foreground moves, the background behind it is almost all in the clip already, and mostly in
*earlier* frames (a streaming pass works). When the foreground is still and the camera moves a little, only the rim
nearest the silhouette is ever seen, and the rest must be painted — once.

## Experiment 2 — stability (running)

Three arms on the camera's own frames (blur included), all scored **inside the hole only** against the truth background:

- **A** per-frame LaMa over the whole hole (today's tool run naively on video);
- **B1** copy from every frame that saw the point (median, bilinear), per-frame LaMa for the never-seen rest;
- **B2** copy, then paint once: a never-seen point keeps the value it was given in the previous frame (carried with the
  background depth), LaMa only for points never painted before.

Scores: MAE, masked LPIPS on the hole's bounding box, and the **warp error** between consecutive frames (hole points
present in both holes, moved with the true pose and depth), next to the truth's own warp error (its floor).

| shot | A MAE / LPIPS / warp | B1 | B2 | truth warp |
|---|---|---|---|---|
| walker_tripod | 0.0122 / 0.0046 / 0.0104 | 0 / 0 / 0 | 0 / 0 / 0 | 0 |
| *(eight shots running; about an hour each under the shared CPU)* | | | | |

The arms were started before the one-surface fix, so B1/B2 gathered a few edge pixels they should not have; the effect
is bounded by the coverage change above (≤ 1.5 points of pixels). On walker_tripod the copy is exact (a static, sharp background seen by other frames) and per-frame LaMa flickers by
0.010 per frame where the truth does not flicker at all.

## What was not done

- A video inpainter arm (S63 arm C: ProPainter, DiffuEraser, MiniMax-Remover) — no GPU here; the arms above are the
  copy-and-paint baseline it would have to beat.
- Coverage of the stuff/stuff band and of the outpaint strip beyond the frame by camera motion (the pan and truck shots
  do reveal beyond-frame content) — needs the truth rendered beyond each frame's edge.
- Estimated pose and depth (DA3 multi-view) in place of the truth — the realistic version of every number here.
