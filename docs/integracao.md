# Guia de Integracao Frontend - API Petstore Apex

## 1. Visao Geral

- Stack backend: FastAPI + SQLAlchemy + SQLite
- Formato de resposta: JSON
- Ambiente local:
  - API: `http://127.0.0.1:8000`
  - Swagger interativo: `http://127.0.0.1:8000/docs`
- CORS liberado para: `http://localhost:5173` e `http://127.0.0.1:5173`

---

## 2. Autenticacao (JWT Bearer)

Todos os endpoints de escrita e os de leitura de usuarios exigem token JWT no header `Authorization`.

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

Resposta `200`:

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer",
  "user": { /* objeto User */ }
}
```

### Registro publico

```http
POST /auth/register
Content-Type: application/json
```

Recebe um `UserCreate` em body JSON (nao query params). Retorna `201` + `TokenResponse`.

> **Atencao**: o campo `is_superuser` e ignorado no registro; sempre sera `false`. So um superuser pode criar outros superusers via `POST /user`.

### Endpoints auxiliares

| Metodo | Rota | Auth | Descricao |
|---|---|---|---|
| `GET` | `/auth/me` | sim | Retorna o usuario logado |
| `POST` | `/auth/logout` | nao | Instrucao para remover o token no cliente |

### Usando o token no frontend

**axios — header global:**

```ts
import axios from 'axios';

export const api = axios.create({ baseURL: 'http://127.0.0.1:8000' });

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

**Swagger:** use o botao "Authorize" e cole `Bearer <token>`.

---

## 3. Entrada de dados (query params)

Todos os endpoints de criacao e atualizacao (exceto `/auth/login` e `/auth/register`) recebem dados por **query params**, nao por body JSON.

**axios — use `params`:**

```ts
await api.post('/user', null, {
  params: { name: 'Gabriel', email: 'g@email.com', password: 'senha123', profile_type: 'cliente', cpf: '111.111.111-11' },
});
```

---

## 4. Convencao de respostas e erros

### 4.1 Codigos de sucesso

| Metodo | Codigo | Corpo |
|---|---|---|
| `POST` | `201` | objeto criado |
| `GET` | `200` | objeto ou array |
| `PUT` | `200` | objeto atualizado |
| `DELETE` | `200` | `{ "message": "..." }` |

### 4.2 Codigos de erro

| Codigo | Causa |
|---|---|
| `400` | Regra de negocio (duplicidade, campo invalido, conflito) |
| `401` | Token ausente ou invalido |
| `403` | Sem permissao para a operacao |
| `404` | Recurso nao encontrado |
| `422` | Tipo ou formato invalido de parametro (FastAPI) |

**Formato de erro:**

```json
{ "detail": "Mensagem descritiva do erro" }
```

**Formato de erro 422:**

```json
{
  "detail": [
    { "loc": ["query", "email"], "msg": "Field required", "type": "missing" }
  ]
}
```

---

## 5. Regras de autorizacao por recurso

| Recurso | Leitura | Criacao | Atualizacao | Exclusao |
|---|---|---|---|---|
| `/user` | Requer auth | Auth; so superuser pode criar superuser | Auth; so o proprio usuario ou superuser | So o proprio usuario ou superuser |
| `/store` | Publica | So superuser | So superuser | So superuser |
| `/pet` | Publica | Auth; cliente so cria para si mesmo | Auth; dono, funcionario ou superuser | Auth; dono, funcionario ou superuser |
| `/appointment` | Publica | Auth; cliente so cria para si mesmo | Auth; superuser, funcionario ou cliente dono | Auth; superuser, funcionario ou cliente dono |
| `/service` | Publica | Funcionario ou superuser | Funcionario ou superuser | Funcionario ou superuser |
| `/category` | Publica | Funcionario ou superuser | Funcionario ou superuser | Funcionario ou superuser |
| `/tag` | Publica | Funcionario ou superuser | Funcionario ou superuser | Funcionario ou superuser |

---

## 6. Contrato por recurso

### 6.1 Autenticacao

Prefixo: `/auth`

| Metodo | Rota | Auth | Body | Retorno |
|---|---|---|---|---|
| `POST` | `/auth/login` | nao | JSON `{email, password}` | `201` + `TokenResponse` |
| `POST` | `/auth/register` | nao | JSON `UserCreate` | `201` + `TokenResponse` |
| `GET` | `/auth/me` | sim | — | `200` + `User` |
| `POST` | `/auth/logout` | nao | — | `200` + `{message}` |

