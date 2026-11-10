FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=5000 FEATURE_DESCONTO_PROMO=false

WORKDIR /app

RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools && python -m pip install --no-cache-dir -r requirements.txt && addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY app.py .
COPY templates ./templates
COPY static ./static

RUN mkdir -p /app/data && chown -R appuser:appgroup /app

USER appuser
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]