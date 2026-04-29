from fastapi import APIRouter, Depends, Query, HTTPException
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import service_service
from app.schemas.schemas import Service
from app.schemas.models import UserModel
from app.core.security import get_current_active_user

router = APIRouter(prefix="/service", tags=["CRUD de Serviços"])


@router.post("", status_code=201, response_model=Service)
def create_service(
    name: str = Query(..., min_length=2, max_length=120),
    description: str | None = Query(None, max_length=500),
    price: Decimal | None = Query(None, ge=0),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem criar serviços")
    created = service_service.create_service(
        db=db,
        name=name,
        description=description,
        price=price,
    )
    return created


@router.get("/services", response_model=list[Service])
def list_services(db: Session = Depends(get_db)) -> list[Service]:
    return service_service.list_services(db)


@router.get("/{id}", response_model=Service)
def get_service(id: int, db: Session = Depends(get_db)) -> Service:
   return service_service.get_service(db, id)


@router.put("/{id}", response_model=Service)
def update_service(
    id: int,
    name: str | None = Query(None, min_length=2, max_length=120),
    description: str | None = Query(None, max_length=500),
    price: Decimal | None = Query(None, ge=0),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Service:
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem atualizar serviços")
    updated_service = service_service.update_service(
        db=db,
        service_id=id,
        name=name,
        description=description,
        price=price,
    )
    return updated_service


@router.delete("/{id}", status_code=200, response_model=dict)
def delete_service(id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)) -> dict:
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem deletar serviços")
    service_service.delete_service(db, id)
    return {"message": "Serviço deletado com sucesso"}