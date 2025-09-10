FROM pytorch/pytorch:2.8.0-cuda12.6-cudnn9-runtime
WORKDIR /app

RUN sed -i 's|http://archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com/ubuntu|https://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y git libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/GGoneng/AI-Doctor.git /app

# 프로젝트 패키지 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# 컨테이너 종료 방지
CMD ["sleep", "infinity"]
