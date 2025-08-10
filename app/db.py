import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite://")


DATABASE_URL = os.getenv("CARD_INV_DB_URL", "sqlite:///./card_inventory.db")

connect_args = {"check_same_thread": False} if _is_sqlite(DATABASE_URL) else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()