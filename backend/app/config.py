"""Konfigurácia aplikácie cez premenné prostredia."""

from __future__ import annotations

import os


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


class Settings:
    # Lokálne SQLite. Pri nasadení Postgres (Supabase), napr.
    # postgresql+psycopg://user:heslo@host:6543/postgres
    database_url: str = _env("DATABASE_URL", "sqlite:///./algoanalyzer.db")
    # Schéma v Postgrese, aby AlgoLab nezasahoval do iných tabuliek projektu.
    db_schema: str = _env("DB_SCHEMA", "algolab")

    cors_origins: list[str] = [
        o for o in _env(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:5180",
        ).split(",") if o
    ]

    # Ak je nastavené, kód sa spúšťa na samostatnom runneri (Vercel projekt bez hesiel).
    runner_url: str = _env("RUNNER_URL")
    runner_token: str = _env("RUNNER_TOKEN")

    # Ak je nastavené, vytváranie a úprava vlastného kódu vyžaduje toto heslo.
    edit_password: str = _env("EDIT_PASSWORD")

    # Limity sandboxu.
    default_timeout_ms: int = int(_env("SANDBOX_TIMEOUT_MS", "5000"))
    max_timeout_ms: int = int(_env("SANDBOX_MAX_TIMEOUT_MS", "10000"))
    # Koľko sekúnd smie trvať jedna dávka experimentu (jedno volanie /step).
    step_budget_s: float = float(_env("STEP_BUDGET_S", "15"))
    max_algorithms_per_experiment: int = int(_env("MAX_ALGORITHMS", "8"))

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgres")


settings = Settings()
