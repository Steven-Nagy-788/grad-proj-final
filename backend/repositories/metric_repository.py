"""
Metric repository - Database operations for metrics.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from backend.models.database import Metric, Run
from backend.repositories.base import BaseRepository


class MetricRepository(BaseRepository[Metric]):
    """Repository for Metric entity operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Metric, db)
    
    async def get_by_run_id(self, run_id: int) -> Optional[Metric]:
        """Get metrics for a specific run."""
        result = await self.db.execute(
            select(Metric).where(Metric.run_id == run_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_map_id(
        self, 
        map_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Metric]:
        """Get all metrics for runs of a specific map."""
        result = await self.db.execute(
            select(Metric)
            .join(Run)
            .where(Run.map_id == map_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_hardness_range(
        self, 
        min_hardness: float, 
        max_hardness: float,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Metric]:
        """Get metrics within a hardness score range."""
        result = await self.db.execute(
            select(Metric)
            .where(
                and_(
                    Metric.hardness_score >= min_hardness,
                    Metric.hardness_score <= max_hardness
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_solvable_runs(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Metric]:
        """Get metrics for solvable runs."""
        result = await self.db.execute(
            select(Metric)
            .where(Metric.solvability == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_avg_hardness_by_map(self, map_id: int) -> Optional[float]:
        """Get average hardness score for a map."""
        result = await self.db.execute(
            select(func.avg(Metric.hardness_score))
            .join(Run)
            .where(
                and_(
                    Run.map_id == map_id,
                    Metric.hardness_score.isnot(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_avg_kills_by_map(self, map_id: int) -> Optional[float]:
        """Get average kills per episode for a map."""
        result = await self.db.execute(
            select(func.avg(Metric.avg_kills_per_episode))
            .join(Run)
            .where(Run.map_id == map_id)
        )
        return result.scalar_one_or_none()
    
    async def get_hardest_runs(self, limit: int = 10) -> List[Metric]:
        """Get runs with highest hardness scores."""
        result = await self.db.execute(
            select(Metric)
            .where(Metric.hardness_score.isnot(None))
            .order_by(Metric.hardness_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def upsert(self, run_id: int, **kwargs) -> Metric:
        """Create or update metrics for a run."""
        existing = await self.get_by_run_id(run_id)
        if existing:
            return await self.update(existing.id, **kwargs)
        else:
            return await self.create(run_id=run_id, **kwargs)
