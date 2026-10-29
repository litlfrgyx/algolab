# Linux kontajner: tu platia limity sandboxu (setrlimit) a izolácia súborov a siete.
# Zostavenie z koreňa repozitára:  docker compose -f backend/docker-compose.yml up --build
FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY runner /runner

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
