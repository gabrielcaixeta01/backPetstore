# Guia de Deploy — TrilhaApex (do zero)

> Stack: **FastAPI** no Render · **PostgreSQL** no Render · **React/Vite** no Vercel

---

## Visão geral da arquitetura

```
Vercel (frontend)                   Render (backend + banco)
https://<projeto>.vercel.app   ──►  https://trilhaapex.onrender.com
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
   | Name | `apex-db` |
   | Database | `apex_db` |
   | User | `apex_user` |
   | Region | `Ohio (US East)` |
   | PostgreSQL Version | **18** |
   | Plan | **Free** |

3. Clique em **Create Database** e aguarde (~1 min)
4. Na página do banco, copie a **Internal Database URL**:
   ```
   postgresql://apex_user:SENHA@dpg-XXXXX-a/apex_db
   ```
   > Use sempre a **Internal URL** — ela é mais rápida e não consome cota de rede externa.

---

## Passo 2 — Criar o Web Service (backend) no Render

1. **Render Dashboard → New → Web Service**
2. Conecte o repositório `TrilhaApex`
3. Configure:

   | Campo | Valor |
   |-------|-------|
   | Name | `trilhaapex` ← mantenha esse nome para a URL não mudar |
   | Region | Mesma do banco |
   | Branch | `main` |
   | Runtime | **Docker** (detectado automaticamente pelo `Dockerfile`) |
   | Plan | **Free** |

4. Na seção **Environment Variables**, adicione **todas** as variáveis abaixo:

   | Variável | Valor |
   |----------|-------|
   | `DATABASE_URL` | Internal Database URL do Passo 1 |
   | `JWT_SECRET_KEY` | Gere com o comando abaixo |
   | `JWT_ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
   | `SUPERUSER_EMAIL` | `admin@apexbrasil.com` |
   | `SUPERUSER_PASSWORD` | `Admin@2024` |
   | `EMPLOYEE_DEFAULT_PASSWORD` | `Apex@2024` |
   | `CLIENT_DEFAULT_PASSWORD` | `Cliente@2024` |
   | `CORS_ORIGINS` | URL completa do seu frontend no Vercel |

   **Gerar JWT_SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   > **Atenção:** `CORS_ORIGINS` deve conter a URL exata do Vercel **sem** barra final.
   > Exemplo: `https://front-apex-delta.vercel.app`
   > Se a URL do Vercel mudar, atualize apenas esta variável — sem precisar alterar o código.

5. Clique em **Create Web Service** e aguarde o build (~3-5 min)
6. Quando aparecer `Live`, teste: `https://trilhaapex.onrender.com/docs`

> O `Dockerfile` executa `alembic upgrade head` automaticamente antes de subir o servidor.
> O seed roda no primeiro startup e popula lojas, funcionários, serviços, clientes, pets e atendimentos.

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

5. Clique em **Deploy** e aguarde (~1 min)
6. Copie a URL gerada (ex: `https://front-apex-delta.vercel.app`) e coloque em `CORS_ORIGINS` no Render (Passo 2)
7. Salve as env vars no Render → o serviço reinicia automaticamente

---

## Dados populados pelo seed

### Lojas

| Nome | CNPJ | Cidade |
|------|------|--------|
| Apex Petstore Centro | 11.111.111/0001-11 | São Paulo – SP |
| Apex Petstore Norte | 22.222.222/0001-22 | São Paulo – SP |
| Apex Petstore Asa Sul | 33.333.333/0001-33 | Brasília – DF |
| Apex Petstore Asa Norte | 44.444.444/0001-44 | Brasília – DF |
| Apex Petstore Plano Piloto | 55.555.555/0001-55 | Brasília – DF |

### Serviços

| Serviço | Preço |
|---------|-------|
| Banho | R$ 50,00 |
| Tosa | R$ 80,00 |
| Banho e Tosa | R$ 120,00 |
| Vacinação | R$ 90,00 |
| Adestramento | R$ 150,00 |
| Consulta Veterinária | R$ 200,00 |
| Pet Hotel (diária) | R$ 80,00 |
| Hidratação | R$ 60,00 |

### Credenciais — Administrador e Funcionários

