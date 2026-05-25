# Backend — TrilhaApex Petstore API

Sistema de gerenciamento de petshop construído com **FastAPI**, **SQLAlchemy** e autenticação via **JWT**. Permite cadastro de usuários (clientes e funcionários), pets, agendamentos de serviços e controle de lojas.

---

## Índice

- [Estrutura de pastas](#estrutura-de-pastas)
- [Tecnologias](#tecnologias)
- [Como rodar](#como-rodar)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Banco de dados — Modelos e relacionamentos](#banco-de-dados--modelos-e-relacionamentos)
- [Arquitetura em camadas](#arquitetura-em-camadas)
- [Autenticação e segurança](#autenticação-e-segurança)
- [Routers — Endpoints da API](#routers--endpoints-da-api)
  - [Auth](#auth-auth)
  - [User](#user-user)
  - [Pet](#pet-pet)
  - [Appointment](#appointment-appointment)
  - [Service](#service-service)
  - [Store](#store-store)
  - [Category](#category-category)
  - [Tag](#tag-tag)
- [Services — Regras de negócio](#services--regras-de-negócio)
- [Regras de autorização por perfil](#regras-de-autorização-por-perfil)

---

## Estrutura de pastas

```
TrilhaApex/
├── app/
│   ├── core/
│   │   └── security.py           # JWT, hashing de senha, dependências de auth
│   ├── routers/                  # Endpoints HTTP organizados por recurso
│   │   ├── auth_crud.py
│   │   ├── user_crud.py
│   │   ├── pet_crud.py
│   │   ├── appointment_crud.py
│   │   ├── service_crud.py
│   │   ├── store_crud.py
│   │   ├── category_crud.py
│   │   └── tag_crud.py
│   ├── schemas/
│   │   ├── models.py             # Modelos ORM (SQLAlchemy)
│   │   └── schemas.py            # Schemas de validação (Pydantic)
│   ├── services/                 # Lógica de negócio e acesso ao banco
│   │   ├── user_service.py
│   │   ├── pet_service.py
│   │   ├── appointment_service.py
│   │   ├── store_service.py
│   │   ├── service_service.py
│   │   ├── category_service.py
│   │   └── tag_service.py
│   ├── database.py               # Configuração da sessão do banco
│   └── main.py                   # Inicialização do app, CORS, routers
├── requirements.txt
└── petstore.db                   # Banco SQLite (desenvolvimento)
```

---

## Tecnologias

| Categoria | Biblioteca |
|-----------|-----------|
| Framework web | FastAPI 0.115+ |
| Servidor ASGI | Uvicorn 0.24+ |
| ORM | SQLAlchemy 2.0+ |
| Migrations | Alembic 1.14+ |
| Validação | Pydantic 2.10+ |
| Autenticação | python-jose (JWT), passlib[bcrypt] |
| Banco dev | SQLite |
| Banco prod | PostgreSQL (via psycopg) |
| Env vars | python-dotenv |
| Testes | pytest, httpx, requests |

---

## Como rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar em modo desenvolvimento
uvicorn app.main:app --reload

# Acessar a documentação interativa
# http://localhost:8000/docs
```

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `sqlite:///./petstore.db` | String de conexão com o banco |
| `JWT_SECRET_KEY` | `change-me-in-production` | Chave de assinatura dos tokens JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Validade do token em minutos |

---

## Banco de dados — Modelos e relacionamentos

### Diagrama de relacionamentos

```
users ──────────── clients ──────── pets ──────── pet_tags ──── tags
  │                   │               │
  └── employees        └── appointments ──── appointment_services ──── services
           │                   │
        stores ────────────────┘
```

### Tabelas

#### `users` — Conta base de qualquer usuário

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `name` | String(120) | Nome completo |
| `email` | String(255) unique | E-mail de login |
| `password_hash` | String(255) | Senha hasheada |
| `phone` | String(20) | Telefone |
| `profile_type` | String | `'cliente'` ou `'funcionario'` |
| `cpf` | String(14) | CPF (pessoa física) |
| `cnpj` | String(18) | CNPJ (pessoa jurídica) |
| `active` | Boolean | Se o usuário pode logar |
| `is_superuser` | Boolean | Acesso administrativo total |
| `created_at` | DateTime | Data de criação |

Cada usuário tem **um** perfil filho: `clients` ou `employees` (cascade delete).

---

#### `clients` — Perfil de cliente

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `user_id` | FK → users.id | Chave primária e estrangeira |
| `client_type` | String | `'pessoa_fisica'` ou `'pessoa_juridica'` |
| `cep` | String(9) | CEP |
| `state` | String(2) | UF |
| `city` | String(120) | Cidade |

Relacionamentos: possui muitos `pets` e muitos `appointments`.

---

#### `employees` — Perfil de funcionário

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `user_id` | FK → users.id | Chave primária e estrangeira |
| `employee_code` | String(20) unique | Código interno do funcionário |
| `job_title` | String(80) | Cargo |
| `salary` | Numeric(10,2) | Salário |
| `hired_at` | Date | Data de contratação |
| `store_id` | FK → stores.id | Loja onde trabalha |

Um funcionário pertence a **uma** loja e pode atender muitos agendamentos.

---

#### `stores` — Lojas do petshop

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `name` | String(120) | Nome da loja |
| `cnpj` | String(18) unique | CNPJ |
| `phone` | String(20) | Telefone |
| `email` | String(255) unique | E-mail |
| `cep` | String(9) | CEP |
| `city` | String(120) | Cidade |
| `state` | String(2) | UF |
| `street` | String(255) | Rua |
| `neighborhood` | String(120) | Bairro |
| `number` | String(20) | Número |
| `active` | Boolean | Loja ativa |
| `created_at` | DateTime | Data de criação |

---

#### `pets` — Animais dos clientes

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `name` | String(120) | Nome do pet |
| `breed` | String(80) | Raça |
| `sex` | String(20) | `'M'` ou `'F'` |
| `size` | String(20) | Tamanho (pequeno, médio, grande...) |
| `weight` | Numeric(6,2) | Peso em kg (deve ser > 0) |
| `health_notes` | String(500) | Observações de saúde |
| `category_id` | FK → categories.id | Espécie do pet |
| `owner_id` | FK → clients.user_id | Dono |

Relacionamentos: pertence a uma `category`, tem muitas `tags` (N:M via `pet_tags`), tem muitos `appointments`.

---

#### `categories` — Espécies / categorias de pets

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `name` | String(80) unique | Nome (ex: cachorro, gato) |
| `description` | String(255) | Descrição opcional |

Deletar uma categoria deleta em cascata todos os pets vinculados.

---

#### `tags` — Etiquetas descritivas dos pets

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `name` | String(80) unique | Nome da tag |
| `description` | String(255) | Descrição opcional |

Relacionamento N:M com `pets` via tabela `pet_tags`.

---

#### `services` — Serviços oferecidos pelo petshop

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `name` | String(120) | Nome do serviço (ex: banho, tosa) |
| `description` | String(500) | Descrição |
| `price` | Numeric(10,2) | Preço base (≥ 0) |

---

#### `appointments` — Agendamentos

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer PK | Identificador |
| `final_value` | Numeric(10,2) | Valor total calculado |
| `service_at` | DateTime | Data e hora do atendimento |
| `payment_method` | String(20) | Forma de pagamento |
| `status` | String(20) | `agendado`, `concluído`, `cancelado` |
| `online` | Boolean | Se foi agendado online |
| `notes` | String(500) | Observações |
| `store_id` | FK → stores.id | Loja do atendimento |
| `client_id` | FK → clients.user_id | Cliente |
| `employee_id` | FK → employees.user_id | Funcionário responsável |
| `pet_id` | FK → pets.id | Pet atendido |

---

#### `appointment_services` — Serviços incluídos em um agendamento (N:M com dados extras)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `appointment_id` | FK → appointments.id | Agendamento |
| `service_id` | FK → services.id | Serviço |
| `charged_value` | Numeric(10,2) | Valor cobrado nesse item |
| `ordered_at` | DateTime | Quando foi solicitado |
| `delivered_at` | DateTime | Quando foi entregue |
| `notes` | String(500) | Observações do item |

O `final_value` do agendamento é a soma de todos os `charged_value` desta tabela.

---

## Arquitetura em camadas

```
Requisição HTTP
      ↓
  Router         → recebe parâmetros, faz checagem de autorização, chama o service
      ↓
  Service        → valida regras de negócio, acessa o banco via SQLAlchemy
      ↓
  Models (ORM)   → mapeamento de tabelas
      ↓
  Database       → SQLite (dev) / PostgreSQL (prod)
```

- **Routers** não contêm lógica de negócio — apenas orquestram a chamada e retornam a resposta HTTP.
- **Services** concentram toda a validação e lógica: unicidade, relacionamentos, cálculos de valor etc.
- **Schemas Pydantic** definem o contrato de entrada e saída de cada endpoint.

---

## Autenticação e segurança

O módulo `app/core/security.py` centraliza toda a lógica de autenticação.

### Fluxo de login

1. Cliente envia `email` e `password` para `POST /auth/login`.
2. O sistema verifica a senha com `passlib` (pbkdf2_sha256).
3. Se válida, gera um **JWT** com `python-jose` assinado com `JWT_SECRET_KEY`.
4. O token é retornado junto com os dados do usuário.
5. Rotas protegidas recebem o token no header `Authorization: Bearer <token>`.
6. A dependência `get_current_active_user` valida o token e verifica se o usuário está ativo.

### Funções principais

| Função | O que faz |
|--------|-----------|
| `hash_password(password)` | Gera hash seguro da senha |
| `verify_password(plain, hashed)` | Compara senha com hash |
| `create_access_token(data)` | Gera JWT com expiração |
| `get_current_user(token, db)` | Decodifica JWT e busca usuário no banco |
| `get_current_active_user(user)` | Garante que o usuário está ativo (`active=True`) |

### CORS

Configurado para permitir requisições apenas de:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

---

## Routers — Endpoints da API

### Auth (`/auth`)

Endpoints públicos e de sessão. Não exigem token para login e registro.

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/auth/login` | Autentica e retorna token JWT | Não |
| `POST` | `/auth/register` | Registra novo usuário e retorna token | Não |
| `GET` | `/auth/me` | Retorna os dados do usuário logado | Sim |
| `POST` | `/auth/logout` | Encerra sessão (invalidação client-side) | Sim |

**Body do login:**
```json
{ "email": "usuario@email.com", "password": "senha123" }
```

**Resposta de sucesso:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { ... }
}
```

---

### User (`/user`)

Gerenciamento de contas de usuários. Aceita perfis de `cliente` e `funcionario` com campos diferentes.

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/user` | Cria usuário | Sim (superuser) |
| `GET` | `/user/users` | Lista todos os usuários | Sim |
| `GET` | `/user/{user_id}` | Busca usuário por ID | Sim |
| `PUT` | `/user/{user_id}` | Atualiza usuário | Sim |
| `DELETE` | `/user/{user_id}` | Remove usuário | Sim |

**Campos para criação de cliente:**
- `name`, `email`, `password`, `phone`, `profile_type: "cliente"`
- `cpf` (pessoa física) ou `cnpj` (pessoa jurídica)
- `client_type`, `cep`, `state`, `city`

**Campos adicionais para funcionário:**
- `profile_type: "funcionario"`, `employee_code`, `job_title`, `salary`, `hired_at`, `store_id`

---

### Pet (`/pet`)

Cadastro e gerenciamento de pets dos clientes.

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/pet` | Cadastra pet | Sim |
| `GET` | `/pet/pets` | Lista todos os pets | Não |
| `GET` | `/pet/{pet_id}` | Busca pet por ID | Não |
| `PUT` | `/pet/{pet_id}` | Atualiza pet | Sim |
| `DELETE` | `/pet/{pet_id}` | Remove pet | Sim |

**Campos principais:**
- `name`, `breed`, `sex` (`M`/`F`), `size`, `weight` (> 0)
- `category_id`, `owner_id`
- `tag_ids` (lista de IDs de tags, opcional)

---

### Appointment (`/appointment`)

Agendamentos de serviços para os pets.

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/appointment` | Cria agendamento | Sim |
| `GET` | `/appointment/appointments` | Lista todos os agendamentos | Não |
| `GET` | `/appointment/{id}` | Busca agendamento por ID | Não |
| `PUT` | `/appointment/{id}` | Atualiza agendamento | Sim |
| `DELETE` | `/appointment/{id}` | Remove agendamento | Sim |

**Campos principais:**
- `service_at` (data/hora), `payment_method`, `status`
- `store_id`, `client_id`, `employee_id`, `pet_id`
- `service_ids` (lista de IDs de serviços)
- O `final_value` é calculado automaticamente pela soma dos serviços

**Status válidos:** `agendado`, `concluído`, `cancelado`

**Formas de pagamento:** `dinheiro`, `cartão de crédito`, `cartão de débito`, `pix`, `transferência bancária`

---

### Service (`/service`)

Serviços oferecidos pelo petshop (banho, tosa, consulta etc.).

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/service` | Cria serviço | Sim (funcionário/superuser) |
| `GET` | `/service/services` | Lista todos os serviços | Não |
| `GET` | `/service/{id}` | Busca serviço por ID | Não |
| `PUT` | `/service/{id}` | Atualiza serviço | Sim (funcionário/superuser) |
| `DELETE` | `/service/{id}` | Remove serviço | Sim (funcionário/superuser) |

---

### Store (`/store`)

Gerenciamento das lojas físicas do petshop.

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/store` | Cria loja | Sim (superuser) |
| `GET` | `/store/stores` | Lista todas as lojas | Não |
| `GET` | `/store/{store_id}` | Busca loja por ID | Não |
| `PUT` | `/store/{store_id}` | Atualiza loja | Sim (superuser) |
| `DELETE` | `/store/{store_id}` | Remove loja | Sim (superuser) |

A resposta inclui a lista de funcionários vinculados à loja.

---

### Category (`/category`)

Categorias/espécies dos pets (cachorro, gato, pássaro etc.).

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/category` | Cria categoria | Sim (funcionário/superuser) |
| `GET` | `/category/categories` | Lista todas as categorias | Não |
| `GET` | `/category/{id}` | Busca categoria por ID | Não |
| `PUT` | `/category/{id}` | Atualiza categoria | Sim (funcionário/superuser) |
| `DELETE` | `/category/{id}` | Remove categoria | Sim (funcionário/superuser) |

> Deletar uma categoria remove em cascata todos os pets vinculados a ela.

---

### Tag (`/tag`)

Tags descritivas para pets (ex: "vacinado", "dócil", "necessita cuidados especiais").

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/tag` | Cria tag | Sim (funcionário/superuser) |
| `GET` | `/tag/tags` | Lista todas as tags | Não |
| `GET` | `/tag/{id}` | Busca tag por ID | Não |
| `PUT` | `/tag/{id}` | Atualiza tag | Sim (funcionário/superuser) |
| `DELETE` | `/tag/{id}` | Remove tag | Sim (funcionário/superuser) |

---

## Services — Regras de negócio

### `user_service.py`

- Valida se o e-mail já está cadastrado.
- Exige senha com no mínimo 6 caracteres.
- Normaliza o `profile_type` (aceita variações como `'client'` → `'cliente'`).
- Para clientes, exige CPF (pessoa física) ou CNPJ (pessoa jurídica).
- Para funcionários, exige `store_id`, `employee_code`, `job_title`, `salary` e `hired_at`.
- Ao deletar um usuário cliente, remove em cascata seus pets (e os agendamentos dos pets).

### `pet_service.py`

- Verifica se o dono existe e é do tipo `cliente`.
- Impede dois pets com o mesmo nome para o mesmo dono.
- Valida que o `weight` é maior que zero.
- Normaliza o sexo do pet (`'macho'` → `'M'`, `'femea'` → `'F'`).
- Valida e carrega as tags passadas em `tag_ids`, garantindo que existem no banco.
- Ao deletar um pet, remove em cascata seus agendamentos.

### `appointment_service.py`

- Verifica se todos os IDs (loja, cliente, funcionário, pet) existem no banco.
- Garante que o **funcionário pertence à loja** informada no agendamento.
- Garante que o **pet pertence ao cliente** do agendamento.
- Calcula o `final_value` automaticamente somando os `charged_value` dos serviços.
- Clientes que criam agendamentos têm `online` forçado para `True`.
- Normaliza forma de pagamento e status (aceita variações de texto).
- Sincroniza o `final_value` ao buscar um agendamento (recalcula se houver divergência).

### `store_service.py`

- Valida formato do CEP com regex (`\d{5}-?\d{3}`).
- Verifica unicidade de CNPJ e e-mail da loja.
- Ao deletar uma loja, remove em cascata os funcionários vinculados.
- Retorna a loja com a lista de funcionários carregada (eager loading).

### `service_service.py`

- Valida que o nome tem entre 2 e 120 caracteres.
- Valida que a descrição não ultrapassa 500 caracteres.
- Valida que o preço não é negativo.

### `category_service.py`

- Valida unicidade e tamanho do nome (2–80 caracteres).
- Ao atualizar, verifica unicidade excluindo o próprio registro.
- Ao deletar uma categoria, pets vinculados são removidos em cascata.

### `tag_service.py`

- Valida unicidade e tamanho do nome (2–80 caracteres).
- Ao deletar uma tag, remove as entradas na tabela `pet_tags` (sem deletar os pets).

---

## Regras de autorização por perfil

| Ação | Cliente | Funcionário | Superuser |
|------|---------|-------------|-----------|
| Criar pet para si | Sim | Sim | Sim |
| Criar pet para outro cliente | Não | Sim | Sim |
| Editar/deletar pet próprio | Sim | Sim | Sim |
| Editar/deletar pet de outro | Não | Sim | Sim |
| Criar agendamento para si | Sim (online=true) | Sim | Sim |
| Criar agendamento para outro | Não | Sim | Sim |
| Gerenciar serviços/categorias/tags | Não | Sim | Sim |
| Criar/editar/deletar lojas | Não | Não | Sim |
| Criar usuários via admin | Não | Não | Sim |
| Editar/deletar qualquer usuário | Não | Não | Sim |
| Editar/deletar a si mesmo | Sim | Sim | Sim |
