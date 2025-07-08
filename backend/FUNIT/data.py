from PIL import Image
import os
import torch.utils.data as data


def default_loader(path):
    return Image.open(path).convert('RGB')


def default_filelist_reader(filelist):
    """
    파일 리스트를 읽어들입니다. 각 줄에 "경로 레이블" 형식이 있을 경우, 레이블을 파싱하여 저장합니다.
    """
    items = []
    with open(filelist, 'r', encoding='utf-8') as rf:
        for line in rf:
            parts = line.strip().split()
            if not parts:
                continue
            img_path = parts[0]
            # 두 번째 토큰이 있으면 레이블, 없으면 0으로
            label = int(parts[1]) if len(parts) > 1 else 0
            items.append((img_path, label))
    return items


class ImageLabelFilelist(data.Dataset):
    def __init__(self,
                 root,
                 filelist,
                 transform=None,
                 filelist_reader=default_filelist_reader,
                 loader=default_loader,
                 return_paths=False):
        self.root = root
        # filelist_reader 리턴값이 (path, label) 튜플 리스트
        self.imgs = filelist_reader(filelist)
        self.transform = transform
        self.loader = loader
        self.return_paths = return_paths

        # 도메인 개수는 파일에 들어있는 유니크 레이블 수
        labels = sorted(set(label for _, label in self.imgs))
        print('Data loader')
        print(f"\tRoot: {self.root}")
        print(f"\tList: {filelist}")
        print(f"\tNumber of classes: {len(labels)}")

    def __getitem__(self, index):
        rel_path, label = self.imgs[index]
        full_path = os.path.join(self.root, rel_path)
        img = self.loader(full_path)
        if self.transform is not None:
            img = self.transform(img)
        if self.return_paths:
            return img, label, full_path
        return img, label

    def __len__(self):
        return len(self.imgs)
