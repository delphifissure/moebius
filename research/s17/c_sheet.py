#!/usr/bin/env python3
"""c_sheet.py <before dir> <after dir> <out.png>: rows = poses, cols = plain | SD view before | SD view after | placeholder check view (after)"""
import sys, os
from PIL import Image, ImageDraw
B, A, OUT = sys.argv[1:4]; poses = ['0_0', '0.6_0', '1_m0.5']; labels = ['rest', 'fx 0.6', 'fx 1.0 fy -0.5']
cols = [('plain', A, 'plain (after)'), ('sd', B, 'SD regions BEFORE'), ('sd', A, 'SD regions AFTER'), ('paint', A, 'placeholder check (white)')]
im0 = Image.open(os.path.join(A, 'plain_0_0.png')); w, h = im0.size; sc = 0.6; W, H = int(w*sc), int(h*sc); pad = 18
sheet = Image.new('RGB', (W*len(cols), (H+pad)*len(poses)+pad), (20,20,20)); d = ImageDraw.Draw(sheet)
for c,(k,dd,lab) in enumerate(cols): d.text((c*W+4, 2), lab, fill=(255,255,255))
for r,p in enumerate(poses):
    for c,(k,dd,lab) in enumerate(cols):
        f = os.path.join(dd, f'{k}_{p}.png')
        if os.path.exists(f): sheet.paste(Image.open(f).convert('RGB').resize((W,H)), (c*W, pad + r*(H+pad)))
    d.text((4, pad + r*(H+pad) + H + 2), labels[r], fill=(255,255,255))
sheet.save(OUT); print(OUT, sheet.size)
