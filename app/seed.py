import os
import logging
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.models import (
    Appointment, AppointmentService, Category, ClientModel,
    EmployeeModel, Pet, Service, Store, Tag, UserModel,
)
from app.core.security import hash_password

logger = logging.getLogger(__name__)

_STORES = [
    dict(name="Pet Club Centro", cnpj="11.111.111/0001-11", phone="(11) 3000-0001", email="centro@petclub.com.br", cep="01310-100", city="São Paulo", state="SP", street="Av. Paulista", neighborhood="Bela Vista", number="1000"),
    dict(name="Pet Club Norte", cnpj="22.222.222/0001-22", phone="(11) 3000-0002", email="norte@petclub.com.br", cep="02010-000", city="São Paulo", state="SP", street="Rua Voluntários da Pátria", neighborhood="Santana", number="500"),
    dict(name="Pet Club Asa Sul", cnpj="33.333.333/0001-33", phone="(61) 3000-0003", email="asasul@petclub.com.br", cep="70390-045", city="Brasília", state="DF", street="SCS Quadra 01", neighborhood="Asa Sul", number="Bloco A"),
    dict(name="Pet Club Asa Norte", cnpj="44.444.444/0001-44", phone="(61) 3000-0004", email="asanorte@petclub.com.br", cep="70712-903", city="Brasília", state="DF", street="SCN Quadra 02", neighborhood="Asa Norte", number="Bloco B"),
    dict(name="Pet Club Plano Piloto", cnpj="55.555.555/0001-55", phone="(61) 3000-0005", email="planopiloto@petclub.com.br", cep="70070-912", city="Brasília", state="DF", street="Esplanada dos Ministérios", neighborhood="Plano Piloto", number="Bloco T"),
]

_EMPLOYEES = [
    dict(name="Carlos Mendes",   email="carlos.mendes@petclub.com.br",   phone="(11) 91111-0001", employee_code="EMP-001", job_title="Veterinário",  salary=5500.00, hired_at=date(2023, 3,  1), store_index=0),
    dict(name="Ana Lima",        email="ana.lima@petclub.com.br",         phone="(11) 91111-0002", employee_code="EMP-002", job_title="Tosadora",     salary=3200.00, hired_at=date(2023, 6, 15), store_index=0),
    dict(name="Pedro Souza",     email="pedro.souza@petclub.com.br",      phone="(11) 91111-0003", employee_code="EMP-003", job_title="Atendente",    salary=2800.00, hired_at=date(2024, 1, 10), store_index=1),
    dict(name="Julia Costa",     email="julia.costa@petclub.com.br",      phone="(11) 91111-0004", employee_code="EMP-004", job_title="Veterinária",  salary=5800.00, hired_at=date(2024, 4,  1), store_index=1),
    dict(name="Bruna Almeida",   email="bruna.almeida@petclub.com.br",    phone="(61) 91111-0005", employee_code="EMP-005", job_title="Veterinária",  salary=5600.00, hired_at=date(2024, 2,  1), store_index=2),
    dict(name="Rafael Lima",     email="rafael.lima@petclub.com.br",      phone="(61) 91111-0006", employee_code="EMP-006", job_title="Tosador",      salary=3400.00, hired_at=date(2024, 3, 20), store_index=2),
    dict(name="Marcos Andrade",  email="marcos.andrade@petclub.com.br",   phone="(61) 91111-0007", employee_code="EMP-007", job_title="Veterinário",  salary=5700.00, hired_at=date(2024, 5,  5), store_index=3),
    dict(name="Patrícia Gomes",  email="patricia.gomes@petclub.com.br",   phone="(61) 91111-0008", employee_code="EMP-008", job_title="Atendente",    salary=2900.00, hired_at=date(2024, 6, 10), store_index=3),
    dict(name="Fernanda Vieira", email="fernanda.vieira@petclub.com.br",  phone="(61) 91111-0009", employee_code="EMP-009", job_title="Tosadora",     salary=3300.00, hired_at=date(2024, 7,  1), store_index=4),
    dict(name="Diego Carvalho",  email="diego.carvalho@petclub.com.br",   phone="(61) 91111-0010", employee_code="EMP-010", job_title="Atendente",    salary=2850.00, hired_at=date(2024, 8, 15), store_index=4),
]

