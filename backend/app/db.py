"""SQLAlchemy engine, session a deklaratívna báza.

Lokálne beží SQLite. Pri nasadení Postgres v samostatnej schéme (algolab),
pripojenie cez pooler Supabase v transakčnom režime, preto bez poolu na strane
aplikácie a bez pripravených dotazov.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

if settings.is_postgres:
    url = settings.database_url
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    _engine = create_engine(url, poolclass=NullPool, connect_args={"prepare_threshold": None})
    engine = _engine.execution_options(schema_translate_map={None: settings.db_schema})
else:
    _engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    engine = _engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def ensure_schema() -> None:
    if settings.is_postgres:
        with _engine.begin() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_namespace WHERE nspname = :s"), {"s": settings.db_schema}
            ).first()
            # Rola aplikácie nemusí mať právo vytvárať schémy, preto len ak chýba.
            if not exists:
                conn.execute(text(f'CREATE SCHEMA "{settings.db_schema}"'))


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
