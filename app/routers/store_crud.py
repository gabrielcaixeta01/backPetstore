from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import Store
from app.schemas.models import UserModel
from app.core.security import get_current_active_user
from app.services import store_service

router = APIRouter(prefix="/store", tags=["CRUD de Lojas"])


@router.post("", status_code=201, response_model=Store)
def create_store(
	name: str = Query(...),
	cnpj: str = Query(...),
	phone: str = Query(...),
	email: str = Query(...),
	active: bool = Query(True),
	created_at: datetime | None = Query(None),
	cep: str = Query(...),
	city: str = Query(...),
	state: str = Query(...),
	street: str = Query(...),
	neighborhood: str = Query(...),
	number: str = Query(...),
	current_user: UserModel = Depends(get_current_active_user),
	db: Session = Depends(get_db),
) -> Store:

	if not getattr(current_user, "is_superuser", False):
		raise HTTPException(status_code=403, detail="Apenas superusers podem criar lojas")

	return store_service.create_store(
		db=db,
		name=name,
		cnpj=cnpj,
		phone=phone,
		email=email,
		active=active,
		created_at=created_at,
		cep=cep,
		city=city,
		state=state,
		street=street,
		neighborhood=neighborhood,
		number=number,
	)


@router.get("/stores", response_model=list[Store])
def list_stores(db: Session = Depends(get_db)) -> list[Store]:
	return store_service.list_stores(db)


@router.get("/{store_id}", response_model=Store)
def get_store(store_id: int, db: Session = Depends(get_db)) -> Store:
	return store_service.get_store(db, store_id)


@router.put("/{store_id}", response_model=Store)
def update_store(
	store_id: int,
	name: str | None = Query(None),
	cnpj: str | None = Query(None),
	phone: str | None = Query(None),
	email: str | None = Query(None),
	active: bool | None = Query(None),
	cep: str | None = Query(None),
	city: str | None = Query(None),
	state: str | None = Query(None),
	street: str | None = Query(None),
	neighborhood: str | None = Query(None),
	number: str | None = Query(None),
	db: Session = Depends(get_db),
) -> Store:
	

	updated_store = store_service.update_store(
		db=db,
		store_id=store_id,
		name=name,
		cnpj=cnpj,
		phone=phone,
		email=email,
		active=active,
		cep=cep,
		city=city,
		state=state,
		street=street,
		neighborhood=neighborhood,
		number=number,
	)
	return updated_store


@router.delete("/{store_id}", status_code=200, response_model=dict)
def delete_store(store_id: int, db: Session = Depends(get_db)) -> dict:
	store_service.delete_store(db, store_id)
	return {"message": "Loja deletada com sucesso"}