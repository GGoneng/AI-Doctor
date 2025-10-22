from Modules.VisionModules import vision_predict
from Modules.LLMModules import *

import torch
import os

from PIL import Image

from io import BytesIO

import numpy as np

from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from uuid import uuid4

import base64
import redis
import pickle
import threading
import time

from typing import Optional

from langchain.chains import LLMChain


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

vision_memory = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
llm_memory = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=1)

gpu_lock = threading.Lock()

def predict_vision(id: str):
    with gpu_lock:
        data = pickle.loads(vision_memory.get(id))
        img = data["inputs"][-1]
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

        data["outputs"].append(base64_img)

        vision_memory.set(id, pickle.dumps(data))

        result_path = os.path.join(BASE_PATH, "result.png")
        Image.fromarray(pred_img).save(result_path)

        return {"id": id, "vision_result": "redis 저장 성공"}

def predict_llm(id: str):
    with gpu_lock:
        data = pickle.loads(llm_memory.get(id))
        
    return None


@app.post("/upload")
async def upload_image(id: Optional[str] = Form(None),
                       file: Optional[UploadFile] = File(None), 
                       text: Optional[str] = Form(None),
                       background_tasks: BackgroundTasks = None):
    
    if id is None:
        id = str(uuid4())

    vision_data = vision_memory.get(id)
    llm_data = llm_memory.get(id)
    
    if vision_data:
        vision_data = pickle.loads(vision_data)
    else:
        vision_data = {}

    if llm_data:
        llm_data = pickle.loads(llm_data)
    else:
        llm_data = {}


    if "inputs" not in vision_data:
        vision_data["inputs"] = []
    
    if "outputs" not in vision_data:
        vision_data["outputs"] = []

    if "inputs" not in llm_data:
        llm_data["inputs"] = []

    if "outputs" not in llm_data:
        llm_data["outputs"] = []
    

    img = await file.read()

    if (len(img) == 0):
        llm_data["inputs"].append(text)
        background_tasks.add_task(predict_llm, id)
    
    elif not text:
        vision_data["inputs"].append(img)
        background_tasks.add_task(predict_vision, id)
    
    else:
        vision_data["inputs"].append(img)
        llm_data["inputs"].append(text)

        # Vision 모델의 추론 우선 (속도, 증상 체크)
        background_tasks.add_task(predict_vision, id)
        # prediction_queue.append(("llm", id))

    vision_memory.set(id, pickle.dumps(vision_data))
    llm_memory.set(id, pickle.dumps(llm_data))

    return {"id": id, "file": file.filename, "prompt": text, "message": "업로드 성공!"}

@app.get("/visionOutputs/{id}")
def get_vision_output(id: str):
    time.sleep(3)
    data = pickle.loads(vision_memory.get(id))

    if not data:
        return {"outputs": []}

    outputs = data.get("outputs", [])

    latest_output = outputs[-1] if outputs else None
    
    return {"outputs": [latest_output] if latest_output else []}