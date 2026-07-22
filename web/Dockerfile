# Reflex single-container prod: install toolchain, BUILD the frontend, run backend + Caddy on $PORT.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl unzip \
    && curl -sL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/bin/caddy \
    && chmod +x /usr/bin/caddy \
    && curl -fsSL https://bun.sh/install | bash \
    && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.bun/bin:${PATH}"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ARG API_URL=https://oakmore-web.onrender.com
ENV API_URL=${API_URL}

# init downloads reflex's bun + node toolchain; export runs the real frontend build.
RUN reflex init --loglevel default
RUN reflex export --frontend-only --no-zip
# fail the build loudly if the static export is empty, and show what we got
RUN test -f .web/_static/index.html && echo "STATIC OK:" && ls .web/_static | head -20

ENV PORT=8080
CMD reflex run --env prod --backend-only --backend-port 8000 & \
    sleep 4 && caddy run --config /app/Caddyfile --adapter caddyfile
