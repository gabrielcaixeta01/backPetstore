from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.schemas.models import Service


def create_service(
    db: Session,
    name: str,
    description: str | None = None,
    price: Decimal | None = None,
):
    stripped_name = name.strip()

    if not stripped_name:
        raise HTTPException(status_code=400, detail="Nome do serviço é obrigatório")
    
    if len(stripped_name) < 2 or len(stripped_name) > 120:
        raise HTTPException(status_code=400, detail="Nome do serviço deve conter entre 2 e 120 caracteres")
    
    if description and len(description) > 500:
        raise HTTPException(status_code=400, detail="Descrição do serviço deve conter no máximo 500 caracteres")

    if price is None:
        raise HTTPException(status_code=400, detail="Preço do serviço é obrigatório")
    if price < 0:
        raise HTTPException(status_code=400, detail="Preço do serviço não pode ser negativo")

    service = Service(name=stripped_name, description=description, price=price)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def get_service(db: Session, service_id: int):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return service


def update_service(
    db: Session,
    service_id: int,
    name: str | None = None,
    description: str | None = None,
    price: Decimal | None = None,
):
    service = get_service(db, service_id)

    if name is not None:
        stripped_name = name.strip()
        if not stripped_name:
            raise HTTPException(status_code=400, detail="Nome do serviço é obrigatório")
        if len(stripped_name) < 2 or len(stripped_name) > 120:
            raise HTTPException(status_code=400, detail="Nome do serviço deve conter entre 2 e 120 caracteres")
        service.name = stripped_name
    if description is not None:
        if len(description) > 500:
            raise HTTPException(status_code=400, detail="Descrição do serviço deve conter no máximo 500 caracteres")
        service.description = description
    if price is not None:
        if price < 0:
            raise HTTPException(status_code=400, detail="Preço do serviço não pode ser negativo")
        service.price = price

    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service_id: int):
    service = get_service(db, service_id)
    db.delete(service)
    db.commit()


def list_services(db: Session) -> list[Service]:
    return db.query(Service).all()