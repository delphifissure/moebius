#!/usr/bin/env python3
"""S9 angle sheet: DA3 8-bit | DA3 16-bit grid tolerance | DA3 16-bit noise term (+ DA2 16-bit noise term) at four eye offsets."""
import os
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'; U='/home/user/moebiusv2/harness/shots/ui_path/'
offs=[('0.1_0','27°'),('0.2_0','45°'),('0.26_0.088','52°/24°'),('0.301_0.068','56°/19°')]
rows=[('DA3 8-bit','ui_bo_da3mono'),('DA3 16-bit, 1/255 fallback (§13)','ui_da3_16'),('DA3 16-bit, grid only 1/65535 (floor off)','ui_da3_s10g'),('DA3 16-bit, visible-step floor (final)','ui_da3_s10d'),('DA2 16-bit, 1/255 fallback','ui_16bit'),('DA2 16-bit, visible step, a86 at grid','ui_da2_s10a')]
rows=[r for r in rows if os.path.isdir(U+r[1])]
im0=Image.open(f'{U}{rows[0][1]}/off_{offs[0][0]}.png'); w,h=im0.size
sheet=Image.new('RGB',(w*len(offs),(h+24)*len(rows)),(30,30,30)); d=ImageDraw.Draw(sheet)
for r,(lab,dirn) in enumerate(rows):
    for c,(o,ang) in enumerate(offs):
        f=f'{U}{dirn}/off_{o}.png'
        if os.path.exists(f): sheet.paste(Image.open(f).convert('RGB'),(c*w,r*(h+24)+24))
        d.text((c*w+6,r*(h+24)+6),f'{lab} | eye {o.replace("_",", ")} m ({ang}) | seams stretched',fill=(255,255,255))
sheet.save(SP+'/s10_angles_sheet.png'); print('s9 angles sheet', sheet.size, [r[1] for r in rows])
