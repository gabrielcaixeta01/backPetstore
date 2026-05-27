from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import pet_service
from app.schemas.schemas import Pet
from app.schemas.models import UserModel
from app.core.security import get_current_active_user
from decimal import Decimal

router = APIRouter(prefix="/pet", tags=["CRUD de Pets"])


@router.post("", status_code=201, response_model=Pet)
def create_pet(
    name: str = Query(...),
    breed: str = Query(...),
    sex: str = Query(...),
    size: str = Query(...),
    weight: Decimal = Query(..., le=100),
    health_notes: str | None = Query(None),
    category_id: int = Query(...),
    owner_id: int = Query(...),
    tag_ids: list[int] | None = Query(None),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if getattr(current_user, "profile_type", None) == "cliente" and owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Clientes só podem criar pets para si mesmos")

    created_pet = pet_service.create_pet(
        db=db,
        name=name,
        breed=breed,
        sex=sex,
        size=size,
        weight=weight,
        health_notes=health_notes,
        category_id=category_id,
        owner_id=owner_id,
        tag_ids=tag_ids,
    )
    return created_pet


@router.get("/pets", response_model=list[Pet])
def list_pets(db: Session = Depends(get_db)):
    return pet_service.list_pets(db)


@router.get("/{pet_id}", response_model=Pet)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    return pet_service.get_pet(db, pet_id)

@router.put("/{pet_id}", response_model=Pet)
def update_pet(
    pet_id: int,
    name: str | None = Query(None),
    breed: str | None = Query(None),
    sex: str | None = Query(None),
    size: str | None = Query(None),
    weight: Decimal | None = Query(None, le=100),
    health_notes: str | None = Query(None),
    category_id: int | None = Query(None),
    owner_id: int | None = Query(None),
    tag_ids: list[str] | None = Query(None),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    pet = pet_service.get_pet(db, pet_id)
    if not (current_user.is_superuser or current_user.profile_type == "funcionario" or pet.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este pet")

    updated_pet = pet_service.update_pet(
        db=db,
        pet_id=pet_id,
        name=name,
        breed=breed,
        sex=sex,
        size=size,
        weight=weight,
        health_notes=health_notes,
        category_id=category_id,
        owner_id=owner_id,
        tag_ids=tag_ids,
    )
    return updated_pet

@router.delete("/{pet_id}", status_code=200, response_model=dict)
def delete_pet(pet_id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)):
    pet = pet_service.get_pet(db, pet_id)
    if not (current_user.is_superuser or current_user.profile_type == "funcionario" or pet.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este pet")
    pet_service.delete_pet(db, pet_id)
    return {"message": "Pet deletado com sucesso"}