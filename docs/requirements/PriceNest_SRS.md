# PriceNest — Software Requirements Specification (SRS)

**Version:** 1.0  
**Status:** Initial engineering specification  
**Normative terms:** “MUST” means mandatory; “SHOULD” means recommended unless a documented reason justifies otherwise; “MAY” means optional.

## 1. Purpose and Scope

This document specifies the software behavior, component boundaries, data requirements, APIs, security, ML inference, testing, and operational requirements for PriceNest.

It complements `PRD.md`, which defines the product goals and user needs. If an implementation detail conflicts with the PRD, AntiGravity must report the conflict instead of silently changing either specification.

## 2. System Architecture

### 2.1 Components

**Frontend**
- Next.js with TypeScript.
- Provides pages and reusable components for estimation, authentication, results, and private history.
- Calls the backend through a centralized typed service/API layer.
- Handles loading, empty, validation, and error states.
- Does not contain the authoritative ML prediction logic or database credentials.

**Backend**
- Python and FastAPI.
- Owns request validation, authentication enforcement, authorization, business logic, persistence, and inference orchestration.
- Uses SQLAlchemy for database access and Alembic for schema migrations.
- Exposes versioned REST APIs under `/api/v1`.

**Database**
- PostgreSQL hosted on Supabase.
- Development configuration must also support a documented local database workflow where practical.
- The database connection must be configured through environment variables.
- Schema changes must be represented by migrations, not manual production-only edits.

**ML package**
- Reusable Python package for data validation, preprocessing, training, evaluation, artifact metadata, and inference.
- Uses Pandas, NumPy, scikit-learn, and joblib as appropriate.
- Training code must be separate from request-time inference code.
- The initial inference integration may run in the FastAPI process.
- Separate model hosting is deferred until evidence demonstrates a need.

### 2.2 Request lifecycle

1. Frontend collects and validates property inputs.
2. Backend validates the request against the authoritative schema.
3. Backend resolves the active model and its supported input contract.
4. The model pipeline transforms inputs using the fitted preprocessing steps.
5. The estimator returns a prediction in its documented target units.
6. Backend validates the result, converts it to the canonical API representation, and applies the documented persistence policy.
7. Frontend displays the result and any applicable limitations.

A failed model load, invalid model output, or unavailable required dependency must not silently fall back to a hardcoded estimate.

## 3. Functional Requirements

### FR-01: Property Estimation

- The API MUST accept a documented property-estimation request.
- The backend MUST validate required fields, types, ranges, and categorical values.
- The API MUST reject unsupported locations or features when the active model does not support them.
- The backend MUST invoke the active fitted pipeline, not duplicate training transformations inside an endpoint.
- The response MUST identify the estimate, currency, and model version when available.
- The application MUST display a limitation notice appropriate to the dataset and model.
- The system MUST NOT return a fabricated prediction when the model is unavailable.

### FR-02: Input Validation

- Validation MUST occur on the server even if the frontend validates the same fields.
- Invalid inputs MUST produce a stable client-error response.
- Numeric inputs MUST be finite; NaN and infinite values MUST be rejected.
- Unit conventions MUST be explicit for area, room counts, building age, and other numeric features.
- Missing-value handling MUST match the fitted training pipeline and model contract.
- The system MUST NOT silently reinterpret square feet as square metres or vice versa.
- Validation bounds MUST be based on documented feature definitions and verified data, not arbitrary assumptions.

### FR-03: Location Support

- The initial target geography is Pune, Maharashtra.
- The set of supported localities MUST be explicitly defined and versioned.
- Locality identifiers or normalized values SHOULD be used to avoid inconsistent free-text matching.
- The backend MUST reject or clearly mark unsupported geography.
- City expansion MUST require data coverage, model evaluation, and an approved configuration change.

### FR-04: Authentication

- Authentication MUST be selected and documented before protected endpoints are implemented.
- Passwords, if managed by the application, MUST never be stored in plaintext.
- Authentication tokens or session identifiers MUST not be logged.
- Protected endpoints MUST authenticate the caller and enforce authorization.
- Logout and session/token expiry MUST follow the selected authentication design.
- Secrets MUST be provided through environment configuration or an approved secret manager.
- No API keys, database passwords, or signing secrets may be committed to Git.

### FR-05: Prediction History

- Authenticated users MUST be able to retrieve only their own history.
- A saved record SHOULD contain an input snapshot, estimate, currency, timestamp, model version, and relevant status.
- History retrieval MUST support bounded pagination and deterministic ordering.
- The API MUST NOT allow a client to select another user's identity as an authorization shortcut.
- The database query MUST enforce ownership through the authenticated identity.
- Anonymous prediction persistence MUST follow an explicit approved policy.
- Retention and deletion behavior MUST be documented before those features are implemented.

