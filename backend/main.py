from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import easyocr

app = FastAPI()

# CORS 설정: 프런트 주소 허용 (기본 : localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# EasyOCR 리더 (한글+영어)
reader = easyocr.Reader(['ko','en'], gpu=False)

class OCRResult(BaseModel):
    text: str
    bbox: list[list[float]]
    confidence: float

@app.post("/api/ocr/", response_model=list[OCRResult])
async def ocr_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "이미지 파일만 업로드 가능합니다.")
    data = await file.read()
    img = Image.open(BytesIO(data)).convert("RGB")
    raw_results = reader.readtext(data)  # [(bbox, text, conf), ...]
    output = []
    for bbox, text, conf in raw_results:
        output.append(OCRResult(
            text=text,
            bbox=bbox,       # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            confidence=conf
        ))
    return output

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
