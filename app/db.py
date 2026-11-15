from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Base

if settings.database_url.startswith("sqlite:"):
    Path("data").mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        settings.database_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(settings.database_url, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
