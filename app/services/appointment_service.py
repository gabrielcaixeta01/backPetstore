from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas.models import Appointment, AppointmentService, ClientModel, EmployeeModel, Pet, Service, Store


PAYMENT_METHOD_ALIASES = {
	"dinheiro": "dinheiro",
	"cash": "dinheiro",
	"cartão de crédito": "cartão de crédito",
	"cartao de credito": "cartão de crédito",
	"credit_card": "cartão de crédito",
	"cartão de débito": "cartão de débito",
	"cartao de debito": "cartão de débito",
	"debit_card": "cartão de débito",
	"pix": "pix",
	"transferência bancária": "transferência bancária",
	"transferencia bancaria": "transferência bancária",
	"transfer_bank": "transferência bancária",
}

APPOINTMENT_STATUS_ALIASES = {
	"agendado": "agendado",
	"scheduled": "agendado",
	"em andamento": "em andamento",
	"in_progress": "em andamento",
	"concluído": "concluído",
	"concluido": "concluído",
	"completed": "concluído",
	"cancelado": "cancelado",
	"canceled": "cancelado",
	"cancelled": "cancelado",
}


def _normalize_payment_method(payment_method: str | None) -> str | None:
	if payment_method is None:
		return None
	return PAYMENT_METHOD_ALIASES.get(payment_method.strip().lower())


def _normalize_status(status: str | None) -> str | None:
	if status is None:
		return None
	return APPOINTMENT_STATUS_ALIASES.get(status.strip().lower())



def _normalize_service_ids(service_ids: list[int] | None) -> list[int] | None:
	if service_ids is None:
		return None

	normalized_ids: list[int] = []
	for service_id in service_ids:
		if isinstance(service_id, int):
			normalized_ids.append(service_id)
			continue

		for chunk in service_id.split(","):
			value = chunk.strip()
			if not value:
				continue
			if not value.isdigit():
				raise HTTPException(status_code=422, detail=f"service_ids inválido: {value}")
			normalized_ids.append(int(value))

	return list(dict.fromkeys(normalized_ids))


def _load_services(db: Session, service_ids: list[int | str] | None) -> list[Service] | None:
	normalized_service_ids = _normalize_service_ids(service_ids)
	if normalized_service_ids is None:
		return None
	if not normalized_service_ids:
		return []

	services = db.query(Service).filter(Service.id.in_(normalized_service_ids)).all()
	services_by_id = {service.id: service for service in services}
	missing_service_ids = [service_id for service_id in normalized_service_ids if service_id not in services_by_id]
	if missing_service_ids:
		raise HTTPException(
			status_code=404,
			detail=f"Serviço(s) não encontrado(s): {', '.join(str(service_id) for service_id in missing_service_ids)}",
		)

	return [services_by_id[service_id] for service_id in normalized_service_ids]



def _require_employee_belongs_to_store(db: Session, employee_id: int, store_id: int) -> None:
	employee = db.query(EmployeeModel).filter(EmployeeModel.user_id == employee_id).first()
	if employee is None:
		raise HTTPException(status_code=404, detail="Funcionário não encontrado")

	if employee.store_id != store_id:
		raise HTTPException(
			status_code=400,
			detail=(
				"O funcionário selecionado não pertence à loja informada "
				f"(funcionário vinculado à loja {employee.store_id})"
			),
		)


def _calculate_appointment_total(db: Session, appointment_id: int) -> Decimal:
	total = (
		db.query(func.coalesce(func.sum(AppointmentService.charged_value), 0))
		.filter(AppointmentService.appointment_id == appointment_id)
		.scalar()
	)
	return Decimal(total)


def _sync_appointment_total(db: Session, appointment: Appointment) -> Appointment:
	appointment.final_value = _calculate_appointment_total(db, appointment.id)
	return appointment


def _validate_appointment_fields(
	payment_method: str | None,
	status: str | None,
	notes: str | None,
) -> None:
	normalized_payment_method = _normalize_payment_method(payment_method)
	if payment_method is not None and normalized_payment_method is None:
		raise HTTPException(
			status_code=400,
			detail=(
				"Forma de pagamento inválida. Use 'dinheiro', 'cartão de crédito', "
				"'cartão de débito', 'pix' ou 'transferência bancária'"
			),
		)

	normalized_status = _normalize_status(status)
	if status is not None and normalized_status is None:
		raise HTTPException(
			status_code=400,
			detail="Status inválido. Use 'agendado', 'em andamento', 'concluído' ou 'cancelado'",
		)

	if notes is not None and len(notes) > 500:
		raise HTTPException(status_code=400, detail="Notas devem conter no máximo 500 caracteres")


