# backend/scripts/split_handwriting_data.py

import os
import random

def split_domain(domain_dir: str,
                 out_dir: str,
                 prefix: str,
                 train_ratio: float = 0.8):
    """
    domain_dir 안의 이미지 파일을
    train_ratio 비율로 train_<prefix>.txt / test_<prefix>.txt 로 분할합니다.
    리스트 안에는 상대경로(prefix/파일명)를 '/' 로 통일해 기록합니다.
    """
    # 1) PNG/JPG 파일만 골라서, 이름만
    fnames = sorted([
        fn for fn in os.listdir(domain_dir)
        if fn.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    if not fnames:
        print(f"⚠️  {domain_dir}에 이미지가 하나도 없습니다.")
        return

    # 2) 상대경로 생성 및 슬래시 통일
    rel_paths = [
        os.path.join(prefix, fn).replace("\\", "/")
        for fn in fnames
    ]

    # 3) shuffle & split
    random.seed(42)
    random.shuffle(rel_paths)
    n_train = int(len(rel_paths) * train_ratio)
    train_list = rel_paths[:n_train]
    test_list  = rel_paths[n_train:]

    # 4) 결과 파일 쓰기
    os.makedirs(out_dir, exist_ok=True)
    train_path = os.path.join(out_dir, f"train_{prefix.replace('/', '_')}.txt")
    test_path  = os.path.join(out_dir, f"test_{prefix.replace('/', '_')}.txt")

    with open(train_path, "w", encoding="utf-8") as f:
        f.write("\n".join(train_list))
    with open(test_path, "w", encoding="utf-8") as f:
        f.write("\n".join(test_list))

    print(f"✅ {prefix} 도메인 분할 완료: {len(train_list)} train, {len(test_list)} test")
    print(f"   → {train_path}")
    print(f"   → {test_path}\n")


if __name__ == "__main__":
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "hand")
    )
    domain_dir = os.path.join(base, "B", "user")
    prefix     = "B/user"

    print(f"▶️ base       = {base}")
    print(f"▶️ domain_dir = {domain_dir}\n")

    split_domain(domain_dir, base, prefix)