### FR-06: Database and Migrations

- SQLAlchemy models and Alembic migrations MUST remain consistent.
- A clean database MUST be buildable using the documented migration process.
- Schema changes MUST be committed as migration files.
- Database transactions MUST be used for operations that require atomicity.
- Database constraints SHOULD enforce important invariants in addition to application validation.
- Indexes MUST be introduced based on query requirements and justified access patterns.
- The application MUST not depend on undocumented manual database changes.
- Connection pools and database timeouts MUST be configured appropriately for the deployment environment.

### FR-07: ML Training Pipeline

- Training MUST be reproducible from documented inputs and configuration.
- Data ingestion, validation, preprocessing, training, and evaluation MUST have clear responsibilities.
- The training process MUST record dataset provenance and the target definition.
- Train/test splitting MUST prevent leakage and reflect the dataset's structure. Where repeated projects, locations, or time periods create leakage risk, the split strategy MUST account for it.
- Preprocessing steps that learn from data MUST be fitted only on the training split during evaluation.
- Baseline models MUST be evaluated before selecting a more complex candidate.
- The chosen model MUST be evaluated on held-out data.
- Training MUST report MAE, RMSE, and R² when appropriate for the target and evaluation setup. MAPE MAY be reported only with a documented explanation of its limitations, especially near zero targets.
- Evaluation SHOULD include residual analysis, segment-level errors, and comparisons against a simple baseline.
- Model performance claims MUST identify the evaluation dataset and its limitations.

### FR-08: Model Artifacts and Inference

- The fitted preprocessing and estimator SHOULD be stored as one pipeline artifact where feasible.
- Artifacts MUST be versioned and accompanied by metadata.
- Metadata SHOULD include model version, training timestamp, dataset identifier, feature schema, target definition, evaluation metrics, and relevant package versions.
- Artifact loading MUST validate the expected schema and compatible package/runtime versions.
- The inference interface MUST validate inputs and outputs.
- The system MUST reject non-finite, malformed, or otherwise invalid model outputs.
- Model files MUST not be loaded from arbitrary user-provided paths.
- Deserializing joblib or pickle files MUST be restricted to trusted artifacts.
- Missing or incompatible artifacts MUST produce a controlled service error and an operational log entry.

### FR-09: Feedback

- Feedback MUST be stored separately from model training labels.
- Feedback MUST not automatically modify the active model or training dataset.
- If feedback is implemented, the API MUST validate its schema and enforce appropriate access controls.
- Any later use of feedback for training MUST require a documented quality-control and provenance process.

### FR-10: Health and Diagnostics

- The backend MUST expose a minimal liveness endpoint.
- Readiness checks MAY verify required dependencies separately from liveness.
- Health responses MUST not expose secrets, stack traces, or private database content.
- Application logs MUST record useful diagnostic context without sensitive request data.
- Error messages returned to clients MUST be safe and consistent.

## 4. API Requirements

### 4.1 General conventions

- Base prefix: `/api/v1`.
- Content type: JSON for standard API requests and responses.
- API schemas MUST be defined using Pydantic models and reflected in OpenAPI.
- API endpoints MUST have documented request fields, response fields, authentication requirements, status codes, and error cases.
- The frontend MUST use typed interfaces that match the backend contract.
- Breaking API changes MUST be versioned or handled through a documented migration plan.

### 4.2 Proposed initial endpoint inventory

| Method and path | Purpose | Access |
|---|---|---|
| `GET /health/live` | Confirm the process is alive | Public |
| `GET /health/ready` | Optional dependency readiness check | Public, minimal response |
| `POST /api/v1/predict/price` | Estimate a property's price | Public or authenticated according to approved policy |
| `GET /api/v1/localities` | List supported localities | Public |
| `GET /api/v1/history` | Retrieve prediction history | Authenticated |
| `GET /api/v1/history/{prediction_id}` | Retrieve one saved prediction | Authenticated and owner-only |
| Authentication endpoints | Register, log in, log out, or refresh sessions if required | According to the chosen auth design |
| Feedback endpoint | Submit optional feedback | According to approved policy |

This inventory is a starting contract. Existing documentation and implementation must be reviewed for conflicts before endpoints are finalized.

### 4.3 Prediction request contract

The exact input fields MUST be derived from the verified dataset, feature engineering decisions, and inference requirements. Do not assume a fixed list of features before the dataset audit.

The request MUST include only supported fields and documented units. Unknown fields MUST be handled consistently through the declared schema policy.

