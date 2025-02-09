from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, Text
from models.base import Base

class Acordao(Base):
    __tablename__ = "acordaos"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(Text)
    ementa = Column(Text)
    feedback = Column(Text, nullable=True)

class AcordaoResponse(BaseModel):
    id: int
    texto: str
    ementa: str
    feedback: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "texto": "Texto do acórdão...",
                "ementa": "Ementa gerada...",
                "feedback": None
            }
        }
