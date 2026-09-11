#!/usr/bin/env python3
"""maps sheet (each model at 8 bits + difference to the DA2 map) and one angle sheet per model. Usage: sheets.py <model> ..."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'; B=SP+'/bakeoff'; U='/home/user/moebiusv2/harness/shots/ui_path/'
ref=np.array(Image.open(SP+'/depth16_pushed.png')).astype(float)/257; models=sys.argv[1:]
tiles=[('DA2-Large (baseline)', ref, None)]
for m in models:
    p=f'{B}/out/{m}_disp16.png'
    if os.path.exists(p): a=np.array(Image.open(p)).astype(float)/257; tiles.append((m, a, a-ref))
    else: tiles.append((m+' (not run)', np.zeros_like(ref), None))
H,W=ref.shape; sheet=Image.new('L',(W*len(tiles),H*2+24),40); d=ImageDraw.Draw(sheet)
for i,(lab,a,df) in enumerate(tiles):
    sheet.paste(Image.fromarray(a.clip(0,255).astype(np.uint8)),(i*W,24)); d.text((i*W+8,6),lab+'  (bright = near)',fill=255)
    if df is not None: sheet.paste(Image.fromarray((df*3+128).clip(0,255).astype(np.uint8)),(i*W,24+H))
    d.text((i*W+8,24+H+6),'difference to DA2 x3' if df is not None else '',fill=255)
sheet.save(B+'/bo_maps_sheet.png'); print('maps sheet', sheet.size)
offs=[('0.1_0','27°'),('0.2_0','45°'),('0.26_0.088','52°/24°'),('0.301_0.068','56°/19°')]
rows=[('DA2-Large 8-bit','ui_16q8')]+[(m+' 8-bit','ui_bo_'+m) for m in models if os.path.isdir(U+'ui_bo_'+m)]
im0=Image.open(f'{U}ui_16q8/off_{offs[0][0]}.png'); w,h=im0.size
sheet=Image.new('RGB',(w*len(offs),(h+24)*len(rows)),(30,30,30)); d=ImageDraw.Draw(sheet)
for r,(lab,dirn) in enumerate(rows):
    for c,(o,ang) in enumerate(offs):
        f=f'{U}{dirn}/off_{o}.png'
        if os.path.exists(f): sheet.paste(Image.open(f).convert('RGB'),(c*w,r*(h+24)+24))
        d.text((c*w+6,r*(h+24)+6),f'{lab} | eye {o.replace("_",", ")} m ({ang}) | seams stretched',fill=(255,255,255))
sheet.save(B+'/bo_angles_sheet.png'); print('angles sheet', sheet.size)
