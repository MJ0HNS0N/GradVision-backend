"""
Database setup: engine, session factory, and the declarative Base
that gradvision_models.py builds on.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Swap this for your real Postgres URL in production / via env var.
# Example Postgres URL: postgresql+psycopg://user:pass@localhost:5432/gradvision
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gradvision.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# FastAPI dependency: `db: Session = Depends(get_db)`
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
