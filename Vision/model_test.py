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
img_path = r"F:/Stomach_X-ray/Pediatric_Abdominal_X-ray/Validation/Source_Data/3.Air_Fluid_Level/3_1625.png"
json_path = r"F:/Stomach_X-ray/Pediatric_Abdominal_X-ray/Validation/Labeling_Data/3.Air_Fluid_Level/3_1625.json"

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

fig, axes = plt.subplots(1, 2, figsize=(12, 8))
axes = axes.flatten()

print(pred.shape, mask_tensor.shape)
axes[0].imshow(pred.squeeze())
axes[0].set_title("Prediction")
axes[1].imshow(mask)
axes[1].set_title("Mask")
plt.show()
