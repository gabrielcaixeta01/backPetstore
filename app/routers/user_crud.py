from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import user_service
from app.schemas.schemas import User
from datetime import date, datetime
from decimal import Decimal
from app.core.security import get_current_active_user

router = APIRouter(prefix="/user", tags=["CRUD de Usuários"])


@router.post("", status_code=201, response_model=User)
def create_user(
    name: str = Query(...),
    email: str = Query(...),
    password: str = Query(...),
    phone: str = Query(...),
    profile_type: str = Query(...),
    cpf: str | None = Query(None),
    cnpj: str | None = Query(None),
    active: bool = Query(True),
    is_superuser: bool = Query(False),
    created_at: datetime | None = Query(None),
    client_type: str | None = Query(None),
    cep: str | None = Query(None),
    state: str | None = Query(None),
    city: str | None = Query(None),
    employee_code: str | None = Query(None),
    job_title: str | None = Query(None),
    salary: Decimal | None = Query(None),
    hired_at: date | None = Query(None),
    store_id: int | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
    

    
    created_user = user_service.create_user(
        db=db,
        name=name,
        password=password,
        email=email,
        phone=phone,
        profile_type=profile_type,
        cpf=cpf,
        cnpj=cnpj,
        active=active,
        is_superuser=is_superuser,
        created_at=created_at,
        client_type=client_type,
        cep=cep,
        state=state,
        city=city,
        employee_code=employee_code,
        job_title=job_title,
        salary=salary,
        hired_at=hired_at,
        store_id=store_id,
    )
    return created_user


@router.get("/users", response_model=list[User])
def list_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return user_service.get_user(db, user_id)


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    name: str | None = Query(None),
    email: str | None = Query(None),
    password: str | None = Query(None),
    phone: str | None = Query(None),
    profile_type: str | None = Query(None),
    cpf: str | None = Query(None),
    cnpj: str | None = Query(None),
    active: bool | None = Query(None),
    is_superuser: bool | None = Query(None),
    client_type: str | None = Query(None),
    cep: str | None = Query(None),
    state: str | None = Query(None),
    city: str | None = Query(None),
    employee_code: str | None = Query(None),
    job_title: str | None = Query(None),
    salary: Decimal | None = Query(None),
    hired_at: date | None = Query(None),
    store_id: int | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
   
    updated_user = user_service.update_user(
        db=db,
        user_id=user_id,
        name=name,
        password=password,
        email=email,
        phone=phone,
        profile_type=profile_type,
        cpf=cpf,
        cnpj=cnpj,
        active=active,
        is_superuser=is_superuser,
        client_type=client_type,
        cep=cep,
        state=state,
        city=city,
        employee_code=employee_code,
        job_title=job_title,
        salary=salary,
        hired_at=hired_at,
        store_id=store_id,
    )
    return updated_user


@router.delete("/{user_id}", status_code=200, response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    user_service.delete_user(db, user_id)
    return {"message": "Usuário deletado com sucesso"}
