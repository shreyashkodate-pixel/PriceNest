# PriceNest — Dataset Feasibility Audit & Data Governance

**Document Version:** 2.0.0  
**Phase:** Phase 2.0 — Dataset Ingestion, Feasibility Audit & EDA  
**Primary Dataset Origin:** Kaggle Residential Housing Dataset (`data/raw/pune_housing_raw.csv`)  
**Audit Status:** **AUDITED & VERIFIED** (Completed October 2026)  
**Last Updated:** October 2026  

---

## 1. Executive Summary & Audit Outcome

This audit presents the empirical findings from directly inspecting and profiling the raw dataset `data/raw/pune_housing_raw.csv` (8,335,049 bytes, 80,000 rows, 18 columns).

### Primary Audit Findings:
1. **Multi-City Scope with Pune Segment:** Despite the file naming, the dataset spans **10 major Indian metropolitan cities** (~8,000 records each). **Pune represents 7,833 records (9.79%)**.
2. **Missing & Duplicate Values:** **0 null values** across all 80,000 rows. **0 duplicate records**; all 80,000 `Property_ID` entries are unique.
3. **Locality Granularity:** The dataset does **not** contain specific neighborhood names (e.g., Baner, Wakad, Kothrud). Geographic granularity is restricted to `City` and `Locality_Type` (`Affordable`, `Mid-Range`, `Premium`).
4. **Target Variable:** Confirmed as `Price_INR_Lakhs` ($1\text{ Lakh} = 100,000\text{ INR}$). Mean price is ₹142.61 Lakhs across all cities, and ₹133.32 Lakhs for the Pune subset.
5. **Synthetic & Heuristic Nature Verified:** Statistical anomalies (zero correlation between BHK and Area, high-rise villas on 40th floors, perfectly uniform 25% splits across property types) confirm that this dataset was algorithmically synthesized.
6. **Modeling Feasibility Decision:** **GO FOR INITIAL EXPERIMENTATION & PIPELINE SCAFFOLDING**. The dataset is technically robust (clean, non-null, properly scaled) for training baseline scikit-learn regression models, building cross-validation pipelines, and verifying end-to-end inference in FastAPI and Next.js. However, models trained on it must be labeled as illustrative prototypes.

---

## 2. Dataset Provenance & Critical Nature Notice

### 2.1 Origin & Platform
- **Source Platform:** Kaggle (Indian Housing / Real Estate Dataset).
- **Physical Location:** `data/raw/pune_housing_raw.csv` (Local only; excluded from version control).
- **Intended Use Case:** Prototyping, algorithmic benchmarking, feature pipeline construction, and developer testing.

### 2.2 Synthetic & Unverified Data Disclosure
> [!WARNING]
> **Verified Synthetic Data Notice:**
> Empirical profiling confirms that `pune_housing_raw.csv` is an algorithmically generated synthetic dataset.
> 
> - **It does NOT represent verified government deed registrations, authenticated Index-II records, or certified bank appraisals in Pune or any other city.**
> - Bedroom counts were generated independently of property square footage ($\text{corr} = 0.0041$).
> - **No commercial, financial, or legal reliance** may be placed on predictions produced by models trained on this dataset.

---

## 3. Post-Inspection Feasibility Audit Matrix

| Audit Dimension | Evaluation Protocol | Current Status | Empirical Findings |
| :--- | :--- | :--- | :--- |
| **Exact Column Headers** | Inspect headers in CSV reader | **VERIFIED** | 18 columns: `Property_ID`, `City`, `Locality_Type`, `Property_Type`, `BHK`, `Bathrooms`, `Super_Area_SqFt`, `Carpet_Area_SqFt`, `Floor_Number`, `Total_Floors`, `Age_of_Property`, `Furnishing_Status`, `Parking`, `Lift_Available`, `Gated_Community`, `Distance_to_Metro_km`, `Distance_to_City_Center_km`, `Price_INR_Lakhs`. |
| **Target Variable Semantics** | Analyze values, units, and distribution | **VERIFIED** | `Price_INR_Lakhs` represents total property price in INR Lakhs ($10^5$ INR). Full dataset mean ₹142.61L; Pune mean ₹133.32L. |
| **Sample Size & Cardinality** | Count total rows and city counts | **VERIFIED** | 80,000 total rows. Pune subset contains 7,833 clean rows (substantially exceeding the 1,000-row minimum requirement). |
| **Missingness & Null Rates** | Compute per-column null percentages | **VERIFIED** | Exactly 0% missing values across all 18 columns. |
| **Outliers & Physical Feasibility** | Filter impossible physical combinations | **VERIFIED** | Unrealistic artifacts detected: 1,772 rows have $<100$ sq.ft. per bedroom; 18,163 villas are listed in high-rises. |
| **Geographic Coverage** | Audit locality and city values | **VERIFIED** | 10 Indian cities. No specific Pune sub-localities (e.g. Baner, Kothrud); only `Locality_Type` (`Affordable`, `Mid-Range`, `Premium`). |
| **Licensing & Terms of Use** | Standard Kaggle community license | **VERIFIED** | Open for non-commercial research, portfolio development, and educational benchmarking. |

