FROM pytorch/pytorch:2.8.0-cuda12.6-cudnn9-runtime
WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/GGoneng/AI-Doctor.git /app

# 프로젝트 패키지 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# 컨테이너 종료 방지
CMD ["sleep", "infinity"]
