# backend/scripts/merge_AB.py
import os

def make_AB_list(a_txt, b_txt, out_txt):
    lines = []
    # A 쪽 (label 0)
    with open(a_txt, 'r', encoding='utf-8') as f:
        for l in f:
            path = l.strip()
            if path: lines.append(f"{path} 0")
    # B/user 쪽 (label 1)
    with open(b_txt, 'r', encoding='utf-8') as f:
        for l in f:
            path = l.strip()
            if path: lines.append(f"{path} 1")
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"✅ 합쳐진 리스트 생성: {out_txt}")

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "data", "hand"
    ))
    make_AB_list(
        os.path.join(base, "train_A.txt"),
        os.path.join(base, "train_user.txt"),
        os.path.join(base, "train_AB.txt")
    )
    make_AB_list(
        os.path.join(base, "train_A.txt"),
        os.path.join(base, "test_user.txt"),
        os.path.join(base, "test_AB.txt")
    )
