from Modules.VisionModules import vision_predict

import torch
import os

from PIL import Image

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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
async def upload_image(file: UploadFile = File(...)):
    img = await file.read()
    num_classes = 5

    pred = vision_predict(img=img, num_classes=num_classes, weights=VISION_WEIGHTS_PATH, device=DEVICE)
    pred_np = pred.cpu().numpy()

    Image.fromarray(pred_np.astype(np.uint8)).save("result.png")

    print(f"파일 이름 : {file.filename}")
    return {"filename": file.filename, "message": "이미지 업로드 성공!"}