# Guia de Integracao Frontend - API Petstore Apex

## 1. Visao Geral
Este documento descreve o contrato atual da API para consumo no frontend.

- Stack backend: FastAPI + SQLAlchemy
- Formato de resposta: JSON
- Ambiente local esperado:
  - API: `http://127.0.0.1:8000`
  - Swagger: `http://127.0.0.1:8000/docs`
- CORS liberado para:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`

## 2. Ponto importante (entrada de dados)
Atualmente, os endpoints de criacao e atualizacao recebem dados por **query params** (na URL), e nao por body JSON.

Exemplo (POST user):

```http
POST /user?name=Gabriel&email=gabriel@email.com&password=12345678&role=cliente
```

No frontend (axios), use `params`:

```ts
await api.post('/user', null, {
  params: {
    name: 'Gabriel',
    email: 'gabriel@email.com',
    password: '12345678',
    role: 'cliente',
  },
});
```

## 2.1 Mudancas recentes

### Appointments agora retornam os servicos prestados em campo `items`
A partir da versao atual, ao retornar um atendimento, o endpoint inclui automaticamente a lista de servicos prestados (campo `items`). Isso elimina a necessidade de fazer uma chamada adicional para obter os detalhes dos servicos.

**O que mudou:**
- Campo `items` (antes `services`) adicionado ao schema `Appointment`
- Cada item contem: `service_id`, `charged_value`, `order_date`, `delivery_date`, e `observations`
- O `value_final` é calculado automaticamente como soma dos `charged_value` dos itens
- Campo `payment_type` renomeado para `payment_method`
- Campo `worker_id` renomeado para `employee_id`
- `service_ids` é agora OBRIGATORIO na criacao e atualizacao
- Validacao: pet deve pertencer ao cliente informado

## 3. Convencao de respostas e erros

### 3.1 Sucesso
- `POST`: `201` + objeto criado
- `GET` lista: `200` + array de objetos
- `GET` por id: `200` + objeto
- `PUT`: `200` + objeto atualizado
- `DELETE`: `200` + `{ "message": "..." }`

### 3.2 Erros
- `400`: regra de negocio (ex.: duplicidade, campo obrigatorio de regra)
- `404`: recurso nao encontrado
- `422`: validacao de parametros do FastAPI (tipo invalido, parametro obrigatorio ausente)

Formato comum de erro:

```json
{
  "detail": "Mensagem de erro"
}
```

Formato de erro de validacao (422):

```json
{
  "detail": [
    {
      "loc": ["query", "name"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

## 4. Contrato por recurso

## 4.1 Users
Prefixo: `/user`

### Endpoints
- `POST /user`
  - Query params:
    - `name` (string, obrigatorio, 2-120 caracteres)
    - `password` (string, obrigatorio, minimo 8)
    - `email` (string, obrigatorio, max 255 caracteres)
    - `phone` (string, opcional, max 20 caracteres)
    - `profile_type` (string, obrigatorio: cliente ou funcionario)
    - `user_active` (boolean, opcional, default `true`)
    - Parametros adicionais para funcionario (se profile_type=funcionario):
      - `hired_at` (date, opcional no router; formato: YYYY-MM-DD)
      - `job_title` (string, max 80 caracteres)
      - `salary` (Decimal, opcional)
      - `store_id` (int, obrigatorio para funcionario)
    - Parametros adicionais para cliente (se profile_type=cliente):
      - `cpf` (string, opcional, max 14 caracteres) ou `cnpj` (string, opcional, max 18 caracteres)
      - `cep` (string, opcional, max 9 caracteres)
      - `city` (string, opcional, max 120 caracteres)
      - `state` (string, opcional, max 2 caracteres)
  - Retorno: `201` + `User`

- `GET /user/users`
  - Retorno: `200` + `User[]`

- `GET /user/{user_id}`
  - Retorno: `200` + `User`

- `PUT /user/{user_id}`
  - Query params (todos opcionais):
    - `name`, `email`, `password`, `phone`, `profile_type`, `user_active`
    - Parametros opcionais adicionais para funcionario:
      - `hired_at` (date, formato YYYY-MM-DD)
      - `job_title` (string)
      - `salary` (Decimal)
      - `store_id` (int)
    - Parametros opcionais adicionais para cliente:
      - `cpf` (string)
      - `cnpj` (string)
      - `cep` (string)
      - `city` (string)
      - `state` (string)
  - Retorno: `200` + `User`

- `Dhone": "11999999999",
  "profile_type": "cliente",
  "cpf": null,
  "cnpj": null,
  "active": true,
  "is_superuser": false,
  "created_at": "2026-04-14T19:30:00"
}
```

**Observacao importante**: O campo `password_hash` NAO deve ser retornado na resposta por motivos de seguranca. Caso esteja sendo retornado, contacte o backend para correção
  "role": "cliente",
  "cpf": null,
  "cnpj": null,
  "active": true,
  "is_superuser": false,
  "created_at": "2026-04-14T19:30:00"
}
```

Observacao: atualmente `password_hash` esta sendo retornado no response.

## 4.2 Stores
Prefixo: `/store`

### Endpoints
- `POST /store`
  - Query params obrigatorios:
    - `name`, `cnpj`, `phone`, `email`, `cep`, `city`, `state`, `address`, `neighborhood`, `number`
  - Query params opcionais:
    - `active` (boolean, default `true`)
  - Retorno: `201` + `Store`

- `GET /store/stores`
  - Retorno: `200` + `Store[]`

- `GET /store/{store_id}`
  - Retorno: `200` + `Store`

- `PUT /store/{store_id}`
  - Query params: todos opcionais do recurso
  - Retorno: `200` + `Store`

- `DELETE /store/{store_id}`
  - Retorno: `200` + `{ "message": "Loja deletada com sucesso" }`

### Shape de resposta `Store`

```json
{
  "id": 1,
  "name": "Loja Centro",
  "cnpj": "12.345.678/0001-90",
  "phone": "1133334444",
  "email": "contato@loja.com",
  "cep": "01001-000",
  "city": "Sao Paulo",
  "state": "SP",
  "address": "Rua A",
  "neighborhood": "Centro",
  "number": "100",
  "active": true,
  "created_at": "2026-04-14T19:30:00"
}
```

## 4.3 Pets
Prefixo: `/pet`

### Endpoints
- `POST /pet`
  - Query params:
    - obrigatorios: `name`, `breed`, `sex`, `size`, `weight`, `category_id`, `owner_id`
    - opcionais: `health_notes`, `tag_ids`
  - Validacoes:
    - `name`: 2-120 caracteres
    - `breed`: max 80 caracteres
    - `sex`: aceita M, F, macho, femea, fêmea (normalizados para M ou F)
    - `weight`: Decimal >= 0
    - `health_notes`: max 500 caracteres
  - Retorno: `201` + `Pet`

- `GET /pet/pets`
  - Retorno: `200` + `Pet[]`

- `GET /pet/{pet_id}`
  - Retorno: `200` + `Pet`

- `PUT /pet/{pet_id}`
  - Query params todos opcionais
  - Retorno: `200` + `Pet`

- `DELETE /pet/{pet_id}`
  - Retorno: `200` + `{ "message": "Pet deletado com sucesso" }`

### Shape de resposta `Pet`

```json
{
  "id": 1,
  "name": "Rex",
  "breed": "SRD",
  "sex": "M",
  "size": "medio",
  "weight": 12.50,
  "health_notes": "Vacinado",
  "category_id": 1,
  "owner_id": 5,
  "tags": [
    {
      "id": 1,
      "name": "alergico",
      "description": ""
    }
  ]
}
```

**Nota**: O campo `weight` é um número Decimal com 2 casas decimais. No frontend, use `number` em TypeScript.

## 4.4 Services
Prefixo: `/service`

### Endpoints
- `POST /service`
  - Query params:
    - `name` (obrigatorio)
    - `description` (opcional)
    - `price` (obrigatorio na regra de negocio)
  - Retorno: `201` + `Service`

- `GET /service/services`
  - Retorno: `200` + `Service[]`

- `GET /service/{id}`
  - Retorno: `200` + `Service`

- `PUT /service/{id}`
  - Query params opcionais: `name`, `description`, `price`
  - Retorno: `200` + `Service`

- `DELETE /service/{id}`
  - Retorno: `200` + `{ "message": "Servico deletado com sucesso" }`

### Shape de resposta `Service`

```json
{
  "id": 1,
  "name": "Banho",
  "description": "Banho completo",
  "price": 79.9
}
```

## 4.5 Categories
Prefixo: `/category`

### Endpoints
- `POST /category`
  - Query params:
    - `name` (obrigatorio)
    - `description` (opcional)
  - Retorno: `201` + `Category`

- `GET /category/categories`
  - Retorno: `200` + `Category[]`

- `GET /category/{id}`
  - Retorno: `200` + `Category`

- `PUT /category/{id}`
  - Query params:
    - `name` (obrigatorio)
    - `description` (opcional)
  - Retorno: `200` + `Category`

- `DELETE /category/{id}`
  - Retorno: `200` + `{ "message": "Categoria deletada com sucesso" }`

### Shape de resposta `Category`

```json
{
  "id": 1,
  "name": "Canino",
  "description": "Pets caninos"
}
```

## 4.6 Tags
Prefixo: `/tag`

### Endpoints
- `POST /tag`
  - Query params:
    - `name` (obrigatorio)
  - Retorno: `201` + `Tag`

- `GET /tag/tags`
  - Retorno: `200` + `Tag[]`

- `GET /tag/{id}`
  - Retorno: `200` + `Tag`

- `PUT /tag/{id}`
  - Query params:
    - `name` (obrigatorio)
    - `description` (opcional)
  - Retorno: `200` + `Tag`

- `DELETE /tag/{id}`
  - Retorno: `200` + `{ "message": "Tag deletada com sucesso" }`

### Shape de resposta `Tag`

```json
{
  "id": 1,
  "name": "Urgente",
  "description": "Atendimento prioritario"
}
```

## 4.7 Appointments
Prefixo: `/appointment`

**Observacao importante**: o campo `employee_id` usado em atendimentos deve receber o `id` do usuario (`users.id`) que possui `employee_profile`. Como a tabela `employees` usa `user_id` como chave primaria, nao existe um ID separado para o funcionario.

### Endpoints
- `POST /appointment`
  - Query params obrigatorios:
    - `store_id` (int)
    - `client_id` (int)
    - `employee_id` (int, id do usuario funcionario)
    - `pet_id` (int; o pet DEVE pertencer ao cliente)
    - `payment_method` (string, obrigatorio; aceita: dinheiro, cash, pix, cartao_credito, credit_card, cartao_debito, debit_card, boleto; normalizados)
    - `service_ids` (lista de ints, obrigatorio; envie repetindo o parametro na URL; minimo 1 servico)
  - Query params opcionais:
    - `service_at` (datetime, default null)
    - `status` (string, default agendado; aceita: agendado, em_andamento, concluido, cancelado; normalizados)
    - `notes` (string, max 500 caracteres)
    - `online` (boolean, default false)
  - Retorno: `201` + `Appointment` (com `items` preenchidos)

- `GET /appointment/appointments`
  - Retorno: `200` + `Appointment[]` (com `items` preenchidos para cada atendimento)

- `GET /appointment/{id}`
  - Retorno: `200` + `Appointment` (com `items` preenchidos)

- `PUT /appointment/{id}`
  - Query params: todos opcionais, incluindo `service_ids` para substituir os servicos do atendimento; se informado, deve conter ao menos um id
  - Retorno: `200` + `Appointment` (com `items` preenchidos)

- `DELETE /appointment/{id}`
  - Retorno: `200` + `{ "message": "Atendimento deletado com sucesso" }`

### Shape de resposta `Appointment`

```json
{
  "id": 1,
  "value_final": 120.00,
  "service_at": "2026-02-01T10:00:00",
  "payment_method": "pix",
  "status": "concluido",
  "online": false,
  "notes": "Atendimento tranquilo",
  "store_id": 1,
  "client_id": 1,
  "employee_id": 6,
  "pet_id": 1,
  "items": [
    {
      "appointment_id": 1,
      "service_id": 1,
      "charged_value": 80.00,
      "order_date": "2026-02-01T10:00:00",
      "delivery_date": null,
      "observations": "Banho completo realizado"
    },
    {
      "appointment_id": 1,
      "service_id": 2,
      "charged_value": 40.00,
      "order_date": "2026-02-01T10:15:00",
      "delivery_date": null,
      "observations": "Tosa complementar"
    }
  ]
}
```

**Observacao**: O campo `items` (antes `services`) contem todos os servicos prestados no atendimento. Cada item representa um servico com seu valor cobrado e opcional data de entrega. O `value_final` é calculado automaticamente como a soma de todos os `charged_value` dos itens. Um atendimento deve sempre ter ao menos um servico.

**O que muda no Frontend:**

1. **Sem chamadas adicionais**: Antes, era necessário fazer uma chamada separada para obter os servicos de um atendimento. Agora eles vêm junto em `items[]`.

2. **Estrutura de iteração**: Para listar os servicos de um atendimento agora é simples:
```ts
appointment.items.forEach(item => {
  console.log(`Servico ${item.service_id}: R$ ${item.charged_value}`);
});
```

3. **Valor total**: O `value_final` já está calculado. Nunca calcule manualmente no front; use sempre `appointment.value_final`.

4. **Mudanças de nomenclatura**:
   - Campo `services` renomeado para `items`
   - Campo `payment_type` renomeado para `payment_method`
   - Campo `worker_id` renomeado para `employee_id`
   - Campo `observations` renomeado para `notes`

5. **Campos obrigatorios**: `store_id`, `client_id`, `employee_id`, `pet_id`, `payment_method` e `service_ids` são OBRIGATORIOS na criacao.

6. **Validacao**: O pet selecionado DEVE pertencer ao cliente informado. Se não, receberá erro 400 com detalhe explicativo.

A API usa autenticação baseada em JWT com esquema Bearer. O login é simples por email e senha (JSON) — não é necessário `client_id`/`client_secret`.

- Endpoint de login:

```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

Resposta (exemplo):

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer",
  "user": { /* objeto User */ }
}
```

- Endpoint de registro (opcional): `POST /auth/register` — envia um `UserCreate` em JSON e recebe o mesmo `TokenResponse` com `access_token`.

Como usar o token no frontend:

- Enviar header `Authorization: Bearer <JWT_TOKEN>` em todas as requisições protegidas.

Exemplo com `fetch`:

```js
const token = '<JWT_TOKEN>';
fetch('/pet/pets', {
  headers: {
    'Authorization': `Bearer ${token}`,
  }
});
```

Exemplo com `axios` (definir header global):

```js
import axios from 'axios';
axios.defaults.baseURL = 'http://127.0.0.1:8000';
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

const resp = await axios.get('/pet/pets');
```

Swagger / OpenAPI:

- Abra `/docs` e use o botão "Authorize" — cole `Bearer <JWT_TOKEN>` (inclua o prefixo `Bearer`) no campo para que o Swagger envie o header automaticamente.

Notas de implementação
- O endpoint de login retorna `token_type: "bearer"`; o frontend pode armazenar o token em memória, `localStorage` ou `sessionStorage` conforme a sua política de segurança.
- Sempre enviar o token em `Authorization` para acessar rotas que dependem de `get_current_active_user`.

1. **Sem chamadas adicionais**: Antes, era necessário fazer uma chamada separada para obter os serviços de um atendimento. Agora eles vêm junto.

2. **Estrutura de iteração**: Para listar os serviços de um atendimento agora é simples:
```ts
appointment.items.forEach(item => {
  console.log(`Serviço ${item.service_id}: R$ ${item.charged_value}`);
});
```

3. **Valor total**: O `value_final` já está calculado. Nunca calcule manualmente no front; use sempre `appointment.value_final`.

**Criar um Atendimento com Serviços:**

Agora o endpoint POST exige `service_ids` e cria automaticamente os registros na tabela de juncao, usando o preço atual de cada servico como `charged_value`.

Exemplo de chamada:

```http
POST /appointment?store_id=1&client_id=1&employee_id=6&pet_id=1&payment_method=pix&service_ids=1&service_ids=2
```

No frontend (axios), envie a lista em `params`:

```ts
await api.post('/appointment', null, {
  params: {
    store_id: 1,
    client_id: 1,
    employee_id: 6,
    pet_id: 1,
    payment_method: 'pix',
    service_ids: [1, 2],
  },
});
```

Ao atualizar um atendimento, informar `service_ids` substitui a lista atual de servicos por nova seleção.

**Regras de Validacao de Atendimentos:**

1. **Pet deve pertencer ao Cliente**: Ao criar ou atualizar um atendimento, o `pet_id` selecionado DEVE pertencer ao cliente (`client_id`) informado. Se tentar usar um pet que pertence a outro cliente, receberá um erro 400:
   ```json
   {
     "detail": "O pet selecionado não pertence ao cliente informado. Pet pertence ao cliente X"
   }
   ```
   **Implicacao no Front**: Ao exibir o formulario de criacao/edicao de atendimento, popule o dropdown de pets filtrando apenas pelos pets do cliente selecionado. Isso evita erros e melhora UX.

2. **Campos Obrigatorios**: `store_id`, `client_id`, `employee_id`, `pet_id`, `payment_method` e `service_ids` sao obrigatorios na criacao do atendimento.

3. **Payment Method Normalization**: O sistema aceita 8 variantes de forma de pagamento e normaliza para 4 valores canonicos:
   - `dinheiro` / `cash` → `dinheiro`
   - `pix` → `pix`
   - `cartao_credito` / `credit_card` → `cartão de crédito`
   - `cartao_debito` / `debit_card` → `cartão de débito`
   - `boleto` → `boleto`

4. **Status Normalization**: O sistema aceita 8 variantes de status e normaliza para 4 valores canonicos:
   - `agendado` / `scheduled` → `agendado`
   - `em_andamento` / `in_progress` → `em_andamento`
   - `concluido` / `completed` → `concluido`
   - `cancelado` / `cancelled` → `cancelado`

5. **Service IDs**: Deve conter ao menos um servico. Envie como lista repetida na query string ou como array em `params` do axios.

## 5. Tipos recomendados no frontend (TypeScript)

```ts
export type ApiError = {
  detail: string | Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
};

export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  profile_type: string;
  cpf: string | null;
  cnpj: string | null;
  active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Store {
  id: number;
  name: string;
  cnpj: string;
  phone: string;
  email: string;
  cep: string;
  city: string;
  state: string;
  address: string;
  neighborhood: string;
  number: string;
  active: boolean;
  created_at: string;
}

export interface Pet {
  id: number;
  name: string;
  breed: string;
  sex: string;
  size: string;
  weight: number;  // Decimal com 2 casas
  health_notes: string | null;
  category_id: number;
  owner_id: number;
  tags: Tag[];
}

export interface Service {
  id: number;
  name: string;
  description: string | null;
  price: number;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export interface Tag {
  id: number;
  name: string;
  description: string | null;
}

export interface AppointmentService {
  appointment_id: number;
  service_id: number;
  charged_value: number;
  order_date: string;
  delivery_date: string | null;
  observations: string | null;
}

export interface Appointment {
  id: number;
  value_final: number;
  service_at: string | null;
  payment_method: string;
  status: string;
  online: boolean;
  notes: string | null;
  store_id: number;
  client_id: number;
  employee_id: number;
  pet_id: number;
  items: AppointmentService[];  // antes chamado de "services"
}
```

## 6. Exemplo de client HTTP (axios)

```ts
import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

export async function listUsers() {
  const { data } = await api.get('/user/users');
  return data;
}

export async function createUser(payload: {
  name: string;
  email: string;
  password: string;
  phone?: string;
  role?: string;
}) {
  const { data } = await api.post('/user', null, { params: payload });
  return data;
}

export async function updateUser(userId: number, payload: Partial<{
  name: string;
  email: string;
  password: string;
  phone: string;
  profile_type: string;
  user_active: boolean;
  hired_at: string;
  job_title: string;
  salary: number;
  store_id: number;
  cpf: string;
  cnpj: string;
  cep: string;
  city: string;
  state: string;
}>) {
  const { data } = await api.put(`/user/${userId}`, null, { params: payload });
  return data;
}

// Exemplo especifico para appointments
export async function getAppointment(appointmentId: number) {
  const { data } = await api.get(`/appointment/${appointmentId}`);
  // data sera um objeto Appointment com items preenchido
  return data;
}

export async function listAppointments() {
  const { data } = await api.get('/appointment/appointments');
  // Cada item no array tera a lista de servicos prestados em items[]
  return data;
}

export async function createAppointment(payload: {
  store_id: number;
  client_id: number;
  employee_id: number;
  pet_id: number;
  payment_method: string;
  service_ids: number[];
  service_at?: string;
  status?: string;
  notes?: string;
  online?: boolean;
}) {
  const { data } = await api.post('/appointment', null, { params: payload });
  return data;
}
```

### Exemplo de uso no componente (React)

```tsx
const appointment = await getAppointment(1);

// Agora voce pode acessar os servicos direto:
appointment.items.forEach(item => {
  console.log(`Servico ${item.service_id}: R$ ${item.charged_value}`);
});

// Total ja esta calculado
console.log(`Total: R$ ${appointment.value_final}`);

// Quando criar um atendimento, sempre considere a regra de pet vs cliente
async function criarAtendimento(dados: {
  store_id: number;
  client_id: number;
  employee_id: number;
  pet_id: number;
  payment_method: string;
  service_ids: number[];
}) {
  try {
    const response = await api.post('/appointment', null, { params: dados });
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 400 && error.response?.data?.detail?.includes('pet')) {
      // Erro de validacao: pet nao pertence ao cliente
      console.error('Pet selecionado nao pertence ao cliente');
      // Aqui voce pode exibir um alerta no UI
    }
    throw error;
  }
}
```

## 7. Checklist de integracao no frontend

- Configurar `baseURL` para `http://127.0.0.1:8000`.
- Enviar dados de POST/PUT via `params`.
- Tratar erros `400`, `404`, `422` lendo `error.response.data.detail`.
- Tipar campos de data/hora como `string` (ISO).
- Tipar campos decimais como `number` no front.
- Usar `/docs` para validar rapidamente qualquer contrato durante desenvolvimento.

## 8. Resumo das mudancas de campo e tipo

| Recurso | Campo Anterior | Campo Atual | Tipo Anterior | Tipo Atual | Notas |
|---------|---|---|---|---|---|
| Pet | - | weight | float | Decimal | Mudança de tipo no router e schema |
| Pet | sexo | sex | string | string | Agora aceita alias normalization (M/F/macho/femea) |
| User | role | profile_type | string | string | Renomeado |
| User | - | hired_at | datetime | date | Mudança de tipo em schemas e service |
| Appointment | payment_type | payment_method | string | string | Renomeado e agora com alias normalization |
| Appointment | worker_id | employee_id | int | int | Renomeado |
| Appointment | observations | notes | string | string | Renomeado |
| Appointment | services | items | array | array | Campo renomeado |

## 9. Fontes do contrato (backend)

- `app/main.py`
- `app/routers/auth_crud.py`
- `app/routers/user_crud.py`
- `app/routers/store_crud.py`
- `app/routers/pet_crud.py`
- `app/routers/service_crud.py`
- `app/routers/category_crud.py`
- `app/routers/tag_crud.py`
- `app/routers/appointment_crud.py`
- `app/schemas/schemas.py`
- `app/schemas/models.py`
- `app/services/user_service.py`
- `app/services/store_service.py`
- `app/services/pet_service.py`
- `app/services/service_service.py`
- `app/services/category_service.py`
- `app/services/tag_service.py`
- `app/services/appointment_service.py`
- `app/core/security.py`