---

### 6.2 Users

Prefixo: `/user` — todos os endpoints exigem autenticacao.

| Metodo | Rota | Auth extra | Retorno |
|---|---|---|---|
| `POST` | `/user` | — | `201` + `User` |
| `GET` | `/user/users` | — | `200` + `User[]` |
| `GET` | `/user/{user_id}` | — | `200` + `User` |
| `PUT` | `/user/{user_id}` | So o proprio ou superuser | `200` + `User` |
| `DELETE` | `/user/{user_id}` | So o proprio ou superuser | `200` + `{message}` |

**Params de criacao (`POST /user`):**

| Param | Tipo | Obrigatorio | Regras |
|---|---|---|---|
| `name` | string | sim | 2–120 caracteres |
| `email` | string | sim | max 255 caracteres, unico |
| `password` | string | sim | minimo 6 caracteres |
| `phone` | string | sim | max 20 caracteres |
| `profile_type` | string | sim | `"cliente"` ou `"funcionario"` |
| `cpf` | string | um dos dois | max 14 caracteres |
| `cnpj` | string | um dos dois | max 18 caracteres |
| `active` | bool | nao | default `true` |
| `is_superuser` | bool | nao | default `false`; so superuser pode usar `true` |

**Params adicionais para `profile_type = "cliente"`:**

| Param | Tipo | Obrigatorio | Regras |
|---|---|---|---|
| `client_type` | string | nao | `"pessoa_fisica"` ou `"pessoa_juridica"` |
| `cep` | string | nao | max 9 caracteres |
| `state` | string | nao | 2 caracteres |
| `city` | string | nao | max 120 caracteres |

**Params adicionais para `profile_type = "funcionario"` (todos obrigatorios):**

| Param | Tipo | Regras |
|---|---|---|
| `employee_code` | string | max 20 caracteres, unico |
| `job_title` | string | max 80 caracteres |
| `salary` | Decimal | valor positivo |
| `hired_at` | date | formato `YYYY-MM-DD` |
| `store_id` | int | deve existir no banco |

**Shape de resposta `User`:**

```json
{
  "id": 1,
  "name": "Ana Paula",
  "email": "ana.paula@exemplo.com",
  "phone": "11990001111",
  "profile_type": "cliente",
  "cpf": "111.111.111-11",
  "cnpj": null,
  "active": true,
  "is_superuser": false,
  "created_at": "2026-01-10T09:00:00",
  "client_profile": {
    "user_id": 1,
    "client_type": "pessoa_fisica",
    "cep": "01001-000",
    "state": "SP",
    "city": "Sao Paulo"
  },
  "employee_profile": null
}
```

> `employee_profile` contem: `user_id`, `employee_name`, `employee_code`, `job_title`, `salary`, `hired_at`, `store_id`.

---

### 6.3 Stores

Prefixo: `/store` — escrita exige superuser.

| Metodo | Rota | Auth | Retorno |
|---|---|---|---|
| `POST` | `/store` | Superuser | `201` + `Store` |
| `GET` | `/store/stores` | nao | `200` + `Store[]` |
| `GET` | `/store/{store_id}` | nao | `200` + `Store` |
| `PUT` | `/store/{store_id}` | Superuser | `200` + `Store` |
| `DELETE` | `/store/{store_id}` | Superuser | `200` + `{message}` |

**Params de criacao obrigatorios:**
`name`, `cnpj`, `phone`, `email`, `cep`, `city`, `state`, `street`, `neighborhood`, `number`

**Params opcionais:** `active` (bool, default `true`)

**Shape de resposta `Store`:**

```json
{
  "id": 1,
  "name": "Petshop GC Paulista",
  "cnpj": "10.000.000/0001-01",
  "phone": "1130001001",
  "email": "paulista@petshopgc.com",
  "cep": "01310-100",
  "city": "Sao Paulo",
  "state": "SP",
  "street": "Av Paulista",
  "neighborhood": "Bela Vista",
  "number": "1000",
  "active": true,
  "created_at": "2026-01-01T08:00:00",
  "employees": []
}
```

> O campo e `"street"` (nao `"address"`).

---

### 6.4 Pets

Prefixo: `/pet`

