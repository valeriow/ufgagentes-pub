from sqlalchemy import Column, Integer, String
from models.base import Base
from pydantic import BaseModel
from typing import Optional


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

class UserBase(BaseModel):
    username: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "user1",
                "role": "user"
            }
        }

