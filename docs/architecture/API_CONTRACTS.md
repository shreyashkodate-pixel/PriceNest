# PriceNest — API Specification & Interface Contracts

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Project Foundation & Documentation  
**Base Protocol:** HTTPS / JSON REST  
**OpenAPI Specification Target:** OpenAPI 3.1  
**Last Updated:** October 2026  

---

## 1. Global API Standards

- **Base URL:** `/api/v1`
- **Request Headers:**
  - `Content-Type: application/json`
  - `Accept: application/json`
  - `X-Session-ID: <uuid>` (Optional client session tracking header)
- **Character Encoding:** UTF-8
- **Date/Time Standard:** ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`)
- **Currency Convention:** Base values are non-negative numeric floats/decimals in Indian Rupees (INR). Display fields use standard Indian numbering terms:
  - **Lakhs (L):** $1\text{ Lakh} = 100,000\text{ INR} = 10^5\text{ INR}$
  - **Crores (Cr):** $1\text{ Crore} = 10,000,000\text{ INR} = 10^7\text{ INR}$

---

## 2. Standard Response Envelopes

### 2.1 Standard Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### 2.2 Standard Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The property parameters provided fail physical feasibility checks.",
    "details": [
      {
        "field": "total_sqft",
        "issue": "Area must be at least 300 sq.ft. for a 1 BHK."
      }
    ]
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

---

## 3. Endpoints Specification

### 3.1 System Health & Diagnostics (SRS Section 4.2 & FR-10)

#### `GET /health/live`
Liveness probe confirming the server process is responsive.
- **Access:** Public
- **Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

#### `GET /health/ready`
Readiness probe verifying database connectivity and active model availability without disclosing internal configuration or stack traces.
- **Access:** Public
- **Response:** `200 OK`
```json
{
  "status": "ready",
  "database": "connected",
  "model_engine": "available"
}
```

*(Note: `GET /health` is maintained as a root alias for cloud container orchestration probes on Render).*

---

### 3.2 Property Price Estimation

> [!NOTE]
> **Provisional Contract Notice:**
> Per PRD Section 6 (F-01, F-05) and SRS Section 4.3, the authoritative input fields and physical validation bounds MUST be determined from the verified dataset during Phase 2 EDA. The fields and bounds listed below represent the initial domain baseline and are subject to confirmation. Similarly, price ranges and confidence scores will only be displayed if statistically supported by model evaluation.

#### `POST /api/v1/predict/price`
Calculates an estimated market valuation for a residential property in Pune.


**Request Body:**
```json
{
  "locality_name": "Baner",
  "locality_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "total_sqft": 1050.0,
  "bhk": 2.0,
  "bathrooms": 2,
  "balconies": 1,
  "furnishing": "semi_furnished",
  "property_age": "1_5_years",
  "parking": 1
}
```

**Field Validation Constraints:**
| Field | Type | Required | Constraints |
| :--- | :--- | :--- | :--- |
| `locality_name` | String | Yes | Minimum 2 characters. Validated against Pune localities. |
| `locality_id` | UUID | No | Optional UUID foreign key to `localities` table. |
| `total_sqft` | Float | Yes | Minimum $200.0$, Maximum $25,000.0$. Must satisfy $total\_sqft \ge bhk \times 150$. |
| `bhk` | Float | Yes | Minimum $1.0$, Maximum $10.0$ (supports fractional values like $2.5$). |
| `bathrooms` | Integer | Yes | Minimum $1$, Maximum $10$. |
| `balconies` | Integer | No | Minimum $0$, Maximum $6$. Default: $1$. |
| `furnishing` | Enum | No | Values: `unfurnished`, `semi_furnished`, `fully_furnished`. Default: `unfurnished`. |
| `property_age` | Enum | No | Values: `under_construction`, `new`, `1_5_years`, `5_10_years`, `10_plus_years`. |
| `parking` | Integer | No | Minimum $0$, Maximum $5$. Default: $1$. |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "prediction_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "predicted_price_inr": 8250000.00,
    "formatted_price": "₹82.50 Lakh",
    "price_range": {
      "min_inr": 7800000.00,
      "max_inr": 8700000.00,
      "formatted_range": "₹78.00 L – ₹87.00 L"
    },
    "per_sqft_rate_inr": 7857.14,
    "formatted_per_sqft_rate": "₹7,857 / sq.ft.",
    "confidence_score": 0.88,
    "feature_breakdown": {
      "locality_premium_pct": 14.2,
      "size_contribution_inr": 6500000.00,
      "amenities_adjustment_inr": 1750000.00
    },
    "model_metadata": {
      "version": "v1.0.0",
      "algorithm": "HistGradientBoostingRegressor",
      "latency_ms": 8.35
    },
    "disclaimer": "This estimate is generated algorithmically for educational and developmental purposes using an exploratory dataset. It does not represent a certified real-estate valuation or legal deed record."
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

---

### 3.3 Pune Micro-Market Localities

#### `GET /api/v1/localities`
Returns a list of supported Pune micro-markets with optional zone filtering and search queries.

**Query Parameters:**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | String | No | Search substring for locality name autocomplete. |
| `zone` | String | No | Filter by zone: `West Pune`, `East Pune`, `Central Pune`, `PCMC`, `PMRDA`. |
| `limit` | Integer | No | Number of records to return (Default: $50$, Max: $200$). |
| `offset` | Integer | No | Pagination offset (Default: $0$). |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 42,
    "items": [
      {
        "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "name": "Baner",
        "slug": "baner",
        "zone": "West Pune",
        "pincode": "411045",
        "benchmark_price_per_sqft": 8200.0,
        "is_active": true
      },
      {
        "id": "e3e7f2a1-8d23-4e89-a21b-6cb8f1920194",
        "name": "Wakad",
        "slug": "wakad",
        "zone": "PCMC",
        "pincode": "411057",
        "benchmark_price_per_sqft": 7100.0,
        "is_active": true
      }
    ]
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

---

### 3.4 User Authentication & Session Management (PRD F-03, SRS FR-04)

#### `POST /api/v1/auth/register`
Registers a new user account with validated email and secure password.
- **Access:** Public
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Pooja Deshmukh"
}
```
- **Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "full_name": "Pooja Deshmukh"
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

