# PriceNest — Technical Debt & Architectural Constraints

**Document Version:** 1.0.0  
**Last Updated:** October 2026  
**Status:** Active Tracking  
**Scope:** Covers Data Ingestion, ML Modeling, Backend Architecture, Security, and Cloud Deployments  

---

## 1. Overview & Purpose

This document tracks all known technical debt, synthetic data constraints, architectural trade-offs, and deferred engineering items across PriceNest. Every item is categorized with its operational risk level, affected subsystem, and planned resolution phase.

---

## 2. Technical Debt Registry

### Summary Matrix

| ID | Category | Item Description | Risk Level | Affected Subsystem | Planned Resolution |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **TD-DATA-01** | Dataset Fidelity | Decoupled BHK and Area Correlation ($r = 0.0041$) | High | `data/`, `ml/` | Phase 7 (Real Data Ingestion) |
| **TD-DATA-02** | Dataset Fidelity | Absence of Micro-Market Localities & Spatial Coordinates | High | `data/`, `backend/` | Phase 7 (MahaRERA Registry) |
| **TD-DATA-03** | Dataset Fidelity | Lack of Temporal Dynamics & Macroeconomic Factors | Medium | `data/`, `ml/` | Phase 7 (Temporal Modeling) |
| **TD-DATA-04** | Dataset Fidelity | Static Non-Physical Anomaly Cutoff ($< 200$ sq.ft.) | Low | `ml/src/` | Phase 3.2 (Outlier Engineering) |
| **TD-ML-01** | Modeling | Formula Reverse-Engineering vs Real Valuation ($R^2 \approx 0.75$) | High | `ml/`, `frontend/` | Mandatory UI/API Disclaimers |
| **TD-ML-02** | Modeling | Luxury Tail Under-Prediction Bias ($+₹22.81$ Lakhs on $> ₹200$L) | Medium | `ml/` | Phase 3.2 (Target Log Transform) |
| **TD-ML-03** | MLOps | Manual Model Versioning & Lack of Automated Registry (DVC/MLflow)| Low | `ml/models/` | Post-MVP / Phase 6 |
| **TD-BACK-01**| Backend Architecture| Embedded Model Inference in FastAPI Worker Process | Resolved | `backend/` | Resolved in Phase 4.0 (1.45ms latency) |
| **TD-BACK-02**| Backend Architecture| Uninitialized Alembic Database Migrations on Supabase | Resolved | `backend/alembic/` | Resolved in Phase 4.0 (`0001_initial_schema.py`) |
| **TD-BACK-03**| API Security | Absence of User Auth & Privacy on Public Prediction Endpoint | Resolved | `backend/app/` | Resolved in Phase 4.0 (JWT + SHA-256 IP hash) |
| **TD-OPS-01** | Git & CI/CD | GitHub PAT `workflow` Scope Requirement for CI Pipeline | Low | `.github/workflows/` | GitHub Token Scope Configuration |

---

## 3. Deep-Dive Item Descriptions

### 3.1. Data & Domain Fidelity Debt

#### TD-DATA-01: Decoupled BHK and Area Correlation
- **Observation:** In authentic residential housing (Pune municipal areas), physical square footage and bedroom count exhibit high correlation ($r \approx 0.70 - 0.85$). In the Kaggle dataset, the correlation is virtually zero ($r = 0.0041$). The generator produced 4-BHK units with 500 sq.ft. and 1-BHK units with 4,000 sq.ft.
- **Risk:** Models trained on this distribution do not penalize non-physical combinations (e.g., 5 BHK in 600 sq.ft.) naturally via data geometry.
- **Mitigation:** Enforce Pydantic validation boundaries on the API layer (`Super_Area_SqFt >= BHK * 250` warning or strict boundary checks) in Phase 4.

#### TD-DATA-02: Absence of Micro-Market Localities & Spatial Coordinates
- **Observation:** The dataset contains only a coarse 3-tier categorical column `Locality_Type` (`Affordable`, `Mid-Range`, `Premium`). It contains zero Pune neighborhood identifiers (e.g., Kothrud, Hinjewadi, Wakad, Baner, Kharadi, Viman Nagar, Magarpatta, Hadapsar) and zero geographic coordinates (latitude/longitude).
- **Risk:** Real estate prices in Pune vary heavily by micro-market (e.g., Koregaon Park vs. Wagholi). The model cannot distinguish between prime tech hubs and emerging suburbs within the same tier.
- **Mitigation:** In Phase 4/5, expose a curated Pune locality mapping in the database (`localities` table) that maps user-selected localities to their respective synthetic tier (`Affordable`, `Mid-Range`, `Premium`) with explicit UI disclosure.

