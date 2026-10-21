# PriceNest — Data Directory Guide & Provenance

This directory defines the local file structure, storage protocols, and provenance guidelines for all datasets used in the PriceNest real-estate price prediction engine.

---

## 1. Directory Layout

```
data/
├── README.md               # Data storage, provenance, and privacy policies (this file)
├── raw/                    # Untouched, original dataset downloads (ignored by Git)
│   └── .gitkeep
└── processed/              # Cleaned, transformed, feature-engineered datasets (ignored by Git)
    └── .gitkeep
```

> **IMPORTANT:** All CSV, TSV, Parquet, and Excel files stored in `data/raw/` and `data/processed/` are strictly excluded from version control via `.gitignore`. Never commit raw data files, data extracts, or proprietary property records to the Git repository.

---

## 2. Dataset Storage & Local Setup

When downloading datasets for development or experimentation:

1. **Local Raw Storage Path:**
   Place the downloaded CSV into:
   ```bash
   data/raw/pune_housing_raw.csv
   ```
2. **Intermediate & Processed Storage Path:**
   Output transformed, cleaned, and feature-engineered splits into:
   ```bash
   data/processed/pune_housing_cleaned.parquet
   data/processed/train.parquet
   data/processed/test.parquet
   ```
3. **Storage Hygiene:**
   - Keep filenames consistent, lowercase, and snake_cased.
   - Never edit files in `data/raw/` manually. All transformations must be deterministic, reproducible, and executed via scripts or notebooks in `ml/`.

---

## 3. Dataset Provenance & Nature

### Development Dataset Origin
- **Source Platform:** Kaggle (Pune Housing / Real Estate Dataset).
- **Intended Usage:** Strictly for local prototyping, baseline feature engineering, pipeline scaffolding, and algorithmic experimentation.

### Critical Notice on Synthetic Nature & Real-World Accuracy
- **Synthetic & Heuristic Nature:** The Kaggle dataset used during this initial development phase contains synthetic or heuristically generated observations. 
- **Non-Verified Records:** This dataset **does NOT represent verified government deed registrations, authenticated index-II property records, or legally audited property transactions in Pune, Maharashtra.**
- **No Direct Financial Reliance:** Estimates derived from this development dataset must never be treated as legal appraisals, certified financial valuations, or guaranteed market values for real-estate purchases, mortgages, or investments.
- **Consumer Disclaimers:** Any user-facing interface displaying predictions derived from this baseline model must include prominent disclaimers regarding model scope, estimation confidence, and synthetic training data provenance.

---

## 4. Dataset Inspection Status

Detailed schema audit, column statistics, missing value ratios, and distributions are documented in:
- [`docs/dataset/DATASET_FEASIBILITY_AUDIT.md`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/DATASET_FEASIBILITY_AUDIT.md)
- [`docs/dataset/DATA_DICTIONARY.md`](file:///Users/apple/Documents/Projects/PriceNest/docs/dataset/DATA_DICTIONARY.md)

| Attribute | Status | Notes |
| :--- | :--- | :--- |
| **Exact Column Names** | **Pending Direct Inspection** | To be verified during Phase 2 exploratory data analysis (EDA). |
| **Target Variable Semantics** | **Pending Direct Inspection** | To be verified (e.g., total price in INR Lakhs vs. price per sq. ft.). |
| **Sample Size & Split** | **Pending Direct Inspection** | Exact row count and distribution pending initial load. |
| **License & Attribution** | **Pending Direct Inspection** | Kaggle contributor license terms to be documented upon file audit. |
| **Geographic Bounds** | **Pending Direct Inspection** | Pune Municipal Corporation (PMC), PCMC, and PMRDA locality representation to be audited. |

---

## 5. Data Privacy & Compliance
- Ensure no Personally Identifiable Information (PII) such as individual buyer names, phone numbers, email addresses, or exact flat/unit numbers are collected, stored, or processed.
- All spatial data is aggregated at the micro-market or locality level (e.g., Baner, Wakad, Kothrud, Viman Nagar).
