"""Konfigurácia aplikácie (cez premenné prostredia s rozumnými predvolbami)."""

from __future__ import annotations

import os


class Settings:
    # SQLite súbor v adresári backend/. Pre PostgreSQL stačí zmeniť DATABASE_URL.
    database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./algoanalyzer.db")

    # Povolené originy frontendu (Vite dev servery).
    cors_origins: list[str] = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:5180",
    ).split(",")

    # Predvolené limity sandboxu (Docker/Linux ich vynúti cez setrlimit).
    default_timeout_ms: int = int(os.environ.get("SANDBOX_TIMEOUT_MS", "10000"))
    default_memory_mb: int = int(os.environ.get("SANDBOX_MEMORY_MB", "512"))


settings = Settings()
