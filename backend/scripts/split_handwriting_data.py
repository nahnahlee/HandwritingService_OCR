# backend/scripts/split_handwriting_data.py

import os
import random

def split_domain(domain_dir: str, out_dir: str, prefix: str, train_ratio: float = 0.8):
    """
    domain_dir 에 있는 .png 파일을 읽어서
    train_ratio 비율만큼 train_<prefix>.txt, 나머지를 test_<prefix>.txt 에 기록합니다.
    """
    # 1) 파일 목록 수집
    imgs = [
        os.path.join(domain_dir, fname)
        for fname in os.listdir(domain_dir)
        if fname.lower().endswith(".png")
    ]
    if not imgs:
        print(f"⚠️  {domain_dir} 에는 PNG 파일이 없습니다.")
        return

    # 2) 섞고 분할
    random.seed(42)
    random.shuffle(imgs)
    n_train = int(len(imgs) * train_ratio)
    train_list = imgs[:n_train]
    test_list  = imgs[n_train:]

    # 3) out_dir 가 없으면 생성
    os.makedirs(out_dir, exist_ok=True)

    # 4) 파일 쓰기
    train_path = os.path.join(out_dir, f"train_{prefix}.txt")
    test_path  = os.path.join(out_dir, f"test_{prefix}.txt")
    with open(train_path, "w", encoding="utf-8") as f:
        f.write("\n".join(train_list))
    with open(test_path, "w", encoding="utf-8") as f:
        f.write("\n".join(test_list))

    print(f"✅ {prefix} 도메인 분할 완료: {len(train_list)} train, {len(test_list)} test")
    print(f"   → {train_path}")
    print(f"   → {test_path}")

if __name__ == "__main__":
    # data/hand/B 만 분할하도록 변경
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "hand")
    )
    domain_dir = os.path.join(base, "B")
    print(f"▶️ base        = {base}")
    print(f"▶️ domain_dir  = {domain_dir}")
    split_domain(os.path.join(base, "B"), base, "B")
