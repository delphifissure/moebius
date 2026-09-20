# R6 — Other ways to deal with the troll and the sunflowers: a targeted literature review (2026-09-20)

**Why this note.** R1 surveyed the field by scene element; R5 surveyed the layered-decomposition stack. Neither was aimed at
the two failures that S35 has now isolated and measured, and S35 §57 closed the far field's own part of the question with
three falsified constructions. This review is narrower and later: it asks what *else*, in the literature, addresses these two
cases specifically. It is not a "what is new since R5" scan — R5 was a week ago — it is a differently aimed one.

**What could be read.** The egress policy blocks arXiv, openaccess.thecvf.com, semanticscholar, alphaXiv, github.io project
pages, mlanthology and papernotes, as R5 also recorded. Readable: web search result summaries (which do quote the papers'
own text), github.com and huggingface.co. **So: no paper here was read in full.** Everything below is from abstracts,
search summaries and repository pages, and is marked as such. The three claims I would most want to verify against the PDFs
are flagged at the end.

---

## 1. The two failures, restated as literature problems

**The troll** is a large figure in front of a forest that recedes continuously. What must appear behind him is foliage,
trunks, ground and sky at many depths — not a plane, not a smooth continuation of any one visible surface, but a *field with
statistics*. Our construction fills 17 % of his band with his own depth (the unowned fall-back) and reads 58 % of his
surface lips as "nearer" than the data beside the hole.

**The sunflowers** are a dense field of similar objects at graded depths. Behind a head, the truth is more field. Our
construction fills it with sky, because the field's pieces are labelled things, their marches behind the head are open, and
the two-sided rule sends them to the hedge tier (§51).

Both reduce to one question, which §57 measured and could not answer from geometry: **is a thing in front of a hole an
occluder, or is it itself what is behind?** The contested texels split roughly evenly, and the far lip and the agreement
count both failed to separate them.

In the literature's vocabulary the two cases are: **amodal completion of a background ("stuff") region behind an occluder**,
and **figure–ground / border-ownership assignment at an occlusion boundary**. Those are two distinct bodies of work, and
we have used neither.

---

## 2. Family A — Counterfactual and amodal depth: ask a model what the depth is behind the occluder

**The oldest exact statement of our problem.** *Counterfactual Depth from a Single RGB Image* (Issaranon, Zou, Hoiem;
UIUC; ICCVW 2019) takes a single RGB image **and an object mask**, and predicts *the depth map of the scene as it would be
with that object removed*. That is, texel for texel, the thing our band needs. The authors' own justification — "it works
for the same reason scene completion works: the spatial structure of objects is simple" — is exactly the premise our plane
law encodes by hand. Encoder-decoder, mask-conditioned decoder, pixel resolution rather than voxels, no RGB-D input needed.

**The modern one, with weights.** *Amodal Depth Anything: Amodal Depth Estimation in the Wild* (Li et al.; ICCV 2025;
arXiv 2412.02336). Interface, from the summaries: **image + observed depth map + an amodal mask → depth inside the mask's
invisible part**, with the visible part taken from the observed depth and the prediction aligned to it by scale-and-shift
over the shared region. Two models: **Amodal-DAV2** (deterministic, on Depth Anything V2) and **Amodal-DepthFM**
(generative, conditional flow matching). Trained on **ADIW**, 564 K samples built by compositing occluders over segmentation
datasets. Relative rather than metric depth, deliberately, for generalisation. Reported 50.7 % RMSE improvement over prior
state of the art on ADIW. **Code and weights are released under MIT** (`github.com/zhyever/Amodal-Depth-Anything`,
`huggingface.co/zhyever/Amodal-Depth-Anything`, 0.4 B parameters), with an `infer.py` taking an image path and a mask path.

**Why this matters to us more than anything else in the review.** Three of its properties line up with decisions we have
already made and measured:

1. It takes the **observed depth map as an input** and aligns its output to it by scale-and-shift on the shared region.
   That is precisely the "normalise the layer's depth against the scene depth" proposal R5 examined and S26 tested — here it
   is the published interface, not something we must invent.
2. It **answers §57's question without having to decide it**. We do not ask "is this thing the far side"; we hand it a
   region and a mask and receive a depth field. The prior does the deciding.
3. Its output is a **depth field over a masked region**, which is the exact shape of the object our bake already wants: our
   band is a mask, and `sheets.py` already computes both the band (`disocc.u8`) and the visible components (`comp.i32`).

**The caveat that decides whether it works.** ADIW is built by compositing *objects*, and every framing in the amodal
literature is object-centric: "predict the depth of the occluded parts of **objects**". Our target is the opposite kind of
region — a forest, a field, a ground. Whether a model trained on "an object continues behind an occluder" transfers to "a
cluttered background continues behind a figure" is **untested by the paper and unknowable from the abstract**. It is,
however, *exactly* what L5 and L6 can now measure, which is the single strongest reason to run this test rather than argue
about it.

---

## 3. Family B — Diminished reality: remove the occluder, inpaint colour *and* depth together

