"""
Run repository - Database operations for runs.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.models.database import Run, RunStatus, RunType
from backend.repositories.base import BaseRepository


class RunRepository(BaseRepository[Run]):
    """Repository for Run entity operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Run, db)
    
    async def get_by_map_id(
        self, 
        map_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Run]:
        """Get all runs for a specific map."""
        result = await self.db.execute(
            select(Run)
            .where(Run.map_id == map_id)
            .order_by(Run.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_status(
        self, 
        status: RunStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Run]:
        """Get all runs with a specific status."""
        result = await self.db.execute(
            select(Run)
            .where(Run.status == status)
            .order_by(Run.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_type(
        self, 
        run_type: RunType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Run]:
        """Get all runs of a specific type."""
        result = await self.db.execute(
            select(Run)
            .where(Run.run_type == run_type)
            .order_by(Run.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_metrics(self, run_id: int) -> Optional[Run]:
        """Get a run with its metrics loaded."""
        result = await self.db.execute(
            select(Run)
            .options(joinedload(Run.metrics))
            .where(Run.id == run_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_runs(self, limit: int = 10) -> List[Run]:
        """Get pending runs waiting to be executed."""
        result = await self.db.execute(
            select(Run)
            .where(Run.status == RunStatus.PENDING)
            .order_by(Run.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_running_runs(self) -> List[Run]:
        """Get currently running runs."""
        result = await self.db.execute(
            select(Run).where(Run.status == RunStatus.RUNNING)
        )
        return list(result.scalars().all())
    
    async def update_status(
        self, 
        run_id: int, 
        status: RunStatus,
        error_message: Optional[str] = None
    ) -> Optional[Run]:
        """Update run status with optional error message."""
        update_data = {"status": status}
        
        if status == RunStatus.RUNNING:
            update_data["started_at"] = datetime.utcnow()
        elif status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
            update_data["completed_at"] = datetime.utcnow()
        
        if error_message:
            update_data["error_message"] = error_message
        
        return await self.update(run_id, **update_data)
    
    async def count_by_map(self, map_id: int) -> int:
        """Count runs for a specific map."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).select_from(Run).where(Run.map_id == map_id)
        )
        return result.scalar_one()
