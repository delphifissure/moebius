#!/usr/bin/env python3
"""Markdown tables from out/scores.json for the S26 note: hidden-layer depth median |error| in metres per scene, per
set (bg = background / other thing behind the object; own = the object's own back faces; peel1 = both), per arm.
Model arms: global visible fit + ordering clamp (the stack's honest default), local fit, oracle (shape bound).
Also a per-scene 'as % of the hidden depth p95' view so the miniature scenes and S15/S32 read on one scale."""
import json, os, sys
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); d = json.load(open(f'{OUT}/scores.json'))
MODELS = [m for m in ('da3', 'moge3', 'depthlab', 'depthlab1') if any(m in R for R in d.values())]
def g(R, m, k, key='median_abs', sub='hidden_clamped'):
    e = R.get(m, {}).get('peel1' if k == 'own' else k)
    if not e: return None
    blk = e.get(('own_clamped' if sub == 'hidden_clamped' else 'own') if k == 'own' else sub)
    return None if not blk else blk.get(key)
def f(v, pct=None):
    if v is None: return '–'
    return f'{v:.4f}' if pct is None else f'{v:.4f} ({100*v/pct:.0f}%)'
lines = []
for k, title in (('bg', 'background and other-thing layers (classes 2/3)'), ('own', "the object's own back faces (classes 4/5)"), ('peel1', 'first hidden layer, all classes')):
    lines.append(f'\n**{title}** — median |error| in metres (in brackets: % of the set\'s hidden-depth p95)\n')
    hdr = '| scene | scene depth | n | plane law |' + ''.join(f' {m} clamp | {m} local |' if k != 'own' else f' {m} clamp |' for m in MODELS) + ' oracle (best model) |'
    lines.append(hdr); lines.append('|' + '---|' * (hdr.count('|') - 1))
    for S, R in d.items():
        n = R['hidden_px'].get(k, 0)
        if not n: continue
        p95 = R['hidden_depth_p5_p95'].get('peel1' if k == 'own' else k, [None, None])[1]
        pl = R.get('plane', {}).get(k) or {}; row = f"| {S} | {R['outer']} | {n} | {f(pl.get('median_abs'), p95)} |"
        ors = []
        for m in MODELS:
            row += f" {f(g(R, m, k), p95)} |"
            if k != 'own':
                row += f" {f(g(R, m, k, sub='local'), p95)} |"
                o = g(R, m, k, sub='oracle'); ors.append(o if o is not None else 9e9)
        row += f" {f(min(ors), p95) if ors and min(ors) < 9e9 else '–'} |"
        lines.append(row)
# wins
lines.append('\n**Wins (median |error|, global fit + clamp vs the plane law)**\n')
for k in ('bg', 'own', 'peel1'):
    for m in MODELS:
        w = t = 0
        for S, R in d.items():
            a = (R.get('plane', {}).get(k) or {}).get('median_abs'); b = g(R, m, k)
            if a is None or b is None: continue
            t += 1; w += b < a
        if t: lines.append(f'- {k}: {m} beats the plane law on {w} of {t} scenes')
open(f'{OUT}/tables.md', 'w').write('\n'.join(lines)); print('\n'.join(lines))