### 4.4 Prediction response contract

The response SHOULD contain:
- A numeric estimate in INR.
- The currency identifier `INR`.
- The resolved location, where applicable.
- A model version or model identifier.
- A disclaimer or result-status indicator where appropriate.
- A timestamp if part of the finalized API convention.

The estimate's numeric representation MUST be documented. The API MUST not use a formatted currency string as the sole machine-readable numeric value.

### 4.5 Error contract

Use the repository's established error envelope if one has already been approved. Otherwise define and document a consistent schema, for example:

- `success`: boolean.
- `data`: response payload or null.
- `error`: stable error code and safe message or null.
- `timestamp`: response timestamp.

The exact envelope MUST be consistent across endpoints. Do not maintain competing response formats.

Expected status classes include:
- `2xx`: successful operation.
- `400` or `422`: invalid request, according to the chosen validation convention.
- `401`: authentication required or invalid.
- `403`: authenticated caller lacks permission.
- `404`: resource unavailable or not found.
- `409`: conflicting state where applicable.
- `429`: rate limit exceeded where configured.
- `500`: unexpected server failure.
- `503`: required inference or service dependency unavailable.

The API MUST not expose internal exception messages or stack traces in production.

## 5. Data Requirements

### 5.1 Dataset provenance

Every training dataset MUST have a documented source, acquisition date where known, license or usage constraints, schema, target definition, and known limitations.

Synthetic datasets MUST be labelled as synthetic when supported by reliable evidence. Unverified provenance MUST be explicitly labelled unverified.

### 5.2 Data validation

The validation workflow MUST examine:
- File readability and encoding.
- Row and column counts.
- Duplicate rows and candidate duplicate entities.
- Missing values.
- Column types and parsing errors.
- Target values and units.
- Impossible or suspicious ranges.
- Categorical cardinality and inconsistent labels.
- Geographic coverage.
- Potential target leakage.
- Train/test overlap and repeated-entity leakage.
- Data licensing and permitted use.

A failed validation check MUST be reported rather than silently discarded.

### 5.3 Storage and versioning

- Raw datasets MUST remain unchanged during analysis.
- Raw and processed datasets MUST be excluded from Git by default unless a dataset is explicitly approved for version control.
- Data transformations MUST be reproducible and documented.
- Large model artifacts MUST not be committed by default.
- Dataset and artifact references MUST be traceable from experiment reports.

## 6. Database Requirements

The database design MUST support users, prediction records, and any additional approved entities.

Potential entities include:
- Users or authentication references.
- Prediction records.
- Supported localities.
- Model registry metadata.
- Optional valuation feedback.
- Optional saved valuations, if distinct from ordinary history.

The final schema MUST be driven by actual product requirements. Do not implement every proposed entity merely because it appears in an early architecture diagram.

Each entity MUST define its primary key, required fields, constraints, timestamps where appropriate, and ownership/access rules. Foreign keys and indexes MUST be justified. Sensitive authentication data MUST be handled according to the selected authentication architecture.

## 7. Security and Privacy

- The backend MUST enforce authorization independently of frontend visibility.
- Database credentials and signing secrets MUST remain outside source control.
- `.env`, `.env.local`, and equivalent secret-bearing files MUST be ignored by Git.
- `.env.example` files MUST contain placeholders only.
- CORS MUST allow only the required configured origins in deployed environments.
- Requests MUST be validated and bounded to reduce abuse and resource exhaustion.
- Rate limiting SHOULD protect expensive prediction and authentication endpoints where appropriate.
- Passwords and tokens MUST never be logged.
- Logs MUST avoid unnecessary personal information and sensitive property/user data.
- User-specific records MUST be protected against insecure direct object reference vulnerabilities.
- Database access MUST use parameterized ORM/query operations rather than unsafe string concatenation.
- Production error responses MUST be sanitized.
- Dependency updates and deployment configuration MUST be reviewed for security impact.

If row-level security is introduced in Supabase, its policies MUST be tested. RLS is not a substitute for application authorization.

## 8. Non-Functional Requirements

### NFR-01: Maintainability
Code MUST be organized into clear modules. API endpoints MUST delegate non-trivial business logic to services or equivalent modules. Shared logic MUST not be duplicated across frontend, backend, and training scripts.

### NFR-02: Reliability
Failures in the database, model loading, validation, or external dependencies MUST be handled explicitly. No fake success response or silent fallback is permitted.

### NFR-03: Performance
Measure API latency and model inference time under representative conditions. Establish quantitative service targets after a baseline is available. Avoid claiming a specific response-time guarantee without measurement.

