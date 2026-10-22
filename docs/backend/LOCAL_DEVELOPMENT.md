# PriceNest — Backend Local Development Guide

This guide details instructions for setting up, running, migrating, and testing the PriceNest FastAPI backend locally.

---

## 1. Prerequisites

- Python 3.11+ (Python 3.14 verified)
- Virtual environment (`.venv`)
- SQLite (built-in) or PostgreSQL 15+

---

## 2. Environment Setup

1. **Activate the Virtual Environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure Local Environment:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   *(By default, `backend/.env.example` is preconfigured for local SQLite development. For local PostgreSQL, update `DATABASE_URL` and `SYNC_DATABASE_URL`).*

---

## 3. Database Migrations

PriceNest uses **Alembic** for schema migrations.

### Run Migrations to Latest Schema:
```bash
cd backend
alembic upgrade head
```

### Inspect Current Revision:
```bash
cd backend
alembic current
```

### Rollback Last Migration:
```bash
cd backend
alembic downgrade -1
```

---

## 4. Running the Development Server

Start the FastAPI application with Uvicorn:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Documentation (Swagger):** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **Liveness Probe:** `http://localhost:8000/health/live`
- **Readiness Probe:** `http://localhost:8000/health/ready`
- **OpenAPI Schema (JSON):** `http://localhost:8000/openapi.json`

---

## 5. Running the Automated Test Suite

Execute the full test suite with coverage reporting:
```bash
pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing
```

### Run Static Analysis & Linting:
```bash
ruff check backend/ ml/
```
