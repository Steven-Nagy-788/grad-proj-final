"""
Map service - Business logic for maps.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
from pathlib import Path

from backend.models.database import Map
from backend.models.schemas import MapCreate, MapStats
from backend.repositories.map_repository import MapRepository
from backend.repositories.run_repository import RunRepository
from backend.repositories.metric_repository import MetricRepository
from backend.repositories.bug_repository import BugRepository


class MapService:
    """Service layer for Map operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MapRepository(db)
        self.run_repo = RunRepository(db)
        self.metric_repo = MetricRepository(db)
        self.bug_repo = BugRepository(db)
    
    async def create(self, data: MapCreate) -> Map:
        """Create a new map entry."""
        # Check for duplicates
        existing = await self.repo.get_by_file_path(data.file_path)
        if existing:
            raise ValueError(f"Map with file path already exists: {data.file_path}")
        
        # Calculate file hash if file exists
        file_hash = None
        if Path(data.file_path).exists():
            file_hash = await self._calculate_file_hash(data.file_path)
        
        return await self.repo.create(
            name=data.name,
            file_path=data.file_path,
            file_hash=file_hash,
            scenario=data.scenario,
            metadata=data.metadata
        )
    
    async def get_by_id(self, map_id: int) -> Optional[Map]:
        """Get a map by ID."""
        return await self.repo.get_by_id(map_id)
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        scenario: Optional[str] = None
    ) -> List[Map]:
        """Get all maps with optional filtering."""
        if scenario:
            return await self.repo.get_by_scenario(scenario, skip, limit)
        return await self.repo.get_all(skip, limit)
    
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Map]:
        """Search maps by name."""
        return await self.repo.search_by_name(query, skip, limit)
    
    async def update(self, map_id: int, **kwargs) -> Optional[Map]:
        """Update a map."""
        return await self.repo.update(map_id, **kwargs)
    
    async def delete(self, map_id: int) -> bool:
        """Delete a map and all associated data."""
        return await self.repo.delete(map_id)
    
    async def get_stats(self, map_id: int) -> Optional[MapStats]:
        """Get aggregated statistics for a map."""
        map_obj = await self.repo.get_by_id(map_id)
        if not map_obj:
            return None
        
        total_runs = await self.run_repo.count_by_map(map_id)
        avg_hardness = await self.metric_repo.get_avg_hardness_by_map(map_id)
        avg_kills = await self.metric_repo.get_avg_kills_by_map(map_id)
        total_bugs = await self.bug_repo.count_by_map(map_id)
        
        # TODO: Calculate solvability rate
        solvability_rate = None
        
        return MapStats(
            map_id=map_id,
            total_runs=total_runs,
            avg_hardness=avg_hardness,
            solvability_rate=solvability_rate,
            total_bugs=total_bugs,
            avg_kills=avg_kills
        )
    
    async def check_duplicate(self, file_path: str) -> Optional[Map]:
        """Check if a map with the same file already exists."""
        # First check by path
        existing = await self.repo.get_by_file_path(file_path)
        if existing:
            return existing
        
        # Then check by hash
        if Path(file_path).exists():
            file_hash = await self._calculate_file_hash(file_path)
            existing = await self.repo.get_by_file_hash(file_hash)
            if existing:
                return existing
        
        return None
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
