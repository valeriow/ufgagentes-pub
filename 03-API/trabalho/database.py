from sqlalchemy import create_engine
from models.base import Base
from sqlalchemy.orm import sessionmaker
from logging import Handler
from contextlib import contextmanager
from datetime import datetime

from models.logs import LogEntry
from settings import DATABASE_URL, LOG_DATABASE_URL


# Database engines
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
log_engine = create_engine(LOG_DATABASE_URL, connect_args={"check_same_thread": False})

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
LogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=log_engine)

def get_log_db():
    db = LogSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def recreate_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

class DatabaseHandler(Handler):
    def emit(self, record):
        db = next(get_log_db())
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            message=record.getMessage()
        )
        db.add(log_entry)
        db.commit()

# Export what's needed
#__all__ = ['Base', 'engine', 'get_db', 'DatabaseHandler']