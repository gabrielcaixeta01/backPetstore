from fastapi import HTTPException
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from app.schemas.models import Category, ClientModel, Pet, Tag


VALID_SEX_VALUES = {
    "M": "M",
    "F": "F",
    "macho": "M",
    "femea": "F",
    "fêmea": "F",
}


def _normalize_sex(sex: str | None) -> str | None:
    if sex is None:
        return None
    return VALID_SEX_VALUES.get(sex.strip().lower(), None)


def _normalize_tag_ids(tag_ids: list[int | str] | None) -> list[int] | None:
    if tag_ids is None:
        return None

    normalized_ids: list[int] = []
    for tag_id in tag_ids:
        if isinstance(tag_id, int):
            normalized_ids.append(tag_id)
            continue

        for chunk in tag_id.split(","):
            value = chunk.strip()
            if not value:
                continue
            if not value.isdigit():
                raise HTTPException(status_code=422, detail=f"tag_ids inválido: {value}")
            normalized_ids.append(int(value))

    return list(dict.fromkeys(normalized_ids))


def _load_tags(db: Session, tag_ids: list[int | str] | None) -> list[Tag] | None:
    normalized_tag_ids = _normalize_tag_ids(tag_ids)
    if normalized_tag_ids is None:
        return None
    if not normalized_tag_ids:
        return []

    tags = db.query(Tag).filter(Tag.id.in_(normalized_tag_ids)).all()
    tags_by_id = {tag.id: tag for tag in tags}
    missing_tag_ids = [tag_id for tag_id in normalized_tag_ids if tag_id not in tags_by_id]
    if missing_tag_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Tag(s) não encontrada(s): {', '.join(str(tag_id) for tag_id in missing_tag_ids)}",
        )

    return [tags_by_id[tag_id] for tag_id in normalized_tag_ids]


def create_pet(
    db: Session,
    name: str,
    breed: str,
    sex: str,
    size: str,
    weight: Decimal,
    category_id: int,
    owner_id: int,
    health_notes: str | None = None,
    tag_ids: list[int | str] | None = None,
):
    name = name.strip() if name else name

    if not name:
        raise HTTPException(status_code=400, detail="Nome do pet é obrigatório")

    if len(name) < 2 or len(name) > 120:
        raise HTTPException(status_code=400, detail="Nome do pet deve conter entre 2 e 120 caracteres")
    
    if not breed:
        raise HTTPException(status_code=400, detail="Raça do pet é obrigatória")

    if len(breed) > 80:
        raise HTTPException(status_code=400, detail="Raça do pet deve conter no máximo 80 caracteres")
    
    normalized_sex = _normalize_sex(sex)
    if normalized_sex is None:
        raise HTTPException(status_code=400, detail="Sexo do pet inválido. Use 'M', 'F', 'macho' ou 'femea'")

    if not size:
        raise HTTPException(status_code=400, detail="Tamanho do pet é obrigatório")

    if weight is None:
        raise HTTPException(status_code=400, detail="Peso do pet é obrigatório")
    if weight <= 0:
        raise HTTPException(status_code=400, detail="Peso do pet deve ser maior que zero")
    
    if health_notes and len(health_notes) > 500:
        raise HTTPException(status_code=400, detail="Anotações de saúde devem conter no máximo 500 caracteres")
    
    if category_id is None:
        raise HTTPException(status_code=400, detail="Categoria do pet é obrigatória")

    if owner_id is None:
        raise HTTPException(status_code=400, detail="Dono do pet é obrigatório para criar pet")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Categoria com id {category_id} não encontrada")

    owner = db.query(ClientModel).filter(ClientModel.user_id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail=f"Cliente (dono) com id {owner_id} não encontrado")

    loaded_tags = _load_tags(db, tag_ids)

    duplicated_pet = (
        db.query(Pet)
        .filter(Pet.owner_id == owner_id, func.lower(Pet.name) == name.lower())
        .first()
    )
    if duplicated_pet:
        raise HTTPException(status_code=400, detail="Este dono já possui um pet com esse nome")

    db_pet = Pet(
        name=name,
        breed=breed,
        sex=normalized_sex,
        size=size,
        weight=weight,
        health_notes=health_notes,
        category_id=category_id,
        owner_id=owner_id,
    )

    if loaded_tags is not None:
        db_pet.tags = loaded_tags

    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return get_pet(db, db_pet.id)


