# Deploy no Render

## Pré-requisitos

- Conta em [render.com](https://render.com)
- Repositório no GitHub (já conectado ao Render)

---

## 1. Criar o banco PostgreSQL

1. No dashboard do Render → **New → PostgreSQL**
2. Preencha:
   - **Name**: `apex-db` (ou qualquer nome)
   - **Region**: a mais próxima de você
   - **Plan**: Free (90 dias grátis) ou pago
3. Clique em **Create Database**
4. Aguarde ficar `Available` e copie a **Internal Database URL** — você vai usar no próximo passo

> Use a *Internal* URL quando a API e o banco estiverem no mesmo ambiente Render.  
> Use a *External* URL apenas para acessar de fora (ex: DBeaver local).

---

## 2. Criar o Web Service (API)

1. No dashboard → **New → Web Service**
2. Conecte o repositório do projeto
3. Configure:

| Campo | Valor |
|-------|-------|
| **Name** | `apex-api` |
| **Region** | mesma do banco |
| **Branch** | `main` |
| **Runtime** | **Docker** |
| **Instance Type** | Free ou pago |

4. Clique em **Advanced** → **Add Environment Variable** e adicione:

| Variável | Valor |
|----------|-------|
| `DATABASE_URL` | Internal Database URL copiada no passo 1 |
| `JWT_SECRET_KEY` | uma chave forte (gere com `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `CORS_ORIGINS` | URL do seu frontend (ex: `https://apexbrasilpetstore.vercel.app`) |

5. Clique em **Create Web Service**

---

## 3. Migrations

As migrations rodam **automaticamente** a cada deploy — o Dockerfile executa `alembic upgrade head` antes de iniciar a API.

Para criar uma nova migration após alterar os modelos:

```bash
alembic revision --autogenerate -m "descricao da mudanca"
```

Commit o arquivo gerado em `alembic/versions/` e faça push — o próximo deploy aplica automaticamente.

---

## 4. Verificar o deploy

- Acompanhe os logs na aba **Logs** do serviço
- A API estará disponível em `https://<nome-do-servico>.onrender.com`
- Acesse `/docs` para confirmar que o Swagger está funcionando

---

## Redeploy manual

Qualquer push na branch `main` dispara deploy automático.  
Para forçar manualmente: **Manual Deploy → Deploy latest commit** no painel do serviço.

---

## Variáveis de ambiente — referência completa

```env
DATABASE_URL=postgresql://user:pass@host/dbname   # fornecida pelo Render
JWT_SECRET_KEY=<chave-gerada>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://seu-frontend.vercel.app
```

> O `database.py` converte automaticamente `postgresql://` para o formato do psycopg3 — não precisa ajustar a URL manualmente.


---

## Variáveis para o Render

SUPERUSER_EMAIL=admin@apexbrasil.com
SUPERUSER_PASSWORD=<senha-forte>
EMPLOYEE_DEFAULT_PASSWORD=<senha-para-funcionarios>
