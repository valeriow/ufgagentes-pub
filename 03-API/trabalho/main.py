from fastapi import FastAPI, Depends, UploadFile, File, Query, Path, status, Request
from fastapi.openapi.utils import get_openapi
from fastapi.params import Body
from fastapi.routing import APIRouter
import logging
import jwt
import litellm
import PyPDF2
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import textwrap


# Import settings and database
from models.acordaos import AcordaoRequest
from settings import (
    API_TITLE, SECRET_KEY, MODEL_NAME, INSTALL_KEY,
    TOKEN_EXPIRE_HOURS, LOG_LEVEL, LOG_FORMAT
)


from database import DatabaseHandler, get_db, get_log_db
from models.logs import LogEntry

from models import (
    User, Acordao
)

from auth import check_admin_access, check_user_access

# Configure logging
logger = logging.getLogger("API")
logger.setLevel(getattr(logging, LOG_LEVEL))
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)
logger.addHandler(DatabaseHandler())


sao_paulo_tz = timezone(timedelta(hours=-3))

# Initialize FastAPI with metadata
app = FastAPI(
    title=API_TITLE,
    description=textwrap.dedent("""
    API para geração automática de ementas de acórdãos usando IA.
    
    ## Funcionalidades
    
    * Geração de ementas a partir de texto
    * Geração de ementas a partir de PDFs
    * Autenticação e autorização
    * Gestão de usuários
    """),
    version="1.0.0",
    contact={
        "name": "Suporte",
        "email": "suporte@exemplo.com",
    },
    license_info={
        "name": "MIT",
    },
)

v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

# Configuração de criptografia de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define constants
ACORDAO_NOT_FOUND = "Acórdão não encontrado"

class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        internal_code: str = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.internal_code = internal_code

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    logger.error(f"APIError: {exc.status_code} - {exc.detail} ({exc.internal_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "internal_code": exc.internal_code
        }
    )

@v1_router.post("/auth/login", 
                description="Autenticar usuário e obter token de acesso",
                tags=["Autenticação"])
async def login(
    usuario: str = Body(..., description="Nome do usuário", min_length=3, example="user1"),
    senha: str = Body(..., description="Senha do usuário", example="p1"),
    db: Session = Depends(get_db)
):
    logger.debug(f"Tentativa de login para usuário: {usuario}")
    user = db.query(User).filter(User.username == usuario).first()
    if not user or not pwd_context.verify(senha, user.password):
        logger.info(f"Falha na autenticação para usuário: {usuario}")
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            internal_code="INVALID_CREDENTIALS"
        )
    
    logger.info(f"Login bem-sucedido para usuário: {usuario}")
    payload = {
        "username": user.username,
        "role": user.role,
        "exp": datetime.now(sao_paulo_tz) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@v1_router.post("/auth/refresh",
                description="Renovar token JWT",
                tags=["Autenticação"])
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    logger.debug("Tentativa de renovação de token")
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Tentativa de refresh sem token")
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            internal_code="TOKEN_MISSING"
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = db.query(User).filter(User.username == payload["username"]).first()
        if not user:
            raise APIError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                internal_code="USER_NOT_FOUND"
            )
        
        new_payload = {
            "username": user.username,
            "role": user.role,
            "exp": datetime.now(sao_paulo_tz) + timedelta(hours=TOKEN_EXPIRE_HOURS)
        }
        new_token = jwt.encode(new_payload, SECRET_KEY, algorithm="HS256")
        logger.info(f"Token renovado com sucesso para usuário: {user.username}")
        return {"access_token": new_token, "token_type": "bearer"}
        
    except jwt.ExpiredSignatureError:
        logger.warning("Tentativa de refresh com token expirado")
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            internal_code="TOKEN_EXPIRED"
        )
    except jwt.InvalidTokenError:
        logger.warning("Tentativa de refresh com token inválido")
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            internal_code="TOKEN_INVALID"
        )

@v1_router.get("/auth/status",
               description="Verificar status da autenticação",
               tags=["Autenticação"])
async def auth_status(
    current_user: dict = Depends(check_user_access)
):
    logger.info(current_user)
    logger.debug(f"Verificando status de autenticação para usuário: {current_user['username']}")
    exp_datetime = datetime.fromtimestamp(current_user["exp"], tz=timezone.utc)
    return {
        "authenticated": True,
        "username": current_user["username"],
        "role": current_user["role"],
        "expires": exp_datetime.isoformat()
    }

@v1_router.post("/acordao/gerar",
                description="Gerar ementa a partir de texto do acórdão",
                tags=["Ementas"])
