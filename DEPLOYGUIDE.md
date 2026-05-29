# 🚀 Guia de Deploy — Petstore ApexBrasil

Stack: **Vite (front)** · **FastAPI + Docker (back)** · **PostgreSQL (Railway)** · **Vercel (front)** · **Railway (back + banco)**

---

## Visão Geral da Arquitetura

```
┌─────────────┐        HTTPS         ┌──────────────────────────┐
│   Vercel    │  ──────────────────▶  │   Railway (FastAPI)      │
│  (Vite SPA) │                       │   + PostgreSQL           │
└─────────────┘                       └──────────────────────────┘
```

---

## Pré-requisitos

- [ ] Conta no [GitHub](https://github.com)
- [ ] Conta no [Vercel](https://vercel.com) (login com GitHub)
- [ ] Conta no [Railway](https://railway.app) (login com GitHub)
- [ ] Docker Desktop instalado localmente
- [ ] Python 3.11+ e pip

---

## Parte 1 — Migração do Banco: SQLite → PostgreSQL

### 1.1 Instalar dependências

```bash
pip install asyncpg psycopg2-binary sqlalchemy alembic
```

### 1.2 Atualizar a string de conexão

No seu projeto FastAPI, localize onde o banco é configurado (geralmente `database.py` ou similar) e substitua a conexão SQLite pela PostgreSQL:

```python
# Antes (SQLite)
DATABASE_URL = "sqlite:///./petstore.db"

# Depois (PostgreSQL)
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/petstore")
```

> ⚠️ **Nunca hardcode credenciais.** Use sempre variáveis de ambiente.

### 1.3 Ajustar o engine do SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### 1.4 Configurar Alembic para migrations

```bash
alembic init alembic
```

No arquivo `alembic/env.py`, atualize para usar sua `Base` e `DATABASE_URL`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import Base  # ajuste o import conforme seu projeto
import models  # garante que todos os models sejam carregados

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata
```

Gerar a primeira migration:

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

---

## Parte 2 — Dockerfile para o FastAPI

Crie o arquivo `Dockerfile` na raiz do projeto back-end:

```dockerfile
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Roda as migrations e inicia o servidor
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

> 💡 Substitua `main:app` pelo caminho correto do seu arquivo principal FastAPI (ex: `app.main:app`).

### 2.1 Arquivo .dockerignore

Crie `.dockerignore` na raiz do back-end:

```
__pycache__
*.pyc
*.pyo
.env
.venv
venv/
*.db
.git
.gitignore
```

### 2.2 Testar localmente com Docker

```bash
# Build da imagem
docker build -t petstore-api .

# Rodar localmente (para testar, usando um PostgreSQL local ou Docker)
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host.docker.internal:5432/petstore" \
  petstore-api
```

---

## Parte 3 — Docker Compose (desenvolvimento local)

Crie `docker-compose.yml` na raiz do projeto para facilitar o desenvolvimento:

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: petstore
      POSTGRES_PASSWORD: petstore
      POSTGRES_DB: petstore
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./backend   # ajuste para o caminho do seu back-end
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://petstore:petstore@db:5432/petstore
    depends_on:
      - db

volumes:
  postgres_data:
```

Rodar:

```bash
docker compose up --build
```

---

## Parte 4 — Deploy do Back-end no Railway

### 4.1 Criar conta e novo projeto

1. Acesse [railway.app](https://railway.app) e faça login com GitHub
2. Clique em **New Project**
3. Selecione **Deploy from GitHub repo**
4. Autorize o Railway e selecione o repositório do back-end

### 4.2 Adicionar o banco PostgreSQL

1. Dentro do projeto, clique em **+ New Service**
2. Selecione **Database → PostgreSQL**
3. O Railway cria o banco automaticamente e disponibiliza as variáveis de conexão

### 4.3 Configurar variáveis de ambiente

No painel do serviço FastAPI, vá em **Variables** e adicione:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

> O Railway injeta automaticamente `${{Postgres.DATABASE_URL}}` com a URL completa do banco que você criou.

### 4.4 Configurar o deploy via Dockerfile

1. No serviço FastAPI, vá em **Settings → Build**
2. Certifique-se que **Build Method** está como **Dockerfile**
3. Se o Dockerfile não estiver na raiz, ajuste o **Dockerfile Path**

### 4.5 Obter a URL pública do back-end

1. Vá em **Settings → Networking**
2. Clique em **Generate Domain**
3. Anote a URL gerada (ex: `https://petstore-api-production.up.railway.app`)

---

## Parte 5 — Deploy do Front-end na Vercel

### 5.1 Configurar variável de ambiente no Vite

No seu projeto front-end, crie um arquivo `.env.production`:

```
VITE_API_URL=https://petstore-api-production.up.railway.app
```

E use no código assim:

```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

### 5.2 Criar conta e importar projeto

1. Acesse [vercel.com](https://vercel.com) e faça login com GitHub
2. Clique em **Add New → Project**
3. Selecione o repositório do front-end
4. A Vercel detecta Vite automaticamente

### 5.3 Configurar variáveis de ambiente na Vercel

Antes de fazer o deploy, na tela de configuração:

1. Expanda **Environment Variables**
2. Adicione:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://sua-url.up.railway.app` (URL do Railway)

### 5.4 Deploy

Clique em **Deploy**. A Vercel vai:
1. Clonar o repositório
2. Rodar `vite build`
3. Publicar a pasta `/dist`

A URL final será algo como: `https://petstore-apexbrasil.vercel.app`

---

## Parte 6 — CORS no FastAPI

Para o front-end (Vercel) conseguir chamar o back-end (Railway), configure o CORS:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "https://petstore-apexbrasil.vercel.app",  # substitua pela sua URL real
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> 💡 Adicione `FRONTEND_URL` como variável de ambiente no Railway também.

---

## Parte 7 — Checklist Final

### Back-end (Railway)
- [ ] Dockerfile criado e testado localmente
- [ ] `requirements.txt` atualizado com `psycopg2-binary`, `alembic`, `uvicorn`
- [ ] Variável `DATABASE_URL` configurada no Railway
- [ ] Migrations rodando no startup (`alembic upgrade head` no CMD)
- [ ] CORS configurado com a URL do front-end
- [ ] URL pública gerada no Railway

### Front-end (Vercel)
- [ ] `VITE_API_URL` apontando para o Railway
- [ ] Variável adicionada nas configurações da Vercel
- [ ] Build passando sem erros

### Banco de dados
- [ ] PostgreSQL provisionado no Railway
- [ ] String de conexão usando variável de ambiente
- [ ] Migrations aplicadas com sucesso

---

## Referências

- [Documentação Railway](https://docs.railway.app)
- [Documentação Vercel + Vite](https://vitejs.dev/guide/static-deploy.html#vercel)
- [FastAPI com PostgreSQL](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Alembic — Migrations](https://alembic.sqlalchemy.org/en/latest/tutorial.html)