This is the same operation as Family A, framed as a product rather than a prediction, and it is a mature area we have never
cited. *DeepDR* (arXiv 2312.00532) is an RGB-D inpainting framework for diminished reality: plausible image and geometry
inpainting with coherent structure at real-time frame rates. *InpaintFusion* (TU Graz / Keio, 2025) removes objects from
live 3D recordings by optimising colour and depth **simultaneously** so the result holds up when the viewpoint changes, and
reports applying 3D inpainting to *multi-layer* image data for better perceived object distance. *RGBD2* generates scenes by
iterative diffusion-based RGB-D inpainting. There is also a joint-RGBD-diffusion line where a single model does
channel-wise inpainting with **asymmetric masks for the colour and the depth channels**.

**Why this is strategically important for us.** We are already building an SD hand-off: a bundle goes out with colour, a
16-bit depth map, plate 2 and masks, and an inpainted result comes back (S17, and the reimport is item 3 on the project
queue). Today only the *colour* is expected back. Every paper in this family says the same thing: **inpaint the depth in
the same pass, with the same mask, and condition each on the other.** If the returned bundle carried depth as well as
colour, the troll's band would get its geometry from the inpainting prior rather than from our fall-back, and §57's question
would never need answering. That is a change to the hole contract, not a new construction in the far field, and it fits work
already scheduled.

The asymmetric-mask detail is worth keeping: the colour mask and the depth mask need not be the same region, which matches
our situation, where we trust the plate's colour further than its geometry in some classes and the reverse in others.

---

## 4. Family C — Scene deocclusion and amodal segmentation: strong for objects, and it explicitly skips our case

*Object-level Scene Deocclusion* (SIGGRAPH 2024) uses depth to order objects, separates the scene into depth layers, and
de-occludes several objects at one depth in a single denoising pass, trained on a synthetic object ensemble.
*SynergyAmodal* (2025) adds text control. *Open-World Amodal Appearance Completion* (arXiv 2411.13019) completes appearance
for arbitrary objects. R5 already covered RevealLayer, RLD, Amodal SAM and SAMEO in this family.

**The finding here is a negative one, and it is useful.** The amodal literature is organised around *things*, and where it
touches *stuff* it does so deliberately only in the visible domain: **amodal panoptic segmentation** predicts semantic
labels for the *visible* regions of stuff classes and amodal masks only for thing classes. One survey remark makes the
position explicit: background elements, clutter and textures "aren't associated with object category labels, but these
unlabelled regions can be occluders of a target object" — that is, the field treats a forest as an occluder of something
else, never as a region whose own hidden extent is wanted.

The exception worth reading is the oldest: **Semantic Amodal Segmentation** (Zhu et al., CVPR 2017), which annotates "the
full extent of each **region**, not just the visible pixels", with figure-ground edge information and overlap ordering.
Regions, not objects, and an explicit ordering — the closest thing in the literature to the map our bake actually wants.

**So:** do not expect an off-the-shelf deocclusion model to complete the sunflowers' field. Expect it to complete a head.

---

## 5. Family D — Border ownership: the perceptual literature for exactly the §57 decision

This is the one I would not have found without asking §57's question in perceptual terms, and it is the closest thing to a
principled answer that does not need a network.

Border-ownership coding (Zhou, Friedman, von der Heydt, 2000) is the finding that visual cortex assigns each occlusion
boundary to **one side**: the side that owns the border is the figure, the other side continues behind it. "One can code any
complexity of occlusion structure by assigning border-ownership of the occluding contours." Modern CNN work on this reports
that border ownership can be inferred **feed-forward**, and that performance "showed a strong dependence on junction-like
configurations, indicating that geometric context contributes more than isolated edges" — that is, **T-junctions carry the
signal**.

**The connection to our code.** Our two-sided rule *is* a border-ownership test: a thing's continuation behind an occluder
is trusted when the march closes on the sheet's own component on the far side, i.e. when the surface is seen on both sides
of the occluder. That is the strongest and cleanest form of the cue, and it is why the rule is right on L5.

**And the failure is now diagnosable in those terms.** The rule is applied **per connected component**. In a porous field
no individual component wraps the occluder: one tree crown behind the troll's shoulder does not reappear on his other side,
and one sunflower leaf does not reappear past the head. The *forest* wraps him; no crown does. So the cue is present in the
picture and our test cannot see it, because we ask it of the wrong unit.

**The construction this suggests** — and it is the only one in this review that needs no model, no new data and no change
to the hole contract — is to **apply the two-sided test at the group or class level rather than the component level**: a
group of components that are mutually joined, or that share appearance and a depth band, is trusted behind an occluder when
*the group* appears on both sides, even though no single member does. We already compute join-law groups (`groupOf`) and
already use them for the reach bound and the plate, so the machinery exists. The risk is obvious and must be measured: it
loosens exactly the rule that keeps L5 correct.

---

## 6. Family E — Exemplar and patch-based depth inpainting: cheap, statistical, and against a house principle

