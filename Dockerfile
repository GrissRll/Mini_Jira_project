FROM python:3.14-slim AS base

WORKDIR /app

RUN pip install --upgrade pip

ENV PYTHONNUNBUFFERING=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

COPY requirements.txt /app

RUN pip install --no-cache -r requirements.txt

FROM base AS development

COPY . .

CMD ["uvicorn", "app.main:app","--host", "0.0.0.0","--port", "8080", "--reload"]

FROM base AS production


COPY . .

CMD ["uvicorn", "app.main.py:app","--host", "0.0.0.0","--port", "8080"]

