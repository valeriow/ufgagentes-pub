from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime
from models.base import LogBase

class LogEntry(LogBase):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    level = Column(String, index=True)
    message = Column(Text)
    trace = Column(Text, nullable=True)