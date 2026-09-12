#!/usr/bin/env python3
"""S13a: the troll under the current despeckle (base) vs the line-aware rule (lines): shots at 0.1, 0.2, (0.301,0.068) m, plus a 3x zoom
of the region with the most pixel difference between the arms at 0.2 m."""
import os, sys, numpy as np
from PIL import Image, ImageDraw
U='/home/user/moebiusv2/harness/shots/ui_path'; OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'
SH=['0.1_0','0.2_0','0.301_0.068']; rows=[]
for arm in ['base','lines']:
    tiles=[Image.open(f'{U}/s13_troll_{arm}/off_{s}.png').convert('RGB') for s in SH]; rows.append((arm,tiles))
a=np.asarray(rows[0][1][1]).astype(int); b=np.asarray(rows[1][1][1]).astype(int); d=np.abs(a-b).max(-1)
print('pixels differing at 0.2 m (>12):', int((d>12).sum()), 'of', d.size)
ys,xs=np.nonzero(d>12); 
if len(xs): cx,cy=int(np.median(xs)),int(np.median(ys))
else: cx,cy=a.shape[1]//2,a.shape[0]//2
box=(max(0,cx-80),max(0,cy-60),min(a.shape[1],cx+80),min(a.shape[0],cy+60))
w,h=rows[0][1][0].size; W=w*3+8; H=(h+18)*2+ (box[3]-box[1])*3+24
sheet=Image.new('RGB',(W,H),(18,18,18)); dr=ImageDraw.Draw(sheet); y=0
for arm,tiles in rows:
    dr.text((4,y),f'troll — despeckle {arm}   [0.1 m | 0.2 m | 0.301/0.068 m]',fill=(255,255,255)); y+=16
    for k,t in enumerate(tiles): sheet.paste(t,(k*(w+4),y))
    y+=h+2
dr.text((4,y),f'zoom x3 at 0.2 m around the largest difference: base | lines',fill=(255,255,255)); y+=16
for k,(arm,tiles) in enumerate(rows): sheet.paste(tiles[1].crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.NEAREST),(k*((box[2]-box[0])*3+8),y))
sheet.save(f'{OUT}/s13_troll_sheet.png'); print(sheet.size, box)
