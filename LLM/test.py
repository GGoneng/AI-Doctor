# generate_medical_dataset.py
# 실행: python generate_medical_dataset.py
# 출력: lora_dataset_1000.jsonl (각 줄이 JSON)

import json
import random
from datetime import datetime

random.seed(42)

# --- 사전 지식(사용 가능한 정보) 요약(절대 이 외 정보 사용 금지) ---
# 우리가 사용할 수 있는 질환: 유문협착증, 장폐색(기복증), 공기-액체 수준(방사선 징후), 변비
# 각 질환의 핵심 포인트들만 사용합니다 (사용자 제공 지식 범위 내).
# (스크립트 내부의 텍스트는 모두 한국어이며, 주어진 지식만을 이용합니다.)

diseases = [
    "유문협착증",
    "장폐색",
    "공기-액체 수준",
    "변비"
]

# 보호자 질문 템플릿들 (질문은 보호자가 묻는 말투)
question_templates = [
    "안녕하세요, 제 아이가 {age}인데요. {symptom_short} {duration} 어떡하죠?",
    "제 아이({age})가 {symptom_short} 하고 있어요. {duration} 어떤 문제일까요?",
    "아이 걱정돼서요. {symptom_short} 증상에다가 {extra_symptom}. 이럴 때 무슨 병일 수 있나요?",
    "{age} 아기인데 {symptom_short}이(가) 심해요. 방금 X-ray를 찍었더니 어떻게 판단하나요?",
    "{age} 보호자인데요, 아이가 {symptom_short} 있어요. 검사나 치료는 어떻게 해야 하나요?"
]

# 나이 표현(질환별 유리한 나이 포함)
ages_general = ["신생아", "생후 4주 남아", "생후 5주 남아", "생후 6주 남아", "3개월 영아", "1세 영유아"]
ages_for_pyloric = ["생후 3주 남아", "생후 4주 남아", "생후 5주 남아"]

# 증상 조각
symptom_shorts = {
    "유문협착증": ["먹은 뒤 심한 구토가 있어요", "사격성(튀는) 구토가 관찰돼요", "복부 팽만과 구토가 반복돼요"],
    "장폐색": ["심한 구토와 복부 팽만이 있어요", "복통과 배변 중단 증상이 있어요", "배가 많이 부풀어 올라요"],
    "공기-액체 수준": ["X-ray에서 공기와 액체가 보인대요", "복부 X-ray에 공기-액체가 여러 개 보였어요", "복부 촬영 결과 공기-액체 수준 소견이 있다고 하네요"],
    "변비": ["배변 횟수가 줄고 배가 팽창해요", "대변을 못 보고 힘들어해요", "항문 주위에 단단한 덩어리가 만져져요"]
}

extra_symptoms = [
    "울음이 예전보다 잦고 탈수 증상이 의심돼요",
    "체중이 늘지 않아요",
    "구강이 마르고 소변 횟수가 줄었어요",
    "구토 물이 우유 냄새에요"
]

durations = ["며칠째", "하루 종일", "몇 시간째", "수일 전부터", "어제부터 계속"]

