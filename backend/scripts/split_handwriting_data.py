# backend/scripts/split_handwriting_data.py

import os
import random

def write_all_A(domain_dir: str, out_dir: str):
    """A 폴더의 모든 이미지 이름만 모아서 train_A.txt에 저장"""
    fnames = sorted(
        fn for fn in os.listdir(domain_dir)
        if fn.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    path = os.path.join(out_dir, "train_A.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(fnames))
    print(f"✅ A 도메인 전체 작성 → {path} ({len(fnames)}개)")

def split_user(domain_dir: str, out_dir: str, prefix: str="user", ratio: float=0.8):
    """
    B/user 폴더만 랜덤 섞어서
    train_user.txt / test_user.txt 로 분할합니다.
    리스트 안에는 상대경로 ‘user/파일명’ 만 기록.
    """
    fnames = sorted(
        fn for fn in os.listdir(domain_dir)
        if fn.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    rel = [f"{prefix}/{fn}" for fn in fnames]
    random.seed(42)
    random.shuffle(rel)
    n_train = int(len(rel)*ratio)
    train, test = rel[:n_train], rel[n_train:]

    for name, lst in [("train_user.txt", train), ("test_user.txt", test)]:
        p = os.path.join(out_dir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lst))
        print(f"✅ user 도메인 {name} 작성 → {p} ({len(lst)}개)")

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "data", "hand"
    ))

    # 1) A: 모든 글자 전부 학습(train only)
    write_all_A(os.path.join(base, "A"), base)

    # 2) user: 80% train / 20% test
    split_user(os.path.join(base, "B", "user"), base)