| Metodo | Rota | Auth | Retorno |
|---|---|---|---|
| `POST` | `/pet` | sim | `201` + `Pet` |
| `GET` | `/pet/pets` | nao | `200` + `Pet[]` |
| `GET` | `/pet/{pet_id}` | nao | `200` + `Pet` |
| `PUT` | `/pet/{pet_id}` | Dono, funcionario ou superuser | `200` + `Pet` |
| `DELETE` | `/pet/{pet_id}` | Dono, funcionario ou superuser | `200` + `{message}` |

**Params de criacao:**

| Param | Tipo | Obrigatorio | Regras |
|---|---|---|---|
| `name` | string | sim | 2–120 caracteres; unico por dono |
| `breed` | string | sim | max 80 caracteres |
| `sex` | string | sim | `M`, `F`, `macho`, `femea`, `fêmea` — normalizado para `M`/`F` |
| `size` | string | sim | qualquer string nao vazia |
| `weight` | Decimal | sim | >= 0 |
| `category_id` | int | sim | deve existir |
| `owner_id` | int | sim | deve ser um cliente existente |
| `health_notes` | string | nao | max 500 caracteres |
| `tag_ids` | int[] | nao | lista de IDs de tags existentes |

> Clientes so podem criar pets com `owner_id == seu proprio id`.

**Shape de resposta `Pet`:**

```json
{
  "id": 1,
  "name": "Thor",
  "breed": "Labrador",
  "sex": "M",
  "size": "grande",
  "weight": 28.50,
  "health_notes": "Sem restricoes",
  "category_id": 1,
  "owner_id": 1,
  "tags": [
    { "id": 1, "name": "idoso", "description": "Pet com idade avancada" }
  ]
}
```

---

### 6.5 Services

Prefixo: `/service` — escrita exige funcionario ou superuser.

| Metodo | Rota | Auth | Retorno |
|---|---|---|---|
| `POST` | `/service` | Funcionario/superuser | `201` + `Service` |
| `GET` | `/service/services` | nao | `200` + `Service[]` |
| `GET` | `/service/{id}` | nao | `200` + `Service` |
| `PUT` | `/service/{id}` | Funcionario/superuser | `200` + `Service` |
| `DELETE` | `/service/{id}` | Funcionario/superuser | `200` + `{message}` |

**Shape de resposta `Service`:**

```json
{ "id": 1, "name": "Banho", "description": "Banho completo com secagem", "price": 80.00 }
```

---

### 6.6 Categories

Prefixo: `/category` — escrita exige funcionario ou superuser.

| Metodo | Rota | Auth | Retorno |
|---|---|---|---|
| `POST` | `/category` | Funcionario/superuser | `201` + `Category` |
| `GET` | `/category/categories` | nao | `200` + `Category[]` |
| `GET` | `/category/{id}` | nao | `200` + `Category` |
| `PUT` | `/category/{id}` | Funcionario/superuser | `200` + `Category` |
| `DELETE` | `/category/{id}` | Funcionario/superuser | `200` + `{message}` |

> `PUT /category/{id}`: `name` e **obrigatorio**.

**Shape de resposta `Category`:**

```json
{ "id": 1, "name": "Canino", "description": "Pets do tipo cao" }
```

---

### 6.7 Tags

Prefixo: `/tag` — escrita exige funcionario ou superuser.

| Metodo | Rota | Auth | Retorno |
|---|---|---|---|
| `POST` | `/tag` | Funcionario/superuser | `201` + `Tag` |
| `GET` | `/tag/tags` | nao | `200` + `Tag[]` |
| `GET` | `/tag/{id}` | nao | `200` + `Tag` |
| `PUT` | `/tag/{id}` | Funcionario/superuser | `200` + `Tag` |
| `DELETE` | `/tag/{id}` | Funcionario/superuser | `200` + `{message}` |

> `PUT /tag/{id}`: `name` e **opcional** (diferente de category).

**Shape de resposta `Tag`:**

```json
{ "id": 1, "name": "alergico", "description": "Pet com historico de alergia" }
```

---

### 6.8 Appointments

Prefixo: `/appointment`

| Metodo | Rota | Auth | Retorno |
|---|---|---|---|
| `POST` | `/appointment` | sim | `201` + `Appointment` |
| `GET` | `/appointment/appointments` | nao | `200` + `Appointment[]` |
| `GET` | `/appointment/{id}` | nao | `200` + `Appointment` |
| `PUT` | `/appointment/{id}` | Superuser, funcionario ou dono | `200` + `Appointment` |
| `DELETE` | `/appointment/{id}` | Superuser, funcionario ou dono | `200` + `{message}` |

