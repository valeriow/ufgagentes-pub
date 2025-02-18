from pydantic import BaseModel, Field, constr
from typing import Optional, Literal

class LoginRequest(BaseModel):
    usuario: constr(min_length=3, max_length=50) = Field(..., example="user1")
    senha: constr(min_length=2, max_length=50) = Field(..., example="p1")

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., example="novousuario")
    password: constr(min_length=6, max_length=50) = Field(..., example="senha123")
    role: Literal["admin", "user"] = Field(default="user", example="user")

class UserUpdate(BaseModel): 
    username: constr(min_length=3, max_length=50) = Field(..., example="novousuario")
    password: Optional[constr(min_length=6, max_length=50)] = Field(None, example="novasenha123")
    role: Literal["admin", "user"] = Field(default="user", example="user")

class AcordaoCreate(BaseModel): 
    texto: constr(min_length=10) = Field(..., example="O relator apresentou voto no sentido de...")

class AcordaoFeedback(BaseModel):
    feedback: constr(min_length=1, max_length=1000) = Field(
        ..., 
        example="Ementa gerada com sucesso e adequada ao conteúdo"
    )

class BootstrapRequest(BaseModel):
    install_key: constr(min_length=8) = Field(
        ..., 
        example="sua-chave-secreta"
    )
