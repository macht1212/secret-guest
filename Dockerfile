FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN adduser --disabled-password --gecos '' appuser

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY --chown=appuser:appuser . .

USER appuser

CMD alembic upgrade head; uvicorn 'src.main:app' --host=0.0.0.0 --port=8080
