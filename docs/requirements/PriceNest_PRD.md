# PriceNest — Product Requirements Document (PRD)

**Product:** PriceNest  
**Version:** 1.0  
**Status:** Initial product baseline  
**Initial market:** Pune, Maharashtra, India  
**Currency:** Indian Rupee (INR)  
**Audience:** Product owner, AntiGravity, developers, testers, and future contributors

## 1. Product Vision

PriceNest is a residential real-estate price estimation platform that uses machine learning to estimate a property's likely completed-sale value from its characteristics and location.

The product will start with Pune and expand to other cities or regions only when suitable data, features, and model evaluation support that expansion.

PriceNest must be a credible engineering portfolio project, not merely a frontend demo connected to a random prediction formula. Its data processing, model evaluation, backend, persistence, security, and deployment must be reproducible and documented.

**Important distinction:** PriceNest estimates a property's likely value. It does not provide a certified valuation, guarantee a sale price, or replace a qualified valuer.

## 2. Problem Statement

Property buyers, sellers, and researchers often need an initial estimate of residential property value. PriceNest aims to make an estimate accessible through a straightforward interface while explaining the limitations of the model.

The primary technical challenge is developing a defensible estimation pipeline from imperfect real-estate data. Dataset provenance, feature availability, geographic coverage, leakage prevention, and evaluation quality are as important as the prediction algorithm.

## 3. Product Goals

1. Build a working residential property price estimation application.
2. Establish a reproducible data ingestion, validation, exploration, training, evaluation, and inference workflow.
3. Initially investigate Pune residential properties.
4. Provide a clear web interface for entering property details and viewing an estimated price.
5. Support user accounts and private prediction history in the initial product scope.
6. Store prediction records and relevant model-version information.
7. Provide maintainable APIs, automated tests, migrations, and deployment documentation.
8. Distinguish experimental predictions from predictions supported by credible market data.
9. Keep the architecture extensible to additional locations and future models without premature complexity.

## 4. Non-Goals

The initial product will not:

- Guarantee a property's actual sale price.
- Provide legally certified valuations, lending decisions, or investment advice.
- Execute property purchases, sales, rentals, or brokerage transactions.
- Scrape websites or obtain private transaction records without authorization.
- Claim that synthetic Kaggle data represents genuine Pune transactions.
- Deploy an unvalidated model as a trustworthy production valuation service.
- Require microservices, a separate ML-serving service, or a complex orchestration platform for the MVP.
- Introduce payments, chat, social features, or unrelated real-estate marketplace functionality.
- Expand to additional cities solely because a location selector can display them.

## 5. Target Users

### 5.1 Property Explorer
A user who wants an indicative price estimate based on location and property characteristics.

### 5.2 Registered User
A user who wants to save estimates and revisit previous predictions privately.

### 5.3 Project Maintainer
The developer who inspects datasets, trains models, reviews metrics, manages model versions, and maintains the application.

### 5.4 Administrator
A future authorized operational role for managing model releases and approved application settings, if needed. Do not implement a large administrative console unless a specific requirement is approved.

## 6. MVP Scope and Features

### F-01: Property Price Estimation
Users can enter supported residential property details and request an estimate. The interface displays the estimated amount in INR, the supported location, and an appropriate explanation of uncertainty and model limitations.

The input fields must be determined from the audited dataset and intended inference features. Do not expose inputs that the model cannot use reliably.

### F-02: Location Support
Pune is the initial target market. Locality selection must use a controlled, validated list of supported locations where possible.

The initial supported geographic coverage must be documented. PMC, PCMC, and PMRDA must not be treated as interchangeable administrative areas without an explicit mapping.

### F-03: User Accounts
The application must support registration, login, logout, and authenticated access to private user resources. The authentication mechanism must be selected and documented before implementation; do not invent an identity provider or hardcode credentials.

### F-04: Prediction History
Authenticated users can view their own saved prediction records. A record should include the input snapshot, estimated value, timestamp, and model version where available.

Users must not be able to access another user's private history.

### F-05: Prediction Details
The result should display the estimated price, supported input summary, and relevant disclaimer. Additional ranges or confidence indicators must be displayed only when the underlying model or evaluation supports them.

### F-06: Data and Model Workflow
The maintainer can validate a dataset, conduct EDA, engineer features, compare baseline models, evaluate a final candidate, and package the selected preprocessing and estimator pipeline for inference.

Training and inference must use consistent preprocessing. Model selection must be based on held-out evaluation, not training scores alone.

### F-07: Feedback
The architecture may support optional user feedback about an estimate. Feedback must be stored separately from verified sale prices. It must not automatically become training ground truth.

### F-08: Health and Diagnostics
The backend exposes a minimal health endpoint suitable for monitoring. It must not disclose credentials, private records, stack traces, or internal configuration.

### F-09: Responsive and Accessible UI
The frontend must work on desktop and mobile layouts, provide accessible labels, handle validation errors, and display loading, success, empty, and failure states.

## 7. Core User Journeys

