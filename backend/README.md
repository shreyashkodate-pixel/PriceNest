# PriceNest — Backend API Subsystem

The PriceNest backend is built with **FastAPI**, **SQLAlchemy**, and **Alembic**, providing a high-performance, asynchronous REST API for residential property price estimation in Pune, India.

---

## 1. Directory Structure

```
backend/
├── README.md               # Backend architecture & developer guide (this file)
├── .env.example            # Template for local environment configuration
├── requirements.txt        # Python dependency manifest (to be populated in Phase 2)
├── alembic.ini             # Database migration configuration
├── alembic/                # Migration scripts and version history
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── .gitkeep
├── app/                    # Application source package
│   ├── __init__.py
│   ├── main.py             # FastAPI entrypoint, middleware, lifespan hooks
│   ├── core/               # App configuration, settings, database session
│   │   ├── __init__.py
│   │   ├── config.py       # Pydantic BaseSettings
│   │   ├── security.py     # Password hashing & JWT token lifecycle
│   │   └── database.py     # Async SQLAlchemy engine & session factory
│   ├── api/                # API route definitions
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py   # Root v1 APIRouter
│   │       ├── endpoints/
│   │       │   ├── auth.py         # User registration, login, profile (PRD F-03)
│   │       │   ├── predict.py      # Property price estimation
│   │       │   ├── history.py      # Private prediction history (PRD F-04)
│   │       │   ├── localities.py   # Pune micro-markets
│   │       │   └── health.py       # /health/live, /health/ready probes
│   ├── models/             # SQLAlchemy declarative ORM models
│   │   ├── __init__.py
│   │   ├── user.py         # User credentials and state
│   │   ├── locality.py     # Pune localities
│   │   ├── prediction.py   # Prediction audit and user-linked history
│   │   └── model_metadata.py
│   ├── schemas/            # Pydantic v2 request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py         # Registration, login, token schemas
│   │   ├── prediction.py   # Estimation input/output schemas
│   │   ├── history.py      # Paginated history schemas
│   │   └── locality.py
│   └── services/           # Business logic & ML inference adapters
│       ├── __init__.py
│       ├── auth_service.py     # Authentication & token management
│       ├── history_service.py  # Ownership-verified history access
│       ├── ml_service.py       # Model artifact loading and inference wrapper
│       └── locality_service.py
└── tests/                  # Automated test suite (pytest + HTTPX)
    ├── __init__.py
    ├── conftest.py         # Test fixtures and test database setup
    ├── test_health.py
    ├── test_auth.py        # Authentication & authorization checks
    ├── test_history.py     # History isolation & ownership enforcement
    └── test_predict.py
```


---

## 2. Technology Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python Web Framework)
- **Runtime:** Python 3.11+
- **Database Engine:** PostgreSQL hosted on [Supabase](https://supabase.com/)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Declarative Mappings + Asyncpg driver)
- **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Testing Suite:** `pytest` + `pytest-asyncio` + `httpx`
- **Deployment Platform:** [Render](https://render.com/) Web Service

---

## 3. Architecture & Operational Patterns

1. **Lifespan ML Model Loading:**
   The active ML model artifact (`.joblib`) is loaded into application memory once during the FastAPI lifespan startup event (`@asynccontextmanager`) and cached in the application state. Inference requests run synchronously in a threadpool worker or CPU-bound sub-routine without disk re-reads.
2. **Database Connection Pooling:**
   FastAPI interacts with Supabase PostgreSQL using `asyncpg` via SQLAlchemy's async engine, configured with connection pooling compatible with Supabase's Supavisor pooler.
3. **Structured API Contracts:**
   All endpoints strictly enforce Pydantic v2 models for request validation and response serialization, generating auto-documented OpenAPI 3.1 specifications available at `/docs` and `/redoc`.
4. **Resilience & Safe Fallbacks:**
   The prediction service validates input values against valid physical bounds (e.g., minimum realistic square footage for a given BHK) and returns structured error messages (HTTP 422) if parameters are nonsensical.

---

## 4. Local Development Workflow (Reference)

*Note: Application dependencies and virtual environment will be installed in subsequent implementation phases.*

1. **Environment Configuration:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env to configure local DATABASE_URL and settings
   ```
2. **Virtual Environment Setup (When ready):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. **Run Database Migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```
4. **Start Development Server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. **Run Test Suite:**
   ```bash
   pytest tests/ -v
   ```
