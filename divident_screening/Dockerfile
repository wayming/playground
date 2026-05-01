# Use official Ubuntu base image
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# Set non-interactive mode to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies (curl, git, etc.)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    zstd \
    && rm -rf /var/lib/apt/lists/*

ARG DEV_UID=1000
ARG DEV_GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    bash \
    unzip \
    ca-certificates \
    sudo \
    openssh-client \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libx11-6 \
    libxcb1 \
    libxcb-xinerama0 \
    libxkbcommon0

RUN apt update && apt install -y tesseract-ocr libgl1

RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*
    
RUN if getent passwd 1000; then userdel -f $(getent passwd 1000 | cut -d: -f1); fi \
    && if getent group 1000; then groupdel $(getent group 1000 | cut -d: -f1) || true; fi

RUN groupadd -g ${DEV_GID} dev \
    && useradd -m -u ${DEV_UID} -g dev -s /bin/bash -d /home/dev dev \
    && mkdir -p /workspace \
    && chown -R dev:dev /workspace /home/dev
USER dev
WORKDIR /workspace

ENV NPM_CONFIG_PREFIX=/home/dev/.npm-global
ENV PATH=/home/dev/.npm-global/bin:/home/dev/.local/bin:$PATH

#RUN npm install -g @anthropic-ai/claude-code

# ENV CLAUDE_CONFIG_DIR=/workspace/claude_config
RUN pip install --upgrade pip
RUN npm install -g @anthropic-ai/claude-code
CMD ["tail", "-f", "/dev/null"]