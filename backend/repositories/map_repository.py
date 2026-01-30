"""
Map repository - Database operations for maps.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.database import Map
from backend.repositories.base import BaseRepository


class MapRepository(BaseRepository[Map]):
    """Repository for Map entity operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Map, db)
    
    async def get_by_name(self, name: str) -> Optional[Map]:
        """Get a map by name."""
        result = await self.db.execute(
            select(Map).where(Map.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_file_path(self, file_path: str) -> Optional[Map]:
        """Get a map by file path."""
        result = await self.db.execute(
            select(Map).where(Map.file_path == file_path)
        )
        return result.scalar_one_or_none()
    
    async def get_by_file_hash(self, file_hash: str) -> Optional[Map]:
        """Get a map by file hash (for deduplication)."""
        result = await self.db.execute(
            select(Map).where(Map.file_hash == file_hash)
        )
        return result.scalar_one_or_none()
    
    async def get_by_scenario(
        self, 
        scenario: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Map]:
        """Get all maps for a specific scenario."""
        result = await self.db.execute(
            select(Map)
            .where(Map.scenario == scenario)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def search_by_name(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Map]:
        """Search maps by name (case-insensitive)."""
        result = await self.db.execute(
            select(Map)
            .where(Map.name.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
