from XRaySegModules import *

import torch
import torch.nn.functional as F

from PIL import Image

import albumentations as A

import matplotlib.pyplot as plt

WEIGHT_PATH = "./saved_models/best_model_weights.pth"

num_classes = 5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


model = OriginUNet(num_classes=num_classes).to(DEVICE)
model.load_state_dict(torch.load(WEIGHT_PATH, map_location=torch.device(DEVICE), weights_only=True))

model.eval()

transform = A.Compose([A.pytorch.ToTensorV2()])

img_path = r"F:/Stomach_X-ray/Pediatric_Abdominal_X-ray/Validation/Source_Data/1.Pyloric_Stenosis/1_2000.png"
img = Image.open(img_path).convert('L')
img = np.array(img, dtype=np.float32) / 255.0

augmented = transform(image = img)
img_tensor = augmented["image"].unsqueeze(0).to(DEVICE)

pred = model(img_tensor)
pred = torch.argmax(F.softmax(pred, dim=1), dim=1)

print(pred.unique())