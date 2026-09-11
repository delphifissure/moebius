import sys, zipfile, io, json
from PIL import Image
z = zipfile.ZipFile(sys.argv[1])
print(f"{'file':40s} {'bytes':>9s}  mode   bits  size")
for n in z.namelist():
    b = z.read(n)
    if n.endswith('.png'):
        im = Image.open(io.BytesIO(b)); bits = {'I;16':16,'I;16B':16,'I':32,'F':32}.get(im.mode, 8)
        print(f"{n:40s} {len(b):9d}  {im.mode:5s}  {bits:3d}  {im.size[0]}x{im.size[1]}")
    else:
        print(f"{n:40s} {len(b):9d}")
m = json.loads(z.read('meta.json'))
print('meta keys:', sorted(m.keys()))
