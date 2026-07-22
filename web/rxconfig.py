import os
import reflex as rx

# API_URL is the Reflex *backend* public URL (set on both services in prod).
config = rx.Config(
    app_name="oakmore",
    api_url=os.environ.get("API_URL", "http://localhost:8000"),
    cors_allowed_origins=["*"],
    frontend_port=int(os.environ.get("PORT", 3000)),
    backend_port=int(os.environ.get("BACKEND_PORT", 8000)),
)
