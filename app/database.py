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


def run_migrations():
    with engine.begin() as conn:
        columns = conn.execute(text("PRAGMA table_info(opportunities)")).fetchall()
        column_names = [col[1] for col in columns]

        migrations = {
            "source_category": "ALTER TABLE opportunities ADD COLUMN source_category VARCHAR(32) NOT NULL DEFAULT 'lead'",
            "contact_name": "ALTER TABLE opportunities ADD COLUMN contact_name VARCHAR(255) NOT NULL DEFAULT 'unknown'",
            "contact_title": "ALTER TABLE opportunities ADD COLUMN contact_title VARCHAR(255) NOT NULL DEFAULT 'unknown'",
            "contact_source": "ALTER TABLE opportunities ADD COLUMN contact_source VARCHAR(64) NOT NULL DEFAULT 'none'",
            "contact_url": "ALTER TABLE opportunities ADD COLUMN contact_url TEXT",
            "outreach_status": "ALTER TABLE opportunities ADD COLUMN outreach_status VARCHAR(64) NOT NULL DEFAULT 'apply_only'",
        }

        for column, sql in migrations.items():
            if column not in column_names:
                conn.execute(text(sql))
