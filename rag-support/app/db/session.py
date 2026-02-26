from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.utils.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {'check_same_thread': False} if settings.db_url.startswith('sqlite') else {}
engine = create_engine(settings.db_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
