# -----------------------------------------------------------------------------------
# 파일명       : Origin_UNet.py
# 설명         : Image Segmentation (U-Net)을 통한 소아 복부 질환 탐지       
# 작성자       : 이민하
# 작성일       : 2025-08-26
# 
# 사용 모듈    :
#
#
# -----------------------------------------------------------------------------------
# >> 주요 기능
# - 정상 1, 비정상 4가지의 상황을 Image Segmentation을 통해 구별
# - Computer Vision 분야의 U-Net 구조를 직접 구현 
#
# >> 업데이트 내역
# [2025-08-26] 데이터 확인 및 불러오기
# [2025-08-27] 데이터셋 구현
# [2025-08-28] Original U-Net 구현
# [2025-08-29] Dice Loss + Cross Entropy Loss 구현 및 학습 파이프라인 구축
# [2025-09-02] Loss 구조 변경
#
# >> 성능
#
# -----------------------------------------------------------------------------------


import os
import json

import torch
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler

from torch.utils.data import DataLoader

from torchvision.datasets import ImageFolder
from torchvision.transforms import v2
import albumentations as A

from torchmetrics.segmentation import DiceScore

import gdown
from functools import reduce

from XRaySegModules import *

# 데이터 경로 설정
TRAIN_DATA_DIR = "../Pediatric_Abdominal_X-ray/Training/Source_Data"
TRAIN_LABEL_DIR = "../Pediatric_Abdominal_X-ray/Training/Labeling_Data"

VAL_DATA_DIR = "../Pediatric_Abdominal_X-ray/Validation/Source_Data"
VAL_LABEL_DIR = "../Pediatric_Abdominal_X-ray/Validation/Labeling_Data"


# Training 데이터 준비
folder_list = []
label_file_list = []
label_list = []

for folder in os.listdir(TRAIN_LABEL_DIR)[:5]:
    folder_list.append(os.path.join(TRAIN_LABEL_DIR, folder))

for dir in folder_list:
    for file_name in os.listdir(dir)[:300]:
        label_file_list.append(os.path.join(dir, file_name))

for file in label_file_list:
    with open(file, "r", encoding="utf-8") as f:
        label_list.append(json.load(f))

# Validation 데이터 준비
val_folder_list = []
val_label_file_list = []
val_label_list = []

for folder in os.listdir(VAL_LABEL_DIR)[:5]:
    val_folder_list.append(os.path.join(VAL_LABEL_DIR, folder))

for dir in val_folder_list:
    for file_name in os.listdir(dir)[:100]:
        val_label_file_list.append(os.path.join(dir, file_name))

for file in val_label_file_list:
    with open(file, "r", encoding="utf-8") as f:
        val_label_list.append(json.load(f))

replace_dict = {"Labeling_Data": "Source_Data", ".json": ".png"}

train_file_list = [reduce(lambda x, y: x.replace(*y), replace_dict.items(), file) for file in label_file_list]
val_file_list = [reduce(lambda x, y: x.replace(*y), replace_dict.items(), file) for file in val_label_file_list]


transform = A.Compose([ 
    A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0, rotate_limit=5, p=0.5), 
    A.RandomBrightnessContrast(brightness_limit=0.2, p=0.5), 
    A.ElasticTransform(alpha=1, sigma=50, p=0.5),
    A.pytorch.ToTensorV2()
    ])


BATCH_SIZE = 8

trainDS = XRayDataset(train_file_list, label_list, transform)
trainDL = DataLoader(trainDS, batch_size=BATCH_SIZE)

valDS = XRayDataset(val_file_list, val_label_list, transform)
valDL = DataLoader(valDS, batch_size=BATCH_SIZE)


EPOCH = 300 
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LR = 3e-3

num_classes = 5

model = OriginUNet(num_classes=num_classes).to(DEVICE)

loss_fn = CustomWeightedLoss(device=DEVICE)

optimizer = optim.AdamW(model.parameters(), lr=LR)

scheduler = lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=10)


loss, score = training(model=model, trainDL=trainDL, valDL=valDL, optimizer=optimizer, 
                       epoch=EPOCH, data_size=len(trainDS), val_data_size=len(valDS), 
                       loss_fn=loss_fn, scheduler=scheduler, device=DEVICE)