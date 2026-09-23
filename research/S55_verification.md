# S55 verification — the 22 papers re-read against the per-paper notes (2026-09-22)

Requested by the user: "re-read all 23 papers now and check the notes". Method: each paper's text read in full, then
its section of `S55_per_paper_notes.md` read and every factual claim checked against the text (quotations, numbers,
table values, section/figure references, and the conclusions drawn for our problem). Findings are logged per paper as
they are made; corrections are applied to the notes and listed here.

The 23 files are 22 papers: `s54papers/0200a64828063176fda718de6c6b4b90.md` (26 lines) is the truncated first-archive
copy of Bornemann & März, whose full text arrived in the second archive (`s54more/fast-image-inpainting-…md`). It was
read; it is the title page, abstract and the first two paragraphs of §1, identical to the full copy.

Legend: ✔ verified against the text · ✘ wrong, corrected · ~ imprecise, tightened · + missed, added.

---

## 1. Hirschmüller, SGM + MI, PAMI 2008 — 2 127 lines read

✔ §I and §II-B streaking quotations; eq. (11) and its penalty quotation; the contrast-adapted P2 (the fraction bar
is lost in the conversion, reassembled as P2′/|ΔI|, which the surrounding text confirms: larger intensity change,
cheaper discontinuity); §II-E.2 quotation and method; §II-E.3 quotations and eq. (18); §II-G quotation; the 8/16
path rule; (12), (13), the bound L ≤ Cmax + P2; O(WHD), 1–2 s; "more similar to Scanline Optimization"; Table I
ranks (1 px: C-SGM 6.2, SGM 9.3; 0.5 px: 3.6 and 5.0); 1.8 s / 2.7 s on Teddy; HMI +18 %, iterative MI +164 %.
✔ The reading "second lowest disparity = second-farthest arrival" is correct.
~ The median quotation was cut mid-sentence ("… for maintaining discontinuities" continues "in cases where the
mismatched area is at an object border"); completed.
+ Missed: *"mismatched pixel areas that are direct neighbors of occluded pixels are treated as occlusions"* — the
rule for the uncertain ring beside a disocclusion; added.
+ Added the constants he states (σr = P1 ≈ 4, σs = 5, 100 px / 12 px segment floors, 300 px aerial peak filter):
all tuned per data set, relevant to rule 2 if any of this is adopted.
~ The notes' preamble still described the first archive only (Bornemann "truncated", three papers "missing");
updated.
Conclusions for our problem unchanged.

## 2. Scharstein, Szeliski & Zabih, taxonomy — 1 015 lines read

✘ **Attribution.** The file is the 2001 IEEE SMBV workshop paper (three authors, Zabih included), not IJCV 2002;
header corrected.
✘ **SAD's bad-pixel rate** is 12.87 %, not 12.43 % (that is SAD/MF); corrected.
✘ **The load-bearing claim was over-read.** "Adding the vertical term is worth a third of the error, and it is the
only structural change" compares best runs with different settings (Fig. 3: SO λ 100 γ 0; GC λ 1000 γ 2). The
SO→GC gap mixes the vertical term, intensity modulation and scale. Rewritten: the paper supports "SO streaks, GC
does not"; one-third is an upper bound on the vertical term, not its size. This weakens one sentence of S54/S55's
case for cross-line coupling; the qualitative case (three lineages report streaking from per-line solving) stands.
~ The streaking-mechanism quotation is §4 (Implementation), not §5; corrected.
~ "Sprint 30 should sweep γ" contradicts rule 2 (S57 C1); rewritten as derive-then-check.
✔ §6.2 quotation; the SO/GC quotation; eqs. (4)–(6); the "[28,26,14,18]" quotation; the λ/γ sensitivity
quotation; the SO ordering/occlusion quotation; the shiftable-window quotation; Table 1 values DP 9.52, SO 9.76,
GC 6.46.
+ Missed: §3.4 "thin shearing layers" from quantised disparity (our 8-bit terraces); §5's per-region evaluation.
Added.

## 3. Bleyer, Rhemann & Rother, PatchMatch Stereo, BMVC 2011 — 687 lines read

✔ §2.3 fill and weighted-median quotations; eq. (4); the refinement schedule (maxdisp/2, 1, halving, stop at 0.1)
and its quotation; the fronto-parallel-bias and "staircase" quotations; Table 1 Venus 0.5 px (7.57 / 1.73 / 1.00);
the untextured-regions quotation and Fig. 6d/e.
✘ **"Constant → plane is worth 7.6×" was mis-attributed.** Of 7.57 → 1.00, the sub-pixel step is 4.4× and the
slant is 1.7×. Corrected with the Teddy ground-plane figures (5.52 → 2.99 at 1 px) as the fairer slant number.
~ The median filter carries γ **and** the window size (35×35 Middlebury, 71×71×3 video) — two tuned constants, one
of them resolution-dependent; rule-2 note added.
~ "Median for Hirschmüller's stated reason": the paper gives no reason; reworded.
~ The link to "class-1 74 %" is our inference, now marked as such.
+ Missed: propagation checks only causal neighbours and alternates sweep direction; the global variant's failure
was partly the optimiser. Added.

## 4. Schönberger, Sinha & Pollefeys, SGM-Forest, ECCV 2018 — 406 lines read

✔ §1 and §4.1 quotations; Table 1 rows (SGM 50.85/23.04/8.89/5.16; min_d L_r 52.18/25.45/11.81/7.79; median
63.25/31.81/9.90/8.24; best SGM-Forest 46.08/19.99/7.78/4.41) and "38 % worse" at 1 px; the "Both methods perform
worse" quotation; Fig. 1 and §4.2 quotations; P1 = 100, P2 = P1(1 + α e^{−|ΔI|/β}), α 8, β 10 and the derived
bounds (900 / 100); ε_p 5, ε_ρ 0.1, ε_I 10; the §5.2 filtering quotation; 72-d feature; the classifier list;
"even a single decision tree"; refs [7], [13], [14].
~ **Equations (1)–(7) are missing from the supplied file** (blank in the conversion); the N_p definition is read
from prose. Stated in the notes.
~ All ε were grid-searched and cross-validated — tuned; noted. "Sweep α and β" rewritten as derive-then-check
(rule 2).
~ Citation "Scharstein & Szeliski 2002" in the comparison table → the 2001 workshop paper actually supplied.
~ §7's Sprint 30/31 verdict marked superseded by S57; §8's "missing #19" resolved (Banz et al.).
+ **Missed, and useful:** §4.1 "Occlusion" — in an occluded region "only a small subset of scanlines results are
correct", the one propagating in from the continuing surface; plus §5.2's right-view passes for left occlusion
edges. Independent support for the far-side rule and for why all-direction combination fails in our band. Added.

## 5. Zhang & Tam, asymmetric depth smoothing, IEEE T-Broadcasting 2005 — 486 lines read

(Much of the equation content is lost in this file's conversion — eqs. (1)–(3) are blank lines; the method is fully
stated in prose, and the notes rely only on prose.)
✘ **Table II standard errors attached to the wrong row.** Untangled from the garbled extraction: symmetric
44.8 (6.6) / 52.9 (3.6) / 62.1 (1.9); asymmetric 48.6 (8.1) / 58.0 (4.4) / 68.4 (2.5). Corrected; the "None"
column argument (identical stimulus per Table I, differs by 3.8 inside the noise) stands.
~ "Closed-form relation" σ ≈ baseline/4 → empirical, one image, three baselines. Tightened.
~ Envelope sentence updated to the ±90° target.
+ Added the paper's closing claim against high-resolution depth (the counterweight to da2x) and the 3× vs 5×
vertical ratio inconsistency between its study and its figures.
✔ Method (separable Gaussian, w = 3σ in §V-B), the hole-filling and LDI quotations, the quarter-baseline and
margin quotations, the §IV binocular quotation, "curved" geometric distortion, 36 px ≈ 1° ≈ 5 % width, the
depth-resolution concession, the cardboard-effect quotation.

## 6. Ndjiki-Nya et al., DIBR with advanced texture synthesis, IEEE TMM 2011 — 713 lines read

(The equations of §III–VI and all of Table II are lost or garbled in this file; checks rest on the prose.)
✘ **The paper was read as condemning our far-side law. It does not.** §I condemns line-wise *colour* filling
("dominant vertical edges"); §III's own *depth* fill is line-wise ("a verified D_i value is copied line-wise").
Our law is a depth law, i.e. the §III procedure with an unverified rim value. The notes now say so: the paper
supports per-line depth with a verified value plus 2-D colour synthesis, and does not test whether per-line depth
streaks.
✘ "[12], [13]" are not both Zhang & Tam: [13] is Lee & Effendi 2010. Corrected.
~ The k-means *verifies* the copied rim value (criterion equation lost), it does not simply replace it with the
background centroid; the paper's own FG/BG labelling of c_min/c_max is backwards against its 255-is-nearest
convention and against §IV-A. Noted.
~ Blob threshold and depth-exclusion tolerance: symbols and values lost in the conversion; the notes had quoted
them with invented symbols inside the quotation. Marked as brackets/placeholders.
~ "The DIBR field settled on colour filling" → one group's choice; the §I survey also lists smooth-then-fill
hybrids.
~ "The initialisation is what matters, not the synthesis" is an inference (no number for initialisation alone;
patch-size test run with initialisation off). Marked.
~ Newspaper: VSRS better overall, but the paper reports gains on two configurations. Added.
+ Missed: holes under 7 samples filled by Laplace cloning (~10× faster) and excluded from synthesis; only
BG-side border samples get priorities (Fig. 8); a two-sample ring at FG–BG transitions excluded from the sprite
(the third source for "don't trust the rim ring", with Hirschmüller and our S56 `return_align` fix); Fehn's
pre-smoothing cannot close frame-border holes (the S56 margin mechanism). Added.
✔ Header; the §I taxonomy, disocclusion-elimination and line-wise quotations; Fig. 2(g) caption; the "relying on
a single value" quotation; 32×32, k = 2; the §VII-B tie and "slightly better" quotations and the subjective
adoption; the §V median quotations and decreasing-N order; the §VI two enhancements; the parameter table (80×80,
s = 2, 9×9 vs 25×25 and its quotation, w_Ω 0.2 ≈ +3 dB / +0.02); the flicker, sprite and unreliable-DM
quotations; the Table II prose verdicts and "sharper but noisier"; the conclusion's perceptual-measure quotation;
HHI supplied Zhang & Tam's "Interview" image (checked in their paper).

## 7. Criminisi, Pérez & Toyama, exemplar-based inpainting, IEEE TIP 2004 — 697 lines read

(Equations (1)–(3) are blank in this file; the notes' forms are the published ones and agree with every term the
prose defines. Now said in the notes.)
✘ **The medial-axis prediction is stale.** The notes still proposed it as an untested Sprint 31 sub-item; it was
tested as task 61 (S57 §5) and came out negative. Per rule 5, the prediction is replaced by the result; the
"we lack the loop" paragraph is rewritten to match (not a gap for the depth law).
~ "Whatever the real structure was" overstated the Fig. 20 caption, which says "tends to"; tightened.
~ The "broken structures" quotation is about Fig. 11, not "the same figure" (Fig. 20); corrected.
~ Ndjiki-Nya cites this paper for his §VI priority, not for his §V ordering; corrected.
+ Missed: §V limitation (iii), *"our algorithm does not handle depth ambiguities (i.e., what is in front of what
in the occluded area?)"*, the authors' own statement of the boundary between their problem and ours; limitation
(ii), curved structures; the concessions to Jia et al.; the remark that ground truth for inpainting is
"non-trivial" (all comparisons are visual). Added.
✔ Fig. 20 caption quotation; C/D behaviour quotations ("approximately enforces the desirable concentric fill
order", "removing sharp appendices", "grow indiscriminately", "'push' … mitigated"); initialisation and freezing
of C; the §V "necessary and sufficient" and §III no-segmentation quotations; the Jia and [24] quotations; the
§III-2 "any further manipulation" quotation and its qualifier; 9×9 and the texel quotation; SSD over filled
pixels in CIE Lab and footnote 3; n_p from Gaussian-filtered control points; ∇I_p as a maximum; source as a
dilated band (Figs. 21, 24); 2 s vs 45 s on the 200×200 aerial image; 18 s vs 10 min on the bungee photograph.

## 8. Shade, Gortler, He & Szeliski, Layered Depth Images, SIGGRAPH 1998 — 619 lines read

✘ **"We forward-map both together; a backward colour fetch is cheap to try."** Wrong: our plates are displaced GPU
meshes coloured by texture lookup (CODEMAP L2823, L3852, L14665), which is the paper's forward-depth /
backward-colour scheme done by the rasteriser. Proposal withdrawn.
✘ **"Their 90° frustum is the same order as our envelope."** The 90° is each LDI's field of view; their viewer
region is a cube of positions. Corrected (and the envelope sentence updated to the ±90° target).
✘ **Cosine weighting read as an importance weight.** The paper assumes all rays equally important; the cosine is
the measure for a uniform ray density through a face. The truth-kit backlog item built on the misreading is
withdrawn.
~ §4.1's epsilon is a decision along a line of sight (samples from different input views); class 2 is between
neighbouring texels. Marked as an analogy; "the cliff tolerance is our epsilon" softened to "plays the role".
~ "Plate 2 is built from arrival order along the ray — exactly the ray-piercing construction" → the plates share
that construction's *sampling* (source-grid, one sample per texel per layer), which is what the limitation needs.
~ "Real multi-view input" for the 1.24 figure → synthetic renders; the "20 vs 17" inconsistency in the paper
noted. "(up to some maximum)" restored in a quotation.
~ The "large changes in view with only a small amount of gap filling" quotation belongs to the homography
factoring (large zooms), not to the depth-first idea; separated.
✔ Header; the Fig. 1 ladder and its three quotations; §4.1 and §4.2 epsilon quotations; the §4.2 sampling
quotations; the two failure events and the ray-piercing quotation; §7 glancing-angle and "not fully understood"
quotations; the splat-size formula as far as the garbled layout allows (d1/d2, √(cos θ2/cos θ1), resolution and
fov terms; θ approximated by normal-to-z angles); four splat sizes, alphas 1, ½, ¼; 11-bit table (5 + 6 bits),
2048 entries per frame; 32⁴ strata × 16 rays ≈ 16 M; chestnut 7 h, 250 MHz Indigo2, 1.1 M depth pixels, 4–10 fps;
8-byte depth pixel, four per cache line, +25 %; the §7 displacement-map quotation; 30/21/16 Hz.

## 9. Shih, Su, Kopf & Huang, 3D Photography with context-aware layered depth inpainting, CVPR 2020 — 781 lines read

✘ **"Their headline component … the paper's core technical novelty" is edge guidance.** The conclusion names
context-aware layered colour-and-depth inpainting as the core novelty; edge guidance is one part of it. The
context-region mechanism is never ablated. Corrected; the in-hole deltas added next to the whole-image ones.
✘ **"The learned inpainter is worse than diffusion in the hole"** held only for SSIM/PSNR; on LPIPS it beats
diffusion even without dilation (0.085 vs 0.088). Added.
~ "Independently validates R8 item 5 … the most direct cross-validation in the corpus … upgrades armD" → consistent
with it: our measure is temporal step (which A126 says may not gate a change on its own), theirs PSNR/SSIM
against truth; their 5 px is a set value, not a reported sweep. The screen decides.
~ "Plate 1 / plate 2: two layers everywhere" → plate 2 carries a coverage mask; the rigid-slot criticism still
applies.
~ "Every paper forbids the occluder in the context" → dropped Criminisi (object removal has no occluder left).
~ "4 bits per texel" marked as my estimate (they store pointers); "our 2× depth arm won" → "we tried".
~ Two quotations had words silently dropped (the LPIPS cross-validation and the training-data pool); restored or
marked.
+ Missed: the context region *erodes* by the 5 px dilation — the fourth source for not trusting the boundary ring;
alternating expansion; their input requirement that colour and depth discontinuities be aligned, and the
independent-inpainting misalignment warning (the `return_align` failure); supplement failure cases (thin
structures, over-smooth monocular depth). Added.
✔ The LDI-connectivity and cut quotations; the rigid-layer quotation; §3.2 context quotations; 40/100 iterations
and the "do not step back" quotation; Tables 1–3 every value; the dilation reason quotation; the recursion
quotation and Fig. 8; disparity normalisation; bilateral median 7×7, 4.0, 0.5 and its reason; <10 px segments;
1024 px scaling; COCO/MegaDepth training trick, 118k images, ≤3 pairs, 5/10 epochs.

## 10. Szeliski et al., comparative study of MRF energy minimisation, ECCV 2006 — 327 lines read

✘ **The note's verdict was backwards.** It said the paper confirms S54 §4 ("the solver is not our bottleneck").
Checked against S51's own record: S51's solver was **ICM**, the one method the study finds far from the optimum
and "extremely sensitive to the initial estimate"; S51's restarts did **not** converge (438 955 / 440 523 / 507 839
/ 458–464 k — the notes said "five random seeds converging to the same answer"); S51's oracle bound (80.7 % vs 33 %)
is the signature of a weak search, as S51 itself concluded. "Our minimisation is a per-texel closed form" described
the far-side law, not S51. The note is rewritten; **S54 §4 is rewritten in place** (rule 5) to say the question is
open and settled exactly by one min-cut (two-label submodular energy).
✘ **"The cap is precisely what breaks the metric condition."** The square does; truncated L1 is a metric (Tsukuba).
Our k = 1 cap stays expansion-compatible. Corrected.
~ "Once past ICM everyone finds the same minimum" → the best methods do; LBP and swap moves do not always (§6
"dramatic difference in performance"). Added; also "The exception was the Photomontage benchmarks" restored to the
visual-quality quotation, and Teddy's 0.018 % is reached during TRW-S's oscillation.
~ "Penguin is the only benchmark with zero data cost" → Photomontage is data-free wherever images overlap, and it
is the other benchmark where methods differ visibly. Tightened.
~ "Sprint 30 should sweep" and "the sweep is over a named parameter" contradict rule 2; rewritten (derive, then
check; the self-calibrating β is the rule-2 form).
✔ §6 "unlikely to produce significantly more accurate labelings" quotation; §5 <1 %, 0.27 %, 0.13 %, 0.78 %,
0.018 %, LBP <0.04 %; the "more accurate models" caveat; the clipped monomial and Potts quotation; the expansion
condition; the Venus/Penguin non-metric quotation; Penguin's zero data cost, swap problems, TRW-S winner; w_pq = 3
/ 2; the segmentation V_pq, λ = 50, λ₂ = 10, β and the λ₂ quotation; ICM WTA initialisation; "never … swap moves";
LBP's poor showing, the floating people, the schedule hedge; TRW-S lower bound quotation; E = E_d + λE_s,
4-connected; the API quotation.

