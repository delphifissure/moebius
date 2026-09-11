#!/usr/bin/env python3
"""c_views_check.py <audit dir> [poses]: per pose, the set of pixels the SD-regions view tints (sd frame != plain frame)
against the placeholder-only check view (white). Reports both sets and their symmetric difference in pixels / % of frame."""
import sys, os, numpy as np
from PIL import Image
D = sys.argv[1]; poses = sys.argv[2:] or ['0_0', '0.6_0', '1_m0.5']
print(f"{'pose':8s} {'tinted%':>8s} {'white%':>8s} {'tinted&!white':>14s} {'white&!tinted':>14s} {'symdiff%':>9s}  (counts in px; frame = plain frame)")
for p in poses:
    fp = os.path.join(D, f'plain_{p}.png'); fs = os.path.join(D, f'sd_{p}.png'); fw = os.path.join(D, f'paint_{p}.png')
    if not (os.path.exists(fp) and os.path.exists(fs) and os.path.exists(fw)): print(p, 'missing frames'); continue
    a = np.asarray(Image.open(fp).convert('RGB')).astype(int); b = np.asarray(Image.open(fs).convert('RGB')).astype(int); w = np.asarray(Image.open(fw).convert('RGB')).astype(int)
    dimmed = (np.abs(b - 0.35 * a).max(-1) < 10) & (a.max(-1) > 30); tinted = (np.abs(a - b).max(-1) > 12) & ~dimmed; white = (w.min(-1) > 200); black = (w.max(-1) < 40); grey = ~(white | black)
    n = tinted.size; t_nw = int((tinted & ~white).sum()); w_nt = int((white & ~tinted).sum())
    onEdge = int(((tinted & ~white) & grey).sum())
    print(f'{p:8s} {100*tinted.mean():8.2f} {100*white.mean():8.2f} {t_nw:14d} {w_nt:14d} {100*(t_nw+w_nt)/n:9.3f}   (of the tinted-not-white, {onEdge} are anti-aliased edge pixels in the check view; check-view grey total {int(grey.sum())})')
    # where do the disagreements sit? save a map: red = tinted not white, green = white not tinted
    m = np.zeros(a.shape, np.uint8); m[tinted & ~white] = (255, 60, 60); m[white & ~tinted] = (60, 255, 60); m[tinted & white] = (200, 200, 200)
    Image.fromarray(m).save(os.path.join(D, f'agree_{p}.png'))
