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
