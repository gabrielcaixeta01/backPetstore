# Guia de Deploy — PetStore da ApexBrasil

## Render (Backend)

### Como configurar
Dashboard → backPetstore → Environment → Add Environment Variable

| Variável | Valor |
|---|---|
| `DATABASE_URL` | Copiar de: petstore-db → Info → **External Database URL** |
| `JWT_SECRET_KEY` | Gerar com: `openssl rand -hex 32` |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `CORS_ORIGINS` | URL do frontend no Vercel (ex: `https://front-petstore.vercel.app`) |
| `SUPERUSER_EMAIL` | `admin@petstore.com` (ou o que preferir) |
| `SUPERUSER_PASSWORD` | `Admin@2026` |
| `EMPLOYEE_DEFAULT_PASSWORD` | `Petstore@2026` |

### Atenção com DATABASE_URL
O Render fornece a URL no formato `postgres://...` ou `postgresql://...`.
O `database.py` já converte automaticamente para `postgresql+psycopg://`, então
basta colar a URL como está — não precisa editar manualmente.

### Configuração do serviço no Render
- **Environment**: Docker
- **Root Directory**: deixar em branco (Dockerfile está na raiz)
- **Branch**: main

O Render vai usar o `Dockerfile` para buildar e o `CMD` do Dockerfile para subir.
O `docker-compose.yml` é só para dev local — o Render **não usa** o compose.

---

## Vercel (Frontend)

### Como configurar
Dashboard → frontPetstore → Settings → Environment Variables

| Variável | Valor |
|---|---|
| `VITE_BACKEND_URL` | URL do backend no Render (ex: `https://backpetstore.onrender.com`) |

### Atenção
A URL do Render **não tem barra no final**:
- ✅ `https://backpetstore.onrender.com`
- ❌ `https://backpetstore.onrender.com/`

### Build settings (Vercel)
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

---

## CORS: conectando front e back

Após o deploy do frontend, copie a URL do Vercel e adicione em `CORS_ORIGINS` no Render.
Se tiver múltiplas URLs (ex: preview + produção), separe por vírgula:

```
CORS_ORIGINS=https://front-petstore.vercel.app,https://front-petstore-git-main.vercel.app
```

---

## Ordem de deploy recomendada

1. **Render** → criar o serviço do backend (já vai ter a URL)
2. **Vercel** → criar o serviço do frontend com `VITE_BACKEND_URL` apontando pro Render
3. **Render** → adicionar `CORS_ORIGINS` com a URL do Vercel e fazer redeploy

---

## Dev local (.env na raiz do backPetstore)

```env
POSTGRES_DB=petstore_db
POSTGRES_USER=petstore_user
POSTGRES_PASSWORD=petstore_pass
JWT_SECRET_KEY=qualquer-coisa-para-dev
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=
SUPERUSER_EMAIL=admin@petstore.com
SUPERUSER_PASSWORD=Admin@2026
EMPLOYEE_DEFAULT_PASSWORD=Petstore@2026
```

Subir localmente: `docker compose up --build`