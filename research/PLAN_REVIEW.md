# Plan review against the final goal (2026-09-15)

## 0. The goal, as I understand it (correct me)

From one picture — later a video — a head-tracked portal the viewer can look around within ±45° horizontally and ±30°
vertically (the 90°/60° envelope), where **everything is filled** with plausible content that is never a clone of the
foreground, with **no holes and no stretching**, where **objects carry their hidden parts** (behind other objects) and,
in time, **their sides**; produced by **one automatic decomposition pass** with **zero per-image tuning**; the final
textures painted by a diffusion model on clean atlases we hand it; the same machinery for video.

## 1. The plan as it stands (what each stage is, and its evidence)

| stage | what we do | evidence | state |
|---|---|---|---|
| 1 depth | DA3-Mono-Large, 16-bit, effective quantum + noise floor | bake-off S19; kit identity | shipped behind the panel |
| 2 geometry | rim tear law; plane far side per line; band = the reveal set; plate 1 (background continuation), plate 2 (arrival order), sky at infinity, margin strips, fold-alpha | kit: precision 0.94–0.96, recall ≈ 1, depth error median 0 (S9–S11, S15…); six pictures: holes and spaghetti counted (S25) | shipped behind the panel; defaults not yet chosen on a screen |
| 3 placeholders + bundle | wash on the placeholder set; SD bundle at native res, 16-bit, per-class masks, conventions | S17 audit, checker | shipped |
| 4 diffusion inpaint | paint the band / margins / plate 2 | **none — never run** | not built |
| 5 reimport | the painted plates back onto the live plate | **none for the plane set** (only the legacy patch and the MPI layer import) | not built |
| 6 objects | object map (depth on the kit, SAM masks on pictures, live clicks / boxes), object layers at the object's depth, standpoint highlight, band continuation | S27 (S9: 73 → 7–17 error), S28, S29 | shipped behind buttons |
| 7 amodal / 3D per object | the hidden part behind other objects; the sides | pix2gestalt / Amodal3R identified (R5) | not started (GPU) |
| 8 one-pass decomposition | proposals → SAM → depth keeps / glues | S30: SAM-auto fails, depth-alone fails on the painting, OWLv2 + SAM + depth finds both figures on one picture | probe only |
| 9 video | — | nothing | not started |

## 2. Weaknesses, in order of threat to the goal

**W1. The loop to the diffusion model and back has never been closed.** The architecture's central bet is "geometry from
us, texture from a model, on a planar continuation". Stages 4 and 5 do not exist, so no picture has ever been seen
end-to-end. What could go wrong there is exactly what matters most: 15–40 % of a picture is band at 45° (vermeer 41 %),
the model paints it against a flat wash with a planar depth, and lighting, perspective and texture scale must agree with
the visible picture along a long seam. If that looks wrong, the plan changes shape — more of the hidden content must come
from a model that knows the scene (W10), less from our continuation. *Falsifier:* one picture, painted, reimported,
viewed at 27° and 45° on your screen. *Cost:* the reimport is app work (no GPU); the inpaint needs the GPU (or an API).

**W2. Objects are cardboard at wide angles.** S26 showed the zero-thickness rule is the best a texel layer can do, and it is
exact for the *background* behind an object. But at 45° a person's own side is in view, and nothing in the stack
produces it: no layer, no continuation. The "orange revealed on rotation" you described is either a step inside the
picture (S28 reads it) or a side (nothing reads it). A per-object 3D prior (Amodal3R-class) is the only known source, its
quality on paintings, people and creatures is unknown, and the app has no mesh-layer render path for it. *Decision
hiding here:* accept cardboard with a graceful treatment at extreme angles, or commit to per-object 3D. *Falsifier:* one
Amodal3R run on the woman, rendered from 45°, next to the cardboard.

**W3. The depth map is the ceiling of everything downstream, and on real pictures it is rough.** DA3 ramps at silhouettes,
invents steps in painted floors, joins the troll to the ground and the trees; a quarter of the troll's band joins no
visible surface (S28); the plane law is exact where continuations are planes (the kit) and assumed elsewhere (foliage,
curtains, curved rooms). Our photograph metrics — holes, spaghetti, clone counts, band size — are proxies; **we have no
truth for hidden content on a real scene.** *Falsifier (cheap, and I recommend it first):* film 3–5 short sideways phone
pans of real scenes; frame 0 is the picture, the other frames are the truth of the reveals up to the pan's angle. That
scores the band, the plane law and later the painted content on real hidden content, and it doubles as video material.

