# PriceNest — Machine Learning Subsystem (`ml/`)

This directory houses the complete machine learning subsystem for **PriceNest**, strictly decoupled into offline model building (`training/`), production serving (`inference/`), shared pipeline builders (`pipeline/`), and common definitions (`common/`).

---

## 1. Subsystem Architecture

```
ml/
├── training/                      # OFFLINE (experiments + model building)
│   ├── data/                      # local training data references
│   ├── scripts/
│   │   ├── train.py              # Main training entrypoint (SRS FR-07)
│   │   └── evaluate.py           # Subgroup residual and tier analysis
│   ├── experiments/              # Logs and notebook artifacts
│   └── requirements.txt          # Training-only dependencies (matplotlib, seaborn)
│
├── inference/                    # PRODUCTION (used by backend/API)
│   ├── model/
│   │   ├── loader.py             # Safe artifact resolution and caching (SRS FR-08)
│   │   └── predictor.py          # predict() execution and physical bounds
│   ├── services/
│   │   └── prediction_service.py # High-level pricing, currency conversion, ranges
│   └── artifacts/                # Serialized production models (.joblib)
│       └── pricenest_pune_model_v1.0.0_exp.joblib
│
├── pipeline/                     # CORE LOGIC (shared orchestration)
│   ├── __init__.py
│   └── pipeline.py               # build_preprocessor(), build_pipeline()
│
├── common/                       # SHARED CONSTANTS & UTILITIES
│   ├── __init__.py
│   ├── constants.py              # Feature names, categories, disclaimer (Single Source of Truth)
│   └── utils.py                  # Normalizers, Lakhs/Crore formatters, uncertainty ranges
│
└── README.md
```

---

## 2. Core Architectural Principles

1. **Single Source of Truth (`ml/common/constants.py`):**
   - Feature definitions (`NUMERIC_FEATURES`, `CATEGORICAL_FEATURES`) and physical validation thresholds are centralized and imported by both training and inference modules.
2. **Unified Pipeline Packaging (SRS FR-08):**
   - The fitted `ColumnTransformer` (StandardScaler + OneHotEncoder) and estimator (`HistGradientBoostingRegressor`) are serialized together in a single pipeline artifact, eliminating training-serving skew.
3. **Decoupled Serving (`ml/inference/`):**
   - The inference service is self-contained and does not require offline visualization libraries (`matplotlib`, `seaborn`). The FastAPI backend delegates to `ml.inference.services.prediction_service`.
4. **Mandatory Synthetic Data Disclaimer:**
   - Every inference response automatically injects the required algorithmic simulation disclaimer notice.

---

## 3. Usage Workflows

### 3.1 Training a New Model
To train the baseline regression pipeline on the clean Pune dataset:
```bash
python ml/training/scripts/train.py
```
This fits the pipeline, evaluates holdout performance, exports metrics to `ml/reports/baseline_metrics.json`, and serializes the winning model to `ml/inference/artifacts/`.

### 3.2 Evaluating Subgroup Residuals
To inspect residual errors across price tiers (Budget, Mid-Range, Premium, Luxury):
```bash
python ml/training/scripts/evaluate.py
```

### 3.3 Running Inference in Code
```python
from ml.inference.services.prediction_service import prediction_service

result = prediction_service.predict_price({
    "locality_name": "Baner",
    "total_sqft": 1050.0,
    "bhk": 2.0,
    "bathrooms": 2,
    "property_type": "Apartment",
    "furnishing": "semi_furnished",
})

print(result["formatted_price"])        # e.g. "₹1.31 Cr"
print(result["price_range"])             # e.g. "₹1.08 Cr – ₹1.54 Cr"
print(result["formatted_per_sqft_rate"]) # e.g. "₹12,452 / sq.ft."
```
