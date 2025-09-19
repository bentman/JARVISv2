# orchestrator/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY orchestrator.py .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir fastapi uvicorn httpx gunicorn
EXPOSE 7000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "orchestrator:app", "--bind", "0.0.0.0:7000"]