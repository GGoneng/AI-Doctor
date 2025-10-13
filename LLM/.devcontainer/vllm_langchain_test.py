from langchain_community.llms import VLLM
    
llm_model = VLLM(
    model="snuh/hari-q3",
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    temperature=0.8,
    vllm_kwargs={
        "quantization": "bitsandbytes",
        "gpu_memory_utilization": 0.9
    }
)

print(llm_model.invoke("유문협착증의 증상과 치료방법에 대해 설명해주세요.")) 