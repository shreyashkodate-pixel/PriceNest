"""
PriceNest — Property Price Estimation Pydantic Schemas
"""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class PredictionRequestSchema(BaseModel):
    locality_name: str = Field(
        ...,
        min_length=2,
        max_length=128,
        description="Pune locality / micro-market name (e.g., Baner, Wakad, Kothrud)",
        examples=["Baner"],
    )
    locality_id: Optional[str] = Field(
        None,
        description="Optional UUID of the canonical locality record",
    )
    total_sqft: float = Field(
        ...,
        ge=200.0,
        le=25000.0,
        description="Super Built-up Area in square feet",
        examples=[1050.0],
    )
    bhk: float = Field(
        ...,
        ge=1.0,
        le=10.0,
        description="Bedroom count (supports half-BHK e.g., 2.5)",
        examples=[2.0],
    )
    bathrooms: int = Field(
        ...,
        ge=1,
        le=10,
        description="Number of bathrooms",
        examples=[2],
    )
    balconies: Optional[int] = Field(
        1,
        ge=0,
        le=6,
        description="Number of balconies",
    )
    floor_number: Optional[int] = Field(
        2,
        ge=0,
        le=100,
        description="Property floor number (0 for Ground)",
    )
    total_floors: Optional[int] = Field(
        10,
        ge=1,
        le=100,
        description="Total floors in building",
    )
    age_of_property: Optional[float] = Field(
        3.0,
        ge=0.0,
        le=100.0,
        description="Property age in years",
    )
    distance_to_metro_km: Optional[float] = Field(
        2.5,
        ge=0.0,
        le=50.0,
        description="Distance to closest metro station in kilometers",
    )
    distance_to_city_center_km: Optional[float] = Field(
        8.0,
        ge=0.0,
        le=50.0,
        description="Distance to central Pune in kilometers",
    )
    parking: Optional[int] = Field(
        1,
        ge=0,
        le=10,
        description="Dedicated parking slots",
    )
    lift_available: Optional[bool] = Field(
        True,
        description="Whether elevator access is available",
    )
    gated_community: Optional[bool] = Field(
        True,
        description="Whether property is inside a gated community / society",
    )
    property_type: Optional[str] = Field(
        "Apartment",
        description="Type of property: Apartment, Builder Floor, Independent House, or Villa",
    )
    furnishing: Optional[str] = Field(
        "semi_furnished",
        description="Furnishing status: unfurnished, semi_furnished, or fully_furnished",
    )
    locality_type: Optional[str] = Field(
        None,
        description="Locality tier: Affordable, Mid-Range, or Premium",
    )

    @model_validator(mode="after")
    def validate_physical_feasibility(self) -> "PredictionRequestSchema":
        # 1. Total area must be realistic for BHK count
        min_sqft_for_bhk = self.bhk * 150.0
        if self.total_sqft < min_sqft_for_bhk:
            raise ValueError(
                f"Area of {self.total_sqft} sq.ft. is non-physical for {self.bhk} BHK "
                f"(minimum realistic threshold: {min_sqft_for_bhk} sq.ft.)."
            )

        # 2. Floor number cannot exceed total floors
        if self.floor_number is not None and self.total_floors is not None:
            if self.floor_number > self.total_floors:
                raise ValueError(
                    f"Floor number ({self.floor_number}) cannot exceed total building floors ({self.total_floors})."
                )

        return self


class PriceRange(BaseModel):
    min_inr: float
    max_inr: float
    formatted_range: str


class ModelMetadataResponse(BaseModel):
    version: str
    algorithm: str
    latency_ms: float


class PredictionData(BaseModel):
    prediction_id: str
    predicted_price_inr: float
    predicted_price_lakhs: float
    formatted_price: str
    price_range: PriceRange
    per_sqft_rate_inr: float
    formatted_per_sqft_rate: str
    confidence_score: Optional[float] = None
    model_metadata: ModelMetadataResponse
    disclaimer: str
