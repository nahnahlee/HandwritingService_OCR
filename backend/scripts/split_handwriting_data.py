import os
import random

def split_domain(domain_dir: str,
                 out_dir: str,
                 prefix: str,
                 train_ratio: float = 0.8):
    """
    domain_dir 안의 이미지(.png/.jpg/.jpeg) 파일 이름만
    train_<prefix>.txt / test_<prefix>.txt 로 분할 기록합니다.
    한 줄에 '파일명'만 쓰고, 슬래시도 '/'로 통일합니다.
    """
    # 1) 파일명 수집
    fnames = sorted([
        fn for fn in os.listdir(domain_dir)
        if fn.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    if not fnames:
        print(f"⚠️  {domain_dir}에 이미지가 하나도 없습니다.")
        return

    # 2) 상대경로(prefix/파일명) 생성
    rel_paths = [ f"{prefix}/{fn}" for fn in fnames ]

    # 3) shuffle & split
    random.seed(42)
    random.shuffle(rel_paths)
    n_train = int(len(rel_paths) * train_ratio)
    train_list = rel_paths[:n_train]
    test_list  = rel_paths[n_train:]

    # 4) 쓰기
    os.makedirs(out_dir, exist_ok=True)
    train_txt = os.path.join(out_dir, f"train_{prefix}.txt")
    test_txt  = os.path.join(out_dir, f"test_{prefix}.txt")

    with open(train_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(train_list))

    with open(test_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(test_list))

    print(f"✅ {prefix} 분할 완료: {len(train_list)} train / {len(test_list)} test")
    print(f"   → {train_txt}")
    print(f"   → {test_txt}\n")


if __name__ == "__main__":
    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "hand")
    )

    # A 도메인: 100% train
    split_domain(
        domain_dir=os.path.join(base, "A"),
        out_dir=base,
        prefix="A",
        train_ratio=1.0,
    )

    # B/user 도메인: 80% train, 20% test
    split_domain(
        domain_dir=os.path.join(base, "B", "user"),
        out_dir=base,
        prefix="user",
        train_ratio=0.8,
    )
