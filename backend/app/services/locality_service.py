"""
PriceNest — Pune Micro-Market Localities Management Service
"""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.locality import Locality
from backend.app.schemas.locality import LocalityItemData, LocalityListResponseData

INITIAL_PUNE_LOCALITIES = [
    {
        "name": "Baner",
        "slug": "baner",
        "zone": "West Pune",
        "locality_type": "Premium",
        "pincode": "411045",
        "latitude": 18.5590,
        "longitude": 73.7868,
        "benchmark_price_per_sqft": 8200.0,
    },
    {
        "name": "Wakad",
        "slug": "wakad",
        "zone": "PCMC",
        "locality_type": "Mid-Range",
        "pincode": "411057",
        "latitude": 18.5987,
        "longitude": 73.7686,
        "benchmark_price_per_sqft": 7100.0,
    },
    {
        "name": "Kothrud",
        "slug": "kothrud",
        "zone": "West Pune",
        "locality_type": "Premium",
        "pincode": "411038",
        "latitude": 18.5074,
        "longitude": 73.8077,
        "benchmark_price_per_sqft": 9500.0,
    },
    {
        "name": "Hinjewadi",
        "slug": "hinjewadi",
        "zone": "West Pune",
        "locality_type": "Mid-Range",
        "pincode": "411057",
        "latitude": 18.5913,
        "longitude": 73.7389,
        "benchmark_price_per_sqft": 6800.0,
    },
    {
        "name": "Kharadi",
        "slug": "kharadi",
        "zone": "East Pune",
        "locality_type": "Mid-Range",
        "pincode": "411014",
        "latitude": 18.5515,
        "longitude": 73.9349,
        "benchmark_price_per_sqft": 7600.0,
    },
    {
        "name": "Viman Nagar",
        "slug": "viman-nagar",
        "zone": "East Pune",
        "locality_type": "Premium",
        "pincode": "411014",
        "latitude": 18.5679,
        "longitude": 73.9143,
        "benchmark_price_per_sqft": 9800.0,
    },
    {
        "name": "Koregaon Park",
        "slug": "koregaon-park",
        "zone": "Central Pune",
        "locality_type": "Premium",
        "pincode": "411001",
        "latitude": 18.5362,
        "longitude": 73.8940,
        "benchmark_price_per_sqft": 14500.0,
    },
    {
        "name": "Aundh",
        "slug": "aundh",
        "zone": "West Pune",
        "locality_type": "Premium",
        "pincode": "411007",
        "latitude": 18.5602,
        "longitude": 73.8031,
        "benchmark_price_per_sqft": 9200.0,
    },
    {
        "name": "Hadapsar",
        "slug": "hadapsar",
        "zone": "East Pune",
        "locality_type": "Affordable",
        "pincode": "411028",
        "latitude": 18.5089,
        "longitude": 73.9260,
        "benchmark_price_per_sqft": 5800.0,
    },
    {
        "name": "Wagholi",
        "slug": "wagholi",
        "zone": "East Pune",
        "locality_type": "Affordable",
        "pincode": "412207",
        "latitude": 18.5808,
        "longitude": 73.9787,
        "benchmark_price_per_sqft": 5200.0,
    },
    {
        "name": "Bavdhan",
        "slug": "bavdhan",
        "zone": "West Pune",
        "locality_type": "Mid-Range",
        "pincode": "411021",
        "latitude": 18.5134,
        "longitude": 73.7699,
        "benchmark_price_per_sqft": 7400.0,
    },
    {
        "name": "Pimple Saudagar",
        "slug": "pimple-saudagar",
        "zone": "PCMC",
        "locality_type": "Mid-Range",
        "pincode": "411027",
        "latitude": 18.5987,
        "longitude": 73.7978,
        "benchmark_price_per_sqft": 7500.0,
    },
]


class LocalityService:
    """Service providing query and autocomplete operations on Pune localities."""

    async def list_localities(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        zone: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> LocalityListResponseData:
        # Check if table is empty, auto-seed defaults if needed
        count_stmt = select(func.count(Locality.id))
        total_in_db = (await db.execute(count_stmt)).scalar() or 0
        if total_in_db == 0:
            await self.seed_initial_localities(db)

        stmt = select(Locality).where(Locality.is_active == True)  # noqa: E712
        if query:
            stmt = stmt.where(Locality.name.ilike(f"%{query.strip()}%"))
        if zone:
            stmt = stmt.where(Locality.zone == zone.strip())

        # Count filtered
        count_filtered_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_filtered_stmt)).scalar() or 0

        # Paginate
        stmt = stmt.order_by(Locality.name.asc()).offset(offset).limit(min(limit, 200))
        result = await db.execute(stmt)
        items = result.scalars().all()

        return LocalityListResponseData(
            total=total,
            items=[
                LocalityItemData(
                    id=loc.id,
                    name=loc.name,
                    slug=loc.slug,
                    zone=loc.zone,
                    locality_type=loc.locality_type,
                    pincode=loc.pincode,
                    benchmark_price_per_sqft=loc.benchmark_price_per_sqft,
                    is_active=loc.is_active,
                )
                for loc in items
            ],
        )

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Locality]:
        stmt = select(Locality).where(Locality.name.ilike(name.strip()))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def seed_initial_localities(self, db: AsyncSession) -> None:
        """Seed initial Pune micro-markets into the localities table."""
        for item in INITIAL_PUNE_LOCALITIES:
            existing = await self.get_by_name(db, item["name"])
            if not existing:
                loc = Locality(
                    name=item["name"],
                    slug=item["slug"],
                    zone=item["zone"],
                    locality_type=item["locality_type"],
                    pincode=item.get("pincode"),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    benchmark_price_per_sqft=item.get("benchmark_price_per_sqft"),
                    is_active=True,
                )
                db.add(loc)
        await db.flush()


locality_service = LocalityService()
