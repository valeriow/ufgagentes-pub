from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from settings import SECRET_KEY
import jwt

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

def check_admin_access(payload: dict = Depends(get_current_user)):
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permissão negada")
    return payload

def check_user_access(payload: dict = Depends(get_current_user)):
    if payload["role"] not in ["user", "admin"]:
        raise HTTPException(status_code=403, detail="Permissão negada")
    return payload