_CATEGORIES = [
    ("Cachorro", "Cães de todas as raças e portes"),
    ("Gato",     "Felinos domésticos"),
    ("Peixe",    "Peixes de aquário e ornamentais"),
    ("Pássaro",  "Aves domésticas e ornamentais"),
    ("Réptil",   "Répteis e anfíbios"),
    ("Roedor",   "Hamsters, coelhos e similares"),
]

_TAGS = [
    ("Vacinado",          "Animal com vacinas em dia"),
    ("Castrado",          "Animal castrado"),
    ("Microchipado",      "Animal com microchip de identificação"),
    ("Alergia alimentar", "Animal com restrições alimentares"),
    ("Cuidados especiais","Necessita atenção veterinária especial"),
    ("Filhote",           "Animal com menos de 1 ano"),
    ("Idoso",             "Animal com mais de 7 anos"),
]

_SERVICES = [
    dict(name="Banho",                description="Banho completo com shampoo neutro, condicionador e secagem",           price=50.00),
    dict(name="Tosa",                 description="Tosa higiênica ou estética conforme a raça do pet",                    price=80.00),
    dict(name="Banho e Tosa",         description="Pacote completo: banho, tosa, limpeza de ouvidos e corte de unhas",    price=120.00),
    dict(name="Vacinação",            description="Aplicação de vacinas conforme calendário vacinal do pet",              price=90.00),
    dict(name="Adestramento",         description="Sessão individual de adestramento, socialização e comandos básicos",   price=150.00),
    dict(name="Consulta Veterinária", description="Consulta clínica geral com médico veterinário credenciado",            price=200.00),
    dict(name="Pet Hotel (diária)",   description="Hospedagem confortável com alimentação e monitoramento 24h",           price=80.00),
    dict(name="Hidratação",           description="Tratamento de hidratação profunda para pelo e pele ressecados",        price=60.00),
]

_CLIENTS = [
    dict(name="Maria Silva",      email="maria.silva@email.com",      phone="(61) 99001-0001", cpf="111.111.111-11", client_type="pessoa_fisica", cep="70390-025", city="Brasília", state="DF"),
    dict(name="João Oliveira",    email="joao.oliveira@email.com",    phone="(61) 99001-0002", cpf="222.222.222-22", client_type="pessoa_fisica", cep="70712-500", city="Brasília", state="DF"),
    dict(name="Ana Pereira",      email="ana.pereira@email.com",      phone="(61) 99001-0003", cpf="333.333.333-33", client_type="pessoa_fisica", cep="70040-010", city="Brasília", state="DF"),
    dict(name="Lucas Santos",     email="lucas.santos@email.com",     phone="(61) 99001-0004", cpf="444.444.444-44", client_type="pessoa_fisica", cep="70297-400", city="Brasília", state="DF"),
    dict(name="Camila Fernandes", email="camila.fernandes@email.com", phone="(61) 99001-0005", cpf="555.555.555-55", client_type="pessoa_fisica", cep="70673-400", city="Brasília", state="DF"),
]

_PETS = [
    dict(name="Thor", breed="Labrador Retriever", sex="macho",  size="grande",  weight=30.0, health_notes="Vacinado em dia, ativo e saudável",        category_name="Cachorro", tags=["Vacinado", "Microchipado"],       client_index=0),
    dict(name="Mia",  breed="Siamês",             sex="femea",  size="pequeno", weight=4.0,  health_notes="Castrada, sem alergias conhecidas",         category_name="Gato",     tags=["Castrado", "Vacinado"],           client_index=1),
    dict(name="Bob",  breed="Golden Retriever",   sex="macho",  size="grande",  weight=28.0, health_notes="Alergia a frango, vacinado em dia",         category_name="Cachorro", tags=["Vacinado", "Alergia alimentar"],  client_index=2),
    dict(name="Nemo", breed="Peixe-palhaço",      sex="macho",  size="pequeno", weight=0.1,  health_notes="Aquário de 100L com salinidade controlada", category_name="Peixe",    tags=[],                                 client_index=3),
    dict(name="Mel",  breed="Yorkshire Terrier",  sex="femea",  size="pequeno", weight=3.0,  health_notes="Filhote, vacinação em andamento",           category_name="Cachorro", tags=["Filhote", "Vacinado"],             client_index=4),
]