def get_pet(db: Session, pet_id: int):
    pet = (
        db.query(Pet)
        .options(selectinload(Pet.tags))
        .filter(Pet.id == pet_id)
        .first()
    )
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    return pet


def update_pet(
    db: Session,
    pet_id: int,
    name: str | None = None,
    breed: str | None = None,
    sex: str | None = None,
    size: str | None = None,
    weight: Decimal | None = None,
    health_notes: str | None = None,
    category_id: int | None = None,
    owner_id: int | None = None,
    tag_ids: list[int | str] | None = None,
):
    pet = get_pet(db, pet_id)
    loaded_tags = _load_tags(db, tag_ids)

    if name is not None:
        name = name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Nome do pet é obrigatório")
        if len(name) < 2 or len(name) > 120:
            raise HTTPException(status_code=400, detail="Nome do pet deve conter entre 2 e 120 caracteres")
        pet.name = name

    if not pet.name:
        raise HTTPException(status_code=400, detail="Nome do pet é obrigatório")

    if len(pet.name) < 2 or len(pet.name) > 120:
        raise HTTPException(status_code=400, detail="Nome do pet deve conter entre 2 e 120 caracteres")

    if breed is not None:
        if not breed:
            raise HTTPException(status_code=400, detail="Raça do pet é obrigatória")
        if len(breed) > 80:
            raise HTTPException(status_code=400, detail="Raça do pet deve conter no máximo 80 caracteres")
        pet.breed = breed

    if not pet.breed:
        raise HTTPException(status_code=400, detail="Raça do pet é obrigatória")

    if len(pet.breed) > 80:
        raise HTTPException(status_code=400, detail="Raça do pet deve conter no máximo 80 caracteres")

    if sex is not None:
        normalized_sex = _normalize_sex(sex)
        if normalized_sex is None:
            raise HTTPException(status_code=400, detail="Sexo do pet inválido. Use 'M', 'F', 'macho' ou 'femea'")
        pet.sex = normalized_sex

    if size is not None:
        if not size:
            raise HTTPException(status_code=400, detail="Tamanho do pet é obrigatório")
        pet.size = size

    if not pet.size:
        raise HTTPException(status_code=400, detail="Tamanho do pet é obrigatório")

    if weight is not None:
        if weight <= 0:
            raise HTTPException(status_code=400, detail="Peso do pet deve ser maior que zero")
        pet.weight = weight

    if pet.weight is None:
        raise HTTPException(status_code=400, detail="Peso do pet é obrigatório")
    if pet.weight <= 0:
        raise HTTPException(status_code=400, detail="Peso do pet deve ser maior que zero")

    if health_notes is not None:
        if len(health_notes) > 500:
            raise HTTPException(status_code=400, detail="Anotações de saúde devem conter no máximo 500 caracteres")
        pet.health_notes = health_notes

    if pet.health_notes and len(pet.health_notes) > 500:
        raise HTTPException(status_code=400, detail="Anotações de saúde devem conter no máximo 500 caracteres")

    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Categoria com id {category_id} não encontrada")
        pet.category_id = category_id

    if owner_id is not None:
        owner = db.query(ClientModel).filter(ClientModel.user_id == owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail=f"Cliente (dono) com id {owner_id} não encontrado")
        pet.owner_id = owner_id

    if pet.category_id is None:
        raise HTTPException(status_code=400, detail="Categoria do pet é obrigatória")

    if pet.owner_id is None:
        raise HTTPException(status_code=400, detail="Dono do pet é obrigatório")

    duplicated_pet = (
        db.query(Pet)
        .filter(
            Pet.id != pet_id,
            Pet.owner_id == pet.owner_id,
            func.lower(Pet.name) == pet.name.lower(),
        )
        .first()
    )
    if duplicated_pet:
        raise HTTPException(status_code=400, detail="Este dono já possui um pet com esse nome")

    if loaded_tags is not None:
        pet.tags = loaded_tags

    db.commit()
    db.refresh(pet)
    return get_pet(db, pet.id)


def delete_pet(db: Session, pet_id: int):
    pet = get_pet(db, pet_id)
    db.delete(pet)
    db.commit()


def list_pets( db: Session) -> list[Pet]:
    return db.query(Pet).options(selectinload(Pet.tags)).order_by(Pet.id.desc()).all()

