# Patient Encounter Management System

A FastAPI-based backend application to manage patients, doctors, and medical appointments.  
This system allows creating and retrieving patients and doctors, as well as scheduling appointments with proper validation rules.

---

## 📌 Features

- Create and retrieve patients
- Create and retrieve doctors
- Schedule appointments
- Prevent overlapping appointments
- Enforce future-only booking
- Validate active doctor status
- Filter appointments by date and doctor
- Unit tests with pytest
- Code coverage reporting
- Linting and formatting support

---

## 🏗 Tech Stack

- FastAPI
- SQLAlchemy
- Pydantic
- SQLite (default for local/testing)
- Pytest
- Poetry (dependency management)

---

## 📂 Project Structure

```
patient-encounter-system/
│
├── src/patient_encounter_system/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   └── services/
│
├── tests/
├── pyproject.toml
└── README.md
```

---

## 🚀 Setup Instructions

### 1) Clone the repository

```
git clone <your-repo-url>
cd patient-encounter-system
```

---

### 2) Install Poetry (if not installed)

```
pip install poetry
```

Verify:

```
poetry --version
```

---

### 3) Install dependencies

```
poetry install
```

Activate virtual environment:

```
poetry shell
```

---

## 🗄 Database Initialization

Tables are automatically created when the app starts:

```
Base.metadata.create_all(bind=engine)
```

Default DB: SQLite  
You can modify the database URL in `database.py`.

---

## ▶️ Running the Application

```
poetry run uvicorn patient_encounter_system.main:app --reload
```

App runs at:

```
http://127.0.0.1:8000
```

Interactive API docs:

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Running Tests

```
poetry run pytest
```

With coverage:

```
poetry run pytest --cov=patient_encounter_system
```

---

## 🧹 Linting

```
poetry run ruff check src
```

Auto-fix:

```
poetry run ruff check src --fix
```

---

## 🎨 Formatting

Check:

```
poetry run black --check .
```

Format:

```
poetry run black .
```

---

## 🔒 Security Scan

```
poetry run bandit -r src
```

---

## 📌 Appointment Rules

- Appointments must be in the future
- Doctors must be active
- No overlapping appointments
- Back-to-back appointments are allowed
- Times handled in UTC

---

## 📬 API Endpoints

### Patients
- `POST /patients`
- `GET /patients/{id}`

### Doctors
- `POST /doctors`
- `GET /doctors/{id}`

### Appointments
- `POST /appointments`
- `GET /appointments?date=YYYY-MM-DD&doctor_id=ID`

---

## ✅ CI Ready

Project includes:

- pytest
- pytest-cov
- ruff
- pylint
- bandit

Suitable for GitHub Actions CI pipelines.

---

## 👤 Author

Mukesh

---

## 📄 License

This project is for learning and training purposes.
