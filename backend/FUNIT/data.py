"""
Copyright (C) 2019 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license
(https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""
import os
from PIL import Image
import torch.utils.data as data


def default_loader(path):
    return Image.open(path).convert('RGB')


def default_filelist_reader(filelist):
    """
    filelist 파일의 각 줄을
      rel/path.png
    또는
      rel/path.png LABEL
    형식으로 읽고,
    (path, label) 튜플 리스트를 반환합니다.
    LABEL이 없으면 0을 기본값으로 사용합니다.
    """
    entries = []
    with open(filelist, 'r', encoding='utf-8') as rf:
        for raw in rf:
            line = raw.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 1:
                entries.append((parts[0], 0))
            else:
                try:
                    label = int(parts[1])
                except ValueError:
                    label = 0
                entries.append((parts[0], label))
    return entries


class ImageLabelFilelist(data.Dataset):
    """
    filelist 안의 (rel_path, label) 쌍을 읽어
    root/rel_path 에서 이미지를 로드하고,
    (img_tensor, label) 을 반환합니다.
    """
    def __init__(self,
                 root,
                 filelist,
                 transform=None,
                 filelist_reader=default_filelist_reader,
                 loader=default_loader,
                 return_paths=False):
        self.root = root
        # 읽어서 [(rel_path, label), ...] 리스트로 저장
        self.imgs = filelist_reader(filelist)
        self.transform = transform
        self.loader = loader
        self.return_paths = return_paths

        # 클래스 수는 레이블의 유니크 개수
        labels = [lab for _, lab in self.imgs]
        self.classes = sorted(set(labels))
        self.num_classes = len(self.classes)

        print('Data loader')
        print(f"\tRoot: {self.root}")
        print(f"\tList: {filelist}")
        print(f"\tNumber of classes: {self.num_classes}")

    def __getitem__(self, index):
        rel_path, label = self.imgs[index]
        img = self.loader(os.path.join(self.root, rel_path))
        if self.transform is not None:
            img = self.transform(img)
        if self.return_paths:
            return img, label, os.path.join(self.root, rel_path)
        else:
            return img, label

    def __len__(self):
        return len(self.imgs)
