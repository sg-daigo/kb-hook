# syntax=docker/dockerfile:1.7

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# apt-get（キャッシュ & tmpfs）
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    --mount=type=tmpfs,target=/var/lib/apt/lists \
    apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates wget \
 && apt-get clean

# uv インストール（pip cache）
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir uv==0.5.11

# 依存定義のみ先にコピー
COPY pyproject.toml uv.lock ./

# uv sync（uv cache）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /app/.venv --python /usr/local/bin/python \
 && uv sync --frozen --no-dev

# ソースコード
COPY *.py ./

# テンプレート
RUN mkdir ./templates
COPY templates/*.j2 ./templates/

EXPOSE 3001
VOLUME /app/conf/config.ini
VOLUME /app/conf/logging.ini

ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=3001"]
