from PIL import Image, ImageDraw, ImageFont
import os, string

def make_skeletons(
    out_dir="data/hand/A",
    image_size=(256, 256),
    font_path="fonts/NanumGothic-Regular.ttf",
    font_size=200,
):
    # 1) 출력 폴더 생성
    os.makedirs(out_dir, exist_ok=True)

    # 2) 생성할 문자 목록 준비
    chars = list(string.ascii_letters + string.digits + "!?.,")
    chars += [chr(cp) for cp in range(ord("가"), ord("힣") + 1)]

    # 3) 폰트 로드 시도
    base_dir = os.path.dirname(__file__)
    font_file = os.path.join(base_dir, '..', font_path)
    try:
        font = ImageFont.truetype(font_file, font_size)
    except OSError as e:
        print(f"⚠️  Failed to load font '{font_file}': {e}\n   Using default font instead.")
        font = ImageFont.load_default()

    # 4) 각 문자마다 이미지 생성
    for ch in chars:
        img = Image.new("RGB", image_size, "white")
        draw = ImageDraw.Draw(img)

        # 텍스트 치수 측정
        try:
            w, h = font.getsize(ch)
        except AttributeError:
            bbox = draw.textbbox((0, 0), ch, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # 중앙 배치하여 렌더링
        draw.text(
            ((image_size[0] - w) / 2, (image_size[1] - h) / 2),
            ch,
            fill="black",
            font=font
        )

        # 파일명은 유니코드 코드포인트 사용
        filename = f"{ord(ch):X}.png"
        img.save(os.path.join(out_dir, filename))


if __name__ == "__main__":
    make_skeletons(
        out_dir="data/hand/A",
        image_size=(256, 256),
        font_path="fonts/NanumGothic-Regular.ttf",
        font_size=200
    )
    print("✅ A 도메인(폰트 스켈레톤) 이미지 생성 완료")