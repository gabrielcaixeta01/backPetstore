# Guia de Deploy — TrilhaApex (do zero)

> Stack: **FastAPI** no Render · **PostgreSQL** no Render · **React/Vite** no Vercel

---

## Visão geral da arquitetura

```
Vercel (frontend)                   Render (backend + banco)
apexbrasilpetstore.vercel.app  ──►  trilhaapex.onrender.com
                                          │
                                    PostgreSQL (Render)
```

---

## Pré-requisitos

- Conta no [Render](https://render.com) (free tier é suficiente)
- Conta no [Vercel](https://vercel.com) (free tier)
- Repositórios no GitHub:
  - Backend: `TrilhaApex`
  - Frontend: `frontApex`

---

## Passo 1 — Criar o banco PostgreSQL no Render

1. Acesse **Render Dashboard → New → PostgreSQL**
2. Preencha:
   | Campo | Valor |
   |-------|-------|
   | Name | `apex-db` (ou qualquer nome) |
   | Database | `apex_db` |
   | User | `apex_user` |
   | Region | `Ohio (US East)` ou o mais próximo |
   | PostgreSQL Version | **18** |
   | Plan | **Free** |
3. Clique em **Create Database**
4. Aguarde o banco subir (~1 min)
5. Na página do banco, copie a **Internal Database URL** — ela tem o formato:
   ```
   postgresql://apex_user:SENHA_GERADA@dpg-XXXXX-a/apex_db
   ```
   Guarde essa URL, será usada no próximo passo.

> **Importante:** use a **Internal URL** (não a External URL) para comunicação entre serviços no Render — é mais rápida e não consome a cota de rede externa.

---

## Passo 2 — Criar o Web Service (backend) no Render

1. **Render Dashboard → New → Web Service**
2. Conecte o repositório `TrilhaApex`
3. Configure:
   | Campo | Valor |
   |-------|-------|
   | Name | `trilhaapex` ← **mantenha esse nome** para a URL não mudar |
   | Region | Mesma do banco |
   | Branch | `main` |
   | Runtime | **Docker** (o Render detecta o `Dockerfile` automaticamente) |
   | Plan | **Free** |

4. Na seção **Environment Variables**, adicione **todas** as variáveis abaixo:

   | Variável | Valor |
   |----------|-------|
   | `DATABASE_URL` | Cole a **Internal Database URL** do Passo 1 |
   | `JWT_SECRET_KEY` | Gere uma chave forte (veja comando abaixo) |
   | `JWT_ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
   | `SUPERUSER_EMAIL` | `admin@apexbrasil.com` |
   | `SUPERUSER_PASSWORD` | `Admin@2024` (ou outra senha segura) |
   | `EMPLOYEE_DEFAULT_PASSWORD` | `Apex@2024` |
   | `CORS_ORIGINS` | URL completa do seu frontend no Vercel (ex: `https://front-apex-delta.vercel.app`) |

   **Gerar JWT_SECRET_KEY** (rode no terminal):
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Clique em **Create Web Service**
6. Aguarde o build e o deploy (~3-5 min na primeira vez)
7. Quando aparecer `Live`, teste: `https://trilhaapex.onrender.com/docs`

> O `Dockerfile` já executa `alembic upgrade head` antes de subir o servidor — as tabelas são criadas automaticamente. O seed roda na primeira inicialização e cria lojas, categorias, tags e usuários padrão.

---

## Passo 3 — Deploy do frontend no Vercel

1. **Vercel Dashboard → Add New → Project**
2. Importe o repositório `frontApex`
3. Configure:
   | Campo | Valor |
   |-------|-------|
   | Framework Preset | **Vite** |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |

4. Na seção **Environment Variables**, adicione:

   | Variável | Valor |
   |----------|-------|
   | `VITE_API_URL` | `https://trilhaapex.onrender.com` |

   > Isso substitui (com prioridade) qualquer valor do arquivo `.env.production` commitado no repositório. Se o nome do serviço Render mudar, atualize **só aqui**, sem precisar commitar código.

5. Clique em **Deploy**
6. Aguarde o build (~1 min)
7. Acesse `https://apexbrasilpetstore.vercel.app` e teste o login

---

## Credenciais padrão (criadas pelo seed)

| Usuário | Email | Senha | Perfil |
|---------|-------|-------|--------|
| Administrador | `admin@apexbrasil.com` | `Admin@2024` | superuser |
| Carlos Mendes | `carlos.mendes@apexbrasil.com` | `Apex@2024` | funcionário |
| Ana Lima | `ana.lima@apexbrasil.com` | `Apex@2024` | funcionário |
| Pedro Souza | `pedro.souza@apexbrasil.com` | `Apex@2024` | funcionário |
| Julia Costa | `julia.costa@apexbrasil.com` | `Apex@2024` | funcionário |

---

## Referência de variáveis de ambiente

### Backend — Render Web Service

| Variável | Obrigatória | Descrição | Exemplo |
|----------|:-----------:|-----------|---------|
| `DATABASE_URL` | ✅ | URL de conexão PostgreSQL (Internal do Render) | `postgresql://user:pass@host/db` |
| `JWT_SECRET_KEY` | ✅ | Chave secreta para assinar tokens JWT | `60a1bb6e0cbc9...` |
| `JWT_ALGORITHM` | ✅ | Algoritmo de assinatura | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Tempo de expiração do token em minutos | `60` |
| `SUPERUSER_EMAIL` | ✅ | Email do admin criado no seed | `admin@apexbrasil.com` |
| `SUPERUSER_PASSWORD` | ✅ | Senha do admin (sem essa var, admin não é criado) | `Admin@2024` |
| `EMPLOYEE_DEFAULT_PASSWORD` | ❌ | Senha padrão dos funcionários seed | `Apex@2024` |
| `CORS_ORIGINS` | ✅ | URL do frontend no Vercel (separadas por vírgula se houver mais de uma) | `https://seu-projeto.vercel.app` |

### Frontend — Vercel

| Variável | Obrigatória | Descrição | Valor produção |
|----------|:-----------:|-----------|----------------|
| `VITE_API_URL` | ✅ | URL base do backend | `https://trilhaapex.onrender.com` |

---

## Desenvolvimento local (Docker Compose)

```bash
# Na raiz do TrilhaApex
docker compose up --build
```

A API sobe em `http://localhost:8000`. Para o frontend:

```bash
# Na raiz do frontApex
npm install
npm run dev
```

O Vite faz proxy de `/api/*` para `http://127.0.0.1:8000` — nenhuma configuração extra necessária.

---

## Troubleshooting

### "No 'Access-Control-Allow-Origin' header"
- Confirme que o Web Service no Render está com status **Live** (não crashed)
- Verifique os logs do Render — se o seed ou a conexão com o banco falharem no startup, a API não sobe
- A URL `https://apexbrasilpetstore.vercel.app` já está hardcoded no backend, então CORS não precisa de configuração extra

### Seed não criou o admin
- Confirme que `SUPERUSER_PASSWORD` está definida no Render (sem ela o admin é pulado)
- Veja os logs do Render por linhas `seed: superuser criado` ou `seed: erro`

### Render "Service unavailable"
- O free tier hiberna após 15 min de inatividade — o primeiro request demora ~30s para "acordar"
- Se permanecer unavailable, verifique se `DATABASE_URL` usa a **Internal URL** correta

### Frontend chama URL errada em produção
- Confirme que a variável `VITE_API_URL` está definida nas **Environment Variables** do Vercel (não apenas no arquivo `.env.production`)
- Após alterar env vars no Vercel, faça um **Redeploy** manual (Deployments → Redeploy)