async def gerar_ementa(
    texto: str = Body(..., description="Texto do acórdão", min_length=3, media_type="text/plain"),
    db: Session = Depends(get_db),
    _: dict = Depends(check_user_access)
    ):
    logger.debug("Iniciando geração de ementa")
    with open("prompt.md", "r") as f:
        texto_prompt = f.read()
        
    resposta = litellm.completion(model=MODEL_NAME, messages=[
        {"role": "system", "content": texto_prompt.replace('"', '\\"').replace('`', '\\`')},
        {"role": "user", "content": f"Gere uma ementa para este acórdão: {texto.replace('"', '\\"').replace('`', '\\`')}"}
    ])
    logger.info("Ementa gerada com sucesso pelo modelo")
    logger.debug(f"Resposta do modelo: {resposta['choices'][0]['message']['content'][:100]}...")
    ementa = resposta["choices"][0]["message"]["content"]
    novo_acordao = Acordao(texto=texto, ementa=ementa)
    db.add(novo_acordao)
    db.commit()
    db.refresh(novo_acordao)
    return novo_acordao

@v2_router.post("/acordao/gerar_pdf",
                description="Gerar ementa a partir de arquivo PDF do acórdão",
                tags=["Ementas"])
async def gerar_ementa_pdf(
    file: UploadFile = File(..., description="Arquivo PDF do acórdão"),
    db: Session = Depends(get_db),
    _: dict = Depends(check_user_access)
):
    logger.debug(f"Iniciando processamento do PDF: {file.filename}")
    pdf_reader = PyPDF2.PdfReader(file.file)
    texto_extraido = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    if not texto_extraido.strip():
        logger.info(f"PDF sem texto extraível: {file.filename}")
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O PDF enviado não contém texto extraível.",
            internal_code="PDF_NO_TEXT"
        )
    logger.info(f"PDF processado com sucesso: {file.filename}")
    return await gerar_ementa(texto=texto_extraido, db=db, _=_)

def init_database(db: Session = Depends(get_db)):
    logger.info("Iniciando inicialização do banco de dados")
    if db.query(User).first() is None:    
        logger.debug("Inserindo usuários de exemplo")
        sample_users = [
            {"username": "user1", "password": "p1", "role": "admin"},
            {"username": "user2", "password": "p2", "role": "user"},
            {"username": "user3", "password": "p3", "role": "user"},
            {"username": "user4", "password": "p4", "role": "user"},
            {"username": "user5", "password": "p5", "role": "user"}
        ]
        
        for user in sample_users:
            hashed_password = pwd_context.hash(user["password"])
            new_user = User(username=user["username"], password=hashed_password, role=user["role"])
            db.add(new_user)
        
        db.commit()
        logger.info("Banco de dados inicializado com sucesso")
        return {"message": "Banco de dados inicializado com sucesso"}
    
    logger.info("Inicialização do banco ignorada - já existe")
    return {"message": "Banco de dados já existe. Use force=True para recriar"}

@app.post("/bootstrap",
          description="Inicializar o sistema com usuário admin",
          tags=["Administração"])
async def bootstrap_admin(
    install_key: str = Query(
        ..., 
        description="Chave de instalação do sistema",
        min_length=8,
        example="sua-chave-secreta"
    ),
    db: Session = Depends(get_db)
):
    logger.info("Iniciando processo de bootstrap")
    if install_key != INSTALL_KEY:
        logger.warning("Tentativa de bootstrap com chave inválida")
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de instalação inválida",
            internal_code="INVALID_INSTALL_KEY"
        )

    try:
        logger.debug("Recriando tabelas do banco de dados")
        
    
        
        if db.query(User).first():
            logger.info("Bootstrap negado - usuários já existem")
            raise APIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bootstrap não permitido: banco de dados já contém usuários",
                internal_code="BOOTSTRAP_NOT_ALLOWED"
            )
        
        init_database(db)
        
        logger.info("Bootstrap concluído com sucesso.")
        return {
            "message": "Bootstrap concluído com sucesso."        }
    except Exception as e:
        logger.error(f"Erro durante bootstrap: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao inicializar o banco de dados",
            internal_code="DB_INIT_ERROR"
        )

# CRUD Operations - Users
@v1_router.get("/users", 
               description="Listar todos os usuários",
               tags=["Usuários"])
async def list_users(
    db: Session = Depends(get_db),
    _: dict = Depends(check_user_access),
    skip: int = Query(
        default=0,
        ge=0,
        description="Número de registros para pular",
        example=0
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Número máximo de registros a retornar",
        example=10
    )
):
    logger.debug(f"Listando usuários: skip={skip}, limit={limit}")
    logger.info("Listando usuários")
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    return {
        "total": total,
        "items": users,
        "skip": skip,
        "limit": limit
    }

@v1_router.get("/users/{user_id}", 
               description="Obter detalhes de um usuário",
               tags=["Usuários"])
