# PriceNest — Product & System Requirements Specification

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Project Foundation & Documentation  
**Geographic Focus:** Pune, Maharashtra, India  
**Last Updated:** October 2026  

> [!IMPORTANT]
> **Specification Authority Notice:**
> The primary, normative product and engineering specifications for PriceNest are:
> 1. [`docs/requirements/PriceNest_PRD.md`](file:///Users/apple/Documents/Projects/PriceNest/docs/requirements/PriceNest_PRD.md) (Product Requirements Document)
> 2. [`docs/requirements/PriceNest_SRS.md`](file:///Users/apple/Documents/Projects/PriceNest/docs/requirements/PriceNest_SRS.md) (Software Requirements Specification)
>
> In the event of any conflict, omission, or ambiguity, `PriceNest_PRD.md` and `PriceNest_SRS.md` take absolute precedence over this document. In particular, **User Accounts and Private Prediction History are confirmed as core MVP scope** per PRD F-03/F-04 and SRS FR-04/FR-05.

---

## 1. Executive Summary & Vision

**PriceNest** is an intelligent residential real-estate price prediction platform designed to provide transparent, instant, and explainable property valuations across Pune, Maharashtra, India. 

Residential real estate in Indian metropolitan areas—and particularly Pune—is characterized by extreme micro-market fragmentation. Real estate pricing in Pune exhibits significant variance across tech hubs (Hinjawadi, Kharadi, Magarpatta), established urban residential cores (Kothrud, Prabhat Road, Model Colony), affluent suburban corridors (Baner, Balewadi, Kalyani Nagar, Koregaon Park), and rapidly expanding PCMC/PMRDA suburbs (Wakad, Ravet, Punawale, Moshi).

PriceNest addresses information asymmetry by enabling home buyers, property sellers, and investors to input property parameters (locality, size, bedrooms, amenities, property age) and receive an instant, data-driven estimated price in Indian Rupees (INR Lakhs and Crores), accompanied by valuation confidence intervals and micro-market context.

---

## 2. Target Market & Geographic Scope

### Primary Geography: Pune Metropolitan Region
- **Pune Municipal Corporation (PMC):** Central, South, and East Pune zones including Kothrud, Deccan, Shivajinagar, Camp, Viman Nagar, Kalyani Nagar, Hadapsar, Kharadi, Kondhwa, Wanowrie, Sinhagad Road.
- **Pimpri-Chinchwad Municipal Corporation (PCMC):** West and North-West tech and industrial corridors including Wakad, Pimple Saudagar, Pimple Nilakh, Ravet, Hinjawadi (PMRDA/MIDC boundary), Moshi, Chikhali, Nigdi.
- **PMRDA Suburban Extensions:** Wagholi, Undri, Pisoli, Bhugaon, Pirangut, Punawale, Tathawade.

---

## 3. User Personas

| Persona | Role | Primary Objective | Key Pain Point |
| :--- | :--- | :--- | :--- |
| **P1: First-Time Home Buyer** | IT professional / family looking for 2-3 BHK in Pune (e.g. Hinjawadi, Wakad, Kharadi). | Evaluate whether a builder's quote or resale listing is reasonably priced. | Unclear base pricing per square foot, confusing difference between carpet vs super built-up area. |
| **P2: Property Reseller / Owner** | Existing homeowner planning to list their apartment for sale. | Establish a competitive, realistic asking price before listing on portals. | Over-reliance on local broker estimates that fluctuate wildly. |
| **P3: Real Estate Investor** | Retail investor comparing yields and capital appreciation potential across micro-markets. | Compare per-sq.ft. price levels across diverse localities to spot valuation disparities. | Lack of quick, normalized comparative analytics across Pune neighborhoods. |
| **P4: Platform Administrator / Data Scientist** | Internal engineering and ML team. | Monitor inference latency, track prediction drifts, audit queries, and evaluate retrained models. | Lack of unified audit logging and model version governance. |

---

## 4. Functional Requirements (FR)

### FR-1: Real-Time Valuation Estimation Engine
- **FR-1.1:** The system shall accept property attributes from the client, including:
  - Locality / Micro-Market (mandatory, selectable from validated Pune localities)
  - Total Area in Square Feet (mandatory, positive numeric value)
  - BHK Configuration (mandatory, 1 to 5+ bedrooms)
  - Number of Bathrooms (mandatory, integer $\ge 1$)
  - Number of Balconies (optional, integer $\ge 0$)
  - Furnishing Status (optional: Unfurnished, Semi-Furnished, Fully Furnished)
  - Property Age / Possession Status (optional: Ready-to-move, Under Construction, Resale age band)
  - Reserved Parking (optional: None, Covered, Open, 1, 2)
- **FR-1.2:** The system shall return a real-time valuation output containing:
  - Estimated Property Value in INR (e.g., ₹7,500,000)
  - Human-friendly Indian numerical notation (e.g., `₹75.00 Lakh` or `₹1.85 Crore`)
  - Estimated Price Range / Confidence Interval (e.g., `₹71.25 L – ₹78.75 L`)
  - Estimated Rate per Square Foot (`₹/sq.ft.`)
  - Active Model Version identifier and inference timestamp
- **FR-1.3:** The system shall validate physical feasibility constraints (e.g., rejecting a 3 BHK with 250 sq.ft. area as invalid input).

### FR-2: Pune Locality Discovery & Micro-Market Benchmarks
- **FR-2.1:** The system shall maintain a managed registry of Pune localities with standardized names, slug identifiers, and regional classifications (e.g., West Pune, East Pune, PCMC).
- **FR-2.2:** The API shall provide autocomplete/search endpoints returning active localities with metadata.
- **FR-2.3:** The platform shall display locality benchmark statistics (e.g., average rate per square foot, typical BHK distributions) to provide contextual grounding for the estimate.

### FR-3: Valuation Explanability & Driver Breakdown
- **FR-3.1:** The prediction response shall provide high-level feature attribution or directional indicators (e.g., indicating whether the chosen locality commands a premium relative to the citywide average).
- **FR-3.2:** The user interface shall visually communicate the proportion of valuation attributed to size/area versus locality premium.

### FR-4: Query Logging & Audit Trail
- **FR-4.1:** Every valid valuation request submitted to the backend shall be recorded in the `prediction_requests` table with an anonymous session ID, input features, output price, model version, and inference latency.
- **FR-4.2:** No personal identifying information (PII) such as user names or mobile numbers shall be required for basic valuations.

### FR-5: Saved Valuations & Property Comparison
- **FR-5.1:** Users shall be able to save generated valuations to local storage (guest mode) or to their database profile.
- **FR-5.2:** The platform shall support side-by-side comparison of up to 3 distinct property valuations (e.g., comparing a 2 BHK in Baner vs a 3 BHK in Ravet).

### FR-6: User Valuation Feedback Loop
- **FR-6.1:** Users shall have the option to rate the estimated valuation (e.g., "Accurate", "Too High", "Too Low").
- **FR-6.2:** Users with actual transaction or listing knowledge may submit a known actual price for ground-truth benchmarking and continuous model evaluation.

### FR-7: Data Provenance & Methodology Transparency
- **FR-7.1:** The application shall feature a persistent, accessible Methodology page detailing:
  - The origin and nature of the training dataset.
  - Clear disclosure that the development model is trained on a Kaggle development dataset containing synthetic/heuristic observations.
  - Explicit notification that predictions do not constitute legal stamp-duty valuations, government Ready Reckoner (RR) rates, or certified banking appraisals.
- **FR-7.2:** Model version metadata shall be exposed via a dedicated public endpoint (`GET /api/v1/models/active`).

---

## 5. Non-Functional Requirements (NFR)

### NFR-1: Performance & Latency
- **API Latency:** The p95 response time for the `POST /api/v1/predict/price` endpoint shall not exceed **200 milliseconds** under standard load (excluding network transport).
- **Frontend Core Web Vitals:** Next.js application shall achieve:
  - Largest Contentful Paint (LCP) < 2.0s
  - First Input Delay (FID) / Interaction to Next Paint (INP) < 100ms
  - Cumulative Layout Shift (CLS) < 0.05

### NFR-2: Scalability & High Availability
- **Stateless Backend:** The FastAPI application shall remain strictly stateless to permit effortless horizontal scaling on Render.
- **Connection Management:** Database queries to Supabase PostgreSQL shall utilize connection pooling (Supavisor) to prevent connection exhaustion during concurrent traffic spikes.

### NFR-3: Security, Privacy & Integrity
- **CORS Protection:** FastAPI shall enforce strict Cross-Origin Resource Sharing (CORS) whitelisting only authorized frontend domains.
- **Input Sanitization:** All incoming payloads shall be strictly validated using Pydantic v2 schemas; non-whitelisted fields shall be rejected.
- **Zero Secrets in Source:** No database passwords, Supabase service keys, or environment secrets shall be stored in Git.

### NFR-4: Observability & Monitoring
- **Health Checks:** The backend shall expose `/health` and `/api/v1/health` probes checking application liveness and database connectivity.
- **Structured Logging:** FastAPI shall produce structured JSON logs capturing HTTP method, path, status code, latency, and sanitized query metadata.

### NFR-5: Accessibility & Responsiveness
- **Responsive Layout:** The web application shall provide a seamless, optimized user experience across mobile (375px+), tablet, and desktop (1440px+) viewports.
- **Accessibility:** UI components shall comply with WCAG 2.1 Level AA guidelines, including minimum 4.5:1 text contrast ratios, semantic HTML landmarks, and keyboard navigability.

---

## 6. Out-of-Scope (Phase 1 Baseline)

1. **Commercial & Industrial Real Estate:** Warehouses, IT parks, retail shops, and commercial offices are excluded; the initial scope is exclusively residential apartments, flats, and villas.
2. **Legal Title & Encumbrance Verification:** PriceNest does not check 7/12 extracts, title ownership, RERA registration litigation status, or municipal building sanctions.
3. **Government Ready Reckoner (RR) Calculation:** Predictions are algorithmic market estimates, not statutory stamp duty tax computations prescribed by the Maharashtra Department of Registration and Stamps.
4. **Automated Scraping of Real-Estate Portals:** No live unauthenticated web scraping against commercial portals (e.g. 99acres, MagicBricks, Housing.com) is included in this phase.
