from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import Appointment
from app.services import appointment_service
from app.core.security import get_current_active_user
from app.schemas.models import UserModel

router = APIRouter(prefix="/appointment", tags=["CRUD de Atendimentos"])


@router.post("", status_code=201, response_model=Appointment)
def create_appointment(
	service_at: datetime | None = Query(None),
	payment_method: str = Query(...),
	status: str = Query("agendado"),
	online: bool = Query(False),
	notes: str | None = Query(None),
	store_id: int = Query(...),
	client_id: int = Query(...),
	employee_id: int = Query(...),
	pet_id: int = Query(...),
	service_ids: list[int] = Query(...),
	current_user: UserModel = Depends(get_current_active_user),
	db: Session = Depends(get_db),
):

	if getattr(current_user, "profile_type", None) == "cliente":
		if client_id != current_user.id:
			from fastapi import HTTPException
			raise HTTPException(status_code=403, detail="Clientes só podem criar atendimentos para si mesmos")
		online = True

	return appointment_service.create_appointment(
		db=db,
		service_at=service_at,
		payment_method=payment_method,
		status=status,
		online=online,
		notes=notes,
		store_id=store_id,
		client_id=client_id,
		employee_id=employee_id,
		pet_id=pet_id,
		service_ids=service_ids,
	)


@router.get("/appointments", response_model=list[Appointment])
def list_appointments(db: Session = Depends(get_db)) -> list[Appointment]:
	return appointment_service.list_appointments(db)


@router.get("/{id}", response_model=Appointment)
def get_appointment(id: int, db: Session = Depends(get_db)) -> Appointment:
	return appointment_service.get_appointment(db, id)


@router.put("/{id}", response_model=Appointment)
def update_appointment(
	id: int,
	service_at: datetime | None = Query(None),
	payment_method: str | None = Query(None),
	status: str | None = Query(None),
	online: bool | None = Query(None),
	notes: str | None = Query(None),
	store_id: int | None = Query(None),
	client_id: int | None = Query(None),
	employee_id: int | None = Query(None),
	pet_id: int | None = Query(None),
	service_ids: list[int] | None = Query(None),
    current_user: UserModel = Depends(get_current_active_user),
	db: Session = Depends(get_db),
) -> Appointment:

	appointment = appointment_service.get_appointment(db, id)
	if not (getattr(current_user, "is_superuser", False) or getattr(current_user, "profile_type", None) == "funcionario" or appointment.client_id == current_user.id):
		
		raise HTTPException(status_code=403, detail="Você não tem permissão para atualizar este atendimento")

	updated_appointment = appointment_service.update_appointment(
		db=db,
		appointment_id=id,
		service_at=service_at,
		payment_method=payment_method,
		status=status,
		online=online,
		notes=notes,
		store_id=store_id,
		client_id=client_id,
		employee_id=employee_id,
		pet_id=pet_id,
		service_ids=service_ids,
	)
	return updated_appointment


@router.delete("/{id}", status_code=200, response_model=dict)
def delete_appointment(id: int, current_user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)) -> dict:
	appointment = appointment_service.get_appointment(db, id)
	if not (getattr(current_user, "is_superuser", False) or getattr(current_user, "profile_type", None) == "funcionario" or appointment.client_id == current_user.id):
		raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este atendimento")
	appointment_service.delete_appointment(db, id)
	return {"message": "Atendimento deletado com sucesso"}