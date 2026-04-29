from datetime import datetime, date

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.orm import relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), index=True, nullable=False)
    cnpj = Column(String(18), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    cep = Column(String(9), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(2), nullable=False)
    street = Column(String(255), nullable=False)
    neighborhood = Column(String(120), nullable=False)
    number = Column(String(20), nullable=False)

    employees = relationship("EmployeeModel", back_populates="store", passive_deletes=True)
    appointments = relationship("Appointment", back_populates="store", passive_deletes=True)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    profile_type = Column(String(20), nullable=False)
    cpf = Column(String(14))
    cnpj = Column(String(18))
    active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    client_profile = relationship("ClientModel", back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True,)
    employee_profile = relationship("EmployeeModel", back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True,)


class ClientModel(Base):
    __tablename__ = "clients"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    client_type = Column(String(20), nullable=False)
    cep = Column(String(9), nullable=False)
    state = Column(String(2), nullable=False)
    city = Column(String(120), nullable=False)

    user = relationship("UserModel", back_populates="client_profile")
    pets = relationship("Pet", back_populates="owner", passive_deletes=True)
    appointments = relationship("Appointment", back_populates="client", passive_deletes=True)


class EmployeeModel(Base):
    __tablename__ = "employees"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    employee_code = Column(String(20), nullable=False, unique=True)
    job_title = Column(String(80), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    hired_at = Column(Date, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)

    user = relationship("UserModel", back_populates="employee_profile")
    store = relationship("Store", back_populates="employees")
    appointments = relationship("Appointment", back_populates="employee", passive_deletes=True)

    @property
    def employee_name(self) -> str | None:
        return self.user.name if self.user is not None else None


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(80), index=True, unique=True, nullable=False)
    description = Column(String(255))

    pets = relationship("Pet", back_populates="category", cascade="all, delete-orphan", passive_deletes=True)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(80), index=True, unique=True, nullable=False)
    description = Column(String(255))

    pets = relationship("Pet", secondary="pet_tags", back_populates="tags")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), index=True, nullable=False)
    breed = Column(String(80), nullable=False)
    sex = Column(String(20), nullable=False)
    size = Column(String(20), nullable=False)
    weight = Column(Numeric(6, 2), nullable=False)
    health_notes = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category", back_populates="pets")
    owner = relationship("ClientModel", back_populates="pets")
    tags = relationship("Tag", secondary="pet_tags", back_populates="pets")


pet_tags = Table(
    "pet_tags",
    Base.metadata,
    Column("pet_id", Integer, ForeignKey("pets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    description = Column(String(500))
    price = Column(Numeric(10, 2), nullable=False)

    appointment_links = relationship("AppointmentService", back_populates="service", passive_deletes=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    final_value = Column(Numeric(10, 2), nullable=False)
    service_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    payment_method = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    online = Column(Boolean, nullable=False, default=False)
    notes = Column(String(500))
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.user_id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.user_id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)

    store = relationship("Store", back_populates="appointments")
    client = relationship("ClientModel", back_populates="appointments")
    employee = relationship("EmployeeModel", back_populates="appointments")
    pet = relationship("Pet", backref="appointments")
    services = relationship("AppointmentService", back_populates="appointment", cascade="all, delete-orphan")


class AppointmentService(Base):
    __tablename__ = "appointment_services"

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), primary_key=True)
    charged_value = Column(Numeric(10, 2), nullable=False)
    ordered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    notes = Column(String(500))

    appointment = relationship("Appointment", back_populates="services")
    service = relationship("Service", back_populates="appointment_links")
