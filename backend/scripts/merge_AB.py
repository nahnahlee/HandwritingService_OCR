# backend/scripts/merge_AB.py
import random

def make_AB_list(a_txt, b_txt, out_txt):
    # 1) 기존 train_A.txt/train_B.txt 에서 경로 읽어오기
    with open(a_txt, 'r', encoding='utf-8') as f:
        a_paths = [l.strip() for l in f if l.strip()]
    with open(b_txt, 'r', encoding='utf-8') as f:
        b_paths = [l.strip() for l in f if l.strip()]

    # 2) 레이블 붙이기 (A:0, B:1)
    lines = [f"{p} 0" for p in a_paths] + [f"{p} 1" for p in b_paths]
    random.shuffle(lines)

    # 3) 파일 쓰기
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"✅ 만든 파일: {out_txt}  (총 {len(lines)}개)")

if __name__ == "__main__":
    base = "backend/data/hand"
    make_AB_list(f"{base}/train_A.txt", f"{base}/train_B.txt", f"{base}/train_AB.txt")
    make_AB_list(f"{base}/test_A.txt",  f"{base}/test_B.txt",  f"{base}/test_AB.txt")
