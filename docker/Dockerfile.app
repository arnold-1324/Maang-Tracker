
# Multi-stage Dockerfile for MAANG Tracker App
FROM python:3.11-slim as base

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --prefer-binary 2>&1 || pip install --no-cache-dir -r requirements.txt

# ==================== DEVELOPMENT STAGE ====================
FROM base as development

ENV ENVIRONMENT=development
ENV DEBUG=True
ENV PYTHONUNBUFFERED=1

COPY . .

# Expose ports for development services
EXPOSE 5000 8765 8000

# Default command for development
CMD ["python", "-m", "ui.dashboard"]

# ==================== PRODUCTION STAGE ====================
FROM base as production

ENV ENVIRONMENT=production
ENV DEBUG=False
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 appuser

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000 8765

# Run gunicorn for production
RUN pip install --no-cache-dir gunicorn

CMD ["gunicorn", \
     "--workers=4", \
     "--worker-class=sync", \
     "--bind=0.0.0.0:5000", \
     "--timeout=120", \
     "--access-logfile=-", \
     "--error-logfile=-", \
     "ui.dashboard:app"]

# ==================== HEALTHCHECK ====================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