#### TD-DATA-03: Lack of Temporal Dynamics & Macroeconomic Factors
- **Observation:** The dataset represents a static cross-sectional snapshot with no timestamp, sale date, or interest rate features.
- **Risk:** Unable to model inflation, RBI repo rate changes, construction material index shifts, or seasonal demand.
- **Mitigation:** Disclose static nature in the application methodology page; plan time-series ingestion for future real-world datasets.

#### TD-DATA-04: Static Non-Physical Anomaly Cutoff
- **Observation:** Filtered 14 records with `Super_Area_SqFt < 200` sq.ft. via hardcoded thresholding in `ml/src/train_baseline.py`.
- **Risk:** High-end outliers (e.g., properties with area $> 5,000$ sq.ft. or listed prices $> ₹500$ Lakhs) were retained without robust leverage/Cook's distance screening.
- **Mitigation:** Implement automated IQR/Isolation Forest outlier diagnostics before training production-grade models.

---

### 3.2. Machine Learning & Modeling Debt

#### TD-ML-01: Formula Reverse-Engineering vs Real Valuation
- **Observation:** The model achieved $R^2 = 0.7481$ and MAE = ₹32.48 Lakhs. Over 90% of model feature importance is concentrated in `Super_Area_SqFt` and `Locality_Type`.
- **Risk:** High statistical score gives a false illusion of real-world readiness. The model reverse-engineered the synthetic dataset generator's arithmetic formula, not genuine market transactions.
- **Mitigation:** Mandatory UI and API disclaimer badges must accompany every prediction response:
  > *"Illustrative estimate based on experimental synthetic data. Not valid for financial or legal valuation."*

#### TD-ML-02: Luxury Tail Under-Prediction Bias
- **Observation:** On properties priced above ₹200 Lakhs, the winning model exhibits a positive mean residual bias of $+₹22.81$ Lakhs and an elevated MAE of ₹70.68 Lakhs.
- **Risk:** High-value luxury homes and penthouses are systematically undervalued.
- **Mitigation:** In future model tuning, evaluate target log-transformation (`y_train = np.log1p(Price)`) or quantile loss regression to handle long-tail skewness.

#### TD-ML-03: Manual Model Versioning
- **Observation:** Model artifacts are manually saved as `.joblib` files under `ml/models/` without automated registry tracking (MLflow, Weights & Biases, or DVC).
- **Risk:** Risk of model drift or unversioned artifact overwrites as experiments scale.
- **Mitigation:** Version model files strictly with semantic naming conventions (e.g., `pricenest_pune_model_v1.0.0_exp.joblib`) and maintain JSON metric records.

---

### 3.3. Backend, Architecture & Operations Debt

#### TD-BACK-01: Embedded Model Inference in FastAPI Worker Process
- **Observation:** Loading the 554 KB `.joblib` pipeline into memory inside the FastAPI lifespan startup (`prediction_service.py`).
- **Risk:** While memory overhead is minimal (< 50 MB), multi-worker scaling on Render free/starter tiers must be benchmarked to prevent memory spikes.
- **Mitigation:** Implement warm startup profiling, caching of the pipeline singleton, and test concurrent latency under load in Phase 4.

#### TD-BACK-02: Uninitialized Alembic Database Migrations
- **Observation:** SQLAlchemy schemas exist as documentation designs in `docs/architecture/DATABASE_DESIGN.md`, but no live Alembic migrations have been run against Supabase PostgreSQL.
- **Risk:** Database drift if tables are created manually.
- **Mitigation:** Execute Phase 4 Step 1: scaffold Alembic async environment, create initial revision (`001_initial_schema.py`), and test automated up/down migrations.

#### TD-BACK-03: Public Prediction Endpoint Protection
- **Observation:** Phase 4 must expose `/api/v1/predict` to both guest visitors and authenticated users.
- **Risk:** Potential abuse or denial-of-service from automated scrapers.
- **Mitigation:** Implement sliding-window IP rate limiting (e.g., 20 requests/minute for anonymous users) and Pydantic request payload size limits.

#### TD-OPS-01: GitHub PAT `workflow` Scope Requirement
- **Observation:** Pushing commits containing `.github/workflows/` requires a Personal Access Token with the `workflow` scope.
- **Risk:** Rejection of git push if token permissions expire or lack the workflow scope.
- **Mitigation:** Ensure GitHub developer settings have the `workflow` checkbox enabled for active tokens.
