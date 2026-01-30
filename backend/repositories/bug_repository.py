"""
Bug repository - Database operations for bugs.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from backend.models.database import Bug, Run, BugType, BugSeverity
from backend.repositories.base import BaseRepository


class BugRepository(BaseRepository[Bug]):
    """Repository for Bug entity operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Bug, db)
    
    async def get_by_run_id(
        self, 
        run_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get all bugs for a specific run."""
        result = await self.db.execute(
            select(Bug)
            .where(Bug.run_id == run_id)
            .order_by(Bug.detected_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_map_id(
        self, 
        map_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get all bugs for runs of a specific map."""
        result = await self.db.execute(
            select(Bug)
            .join(Run)
            .where(Run.map_id == map_id)
            .order_by(Bug.detected_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_type(
        self, 
        bug_type: BugType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get bugs of a specific type."""
        result = await self.db.execute(
            select(Bug)
            .where(Bug.bug_type == bug_type)
            .order_by(Bug.detected_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_severity(
        self, 
        severity: BugSeverity, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get bugs of a specific severity."""
        result = await self.db.execute(
            select(Bug)
            .where(Bug.severity == severity)
            .order_by(Bug.detected_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_critical_bugs(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get critical severity bugs."""
        return await self.get_by_severity(BugSeverity.CRITICAL, skip, limit)
    
    async def count_by_run(self, run_id: int) -> int:
        """Count bugs for a specific run."""
        result = await self.db.execute(
            select(func.count()).select_from(Bug).where(Bug.run_id == run_id)
        )
        return result.scalar_one()
    
    async def count_by_type(self, bug_type: BugType) -> int:
        """Count bugs of a specific type."""
        result = await self.db.execute(
            select(func.count()).select_from(Bug).where(Bug.bug_type == bug_type)
        )
        return result.scalar_one()
    
    async def count_by_map(self, map_id: int) -> int:
        """Count bugs for a specific map."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Bug)
            .join(Run)
            .where(Run.map_id == map_id)
        )
        return result.scalar_one()
    
    async def get_summary_by_type(self, run_id: Optional[int] = None) -> dict:
        """Get bug count grouped by type."""
        query = select(Bug.bug_type, func.count(Bug.id)).group_by(Bug.bug_type)
        if run_id:
            query = query.where(Bug.run_id == run_id)
        
        result = await self.db.execute(query)
        return {str(row[0]): row[1] for row in result.all()}
    
    async def get_summary_by_severity(self, run_id: Optional[int] = None) -> dict:
        """Get bug count grouped by severity."""
        query = select(Bug.severity, func.count(Bug.id)).group_by(Bug.severity)
        if run_id:
            query = query.where(Bug.run_id == run_id)
        
        result = await self.db.execute(query)
        return {str(row[0]): row[1] for row in result.all()}
    
    async def bulk_create(self, bugs: List[dict]) -> int:
        """Bulk insert bugs. Returns count of inserted bugs."""
        if not bugs:
            return 0
        
        bug_objects = [Bug(**b) for b in bugs]
        self.db.add_all(bug_objects)
        await self.db.commit()
        return len(bug_objects)
