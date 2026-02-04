from datetime import datetime, timezone, timedelta, date
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Patient, Doctor, Appointment


def _ensure_utc(dt: datetime) -> datetime:
    """
    SQLite strips timezone info.
    This helper ensures all datetimes are UTC-aware before comparison.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def create_patient(db: Session, data):
    patient = Patient(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_number=data.phone_number,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int):
    return db.get(Patient, patient_id)


def create_doctor(db: Session, data):
    doctor = Doctor(
        full_name=data.full_name,
        specialization=data.specialization,
        active=True,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: int):
    return db.get(Doctor, doctor_id)


def create_appointment(db: Session, data):
    # Normalize incoming datetime
    start_time = _ensure_utc(data.start_time)
    end_time = start_time + timedelta(minutes=data.duration_minutes)

    if start_time <= datetime.now(timezone.utc):
        raise ValueError("Appointment must be in the future")

    doctor = db.get(Doctor, data.doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")
    if not doctor.active:
        raise ValueError("Doctor is inactive")

    patient = db.get(Patient, data.patient_id)
    if not patient:
        raise ValueError("Patient not found")

    stmt = select(Appointment).where(Appointment.doctor_id == data.doctor_id)
    existing_appointments = db.execute(stmt).scalars().all()

    for appt in existing_appointments:
        existing_start = _ensure_utc(appt.start_time)
        existing_end = existing_start + timedelta(minutes=appt.duration_minutes)

        # Overlap logic (allows back-to-back)
        if start_time < existing_end and end_time > existing_start:
            raise ValueError("Appointment conflict")

    appt = Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        start_time=start_time,
        duration_minutes=data.duration_minutes,
    )

    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


def get_appointments_by_date(
    db: Session,
    query_date: date,
    doctor_id: int | None = None,
):
    start_dt = datetime.combine(
        query_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )
    end_dt = start_dt + timedelta(days=1)

    stmt = select(Appointment).where(
        Appointment.start_time >= start_dt,
        Appointment.start_time < end_dt,
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)

    return db.execute(stmt).scalars().all()
