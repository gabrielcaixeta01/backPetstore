from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.models import Category


def create_category(db: Session, name: str, description: str | None = None):
    name = name.strip() if name else name
    exists = db.query(Category).filter(Category.name == name).first()

    if exists:
        raise HTTPException(status_code=400, detail="Categoria já existe")
    
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Nome deve ter 2 ou mais caracteres")
    if len(name) > 80:
        raise HTTPException(status_code=400, detail="Nome deve ter no máximo 80 caracteres")
    
    if description and len(description) > 255:
        raise HTTPException(status_code=400, detail="Descrição deve ter no máximo 255 caracteres")
    
    db_category = Category(name=name, description=description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category

def update_category(db: Session, category_id: int, name: str, description: str | None = None):
    category = get_category(db, category_id)

    if name is not None:
        name = name.strip()
        if db.query(Category).filter(Category.name == name, Category.id != category_id).first():
            raise HTTPException(status_code=400, detail="Outra categoria já existe com esse nome")
        if len(name) < 2:
            raise HTTPException(status_code=400, detail="Nome deve ter 2 ou mais caracteres")
        if len(name) > 80:
            raise HTTPException(status_code=400, detail="Nome deve ter no máximo 80 caracteres")
        
        category.name = name
    
    if description is not None:
        if len(description) > 255:
            raise HTTPException(status_code=400, detail="Descrição deve ter no máximo 255 caracteres")
        category.description = description

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    db.delete(category)
    db.commit()
    

def list_categories(db: Session):
    return db.query(Category).all()