# 의사 응답 템플릿(의학적 reasoning 포함 — 반드시 지식 범위 내)
# 각 질환별 템플릿은 지식에 포함된 키워드만 사용합니다.
answer_templates = {
    "유문협착증": [
        ("인사 및 공감", "안녕하세요. 걱정 많으시겠습니다. "),
        ("초기평가", "연령이 {age}인 점과 {symptom} 소견을 종합하면 유문협착증의 가능성을 고려해야 합니다. 특히 생후 3~6주 사이 남아에서 먹은 후 몇 분 내에 발생하는 심한 구토(사격성 구토)는 유문협착증의 전형적인 증상입니다. "),
        ("영상근거", "복부 X-ray에서는 위가 팽창하고 '더블 버블 징후'가 관찰될 수 있으며, 유문부의 두꺼워짐(타깃 징후, 올리브 모양 종괴)이 보이면 진단을 의심하게 됩니다. "),
        ("권고검사", "확진은 초음파 검사(유문부 두께 측정)로 합니다. 초음파 검사를 권해드립니다. "),
        ("치료/조치", "응급성 탈수가 있으면 우선 수액 보충 등 안정화가 필요하며, 확진 시 표준 치료는 유문근막절개술(수술)입니다. 일부 내시경적 치료 시도가 알려져 있으나 대부분 수술적 처치가 필요합니다. "),
        ("주의", "즉시 진료를 권하며, 탈수나 체중감소가 있으면 빨리 응급실로 가시길 권합니다. ")
    ],
    "장폐색": [
        ("인사 공감", "안녕하세요. 상황이 급해 보이네요. "),
        ("초기평가", "증상(복부 팽만, 구토, 배변 중단 등)과 X-ray 소견을 종합하면 장폐색(기복증)을 의심할 수 있습니다. "),
        ("영상근거", "복부 X-ray에서 장관 확장과 다발성 '공기-액체 수준'이 관찰되는 것은 장폐색을 시사하는 전형적 소견입니다. 심한 경우 복막하 공기 소견이 나타날 수 있습니다. "),
        ("권고검사", "폐색의 위치와 원인을 확인하기 위해 복부 초음파나 CT 검사가 필요합니다. "), 
        ("치료/조치", "원인에 따라 다르지만 선천성 원인이면 수술이 필요합니다. 보존적 치료(금식, 정맥영양 등)를 먼저 시행할 수 있고, 원인에 따라 내시경적 감압이나 수술적 치료가 필요할 수 있습니다. "),
        ("주의", "복막염 소견(심한 통증, 발열, 혈액검사 이상)이 있으면 즉시 응급 수술이 필요할 수 있으니 지체하지 마십시오. ")
    ],
    "공기-액체 수준": [
        ("인사 공감", "안녕하세요. 검사 결과를 보시고 놀라셨겠어요. "),
        ("초기평가", "공기-액체 수준은 질환 자체가 아니라 방사선학적 징후입니다. 여러 개의 공기-액체 수준이 관찰되면 장폐색이나 장내 내용물 축적을 의심해야 합니다. "),
        ("영상근거", "X-ray에서 공기와 액체가 동시에 존재하는 모습은 폐색을 시사할 수 있지만 단독으로 확진을 내리진 않습니다. "),
        ("권고검사", "임상 증상과 함께 초음파 또는 CT 등 추가 검사가 필요합니다. "),
        ("치료/조치", "공기-액체 수준은 원인 질환(예: 장폐색, 변비 등)에 따라 치료가 달라집니다. 원인에 따른 치료 계획을 세워야 합니다. "),
        ("주의", "증상이 심하거나 배가 심하게 부풀고 통증이 심하면 즉시 추가 검사 및 치료가 필요합니다. ")
    ],
    "변비": [
        ("인사 공감", "안녕하세요. 배변 문제로 많이 불편하셨겠어요. "),
        ("초기평가", "배변 횟수 감소, 배변 시 통증, 복부 팽만 등은 소아 변비의 전형적 증상입니다. "),
        ("영상근거", "복부 X-ray에서는 대장 팽창과 공기-변이 혼합된 모습, 항문 주변에 변 덩어리(변 덩어리)가 관찰될 수 있습니다. 때론 공기-액체 수준 소견이 동반될 수 있습니다. "),
        ("권고검사", "대부분은 임상 진찰과 병력으로 진단하지만 필요하면 복부 초음파나 장관 운동 검사로 원인 평가를 할 수 있습니다. "),
        ("치료/조치", "급성일 경우 좌욕이나 관을 통한 배변 유도 등이 필요할 수 있고, 만성일 경우 섬유질 섭취 증가, 충분한 수분 섭취, 적절한 완하제 사용을 권장합니다. "),
        ("주의", "심한 통증, 출혈, 체중감소가 있으면 추가 검사가 필요합니다. ")
    ]
}

