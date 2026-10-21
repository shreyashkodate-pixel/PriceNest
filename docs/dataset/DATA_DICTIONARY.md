# PriceNest — Real Estate Data Dictionary & Schema Specification

**Document Version:** 2.0.0  
**Phase:** Phase 2.0 — Dataset Ingestion, Feasibility Audit & EDA  
**Inspection Status:** **AUDITED & CONFIRMED** (Direct inspection of `data/raw/pune_housing_raw.csv`)  
**Target Market:** Multi-City Baseline with Pune Segment (N=7,833 in Pune; N=80,000 across 10 Cities)  
**Last Updated:** October 2026  

---

## 1. Overview & Dataset Profile Summary

The raw dataset stored at `data/raw/pune_housing_raw.csv` has been directly inspected and profiled via `scripts/inspect_dataset.py`.

- **Total Rows:** 80,000 observations
- **Total Columns:** 18 attributes
- **Missing Values:** 0 null values across all columns
- **Duplicate Records:** 0 duplicate rows; 80,000 unique `Property_ID`s (`PROP-000001` to `PROP-080000`)
- **Geographic Coverage:** 10 major Indian metropolitan areas (Bangalore, Chennai, Hyderabad, Delhi, Mumbai, Jaipur, Ahmedabad, Chandigarh, Kolkata, Pune).
- **Pune Representation:** 7,833 rows (9.79% of dataset)
- **Target Variable:** `Price_INR_Lakhs` (Total price in Indian Rupee Lakhs; $1\text{ Lakh} = 100,000\text{ INR}$).

---

## 2. Confirmed Dataset Schema

The table below catalogs the 18 physical columns discovered and confirmed in `data/raw/pune_housing_raw.csv`:

