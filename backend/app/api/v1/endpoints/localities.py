"""
PriceNest — Pune Micro-Market Localities Endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.locality import LocalityListResponseData
from backend.app.services.locality_service import locality_service

router = APIRouter(prefix="/localities", tags=["Localities & Micro-Markets"])


@router.get(
    "",
    response_model=StandardResponse[LocalityListResponseData],
    status_code=status.HTTP_200_OK,
    summary="List supported Pune localities with autocomplete and zone filters",
)
async def list_localities(
    query: Optional[str] = Query(None, description="Substring search for locality name"),
    zone: Optional[str] = Query(None, description="Filter by zone (e.g., West Pune, East Pune, PCMC)"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[LocalityListResponseData]:
    localities_data = await locality_service.list_localities(
        db=db,
        query=query,
        zone=zone,
        limit=limit,
        offset=offset,
    )
    return StandardResponse(data=localities_data)
