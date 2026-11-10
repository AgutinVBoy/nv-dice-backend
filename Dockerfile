FROM python:3.11.9-slim AS builder

COPY --from=ghcr.io/astral-sh/uv /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT="/app/.venv" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project


FROM python:3.11.9-slim


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY alembic.ini gunicorn_conf.py ./
COPY alembic ./alembic
COPY ./src ./src

RUN pybabel compile -d ./src/locales/ && python -m compileall src/

EXPOSE 8000

CMD ["gunicorn", "src.main:app", "-c", "gunicorn_conf.py"]