FROM nvidia/cuda:12.6.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    git \
    curl \
    ca-certificates \
    sudo \
    iptables \
    vim \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://get.docker.com | sh

ENV PATH="/usr/local/bin:$PATH"

VOLUME /var/lib/docker

WORKDIR /app

RUN git clone https://github.com/GGoneng/AI-Doctor.git /app

CMD ["sleep", "infinity"]


