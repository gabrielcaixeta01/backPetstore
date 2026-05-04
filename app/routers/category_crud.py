from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.schemas import Category
from app.database import get_db
from sqlalchemy.orm import Session
from app.services import category_service
from app.schemas.models import UserModel
from app.core.security import get_current_active_user

router = APIRouter(prefix="/category", tags=["CRUD de Categorias"])

@router.post("", status_code=201, response_model=Category)
def create_category(
    name: str = Query(..., min_length=2, max_length=80),
    description: str | None = Query(None, max_length=255),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem criar categorias")
    created_category = category_service.create_category(db=db, name=name, description=description)
    return created_category


@router.get("/categories", response_model=list[Category])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)


@router.get("/{id}", response_model=Category)
def get_category(id: int, db: Session = Depends(get_db)):
    return category_service.get_category(db, id)

@router.put("/{id}", response_model=Category)
def update_category(
    id: int,
    name: str | None = Query(None, min_length=2, max_length=80),
    description: str | None = Query(None, max_length=255),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem atualizar categorias")
    updated_category = category_service.update_category(db=db, category_id=id, name=name, description=description)
    return updated_category



@router.delete("/{id}", status_code=200, response_model=dict)
def delete_category( id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)) -> dict:
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem deletar categorias")
    category_service.delete_category(db, id)
    return {"message": "Categoria deletada com sucesso"}