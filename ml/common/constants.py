"""
PriceNest — Machine Learning Common Constants
Single Source of Truth for feature schemas, categories, physical bounds, and disclaimers.
"""

from typing import Dict, List

# Authoritative feature definitions expected by the trained pipeline
NUMERIC_FEATURES: List[str] = [
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

CATEGORICAL_FEATURES: List[str] = [
    "Locality_Type",
    "Property_Type",
    "Furnishing_Status",
]

ALL_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES

TARGET_COLUMN: str = "Price_INR_Lakhs"

# Categorical domain values learned during training
VALID_LOCALITY_TYPES: List[str] = ["Affordable", "Mid-Range", "Premium"]
VALID_PROPERTY_TYPES: List[str] = ["Apartment", "Builder Floor", "Independent House", "Villa"]
VALID_FURNISHING_STATUS: List[str] = ["Furnished", "Semi-Furnished", "Unfurnished"]

# Physical feasibility constraints
MIN_SUPER_AREA_SQFT: float = 200.0
MAX_SUPER_AREA_SQFT: float = 25000.0
MIN_BHK: float = 1.0
MAX_BHK: float = 10.0
MIN_SQFT_PER_BHK: float = 150.0
MIN_BATHROOMS: int = 1
MAX_BATHROOMS: int = 10

# Subgroup MAE tiers from Phase 3 evaluation report for empirical uncertainty estimation
MAE_TIERS: Dict[str, float] = {
    "budget": 14.68,   # < ₹50L
    "mid": 19.07,      # ₹50L - ₹100L
    "premium": 30.86,  # ₹100L - ₹200L
    "luxury": 70.68,   # > ₹200L
}

# Mandatory Synthetic Data Disclaimer (SRS Section 4.3 & PRD Section 6)
DISCLAIMER_NOTICE: str = (
    "This estimate is generated algorithmically for educational and developmental purposes "
    "using an exploratory dataset. It does not represent a certified real-estate valuation "
    "or legal deed record."
)

DEFAULT_MODEL_VERSION: str = "v1.0.0"
DEFAULT_MODEL_FILENAME: str = "pricenest_pune_model_v1.0.0_exp.joblib"
