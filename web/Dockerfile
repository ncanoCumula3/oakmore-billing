# Reflex single-container prod: build the frontend, run backend + Caddy on $PORT.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl unzip \
    && curl -sL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/bin/caddy \
    && chmod +x /usr/bin/caddy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Public URL of this service so the browser reaches the backend through Caddy.
ARG API_URL=https://oakmore-web.onrender.com
ENV API_URL=${API_URL}

# Initialise + export the static frontend (downloads bun on first run).
RUN reflex init --loglevel warning || true
RUN reflex export --frontend-only --no-zip

ENV PORT=8080
CMD reflex run --env prod --backend-only --backend-port 8000 & \
    sleep 4 && caddy run --config /app/Caddyfile --adapter caddyfile
