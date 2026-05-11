from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import create_access_token, get_current_active_user, verify_password
from app.schemas.models import UserModel
from app.schemas.schemas import LoginRequest, LogoutResponse, TokenResponse, User, UserCreate
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="Esta conta foi desativada. Entre em contato com nossa equipe para reativá-la.",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "profile_type": user.profile_type,
            "is_superuser": user.is_superuser,
        }
    )

    return TokenResponse(access_token=access_token, user=User.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    created_user = user_service.create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        phone=payload.phone,
        profile_type=payload.profile_type,
        cpf=payload.cpf,
        cnpj=payload.cnpj,
        active=payload.active,
        is_superuser=False,
        created_at=None,
        client_type=payload.client_type,
        cep=payload.cep,
        state=payload.state,
        city=payload.city,
        employee_code=payload.employee_code,
        job_title=payload.job_title,
        salary=payload.salary,
        hired_at=payload.hired_at,
        store_id=payload.store_id,
    )

    access_token = create_access_token(
        {
            "sub": str(created_user.id),
            "email": created_user.email,
            "profile_type": created_user.profile_type,
            "is_superuser": created_user.is_superuser,
        }
    )

    return TokenResponse(access_token=access_token, user=User.model_validate(created_user))


@router.get("/me", response_model=User)
def read_current_user(current_user: UserModel = Depends(get_current_active_user)) -> User:
    return User.model_validate(current_user)


@router.post("/logout", response_model=LogoutResponse)
def logout() -> LogoutResponse:
    return LogoutResponse(message="Logout realizado com sucesso. Remova o token no cliente.")