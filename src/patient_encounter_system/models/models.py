from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from patient_encounter_system.database import Base



# =========================
# PATIENT MODEL
# =========================
class Patient(Base):
    __tablename__ = "Shanmukh_patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    appointments = relationship(
        "Appointment",
        back_populates="patient",
        passive_deletes=True,
    )


# =========================
# DOCTOR MODEL
# =========================
class Doctor(Base):
    __tablename__ = "Shanmukh_doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    full_name: Mapped[str] = mapped_column(String(200), nullable=False)

    specialization: Mapped[str] = mapped_column(String(150), nullable=False)

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    appointments = relationship(
        "Appointment",
        back_populates="doctor",
        passive_deletes=True,
    )


# =========================
# APPOINTMENT MODEL
# =========================
class Appointment(Base):
    __tablename__ = "Shanmukh_appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("Shanmukh_patients.id", ondelete="RESTRICT"),
        nullable=False,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("Shanmukh_doctors.id", ondelete="RESTRICT"),
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,  # required by spec
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    # Indexes for performance
    __table_args__ = (
        Index("idx_doctor_start", "doctor_id", "start_time"),
    )
