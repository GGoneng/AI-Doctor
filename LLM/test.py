from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_name = "snuh/hari-q3"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,     # 8bit 양자화로 메모리 절약
    device_map="auto"
)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer
)

prompt = "Pyloric_Stenosis 증상, 치료법, 유의해야할 점 알려줘"
result = generator(prompt, truncation=True, do_sample=True, temperature=0.8, top_p=0.9)

print(result[0]['generated_text'])
