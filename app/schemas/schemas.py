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
    name: str = Field(min_length=2, max_length=120)
    cnpj: str = Field(min_length=14, max_length=18)
    phone: str = Field(max_length=20)
    email: str = Field(max_length=255)
    cep: str = Field(max_length=9)
    city: str = Field(max_length=120)
    state: str = Field(min_length=2, max_length=2)
    street: str = Field(max_length=255)
    neighborhood: str = Field(max_length=120)
    number: str = Field(max_length=20)
    active: bool = True


class StoreUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    cnpj: Optional[str] = Field(default=None, min_length=14, max_length=18)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    cep: Optional[str] = Field(default=None, max_length=9)
    city: Optional[str] = Field(default=None, max_length=120)
    state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    street: Optional[str] = Field(default=None, max_length=255)
    neighborhood: Optional[str] = Field(default=None, max_length=120)
    number: Optional[str] = Field(default=None, max_length=20)
    active: Optional[bool] = None


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
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(max_length=255)
    password: str
    phone: str = Field(max_length=20)
    profile_type: Literal["cliente", "funcionario"]
    cpf: Optional[str] = Field(default=None, max_length=14)
    cnpj: Optional[str] = Field(default=None, max_length=18)
    active: bool = True
    is_superuser: bool = False
    client_type: Optional[str] = Field(default=None, max_length=20)
    cep: Optional[str] = Field(default=None, max_length=9)
    state: Optional[str] = Field(default=None, max_length=2)
    city: Optional[str] = Field(default=None, max_length=120)
    employee_code: Optional[str] = Field(default=None, max_length=20)
    job_title: Optional[str] = Field(default=None, max_length=80)
    salary: Optional[Decimal] = None
    hired_at: Optional[date] = None
    store_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    profile_type: Optional[Literal["cliente", "funcionario"]] = None
    cpf: Optional[str] = Field(default=None, max_length=14)
    cnpj: Optional[str] = Field(default=None, max_length=18)
    active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    client_type: Optional[str] = Field(default=None, max_length=20)
    cep: Optional[str] = Field(default=None, max_length=9)
    state: Optional[str] = Field(default=None, max_length=2)
    city: Optional[str] = Field(default=None, max_length=120)
    employee_code: Optional[str] = Field(default=None, max_length=20)
    job_title: Optional[str] = Field(default=None, max_length=80)
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
    breed: str
    sex: str
    size: str
    weight: Decimal
    health_notes: Optional[str] = None
    category_id: int
    owner_id: int
    tags: list[Tag] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    breed: str = Field(max_length=80)
    sex: str = Field(max_length=20)
    size: str = Field(max_length=20)
    weight: Decimal = Field(gt=0, le=100, decimal_places=2)
    health_notes: Optional[str] = Field(default=None, max_length=500)
    category_id: int
    owner_id: int
    tag_ids: list[int] = Field(default_factory=list)


class PetUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    breed: Optional[str] = Field(default=None, max_length=80)
    sex: Optional[str] = Field(default=None, max_length=20)
    size: Optional[str] = Field(default=None, max_length=20)
    weight: Optional[Decimal] = Field(default=None, gt=0, le=100, decimal_places=2)
    health_notes: Optional[str] = Field(default=None, max_length=500)
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
    employee_id: Optional[int] = None
    pet_id: int
    services: List["AppointmentService"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    service_at: datetime = Field(default_factory=datetime.utcnow)
    payment_method: str
    status: str
    online: bool = False
    notes: Optional[str] = None
    store_id: int
    client_id: int
    employee_id: Optional[int] = None
    pet_id: int


class AppointmentUpdate(BaseModel):
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
