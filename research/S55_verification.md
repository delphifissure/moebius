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
