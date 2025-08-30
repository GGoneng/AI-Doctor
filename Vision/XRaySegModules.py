import torch
import torch.nn as nn
import torch.nn.functional as F

from torchmetrics.segmentation import DiceScore
from torch.utils.data import Dataset, DataLoader

from PIL import Image, ImageDraw

import numpy as np



class XRayDataset(Dataset):
    def __init__(self, img_path, json_list, transform=None):
        self.img_path = img_path
        self.label = json_list
        self.transform = transform

    def __len__(self):
        return len(self.img_path)
    
    def __getitem__(self, idx):
        img_path = self.img_path[idx]
        item = self.label[idx]

        img = Image.open(img_path).convert('L')
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)

        for shape in item["shapes"]:
            points = [tuple(point) for point in shape["points"]]
            class_id = shape["class"]
            draw.polygon(points, fill=class_id)
        
        img = np.array(img)
        mask = np.array(mask)

        if self.transform:
            augment = self.transform(image=img, mask=mask)
            img = augment["image"]
            mask = augment["mask"]

        return img, mask



class Conv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.ReLU()
        )
    
    def forward(self, input):
        return self.conv(input)
    
class Expand(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.up = nn.Sequential(
            nn.ConvTranspose2d(in_ch, out_ch, 2, stride=2),
        )
        self.conv = Conv(in_ch, out_ch)

    def forward(self, input, skip):
        x = self.up(input)
        x = torch.cat((x, skip), dim=1)
        x = self.conv(x)

        return x

class OriginUNet(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        
        self.encoder1 = Conv(1, 64)
        self.encoder2 = Conv(64, 128)
        self.encoder3 = Conv(128, 256)
        self.encoder4 = Conv(256, 512)

        self.maxpool = nn.MaxPool2d(2)

        self.bottleneck = Conv(512, 1024)

        self.decoder1 = Expand(1024, 512)
        self.decoder2 = Expand(512, 256)
        self.decoder3 = Expand(256, 128)
        self.decoder4 = Expand(128, 64)

        self.output = nn.Conv2d(64, num_classes, 1)

        self.dropout = nn.Dropout2d(0.2)

    def forward(self, input):
        in1 = self.encoder1(input)
        in2 = self.encoder2(self.maxpool(in1))
        in3 = self.encoder3(self.maxpool(in2))
        in4 = self.encoder4(self.maxpool(in3))

        bn = self.bottleneck(self.dropout(self.maxpool(in4)))

        out1 = self.decoder1(bn, in4)
        out2 = self.decoder2(out1, in3)
        out3 = self.decoder3(out2, in2)
        out4 = self.decoder4(out3, in1)

        final_output = self.output(out4)

        return final_output


class CustomWeightedLoss(nn.Module):
    def __init__(self, num_cls):
        super().__init__()
        self.class_weights = torch.tensor([0.1, 1.0, 1.0, 1.0, 1.0], dtype=torch.float32)
        self.CELoss = nn.CrossEntropyLoss(weight=self.class_weights)
        self.DiceCoef = DiceScore(num_classes=num_cls, include_background=False, average="macro", input_format="index")

    def forward(self, pred, target):
        ce_loss = self.CELoss(pred, target)
        dice_loss = 1 - self.DiceCoef(pred, target)

        return ce_loss + dice_loss
    

def training(model, trainDL, optimizer, epoch, scheduler, device):
    # 가중치 파일 저장 위치 정의
    SAVE_PATH = './saved_models'
    os.makedirs(SAVE_PATH, exist_ok=True)

    # Early Stopping을 위한 변수
    BREAK_CNT_LOSS = 0
    BREAK_CNT_SCORE = 0
    LIMIT_VALUE = 10

    # Loss가 더 낮은 가중치 파일을 저장하기 위하여 Loss 로그를 담을 리스트
    LOSS_HISTORY = []

    for epoch in range(1, EPOCH + 1):
        # GPU 환경에서 training과 testing을 반복하므로 eval 모드 -> train 모드로 전환
        # testing에서는 train 모드 -> eval 모드
        model.train()

        SAVE_WEIGHT = os.path.join(SAVE_PATH, f"best_model_weights.pth")

        loss_total = 0

        # Train DataLoader에 저장된 Feature, Target 텐서로 학습 진행
        for featureTS, targetTS in trainDL:
            # GPU 환경으로 데이터 이동
            featureTS = featureTS.to(device)
            targetTS = targetTS.to(device)

            # 결과 추론
            pre_val = model(featureTS)

            # 추론값으로 Loss값 계산
            loss = CustomWeightedLoss(pre_val, targetTS)

            # 활성화 함수 +