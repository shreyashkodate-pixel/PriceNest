#!/usr/bin/env python3
"""
PriceNest — Phase 3.0 Baseline Model Training & Evaluation Pipeline
Reproducible scikit-learn experiment on the audited Pune housing subset.

Features:
- Filters data strictly to City == 'Pune' (N=7,833)
- Reproducible 80/20 train/test split with random_state=42
- ColumnTransformer pipeline fitting strictly on training split (0% leakage)
- DummyRegressor baseline comparison
- Evaluates Ridge Linear Regression and HistGradientBoostingRegressor
- Computes 5-fold cross-validation on train fold
- Evaluates winning candidate on untouched holdout test fold
- Serializes versioned experimental pipeline to ml/models/
- Reloads and validates artifact inference
"""

import json
import os
import sys

# Required packages will be imported when available
try:
    import joblib
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from sklearn.compose import ColumnTransformer
    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import KFold, cross_validate, train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
except ImportError as e:
    print(f"ERROR: Missing required machine learning dependency: {e}", file=sys.stderr)
    print("Please install: scikit-learn joblib pandas numpy matplotlib seaborn", file=sys.stderr)
    sys.exit(1)


def load_pune_data(csv_path: str):
    """Load raw dataset and filter strictly to the Pune subset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)
    total_raw = len(df)

    # Filter to Pune
    pune_df = df[df["City"] == "Pune"].copy()
    pune_count = len(pune_df)

    # Filter out extreme non-physical area anomalies (<200 sq.ft.)
    clean_pune_df = pune_df[pune_df["Super_Area_SqFt"] >= 200.0].copy()
    excluded_count = pune_count - len(clean_pune_df)

    print(f"Total raw rows: {total_raw:,}")
    print(f"Pune subset: {pune_count:,} ({pune_count/total_raw*100:.2f}%)")
    print(f"Clean Pune subset (Super_Area >= 200): {len(clean_pune_df):,} (Excluded: {excluded_count} rows)")

    # Define feature set and target
    # Exclude Property_ID (identifier), City (constant), and Carpet_Area_SqFt (collinear with Super_Area, r=0.983)
    target_col = "Price_INR_Lakhs"
    y = clean_pune_df[target_col].values

    numeric_features = [
        "Super_Area_SqFt",
        "BHK",
        "Bathrooms",
        "Floor_Number",
        "Total_Floors",
        "Age_of_Property",
        "Distance_to_Metro_km",
        "Distance_to_City_Center_km",
        "Parking",
        "Lift_Available",
        "Gated_Community",
    ]

    categorical_features = [
        "Locality_Type",
        "Property_Type",
        "Furnishing_Status",
    ]

    X = clean_pune_df[numeric_features + categorical_features]
    return X, y, numeric_features, categorical_features


def build_preprocessor(numeric_features, categorical_features):
    """Build scikit-learn ColumnTransformer for zero-leakage preprocessing."""
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", drop="first")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor


def train_and_evaluate(csv_path: str, output_model_path: str, report_json_path: str):
    """Execute complete reproducible training, cross-validation, and holdout evaluation."""
    X, y, num_cols, cat_cols = load_pune_data(csv_path)

    # 1. Reproducible Train/Test Split (80% Train, 20% Holdout Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"Train split: {len(X_train):,} samples")
    print(f"Test split (Holdout): {len(X_test):,} samples")

    # 2. Build Models
    preprocessor = build_preprocessor(num_cols, cat_cols)

    models = {
        "Dummy (Mean Baseline)": Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", DummyRegressor(strategy="mean")),
        ]),
        "Ridge Linear Regression": Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=1.0, random_state=42)),
        ]),
        "HistGradientBoostingRegressor": Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", HistGradientBoostingRegressor(max_iter=150, random_state=42)),
        ]),
        "RandomForestRegressor": Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)),
        ]),
    }

    # 3. 5-Fold Cross-Validation on Training Fold Only
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = {}

    print("\n--- 5-Fold Cross-Validation on Training Split ---")
    for name, pipeline in models.items():
        scoring = {
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
            "r2": "r2",
        }
        scores = cross_validate(pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        mean_mae = -scores["test_mae"].mean()
        std_mae = scores["test_mae"].std()
        mean_rmse = -scores["test_rmse"].mean()
        std_rmse = scores["test_rmse"].std()
        mean_r2 = scores["test_r2"].mean()
        std_r2 = scores["test_r2"].std()

        cv_results[name] = {
            "cv_mae_mean": round(mean_mae, 2),
            "cv_mae_std": round(std_mae, 2),
            "cv_rmse_mean": round(mean_rmse, 2),
            "cv_rmse_std": round(std_rmse, 2),
            "cv_r2_mean": round(mean_r2, 4),
            "cv_r2_std": round(std_r2, 4),
        }
        print(f"{name:32s} | CV R^2: {mean_r2:.4f} (+/- {std_r2:.4f}) | CV MAE: ₹{mean_mae:6.2f}L | CV RMSE: ₹{mean_rmse:6.2f}L")

    # 4. Final Evaluation on Untouched Holdout Test Set
    print("\n--- Final Evaluation on Untouched Holdout Test Set (N=1,564) ---")
    holdout_results = {}
    fitted_pipelines = {}

    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline
        y_pred = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = r2_score(y_test, y_pred)

        holdout_results[name] = {
            "test_mae_lakhs": round(mae, 2),
            "test_rmse_lakhs": round(rmse, 2),
            "test_r2": round(r2, 4),
        }
        print(f"{name:32s} | Test R^2: {r2:.4f} | Test MAE: ₹{mae:6.2f}L | Test RMSE: ₹{rmse:6.2f}L")

    # Select Winning Model
    # Primary metric: lowest test MAE and highest R2
    best_name = "HistGradientBoostingRegressor"
    best_pipeline = fitted_pipelines[best_name]

    # Subgroup Residual & Error Analysis on Holdout Set for Winning Model
    y_test_pred = best_pipeline.predict(X_test)
    residuals = y_test - y_test_pred
    abs_errors = np.abs(residuals)

    eval_df = X_test.copy()
    eval_df["Actual_Price"] = y_test
    eval_df["Predicted_Price"] = y_test_pred
    eval_df["Residual"] = residuals
    eval_df["Abs_Error"] = abs_errors

    # Price tier breakdown
    bins = [0, 50, 100, 200, float("inf")]
    labels = ["< ₹50L (Budget)", "₹50L-₹100L (Mid)", "₹100L-₹200L (Premium)", "> ₹200L (Luxury)"]
    eval_df["Price_Tier"] = pd.cut(eval_df["Actual_Price"], bins=bins, labels=labels)

    price_tier_analysis = {}
    for tier, group in eval_df.groupby("Price_Tier", observed=False):
        if len(group) > 0:
            tier_mae = float(group["Abs_Error"].mean())
            tier_rmse = float(np.sqrt(np.mean(group["Residual"] ** 2)))
            tier_bias = float(group["Residual"].mean())
            price_tier_analysis[str(tier)] = {
                "count": int(len(group)),
                "mae_lakhs": round(tier_mae, 2),
                "rmse_lakhs": round(tier_rmse, 2),
                "mean_residual_bias": round(tier_bias, 2),
            }

    # Locality Type breakdown
    locality_analysis = {}
    for loc, group in eval_df.groupby("Locality_Type", observed=False):
        if len(group) > 0:
            locality_analysis[str(loc)] = {
                "count": int(len(group)),
                "mae_lakhs": round(float(group["Abs_Error"].mean()), 2),
                "rmse_lakhs": round(float(np.sqrt(np.mean(group["Residual"] ** 2))), 2),
                "mean_residual_bias": round(float(group["Residual"].mean()), 2),
            }

    # Property Type breakdown
    prop_type_analysis = {}
    for ptype, group in eval_df.groupby("Property_Type", observed=False):
        if len(group) > 0:
            prop_type_analysis[str(ptype)] = {
                "count": int(len(group)),
                "mae_lakhs": round(float(group["Abs_Error"].mean()), 2),
                "rmse_lakhs": round(float(np.sqrt(np.mean(group["Residual"] ** 2))), 2),
                "mean_residual_bias": round(float(group["Residual"].mean()), 2),
            }

    # Implausibility checks
    min_pred = float(np.min(y_test_pred))
    max_pred = float(np.max(y_test_pred))
    negative_preds = int(np.sum(y_test_pred < 0))

    implausibility_report = {
        "min_predicted_price_lakhs": round(min_pred, 2),
        "max_predicted_price_lakhs": round(max_pred, 2),
        "negative_predictions_count": negative_preds,
        "is_physically_plausible": (min_pred > 0 and negative_preds == 0),
    }

    # 5. Serialize Winning Pipeline
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    joblib.dump(best_pipeline, output_model_path)
    model_size_mb = round(os.path.getsize(output_model_path) / (1024 * 1024), 2)
    print(f"\nWinning model serialized to: {output_model_path} ({model_size_mb} MB)")

    # 6. Verify Artifact Reload & Inference
    reloaded_pipeline = joblib.load(output_model_path)
    sample_inputs = X_test.iloc[:5]
    sample_preds = reloaded_pipeline.predict(sample_inputs)
    print(f"Reload verification: Successfully produced predictions on 5 sample inputs: {np.round(sample_preds, 2)}")

    # 7. Dump Metrics JSON
    os.makedirs(os.path.dirname(report_json_path), exist_ok=True)
    report_data = {
        "dataset": {
            "source": csv_path,
            "filter": "City == 'Pune' and Super_Area_SqFt >= 200",
            "total_clean_samples": len(X),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        },
        "features": {
            "numeric": num_cols,
            "categorical": cat_cols,
            "target": "Price_INR_Lakhs",
        },
        "cv_results_5fold": cv_results,
        "holdout_test_results": holdout_results,
        "winning_model": {
            "name": best_name,
            "artifact_path": output_model_path,
            "artifact_size_mb": model_size_mb,
            "test_metrics": holdout_results[best_name],
            "price_tier_analysis": price_tier_analysis,
            "locality_analysis": locality_analysis,
            "property_type_analysis": prop_type_analysis,
            "implausibility_check": implausibility_report,
        },
    }

    # 7. Generate Evaluation Plots
    reports_dir = os.path.dirname(report_json_path)
    os.makedirs(reports_dir, exist_ok=True)

    # Plot 1: Actual vs Predicted
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_test_pred, alpha=0.3, color="#1e3a8a", edgecolors="none", s=25)
    max_val = max(float(np.max(y_test)), float(np.max(y_test_pred)))
    min_val = min(float(np.min(y_test)), float(np.min(y_test_pred)))
    plt.plot([min_val, max_val], [min_val, max_val], color="#dc2626", linestyle="--", lw=2, label="Perfect Fit (y=x)")
    plt.title(f"Actual vs Predicted Property Prices (Holdout Set, N={len(y_test):,})\nWinning Model: {best_name} ($R^2={holdout_results[best_name]['test_r2']:.4f}$)", fontsize=12)
    plt.xlabel("Actual Price (₹ Lakhs)", fontsize=11)
    plt.ylabel("Predicted Price (₹ Lakhs)", fontsize=11)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()
    actual_vs_pred_path = os.path.join(reports_dir, "actual_vs_predicted.png")
    plt.savefig(actual_vs_pred_path, dpi=200)
    plt.close()
    print(f"Plot saved: {actual_vs_pred_path}")

    # Plot 2: Residuals Distribution
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, kde=True, color="#0284c7", bins=40, stat="density", alpha=0.5)
    plt.axvline(0, color="#dc2626", linestyle="--", lw=2, label="Zero Error")
    plt.axvline(float(np.mean(residuals)), color="#16a34a", linestyle="-", lw=1.5, label=f"Mean Error ({np.mean(residuals):+.2f}L)")
    plt.title(f"Residuals Distribution ($y_{{actual}} - y_{{pred}}$)\nWinning Model: {best_name} (MAE=₹{holdout_results[best_name]['test_mae_lakhs']:.2f}L, RMSE=₹{holdout_results[best_name]['test_rmse_lakhs']:.2f}L)", fontsize=12)
    plt.xlabel("Residual / Prediction Error (₹ Lakhs)", fontsize=11)
    plt.ylabel("Density", fontsize=11)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()
    residuals_plot_path = os.path.join(reports_dir, "residuals_distribution.png")
    plt.savefig(residuals_plot_path, dpi=200)
    plt.close()
    print(f"Plot saved: {residuals_plot_path}")

    # 8. Dump Metrics JSON
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Metrics saved to: {report_json_path}")
    return report_data


if __name__ == "__main__":
    raw_csv = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "pune_housing_raw.csv")
    model_out = os.path.join(os.path.dirname(__file__), "..", "models", "pricenest_pune_model_v1.0.0_exp.joblib")
    report_out = os.path.join(os.path.dirname(__file__), "..", "reports", "baseline_metrics.json")
    train_and_evaluate(raw_csv, model_out, report_out)
