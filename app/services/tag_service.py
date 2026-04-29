from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.models import Tag


def create_tag(db: Session, name: str, description: str | None = None):
    name = name.strip() if name else name
    exists = db.query(Tag).filter(Tag.name == name).first()

    if exists:
        raise HTTPException(status_code=400, detail="Tag já existe")
    
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Nome deve ter 2 ou mais caracteres")
    if len(name) > 80:
        raise HTTPException(status_code=400, detail="Nome deve ter no máximo 80 caracteres")
    
    if description and len(description) > 255:
        raise HTTPException(status_code=400, detail="Descrição deve ter no máximo 255 caracteres")
    
    db_tag = Tag(name=name, description=description )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_tag(db: Session, tag_id: int):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag não encontrada")
    return tag

def update_tag(db: Session, tag_id: int, name: str, description: str | None = None):
    tag = get_tag(db, tag_id)

    if name is not None:
        name = name.strip()
        if len(name) < 2:
            raise HTTPException(status_code=400, detail="Nome deve ter 2 ou mais caracteres")
        if len(name) > 80:
            raise HTTPException(status_code=400, detail="Nome deve ter no máximo 80 caracteres")
        if db.query(Tag).filter(Tag.name == name, Tag.id != tag_id).first():
            raise HTTPException(status_code=400, detail="Outra tag já existe com esse nome")
        tag.name = name
    if description is not None:
        if len(description) > 255:
            raise HTTPException(status_code=400, detail="Descrição deve ter no máximo 255 caracteres")
        tag.description = description

    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int):
    tag = get_tag(db, tag_id)
    db.delete(tag)
    db.commit()
    

def list_tags(db: Session):
    return db.query(Tag).all()