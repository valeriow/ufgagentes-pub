from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJ...",
                "token_type": "bearer"
            }
        }

class Message(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operação realizada com sucesso"
            }
        }

class DatabaseInitRequest(BaseModel):
    force: bool = False

class BootstrapRequest(BaseModel):
    admin_username: str
    admin_password: str
    install_key: str
