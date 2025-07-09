# backend/scripts/merge_AB.py

import os

def make_AB_list(a_txt, b_txt, out_txt):
    lines = []
    # A: label 0
    with open(a_txt, 'r', encoding='utf-8') as fa:
        for l in fa:
            img = l.strip()
            if img:
                lines.append(f"A/{os.path.basename(img)} 0")
    # B: label 1
    with open(b_txt, 'r', encoding='utf-8') as fb:
        for l in fb:
            img = l.strip()
            if img:
                lines.append(f"B/user/{os.path.basename(img)} 1")
    # shuffle if you like
    import random; random.shuffle(lines)
    with open(out_txt, 'w', encoding='utf-8') as fo:
        fo.write("\n".join(lines))

if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..", "data", "hand")
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
    print("✅ train_AB.txt / test_AB.txt 생성 완료")
