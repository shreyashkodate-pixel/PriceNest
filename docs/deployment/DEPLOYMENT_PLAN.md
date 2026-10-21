# PriceNest — Cloud Deployment Plan & Operational Runbook

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Project Foundation & Documentation  
**Deployment Targets:** Vercel (Frontend) | Render (Backend) | Supabase (Database)  
**Last Updated:** October 2026  

---

## 1. Cloud Architecture Overview

PriceNest is deployed across a best-in-class multi-cloud topology designed for high developer productivity, zero operational overhead, and robust isolation between presentation, application logic, and relational storage.

```mermaid
flowchart LR
    subgraph "Vercel Edge Network"
        VercelApp["Next.js Web App<br/>(Global CDN / Edge)"]
    end

    subgraph "Render Cloud Platform"
        RenderAPI["FastAPI Web Service<br/>(Docker / Python 3.11)"]
    end

    subgraph "Supabase Cloud"
        Pooler["Supavisor Pooler<br/>(Port 6543 / 5432)"]
        PostgresDB[("PostgreSQL 15+<br/>Relational Database")]
        Pooler --> PostgresDB
    end

    subgraph "Developer Workflow"
        GitHub["GitHub Repository<br/>(main / develop)"]
        GHA["GitHub Actions CI<br/>(Lint & Test)"]
        GitHub --> GHA
    end

    GitHub -->|"Auto Deploy"| VercelApp
    GitHub -->|"Auto Deploy"| RenderAPI
    VercelApp -->|"HTTPS REST API"| RenderAPI
    RenderAPI -->|"Asyncpg SSL"| Pooler
```

---

## 2. Environment Configuration Matrix

| Tier | Component | Platform | Primary URL Pattern | Key Environment Variables |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | Next.js App | Vercel | `https://pricenest.vercel.app` | `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_APP_NAME` |
| **Backend** | FastAPI Service | Render | `https://pricenest-api.onrender.com` | `DATABASE_URL`, `SYNC_DATABASE_URL`, `ALLOWED_ORIGINS`, `ACTIVE_MODEL_VERSION` |
| **Database** | PostgreSQL | Supabase | `db.<ref>.supabase.co:5432` | `POSTGRES_PASSWORD`, `DATABASE_URL` (injected into backend) |
| **CI/CD** | Actions Runner | GitHub | N/A | Automated PR status checks, linting, tests |

---

## 3. Deployment Runbook

### Phase A: Database Tier Provisioning (Supabase)
1. **Create Project:** Initialize a new Supabase project in the `ap-south-1` (Mumbai) region for lowest latency to Indian users.
2. **Retrieve Connection String:**
   - **Transaction Pooler URL (Supavisor, Port 6543):** For FastAPI asyncpg runtime connections.
   - **Session / Direct URL (Port 5432):** For running Alembic database migrations.
3. **Run Initial Alembic Migration:**
   ```bash
   cd backend
   alembic upgrade head
   ```
4. **Seed Pune Localities Reference Data:**
   ```bash
   python scripts/seed_localities.py
   ```

---

### Phase B: Backend API Tier Deployment (Render)
1. **Create Web Service:**
   - Connect the GitHub repository `shreyashkodate-pixel/PriceNest` to Render.
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
2. **Configure Environment Variables in Render Dashboard:**
   - `APP_ENV`: `production`
   - `DEBUG`: `False`
   - `PORT`: `10000`
   - `ALLOWED_ORIGINS`: `https://pricenest.vercel.app,https://*.vercel.app`
   - `DATABASE_URL`: `postgresql+asyncpg://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
   - `SYNC_DATABASE_URL`: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
   - `ACTIVE_MODEL_VERSION`: `v1.0.0`
   - `ACTIVE_MODEL_FILENAME`: `pricenest_pune_model_v1.0.0.joblib`
3. **Health Check Probe:**
   - Set Health Check Path to `/health` in the Render dashboard.
   - Render will verify that HTTP 200 is returned before routing public traffic to the new build.

---

### Phase C: Frontend Tier Deployment (Vercel)
1. **Import Project into Vercel:**
   - Connect GitHub repository `shreyashkodate-pixel/PriceNest`.
   - **Root Directory:** Select `frontend`.
   - **Framework Preset:** Next.js.
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
2. **Configure Environment Variables in Vercel Dashboard:**
   - `NEXT_PUBLIC_API_BASE_URL`: `https://pricenest-api.onrender.com/api/v1`
   - `NEXT_PUBLIC_APP_NAME`: `PriceNest`
3. **Deploy & Verify:**
   - Trigger build on branch `main`.
   - Verify Edge CDN caching and test calculator interactions against the Render backend.

---

## 4. Machine Learning Model Artifact Deployment Strategy

As defined in the system architecture:
- **Baseline Deployment (Phase 1-3):**
  - Model artifacts (`*.joblib`) are packaged with the backend build or copied from an artifact storage cache into `backend/app/models/` or `ml/models/` during the Render build phase.
  - FastAPI loads the model into application memory on startup via the `lifespan` handler.
- **Artifact Update Protocol:**
  - When a new model version is approved, the new `.joblib` file is versioned (e.g., `pricenest_pune_model_v1.1.0.joblib`), registered in `model_registry`, and the `ACTIVE_MODEL_VERSION` environment variable on Render is updated to trigger a zero-downtime rolling reload.

---

## 5. Rollback & Disaster Recovery Procedures

1. **Frontend Rollback:**
   - Instantly rollback to the previous successful deployment via the Vercel dashboard with zero downtime.
2. **Backend Rollback:**
   - Revert to the prior deployment commit in Render or redeploy the prior successful image.
3. **Database Migration Rollback:**
   - In the event of an unintended schema modification, execute:
     ```bash
     cd backend
     alembic downgrade -1
     ```
4. **Model Rollback:**
   - Update `ACTIVE_MODEL_VERSION` to the prior stable version (e.g., revert from `v1.1.0` back to `v1.0.0`). The lifespan handler immediately loads the fallback artifact.