## 11. Jakubowska, Zięba & Spurek, ORCA, arXiv 2609.17450 (2026) — 314 lines read

✘ **"Six papers, six lineages" for the occludee rule** included Criminisi (no occluder in object removal) →
five. **"Three papers say the rim estimate should be a robust statistic"** counted PatchMatch's post-fill median
→ two (Ndjiki-Nya, ORCA). Corrected.
✘ **"TSED is the same kind of thing our temporal step measures."** TSED checks correspondences against camera
geometry; temporal step is frame-to-frame LPIPS. Corrected.
~ "Tuned" → the paper does not say how its three thresholds were chosen; "set" is what the text supports.
~ The distance-to-rim arm was to be judged on temporal step (A126) → rewritten as a kit-truth test conditioned on
reveal. Sprint 31 reference updated (on hold, S57). The quantile-clipping likeness to our effective-quantum work
withdrawn. "None principled except Shade's" → our fold ratio is derived too.
+ Missed: **no ablation of the local-versus-generative split** — the only comparison is against VistaDream, so the
paper does not show its own hybrid beats all-generative; the paper's concession that LLaVA-IQA criteria sometimes
favour VistaDream; sequential repair with re-rendering after each (the task #60 question, answered by
construction). Added.
✔ Header; the 9 000 px / 45 % / 64 px quotation; the two-call budget quotation; the small-or-elongated quotation;
the donor-ring quotation; ring 3/28, ≥32 donors, 78th percentile, nearest-neighbour fallback; no-reference
metrics; 99 DIV2K images and the exclusion quotation; MUSIQ 61.60 → 68.71, CLIP-IQA 0.474 → 0.574, Quality
0.407 → 0.630; the Table 2 saturation cases (steampunk, car, 0.02 → 0.00); TSED 0.8265 → 0.9980, 0.9864 → 1.0000;
Depth Pro, robust quantiles, displacement along rays and its quotation; the affine depth alignment on the ring with
outlier rejection and boundary blending; depth not a supervision signal; every §4.2 training/repair parameter;
the wider-Gaussians quotation.

