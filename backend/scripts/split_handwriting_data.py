# backend/scripts/split_handwriting_data.py

import os, random

def write_all_A(domain_dir, out_dir):
    """A 도메인의 모든 파일을 파일명만으로 train_A.txt 에 저장합니다."""
    fnames = sorted(fn for fn in os.listdir(domain_dir) if fn.lower().endswith(".png"))
    path = os.path.join(out_dir, "train_A.txt")
    with open(path, "w", encoding="utf-8") as f:
        for fn in fnames:
            f.write(fn + "\n")
    print("✅ A 도메인(train_A.txt) 작성 완료:", path)

def split_user(domain_dir, out_dir, prefix="user", label=1, ratio=0.8):
    """B/user 도메인을 train_user.txt/test_user.txt 로 나눕니다."""
    fnames = sorted(fn for fn in os.listdir(domain_dir)
                    if fn.lower().endswith((".png", ".jpg", ".jpeg")))
    rels = [f"{prefix}/{fn} {label}" for fn in fnames]
    random.seed(42)
    random.shuffle(rels)
    n = int(len(rels) * ratio)
    for name, lst in [("train_user.txt", rels[:n]), ("test_user.txt", rels[n:])]:
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lst))
        print(f"✅ user 도메인({name}) 작성 완료:", path)

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "hand"))

    # 1) A 도메인은 전부 학습만 → train_A.txt (레이블 없이 파일명만)
    write_all_A(os.path.join(base, "A"), base)

    # 2) B/user 도메인 → train_user.txt / test_user.txt (경로+레이블)
    split_user(os.path.join(base, "B", "user"), base)