#### `POST /api/v1/auth/login`
Authenticates user credentials and issues an access token/session.
- **Access:** Public
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

#### `GET /api/v1/auth/me`
Retrieves authenticated user profile.
- **Access:** Authenticated (Bearer Token / Session)
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "full_name": "Pooja Deshmukh"
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

---

### 3.5 Private Prediction History (PRD F-04, SRS FR-05)

#### `GET /api/v1/history`
Retrieves bounded, paginated prediction records owned strictly by the authenticated caller.
- **Access:** Authenticated (Owner-only)
- **Query Parameters:**
  - `limit` (int, default: 20, max: 100)
  - `offset` (int, default: 0)
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 3,
    "items": [
      {
        "prediction_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "locality_name": "Baner",
        "total_sqft": 1050.0,
        "bhk": 2.0,
        "predicted_price_inr": 8250000.00,
        "formatted_price": "₹82.50 Lakh",
        "model_version": "v1.0.0",
        "created_at": "2026-10-21T14:30:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

#### `GET /api/v1/history/{prediction_id}`
Retrieves full snapshot details of one saved prediction owned by the authenticated caller.
- **Access:** Authenticated (Strict ownership check; unauthorized callers receive 404/403)
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "prediction_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "locality_name": "Baner",
    "input_features": {
      "total_sqft": 1050.0,
      "bhk": 2.0,
      "bathrooms": 2
    },
    "predicted_price_inr": 8250000.00,
    "formatted_price": "₹82.50 Lakh",
    "model_version": "v1.0.0",
    "created_at": "2026-10-21T14:30:00Z"
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

---

### 3.6 Valuation Feedback

#### `POST /api/v1/valuations/{prediction_id}/feedback`
Allows users to submit accuracy feedback or report known ground-truth transaction pricing.

**Path Parameter:**
- `prediction_id` (UUID): ID returned by `POST /api/v1/predict/price`.

**Request Body:**
```json
{
  "feedback_type": "accurate",
  "reported_actual_price_inr": 8100000.00,
  "comments": "Matches recent purchase in a neighboring society."
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "feedback_id": "b4897210-47bf-4e6f-9988-cb94317a264a",
    "prediction_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "status": "recorded"
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

---

### 3.7 Model Governance & Provenance

#### `GET /api/v1/models/active`
Returns detailed metadata regarding the active machine learning model deployed in production.


**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "version": "v1.0.0",
    "model_name": "pricenest_pune_regressor",
    "algorithm": "HistGradientBoostingRegressor",
    "training_date": "2026-10-21T00:00:00Z",
    "dataset_provenance": "Kaggle Pune Housing Dataset (Development / Exploratory Baseline)",
    "offline_metrics": {
      "r2_score": 0.865,
      "mae_inr_lakhs": 5.40,
      "rmse_inr_lakhs": 8.75,
      "mape": 0.098
    },
    "features_used": [
      "locality",
      "total_sqft",
      "bhk",
      "bathrooms",
      "balconies",
      "furnishing"
    ]
  },
  "meta": {
    "timestamp": "2026-10-21T14:30:00Z"
  }
}
```

---

## 4. HTTP Status Codes & Error Registry

| Code | Name | Scenario |
| :--- | :--- | :--- |
| `200` | OK | Request succeeded and data returned. |
| `201` | Created | Resource successfully created (e.g. feedback recorded). |
| `400` | Bad Request | Syntactically malformed JSON or unsupported parameters. |
| `404` | Not Found | Requested prediction ID or locality slug does not exist. |
| `422` | Unprocessable Entity | Pydantic schema validation failure or out-of-bounds physical values. |
| `429` | Too Many Requests | Rate limit exceeded (standard limit: 60 requests/minute per IP). |
| `500` | Internal Server Error | Unhandled server error (logs captured with correlation request ID). |
| `503` | Service Unavailable | Database or in-memory ML model engine not initialized. |