## 12. Sinha, Steedly & Szeliski, Piecewise planar stereo for IBR, ICCV 2009 — 335 lines read

~ **Class 3 = crease is my mapping, not the paper's.** Class 3 is defined by our law's axis switch; whether truth
has a crease there is unestablished. "Class 3 should have continuous depth" → conditional, with the kit-truth check
that separates the two readings. This bears on task #56's premise.
~ The smoothness equation is blank in the file; the "nothing → most expensive" row was inference and is removed.
The λ's are hand-set ("chosen empirically"; "possible to learn … from training data") — rule 2 noted.
~ "Our temporal step is an edge-motion proxy" → it is frame-to-frame LPIPS; the paper's perceptual claim argues
for the screen in motion (A126). The cross-fade look re-aimed: we render one source, so the question is our
per-layer alphas.
+ Missed: §6 *"we do not handle occlusions in the scene and do not deal with large foreground objects"* — the
taxonomy transfers, the method does not; ground and back planes are from Hoiem et al. and depend on the horizon.
Added.
✔ The occlusion/crease quotation; C⁰ quotation (§1.2); crease lines and S1; S2 as VD lines with the far plane
behind; S3; λ 1000 / 1200 / 2000; the §2 "small discrete set of plane hypotheses" quotation; the §1 perceptual
and §5 cross-fade quotations and binary α; SfM, ≥4-view lines, mean-shift VDs; 28–145 min, 2–3 Mpixel, 33–127
planes; the ground-plane construction (95 %) and back-planes.

