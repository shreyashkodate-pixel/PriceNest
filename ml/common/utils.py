"""
PriceNest — Machine Learning Common Utilities
Reusable formatting, normalization, and statistical interval functions.
"""

from typing import Optional, Tuple

from ml.common.constants import MAE_TIERS


def convert_lakhs_to_inr(lakhs: float) -> float:
    """Convert price from Lakhs of INR to absolute INR."""
    return round(float(lakhs) * 100_000.0, 2)


def format_inr_price(pred_lakhs: float) -> str:
    """Format numeric valuation into standard Indian numbering (Lakhs and Crores)."""
    if pred_lakhs >= 100.0:
        cr_val = pred_lakhs / 100.0
        return f"₹{cr_val:.2f} Cr"
    return f"₹{pred_lakhs:.2f} Lakh"


def format_per_sqft(rate_inr: float) -> str:
    """Format per square foot rate into display string."""
    return f"₹{rate_inr:,.0f} / sq.ft."


def normalize_locality_tier(val: Optional[str]) -> str:
    """Normalize raw locality input or tier string to canonical Locality_Type."""
    if not val:
        return "Mid-Range"
    val_clean = str(val).strip().lower()
    if "premium" in val_clean or val_clean in ["baner", "koregaon park", "kalyani nagar", "aundh", "viman nagar"]:
        return "Premium"
    elif "affordable" in val_clean or val_clean in ["wagholi", "hadapsar", "lohegaon", "katraj"]:
        return "Affordable"
    return "Mid-Range"


def normalize_property_type(val: Optional[str]) -> str:
    """Normalize raw property type input to canonical Property_Type."""
    if not val:
        return "Apartment"
    val_clean = str(val).strip().lower()
    if "villa" in val_clean:
        return "Villa"
    elif "house" in val_clean or "independent" in val_clean:
        return "Independent House"
    elif "builder" in val_clean or "floor" in val_clean:
        return "Builder Floor"
    return "Apartment"


def normalize_furnishing(val: Optional[str]) -> str:
    """Normalize raw furnishing status to canonical Furnishing_Status."""
    if not val:
        return "Semi-Furnished"
    val_clean = str(val).strip().lower()
    if "unfurnish" in val_clean:
        return "Unfurnished"
    elif "semi" in val_clean:
        return "Semi-Furnished"
    elif "furnish" in val_clean:
        return "Furnished"
    return "Semi-Furnished"


def calculate_price_range(pred_lakhs: float) -> Tuple[float, float, str]:
    """Compute empirical uncertainty interval around point estimate using subgroup MAE."""
    if pred_lakhs < 50.0:
        delta_lakhs = MAE_TIERS["budget"]
    elif pred_lakhs <= 100.0:
        delta_lakhs = MAE_TIERS["mid"]
    elif pred_lakhs <= 200.0:
        delta_lakhs = MAE_TIERS["premium"]
    else:
        delta_lakhs = MAE_TIERS["luxury"]

    min_lakhs = max(1.0, pred_lakhs - (delta_lakhs * 0.75))
    max_lakhs = pred_lakhs + (delta_lakhs * 0.75)

    min_inr = convert_lakhs_to_inr(min_lakhs)
    max_inr = convert_lakhs_to_inr(max_lakhs)

    def _fmt(v_lakhs: float) -> str:
        if v_lakhs >= 100.0:
            return f"₹{v_lakhs/100:.2f} Cr"
        return f"₹{v_lakhs:.2f} L"

    formatted_range = f"{_fmt(min_lakhs)} – {_fmt(max_lakhs)}"
    return min_inr, max_inr, formatted_range
