"""
PriceNest — Valuation Feedback Pydantic Schemas
"""

from typing import Optional

from pydantic import BaseModel, Field


class ValuationFeedbackRequest(BaseModel):
    feedback_type: str = Field(
        ...,
        description="Sentiment: accurate, too_high, or too_low",
        examples=["accurate"],
    )
    reported_actual_price_inr: Optional[float] = Field(
        None,
        description="User-reported actual market price in INR",
        examples=[8100000.00],
    )
    comments: Optional[str] = Field(
        None,
        description="Qualitative user observations",
        examples=["Matches recent purchase in a neighboring society."],
    )


class ValuationFeedbackResponseData(BaseModel):
    feedback_id: str
    prediction_id: str
    status: str = "recorded"
