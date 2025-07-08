# backend/scripts/merge_AB.py

import os
import random

def merge_ab(a_list, b_list, out_list,
             prefix_a="A", prefix_b="B/user", shuffle=True):
    # A, B/user 리스트를 읽어서
    with open(a_list, 'r', encoding='utf-8') as fa:
        a_lines = [ln.strip() for ln in fa if ln.strip()]
    with open(b_list, 'r', encoding='utf-8') as fb:
        b_lines = [ln.strip() for ln in fb if ln.strip()]

    # 상대경로로 prefix 붙이기
    merged = [f"{prefix_a}/{ln}" for ln in a_lines] + \
             [f"{prefix_b}/{ln}" for ln in b_lines]

    if shuffle:
        random.seed(42)
        random.shuffle(merged)

    os.makedirs(os.path.dirname(out_list), exist_ok=True)
    with open(out_list, 'w', encoding='utf-8') as fo:
        fo.write("\n".join(merged) + "\n")

    print(f"✅ Merged {len(a_lines)} + {len(b_lines)} → {out_list}")

if __name__ == "__main__":
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "hand")
    )
    merge_ab(
        os.path.join(base, "train_A.txt"),
        os.path.join(base, "train_user.txt"),
        os.path.join(base, "train_AB.txt")
    )
    merge_ab(
        os.path.join(base, "train_A.txt"),
        os.path.join(base, "test_user.txt"),
        os.path.join(base, "test_AB.txt")
    )