_APPOINTMENTS = [
    dict(client_email="maria.silva@email.com",      pet_name="Thor", store_index=0, employee_email="carlos.mendes@petclub.com.br",   service_names=["Banho e Tosa"],              service_at=datetime(2026, 5, 10, 9,  0), payment_method="pix",            status="concluido", online=False, notes="Tosa estética padrão Labrador."),
    dict(client_email="joao.oliveira@email.com",    pet_name="Mia",  store_index=1, employee_email="julia.costa@petclub.com.br",     service_names=["Consulta Veterinária"],      service_at=datetime(2026, 5, 12, 14, 0), payment_method="cartao_credito", status="concluido", online=False, notes="Consulta de rotina anual."),
    dict(client_email="ana.pereira@email.com",      pet_name="Bob",  store_index=2, employee_email="bruna.almeida@petclub.com.br",   service_names=["Banho", "Hidratação"],       service_at=datetime(2026, 5, 15, 10, 0), payment_method="dinheiro",       status="concluido", online=False, notes="Atenção: alergia a frango, usar shampoo hipoalergênico."),
    dict(client_email="camila.fernandes@email.com", pet_name="Mel",  store_index=4, employee_email="fernanda.vieira@petclub.com.br", service_names=["Banho e Tosa"],              service_at=datetime(2026, 5, 20, 11, 0), payment_method="pix",            status="concluido", online=False, notes=None),
    dict(client_email="maria.silva@email.com",      pet_name="Thor", store_index=0, employee_email="ana.lima@petclub.com.br",        service_names=["Adestramento"],              service_at=datetime(2026, 6,  1, 9,  0), payment_method="pix",            status="agendado",  online=False, notes="Primeira sessão de adestramento."),
    dict(client_email="lucas.santos@email.com",     pet_name="Nemo", store_index=3, employee_email="marcos.andrade@petclub.com.br", service_names=["Consulta Veterinária"],      service_at=datetime(2026, 6,  5, 15, 0), payment_method="cartao_debito",  status="agendado",  online=False, notes="Primeira consulta do Nemo."),
    dict(client_email="joao.oliveira@email.com",    pet_name="Mia",  store_index=3, employee_email="patricia.gomes@petclub.com.br", service_names=["Banho", "Tosa"],             service_at=datetime(2026, 6,  8, 13, 0), payment_method="pix",            status="agendado",  online=True,  notes="Agendamento online."),
]

# ---------------------------------------------------------------------------
# Seeders
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
    email = os.getenv("SUPERUSER_EMAIL", "admin@petstore.com")
    password = os.getenv("SUPERUSER_PASSWORD")
    employee_code = "SUP-001"

    existing_employee = db.query(EmployeeModel).filter(EmployeeModel.employee_code == employee_code).first()
    if existing_employee is not None:
        return

    if password is None:
        logger.warning("seed: SUPERUSER_PASSWORD não definida — superuser não será criado.")
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
        employee_code=employee_code,
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


def _seed_services(db: Session) -> None:
    for data in _SERVICES:
        if not db.query(Service).filter(Service.name == data["name"]).first():
            db.add(Service(**data))
            logger.info("seed: serviço criado — %s", data["name"])


def _seed_employees(db: Session, stores: list[Store]) -> None:
    default_password = os.getenv("EMPLOYEE_DEFAULT_PASSWORD", "Petstore@2026")
    for data in _EMPLOYEES:
        if db.query(EmployeeModel).filter(EmployeeModel.employee_code == data["employee_code"]).first():
            continue
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


def _seed_clients(db: Session) -> list[ClientModel]:
    default_password = os.getenv("CLIENT_DEFAULT_PASSWORD", "Petstore@2026")
    clients: list[ClientModel] = []
    for data in _CLIENTS:
        user = db.query(UserModel).filter(UserModel.email == data["email"]).first()
        if user is None:
            user = UserModel(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                cpf=data["cpf"],
                password_hash=hash_password(default_password),
                profile_type="cliente",
                is_superuser=False,
                active=True,
            )
            db.add(user)
            db.flush()
            client = ClientModel(
                user_id=user.id,
                client_type=data["client_type"],
                cep=data["cep"],
                city=data["city"],
                state=data["state"],
            )
            db.add(client)
            db.flush()
            logger.info("seed: cliente criado — %s", data["name"])
        else:
            client = db.query(ClientModel).filter(ClientModel.user_id == user.id).first()
        clients.append(client)
    return clients


