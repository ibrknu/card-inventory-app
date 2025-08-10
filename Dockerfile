# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (only what's needed to build common wheels)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY . /app

# Default DB path inside container (mounted volume recommended)
ENV CARD_INV_DB_URL=sqlite:////data/card_inventory.db

EXPOSE 8000

CMD ["uvicorn", "card_inventory.app.main:app", "--host", "0.0.0.0", "--port", "8000"]