Senha padrão dos funcionários: **`Apex@2024`** (ou o valor de `EMPLOYEE_DEFAULT_PASSWORD`)

| Nome | Email | Cargo | Loja |
|------|-------|-------|------|
| Administrador | `admin@apexbrasil.com` | Administrador do Sistema | Centro |
| Carlos Mendes | `carlos.mendes@apexbrasil.com` | Veterinário | Centro |
| Ana Lima | `ana.lima@apexbrasil.com` | Tosadora | Centro |
| Pedro Souza | `pedro.souza@apexbrasil.com` | Atendente | Norte |
| Julia Costa | `julia.costa@apexbrasil.com` | Veterinária | Norte |
| Bruna Almeida | `bruna.almeida@apexbrasil.com` | Veterinária | Asa Sul |
| Rafael Lima | `rafael.lima@apexbrasil.com` | Tosador | Asa Sul |
| Marcos Andrade | `marcos.andrade@apexbrasil.com` | Veterinário | Asa Norte |
| Patrícia Gomes | `patricia.gomes@apexbrasil.com` | Atendente | Asa Norte |
| Fernanda Vieira | `fernanda.vieira@apexbrasil.com` | Tosadora | Plano Piloto |
| Diego Carvalho | `diego.carvalho@apexbrasil.com` | Atendente | Plano Piloto |

### Credenciais — Clientes

Senha padrão dos clientes: **`Cliente@2024`** (ou o valor de `CLIENT_DEFAULT_PASSWORD`)

| Nome | Email | Pet |
|------|-------|-----|
| Maria Silva | `maria.silva@email.com` | Thor (Labrador, macho) |
| João Oliveira | `joao.oliveira@email.com` | Mia (Siamês, fêmea) |
| Ana Pereira | `ana.pereira@email.com` | Bob (Golden Retriever, macho) |
| Lucas Santos | `lucas.santos@email.com` | Nemo (Peixe-palhaço, macho) |
| Camila Fernandes | `camila.fernandes@email.com` | Mel (Yorkshire, fêmea) |

---

## Referência de variáveis de ambiente

### Backend — Render Web Service

| Variável | Obrigatória | Descrição |
|----------|:-----------:|-----------|
| `DATABASE_URL` | ✅ | Internal Database URL do PostgreSQL no Render |
| `JWT_SECRET_KEY` | ✅ | Chave secreta para assinar tokens JWT |
| `JWT_ALGORITHM` | ✅ | Algoritmo de assinatura (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Expiração do token em minutos |
| `CORS_ORIGINS` | ✅ | URL exata do frontend no Vercel (sem barra final) |
| `SUPERUSER_EMAIL` | ✅ | Email do admin criado pelo seed |
| `SUPERUSER_PASSWORD` | ✅ | Senha do admin (sem ela o admin não é criado) |
| `EMPLOYEE_DEFAULT_PASSWORD` | ❌ | Senha padrão dos funcionários seed (default: `Apex@2024`) |
| `CLIENT_DEFAULT_PASSWORD` | ❌ | Senha padrão dos clientes seed (default: `Cliente@2024`) |

### Frontend — Vercel

| Variável | Obrigatória | Valor |
|----------|:-----------:|-------|
| `VITE_API_URL` | ✅ | `https://trilhaapex.onrender.com` |

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
- Verifique se `CORS_ORIGINS` no Render tem a URL exata do Vercel (sem barra final, sem aspas)
- Após salvar a env var, aguarde o Render reiniciar (~30s) antes de testar novamente
- Confirme nos logs do Render: busque `CORS allowed origins` para ver a lista ativa

### Seed não criou o admin / clientes / pets
- Confirme que `SUPERUSER_PASSWORD` está definida no Render
- Veja os logs do Render por linhas `seed: ... criado` ou `seed: erro`

### Render "Service unavailable"
- O free tier hiberna após 15 min de inatividade — o primeiro request demora ~30-60s para "acordar"
- Se permanecer unavailable, verifique se `DATABASE_URL` usa a **Internal URL** correta

### Frontend chama URL errada em produção
- Confirme que `VITE_API_URL` está nas **Environment Variables** do Vercel
- Após alterar env vars no Vercel: **Deployments → Redeploy** para rebuild com os novos valores
