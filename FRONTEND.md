# Frontend — Guia de Integração com a API

Base URL de desenvolvimento: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

---

## Índice

- [Autenticação](#autenticação)
- [Padrão de requisições](#padrão-de-requisições)
- [Tratamento de erros](#tratamento-de-erros)
- [Fluxos por tela](#fluxos-por-tela)
  - [Login](#login)
  - [Registro](#registro)
  - [Perfil do usuário logado](#perfil-do-usuário-logado)
  - [Pets](#pets)
  - [Agendamento online (cliente)](#agendamento-online-cliente)
  - [Agendamento administrativo (funcionário/superuser)](#agendamento-administrativo-funcionáriosuperuser)
  - [Lojas](#lojas)
  - [Funcionários por loja](#funcionários-por-loja)
  - [Serviços](#serviços)
  - [Categorias](#categorias)
  - [Tags](#tags)
  - [Usuários (admin)](#usuários-admin)
- [Regras de exibição por perfil](#regras-de-exibição-por-perfil)
- [Referência rápida de endpoints](#referência-rápida-de-endpoints)

---

## Autenticação

A API usa **JWT Bearer Token**. Após o login, armazene o token e envie em toda requisição protegida.

### Onde guardar o token

```js
// Salvar após login
localStorage.setItem('token', response.access_token)
localStorage.setItem('user', JSON.stringify(response.user))

// Ler em requisições
const token = localStorage.getItem('token')
```

### Como enviar o token

```js
headers: {
  'Authorization': `Bearer ${token}`
}
```

### Dados do usuário logado

A resposta do login já traz o objeto `user` completo — use-o para controlar o que mostrar na interface sem precisar de uma requisição adicional:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@email.com",
    "phone": "11999999999",
    "profile_type": "cliente",
    "cpf": "123.456.789-00",
    "cnpj": null,
    "active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T00:00:00",
    "client_profile": {
      "user_id": 1,
      "client_type": "pessoa_fisica",
      "cep": "01310-100",
      "state": "SP",
      "city": "São Paulo"
    },
    "employee_profile": null
  }
}
```

---

## Padrão de requisições

> **Atenção:** todos os parâmetros de criação e atualização são enviados como **query string** (não como body JSON). Isso é diferente do padrão REST convencional.

```js
// Exemplo de criação de pet
fetch('http://localhost:8000/pet?name=Rex&breed=Labrador&sex=M&size=grande&weight=25&category_id=1&owner_id=3', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
})
```

Você pode montar a URL com `URLSearchParams`:

```js
const params = new URLSearchParams({
  name: 'Rex',
  breed: 'Labrador',
  sex: 'M',
  size: 'grande',
  weight: 25,
  category_id: 1,
  owner_id: 3,
})

fetch(`http://localhost:8000/pet?${params}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
})
```

Para campos de lista (ex: `tag_ids`, `service_ids`), repita o parâmetro:

```js
// service_ids=[1, 2, 3]
const params = new URLSearchParams()
params.append('service_ids', 1)
params.append('service_ids', 2)
params.append('service_ids', 3)
```

---

## Tratamento de erros

A API retorna erros no formato:

```json
{ "detail": "Mensagem de erro em português" }
```

Códigos usados:

| Código | Situação |
|--------|---------|
| `400` | Dado inválido ou regra de negócio violada |
| `401` | Token ausente ou inválido |
| `403` | Sem permissão para a ação |
| `404` | Recurso não encontrado |
| `422` | Parâmetro obrigatório faltando |

```js
const res = await fetch(url, options)
if (!res.ok) {
  const err = await res.json()
  showError(err.detail) // ex: "O pet selecionado não pertence ao cliente informado"
}
```

---

## Fluxos por tela

---

### Login

**Endpoint:** `POST /auth/login`

```js
const res = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
const data = await res.json()
// data.access_token → salvar no localStorage
// data.user → salvar para controle de perfil
```

**Campos do formulário:** `email`, `password`

**Após o login**, redirecionar com base em `user.profile_type`:
- `"cliente"` → área do cliente
- `"funcionario"` → área administrativa
- `user.is_superuser === true` → painel de admin

---

### Registro

**Endpoint:** `POST /auth/register`

Mesmos campos de criação de usuário. Exibe campos diferentes conforme o tipo escolhido:

**Campos base (sempre):**

| Campo | Tipo | Observação |
|-------|------|-----------|
| `name` | texto | mín. 2 caracteres |
| `email` | email | único no sistema |
| `password` | senha | mín. 6 caracteres |
| `phone` | texto | |
| `profile_type` | select | `"cliente"` ou `"funcionario"` |

**Se `profile_type = "cliente"`:**

| Campo | Tipo | Observação |
|-------|------|-----------|
| `client_type` | select | `"pessoa_fisica"` ou `"pessoa_juridica"` |
| `cpf` | texto | obrigatório se pessoa_fisica |
| `cnpj` | texto | obrigatório se pessoa_juridica |
| `cep` | texto | |
| `state` | texto (2 chars) | UF |
| `city` | texto | |

**Se `profile_type = "funcionario"`:**

| Campo | Tipo | Observação |
|-------|------|-----------|
| `employee_code` | texto | código interno |
| `job_title` | texto | cargo |
| `salary` | número | |
| `hired_at` | data | |
| `store_id` | select | buscar de `GET /store/stores` |
| `cpf` ou `cnpj` | texto | |

Retorna o mesmo objeto `TokenResponse` do login — salvar token e redirecionar.

---

### Perfil do usuário logado

**Endpoint:** `GET /auth/me`

```js
const res = await fetch('http://localhost:8000/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
})
const user = await res.json()
```

Use para atualizar os dados exibidos no header/navbar.

**Atualizar perfil:** `PUT /user/{user_id}` — enviar apenas os campos alterados.

---

### Pets

#### Listar pets do cliente logado

A API não tem filtro por dono na listagem — liste todos e filtre no frontend:

```js
const res = await fetch('http://localhost:8000/pet/pets')
const pets = await res.json()
const meusPets = pets.filter(p => p.owner_id === user.id)
```

#### Cadastrar pet

**Endpoint:** `POST /pet` — requer token

| Campo | Tipo | Observação |
|-------|------|-----------|
| `name` | texto | único por dono |
| `breed` | texto | raça |
| `sex` | select | `"M"` ou `"F"` |
| `size` | select | ex: `"pequeno"`, `"médio"`, `"grande"` |
| `weight` | número | deve ser maior que 0 |
| `category_id` | select | buscar de `GET /category/categories` |
| `owner_id` | int | para cliente: use `user.id` sempre |
| `tag_ids` | lista de int | buscar de `GET /tag/tags`, opcional |
| `health_notes` | textarea | opcional |

**Importante:** se o usuário for cliente, sempre envie `owner_id = user.id`. O backend rejeita com 403 se tentar criar para outro dono.

#### Editar/excluir pet

- `PUT /pet/{pet_id}` — enviar apenas campos alterados
- `DELETE /pet/{pet_id}`

Clientes só podem editar/excluir seus próprios pets.

---

### Agendamento online (cliente)

Este é o fluxo mais importante para a área do cliente. Siga as etapas em ordem.

#### Etapa 1 — Escolher a loja

```js
const res = await fetch('http://localhost:8000/store/stores')
const lojas = await res.json()
// Montar select/cards com lojas ativas
const lojasAtivas = lojas.filter(l => l.active)
```

Exibir: `name`, `city`, `state`, `street`, `number`.

#### Etapa 2 — Escolher o funcionário (opcional)

Após o cliente selecionar a loja, buscar os funcionários dela:

```js
const res = await fetch(`http://localhost:8000/store/${store_id}/employees`)
const funcionarios = await res.json()
// Montar select com funcionários
// Inclui opção "Sem preferência" (deixar em branco)
```

Exibir: `employee_name`, `job_title`.

> Se o cliente não escolher nenhum funcionário, o agendamento é criado sem `employee_id` e a loja atribui depois.

#### Etapa 3 — Escolher o pet

```js
const res = await fetch('http://localhost:8000/pet/pets')
const todos = await res.json()
const meusPets = todos.filter(p => p.owner_id === user.id)
```

#### Etapa 4 — Escolher os serviços

```js
const res = await fetch('http://localhost:8000/service/services')
const servicos = await res.json()
// Checkboxes ou multi-select
```

Exibir: `name`, `description`, `price`. Mostrar o total somando os preços selecionados.

#### Etapa 5 — Preencher data/hora e pagamento

| Campo | Tipo | Valores aceitos |
|-------|------|----------------|
| `service_at` | datetime-local | qualquer data futura |
| `payment_method` | select | `dinheiro`, `cartão de crédito`, `cartão de débito`, `pix`, `transferência bancária` |
| `notes` | textarea | opcional, máx. 500 chars |

#### Etapa 6 — Criar o agendamento

```js
const params = new URLSearchParams({
  store_id: lojaSelecionada,
  client_id: user.id,           // sempre o próprio usuário
  pet_id: petSelecionado,
  payment_method: formaPagamento,
  service_at: dataHora,         // formato ISO: "2024-06-01T14:00:00"
  status: 'agendado',
  notes: observacoes || '',
})

// employee_id só se o cliente tiver escolhido um
if (funcionarioSelecionado) {
  params.append('employee_id', funcionarioSelecionado)
}

// service_ids: um append por serviço
servicosSelecionados.forEach(id => params.append('service_ids', id))

const res = await fetch(`http://localhost:8000/appointment?${params}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
})
```

**O backend automaticamente:**
- Força `online = true`
- Rejeita com 403 se `client_id` for diferente do usuário logado
- Calcula o `final_value` pela soma dos serviços

#### Exibir agendamentos do cliente

```js
const res = await fetch('http://localhost:8000/appointment/appointments')
const todos = await res.json()
const meusAgendamentos = todos.filter(a => a.client_id === user.id)
```

Status possíveis para exibir como badge/chip:

| Status | Cor sugerida |
|--------|-------------|
| `agendado` | azul |
| `em andamento` | amarelo |
| `concluído` | verde |
| `cancelado` | vermelho |

---

### Agendamento administrativo (funcionário/superuser)

Mesma estrutura do fluxo do cliente, com diferenças:

- `client_id` pode ser qualquer cliente — adicionar busca/select de clientes: `GET /user/users` (filtrar por `profile_type === "cliente"`)
- `employee_id` pode ser qualquer funcionário da loja selecionada
- `online` pode ser `false` (atendimento presencial)
- `status` pode ser qualquer valor, não apenas `"agendado"`

Atualização de status de um agendamento (ex: de `agendado` para `em andamento`):

```js
const params = new URLSearchParams({ status: 'em andamento' })
await fetch(`http://localhost:8000/appointment/${id}?${params}`, {
  method: 'PUT',
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

### Lojas

> Criação, edição e exclusão de lojas são exclusivas para **superuser**.

#### Listar lojas

```js
const res = await fetch('http://localhost:8000/store/stores')
const lojas = await res.json()
// Cada loja já vem com employees[] embutido
```

#### Criar loja

**Endpoint:** `POST /store` — requer token de superuser

| Campo | Tipo |
|-------|------|
| `name` | texto (2-120) |
| `cnpj` | texto (14-18) |
| `phone` | texto |
| `email` | email único |
| `cep` | texto (formato `00000-000`) |
| `city` | texto |
| `state` | texto (2 chars, UF) |
| `street` | texto |
| `neighborhood` | texto |
| `number` | texto |
| `active` | boolean (default `true`) |

---

### Funcionários por loja

**Endpoint:** `GET /store/{store_id}/employees` — público, sem autenticação

```js
const res = await fetch(`http://localhost:8000/store/${store_id}/employees`)
const funcionarios = await res.json()
```

Resposta:

```json
[
  {
    "user_id": 5,
    "employee_name": "Maria Santos",
    "employee_code": "F001",
    "job_title": "Tosadora",
    "salary": 2500.00,
    "hired_at": "2023-01-15",
    "store_id": 1
  }
]
```

Use `employee_name` e `job_title` para exibir no select de escolha de funcionário.

---

### Serviços

Listagem pública, criação/edição requer funcionário ou superuser.

```js
// Listar (público)
const res = await fetch('http://localhost:8000/service/services')

// Criar (requer token de funcionário/superuser)
const params = new URLSearchParams({ name, description, price })
await fetch(`http://localhost:8000/service?${params}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

### Categorias

Listagem pública, gestão requer funcionário ou superuser.

```js
// Listar (público) — popular select de categoria ao cadastrar pet
const res = await fetch('http://localhost:8000/category/categories')
```

---

### Tags

Listagem pública, gestão requer funcionário ou superuser.

```js
// Listar (público) — popular multi-select ao cadastrar pet
const res = await fetch('http://localhost:8000/tag/tags')
```

---

### Usuários (admin)

> Listagem e gestão de usuários requer autenticação. Criação requer superuser.

```js
// Listar todos os usuários
const res = await fetch('http://localhost:8000/user/users', {
  headers: { 'Authorization': `Bearer ${token}` }
})
const usuarios = await res.json()

// Filtrar clientes para select em agendamento administrativo
const clientes = usuarios.filter(u => u.profile_type === 'cliente')
```

---

## Regras de exibição por perfil

Use `user.profile_type` e `user.is_superuser` (salvos no localStorage após login) para controlar o que cada usuário vê:

```js
const user = JSON.parse(localStorage.getItem('user'))
const isCliente     = user.profile_type === 'cliente'
const isFuncionario = user.profile_type === 'funcionario'
const isSuperuser   = user.is_superuser
```

| Funcionalidade | Cliente | Funcionário | Superuser |
|----------------|---------|-------------|-----------|
| Ver pets | próprios | todos | todos |
| Cadastrar pet | para si | para qualquer cliente | para qualquer cliente |
| Agendar | para si (online=true) | para qualquer cliente | para qualquer cliente |
| Ver agendamentos | próprios | todos | todos |
| Alterar status de agendamento | não | sim | sim |
| Gerenciar serviços/categorias/tags | não | sim | sim |
| Gerenciar lojas | não | não | sim |
| Criar/editar usuários | não | não | sim |
| Ver lista de todos os usuários | não | sim | sim |

---

## Referência rápida de endpoints

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `POST` | `/auth/login` | Não | Login |
| `POST` | `/auth/register` | Não | Registro |
| `GET` | `/auth/me` | Sim | Usuário logado |
| `GET` | `/user/users` | Sim | Listar usuários |
| `GET` | `/user/{id}` | Sim | Buscar usuário |
| `PUT` | `/user/{id}` | Sim | Atualizar usuário |
| `DELETE` | `/user/{id}` | Sim | Deletar usuário |
| `GET` | `/pet/pets` | Não | Listar pets |
| `POST` | `/pet` | Sim | Criar pet |
| `PUT` | `/pet/{id}` | Sim | Atualizar pet |
| `DELETE` | `/pet/{id}` | Sim | Deletar pet |
| `GET` | `/appointment/appointments` | Não | Listar agendamentos |
| `POST` | `/appointment` | Sim | Criar agendamento |
| `PUT` | `/appointment/{id}` | Sim | Atualizar agendamento |
| `DELETE` | `/appointment/{id}` | Sim | Deletar agendamento |
| `GET` | `/store/stores` | Não | Listar lojas |
| `GET` | `/store/{id}` | Não | Buscar loja |
| `GET` | `/store/{id}/employees` | Não | Funcionários da loja |
| `POST` | `/store` | Superuser | Criar loja |
| `PUT` | `/store/{id}` | Superuser | Atualizar loja |
| `DELETE` | `/store/{id}` | Superuser | Deletar loja |
| `GET` | `/service/services` | Não | Listar serviços |
| `POST` | `/service` | Funcionário | Criar serviço |
| `PUT` | `/service/{id}` | Funcionário | Atualizar serviço |
| `DELETE` | `/service/{id}` | Funcionário | Deletar serviço |
| `GET` | `/category/categories` | Não | Listar categorias |
| `POST` | `/category` | Funcionário | Criar categoria |
| `PUT` | `/category/{id}` | Funcionário | Atualizar categoria |
| `DELETE` | `/category/{id}` | Funcionário | Deletar categoria |
| `GET` | `/tag/tags` | Não | Listar tags |
| `POST` | `/tag` | Funcionário | Criar tag |
| `PUT` | `/tag/{id}` | Funcionário | Atualizar tag |
| `DELETE` | `/tag/{id}` | Funcionário | Deletar tag |
