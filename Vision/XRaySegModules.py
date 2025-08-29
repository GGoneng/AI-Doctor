import torch
import torch.nn as nn

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
            draw.polygon(points, fill=1)
        
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
    def __init__(self, in_ch, out_ch):
        super().__init__()
        
        self.encoder1 = Conv(in_ch, 64)
        self.encoder2 = Conv(64, 128)
        self.encoder3 = Conv(128, 256)
        self.encoder4 = Conv(256, 512)

        self.maxpool = nn.MaxPool2d(2)

        self.bottleneck = Conv(512, 1024)

        self.decoder1 = Expand(1024, 512)
        self.decoder2 = Expand(512, 256)
        self.decoder3 = Expand(256, 128)
        self.decoder4 = Expand(128, 64)

        self.output = nn.Conv2d(64, out_ch, 1)

        self.dropout = nn.Dropout2D(0.2)

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
    