"""
PriceNest — Machine Learning Pipeline Architecture
Constructs reusable scikit-learn ColumnTransformer and Pipeline objects.
"""

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.common.constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES


def build_preprocessor() -> ColumnTransformer:
    """Build scikit-learn ColumnTransformer for zero-leakage numeric scaling and categorical encoding."""
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", drop="first")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def build_pipeline(regressor=None) -> Pipeline:
    """
    Construct a complete end-to-end pipeline bundling preprocessing and regression estimator.
    Defaults to HistGradientBoostingRegressor.
    """
    if regressor is None:
        regressor = HistGradientBoostingRegressor(max_iter=150, random_state=42)

    return Pipeline([
        ("preprocessor", build_preprocessor()),
        ("regressor", regressor),
    ])