### NFR-04: Reproducibility
Document supported runtime versions, dependency installation, environment variables, migrations, test commands, and model training commands. Use pinned or constrained dependencies where appropriate.

### NFR-05: Accessibility and usability
Frontend forms MUST have labels, keyboard-operable controls, readable error messages, responsive layouts, and clear status feedback.

### NFR-06: Observability
Use structured, useful application logs. Logs MUST not contain secrets. Record failures and enough context to diagnose them without exposing private records.

### NFR-07: Portability
The application MUST support local development and the approved deployment targets without embedding machine-specific absolute paths or credentials.

### NFR-08: Scalability
Prefer a modular monolith initially. Introduce queues, separate inference services, caching, or additional infrastructure only when demonstrated requirements justify them.

### NFR-09: Compatibility
Frontend request types, Pydantic schemas, database migrations, and model feature schemas MUST remain consistent. Automated tests SHOULD catch contract drift.

## 9. Testing Requirements

### 9.1 Backend
Tests MUST cover:
- Request and response validation.
- Successful and failed prediction paths.
- Model missing or incompatible.
- Database persistence and migration behavior.
- Authentication and authorization.
- User history ownership.
- Not-found and invalid-input cases.
- Safe error responses.
- Health endpoints.

Use pytest and HTTPX for suitable API tests. Isolate tests from production data and credentials.

### 9.2 ML
Tests MUST cover:
- Dataset schema validation.
- Missing and invalid data handling.
- Preprocessing fitted without leakage.
- Training pipeline execution on a small controlled fixture.
- Artifact serialization and loading.
- Inference schema validation.
- Finite and correctly typed predictions.
- Consistency between training and inference preprocessing.

### 9.3 Frontend
Tests SHOULD cover:
- Form validation.
- Loading, success, empty, and failure states.
- API error handling.
- Protected pages and unauthorized access behavior.
- History rendering.
- Responsive and accessible interaction basics.

### 9.4 Integration
Integration checks MUST verify that frontend contracts match backend schemas, backend inference can load the selected model artifact, and migrations work in a clean test database.

Tests MUST not require sending real emails, charging payments, or contacting external production services unless explicitly approved for a separate test.

## 10. Configuration and Deployment

- Frontend target: Vercel.
- Backend target: Render.
- Database target: Supabase PostgreSQL.
- Model hosting: deferred.
- Each environment MUST have explicit configuration and no committed secrets.
- Database migrations MUST be run through a documented controlled process.
- Production deployment MUST verify health, model availability, database connectivity, CORS, and authentication configuration.
- Rollback instructions MUST be documented for backend and model releases.
- A failed deployment MUST not be treated as successful merely because the build completed.

## 11. Development Workflow Requirements

Before each phase, AntiGravity MUST:
1. Read this SRS, the PRD, and relevant architecture/API/database documentation.
2. Inspect the current Git branch, status, files, and tests.
3. Identify dependencies and decisions that remain unresolved.
4. Propose the smallest implementation scope for the phase.
5. Avoid unrelated refactoring and overwriting user changes.
6. Implement in small, reviewable steps.
7. Run relevant tests and report exact commands and outcomes.
8. Update documentation when contracts or behavior change.
9. List files changed, known limitations, and follow-up work.
10. Stop at the specified phase boundary.

AntiGravity MUST NOT read secrets, install services, modify remote settings, deploy, commit, or push unless the user explicitly authorizes the relevant action.

## 12. Definition of Done

A feature is complete only when:
- Its requirement and acceptance criteria are traceable.
- Implementation and error paths are present.
- Input validation and access controls are implemented where required.
- Relevant automated tests pass.
- Documentation matches actual behavior.
- No secrets or unintended data are committed.
- The final report distinguishes verified behavior from assumptions or pending work.

A model is not production-ready merely because training completed. It must have verified provenance, suitable evaluation, an inference-compatible artifact, documented limitations, and approved release criteria.

## 13. Requirement Traceability

Every major feature SHOULD map to:
- One or more PRD feature IDs.
- Relevant SRS functional requirements.
- API/schema/database changes where applicable.
- Automated tests.
- A phase acceptance checklist.

Maintain this traceability as the project evolves.

## 14. Unresolved Decisions

Do not silently invent:
- Dataset identity, licensing, or real-world provenance.
- Target price semantics or feature meanings.
- Final model accuracy thresholds.
- Authentication provider or token lifecycle.
- Prediction retention and deletion rules.
- Supported area units and conversion policy.
- Production model hosting and release strategy.
- Confidence intervals or valuation ranges.
- Production service-level guarantees.

Document each decision, the evidence required, and the point at which approval is needed.
