# DocSentinel — API server
# Python 3.11 slim; run with docker-compose for API + optional Ollama.
FROM python:3.11-slim

WORKDIR /app

# System deps for pymupdf (PDF) and embedding models
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Chroma and uploads persist here
ENV CHROMA_PERSIST_DIR=/data/chroma
VOLUME /data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