## 13. Gallup, Frahm & Pollefeys, Piecewise planar and non-planar stereo, CVPR 2010 — 414 lines read

✘ **The discard-label mechanism was argued with the perimeter cost on the wrong side** (discarding creates the
label boundary and pays λ·P; staying pays nothing). Conclusion (discard wins when A/P is large) unchanged;
reasoning corrected.
✘ **"Class 3 might be metrication."** Not in the shipped law (no MRF); metrication would shape S51-style labelling
boundaries. Corrected.
~ The smoothness equation is blank in the file, and d_min = 2 vs d_max = 0.2 m cannot be one clamped distance;
the notes' formula is now marked as a reconstruction and d_min read as a penalty floor.
~ "d_min is aimed straight at class 1" → a hypothesis with its limits (S51: class 1 is not an axis-choice problem;
a switch between agreeing candidates changes nothing visible). Floor/cap values must be derived (rule 2); Sprint
30 on hold.
~ "Subsumes the shape-vs-reveal concern" → takes a side (compactness) that the kit-truth test must check. "New
task" had not been created; now pointed at LIVE_PASS §10.
~ The bush/sloping-ground quotation is §1, not §3.4. "Harder, more varied dataset" → one rig's street video; the
insensitivity claim is asserted, not analysed; parameters hand-chosen. The 94.7 / 97.2 % figures are
classification, not depth accuracy.
+ Missed: relative-to-median distances as a self-calibration; §1 "simplified geometry can often look better".
Added.
✔ The non-plane-label quotation and ρ_bias 0.5 / ρ_max 6; the discard-label quotation; the d_min/d_max quotation
and λ_smooth 5, d_min 2, d_max 0.2 m, γ 10; π∞ quotation; the RANSAC recipe (σ 8, M 100, MLESAC, contiguity,
N 20) and its quotation; the §4 parameters quotation; 22 700 segments in 28 images; the classifier (16×16 grid,
features, edge-orientation quotation, ~5 000 segments, kNN, λ_class 2, no hard decision); the metrication
quotation.

