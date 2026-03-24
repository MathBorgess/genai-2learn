from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from flask import Flask


_engine = None
_SessionLocal = None


def init_db(app: Flask) -> None:
    global _engine, _SessionLocal
    database_url = app.config["DATABASE_URL"]
    _engine = create_engine(database_url, pool_pre_ping=True)
    _SessionLocal = sessionmaker(bind=_engine)


def get_db_session() -> Session:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return _SessionLocal()