async def get_user(
    user_id: int = Path(
        ..., 
        description="ID do usuário",
        gt=0,
        example=1
    ),
    db: Session = Depends(get_db),
    _: dict = Depends(check_user_access)
):
    logger.debug(f"Buscando usuário com ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.info(f"Usuário não encontrado: {user_id}")
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
            internal_code="USER_NOT_FOUND"
        )
    return user

@v1_router.post("/users", 
                description="Criar novo usuário",
                tags=["Usuários"])
async def create_user(
    username: str = Query(
        ..., 
        description="Nome de usuário",
        min_length=3,
        max_length=50,
        example="novousuario"
    ),
    password: str = Query(
        ..., 
        description="Senha do usuário",
        min_length=6,
        example="senha123"
    ),
    role: str = Query(
        default="user",
        description="Papel do usuário (admin ou user)",
        regex="^(admin|user)$",
        example="user"
    ),
    db: Session = Depends(get_db),
    _: dict = Depends(check_admin_access)
):
    logger.info(f"Tentativa de criar novo usuário: {username}")
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        logger.warning(f"Tentativa de criar usuário com username duplicado: {username}")
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe",
            internal_code="USERNAME_EXISTS"
        )
    
    try:
        hashed_password = pwd_context.hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Usuário criado com sucesso: {username}")
        return new_user
    except Exception as e:
        logger.error(f"Erro ao criar usuário {username}: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário",
            internal_code="USER_CREATION_ERROR"
        )

@v1_router.put("/users/{user_id}",
               description="Atualizar usuário",
               tags=["Usuários"])
async def update_user(
    user_id: int = Path(
        ..., 
        description="ID do usuário",
        gt=0,
        example=1
    ),
    username: str = Query(
        ..., 
        description="Nome de usuário",
        min_length=3,
        max_length=50,
        example="novousuario"
    ),
    password: str = Query(
        None, 
        description="Nova senha (opcional)",
        min_length=6,
        example="novasenha123"
    ),
    role: str = Query(
        default="user",
        description="Papel do usuário (admin ou user)",
        regex="^(admin|user)$",
        example="user"
    ),
    db: Session = Depends(get_db),
    _: dict = Depends(check_admin_access)
):
    logger.info(f"Tentativa de atualizar usuário {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.info(f"Tentativa de atualizar usuário inexistente: {user_id}")
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
            internal_code="USER_NOT_FOUND"
        )
    
    try:
        if password:
            db_user.password = pwd_context.hash(password)
            logger.debug(f"Senha atualizada para usuário {user_id}")
        
        db_user.username = username
        db_user.role = role
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuário {user_id} atualizado com sucesso")
        return db_user
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário {user_id}: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário",
            internal_code="USER_UPDATE_ERROR"
        )

@v1_router.delete("/users/{user_id}", 
                  description="Excluir usuário",
                  tags=["Usuários"])
async def delete_user(
    user_id: int = Path(
        ..., 
        description="ID do usuário",
        gt=0,
        example=1
    ),
    db: Session = Depends(get_db),
    _: dict = Depends(check_admin_access)
):
    logger.info(f"Tentativa de excluir usuário {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.info(f"Tentativa de excluir usuário inexistente: {user_id}")
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
            internal_code="USER_NOT_FOUND"
        )
    
    try:
        db.delete(user)
        db.commit()
        logger.info(f"Usuário {user_id} excluído com sucesso")
        return {"message": "Usuário excluído com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao excluir usuário {user_id}: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir usuário",
            internal_code="USER_DELETION_ERROR"
        )

@v1_router.put("/acordaos/{acordao_id}/feedback",
               description="Atualizar feedback do acórdão",
               tags=["Ementas"])
async def update_acordao_feedback(
    acordao_id: int = Path(
        ..., 
        description="ID do acórdão",
        gt=0,
        example=1
    ),
    feedback: str = Query(
        ...,
        description="Feedback sobre a ementa gerada",
        min_length=1,
        max_length=1000,
        example="Ementa gerada com sucesso e adequada ao conteúdo"
    ),
    db: Session = Depends(get_db),
    _: dict = Depends(check_admin_access)
):
    logger.info(f"Atualizando feedback do acórdão {acordao_id}")
    try:
        acordao = db.query(Acordao).filter(Acordao.id == acordao_id).first()
        if not acordao:
            logger.info(f"Acórdão não encontrado para atualização: {acordao_id}")
            raise APIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Acórdão não encontrado",
                internal_code="ACORDAO_NOT_FOUND"
            )
        
        acordao.feedback = feedback
        db.commit()
        db.refresh(acordao)
        logger.info(f"Feedback atualizado com sucesso para acórdão {acordao_id}")
        return acordao
    except Exception as e:
        logger.error(f"Erro ao atualizar feedback do acórdão {acordao_id}: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar feedback do acórdão",
            internal_code="ACORDAO_FEEDBACK_UPDATE_ERROR"
        )

