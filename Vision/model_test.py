from XRaySegModules import *

import torch
import torch.nn.functional as F

from PIL import Image

import albumentations as A

import json
import matplotlib.pyplot as plt

WEIGHT_PATH = "./saved_models/best_model_weights.pth"

num_classes = 5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


model = OriginUNet(num_classes=num_classes).to(DEVICE)
model.load_state_dict(torch.load(WEIGHT_PATH, map_location=torch.device(DEVICE), weights_only=True))

model.eval()

transform = A.Compose([A.pytorch.ToTensorV2()])


# 데이터 불러오기
img_path = r"F:/Stomach_X-ray/Pediatric_Abdominal_X-ray/Validation/Source_Data/1.Pyloric_Stenosis/1_1816.png"
json_path = r"F:/Stomach_X-ray/Pediatric_Abdominal_X-ray/Validation/Labeling_Data/1.Pyloric_Stenosis/1_1816.json"

img = Image.open(img_path).convert('L')

with open(json_path, "r", encoding="utf-8") as f:
    item = json.load(f)

mask = Image.new('L', img.size, 0)
draw = ImageDraw.Draw(mask)

for shape in item["shapes"]:
    points = [tuple(point) for point in shape["points"]]
    class_id = shape["class"]
    draw.polygon(points, fill=class_id)


img = np.array(img, dtype=np.float32) / 255.0
mask = np.array(mask, dtype=np.int64)


augmented = transform(image=img, mask=mask)
img_tensor = augmented["image"].unsqueeze(0).to(DEVICE)
mask_tensor = augmented["mask"]

pred = model(img_tensor)
pred = torch.argmax(F.softmax(pred, dim=1), dim=1).cpu()

print(pred.unique())

fig, ax = plt.subplots(figsize=(6, 6))  # Figure + Axes 생성

ax.imshow(img, cmap="gray")  # 배경 이미지
ax.imshow(pred.squeeze(), cmap="jet", alpha=0.4)  # 예측값 오버레이
ax.set_title("Prediction Overlay")

plt.show()