import os
from PIL import Image
import torch.utils.data as data


def default_loader(path: str):
    """
    이미지를 열어서 RGB로 변환해 반환합니다.
    """
    return Image.open(path).convert('RGB')


def default_filelist_reader(filelist: str):
    """
    filelist 파일을 읽어서
    각 줄을 "경로 레이블" 형태로 해석해
    [(경로, 레이블), ...] 리스트를 반환합니다.
    레이블이 없으면 0으로 간주합니다.
    """
    im_list = []
    with open(filelist, 'r', encoding='utf-8') as rf:
        for raw in rf:
            line = raw.strip()
            if not line:
                continue
            parts = line.split()
            # "경로 레이블" or just "경로"
            path = parts[0]
            label = int(parts[1]) if len(parts) > 1 else 0
            im_list.append((path, label))
    return im_list


class ImageLabelFilelist(data.Dataset):
    """
    path와 label을 직접 filelist에서 읽어오는 Dataset.
    get_train_loaders()에서 사용됩니다.
    """
    def __init__(
        self,
        root: str,
        filelist: str,
        transform=None,
        filelist_reader=default_filelist_reader,
        loader=default_loader,
        return_paths: bool = False
    ):
        self.root = root
        # [(경로, 레이블), ...] 형태로 로드
        self.imgs = filelist_reader(filelist)
        self.transform = transform
        self.loader = loader
        self.return_paths = return_paths

        # 몇 개의 클래스가 있는지 로그로 표시해 줍니다.
        classes = sorted(set(label for _, label in self.imgs))
        print("Data loader")
        print(f"\tRoot: {self.root}")
        print(f"\tList: {filelist}")
        print(f"\tNumber of classes: {len(classes)}")

    def __getitem__(self, index: int):
        im_path, label = self.imgs[index]
        full_path = os.path.join(self.root, im_path)
        img = self.loader(full_path)
        if self.transform is not None:
            img = self.transform(img)
        if self.return_paths:
            return img, label, full_path
        return img, label

    def __len__(self) -> int:
        return len(self.imgs)
