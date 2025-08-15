FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    GUNICORN_CMD_ARGS="--workers 2 --worker-class gthread --threads 8 --timeout 120 --bind 0.0.0.0:${PORT}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt

COPY . /app

ENV PATH="/opt/venv/bin:$PATH"
CMD ["gunicorn", "wsgi:app"]