@v1_router.delete("/acordaos/{acordao_id}",
                  description="Excluir acórdão",
                  tags=["Ementas"])
async def delete_acordao(
    acordao_id: int = Path(
        ..., 
        description="ID do acórdão",
        gt=0,
        example=1
    ),
    db: Session = Depends(get_db),
    _: dict = Depends(check_admin_access)
):
    logger.info(f"Tentativa de excluir acórdão {acordao_id}")
    try:
        acordao = db.query(Acordao).filter(Acordao.id == acordao_id).first()
        if not acordao:
            logger.info(f"Tentativa de excluir acórdão inexistente: {acordao_id}")
            raise APIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Acórdão não encontrado",
                internal_code="ACORDAO_NOT_FOUND"
            )
        
        db.delete(acordao)
        db.commit()
        logger.info(f"Acórdão {acordao_id} excluído com sucesso")
        return {"message": "Acórdão excluído com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao excluir acórdão {acordao_id}: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir acórdão",
            internal_code="ACORDAO_DELETION_ERROR"
        )

@v1_router.get("/logs", 
               description="Listar logs do sistema",
               tags=["Sistema"])
async def list_logs(
    db: Session = Depends(get_log_db),
    _: dict = Depends(check_admin_access),
    skip: int = Query(
        default=0,
        ge=0,
        description="Número de registros para pular",
        example=0
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Número máximo de registros a retornar",
        example=10
    ),
    level: str = Query(
        default=None,
        description="Filtrar por nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        regex=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)?$",
        example="ERROR"
    ),
    start_date: str = Query(
        default=None,
        description="Filtrar logs a partir desta data (formato: YYYY-MM-DD)",
        regex=r"^\d{4}-\d{2}-\d{2}$",
        example="2024-01-01"
    )
):
    logger.debug(f"Listando logs: skip={skip}, limit={limit}, level={level}, start_date={start_date}")
    logger.info("Listando logs do sistema")
    try:
        query = db.query(LogEntry).order_by(LogEntry.id.desc())
        
        if level:
            query = query.filter(LogEntry.level == level)
        if start_date:
            query = query.filter(LogEntry.timestamp >= f"{start_date} 00:00:00")
            
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "items": logs,
            "skip": skip,
            "limit": limit,
            "filters": {
                "level": level,
                "start_date": start_date
            }
        }
    except Exception as e:
        logger.error(f"Erro ao listar logs: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao recuperar logs do sistema",
            internal_code="LOG_RETRIEVAL_ERROR"
        )

@v1_router.get("/acordaos",
               description="Listar todos os acórdãos",
               tags=["Ementas"])
async def list_acordaos(
    db: Session = Depends(get_db),
    _: dict = Depends(check_user_access),
    skip: int = Query(
        default=0,
        ge=0,
        description="Número de registros para pular",
        example=0
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Número máximo de registros a retornar",
        example=10
    ),
    has_feedback: bool = Query(
        default=None,
        description="Filtrar por acórdãos com/sem feedback",
        example=True
    )
):
    logger.debug(f"Listando acórdãos: skip={skip}, limit={limit}, has_feedback={has_feedback}")
    try:
        query = db.query(Acordao)
        
        if has_feedback is not None:
            if has_feedback:
                query = query.filter(Acordao.feedback.isnot(None))
            else:
                query = query.filter(Acordao.feedback.is_(None))
            
        total = query.count()
        acordaos = query.order_by(Acordao.id.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "items": acordaos,
            "skip": skip,
            "limit": limit,
            "filters": {
                "has_feedback": has_feedback
            }
        }
    except Exception as e:
        logger.error(f"Erro ao listar acórdãos: {str(e)}")
        raise APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao recuperar acórdãos",
            internal_code="ACORDAO_RETRIEVAL_ERROR"
        )

# Customize OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Update security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your bearer token in the format: Bearer <token>"
        }
    }
    
    # Add security requirement to all endpoints
    if "paths" in openapi_schema:
        for path in openapi_schema["paths"].values():
            for operation in path.values():
                operation["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", include_in_schema=False)
async def root():
    """
    Redirect root path to API documentation
    """
    return RedirectResponse(url="/docs")

app.include_router(v1_router)
app.include_router(v2_router)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health",
         description="Verificar status da API",
         tags=["Sistema"])
async def health_check():
    return {
        "status": "healthy",
        "database": check_database_connection(),
        "version": "1.0.0"
    }

def check_database_connection():
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return "connected"
    except Exception:
        return "disconnected"

# Add error handling middleware
@app.middleware("http")
async def error_handling_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"}
        )
