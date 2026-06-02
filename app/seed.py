import os
import logging
from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.models import Category, EmployeeModel, Store, Tag, UserModel
from app.core.security import hash_password

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dados iniciais
# ---------------------------------------------------------------------------

_STORES = [
    dict(
        name="Apex Petstore Centro",
        cnpj="11.111.111/0001-11",
        phone="(11) 3000-0001",
        email="centro@apexbrasil.com",
        cep="01310-100",
        city="São Paulo",
        state="SP",
        street="Av. Paulista",
        neighborhood="Bela Vista",
        number="1000",
    ),
    dict(
        name="Apex Petstore Norte",
        cnpj="22.222.222/0001-22",
        phone="(11) 3000-0002",
        email="norte@apexbrasil.com",
        cep="02010-000",
        city="São Paulo",
        state="SP",
        street="Rua Voluntários da Pátria",
        neighborhood="Santana",
        number="500",
    ),
]

_CATEGORIES = [
    ("Cachorro", "Cães de todas as raças e portes"),
    ("Gato", "Felinos domésticos"),
    ("Peixe", "Peixes de aquário e ornamentais"),
    ("Pássaro", "Aves domésticas e ornamentais"),
    ("Réptil", "Répteis e anfíbios"),
    ("Roedor", "Hamsters, coelhos e similares"),
]

_TAGS = [
    ("Vacinado", "Animal com vacinas em dia"),
    ("Castrado", "Animal castrado"),
    ("Microchipado", "Animal com microchip de identificação"),
    ("Alergia alimentar", "Animal com restrições alimentares"),
    ("Cuidados especiais", "Necessita atenção veterinária especial"),
    ("Filhote", "Animal com menos de 1 ano"),
    ("Idoso", "Animal com mais de 7 anos"),
]

# store_index refere-se à posição em _STORES
_EMPLOYEES = [
    dict(
        name="Carlos Mendes",
        email="carlos.mendes@apexbrasil.com",
        phone="(11) 91111-0001",
        employee_code="EMP-001",
        job_title="Veterinário",
        salary=5500.00,
        hired_at=date(2023, 3, 1),
        store_index=0,
    ),
    dict(
        name="Ana Lima",
        email="ana.lima@apexbrasil.com",
        phone="(11) 91111-0002",
        employee_code="EMP-002",
        job_title="Tosadora",
        salary=3200.00,
        hired_at=date(2023, 6, 15),
        store_index=0,
    ),
    dict(
        name="Pedro Souza",
        email="pedro.souza@apexbrasil.com",
        phone="(11) 91111-0003",
        employee_code="EMP-003",
        job_title="Atendente",
        salary=2800.00,
        hired_at=date(2024, 1, 10),
        store_index=1,
    ),
    dict(
        name="Julia Costa",
        email="julia.costa@apexbrasil.com",
        phone="(11) 91111-0004",
        employee_code="EMP-004",
        job_title="Veterinária",
        salary=5800.00,
        hired_at=date(2024, 4, 1),
        store_index=1,
    ),
]

# ---------------------------------------------------------------------------
# Seeders individuais
# ---------------------------------------------------------------------------

def _seed_stores(db: Session) -> list[Store]:
    stores: list[Store] = []
    for data in _STORES:
        store = db.query(Store).filter(Store.cnpj == data["cnpj"]).first()
        if store is None:
            store = Store(**data)
            db.add(store)
            db.flush()
            logger.info("seed: loja criada — %s", data["name"])
        stores.append(store)
    return stores


def _seed_superuser(db: Session, store: Store) -> None:
    email = os.getenv("SUPERUSER_EMAIL", "admin@apexbrasil.com")
    password = os.getenv("SUPERUSER_PASSWORD")

    if password is None:
        logger.warning(
            "seed: SUPERUSER_PASSWORD não definida — superuser não será criado. "
            "Defina a variável de ambiente para criá-lo automaticamente."
        )
        return

    if db.query(UserModel).filter(UserModel.email == email).first():
        return

    user = UserModel(
        name="Administrador",
        email=email,
        password_hash=hash_password(password),
        phone="(11) 00000-0000",
        profile_type="funcionario",
        is_superuser=True,
        active=True,
    )
    db.add(user)
    db.flush()

    db.add(EmployeeModel(
        user_id=user.id,
        employee_code="SUP-001",
        job_title="Administrador do Sistema",
        salary=0,
        hired_at=date.today(),
        store_id=store.id,
    ))
    logger.info("seed: superuser criado — %s", email)


def _seed_categories(db: Session) -> None:
    for name, description in _CATEGORIES:
        if not db.query(Category).filter(Category.name == name).first():
            db.add(Category(name=name, description=description))
            logger.info("seed: categoria criada — %s", name)


def _seed_tags(db: Session) -> None:
    for name, description in _TAGS:
        if not db.query(Tag).filter(Tag.name == name).first():
            db.add(Tag(name=name, description=description))
            logger.info("seed: tag criada — %s", name)


def _seed_employees(db: Session, stores: list[Store]) -> None:
    default_password = os.getenv("EMPLOYEE_DEFAULT_PASSWORD", "Apex@2024")
    for data in _EMPLOYEES:
        if db.query(UserModel).filter(UserModel.email == data["email"]).first():
            continue

        store = stores[data["store_index"]]
        user = UserModel(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            password_hash=hash_password(default_password),
            profile_type="funcionario",
            is_superuser=False,
            active=True,
        )
        db.add(user)
        db.flush()

        db.add(EmployeeModel(
            user_id=user.id,
            employee_code=data["employee_code"],
            job_title=data["job_title"],
            salary=data["salary"],
            hired_at=data["hired_at"],
            store_id=store.id,
        ))
        logger.info("seed: funcionário criado — %s (%s)", data["name"], data["employee_code"])


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def run_seed() -> None:
    db = SessionLocal()
    try:
        stores = _seed_stores(db)
        _seed_superuser(db, stores[0])
        _seed_categories(db)
        _seed_tags(db)
        _seed_employees(db, stores)
        db.commit()
        logger.info("seed: concluído.")
    except Exception:
        db.rollback()
        logger.exception("seed: erro — rollback realizado.")
        raise
    finally:
        db.close()
