from datetime import datetime, timezone, timedelta, date

from sqlalchemy import select
from sqlalchemy.orm import Session

from patient_encounter_system.models.models import (
    Patient,
    Doctor,
    Appointment,
)



# =========================
# PATIENT SERVICES
# =========================

def create_patient(db: Session, data):
    patient = Patient(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email.lower(),
        phone_number=data.phone_number,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int):
    return db.get(Patient, patient_id)


# =========================
# DOCTOR SERVICES
# =========================

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


# =========================
# APPOINTMENT SERVICES
# =========================

def create_appointment(db: Session, data):
    """
    Enforces:
    - Future booking
    - Doctor must be active
    - No overlaps
    - Transaction-safe creation
    """

    # Convert to UTC
    start_time = data.start_time.astimezone(timezone.utc)
    end_time = start_time + timedelta(minutes=data.duration_minutes)

    # ---- Future check ----
    if start_time <= datetime.now(timezone.utc):
        raise ValueError("Appointment must be in the future")

    # ---- Doctor exists + active ----
    doctor = db.get(Doctor, data.doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")

    if not doctor.active:
        raise ValueError("Doctor is inactive")

    # ---- Patient exists ----
    patient = db.get(Patient, data.patient_id)
    if not patient:
        raise ValueError("Patient not found")

    # ---- Overlap check (FINAL CORRECT VERSION) ----
    overlap_stmt = select(Appointment).where(
        Appointment.doctor_id == data.doctor_id
    )

    appointments = db.execute(overlap_stmt).scalars().all()

    for appt in appointments:
        existing_start = appt.start_time

    # FIX: SQLite returns naive datetime
        if existing_start.tzinfo is None:
            existing_start = existing_start.replace(tzinfo=timezone.utc)

        existing_end = existing_start + timedelta(
            minutes=appt.duration_minutes
    )

        if existing_start < end_time and existing_end > start_time:
            raise ValueError("Appointment conflict")


    # ---- Transaction-safe insert ----
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



# =========================
# SCHEDULE QUERY
# =========================

def get_appointments_by_date(
    db: Session,
    query_date: date,
    doctor_id: int | None = None,
):
    """
    Returns all appointments for a date (UTC-based).
    """

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