| Column Name | Confirmed Physical Type | Domain Semantics | Observed Range / Unique Values | Measurement Unit | Missing % | Modeling Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Property_ID` | String | Unique synthetic identifier | `PROP-000001` to `PROP-080000` | Alphanumeric | 0.0% | Identifier (Drop) |
| `City` | String (Categorical) | Metropolitan city name | 10 cities (~8,000 records each) | Nominal | 0.0% | Feature / Filter |
| `Locality_Type` | String (Categorical) | Broad neighborhood pricing tier | `Mid-Range` (50.3%), `Affordable` (25.0%), `Premium` (24.7%) | Ordinal / Categorical | 0.0% | Core Predictor |
| `Property_Type` | String (Categorical) | Physical structure category | `Apartment` (25.1%), `Villa` (25.0%), `Builder Floor` (25.0%), `Independent House` (24.9%) | Nominal | 0.0% | Feature |
| `BHK` | Float / Integer | Count of bedrooms | $1.0$ to $6.0$ (Mean: $2.83$, Median: $3.0$) | Count | 0.0% | Feature *(Synthetic)* |
| `Bathrooms` | Float / Integer | Count of bathrooms | $1.0$ to $6.0$ (Mean: $3.32$, Median: $3.0$) | Count | 0.0% | Feature *(Synthetic)* |
| `Super_Area_SqFt` | Float (Continuous) | Super built-up area | $16.02$ to $4,502.97$ sq.ft. (Mean: $1,409.51$, Median: $1,286.80$) | Square Feet | 0.0% | Primary Predictor |
| `Carpet_Area_SqFt` | Float (Continuous) | Usable floor area inside walls | $11.51$ to $3,578.25$ sq.ft. (Mean: $1,057.01$, Median: $960.59$) | Square Feet | 0.0% | Secondary Predictor |
| `Floor_Number` | Float / Integer | Property floor level | $0.0$ to $43.0$ (Mean: $10.74$, Median: $8.0$) | Index ($0 = \text{Ground}$) | 0.0% | Feature |
| `Total_Floors` | Float / Integer | Total building floors | $1.0$ to $44.0$ (Mean: $22.46$, Median: $22.0$) | Count | 0.0% | Feature |
| `Age_of_Property` | Float / Integer | Age of building in years | $0.0$ to $39.0$ years (Mean: $19.45$, Median: $19.0$) | Years | 0.0% | Predictor (Depreciation) |
| `Furnishing_Status` | String (Categorical) | Interior furnishing level | `Semi-Furnished` (33.5%), `Furnished` (33.5%), `Unfurnished` (33.0%) | Nominal | 0.0% | Feature |
| `Parking` | Integer (Binary) | Reserved parking flag | $0$ (No parking: 34.5%), $1$ (Parking: 65.5%) | Binary | 0.0% | Feature |
| `Lift_Available` | Integer (Binary) | Building elevator flag | $0$ (No: 5.2%), $1$ (Yes: 94.8%) | Binary | 0.0% | Feature |
| `Gated_Community` | Integer (Binary) | Gated security flag | $0$ (No: 45.3%), $1$ (Yes: 54.7%) | Binary | 0.0% | Feature |
| `Distance_to_Metro_km` | Float (Continuous) | Proximity to transit station | $0.00$ to $11.63$ km (Mean: $3.12$, Median: $3.01$) | Kilometres | 0.0% | Feature |
| `Distance_to_City_Center_km` | Float (Continuous) | Distance to central business district | $0.00$ to $25.39$ km (Mean: $9.01$, Median: $8.96$) | Kilometres | 0.0% | Predictor (Location) |
| `Price_INR_Lakhs` | Float (Continuous) | **Target Variable:** Total sale price | ₹$2.77$ to ₹$3,334.92$ Lakhs (Mean: ₹$142.61$L, Median: ₹$96.60$L) | INR Lakhs | 0.0% | **Target ($Y$)** |

---

## 3. Critical Target Variable Semantics

1. **Target Unit and Scale:**
   - The column `Price_INR_Lakhs` unequivocally represents the **Total Property Price in Indian Rupee Lakhs**.
   - $1\text{ Lakh} = 100,000\text{ INR} = 10^5\text{ INR}$.
   - Example: A value of `127.38` denotes **₹1,27,38,000** (₹1.27 Crore or ₹127.38 Lakhs).
2. **Target Distribution Characteristics:**
   - **Full Dataset (N=80,000):** Mean = ₹142.61L, Std = ₹147.24L, 25th percentile = ₹54.35L, Median = ₹96.60L, 75th percentile = ₹176.71L, 99th percentile = ₹739.73L.
   - **Pune Subset (N=7,833):** Mean = ₹133.32L, Std = ₹110.10L, 25th percentile = ₹61.87L, Median = ₹99.56L, 75th percentile = ₹167.25L, 99th percentile = ₹497.83L.
   - Right-skewed distribution characteristic of real estate pricing across tiers.

---

## 4. Key Limitations & Synthetic Data Characteristics

Direct statistical inspection revealed several synthetic artifacts:

1. **Absence of Specific Named Pune Localities:**
   - The dataset does **not** contain granular Pune locality names (e.g., Baner, Wakad, Kothrud, Hinjawadi).
   - The only location feature is `Locality_Type` with values `Affordable`, `Mid-Range`, and `Premium`.
2. **Decoupling of Area and Bedroom Count (Zero Correlation):**
   - In physical reality, property size and bedroom count have a strong positive correlation ($r \approx 0.80$).
   - In this dataset, $\text{corr}(BHK, Super\_Area\_SqFt) = \mathbf{0.0041}$ (essentially zero). Bedrooms were generated independently of square footage.
3. **High-Rise Villas and Independent Houses:**
   - Over $90\%$ of `Villa` and `Independent House` records are listed on upper floors of tall buildings (up to floor 43 of 44 floors), which is physically impossible.
4. **Synthetic Area Ratio:**
   - The ratio `Carpet_Area_SqFt / Super_Area_SqFt` is strictly bounded between $0.65$ and $0.85$ with a uniform average of exactly $0.75$.
5. **Feature Importance on Price:**
   - `Super_Area_SqFt`, `City`, and `Locality_Type` account for over $95\%$ of price variance in regression models.
   - `BHK`, `Bathrooms`, `Floor_Number`, `Parking`, `Lift_Available`, and `Property_Type` have near-zero correlation with price ($|r| < 0.02$).

---

## 5. Standardized Currency Conversion Rules

For ingestion into the ML pipeline and exposure via the API:
- **Canonical Model Output:** Absolute Indian Rupees: $\text{Price}_{\text{INR}} = \text{Price\_INR\_Lakhs} \times 100,000.0$.
- **Human-Friendly Display:**
  - If $\text{Price}_{\text{INR}} \ge 10,000,000$ (₹1 Crore): Format as `₹X.XX Crore` (e.g. `₹1.85 Cr`).
  - If $\text{Price}_{\text{INR}} < 10,000,000$: Format as `₹XX.XX Lakh` (e.g. `₹82.50 L`).