## 14. Banz, Pirsch & Blume, Penalty functions for SGM, ISPRS 2012 — 814 lines read

✘ **Misquotation.** "All [adaptive] functions are insensitive to … non-optimal parametrization" — the original
says "All functions", the constant included. The bracket reversed part of the paper's point. Corrected.
✘ **"Our input is noisy, so expect the 7-point AWGN gain."** Banz degrades the intensity image (matching cost and
the |ΔI| the penalty reads); our measured noise is in the depth map. Transfer withdrawn; only "constant penalties
are brittle across conditions" carries.
✘ **"Tune on the noisiest picture"** is per-image tuning (rule 2). Rewritten: constants derived; *check* first on
the noisiest picture. The same fix applied to the Sprint 30 bullet list ("sweep α, γ, floor, cap").
~ "Banz's P2,min is a floor for our reason" → it only keeps P2 ≥ P1; one paper (Gallup), not two, argues the floor.
"Scharstein's V_max" → Szeliski et al.'s.
~ The Fig. 6 explanation of why the reciprocal keeps thin structures is my inference (the plot is lost in this
file; the paper says only the two curves are similar). Marked. "Sweep both" → carry both forms.
+ Missed: the reciprocal also wins under salt-and-pepper with census (7.40 vs 8.27 %); the linear wins big under
AWGN with rank (32.61 vs 40.61 %); the constant beats the linear under salt-and-pepper (7.63 vs 8.27 %); the clean-
image cost of the degraded-condition parameter sets (6.27 %, 5.37 % vs 5.23 %); the real-image check is visual
only; the "sophisticated image preprocessing" caution. Added.
✔ The four forms and their quotations (the reciprocal's fraction reassembled); Table 1 census values; the "does not
result in any performance improvement" and 6.05 / 5.91 % quotations; the β quotation; the thin-structure
quotation; the rank quotation; the variance quotation; the clipping quotation; Table 2 census values; 0.15 / 7.4
points, ×4.9; the conclusion quotation; the three parameter sets and α = 0.5; the degraded-configuration
quotations; the constant-brittleness and 0.5-point transfer quotations; the no-post-processing and hole-bias
quotations.

## 15–17. Daribo & Pesquet-Popescu (MMSP 2010, 194 lines), Daribo & Saito (T-BC 2011, 246 lines), Gautier, Le Meur & Guillemot (3DTV 2011, 130 lines) — all read

✘ **"Not LDI (rejected on bandwidth)."** Daribo 2011 is an LDV paper; it uses inpainting to shrink the layered
residual. Daribo 2010 says only that LDI adds "overhead complexity". Corrected.
✘ **Baselines of ~65 mm and twice that** were Ndjiki-Nya's numbers, attributed to Daribo. The Daribo papers state
no baseline. Corrected.
✘ **PSNR "above Criminisi throughout by a visually small margin"** — the curves are lost in the file; only the axis
ranges survive. The claim is withdrawn; the text's own sentence quoted instead.
~ Gautier cites the 2010 version only and shares Daribo's code, so the two are one lineage; the occludee-rule count
is now 6th/7th (after the paper-7 and paper-11 corrections), not 7th/8th. "DIBR settled on" → "this lineage".
~ "S33 measures what diffusing depth produces" → S33 measured our law's ramps, the same failure a smooth fill
has. Envelope sentences updated to the ±90° target. "Must be swept" (K) → derive and check on screen (rule 2,
A126). The "fifth robust statistic … overwhelming" → a consistent instinct acting at different stages. Shih's
dilation claim restated to what Table 3 shows. The detachment check is not on the task list; said so.
+ Missed: Gautier's depth channel is the supplied depth of the final view ("depth inpainting … out of the scope"),
so his 3-D tensor had true depth in the hole; crack filling by averaging (a two-tier rule); out-of-field strip
filling (the frame-edge problem); Daribo 2011's argument against depth pre-filtering. Added.
✔ Titles, venues, line counts; Criminisi "makes no distinction"; Oh's boundary swap; P = C·D·L and the L(p)
formula; the "naturally favors background" quotation (and the critique of it, which stands); the β patch
distance; the depth-diffusion and "texture-less" quotations and Navier–Stokes; the one-reference-view and
"fewer disocclusions" quotations; the Di Zenzo tensor, D(p) formula and flat/edge quotation; the RGBZ tensor and
its quotation; the one-side-only quotation; α_Z = 3, α_RGB = 1, K = 5, Wexler et al.; the smoothing-counterpart
quotation; the anti-ghosting quotation; the Oh-connexity quotation; the disoccluded-only PSNR quotation; the
"essentially address visually" quotation.
