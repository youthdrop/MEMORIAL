# ---- 1) Build frontend (Vite) ----
FROM node:20-alpine AS fe
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend ./
RUN npm run build

# ---- 2) Backend runtime (Flask/Gunicorn) ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# Python deps
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install -r backend/requirements.txt

# Backend code
COPY backend ./backend

# Frontend build where app.py expects it: ../frontend/dist relative to backend/
COPY --from=fe /fe/dist ./frontend/dist

# Run
WORKDIR /app/backend
ENV PORT=8080
CMD ["gunicorn","-b","0.0.0.0:8080","app:app"]
