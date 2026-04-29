from datetime import datetime
import re
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.schemas.models import EmployeeModel, Store


def create_store(
    db: Session,
    name: str,
    cnpj: str,
    phone: str | None = None,
    email: str | None = None,
    cep: str | None = None,
    city: str | None = None,
    state: str | None = None,
    street: str | None = None,
    neighborhood: str | None = None,
    number: str | None = None,
    active: bool = True,
    created_at: datetime | None = None,
):
    name = name.strip() if name else name

    required_fields = {
        "name": name,
        "cnpj": cnpj,
        "phone": phone,
        "email": email,
        "city": city,
        "state": state,
        "street": street,
        "neighborhood": neighborhood,
        "number": number,
    }
    missing = [field for field, value in required_fields.items() if value in (None, "")]
    if missing:
        raise HTTPException(status_code=400, detail=f"Campos obrigatórios ausentes: {', '.join(missing)}")

    exists_name = db.query(Store).filter(Store.name == name).first()
    exists_cnpj = db.query(Store).filter(Store.cnpj == cnpj).first()
    exists_email = db.query(Store).filter(Store.email == email).first()

    if exists_name:
        raise HTTPException(status_code=400, detail="Loja já existe com esse nome")
    if exists_cnpj:
        raise HTTPException(status_code=400, detail="Loja já existe com esse CNPJ")
    if exists_email:
        raise HTTPException(status_code=400, detail="Loja já existe com esse email")

    if len(name.strip()) < 2 or len(name.strip()) > 120:
        raise HTTPException(status_code=400, detail="Nome da loja deve conter entre 2 e 120 caracteres")
    
    if phone and len(phone) > 20:
        raise HTTPException(status_code=400, detail="Telefone da loja deve conter no máximo 20 caracteres")
    if email and len(email) > 255:
        raise HTTPException(status_code=400, detail="Email da loja deve conter no máximo 255 caracteres")
    
    if cep and not re.fullmatch(r"\d{5}-?\d{3}", cep):
        raise HTTPException(status_code=400, detail="CEP da loja inválido. Use 8 dígitos com ou sem hífen")
    if city and len(city) > 120:
        raise HTTPException(status_code=400, detail="Cidade da loja deve conter no máximo 120 caracteres")
    if state and len(state) > 2:
        raise HTTPException(status_code=400, detail="Estado da loja deve conter no máximo 2 caracteres")
    if street and len(street) > 255:
        raise HTTPException(status_code=400, detail="Rua da loja deve conter no máximo 255 caracteres")
    if neighborhood and len(neighborhood) > 120:
        raise HTTPException(status_code=400, detail="Bairro da loja deve conter no máximo 120 caracteres")
    if number and len(number) > 20:
        raise HTTPException(status_code=400, detail="Número da loja deve conter no máximo 20 caracteres")
    
    db_store = Store(
        name=name,
        cnpj=cnpj,
        phone=phone,
        email=email,
        cep=cep,
        city=city,
        state=state,
        street=street,
        neighborhood=neighborhood,
        number=number,
        active=active,
        created_at=created_at or datetime.utcnow(),
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

def get_store(db: Session, store_id: int):
    store = (
        db.query(Store)
        .options(joinedload(Store.employees).joinedload(EmployeeModel.user))
        .filter(Store.id == store_id)
        .first()
    )
    if not store:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return store

def update_store(
    db: Session,
    store_id: int,
    name: str | None = None,
    cnpj: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    cep: str | None = None,
    city: str | None = None,
    state: str | None = None,
    street: str | None = None,
    neighborhood: str | None = None,
    number: str | None = None,
    active: bool | None = None,
):

    store = get_store(db, store_id)

    if name is not None:
        name = name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Nome da loja é obrigatório")
        if len(name) < 2 or len(name) > 120:
            raise HTTPException(status_code=400, detail="Nome da loja deve conter entre 2 e 120 caracteres")

    if phone is not None and len(phone) > 20:
        raise HTTPException(status_code=400, detail="Telefone da loja deve conter no máximo 20 caracteres")
    if email is not None and len(email) > 255:
        raise HTTPException(status_code=400, detail="Email da loja deve conter no máximo 255 caracteres")
    if cep is not None and not re.fullmatch(r"\d{5}-?\d{3}", cep):
        raise HTTPException(status_code=400, detail="CEP da loja inválido. Use 8 dígitos com ou sem hífen")
    if city is not None and len(city) > 120:
        raise HTTPException(status_code=400, detail="Cidade da loja deve conter no máximo 120 caracteres")
    if state is not None and len(state) > 2:
        raise HTTPException(status_code=400, detail="Estado da loja deve conter no máximo 2 caracteres")
    if street is not None and len(street) > 255:
        raise HTTPException(status_code=400, detail="Rua da loja deve conter no máximo 255 caracteres")
    if neighborhood is not None and len(neighborhood) > 120:
        raise HTTPException(status_code=400, detail="Bairro da loja deve conter no máximo 120 caracteres")
    if number is not None and len(number) > 20:
        raise HTTPException(status_code=400, detail="Número da loja deve conter no máximo 20 caracteres")

    for field, value in {
        "name": name,
        "cnpj": cnpj,
        "phone": phone,
        "email": email,
        "cep": cep,
        "city": city,
        "state": state,
        "street": street,
        "neighborhood": neighborhood,
        "number": number,
        "active": active,
    }.items():
        if value is not None:
            setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store_id: int):
    store = get_store(db, store_id)
    db.delete(store)
    db.commit()
   


def list_stores(db: Session):
    return db.query(Store).options(joinedload(Store.employees).joinedload(EmployeeModel.user)).all()