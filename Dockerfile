FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CHROME_PATH=/usr/bin/chromium \
    PAPERCUT_LIB=/app/library

# Install system dependencies: Node.js 20, ffmpeg, Chromium (for Remotion & Web Audio BGM), rclone, fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    ffmpeg \
    chromium \
    rclone \
    fonts-liberation \
    fonts-noto-core \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package definitions first for better Docker layer caching
COPY pyproject.toml README.md ./
COPY library/papercut/template/package.json library/papercut/template/package-lock.json ./library/papercut/template/

RUN npm ci --prefix /app/library/papercut/template --no-audit --no-fund

# Copy workflow, agents, config, assets, and library
COPY . .

RUN pip install --no-cache-dir -e . && mkdir -p /app/episodes /app/out

ENTRYPOINT ["papercraft"]
CMD ["doctor"]
