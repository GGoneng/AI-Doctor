from Modules.VisionModules import vision_predict

import torch
import os

from PIL import Image

from io import BytesIO

import numpy as np

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

from uuid import uuid4

import base64
import redis
import pickle

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

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)

@app.post("/upload")
async def upload_image(file: Optional[UploadFile] = File(None), 
                       text: Optional[str] = Form(None)):
    
    id = str(uuid4())

    img = await file.read()

    if (len(img) == 0):
        r.set(id, pickle.dumps({"text": text}))
    
    elif (text == None):
        r.set(id, pickle.dumps({"img": img}))
    
    else:
        r.set(id, pickle.dumps({"text": text, "img": img}))

    return {"id": id, "file": file.filename, "prompt": text, "message": "업로드 성공!"}


@app.post("/predictVision")
def predict_vision(id: str):
    data = pickle.loads(r.get(id))
    img = data["img"]
    img = Image.open(BytesIO(img)).convert("RGB")

    img_np = np.array(img, dtype=np.float32)
    num_classes = 5

    pred = vision_predict(img=img, num_classes=num_classes, weights=VISION_WEIGHTS_PATH, device=DEVICE)
    pred_np = pred.cpu().numpy()

    symptom_list = ["증상 없음", "유문협착증", "기복증", "공기액체층", "변비"]
    symptom_class = max(np.unique(pred_np))

    symptom = symptom_list[symptom_class]

    print(symptom)

    palette = np.array([
        [0, 0, 0],        # class 0 → black
        [255, 0, 0],      # class 1 → red
        [0, 255, 0],      # class 2 → green
        [0, 0, 255],      # class 3 → blue
        [255, 255, 0],    # class 4 → yellow
    ], dtype=np.uint8)

    color_mask = palette[pred_np] 
    color_mask = color_mask.astype(np.float32)

    blend_ratio = 0.3  # 투명도 (0.0~1.0)
    pred_img = (img_np * (1 - blend_ratio) + color_mask * blend_ratio).astype(np.uint8)

    buffer = BytesIO()
    Image.fromarray(pred_img).save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

    data["vision_pred"] = base64_img
    r.set(id, pickle.dumps(data))

    Image.fromarray(pred_img).save("result.png")

    return {"id": id, "vision_result": "redis 저장 성공"}