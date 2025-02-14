import os
from dotenv import load_dotenv


# Carregar variáveis de ambiente
load_dotenv()


# API Settings
API_TITLE = "API de Geração de Ementas de Acórdãos"
API_VERSION = "v1"

# Security Settings
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta")
INSTALL_KEY = os.getenv("INSTALL_KEY", "chave-secreta-instalacao")

# Database Settings
DATABASE_URL = "sqlite:///ementas.db"
LOG_DATABASE_URL = "sqlite:///log.db"

# Model Settings
MODEL_NAME = os.getenv("LITELLM_MODEL", "gpt-4o-mini")

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Security Settings
TOKEN_EXPIRE_HOURS = 1