**Params de criacao:**

| Param | Tipo | Obrigatorio | Notas |
|---|---|---|---|
| `store_id` | int | sim | deve existir |
| `client_id` | int | sim | deve ser um cliente existente |
| `employee_id` | int | sim | deve ser funcionario da loja informada |
| `pet_id` | int | sim | deve pertencer ao `client_id` informado |
| `payment_method` | string | sim | ver tabela de valores aceitos abaixo |
| `service_ids` | int[] | sim | minimo 1; envie repetindo o param ou como array |
| `service_at` | datetime | nao | ISO 8601; default: agora |
| `status` | string | nao | ver tabela abaixo; default: `"agendado"` |
| `notes` | string | nao | max 500 caracteres |
| `online` | bool | nao | default `false`; forcado `true` se criado por cliente |

> Clientes so podem criar atendimentos com `client_id == seu proprio id`.

**Valores aceitos para `payment_method`:**

| Envie | Armazenado como |
|---|---|
| `pix` | `pix` |
| `dinheiro` ou `cash` | `dinheiro` |
| `cartão de crédito`, `cartao de credito` ou `credit_card` | `cartão de crédito` |
| `cartão de débito`, `cartao de debito` ou `debit_card` | `cartão de débito` |
| `transferência bancária`, `transferencia bancaria` ou `transfer_bank` | `transferência bancária` |

**Valores aceitos para `status`:**

| Envie | Armazenado como |
|---|---|
| `agendado` ou `scheduled` | `agendado` |
| `em andamento` ou `in_progress` | `em andamento` |
| `concluído`, `concluido` ou `completed` | `concluído` |
| `cancelado`, `canceled` ou `cancelled` | `cancelado` |

**Regras de validacao:**

1. O `pet_id` deve pertencer ao `client_id`. Se nao, retorna `400`:
   ```json
   { "detail": "O pet selecionado não pertence ao cliente informado. Pet pertence ao cliente X" }
   ```
   **Implicacao no front**: filtre o dropdown de pets pelo cliente selecionado.

2. O `employee_id` deve ser funcionario da `store_id` informada. Se nao, retorna `400`.

3. `service_ids` deve conter ao menos 1 id. IDs invalidos retornam `404`.

4. Ao atualizar (`PUT`): trocar `client_id` sem trocar `pet_id` (ou vice-versa) tambem dispara a validacao de dono do pet.

**Shape de resposta `Appointment`:**

```json
{
  "id": 1,
  "final_value": 80.00,
  "service_at": "2026-02-01T10:00:00",
  "payment_method": "pix",
  "status": "concluído",
  "online": false,
  "notes": "Atendimento tranquilo",
  "store_id": 1,
  "client_id": 1,
  "employee_id": 6,
  "pet_id": 1,
  "services": [
    {
      "appointment_id": 1,
      "service_id": 1,
      "charged_value": 80.00,
      "ordered_at": "2026-02-01T10:00:00",
      "delivered_at": null,
      "notes": "Banho completo realizado"
    }
  ]
}
```

> Campos do `AppointmentService`: `ordered_at`, `delivered_at`, `notes` (nao `order_date`, `delivery_date`, `observations`).
> O campo do array e `"services"` (nao `"items"`).
> O valor total e `"final_value"` (nao `"value_final"`).
> `final_value` e calculado automaticamente; nunca calcule no front.

**Exemplo axios — criar atendimento:**

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

---

## 7. Tipos TypeScript recomendados

```ts
export type ApiError = {
  detail: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
};

export interface Client {
  user_id: number;
  client_type: string;
  cep: string;
  state: string;
  city: string;
}

export interface Employee {
  user_id: number;
  employee_name: string | null;
  employee_code: string;
  job_title: string;
  salary: number;
  hired_at: string;   // YYYY-MM-DD
  store_id: number;
}

export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  profile_type: 'cliente' | 'funcionario';
  cpf: string | null;
  cnpj: string | null;
  active: boolean;
  is_superuser: boolean;
  created_at: string;
  client_profile: Client | null;
  employee_profile: Employee | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  user: User;
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
  street: string;          // campo correto (nao "address")
  neighborhood: string;
  number: string;
  active: boolean;
  created_at: string;
  employees: Employee[];
}

export interface Tag {
  id: number;
  name: string;
  description: string | null;
}

export interface Pet {
  id: number;
  name: string;
  breed: string;
  sex: 'M' | 'F';
  size: string;
  weight: number;
  health_notes: string | null;
  category_id: number;
  owner_id: number;
  tags: Tag[];
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export interface Service {
  id: number;
  name: string;
  description: string | null;
  price: number;
}

export interface AppointmentService {
  appointment_id: number;
  service_id: number;
  charged_value: number;
  ordered_at: string;           // campo correto (nao "order_date")
  delivered_at: string | null;  // campo correto (nao "delivery_date")
  notes: string | null;         // campo correto (nao "observations")
}

export interface Appointment {
  id: number;
  final_value: number;          // campo correto (nao "value_final")
  service_at: string;
  payment_method: string;
  status: string;
  online: boolean;
  notes: string | null;
  store_id: number;
  client_id: number;
  employee_id: number;
  pet_id: number;
  services: AppointmentService[];  // campo correto (nao "items")
}
```

