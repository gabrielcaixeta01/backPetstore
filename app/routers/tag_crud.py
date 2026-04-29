from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.schemas import Tag
from app.database import get_db
from sqlalchemy.orm import Session
from app.services import tag_service
from app.schemas.models import UserModel
from app.core.security import get_current_active_user

router = APIRouter(prefix="/tag", tags=["CRUD de Tags"])

@router.post("", status_code=201, response_model=Tag)
def create_tag(
    name: str = Query(..., min_length=2, max_length=80),
    description: str | None = Query(None, max_length=255),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem criar tags")
    created_tag = tag_service.create_tag(db=db, name=name, description=description)
    return created_tag


@router.get("/tags", response_model=list[Tag])
def list_tags(db: Session = Depends(get_db)):
    return tag_service.list_tags(db)


@router.get("/{id}", response_model=Tag)
def get_tag(id: int, db: Session = Depends(get_db)):
    return tag_service.get_tag(db, id)

@router.put("/{id}", response_model=Tag)
def update_tag(
    id: int,
    name: str | None = Query(None, min_length=2, max_length=80),
    description: str | None = Query(None, max_length=255),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem atualizar tags")
    updated_tag = tag_service.update_tag(db=db, tag_id=id, name=name, description=description)
    return updated_tag



@router.delete("/{id}", status_code=200, response_model=dict)
def delete_tag( id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)) -> dict:
    if not (getattr(current_user, "profile_type", None) == "funcionario" or getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=403, detail="Apenas funcionários ou superusers podem deletar tags")
    tag_service.delete_tag(db, id)
    return {"message": "Tag deletada com sucesso"}