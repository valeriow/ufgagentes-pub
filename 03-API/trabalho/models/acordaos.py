from sqlalchemy import Column, Integer, Text
from models.base import Base
from pydantic import BaseModel

class Acordao(Base):
    __tablename__ = "acordaos"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(Text)
    ementa = Column(Text)
    feedback = Column(Text, nullable=True)

class AcordaoRequest(BaseModel):
    texto_acordao: str