def _seed_pets(db: Session, clients: list[ClientModel]) -> list[Pet]:
    pets: list[Pet] = []
    for data in _PETS:
        client = clients[data["client_index"]]
        existing = (
            db.query(Pet)
            .filter(Pet.name == data["name"], Pet.owner_id == client.user_id)
            .first()
        )
        if existing:
            pets.append(existing)
            continue

        category = db.query(Category).filter(Category.name == data["category_name"]).first()
        if category is None:
            logger.warning("seed: categoria '%s' não encontrada, pulando pet %s", data["category_name"], data["name"])
            pets.append(None)  # type: ignore
            continue

        pet = Pet(
            name=data["name"],
            breed=data["breed"],
            sex=data["sex"],
            size=data["size"],
            weight=data["weight"],
            health_notes=data.get("health_notes"),
            category_id=category.id,
            owner_id=client.user_id,
        )
        for tag_name in data.get("tags", []):
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                pet.tags.append(tag)
        db.add(pet)
        db.flush()
        logger.info("seed: pet criado — %s (dono: user_id=%s)", data["name"], client.user_id)
        pets.append(pet)
    return pets


def _seed_appointments(db: Session, stores: list[Store], pets: list[Pet], clients: list[ClientModel]) -> None:
    for data in _APPOINTMENTS:
        client_user = db.query(UserModel).filter(UserModel.email == data["client_email"]).first()
        if client_user is None:
            logger.warning("seed: cliente '%s' não encontrado, pulando atendimento", data["client_email"])
            continue
        client = db.query(ClientModel).filter(ClientModel.user_id == client_user.id).first()
        if client is None:
            continue

        pet = db.query(Pet).filter(Pet.name == data["pet_name"], Pet.owner_id == client.user_id).first()
        if pet is None:
            logger.warning("seed: pet '%s' não encontrado para '%s', pulando atendimento", data["pet_name"], data["client_email"])
            continue

        exists = (
            db.query(Appointment)
            .filter(
                Appointment.client_id == client.user_id,
                Appointment.pet_id == pet.id,
                Appointment.service_at == data["service_at"],
            )
            .first()
        )
        if exists:
            continue

        employee_user = db.query(UserModel).filter(UserModel.email == data["employee_email"]).first()
        employee = (
            db.query(EmployeeModel).filter(EmployeeModel.user_id == employee_user.id).first()
            if employee_user else None
        )

        store = stores[data["store_index"]]

        services: list[Service] = []
        total = 0.0
        for svc_name in data["service_names"]:
            svc = db.query(Service).filter(Service.name == svc_name).first()
            if svc:
                services.append(svc)
                total += float(svc.price)

        appointment = Appointment(
            final_value=total,
            service_at=data["service_at"],
            payment_method=data["payment_method"],
            status=data["status"],
            online=data["online"],
            notes=data.get("notes"),
            store_id=store.id,
            client_id=client.user_id,
            employee_id=employee.user_id if employee else None,
            pet_id=pet.id,
        )
        db.add(appointment)
        db.flush()

        for svc in services:
            db.add(AppointmentService(
                appointment_id=appointment.id,
                service_id=svc.id,
                charged_value=svc.price,
            ))

        logger.info(
            "seed: atendimento criado — %s | pet: %s | %s",
            data["client_email"], data["pet_name"], data["service_at"].strftime("%Y-%m-%d"),
        )


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def run_seed() -> None:
    db = SessionLocal()
    try:
        stores  = _seed_stores(db)
        _seed_superuser(db, stores[0])
        _seed_categories(db)
        _seed_tags(db)
        _seed_services(db)
        _seed_employees(db, stores)
        clients = _seed_clients(db)
        pets    = _seed_pets(db, clients)
        _seed_appointments(db, stores, pets, clients)
        db.commit()
        logger.info("seed: concluído com sucesso.")
    except Exception:
        db.rollback()
        logger.exception("seed: erro — rollback realizado. App continuará sem dados iniciais.")
    finally:
        db.close()