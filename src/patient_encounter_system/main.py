from datetime import date

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

# ✅ absolute imports (correct for src layout)
from patient_encounter_system.database import engine, get_db
from patient_encounter_system.models.models import Base
from patient_encounter_system.schemas.schemas import (
    PatientCreate,
    PatientRead,
    DoctorCreate,
    DoctorRead,
    AppointmentCreate,
    AppointmentRead,
)
from patient_encounter_system.services.services import (
    create_patient,
    get_patient,
    create_doctor,
    get_doctor,
    create_appointment,
    get_appointments_by_date,
)

app = FastAPI(title="Medical Encounter Management System")

# create tables (for dev/testing)
Base.metadata.create_all(bind=engine)

# =========================
# PATIENT APIs
# =========================

@app.post(
    "/patients",
    response_model=PatientRead,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_api(
    payload: PatientCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_patient(db, payload)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@app.get(
    "/patients/{patient_id}",
    response_model=PatientRead,
)
def get_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = get_patient(db, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return patient


# =========================
# DOCTOR APIs
# =========================

@app.post(
    "/doctors",
    response_model=DoctorRead,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_api(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
):
    return create_doctor(db, payload)


@app.get(
    "/doctors/{doctor_id}",
    response_model=DoctorRead,
)
def get_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found",
        )

    return doctor


# =========================
# APPOINTMENT APIs
# =========================

@app.post(
    "/appointments",
    response_model=AppointmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment_api(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_appointment(db, payload)

    except ValueError as e:
        message = str(e)

        if (
            "conflict" in message.lower()
            or "inactive" in message.lower()
            or "future" in message.lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        if "not found" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )


@app.get(
    "/appointments",
    response_model=list[AppointmentRead],
)
def list_appointments_api(
    date: date = Query(...),
    doctor_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_appointments_by_date(
        db,
        query_date=date,
        doctor_id=doctor_id,
    )
