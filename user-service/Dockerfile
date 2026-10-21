FROM python:3.13-slim

WORKDIR /app

# Install OS updates and dependencies in a single layer, then drop cache
COPY requirements.txt .
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Run as a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 5001

# Use gunicorn for production-safe multi-worker serving
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5001", "app:app"]