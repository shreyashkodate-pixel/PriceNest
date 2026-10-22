# PriceNest — Backend API Subsystem

The PriceNest backend is built with **FastAPI**, **SQLAlchemy**, and **Alembic**, providing a high-performance, asynchronous REST API for residential property price estimation in Pune, Maharashtra, India.

---

## 1. Directory Structure

```
backend/
├── README.md               # Backend architecture & developer guide (this file)
├── .env.example            # Template for local environment configuration
├── requirements.txt        # Python dependency manifest
├── alembic.ini             # Database migration configuration
├── alembic/                # Migration scripts and version history
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_schema.py
├── app/                    # Application source package
│   ├── main.py             # FastAPI entrypoint, middleware, lifespan hooks
│   ├── core/               # App configuration, settings, database session
│   │   ├── config.py       # Pydantic BaseSettings
│   │   ├── database.py     # Async SQLAlchemy engine & session factory
│   │   ├── exceptions.py   # Centralized error envelopes & handlers
│   │   ├── logging.py      # Structured application logging
│   │   └── security.py     # Password hashing & JWT token lifecycle
│   ├── api/                # API route definitions
│   │   └── v1/
│   │       ├── router.py   # Root v1 APIRouter
│   │       └── endpoints/
│   │           ├── auth.py         # User registration, login, profile
│   │           ├── feedback.py     # Accuracy feedback & ground truth
│   │           ├── health.py       # /health/live, /health/ready probes
│   │           ├── history.py      # Private prediction history (owner-only)
│   │           ├── localities.py   # Pune micro-markets & autocomplete
│   │           ├── models.py       # Active ML model metadata
│   │           └── predict.py      # Property price estimation
│   ├── models/             # SQLAlchemy declarative ORM models
│   │   ├── base.py
│   │   ├── user.py         # User credentials and state
│   │   ├── locality.py     # Pune localities
│   │   ├── model_metadata.py # Model registry
│   │   ├── prediction.py   # Prediction audit and user-linked history
│   │   ├── feedback.py     # Valuation feedback
│   │   └── saved_valuation.py # Bookmarks
│   ├── schemas/            # Pydantic v2 request/response schemas
│   │   ├── common.py       # Standard envelopes & pagination
│   │   ├── user.py         # Registration, login, token schemas
│   │   ├── prediction.py   # Estimation input/output schemas
│   │   ├── history.py      # Paginated history schemas
│   │   ├── locality.py     # Localities schemas
│   │   ├── feedback.py     # Feedback schemas
│   │   └── model_metadata.py
│   └── services/           # Business logic & ML inference adapters
│       ├── auth_service.py     # Authentication & token management
│       ├── history_service.py  # Ownership-verified history access
│       ├── ml_service.py       # Model artifact loading and inference wrapper
│       ├── locality_service.py # Locality queries and seeding
│       └── feedback_service.py # Valuation feedback
└── tests/                  # Automated test suite (pytest + HTTPX, 32 tests, 89% cov)
    ├── conftest.py         # Test fixtures and test database setup
    ├── test_health.py
    ├── test_ml_service.py
    ├── test_predict_api.py
    ├── test_auth_api.py
    ├── test_history_api.py
    ├── test_localities_api.py
    ├── test_feedback_api.py
    ├── test_models_api.py
    └── test_security.py
```

---

## 2. Technology Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python Web Framework)
- **Runtime:** Python 3.11+ / Python 3.14
- **Database Engine:** PostgreSQL hosted on [Supabase](https://supabase.com/) / SQLite local dev fallback
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Declarative Mappings + Asyncpg / aiosqlite driver)
- **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Testing Suite:** `pytest` + `pytest-asyncio` + `pytest-cov` + `httpx` (32 tests, 89% coverage)
- **Deployment Platform:** [Render](https://render.com/) Web Service

---

## 3. Architecture & Operational Patterns

1. **Lifespan ML Model Loading:**
   The active ML model artifact (`ml/models/pricenest_pune_model_v1.0.0_exp.joblib`) is loaded into application memory once during the FastAPI lifespan startup event (`@asynccontextmanager`) and cached in the application singleton service. Inference runs in-process in $< 2\text{ms}$ with zero external network overhead.
2. **Database Connection Pooling & Asynchrony:**
   FastAPI interacts with Supabase PostgreSQL using `asyncpg` via SQLAlchemy's async engine, configured with connection pooling (`pool_recycle=1800`, `pool_pre_ping=True`) compatible with Supabase's Supavisor pooler.
3. **Structured API Contracts & Standard Envelopes:**
   All endpoints strictly enforce Pydantic v2 models for request validation and response serialization, generating auto-documented OpenAPI 3.1 specifications available at `/docs` and `/redoc`.
4. **Resilience & Safe Fallbacks:**
   The prediction service validates input values against physical domain bounds (e.g., minimum 150 sq.ft. per BHK configuration, floor limit checks) and returns structured error messages (HTTP 422) if parameters are nonsensical.
5. **Private History & Owner Isolation:**
   Valuation records are persisted in `prediction_requests` and strictly owner-isolated (returns 404 on cross-user prediction lookups to prevent ID enumeration).

---

## 4. Local Development Workflow

1. **Environment Configuration:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env to configure local DATABASE_URL or use default SQLite
   ```
2. **Virtual Environment Setup:**
   ```bash
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
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. **Run Test Suite:**
   ```bash
   pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing
   ```
