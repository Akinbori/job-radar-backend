from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- MIGRATION FIX ---
def run_migrations():
    with engine.begin() as conn:
        columns = conn.execute(text("PRAGMA table_info(opportunities)")).fetchall()
        column_names = [col[1] for col in columns]

        if "source_category" not in column_names:
            conn.execute(
                text("ALTER TABLE opportunities ADD COLUMN source_category VARCHAR(32) NOT NULL DEFAULT 'lead'")
            )
