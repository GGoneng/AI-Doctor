from langchain.prompts import PromptTemplate
from langchain_community.llms import VLLM

MODEL_NAME = "snuh/hari-q3"

llm = VLLM(
    model=MODEL_NAME,
    max_new_tokens=1024,
    top_k=10,
    top_p=0.95,
    temperature=0.8
)

prompts = {
"xray" : PromptTemplate(
input_variables=["symptom"],
template="""
    ### Instruction:
    당신은 임상 지식을 갖춘 유능하고 신뢰할 수 있는 한국어 기반 의료 어시스턴트입니다.
    사용자의 질문에 대해 정확하고 신중한 임상 추론을 바탕으로 진단 가능성을 제시해 주세요.
    반드시 환자의 연령, 증상, 검사 결과, 통증 부위 등 모든 단서를 종합적으로 고려하여 추론 과정과 진단명을 제시해야 합니다.
    의학적으로 정확한 용어를 사용하되, 필요하다면 일반인이 이해하기 쉬운 용어도 병행해 설명해 주세요.

    ### Question:
    소아 복부 X-ray에서 {symptom}이 발견되었습니다.
    {symptom}의 증상, 치료 방법을 설명해주세요.

    ### Output:
    [<end>]
    """
),

"question" : PromptTemplate(
input_variables=["question"],
template="""
    ### Instruction:
    당신은 임상 지식을 갖춘 유능하고 신뢰할 수 있는 한국어 기반 의료 어시스턴트입니다.
    사용자의 질문에 대해 정확하고 신중한 임상 추론을 바탕으로 진단 가능성을 제시해 주세요.
    반드시 환자의 연령, 증상, 검사 결과, 통증 부위 등 모든 단서를 종합적으로 고려하여 추론 과정과 진단명을 제시해야 합니다.
    의학적으로 정확한 용어를 사용하되, 필요하다면 일반인이 이해하기 쉬운 용어도 병행해 설명해 주세요.

    ### Question:
    {question}

    ### Output:
    [<end>]
    """    
)}

