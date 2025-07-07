# backend/convert_cli.py
import argparse
from PIL import Image, ImageDraw, ImageFont
import os

def render_text(text, out_path):
    img = Image.new("RGB", (800,200), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 48)
    draw.text((10,10), text, fill="black", font=font)
    img.save(out_path)

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--text", required=True)
    p.add_argument("--out",  required=True)
    args = p.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    render_text(args.text, args.out)
