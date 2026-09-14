# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend/web_app

COPY frontend/web_app/package*.json ./
RUN npm install

COPY frontend/web_app ./
RUN npm run build


# Stage 2: Production Python Backend + Served Static Bundle
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies (including Tesseract OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY backend ./backend
COPY data ./data

# Copy built frontend assets
COPY --from=frontend-build /app/frontend/web_app/dist ./frontend/web_app/dist

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]