# 답변 포맷 생성 함수 (의사 대화형)
def make_answer(disease, age, symptom_snippet, extra=None):
    parts = answer_templates[disease]
    # 각 파트는 (tag, text_template)
    answer = ""
    for tag, template in parts:
        # 일부 템플릿 안의 {age} {symptom} 치환
        text = template.format(age=age, symptom=symptom_snippet)
        answer += text
    # 끝맺음: 공감과 행동 권고는 이미 포함되어 있음
    return answer.strip()

# 질문 생성 함수
def make_question(disease):
    # 나이 선택
    if disease == "유문협착증":
        age = random.choice(ages_for_pyloric)
    else:
        age = random.choice(ages_general)
    symptom = random.choice(symptom_shorts[disease])
    extra = random.choice(extra_symptoms) if random.random() < 0.3 else ""
    duration = random.choice(durations)
    q_template = random.choice(question_templates)
    question = q_template.format(age=age, symptom_short=symptom, extra_symptom=extra, duration=duration)
    # 정제: 겹치는 공백 제거
    question = " ".join(question.split())
    return question, age, symptom

# 메인 생성 루프
def generate_dataset(per_disease=250, out_path="lora_dataset_1000.jsonl"):
    total = per_disease * len(diseases)
    count = 0
    dataset = []
    for disease in diseases:
        for i in range(per_disease):
            q, age, symptom_snippet = make_question(disease)
            # Answer: 의사 응답 — 지식 범위 내 상세화
            ans = make_answer(disease, age, symptom_snippet)
            # 약간의 다양성(말투 뉘앙스) 추가: 친근/차분/세심은 system 레벨에서 통제되므로
            # 여기서는 답변 끝 문장 일부를 무작위로 바꿈(권고 강조 등)
            closing = ""
            if disease == "유문협착증":
                closing_choices = [
                    "빠른 진료와 초음파 검사를 권합니다.",
                    "탈수 증상이 보이면 즉시 응급실로 가시길 바랍니다."
                ]
            elif disease == "장폐색":
                closing_choices = [
                    "즉시 추가 영상 검사 및 외과적 평가가 필요할 수 있습니다.",
                    "금식 및 수액치료 등 초기 처치가 필요합니다."
                ]
            elif disease == "공기-액체 수준":
                closing_choices = [
                    "임상 양상과 추가 검사를 토대로 원인 규명이 필요합니다.",
                    "필요 시 초음파/CT 검사를 진행해 원인을 확인하시기 바랍니다."
                ]
            else:  # 변비
                closing_choices = [
                    "식이조절과 수분 섭취를 권하며 증상 지속 시 내원하세요.",
                    "심한 경우 항문 관리를 통한 배변 유도가 필요할 수 있습니다."
                ]
            if random.random() < 0.6:
                closing = " " + random.choice(closing_choices)
            ans = ans + closing
            # assemble record: use Instruction fixed, Question into 'input', answer into 'output'
            record = {
                "instruction": (
                    "당신은 임상 지식을 갖춘 유능하고 신뢰할 수 있는 한국어 기반 의료 어시스턴트입니다. "
                    "사용자의 질문에 대해 정확하고 신중한 임상 추론을 바탕으로 진단 가능성을 제시해 주세요. "
                    "반드시 환자의 연령, 증상, 검사 결과, 통증 부위 등 모든 단서를 종합적으로 고려하여 추론 과정과 진단명을 제시해야 합니다. "
                    "의학적으로 정확한 용어를 사용하되, 필요하다면 일반인이 이해하기 쉬운 용어도 병행해 설명해 주세요. "
                    "아래의 지식 정보만 사용하세요: 유문협착증, 장폐색, 공기-액체 수준(방사선 징후), 변비에 대한 사전 지식."
                ),
                "input": q,
                "output": ans
            }
            dataset.append(record)
            count += 1
            if count % 50 == 0:
                print(f"{count}/{total} samples generated ({datetime.now().isoformat()})")
    # 파일로 저장
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"완료: 총 {len(dataset)}개 생성, 파일명: {out_path}")

if __name__ == "__main__":
    # per disease 갯수 변경 가능 (기본 250)
    generate_dataset(per_disease=250, out_path="lora_dataset_1000.jsonl")
