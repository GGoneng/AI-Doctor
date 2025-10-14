FROM pytorch/pytorch:2.8.0-cuda12.6-cudnn9-runtime
WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 build-essential

COPY requirements.txt .

RUN pip install --no-cache-dir -r /app/requirements.txt
