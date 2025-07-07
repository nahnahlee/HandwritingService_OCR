# backend/inference.py

import os
import argparse
from PIL import Image
import torch
from torchvision import transforms
from models import create_model  # FUNIT 레포 구조에 맞게 import

def load_image(path, size=256):
    img = Image.open(path).convert("RGB")
    tf = transforms.Compose([
        transforms.Resize(size),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize((.5,)*3, (.5,)*3),
    ])
    return tf(img).unsqueeze(0)

def save_image(tensor, out_path):
    img = tensor.detach().cpu().squeeze(0)
    img = (img * .5 + .5).clamp(0,1)
    transforms.ToPILImage()(img).save(out_path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--content", required=True)   # skeleton image
    p.add_argument("--style",   required=True)   # user handwriting sample
    p.add_argument("--checkpoint_dir", default="FUNIT/checkpoints/handwriting_funit")
    p.add_argument("--out",     required=True)
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # 1) 모델 로드
    model = create_model(args.checkpoint_dir, phase="test", n_shot=5)
    model.eval()

    # 2) 이미지 준비
    content = load_image(args.content)
    style   = load_image(args.style)

    # 3) inference
    with torch.no_grad():
        fake, _ = model(content, style)
    save_image(fake, args.out)