---

## 8. Exemplo de client HTTP completo (axios)

```ts
import axios from 'axios';

export const api = axios.create({ baseURL: 'http://127.0.0.1:8000' });

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const login = (email: string, password: string) =>
  api.post<TokenResponse>('/auth/login', { email, password }).then(r => r.data);

export const register = (payload: Partial<User> & { password: string }) =>
  api.post<TokenResponse>('/auth/register', payload).then(r => r.data);

export const me = () => api.get<User>('/auth/me').then(r => r.data);

// Users
export const listUsers = () => api.get<User[]>('/user/users').then(r => r.data);
export const getUser = (id: number) => api.get<User>(`/user/${id}`).then(r => r.data);
export const createUser = (params: Record<string, unknown>) =>
  api.post<User>('/user', null, { params }).then(r => r.data);
export const updateUser = (id: number, params: Record<string, unknown>) =>
  api.put<User>(`/user/${id}`, null, { params }).then(r => r.data);
export const deleteUser = (id: number) =>
  api.delete<{ message: string }>(`/user/${id}`).then(r => r.data);

// Pets
export const listPets = () => api.get<Pet[]>('/pet/pets').then(r => r.data);
export const getPet = (id: number) => api.get<Pet>(`/pet/${id}`).then(r => r.data);
export const createPet = (params: Record<string, unknown>) =>
  api.post<Pet>('/pet', null, { params }).then(r => r.data);
export const updatePet = (id: number, params: Record<string, unknown>) =>
  api.put<Pet>(`/pet/${id}`, null, { params }).then(r => r.data);
export const deletePet = (id: number) =>
  api.delete<{ message: string }>(`/pet/${id}`).then(r => r.data);

// Appointments
export const listAppointments = () =>
  api.get<Appointment[]>('/appointment/appointments').then(r => r.data);
export const getAppointment = (id: number) =>
  api.get<Appointment>(`/appointment/${id}`).then(r => r.data);
export const createAppointment = (params: {
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
}) => api.post<Appointment>('/appointment', null, { params }).then(r => r.data);
export const updateAppointment = (id: number, params: Record<string, unknown>) =>
  api.put<Appointment>(`/appointment/${id}`, null, { params }).then(r => r.data);
export const deleteAppointment = (id: number) =>
  api.delete<{ message: string }>(`/appointment/${id}`).then(r => r.data);
```

---

## 9. Checklist de integracao

- [ ] Configurar `baseURL` para `http://127.0.0.1:8000`
- [ ] Interceptor de request para injetar `Authorization: Bearer <token>`
- [ ] Tratar erros lendo `error.response.data.detail` (pode ser string ou array)
- [ ] Tipar campos de data/hora como `string` (ISO 8601)
- [ ] Tipar campos decimais (`price`, `salary`, `weight`, `charged_value`, `final_value`) como `number`
- [ ] Usar `street` (nao `address`) na interface `Store`
- [ ] Usar `services` (nao `items`) na interface `Appointment`
- [ ] Usar `final_value` (nao `value_final`) na interface `Appointment`
- [ ] Usar `ordered_at`/`delivered_at`/`notes` (nao `order_date`/`delivery_date`/`observations`) em `AppointmentService`
- [ ] Filtrar pets por cliente ao montar formulario de atendimento
- [ ] Ao enviar listas (`service_ids`, `tag_ids`), usar `params` do axios (serializa como array automaticamente)
- [ ] Usar `/docs` para validar contratos durante desenvolvimento

---

## 10. Fontes do contrato (backend)

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
- `app/services/appointment_service.py`
- `app/core/security.py`