---

## 4. Key Anomaly Findings & Synthetic Footprints

1. **Decoupling of Area and BHK:**
   - In physical reality, a 4 BHK flat is larger than a 1 BHK flat ($r \approx 0.80$).
   - In this dataset, $\text{corr}(BHK, Super\_Area\_SqFt) = \mathbf{0.0041}$. The synthetic generator drew BHK from a discrete uniform distribution without conditioning on area.
2. **High-Rise Independent Houses & Villas:**
   - Over $90\%$ of `Villa` (18,163 of 20,031) and `Independent House` (18,068 of 19,898) records have `Floor_Number > 3` and `Total_Floors > 4` (up to floor 43 of 44).
3. **Rigid Carpet-to-Super Ratio:**
   - The ratio `Carpet_Area_SqFt / Super_Area_SqFt` is uniformly distributed between strictly $0.65$ and $0.85$ (mean $0.75$, std $0.06$).
4. **Symmetric Categorical Frequencies:**
   - Property types: exactly $25.0\%$ each (Apartment 20,049, Villa 20,031, Builder Floor 20,022, Independent House 19,898).
   - Furnishing status: exactly $33.3\%$ each (Semi-Furnished 26,801, Furnished 26,783, Unfurnished 26,416).
   - City representation: exactly $\sim 10\%$ each (8,000 rows $\pm 200$).

---

## 5. Modeling Implications & Recommended Preprocessing

### Strategy 1: Geographic Scope Decision
- **Option A (Pune-Filtered Baseline):** Train the initial model strictly on the `City == 'Pune'` subset ($N = 7,833$). This adheres to the PRD mandate focusing on Pune residential completed sales, eliminating inter-city pricing variance.
- **Option B (All-City Multi-Market Baseline):** Include `City` as a categorical feature ($N = 80,000$). While providing more training samples, city-level variance dominates price determination.
- **Recommendation:** Train primarily on the **Pune subset ($N=7,833$)** for the PriceNest Pune valuation calculator, with an optional multi-city experiment comparison.

### Strategy 2: Preprocessing & Outlier Handling
1. **Drop Identifiers:** Exclude `Property_ID`.
2. **Categorical Encoding:** One-hot encode `Locality_Type`, `Property_Type`, and `Furnishing_Status`.
3. **Binary Preservation:** Keep `Parking`, `Lift_Available`, and `Gated_Community` as binary indicators.
4. **Physical Sanity Filtering:**
   - Drop or flag extreme area outliers: $Super\_Area\_SqFt < 200$ sq.ft. (removes 16 sq.ft. anomalies).
   - Address $SqFt\_per\_BHK < 100$ records during training split preparation.
5. **Feature Scaling:** Apply `StandardScaler` to continuous numerical predictors (`Super_Area_SqFt`, `Age_of_Property`, `Distance_to_City_Center_km`).

---

## 6. Phase 2 Audit Conclusion & Go/No-Go Decision

### Decision: **GO FOR INITIAL PROTOTYPE MODELING (PHASE 3)**

- **Rationale:**
  1. The dataset contains **7,833 clean Pune residential records**, which is ample for $K$-fold cross-validation, baseline regression modeling, and pipeline development.
  2. Data cleanliness is exceptional: zero null values, zero unparseable tokens, zero negative values.
  3. The synthetic nature has been thoroughly documented and does not impede engineering portfolio goals (reproducible pipelines, FastAPI integration, Next.js UI validation).
  4. Disclaimers in the UI and documentation will transparently communicate that predictions reflect baseline synthetic data.
