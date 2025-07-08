# backend/scripts/split_handwriting_data.py

import os, random

def split_domain(domain_dir, out_dir, list_name, train_ratio=0.8):
    """
    domain_dir 안의 이미지 파일을
    train_ratio 비율로 train_<list_name>.txt / test_<list_name>.txt 로 나눕니다.
    리스트에는 '파일명.png'만 기록합니다.
    """
    fnames = sorted([
        fn for fn in os.listdir(domain_dir)
        if fn.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    if not fnames:
        print(f"⚠️  {domain_dir}에 이미지가 하나도 없습니다.")
        return

    random.seed(42)
    random.shuffle(fnames)
    n = int(len(fnames) * train_ratio)
    train, test = fnames[:n], fnames[n:]

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"train_{list_name}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(train))
    with open(os.path.join(out_dir, f"test_{list_name}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(test))

    print(f"✅ {list_name} split: {len(train)} train, {len(test)} test")


if __name__ == "__main__":
    base = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "data", "hand"
    ))

    # A 도메인 (content)
    split_domain(
      domain_dir=os.path.join(base, "A"),
      out_dir=base,
      list_name="A",
      train_ratio=1.0
    )

    # user 도메인 (style)
    split_domain(
      domain_dir=os.path.join(base, "B", "user"),
      out_dir=base,
      list_name="user",
      train_ratio=0.8
    )
