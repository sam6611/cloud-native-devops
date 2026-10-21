FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 5002

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5002", "app:app"]