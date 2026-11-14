FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PAPERCUT_LIB=/app/library

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.py ./
COPY library ./library
COPY studio_api ./studio_api

RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    pydantic>=2.9.0 \
    bcrypt>=4.2.0 \
    cryptography>=43.0.0 \
    jsonschema>=4.20.0 \
    numpy>=1.24.0 \
    pillow>=10.0.0 \
    platformdirs>=4.0.0 \
    python-dotenv>=1.0.0 \
    requests>=2.31.0 \
    soundfile>=0.12.1

EXPOSE 8420

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://127.0.0.1:8420/health || exit 1

CMD ["uvicorn", "studio_api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8420", "--workers", "1"]
