from datetime import datetime
from typing import Optional
from datetime import timedelta
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    ConfigDict,
)


# =========================
# COMMON CONFIG
# =========================
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# =========================
# PATIENT SCHEMAS
# =========================
class PatientCreate(BaseSchema):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_number: str = Field(min_length=5, max_length=20)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: EmailStr):
        return v.lower()


class PatientRead(BaseSchema):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    created_timestamp: datetime
    updated_timestamp: datetime


# =========================
# DOCTOR SCHEMAS
# =========================
class DoctorCreate(BaseSchema):
    full_name: str = Field(min_length=1, max_length=200)
    specialization: str = Field(min_length=1, max_length=150)


class DoctorRead(BaseSchema):
    id: int
    full_name: str
    specialization: str
    active: bool
    created_timestamp: datetime


# =========================
# APPOINTMENT SCHEMAS
# =========================
class AppointmentCreate(BaseSchema):
    patient_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    start_time: datetime
    duration_minutes: int = Field(ge=15, le=180)

    # Ensure timezone-aware datetime
    @field_validator("start_time")
    @classmethod
    def must_be_timezone_aware(cls, v: datetime):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("Datetime must be timezone-aware")
        return v


class AppointmentRead(BaseSchema):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int
    created_timestamp: datetime

    # Derived field (not stored in DB)
    end_time: Optional[datetime] = None

    @field_validator("end_time", mode="before")
    @classmethod
    def compute_end_time(cls, v, info):
        if v is not None:
            return v

        data = info.data
        start = data.get("start_time")
        duration = data.get("duration_minutes")

        if start and duration:
            return start + timedelta(minutes=duration)

        return None
