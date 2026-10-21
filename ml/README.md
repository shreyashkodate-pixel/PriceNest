# PriceNest — Machine Learning & Analytics Subsystem

This directory contains the machine learning pipelines, exploratory data analysis (EDA), feature engineering workflows, training scripts, and serialized model artifacts for PriceNest.

---

## 1. Directory Structure

```
ml/
├── README.md               # ML architecture and operational guide (this file)
├── notebooks/              # Jupyter notebooks for EDA and experimental modeling
│   └── .gitkeep
├── src/                    # Modular Python ML package
│   ├── __init__.py
│   ├── validation.py       # Dataset schema and anomaly verification
│   ├── preprocessing.py    # Cleaning, encoding, and imputation logic
│   ├── features.py         # Feature engineering transforms
│   ├── train.py            # Model training & cross-validation pipeline
│   ├── evaluate.py         # Metrics generation (MAE, RMSE, R2, MAPE)
│   └── inference.py        # Inference adapter and output validation
├── reports/                # Evaluation reports, metric dumps, residual plots (Phase 3)
│   └── .gitkeep
├── tests/                  # ML test suite (leakage, schema, pipeline tests per SRS 9.2)
│   ├── __init__.py
│   ├── test_preprocessing.py
│   ├── test_training_pipeline.py
│   └── test_inference.py
└── models/                 # Serialized production model artifacts (git-ignored)
    └── .gitkeep
```


---

## 2. Technology Stack & Tools

- **Core Data Processing:** `pandas`, `numpy`
- **Visualization & EDA:** `matplotlib`, `seaborn`
- **Machine Learning Engine:** `scikit-learn`
- **Serialization & Persistence:** `joblib`
- **Experiment Tracking / Reports:** JSON metric dumps and Markdown run summaries

---

## 3. Modeling Lifecycle & Methodology

1. **Exploratory Data Analysis (EDA):**
   - Profile data distributions, missingness patterns, skewness, and cardinality of categorical features (such as Pune localities).
   - Identify outliers in price and area (e.g., impossible square footage per bedroom, luxury ultra-high-end penthouses vs affordable housing).
2. **Feature Engineering & Preprocessing:**
   - Standardize area metrics (carpet area, built-up area, super built-up area).
   - Micro-market spatial grouping: target encoding, frequency encoding, or one-hot encoding for high-cardinality locality features.
   - Property age, BHK configuration, bathroom-to-room ratio, and floor level indexation.
3. **Model Selection & Validation:**
   - Baseline models: Linear Regression, Ridge/Lasso regularized baselines.
   - Non-linear ensemble candidates: Random Forest Regressor, Gradient Boosting / HistGradientBoosting.
   - Validation Strategy: $K$-Fold cross-validation (with stratification by price quintiles or spatial micro-markets to prevent regional data leakage).
4. **Evaluation Metrics:**
   - Mean Absolute Error (MAE in INR Lakhs)
   - Root Mean Squared Error (RMSE in INR Lakhs)
   - $R^2$ Score (Coefficient of determination)
   - Mean Absolute Percentage Error (MAPE)
5. **Model Serialization:**
   - Pipelines are bundled with the scikit-learn preprocessing pipeline (imputers, scalers, encoders) and the trained estimator into a single atomic `.joblib` file stored in `ml/models/`.

---

## 4. Model Hosting & Serving Strategy (Deferred Protocol)

As confirmed in the project technical architecture:
- **Phase 1 Baseline:** The decision regarding ML model hosting (e.g., embedded directly within the FastAPI backend runtime vs. isolated as an independent microservice / container) is **deferred** until the training and inference pipeline is established and model memory footprint, artifact size, and inference latency are measured.
- **Embedded Direct Inference Candidate:** If the serialized `scikit-learn` pipeline is compact (< 50MB) and CPU latency is low (< 50ms), loading the model directly into memory within FastAPI using `joblib.load()` on application startup provides optimal operational simplicity and minimal infrastructure cost on Render.
- **Standalone Serving Candidate:** If the model requires heavy auxiliary dependencies or larger memory thresholds, a dedicated container service will be evaluated.

---

## 5. Development Notice: Dataset Realism

All models trained during initial development utilize the Kaggle Pune real estate dataset. As noted in [`data/README.md`](file:///Users/apple/Documents/Projects/PriceNest/data/README.md), this dataset is synthetic/exploratory in nature and does not represent verified real-estate deeds. Model evaluation metrics reflect performance on this dataset distribution and must not be published as real-world market predictions without proper disclaimers.