### Journey A: Obtain an Estimate
1. User opens the estimation page.
2. User selects a supported location and enters property details.
3. Frontend validates required inputs.
4. Backend validates the request again.
5. The inference pipeline generates an estimate using the active model.
6. User sees the result, relevant details, and limitations.
7. If the user is authenticated, the application may save the prediction according to the documented persistence policy.

### Journey B: Review History
1. User signs in.
2. User opens prediction history.
3. Backend returns only records owned by that user.
4. User can open a saved record and review its input snapshot and estimate.

### Journey C: Prepare a Model
1. Maintainer records the dataset's origin and intended use.
2. Data validation and exploratory analysis identify quality limitations.
3. A reproducible split is created, with leakage controls appropriate to the data.
4. Baseline and candidate models are trained.
5. Models are evaluated using appropriate metrics and error analysis.
6. The selected pipeline and metadata are versioned.
7. Deployment is blocked if required quality and provenance checks fail.

## 8. Product and Model Quality Principles

- **Honesty:** Never imply that synthetic data produces verified real-market accuracy.
- **Reproducibility:** Record data provenance, preprocessing, model configuration, evaluation results, and relevant package versions.
- **Consistency:** Training and inference must apply the same fitted preprocessing.
- **Privacy:** User prediction history is private and access-controlled.
- **Maintainability:** Prefer a modular monolith and simple deployment architecture.
- **Evidence-based releases:** Do not approve a model based solely on a high score or one metric.

## 9. Success Criteria

The MVP is considered technically ready when:

1. The documented setup can be reproduced on a clean development environment.
2. Backend and frontend checks pass.
3. Database migrations can create the required schema from a clean database.
4. API validation and error behavior are covered by tests.
5. A trained model can be loaded and used through the documented inference interface.
6. Inference preprocessing matches the training pipeline.
7. Users cannot access other users' private records.
8. Prediction history behaves consistently with the documented persistence policy.
9. Model evaluation includes at least MAE, RMSE, and R² where appropriate, plus residual/error analysis.
10. The data source, limitations, supported geography, and model version are documented.
11. The deployed application never claims verified market accuracy without supporting evidence.

Numerical accuracy thresholds must be set after dataset audit and baseline evaluation. Do not invent an acceptable MAE before inspecting the target-price distribution and intended use.

## 10. Initial Technology Decisions

- Frontend: Next.js with TypeScript.
- Backend: Python with FastAPI.
- Database: PostgreSQL hosted on Supabase.
- ORM and migrations: SQLAlchemy and Alembic.
- ML: Pandas, NumPy, Matplotlib, Seaborn, scikit-learn, and joblib.
- Backend testing: pytest and HTTPX.
- Frontend testing: select and document suitable tools for the existing frontend setup.
- Deployment targets: Vercel for the frontend, Render for the backend, Supabase for PostgreSQL.
- Model hosting: deliberately deferred until the training and inference pipeline is established.

## 11. Data Strategy

The initial Kaggle dataset is for pipeline development and experimentation. Its actual schema, target column, license, provenance, and synthetic status must be confirmed through inspection of the downloaded files and source documentation.

Do not assume a dataset is Pune-specific because Pune appears in a filename or a city column.

Raw datasets must remain local and excluded from Git by default. Record dataset versions, acquisition source, applicable license, and transformations. Later market-facing claims require suitable real-world data and credible evaluation.

## 12. Delivery Phases

- **Phase 1 — Foundation:** Repository structure, PRD/SRS, architecture, initial documentation, and Git hygiene.
- **Phase 2 — Dataset audit and EDA:** Verify source, schema, quality, target, licensing, and feasibility.
- **Phase 3 — ML baseline:** Build reproducible preprocessing, baseline models, evaluation, and model documentation.
- **Phase 4 — Backend foundation:** API, persistence, migrations, validation, and inference integration.
- **Phase 5 — Frontend:** Estimation interface, account flows, results, and history.
- **Phase 6 — Integration and hardening:** Security, automated tests, error handling, accessibility, and end-to-end verification.
- **Phase 7 — Deployment:** Deploy only after environment, model readiness, and acceptance checks pass.
- **Phase 8 — Real-data readiness and expansion:** Reassess market suitability, monitor errors, and consider additional locations.

## 13. Change Control

This PRD is the product-level source of truth. AntiGravity must:

1. Read this PRD and the SRS before implementing a phase.
2. Inspect existing code and documentation before changing files.
3. Identify conflicts rather than silently choosing a different requirement.
4. Document proposed requirement changes and their rationale.
5. Never change the approved stack, security posture, or scope without explicit approval.
6. Update documentation and tests when an approved requirement changes.
7. Report implemented, tested, deferred, and unverified items separately.

## 14. Open Decisions

The following decisions require evidence or explicit approval before implementation:
- Exact dataset and its licensing and provenance.
- Supported inference features and target-price semantics.
- Authentication mechanism and session/token lifecycle.
- Model acceptance thresholds.
- Prediction retention and deletion policy.
- Whether users can delete individual history records.
- Model hosting and release strategy.
- Whether uncertainty ranges are statistically supportable.
- Real transaction data source and permitted use.

Do not silently resolve these decisions by inventing product behavior.
