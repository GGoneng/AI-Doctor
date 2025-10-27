from huggingface_hub import snapshot_download

# D드라이브 내 원하는 폴더에 모델 저장
model_path = snapshot_download("snuh/hari-q3", cache_dir="F:/huggingface_models")

print("모델 다운로드 완료 경로:", model_path)