def create_appointment(
	db: Session,
	store_id: int,
	client_id: int,
	employee_id: int,
	pet_id: int,
	payment_method: str,
	service_ids: list[int],
	service_at: datetime | None,
	online: bool = False,
	status: str = "agendado",
	notes: str | None = None,

):	

	if store_id is None:
		raise HTTPException(status_code=400, detail="Loja é obrigatória")
	if client_id is None:
		raise HTTPException(status_code=400, detail="Cliente é obrigatório")
	if employee_id is None:
		raise HTTPException(status_code=400, detail="Funcionário é obrigatório")
	if pet_id is None:
		raise HTTPException(status_code=400, detail="Pet é obrigatório")
	if not payment_method:
		raise HTTPException(status_code=400, detail="Forma de pagamento é obrigatória")

	_validate_appointment_fields(payment_method=payment_method, status=status, notes=notes)
	normalized_payment_method = _normalize_payment_method(payment_method)
	normalized_status = _normalize_status(status)

	store = db.query(Store).filter(Store.id == store_id).first()
	if not store:
		raise HTTPException(status_code=404, detail=f"Loja com id {store_id} não encontrada")

	client = db.query(ClientModel).filter(ClientModel.user_id == client_id).first()
	if not client:
		raise HTTPException(status_code=404, detail=f"Cliente com id {client_id} não encontrado")

	_require_employee_belongs_to_store(db, employee_id, store_id)

	if service_ids is None:
		raise HTTPException(status_code=400, detail="Ao menos um serviço é obrigatório")
	if not service_ids:
		raise HTTPException(status_code=400, detail="Ao menos um serviço é obrigatório")
	services = _load_services(db, service_ids)

	pet = db.query(Pet).filter(Pet.id == pet_id).first()
	if not pet:
		raise HTTPException(status_code=404, detail="Pet não encontrado")

	if pet.owner_id != client_id:
		raise HTTPException(
			status_code=400,
			detail=f"O pet selecionado não pertence ao cliente informado. Pet pertence ao cliente {pet.owner_id}",
		)

	appointment = Appointment(
		final_value=Decimal("0"),
		service_at=service_at or datetime.utcnow(),
		status=normalized_status or status,
		store_id=store_id,
		client_id=client_id,
		employee_id=employee_id,
		pet_id=pet_id,
		payment_method=normalized_payment_method or payment_method,
		notes=notes,
		online=online,
	)
	db.add(appointment)
	db.flush()

	if services is not None:
		for service in services:
			db.add(
				AppointmentService(
					appointment_id=appointment.id,
					service_id=service.id,
					charged_value=service.price,
				)
			)
		db.flush()

	_sync_appointment_total(db, appointment)
	db.commit()
	db.refresh(appointment)
	return _sync_appointment_total(db, appointment)


def get_appointment(db: Session, appointment_id: int):
	appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
	if not appointment:
		raise HTTPException(status_code=404, detail="Atendimento não encontrado")
	return _sync_appointment_total(db, appointment)


def update_appointment(
	db: Session,
	appointment_id: int,
	service_at: datetime | None = None,
	status: str | None = None,
	store_id: int | None = None,
	client_id: int | None = None,
	employee_id: int | None = None,
	pet_id: int | None = None,
	payment_method: str | None = None,
	notes: str | None = None,
	online: bool | None = None,
	service_ids: list[int] | None = None,
):
	
	appointment = get_appointment(db, appointment_id)
	effective_store_id = store_id if store_id is not None else appointment.store_id
	effective_employee_id = employee_id if employee_id is not None else appointment.employee_id
	
	
	effective_services = _load_services(db, service_ids) if service_ids is not None else None
	_validate_appointment_fields(payment_method=payment_method, status=status, notes=notes)
	normalized_payment_method = _normalize_payment_method(payment_method)
	normalized_status = _normalize_status(status)

	_require_employee_belongs_to_store(db, effective_employee_id, effective_store_id)
	if service_ids is not None and not service_ids:
		raise HTTPException(status_code=400, detail="Ao menos um serviço é obrigatório quando service_ids é informado")

	if pet_id is not None or client_id is not None:
		effective_pet_id = pet_id if pet_id is not None else appointment.pet_id
		effective_client_id = client_id if client_id is not None else appointment.client_id
		pet = db.query(Pet).filter(Pet.id == effective_pet_id).first()
		if not pet:
			raise HTTPException(status_code=404, detail="Pet não encontrado")
		if pet.owner_id != effective_client_id:
			raise HTTPException(
				status_code=400,
				detail=f"O pet selecionado não pertence ao cliente informado. Pet pertence ao cliente {pet.owner_id}",
			)

	updates = {
		"service_at": service_at,
		"status": normalized_status or status,
		"store_id": store_id,
		"client_id": client_id,
		"employee_id": employee_id,
		"pet_id": pet_id,
		"payment_method": normalized_payment_method or payment_method,
		"notes": notes,
		"online": online,
	}
	for key, value in updates.items():
		if value is not None:
			setattr(appointment, key, value)

	if effective_services is not None:
		appointment.services.clear()
		db.flush()
		for service in effective_services:
			db.add(
				AppointmentService(
					appointment_id=appointment.id,
					service_id=service.id,
					charged_value=service.price,
				)
			)
		db.flush()

	_sync_appointment_total(db, appointment)

	db.commit()
	db.refresh(appointment)
	return _sync_appointment_total(db, appointment)


def delete_appointment(db: Session, appointment_id: int):
	appointment = get_appointment(db, appointment_id)
	db.delete(appointment)
	db.commit()


def list_appointments( db: Session) -> list[Appointment]:
	return db.query(Appointment).order_by(Appointment.id).all()
