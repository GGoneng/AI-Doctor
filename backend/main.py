from Modules.VisionModules import predict_vision
# from Modules.LLMModules import *
from Modules.TypeVariable import *

import torch
import os

from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from uuid import uuid4

import redis
import pickle
import time

from typing import Optional, Dict, List, Any

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


@app.post("/upload")
async def upload_image(id: Optional[str] = Form(None),
                       file: Optional[UploadFile] = File(None), 
                       text: Optional[str] = Form(None),
                       background_tasks: BackgroundTasks = None) -> Dict[str, Any]:
    
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
        # background_tasks.add_task(predict_llm, id)
    
    elif not text:
        vision_data["inputs"].append(img)
        background_tasks.add_task(predict_vision, id, vision_memory)
    
    else:
        vision_data["inputs"].append(img)
        llm_data["inputs"].append(text)

        # Vision 모델의 추론 우선 (속도, 증상 체크)
        background_tasks.add_task(predict_vision, id, vision_memory)
        # prediction_queue.append(("llm", id))

    vision_memory.set(id, pickle.dumps(vision_data))
    llm_memory.set(id, pickle.dumps(llm_data))

    return {"id": id, "file": file.filename, "prompt": text, "message": "업로드 성공!"}

@app.get("/visionOutputs/{id}")
def get_vision_output(id: str) -> VisionOutputType:
    time.sleep(3)
    data = pickle.loads(vision_memory.get(id))

    if not data:
        return {"outputs": []}

    outputs = data.get("outputs", [])

    latest_output = outputs[-1] if outputs else None
    
    return {"outputs": [latest_output]}