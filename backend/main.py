# backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import easyocr
import os
import time

app = FastAPI()

# CORS 설정: React 앱(3000)에서 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# EasyOCR 리더 (한글+영어)
reader = easyocr.Reader(['ko', 'en'], gpu=False)

# ---------------- OCR Endpoint ----------------
class OCRResult(BaseModel):
    text: str
    bbox: list[list[float]]
    confidence: float

@app.post("/api/ocr/", response_model=list[OCRResult])
async def ocr_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
    data = await file.read()
    img = Image.open(BytesIO(data)).convert("RGB")
    img_array = np.array(img)
    raw = reader.readtext(img_array)  # [(bbox, text, conf), ...]
    results = []
    for bbox, text, conf in raw:
        results.append(OCRResult(text=text, bbox=bbox, confidence=conf))
    return results

# ---------------- Static Files & Directories ----------------
# 결과 저장 폴더 생성
os.makedirs("results", exist_ok=True)
# /results 경로로 정적 서빙
app.mount("/results", StaticFiles(directory="results"), name="results")

# ---------------- Convert Endpoint ----------------
class ConvertRequest(BaseModel):
    text: str

class ConvertResponse(BaseModel):
    imageURL: str

@app.post("/api/notes/convert", response_model=ConvertResponse)
async def convert_endpoint(req: ConvertRequest):
    text = req.text
    # 출력 파일명 생성
    out_name = f"hw_{int(time.time())}.png"
    out_path = os.path.join("results", out_name)

    # Pillow를 사용한 더미 손글씨 렌더링
    img = Image.new("RGB", (800, 200), "white")
    draw = ImageDraw.Draw(img)
    # 프로젝트 루트에 있는 ttf 폰트 파일 경로를 지정하세요.
    font = ImageFont.truetype("arial.ttf", 48)
    draw.text((10, 10), text, fill="black", font=font)
    img.save(out_path)

    return ConvertResponse(imageURL=f"/results/{out_name}")

# ---------------- Run Server ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
