from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from contextlib import asynccontextmanager

from database import engine, get_db
from models.models import Base
from schemas.schemas import (
    PatientCreate,
    PatientRead,
    DoctorCreate,
    DoctorRead,
    AppointmentCreate,
    AppointmentRead,
)
from services.services import (
    create_patient,
    get_patient,
    create_doctor,
    get_doctor,
    create_appointment,
    get_appointments_by_date,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Medical Encounter Management System",
    lifespan=lifespan,
)


@app.post("/patients", response_model=PatientRead, status_code=201)
def create_patient_api(payload: PatientCreate, db: Session = Depends(get_db)):
    try:
        return create_patient(db, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient_api(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.post("/doctors", response_model=DoctorRead, status_code=201)
def create_doctor_api(payload: DoctorCreate, db: Session = Depends(get_db)):
    try:
        return create_doctor(db, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/doctors/{doctor_id}", response_model=DoctorRead)
def get_doctor_api(doctor_id: int, db: Session = Depends(get_db)):
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@app.post("/appointments", response_model=AppointmentRead, status_code=201)
def create_appointment_api(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_appointment(db, payload)
    except ValueError as e:
        msg = str(e).lower()
        if "conflict" in msg or "future" in msg or "inactive" in msg:
            raise HTTPException(status_code=409, detail=str(e))
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/appointments", response_model=list[AppointmentRead])
def list_appointments_api(
    date: date = Query(...),
    doctor_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_appointments_by_date(db, date, doctor_id)
