from datetime import datetime, timezone, timedelta, date
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Patient, Doctor, Appointment


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
    Rules:
    - Appointment must be in future
    - Doctor must exist and be active
    - Patient must exist
    - No overlapping appointments
    - Back-to-back appointments ARE allowed
    """

    # Normalize to UTC
    start_time = data.start_time.astimezone(timezone.utc)
    end_time = start_time + timedelta(minutes=data.duration_minutes)

    # ---- Future check ----
    if start_time <= datetime.now(timezone.utc):
        raise ValueError("Appointment must be in the future")

    # ---- Doctor validation ----
    doctor = db.get(Doctor, data.doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")
    if not doctor.active:
        raise ValueError("Doctor is inactive")

    # ---- Patient validation ----
    patient = db.get(Patient, data.patient_id)
    if not patient:
        raise ValueError("Patient not found")

    # ---- Overlap check (CORRECT + FINAL) ----
    stmt = select(Appointment).where(Appointment.doctor_id == data.doctor_id)
    existing_appointments = db.execute(stmt).scalars().all()

    for appt in existing_appointments:
        existing_start = appt.start_time

        # SQLite returns naive datetime → normalize
        if existing_start.tzinfo is None:
            existing_start = existing_start.replace(tzinfo=timezone.utc)

        existing_end = existing_start + timedelta(minutes=appt.duration_minutes)

        # Overlap rule
        # Allow exact back-to-back (start == existing_end)
        if start_time < existing_end and end_time > existing_start:
            if start_time != existing_end:
                raise ValueError("Appointment conflict")

    # ---- Create appointment ----
    appointment = Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        start_time=start_time,
        duration_minutes=data.duration_minutes,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


# =========================
# QUERY APPOINTMENTS
# =========================
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
