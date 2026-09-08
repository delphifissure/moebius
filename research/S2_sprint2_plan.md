# Sprint 2 — the quick-bake fix, behind flags (started 2026-09-08)

Inputs: S1 report §5/§5c (the band's anatomy and the fold-tear cause), CODEMAP §10–§13 and §18b
(the sweep's hole rule), R3 (sky at infinity, class-aware far side), the user's envelope decision
(±45° horizontal, ±30° vertical from centre).

## 2a — the envelope (shipped, not flagged: it is the user's spec)

- `bgViewFadeEndDegV = 30`; `bgEnvAspect() = tan30/tan45 = 0.577` replaces the window-aspect
  rule (0.5625) in the per-fragment pose fraction, the CPU sweep grid and the sweep bake;
  `bgFadeFrac` puts the 35/45 fade on the rectangular envelope (start at 0.700 of either rim).
- Truth kit: `reveal.py` vertical extent = tan30/tan45; env45 truths regridded to thy = 0, 15, 30
  (were 0, 15.7, 29.4 from the window aspect) for all nine scenes, sky classes included.

## 2b — the rim tear law (`window._tearLaw = 'rim'`)

- `bgRimLawFor(pw, ph)`: joined(a, b) iff max(ze)/min(ze) ≤ t on the app's own depth law,
  ze = D − z(d); t = 1 + (hfov/pw)/tan(g_min), g_min = 2° (`window._rimGrazeDeg`). Resolution- and
  volume-invariant by construction; the constant is an angle with a stated meaning.
- CPU sweep: a foreground quad is drawn iff its four edges are joined (point splats otherwise);
  the fold-based `torn` set is not consulted for drawing when the flag is on. The A212 baked FG
  tear and the a160 torn footprint use the same edge test (no fold test, no demand gate), so the
  rendered mesh and the sweep agree.
- The far field's anchor is the reach of every unjoined edge (|shift(far) − shift(near)| at the
  envelope rim along the edge's axis), not the far rims alone (membrane sags under rim-less
  surfaces) and not pass 1's band (imports its misses). The sweep's plate pass warps that field and
  names the demand texel per hole cell. Added after the first A/B rounds; see the report §1.
- A/B: 16-bit bakes of S2, S16, S27, S15, S12, S26 with the flag, scored with `check_app_band`
  against the regridded truths; arms must diverge (a134) and the buffers are looked at (a196).
  Results: `S2_sprint2_report.md`.
- Expected from the geometry: floors/ceilings leave the band (no reveal opens on a continuous
  plane); object silhouettes keep it; S16's crease stays joined and its jump tears.

## 2c — sky at infinity (`window._skyInf`)

- Sky texels (source minimum within a quantum, or a supplied mask) and plate texels whose far lip
  is sky are displaced with z → −Z_inf so shift → −e (the plane-at-infinity law, R3 §2).
- Sky margin: the A245 ring at e_max per side (1.25 W at 45°) for sky rows.
- Scored on S15 (sky reveal recall, band precision) and by the sky's measured parallax against
  the closed form −e. Done: report §1 (2c) — 0.998 e measured on the screen, band unchanged.
- Added in the same pass: S2b.3, the grazing-plane rescue in the rim law (S15's horizon strip).

## Not in this sprint

- A segmentation model for the sky on real photographs (R3 D1 needs it; the kit's sky is exact).
- The disparity-space depth law (R3 D5) as a default: flagged experiment at most.
- Anything that changes a default's geometry ships only after the user's live pass.