The DIBR lineage (Criminisi-style exemplar inpainting extended with depth) is the classical answer to "fill a disocclusion
in a textured field": *Depth-Aided Exemplar-Based Disocclusion Filling for DIBR*, *Joint Texture-Depth Inpainting* (JTDI),
depth-aware patch-based disocclusion, parallax-guided disocclusion inpainting. A recurring practical note in this
literature is that **the depth map is filled first**, because depth is "usually constant or slowly changing" and the filled
depth then guides the colour synthesis — the same ordering our bake already uses.

This family is the natural fit for the troll's forest on statistical grounds: copying patches of *visible* forest (colour
and depth together) into the band reproduces a field with the right statistics at the right depths, which is what the truth
there actually looks like.

**But it collides with a stated principle.** The project's principles say "everything filled, **wash never clone**". Patch
copying is cloning by construction, and our instruments count clones as a defect. Either the principle is refined (a clone
of *a different part of the same surface class* is not the same sin as a clone of the occluder, which is what our
fall-back does today) or this family stays out. That is a decision for the user, not a measurement, and I flag it rather
than assume it.

---

## 7. Family F — Multi-layer representations for porous occluders

MLGS (multi-layer Gaussian splatting: shallow base layers for visible content, extra layers for occluded regions), layered
depth images with several ordered hits per pixel, Deep Multi Depth Panoramas, and the classic foliage-rendering work that
stores per-layer "surface colour, normal, depth, subpixel mask, hit count and leaf bit". R5 covered MLGS; the LDI framing is
already on our own queue as "per-leaf (K-hit) layers for porous objects" (S27).

Nothing here decides the occluder-versus-far-side question. What it offers is **somewhere to put the answer once we have
it**: a forest behind a figure is genuinely several depths per texel, and plate 2 is only two. If any of Families A, B or D
starts producing good hidden geometry for the troll, this is the representation that can carry it.

---

## 8. What I would actually do, cheapest decisive test first

Each of these is measurable on truth we already have. L6 (a figure before a receding forest) and L5 (a graded field) were
built for exactly this and bracket the question from both sides; the bar is the measured arm's **L6 thing class 0.112 m,
L5 whole band 0.000 / 0.238 m**, and nothing may regress S15 (0.264 m) or the ten scenes at 0.000.

1. ~~**Group-level two-sided rule** (Family D).~~ **Spent — see S36.** On checking §32, closing on an exit onto the
   sheet's own join group is exactly the construction measured and removed there (29 k of 794 k marches closed; starwatcher
   sky-valued 50.6 → 47.0 %, jumps 1 967 → 5 662). The border-ownership *diagnosis* stands — a per-component test cannot see
   a cue the field carries as a class — but this form of the fix is not available. Any reopening needs a criterion that
   separates a forest continuing behind a figure from starwatcher's near plain exiting onto its far plain.
2. **Amodal Depth Anything on the kit** (Family A). **Done — S36**, on CPU (0.36 B; no GPU needed for a handful of kit
   images). The transfer question the literature does not answer is answered for our two cases: the model sits at our
   *good-map* accuracy in both scenes without being given a map, so it buys independence from the object map rather than
   accuracy beyond our ceiling. It fixes the sunflowers' configuration (L5 heads-only: 0.238 → 0.034 m over the band) and
   should be kept away from the troll's, where our arm is already better.
3. **Depth in the inpainting contract** (Family B). Not a research question but a contract change: ask for depth back from
   the SD round trip, with the asymmetric-mask option. It is the same sprint as the reimport already on the queue, and it is
   the version of Family A that needs no extra model because the inpainter is already in the plan.
4. **Exemplar depth fill for the troll's forest** (Family E), *only if* the user rules that a within-class clone is
   permitted. Cheap, no GPU, and the best statistical match for foliage.
5. **K-hit layers** (Family F) once something above produces geometry worth carrying.

## 9. What the literature does not offer

- **No one completes background stuff amodally.** The field is object-centric by construction, and amodal panoptic
  segmentation makes the exclusion explicit. Our case is under-served, which is a reason to test transfer rather than
  assume it.
- **No published benchmark matches our measurement.** Amodal depth is scored on composited objects; we score against a
  multi-hit ray-caster over a viewing envelope. Our truth kit is, as far as this review can tell, a better instrument for
  this specific question than anything the papers use — which is worth knowing before deferring to their numbers.
- **Nothing addresses the porous silhouette's geometry at our tolerance.** The foliage work is about rendering plausibly,
  not about the depth of what is between the leaves.

## 10. Claims to verify if the PDFs become readable

1. That Amodal Depth Anything's amodal mask may be an arbitrary region rather than an object instance, and that the model
   does not internally assume a single compact object (this is the load-bearing assumption of item 2 above).
2. The exact scale-and-shift alignment it uses on the shared visible region, against the normalisation S26 already tested.
3. Whether DeepDR or InpaintFusion publish a depth error in the removed region, rather than only perceptual scores — if so,
   that is the number to compare against our 0.112 m.
