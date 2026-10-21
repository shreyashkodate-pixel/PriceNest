# PriceNest — Phase 2.0 Dataset Feasibility Audit & EDA Report

**Document Version:** 1.0.0  
**Phase:** Phase 2.0 — Dataset Ingestion, Feasibility Audit & Exploratory Data Analysis (EDA)  
**Evaluated Dataset:** `data/raw/pune_housing_raw.csv`  
**Execution Date:** October 2026  
**Auditor:** Google AntiGravity (Autonomous AI Assistant)  
**Decision:** **GO (FOR INITIAL MODEL TRAINING & PIPELINE PROTOTYPING)**

---

## 1. Executive Summary & Purpose

The objective of Phase 2.0 was to inspect the downloaded dataset at [`data/raw/pune_housing_raw.csv`](file:///Users/apple/Documents/Projects/PriceNest/data/raw/pune_housing_raw.csv), audit its statistical integrity, verify its geographic relevance to Pune, identify data quality issues and synthetic artifacts, evaluate target variable suitability, and establish an evidence-based recommendation for Phase 3 (Model Training & Evaluation).

### Key Takeaways:
1. **Multi-City Scope:** Although titled `pune_housing_raw.csv`, the dataset is an **all-India residential dataset covering 10 major metropolitan cities** (80,000 total rows; ~8,000 per city).
2. **Pune Segment Size:** The Pune subset contains **7,833 clean observations** (9.79% of the dataset), easily satisfying the minimum volume requirement for training and cross-validation.
3. **Data Completeness:** **0 missing values (0.0% nulls)** across all 18 columns, and **0 duplicate records** (80,000 unique `Property_ID`s).
4. **Locality Granularity Limitation:** The dataset contains **no specific Pune locality names** (e.g., Baner, Wakad, Kothrud, Kharadi). Instead, it provides a 3-tier categorization: `Locality_Type` (`Affordable`, `Mid-Range`, `Premium`).
5. **Confirmed Synthetic Nature:** Statistical analysis reveals synthetic generation footprints:
   - Near-zero correlation between `BHK` and `Super_Area_SqFt` ($r = 0.0041$).
   - 90.7% of villas and independent houses are listed on high-rise floors (up to floor 43).
   - Price is determined predominantly by `Super_Area_SqFt`, `City`, and `Locality_Type`, while bedrooms, bathrooms, and floor levels have negligible influence on price.
6. **Feasibility Decision:** **GO FOR INITIAL EXPERIMENTATION**. The dataset is technically sound for establishing the baseline machine learning pipeline, serializing `.joblib` artifacts, and wiring the FastAPI backend and Next.js frontend, provided the synthetic nature is transparently acknowledged.

---

## 2. Dataset Profile & Structural Verification

| Attribute | Observed Metric | Notes |
| :--- | :--- | :--- |
| **Physical File Path** | [`data/raw/pune_housing_raw.csv`](file:///Users/apple/Documents/Projects/PriceNest/data/raw/pune_housing_raw.csv) | Stored locally; excluded from Git |
| **File Size** | 8,335,049 bytes (7.95 MB) | Comma-separated ASCII/UTF-8 |
| **Total Rows** | 80,000 rows | 80,001 lines including header |
| **Total Columns** | 18 columns | 1 ID, 4 Categorical, 12 Numeric, 1 Target |
| **Missing Values (Nulls)** | 0 (0.0%) | Zero empty cells, NaNs, or null sentinels |
| **Duplicate Rows** | 0 (0.0%) | All 80,000 `Property_ID`s are unique |
| **Parsing Errors** | 0 (0.0%) | All numeric columns parse cleanly as floats |

### Column Inventory & Datatypes

| # | Column Name | Raw Type | Domain Semantics | Valid Range / Unique Values |
| :- | :--- | :--- | :--- | :--- |
| 1 | `Property_ID` | String | Unique property identifier | `PROP-000001` to `PROP-080000` |
| 2 | `City` | String | Metropolitan city name | 10 Indian cities (~8,000 each) |
| 3 | `Locality_Type` | String | Neighborhood pricing category | `Mid-Range` (50.3%), `Affordable` (25.0%), `Premium` (24.7%) |
| 4 | `Property_Type` | String | Property structure category | `Apartment` (25.1%), `Villa` (25.0%), `Builder Floor` (25.0%), `Independent House` (24.9%) |
| 5 | `BHK` | Float / Int | Bedroom count | $1.0$ to $6.0$ (Mean: $2.83$) |
| 6 | `Bathrooms` | Float / Int | Bathroom count | $1.0$ to $6.0$ (Mean: $3.32$) |
| 7 | `Super_Area_SqFt` | Float | Super built-up area | $16.02$ to $4,502.97$ sq.ft. (Mean: $1,409.51$) |
| 8 | `Carpet_Area_SqFt` | Float | Carpet / usable area | $11.51$ to $3,578.25$ sq.ft. (Mean: $1,057.01$) |
| 9 | `Floor_Number` | Float / Int | Property floor level | $0$ (Ground) to $43$ (Mean: $10.74$) |
| 10 | `Total_Floors` | Float / Int | Building total floors | $1$ to $44$ (Mean: $22.46$) |
| 11 | `Age_of_Property` | Float / Int | Property age in years | $0$ to $39$ years (Mean: $19.45$) |
| 12 | `Furnishing_Status` | String | Furnishing level | `Semi-Furnished` (33.5%), `Furnished` (33.5%), `Unfurnished` (33.0%) |
| 13 | `Parking` | Int (Binary) | Dedicated parking flag | $0$ (No: 34.5%), $1$ (Yes: 65.5%) |
| 14 | `Lift_Available` | Int (Binary) | Elevator availability flag | $0$ (No: 5.2%), $1$ (Yes: 94.8%) |
| 15 | `Gated_Community` | Int (Binary) | Gated complex flag | $0$ (No: 45.3%), $1$ (Yes: 54.7%) |
| 16 | `Distance_to_Metro_km` | Float | Proximity to transit station | $0.00$ to $11.63$ km (Mean: $3.12$) |
| 17 | `Distance_to_City_Center_km`| Float | Distance to center | $0.00$ to $25.39$ km (Mean: $9.01$) |
| 18 | `Price_INR_Lakhs` | Float | **Target Variable:** Total price | ₹$2.77$ to ₹$3,334.92$ Lakhs (Mean: ₹$142.61$L) |

---

## 3. Geographic Coverage & Pune Representation

The dataset exhibits an almost perfectly uniform distribution across 10 major Indian metropolitan cities:

| City | Record Count | % of Dataset | Mean Price (₹ Lakhs) | Mean Rate (₹/Super Sq.Ft.) | Mean Super Area (Sq.Ft.) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Bangalore** | 8,189 | 10.24% | ₹149.68 | ₹9,864.82 | 1,410.77 |
| **Chennai** | 8,150 | 10.19% | ₹122.42 | ₹8,010.11 | 1,411.08 |
| **Hyderabad** | 8,060 | 10.07% | ₹115.91 | ₹7,591.58 | 1,409.84 |
| **Delhi** | 8,037 | 10.05% | ₹227.00 | ₹14,911.14 | 1,407.96 |
| **Mumbai** | 8,024 | 10.03% | ₹308.20 | ₹20,164.01 | 1,407.87 |
| **Jaipur** | 8,002 | 10.00% | ₹63.26 | ₹4,149.95 | 1,404.70 |
| **Ahmedabad** | 7,982 | 9.98% | ₹75.64 | ₹4,953.97 | 1,411.75 |
| **Chandigarh** | 7,873 | 9.84% | ₹126.94 | ₹8,331.19 | 1,408.91 |
| **Kolkata** | 7,850 | 9.81% | ₹99.40 | ₹6,465.77 | 1,415.02 |
| **Pune** | **7,833** | **9.79%** | **₹133.32** | **₹8,718.96** | **1,410.30** |

```
Geographic Distribution:
[██████████] Bangalore   : 8,189
[██████████] Chennai     : 8,150
[██████████] Hyderabad   : 8,060
[██████████] Delhi       : 8,037
[██████████] Mumbai      : 8,024
[██████████] Jaipur      : 8,002
[██████████] Ahmedabad   : 7,982
[██████████] Chandigarh  : 7,873
[██████████] Kolkata     : 7,850
[██████████] Pune        : 7,833 (Focal Segment)
```

> **Critical Geographic Finding:** The filename `pune_housing_raw.csv` is a misnomer; Pune constitutes exactly 9.79% of the data. However, **7,833 records** provide a more than sufficient sample for training a dedicated Pune residential price estimation model.

---

## 4. Visualizations & Exploratory Plots

The following vector charts were generated from the raw data and saved to [`docs/dataset/plots/`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/plots):

1. **City Record Distribution:**  
   [`docs/dataset/plots/city_distribution.svg`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/plots/city_distribution.svg)  
   *Illustrates the uniform ~8,000 records per city across all 10 metropolises.*

2. **Mean Property Rate by City (₹ / Sq.Ft.):**  
   [`docs/dataset/plots/city_rates.svg`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/plots/city_rates.svg)  
   *Visualizes city pricing tiers: Mumbai (₹20,164) > Delhi (₹14,911) > Bangalore (₹9,865) > **Pune (₹8,719)** > Chandigarh (₹8,331) > Chennai (₹8,010) > Hyderabad (₹7,592) > Kolkata (₹6,466) > Ahmedabad (₹4,954) > Jaipur (₹4,150).*

3. **Feature Correlations with Price (Pune Segment):**  
   [`docs/dataset/plots/feature_correlations.svg`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/plots/feature_correlations.svg)  
   *Demonstrates that Super Area ($r = 0.794$) and Carpet Area ($r = 0.776$) drive price, whereas BHK, bathrooms, floor number, and parking have near-zero correlation with price.*

4. **Pune Locality Type Breakdown:**  
   [`docs/dataset/plots/pune_locality_type.svg`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/plots/pune_locality_type.svg)  
   *Shows Mid-Range (3,973), Premium (1,956), and Affordable (1,904) proportions in Pune.*

---

## 5. Statistical Evidence of Synthetic Generation

Statistical profiling confirmed that this dataset was programmatically generated using parametric formulas and independent random distributions rather than collected from genuine real-estate transactions:

### 5.1 Area and Bedroom Count Independence
In any genuine housing market, bedroom count strongly predicts area ($r \approx 0.80$). In this dataset:
$$\text{corr}(BHK, Super\_Area\_SqFt) = \mathbf{0.0041}$$
$$\text{corr}(BHK, Carpet\_Area\_SqFt) = \mathbf{0.0042}$$
The synthetic generator sampled `BHK` from a uniform discrete distribution $[1, 6]$ completely independently of the square footage drawn for the property.

### 5.2 Physical Impossibilities in Unit Sizes
- **1,772 records** have $<100$ sq.ft. of carpet area per bedroom (e.g. Row 13: a 4 BHK flat with 5 bathrooms in 622 sq.ft. carpet area, yielding 124 sq.ft. total per bedroom suite including living room, kitchen, and 5 bathrooms).
- **6,640 records** have $<150$ sq.ft. of carpet area per bedroom.
- Minimum `Super_Area_SqFt` is $16.02$ sq.ft., and minimum `Carpet_Area_SqFt` is $11.51$ sq.ft., representing non-physical living quarters.

### 5.3 High-Rise Villas and Independent Houses
- **18,163 of 20,031 Villas (90.7%)** are recorded with `Floor_Number > 3` and `Total_Floors > 4` (up to floor 43 of 44).
- **18,068 of 19,898 Independent Houses (90.8%)** are similarly situated in high-rise towers.
In Indian municipal regulations, independent houses and villas are standalone low-rise structures (typically Ground + 1 or 2 floors).

### 5.4 Rigid Carpet-to-Super Built-Up Ratio
- The ratio `Carpet_Area_SqFt / Super_Area_SqFt` is strictly bounded between $[0.650, 0.850]$ with a mean of $0.750$ and standard deviation $0.060$, characteristic of uniform random generator bounds (`uniform(0.65, 0.85)`).

### 5.5 Perfectly Uniform Categorical Distributions
- Property types each account for exactly $25.0\%$ of records ($\pm 0.1\%$).
- Furnishing status accounts for exactly $33.3\%$ each ($\pm 0.2\%$).
- Cities account for exactly $10.0\%$ each ($\pm 0.2\%$).

---

## 6. Target Variable Analysis & Reverse Engineering

### 6.1 Semantics and Scaling
- `Price_INR_Lakhs` is a continuous floating-point number representing the total property value in Lakhs ($10^5$ INR).
- For Pune:
  - Minimum: ₹5.00 Lakhs
  - 25th percentile: ₹61.87 Lakhs
  - Median: ₹99.56 Lakhs
  - Mean: ₹133.32 Lakhs
  - 75th percentile: ₹167.25 Lakhs
  - 95th percentile: ₹348.47 Lakhs
  - 99th percentile: ₹497.83 Lakhs
  - Maximum: ₹1,586.80 Lakhs

### 6.2 Price Generating Mechanism
An Ordinary Least Squares (OLS) regression on the Pune subset ($N=7,833$) reveals the linear structure of the synthetic price generator ($R^2 = 0.697$, MAE = ₹33.35 Lakhs):

$$\begin{aligned}
\text{Price\_INR\_Lakhs} \approx & + 30.02 \\
& + 0.1023 \times \text{Super\_Area\_SqFt} \\
& + 66.10 \times \mathbb{I}(\text{Premium}) \\
& - 9.04 \times \mathbb{I}(\text{Affordable}) \\
& - 1.31 \times \text{Age\_of\_Property} \\
& - 3.22 \times \text{Distance\_to\_City\_Center\_km} \\
& + \text{noise}
\end{aligned}$$

Notice that `BHK`, `Bathrooms`, `Floor_Number`, `Total_Floors`, and `Parking` have coefficients that are either negligible or physically inverted (e.g. negative coefficient for BHK), confirming they were not meaningful drivers in the price generation formula.

---

## 7. Data Preprocessing & Modeling Strategy Recommendations

### 7.1 Scope: Pune Subset vs. Multi-City Model
- **Primary Recommendation (Pune Focus):** Filter the dataset to `City == 'Pune'` ($N = 7,833$). This strictly aligns with PRD Section 1 ("The product will start with Pune and expand to other cities only when suitable data supports it").
- **Secondary Multi-City Benchmark:** A multi-city baseline using `City` as a categorical feature ($N = 80,000$) can be maintained as a reference comparison.

### 7.2 Data Cleansing & Outlier Filtering
1. **Drop Metadata:** Exclude `Property_ID`.
2. **Handle Non-Physical Outliers:**
   - Exclude properties where `Super_Area_SqFt < 200` sq.ft. (removes impossible tiny units).
   - Filter or handle records where `Carpet_Area_SqFt / BHK < 100` to prevent anomalous feature interactions.
3. **Collinearity Handling:**
   - `Super_Area_SqFt` and `Carpet_Area_SqFt` have a correlation of $0.983$. Keep `Super_Area_SqFt` as the primary size feature (or test a derived carpet ratio) to avoid multi-collinearity.
4. **Encoding & Scaling:**
   - One-hot encode `Locality_Type`, `Property_Type`, and `Furnishing_Status`.
   - Preserve binary features: `Parking`, `Lift_Available`, `Gated_Community`.
   - Standard scale continuous numerical inputs: `Super_Area_SqFt`, `Age_of_Property`, `Distance_to_City_Center_km`, `Distance_to_Metro_km`.

### 7.3 Candidate Algorithms for Phase 3
1. **Baseline 1:** Dummy Regressor (Median / Mean).
2. **Baseline 2:** Regularized Ridge / Lasso Linear Regression.
3. **Candidate 1:** Random Forest Regressor.
4. **Candidate 2:** HistGradientBoostingRegressor / GradientBoostingRegressor.

### 7.4 Evaluation Metrics
Per SRS Section 3 (FR-07):
- **MAE** (Mean Absolute Error) in INR Lakhs.
- **RMSE** (Root Mean Squared Error) in INR Lakhs.
- **$R^2$** (Coefficient of Determination).
- **Residual Analysis** across area quintiles and locality types.

---

## 8. Go / No-Go Decision

### Formal Decision: **GO (FOR PHASE 3 MODEL TRAINING & PIPELINE PROTOTYPING)**

| Decision Criteria | Evaluation | Status |
| :--- | :--- | :---: |
| **Sufficient Volume** | 7,833 Pune records (exceeds 1,000-row minimum threshold) | **PASS** |
| **Data Completeness** | 0 nulls, 0 unparseable rows, 0 duplicate IDs | **PASS** |
| **Target Variable Feasibility** | Clean numeric INR Lakhs with well-behaved continuous distribution | **PASS** |
| **Pipeline Suitability** | Fully suitable for scikit-learn transformers, CV, serialization, and API integration | **PASS** |
| **Market-Facing Disclaimers** | Mandatory disclaimers stating predictions reflect a synthetic development dataset | **REQUIRED** |

---

## 9. Verification Performed

- Executed `scripts/inspect_dataset.py` (read-only profiling generating `data/processed/dataset_profile.json`).
- Executed `scripts/generate_eda_plots.py` (generating 4 SVG vector charts in `docs/dataset/plots/`).
- Verified that `data/raw/pune_housing_raw.csv` was **not modified** (file size remains 8,335,049 bytes).
- Verified that `.gitignore` prevents raw CSV and generated plots/processed data from untracked Git leakage.
- Updated [`docs/dataset/DATA_DICTIONARY.md`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/DATA_DICTIONARY.md) and [`docs/dataset/DATASET_FEASIBILITY_AUDIT.md`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/DATASET_FEASIBILITY_AUDIT.md) with confirmed schema and empirical findings.

---

*This report completes Phase 2.0. In accordance with safety rules, no model training, dependency installation, or application code implementation will occur until approved by the product owner.*
