# --- Stage 1: build the React frontend ---
FROM node:20-alpine AS frontend
WORKDIR /app/frontend

# install deps
COPY frontend/package*.json ./
RUN npm ci

# build
COPY frontend/ .
RUN npm run build


# --- Stage 2: Python backend runtime ---
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# system deps (for psycopg2/builds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
  && rm -rf /var/lib/apt/lists/*

# install backend deps
COPY backend/requirements.txt backend/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r backend/requirements.txt

# copy backend app code
COPY backend/ backend/

# copy built frontend into /app/frontend/dist (what your Flask app serves)
COPY --from=frontend /app/frontend/dist ./frontend/dist

# entrypoint to run migrations then start gunicorn
COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/backend
EXPOSE 8080
CMD ["/entrypoint.sh"]
