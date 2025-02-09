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

1. Inicie o servidor:
```sh
uvicorn main:app --reload
```

2. Acesse a documentação da API:
- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Autenticação

- `POST /auth/token` - Obter token JWT
- `POST /auth/refresh` - Renovar token JWT

### Usuários

- `POST /users/` - Criar usuário
- `GET /users/me` - Obter dados do usuário atual  
- `PUT /users/{id}` - Atualizar usuário
- `DELETE /users/{id}` - Deletar usuário

### Ementas

- `POST /ementas/text` - Gerar ementa a partir de texto
- `POST /ementas/pdf` - Gerar ementa a partir de PDF
- `GET /ementas/{id}` - Obter ementa por ID
- `GET /ementas/` - Listar ementas geradas

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

### Docker
```sh
docker build -t ementa-api .
docker run -p 8000:8000 ementa-api
```

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
