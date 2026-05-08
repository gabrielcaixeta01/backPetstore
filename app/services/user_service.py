from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.security import hash_password
from app.schemas.models import ClientModel, EmployeeModel, Pet, Store, UserModel


ALLOWED_PROFILE_TYPES = {"cliente", "funcionario"}

PROFILE_TYPE_ALIASES = {
    "cliente": "cliente",
    "client": "cliente",
    "funcionario": "funcionario",
    "employee": "funcionario",
}

CLIENT_TYPE_ALIASES = {
    "pessoa fisica": "pessoa_fisica",
    "pessoa física": "pessoa_fisica",
    "pessoa_fisica": "pessoa_fisica",
    "pessoa juridica": "pessoa_juridica",
    "pessoa jurídica": "pessoa_juridica",
    "pessoa_juridica": "pessoa_juridica",
}


def _normalize_profile_type(profile_type: str | None) -> str | None:
    if profile_type is None:
        return None
    return PROFILE_TYPE_ALIASES.get(profile_type.strip().lower())


def _normalize_client_type(client_type: str | None) -> str | None:
    if client_type is None:
        return None
    return CLIENT_TYPE_ALIASES.get(client_type.strip().lower())



def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    phone: str,
    profile_type: str,
    cpf: str | None = None,
    cnpj: str | None = None,
    active: bool = True,
    is_superuser: bool = False,
    created_at: datetime | None = None,
    client_type: str | None = None,
    cep: str | None = None,
    state: str | None = None,
    city: str | None = None,
    employee_code: str | None = None,
    job_title: str | None = None,
    salary: Decimal | None = None,
    hired_at: date | None = None,
    store_id: int | None = None,
):
   
    name = name.strip() if name else name
    normalized_profile_type = _normalize_profile_type(profile_type)
    normalized_client_type = _normalize_client_type(client_type)

    if normalized_profile_type not in ALLOWED_PROFILE_TYPES:
        raise HTTPException(status_code=400, detail="Perfil inválido. Use 'cliente'/'client' ou 'funcionario'/'employee'")

    if is_superuser and normalized_profile_type != "funcionario":
        raise HTTPException(status_code=400, detail="Superusers devem ter perfil 'funcionario'")

    if not name:
        raise HTTPException(status_code=400, detail="Nome do usuário é obrigatório")
    
    if len(name) < 2 or len(name) > 120:
        raise HTTPException(status_code=400, detail="Nome do usuário deve conter entre 2 e 120 caracteres")
    
    if phone and len(phone) > 20:
        raise HTTPException(status_code=400, detail="Número de telefone deve conter no máximo 20 caracteres")

    if email and len(email) > 255:
        raise HTTPException(status_code=400, detail="E-mail deve conter no máximo 255 caracteres")

    if cpf is not None and len(cpf) > 14:
        raise HTTPException(status_code=400, detail="CPF deve conter no máximo 14 caracteres")

    if cnpj is not None and len(cnpj) > 18:
        raise HTTPException(status_code=400, detail="CNPJ deve conter no máximo 18 caracteres")
    
    if client_type is not None and normalized_client_type is None:
        raise HTTPException(
            status_code=400,
            detail="Tipo de cliente inválido. Use 'pessoa_fisica' ou 'pessoa_juridica'",
        )
   
    exists_email = db.query(UserModel).filter(UserModel.email == email).first()
    if exists_email:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    if cpf is not None and cnpj is not None:
        raise HTTPException(status_code=400, detail="CPF e CNPJ não podem ser preenchidos ao mesmo tempo")
    
    if cpf is None and cnpj is None:
        raise HTTPException(status_code=400, detail="CPF ou CNPJ deve ser preenchido")

    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve conter ao menos 6 caracteres")

    db_user = UserModel(
        name=name,
        email=email,
        password_hash=hash_password(password),
        phone=phone,
        profile_type=normalized_profile_type,
        cpf=cpf,
        cnpj=cnpj,
        active=active,
        is_superuser=is_superuser,
        created_at=created_at or datetime.utcnow(),
    )


    db.add(db_user)
    db.flush()

    if normalized_profile_type == "cliente":
        if any(value is not None for value in [employee_code, job_title, salary, hired_at, store_id]):
            raise HTTPException(
                status_code=400,
                detail="Campos de funcionário devem ser nulos quando o perfil for 'cliente'",
            )
        db.add(
            ClientModel(
                user_id=db_user.id,
                client_type=normalized_client_type or "pessoa_fisica",
                cep=cep or "00000-000",
                state=state or "SP",
                city=city or "São Paulo",
            )
        )

    if normalized_profile_type == "funcionario":
        if any(value is not None for value in [client_type, cep, state, city]):
            raise HTTPException(
                status_code=400,
                detail="Campos de cliente devem ser nulos quando o perfil for 'funcionario'",
            )

        missing_employee_fields = []
        if not employee_code:
            missing_employee_fields.append("employee_code")
        if not job_title:
            missing_employee_fields.append("job_title")
        if salary is None:
            missing_employee_fields.append("salary")
        if hired_at is None:
            missing_employee_fields.append("hired_at")
        if store_id is None:
            missing_employee_fields.append("store_id")
        if missing_employee_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Campos obrigatórios para funcionário ausentes: {', '.join(missing_employee_fields)}",
            )

        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail=f"Loja com id {store_id} não encontrada")

        db.add(
            EmployeeModel(
                user_id=db_user.id,
                employee_code=employee_code,
                job_title=job_title,
                salary=salary,
                hired_at=hired_at,
                store_id=store_id,
            )
        )

    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    user = (
        db.query(UserModel)
        .options(joinedload(UserModel.client_profile), joinedload(UserModel.employee_profile))
        .filter(UserModel.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user




def update_user(
        db: Session,
        user_id: int,
        name: str | None = None,
        email: str | None = None,
    password: str | None = None,
        phone: str | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
        active: bool | None = None,
        is_superuser: bool | None = None,
        client_type: str | None = None,
        cep: str | None = None,
        state: str | None = None,
        city: str | None = None,
        employee_code: str | None = None,
        job_title: str | None = None,
        salary: Decimal | None = None,
        hired_at: date | None = None,
        store_id: int | None = None,
    ):

    user = get_user(db, user_id=user_id)
    normalized_client_type = _normalize_client_type(client_type)

    if name is not None and not name.strip():
        raise HTTPException(status_code=400, detail="Nome do usuário é obrigatório")

    if name is not None and len(name) > 120:
        raise HTTPException(status_code=400, detail="Nome do usuário deve conter no máximo 120 caracteres")

    if email is not None and len(email) > 255:
        raise HTTPException(status_code=400, detail="E-mail deve conter no máximo 255 caracteres")

    if phone is not None and len(phone) > 20:
        raise HTTPException(status_code=400, detail="Número de telefone deve conter no máximo 20 caracteres")

    if cpf is not None and len(cpf) > 14:
        raise HTTPException(status_code=400, detail="CPF deve conter no máximo 14 caracteres")

    if cnpj is not None and len(cnpj) > 18:
        raise HTTPException(status_code=400, detail="CNPJ deve conter no máximo 18 caracteres")

    if client_type is not None and normalized_client_type is None:
        raise HTTPException(
            status_code=400,
            detail="Tipo de cliente inválido. Use 'pessoa_fisica' ou 'pessoa_juridica'",
        )

    if email is not None:
        exists_email = (db.query(UserModel).filter(UserModel.email == email, UserModel.id != user_id).first())
        if exists_email:
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    if password is not None and len(password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve conter ao menos 6 caracteres")

    if cpf is not None and cnpj is not None:
        raise HTTPException(status_code=400, detail="CPF e CNPJ não podem ser preenchidos ao mesmo tempo")

    resulting_cpf = cpf if cpf is not None else user.cpf
    resulting_cnpj = cnpj if cnpj is not None else user.cnpj
    if resulting_cpf is not None and resulting_cnpj is not None:
        raise HTTPException(status_code=400, detail="CPF e CNPJ não podem ser preenchidos ao mesmo tempo")

    if user.profile_type == "cliente" and any(value is not None for value in [employee_code, job_title, salary, hired_at, store_id]):
        raise HTTPException(
            status_code=400,
            detail="Campos de funcionário devem ser nulos quando o perfil for 'cliente'",
        )

    if user.profile_type == "funcionario" and any(value is not None for value in [client_type, cep, state, city]):
        raise HTTPException(
            status_code=400,
            detail="Campos de cliente devem ser nulos quando o perfil for 'funcionario'",
        )

    for field, value in {
        "name": name,
        "email": email,
        "phone": phone,
        "cpf": cpf,
        "cnpj": cnpj,
        "active": active,
        "is_superuser": is_superuser,
    }.items():
        if value is not None:
            setattr(user, field, value)

    if password is not None:
        user.password_hash = hash_password(password)

    if user.profile_type == "cliente":
        if user.employee_profile is not None:
            db.delete(user.employee_profile)
            user.employee_profile = None

        if user.client_profile is None:
            missing_client_fields = []
            if not normalized_client_type:
                missing_client_fields.append("client_type")
            if not cep:
                missing_client_fields.append("cep")
            if not state:
                missing_client_fields.append("state")
            if not city:
                missing_client_fields.append("city")
            if missing_client_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campos obrigatórios para criar perfil de cliente: {', '.join(missing_client_fields)}",
                )
            user.client_profile = ClientModel(
                user_id=user.id,
                client_type=normalized_client_type,
                cep=cep,
                state=state,
                city=city,
            )
        else:
            if normalized_client_type is not None:
                user.client_profile.client_type = normalized_client_type
            if cep is not None:
                user.client_profile.cep = cep
            if state is not None:
                user.client_profile.state = state
            if city is not None:
                user.client_profile.city = city

    if user.profile_type == "funcionario":
        if user.client_profile is not None:
            db.delete(user.client_profile)
            user.client_profile = None

        if user.employee_profile is None:
            missing_employee_fields = []
            if not employee_code:
                missing_employee_fields.append("employee_code")
            if not job_title:
                missing_employee_fields.append("job_title")
            if salary is None:
                missing_employee_fields.append("salary")
            if hired_at is None:
                missing_employee_fields.append("hired_at")
            if store_id is None:
                missing_employee_fields.append("store_id")
            if missing_employee_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campos obrigatórios para criar perfil de funcionário: {', '.join(missing_employee_fields)}",
                )
            store = db.query(Store).filter(Store.id == store_id).first()
            if not store:
                raise HTTPException(status_code=404, detail=f"Loja com id {store_id} não encontrada")
            user.employee_profile = EmployeeModel(
                user_id=user.id,
                employee_code=employee_code,
                job_title=job_title,
                salary=salary,
                hired_at=hired_at,
                store_id=store_id,
            )
        else:
            if employee_code is not None:
                user.employee_profile.employee_code = employee_code
            if job_title is not None:
                user.employee_profile.job_title = job_title
            if salary is not None:
                user.employee_profile.salary = salary
            if hired_at is not None:
                user.employee_profile.hired_at = hired_at
            if store_id is not None:
                store = db.query(Store).filter(Store.id == store_id).first()
                if not store:
                    raise HTTPException(status_code=404, detail=f"Loja com id {store_id} não encontrada")
                user.employee_profile.store_id = store_id

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id=user_id)
    
    # Deletar todos os pets do cliente se for um cliente
    if user.profile_type == "cliente":
        db.query(Pet).filter(Pet.owner_id == user_id).delete(synchronize_session=False)
    
    db.delete(user)
    db.commit()

def list_users(db: Session) -> list[UserModel]:
    return (
        db.query(UserModel)
        .options(joinedload(UserModel.client_profile), joinedload(UserModel.employee_profile))
        .all()
    )