FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# 1) dependencies first (cached unless pyproject.toml/poetry.lock change)
RUN pip install --no-cache-dir "poetry>=1.8,<3"
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root

# 2) application code
COPY . .

# 3) run as a non-root user; logs/ is the only writable place
ARG APP_UID=1000
RUN useradd --create-home --uid ${APP_UID} appuser \
    && mkdir -p /app/logs \
    && chown -R appuser /app/logs
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
