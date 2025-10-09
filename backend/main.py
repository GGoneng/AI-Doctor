from Modules.VisionModules import vision_predict

import torch
import os

from PIL import Image

from io import BytesIO

import numpy as np

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
VISION_WEIGHTS_PATH = os.path.join(BASE_PATH, "Weights", "vision_weights.pth")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_image(file: Optional[UploadFile] = File(None), 
                       prompt: Optional[str] = Form(None)):
    
    if (file):
        img = await file.read()
        img = Image.open(BytesIO(img)).convert("RGB")

        num_classes = 5

        pred = vision_predict(img=img, num_classes=num_classes, weights=VISION_WEIGHTS_PATH, device=DEVICE)
        pred_np = pred.cpu().numpy()

        palette = np.array([
            [0, 0, 0],        # class 0 → black
            [255, 0, 0],      # class 1 → red
            [0, 255, 0],      # class 2 → green
            [0, 0, 255],      # class 3 → blue
            [255, 255, 0],    # class 4 → yellow
        ], dtype=np.uint8)

        # (3) RGB 이미지로 변환
        color_mask = palette[pred_np]  # (H, W, 3) 형태로 변환

        # (4) 이미지 저장
        Image.fromarray(color_mask).save("result.png")

        # Image.fromarray(pred_np, mode="L").save("result.png")

        print(f"파일 이름 : {file.filename}")
        return {"filename": file.filename, "message": "이미지 업로드 성공!"}
    
    else:
        return {"filename": None, "prompt": None, "message": ""}