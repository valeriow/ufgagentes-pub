# API de Geração de Ementas de Acórdãos

API REST para geração automática de ementas de acórdãos usando IA, desenvolvida com FastAPI e SQLite.

## Funcionalidades

- Geração de ementas a partir de texto de acórdãos
- Geração de ementas a partir de arquivos PDF
- Autenticação e autorização via JWT
- Gerenciamento de usuários (admin/user roles) 
- Logs do sistema
- Documentação OpenAPI (Swagger)

## Requisitos

- Python 3.10+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```sh
git clone [url-do-repositorio]
cd [nome-do-diretorio]
```

2. Crie e ative um ambiente virtual:
```sh
# Linux/MacOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Instale as dependências:
```sh
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Crie um arquivo `.env` na raiz do projeto
- Adicione suas variáveis conforme o exemplo em `.env.sample`

## Configuração

Ajuste as configurações no arquivo `settings.py`:

- `DATABASE_URL`: URL de conexão com o banco SQLite  
- `SECRET_KEY`: Chave secreta para JWT
- `MODEL_NAME`: Nome do modelo LLM a ser usado
- `LOG_LEVEL`: Nível de logging desejado

## Uso

1. Inicie o servidor com :

Para desenvolvimento:
```sh
fastapi dev main.py
```
ou

Para produção:
```sh
uvicorn main:app --reload
```

2. Acesse a documentação da API:
- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Autenticação

- `POST /auth/login` - Fazer login e obter token JWT
- `POST /auth/refresh` - Renovar token JWT
- `GET /auth/status` - Verificar status da autenticação

### Usuários

- `POST /users/` - Criar novo usuário
- `GET /users/me` - Obter dados do usuário atual
- `GET /users/{id}` - Obter usuário por ID
- `PUT /users/{id}` - Atualizar usuário
- `DELETE /users/{id}` - Deletar usuário
- `GET /users/` - Listar todos usuários (admin)

### Ementas

- `POST /ementas/text` - Gerar ementa a partir de texto
- `POST /ementas/pdf` - Gerar ementa a partir de PDF
- `GET /ementas/{id}` - Obter ementa por ID
- `GET /ementas/` - Listar todas ementas
- `DELETE /ementas/{id}` - Deletar ementa
- `PUT /ementas/{id}` - Atualizar ementa

### Sistema

- `GET /health` - Verificar status do sistema
- `GET /metrics` - Obter métricas do sistema (admin)
- `GET /logs` - Consultar logs do sistema (admin)

## Logging

Os logs do sistema são armazenados em:
- Arquivo de log rotativo
- Banco SQLite dedicado para logs

## Segurança

- Autenticação via JWT
- Roles: admin e user  
- Rate limiting por IP
- CORS configurável
- Sanitização de inputs
- Validação de schema

## Testes

Execute os testes:
```sh
pytest tests/
```

## Deploy

### Docker (em desenvolvimento!)

#### Preparação do Ambiente

1. Certifique-se de ter o Docker instalado:
```sh
docker --version
```

2. Crie um arquivo `.env` para as variáveis de ambiente:
```sh
# Production Environment Variables
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secure-secret-key
MODEL_NAME=gpt-4o-mini
LOG_LEVEL=INFO
```

#### Construção e Execução com Docker

1. Construa a imagem Docker:
```sh
# Versão básica
docker build -t ementa-api .

# Com tag de versão
docker build -t ementa-api:1.0.0 .
```

2. Execute o container:
```sh
# Modo básico
docker run -d \
  --name ementa-api \
  -p 8000:8000 \
  --env-file .env \
  ementa-api

# Com persistência de dados
docker run -d \
  --name ementa-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ementa-api
```

#### Gerenciamento do Container

```sh
# Verificar status
docker ps -a | grep ementa-api

# Logs em tempo real
docker logs -f ementa-api

# Reiniciar container
docker restart ementa-api

# Parar container
docker stop ementa-api

# Remover container
docker rm ementa-api

# Remover imagem
docker rmi ementa-api
```

#### Atualização

1. Pare e remova o container atual:
```sh
docker stop ementa-api
docker rm ementa-api
```

2. Reconstrua a imagem com as alterações:
```sh
docker build -t ementa-api .
```

3. Inicie um novo container:
```sh
docker run -d \
  --name ementa-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ementa-api
```

#### Dicas de Produção

- Use um registry privado para armazenar suas imagens
- Implemente health checks
- Configure limites de recursos (CPU/memória)
- Use redes Docker dedicadas
- Faça backup regular dos dados
- Monitore logs e métricas

### Produção
- Use HTTPS
- Configure firewall  
- Monitore logs
- Configure backup do banco

## Contribuição

1. Fork o projeto
2. Crie sua feature branch
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## Contato

- Nome: Valério Wittler
- Email: valeriow@gmail.com

## Roadmap

- [ ] Suporte a mais formatos de entrada
- [ ] Pipeline CI/CD
- [ ] Interface web administrativa  
- [ ] Métricas e dashboards
- [ ] Clustering e alta disponibilidade
