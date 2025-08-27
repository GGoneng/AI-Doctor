import torch

from torch.utils.data import Dataset, DataLoader

from PIL import Image, ImageDraw

import json
import os

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

        if self.transform:
            img = self.transform(img)
            mask = self.transform(mask)

        return img, mask