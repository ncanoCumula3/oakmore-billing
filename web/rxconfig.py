import os
import reflex as rx

# Single-container prod: Caddy fronts $PORT, serves the exported frontend, and proxies
# /_event, /ping, /_upload to the reflex backend on 8000. api_url is this service's public URL.
config = rx.Config(
    app_name="oakmore",
    api_url=os.environ.get("API_URL", "http://localhost:8000"),
    cors_allowed_origins=["*"],
)
