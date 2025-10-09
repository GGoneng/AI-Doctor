import torch
import torch.nn as nn
import torch.nn.functional as F

from PIL import Image

import albumentations as A

import numpy as np

import cv2 as cv

class _Conv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU()
        )
    
    def forward(self, input):
        return self.conv(input)
    
class _Expand(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.up = nn.Sequential(
            nn.ConvTranspose2d(in_ch, out_ch, 2, stride=2),
            nn.BatchNorm2d(out_ch),
            nn.ReLU()
        )
        self.conv = _Conv(in_ch, out_ch)

    def forward(self, input, skip):
        x = self.up(input)
        x = torch.cat((x, skip), dim=1)
        x = self.conv(x)

        return x

class _OriginUNet(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        
        self.encoder1 = _Conv(1, 64)
        self.encoder2 = _Conv(64, 128)
        self.encoder3 = _Conv(128, 256)
        self.encoder4 = _Conv(256, 512)

        self.maxpool = nn.MaxPool2d(2)

        self.bottleneck = _Conv(512, 1024)

        self.decoder1 = _Expand(1024, 512)
        self.decoder2 = _Expand(512, 256)
        self.decoder3 = _Expand(256, 128)
        self.decoder4 = _Expand(128, 64)

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


def _image_preprocess(img, device="cpu"):
    img = cv.cvtColor(np.array(img), cv.COLOR_RGB2GRAY)
    
    transform = A.Compose([A.Resize(512, 512),
                           A.pytorch.ToTensorV2()])
    
    img = np.array(img, dtype=np.float32) / 255.0

    augmented = transform(image=img)
    img_tensor = augmented["image"].unsqueeze(0).to(device)

    return img_tensor

def vision_predict(img, num_classes, weights, device="cpu"):
    img_tensor = _image_preprocess(img, device)

    model = _OriginUNet(num_classes=num_classes).to(device)
    model.load_state_dict(torch.load(weights, map_location=torch.device(device), weights_only=True))

    model.eval()

    pred = model(img_tensor)
    pred = torch.argmax(F.softmax(pred, dim=1), dim=1).squeeze()

    return pred
