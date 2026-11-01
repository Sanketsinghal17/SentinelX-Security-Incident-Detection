import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import Config
from app.models.models import Base

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass
