# backend/scripts/check_size.py
from PIL import Image
paths = [
    "data/hand/A/AC00.png",   # '가'
    "data/hand/A/AC01.png",   # '각' 등
]
for p in paths:
    img = Image.open(p)
    print(p, "→", img.size)