**W4. Beyond-frame content.** At 45° the picture's own edges need content that was never photographed. The margin strips
are clamp-extended edge texels; vermeer's and the room's far-pose holes are this class (S25 §2). This is outpainting, part
of W1's loop, and the 90° box model's side walls. Not built.

**W5. One pass does not exist yet.** SAM's own automatic mode finds neither figure; the cliff set proposes what it
separates (the woman) and not what DA3 merges (the troll); OWLv2's class-free boxes found both on one picture. A method
needs the six pictures, then video. The object criterion (band demand) inherits W3.

**W6. Video is a different architecture, not a loop over frames.** The bake runs in the browser per image (seconds to
minutes of CPU); video needs an offline batch, temporally consistent depth (a video depth model), temporally consistent
masks (SAM 2's memory), temporally consistent painted content (a video inpainting model), and a per-shot layered
representation the player can stream — with camera motion, the layers move. None of this is designed. The decision that
matters early: does the player consume *one baked scene per frame* or *a layered video* (Broxton-shaped)? The bundle's
shape already leans to the second; the bake does not.

**W7. The live pass has not happened.** Twenty-odd option arms and flags accumulated behind the panel; defaults were never
chosen on a real screen with head tracking; every instrument is synthetic or headless. Each new floor is built on ground
you have not stood on. The risk is not that something is wrong but that we do not know *which* of the arms is worth
keeping, and the dead ones cost every later change.

**W8. Residual constants** (each labelled where it lives; none load-bearing, all should be listed): `--max-frac 0.6` and
`iou ≥ 0.5` in the offline segmenter's pick rule (the browser uses SAM's argmax instead); 3 CSS px pointer slop; 3 × MAD
trimming in the depth fit; NMS at box IoU 0.5 in the OWLv2 probe; SAM-auto's own defaults (0.8 / 0.9) in the probe that
measured it. The geometry has none of ours beyond the window's own extent, as agreed.

**W9. Engineering exposure.** One 28 k-line file; headless verification at 6–25 min per run on a software GPU; the WebGPU
decoder drift (S29 §3c) shows how fragile a browser provider can be; 183 MB of model per origin in the Cache API; WASM
single-thread without cross-origin isolation. None blocks the goal; all slow it.

**W10. The strategic fork we have not tested.** Our approach: explicit layers + our continuation + a 2D inpainter —
cheap, deterministic, 60 fps, controllable, and every hidden texel is *ours to explain*. The alternative (R5: GEN3C, SEVA,
ViewCrafter, camera-controlled video diffusion): generate the off-axis views themselves with a model that has seen 3D, then
bake those views into our layers. It would supply hidden content, beyond-frame content and object sides in one stroke;
it costs a GPU, seconds to minutes per view, limited resolution, and consistency across views that then has to be baked.
Our band and plate machinery would become the *consumer* of generated views rather than the producer of hidden content.
Nothing decides between these except a side-by-side on the same pictures. The GPU makes that experiment possible.

## 3. What this changes about the order of GPU work

The last message put pix2gestalt first. Against the goal, the order should follow the threats:

1. **Close the loop (W1, W4).** App: reimport of the plane bundle (plate 1 colour, plate 2, sky, margins) onto the live
   plate, round-trip test with the bundle checker (no GPU; can start now). GPU: one depth-conditioned inpaint + outpaint of
   the six pictures' bundles (FLUX Fill or SDXL inpaint with a depth ControlNet), reimported, shots at 27° / 45° / 56°.
   The first end-to-end pictures, on your screen.
2. **Real truth (W3).** Your phone pans; a small kit around them (frame alignment, reveal masks, scoring); the band, the
   plane law and the painted content scored on real hidden content.
3. **The fork (W10).** One novel-view model on the same six pictures at ±27° / ±45°, next to step 1's result.
4. **Objects (W2, W5).** pix2gestalt on the troll behind the woman (the red section from a model, through the S27 import);
   Amodal3R on the woman rendered at 45° next to the cardboard; OWLv2 + SAM + depth on the six pictures.
5. **Video (W6).** SAM 2 memory on the pans; a video depth model on them; then the representation decision.
6. **The live pass (W7)** does not need the GPU and should run alongside step 1: choose defaults, strip arms, re-baseline.

Budget for steps 1–4: a few GPU-hours of compute on an A100 80 GB (RLD/RevealLayer in the fork need the 80 GB), a day or two
of app work for the reimport and the pan kit.

## 4. What I would not do

- Build one-pass decomposition or video before the loop is closed: both feed a stage we have never seen work.
- Buy a SAMEO reproduction (training) before knowing whether amodal masks change what the viewer sees at 45°.
- Add more option arms to the plate before the live pass.
