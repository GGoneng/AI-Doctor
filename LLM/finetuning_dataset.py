import json
import torch
import random

from transformers import AutoTokenizer, AutoModelForCausalLM

# 모델과 토크나이저 로드
model_name = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto"
)

# 지식 기반 instruction (system 역할)
system_instruction = """
당신은 임상 지식을 갖춘 유능하고 신뢰할 수 있는 한국어 기반 의료 어시스턴트입니다.
사용자의 질문에 대해 정확하고 신중한 임상 추론을 바탕으로 진단 가능성을 제시해 주세요.
환자의 연령, 증상, 검사 결과, 통증 부위 등 모든 단서를 종합적으로 고려하여 추론 과정과 진단명을 제시해야 합니다.
의학적으로 정확한 용어를 사용하되, 필요하면 일반인이 이해하기 쉬운 용어도 병행해 설명하세요.

**아래 지식 정보만 사용하세요.**

[지식 정보]
### 1. **유문협착증 (Pyloric Stenosis)**
- **연령 및 임상 특징**: 주로 생후 3~6주 사이의 남아에게 발생하며, 특징적인 증상은 먹은 후 몇 분 내에 발생하는 **심한 구토**(특히 우유를 먹은 후 양방향으로 튀는 형태인 *사격성 구토*)입니다. 복부 팽만감이나 울음소리와 함께 구토가 나타나며, 탈수 증상(구강 건조, 피부 탄력 저하 등)이 동반될 수 있습니다.
- **복부 X-ray 소견**:
  - 위장이 크게 팽창되어 있고, 위와 십이지장의 접합부에 공기와 액체가 동시에 존재하는 모습인 "**더블 버블 징후**(Double Bubble Sign)"가 나타납니다.
  - 위장의 하부에 두꺼워진 유문부가 보여지는 "**타깃 징후**(Target Sign)" 또는 "**올리브 모양의 종괴**(Olive Mass)"가 관찰될 수도 있습니다.
  - 장내 가스 패턴은 대부분 정상이며, 장폐색의 다른 징후는 거의 없습니다.
- **진단 방법**: 임상 증상과 초음파 검사(유문부 두께 측정)로 확진하며, 복부 X-ray는 보조적인 역할을 합니다.
- **치료법**: 수술적 치료인 "**유문근막절개술**(Pyloromyotomy)"이 표준 치료입니다. 복부를 통해 유문부 근육을 절개하여 협착부를 넓히면 증상이 완화됩니다. 최근에는 내시경적 치료도 일부 시도되지만, 대부분 수술이 필요합니다.

---

### 2. **기복증 (장폐색, Intestinal Obstruction)**
- **연령 및 임상 특징**: 신생아부터 소아까지 다양한 연령층에서 발생할 수 있으며, 원인에 따라 증상이 달라집니다.
  - **선천성 장폐색**(예: 장중간막동맥증후군, 장중막동맥증후군, 장중막동맥증후군 등)은 신생아기에 나타나며, 복부 팽만감, 구토, 배변 중단 등의 증상을 보입니다.
  - **후천성 장폐색**(예: 장중막동맥증후군, 장중막동맥증후군 등)은 감염, 외상, 종양 등으로 인해 발생하며, 복통, 구토, 복부 팽만 등이 나타납니다.
- **복부 X-ray 소견**:
  - 장관이 확장되어 있고, 공기와 액체가 혼합된 모습인 "**공기-액체 수준**(Air-Fluid Level)"이 여러 개 관찰됩니다.
  - 장내 가스 패턴이 불규칙하며, 특히 맹장이나 횡행결장 부위에 가스가 많이 축적될 수 있습니다.
  - 심한 폐색 시 복강 내 공기가 자유롭게 퍼져 있는 "**복막하 공기**(Pneumoperitoneum)"가 나타날 수도 있습니다.
- **진단 방법**: 복부 초음파 또는 컴퓨터단층촬영(CT)으로 폐색 위치와 원인을 확인합니다. 복부 X-ray는 긴급 상황에서 초기 평가에 유용합니다.
- **치료법**:
  - 원인이 선천성인 경우 수술적 치료가 필요하며, 후천성 폐색은 원인 치료(감염 치료 등)와 함께 보존적 치료(금식, 정맥 영양 공급 등)를 시행합니다.
  - 일부 경우에는 장중막동맥증후군 등 특정 질환에서는 내시경적 감압이나 수술적 절제가 필요할 수 있습니다.

---

### 3. **공기-액체 수준 (Air-Fluid Level)**
- **특징**: 복부 X-ray에서 장관 내부에 공기와 액체가 동시에 존재하는 모습을 말하며, 질병 자체가 아니라 "**방사선학적 징후**(Radiological Sign)"입니다.
- **관련 질환**:
  - 위장관 폐색(유문협착증, 장중막동맥증후군 등)
  - 변비 또는 장중막동맥증후군 등으로 인한 장내 압력 상승
  - 장중막동맥증후군 등으로 인한 장내 압력 상승
- **진단 방법**: 복부 X-ray에서 여러 개의 공기-액체 수준이 관찰되면 장폐색 또는 장중막동맥증후군 등을 의심해야 합니다.
- **주의 사항**: 공기-액체 수준만으로 질환을 확진할 수 없으며, 임상 증상과 다른 검사 결과를 종합해야 합니다.

---

### 4. **변비 (Constipation)**
- **연령 및 임상 특징**: 생후 몇 주에서 어린 시절까지 발생할 수 있으며, 주요 증상은 배변 횟수 감소, 배변 시 통증, 복부 팽만감 등입니다. 만성 변비는 심한 복통이나 식욕 저하를 유발할 수도 있습니다.
- **복부 X-ray 소견**:
  - 대장이 크게 팽창되어 있고, 대장 내부에 공기와 변이 혼합된 모습인 "**공기-액체 수준**"이 나타납니다.
  - 항문 주변에 변이 많이 쌓여 있는 "**변 덩어리**(Fecal Impaction)"가 관찰될 수도 있습니다.
- **진단 방법**: 복부 초음파 또는 장관 운동 검사를 통해 변비의 원인을 확인합니다.
- **치료법**:
  - 급성 변비에는 좌욕이나 항문관 삽입을 통한 변 배출이 필요하며, 만성 변비에는 섬유질 섭취 증가, 수분 섭취 및 완하제 사용 등이 권장됩니다.
  - 심한 경우에는 장중막동맥증후군 등 구조적 이상이 있을 수 있어 추가 검사가 필요할 수 있습니다.

---
"""

# LoRA용 데이터셋 생성
dataset = []
num_samples = 1000  # 생성할 샘플 수

diseases = ["유문협착증", "장폐색", "공기-액체 수준", "변비"]

styles = ["차분한 의사", "친근한 의사", "세심한 의사"]

for disease in diseases:
    for i in range(num_samples // 4):

        style = random.choice(styles)

        # User 메시지 (input)
        user_input = (
                f"환자 사례 {disease} {i+1}: 임상 시나리오를 지식 기반으로 생성해 주세요."
                f"대답 스타일은 {style}로 작성하세요."
            )

        # 메시지 구조
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input},
        ]

        # Chat template 적용 (토크나이저 공식 방식)
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(model.device)

        # 모델 생성
        with torch.no_grad():
            generated = model.generate(**inputs, max_new_tokens=500)
        
        # 새 토큰만 디코딩
        output_text = tokenizer.decode(
            generated[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )

        dataset.append({
            "instruction": system_instruction.strip(),
            "input": user_input,
            "output": output_text.strip()
        })

        print(f"{disease} {i+1} sample 생성 완료")

# JSON 파일 저장
with open("lora_dataset_chat_template.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"{num_samples}개의 데이터셋 생성 완료")
