from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class Store(BaseModel):
    id: int
    name: str
    cnpj: str
    phone: str
    email: str
    cep: str
    city: str
    state: str
    street: str
    neighborhood: str
    number: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    employees: List["Employee"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class StoreCreate(BaseModel):
    name: str
    cnpj: str
    phone: str
    email: str
    cep: str
    city: str
    state: str
    street: str
    neighborhood: str
    number: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    cnpj: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cep: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[str] = None
    active: Optional[bool] = None
    created_at: Optional[datetime] = None


class User(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    profile_type: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    client_profile: Optional["Client"] = None
    employee_profile: Optional["Employee"] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class LogoutResponse(BaseModel):
    message: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    profile_type: Literal["cliente", "funcionario"]
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    active: bool = True
    is_superuser: bool = False
    client_type: Optional[str] = None
    cep: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    employee_code: Optional[str] = None
    job_title: Optional[str] = None
    salary: Optional[Decimal] = None
    hired_at: Optional[datetime] = None
    store_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    profile_type: Optional[Literal["cliente", "funcionario"]] = None
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    client_type: Optional[str] = None
    cep: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    employee_code: Optional[str] = None
    job_title: Optional[str] = None
    salary: Optional[Decimal] = None
    hired_at: Optional[date] = None
    store_id: Optional[int] = None


class Client(BaseModel):
    user_id: int
    client_type: str
    cep: str
    state: str
    city: str

    class Config:
        from_attributes = True


class Employee(BaseModel):
    user_id: int
    employee_name: Optional[str] = None
    employee_code: str
    job_title: str
    salary: Decimal
    hired_at: date
    store_id: int

    class Config:
        from_attributes = True


Store.model_rebuild()
User.model_rebuild()


class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)


class Tag(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)


class TagUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=255)


class Pet(BaseModel):
    id: int
    name: str
    breed: Optional[str] = None
    sex: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[Decimal] = None
    health_notes: Optional[str] = None
    category_id: int
    owner_id: int
    tags: list[Tag] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PetCreate(BaseModel):
    name: str
    breed: Optional[str] = None
    sex: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[Decimal] = None
    health_notes: Optional[str] = None
    category_id: int
    owner_id: int
    tag_ids: list[int] = Field(default_factory=list)


class PetUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    sex: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[Decimal] = None
    health_notes: Optional[str] = None
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None


class Service(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal

    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Decimal = Field(ge=0)


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[Decimal] = Field(default=None, ge=0)


class Appointment(BaseModel):
    id: int
    final_value: Decimal
    service_at: datetime = Field(default_factory=datetime.utcnow)
    payment_method: str
    status: str
    online: bool = False
    notes: Optional[str] = None
    store_id: int
    client_id: int
    employee_id: int
    pet_id: int
    services: List["AppointmentService"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    final_value: Decimal
    service_at: datetime = Field(default_factory=datetime.utcnow)
    payment_method: str
    status: str
    online: bool = False
    notes: Optional[str] = None
    store_id: int
    client_id: int
    employee_id: int
    pet_id: int


class AppointmentUpdate(BaseModel):
    final_value: Optional[Decimal] = None
    service_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    online: Optional[bool] = None
    notes: Optional[str] = None
    store_id: Optional[int] = None
    client_id: Optional[int] = None
    employee_id: Optional[int] = None
    pet_id: Optional[int] = None


class AppointmentService(BaseModel):
    appointment_id: int
    service_id: int
    charged_value: Decimal
    ordered_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentServiceCreate(BaseModel):
    appointment_id: int
    service_id: int
    charged_value: Decimal
    ordered_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None


class AppointmentServiceUpdate(BaseModel):
    charged_value: Optional[Decimal] = None
    ordered_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None


Appointment.model_rebuild()
