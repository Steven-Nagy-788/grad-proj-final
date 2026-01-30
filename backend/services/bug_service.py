"""
Bug service - Business logic for bugs.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Bug, BugType, BugSeverity
from backend.models.schemas import BugCreate
from backend.repositories.bug_repository import BugRepository
from backend.repositories.run_repository import RunRepository


class BugService:
    """Service layer for Bug operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BugRepository(db)
        self.run_repo = RunRepository(db)
    
    async def create(self, data: BugCreate) -> Bug:
        """Create a new bug entry."""
        # Verify run exists
        run = await self.run_repo.get_by_id(data.run_id)
        if not run:
            raise ValueError(f"Run not found: {data.run_id}")
        
        return await self.repo.create(**data.model_dump())
    
    async def get_by_id(self, bug_id: int) -> Optional[Bug]:
        """Get a bug by ID."""
        return await self.repo.get_by_id(bug_id)
    
    async def get_by_run(
        self, 
        run_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get all bugs for a run."""
        return await self.repo.get_by_run_id(run_id, skip, limit)
    
    async def get_by_map(
        self, 
        map_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get all bugs for a map's runs."""
        return await self.repo.get_by_map_id(map_id, skip, limit)
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        bug_type: Optional[BugType] = None,
        severity: Optional[BugSeverity] = None
    ) -> List[Bug]:
        """Get all bugs with optional filtering."""
        if bug_type:
            return await self.repo.get_by_type(bug_type, skip, limit)
        if severity:
            return await self.repo.get_by_severity(severity, skip, limit)
        return await self.repo.get_all(skip, limit)
    
    async def update(self, bug_id: int, **kwargs) -> Optional[Bug]:
        """Update a bug."""
        return await self.repo.update(bug_id, **kwargs)
    
    async def delete(self, bug_id: int) -> bool:
        """Delete a bug."""
        return await self.repo.delete(bug_id)
    
    async def bulk_create(self, run_id: int, bugs: List[Dict[str, Any]]) -> int:
        """Bulk insert bugs for a run."""
        # Verify run exists
        run = await self.run_repo.get_by_id(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        # Add run_id to each bug
        bugs_with_run_id = [{**b, "run_id": run_id} for b in bugs]
        return await self.repo.bulk_create(bugs_with_run_id)
    
    async def get_critical(self, skip: int = 0, limit: int = 100) -> List[Bug]:
        """Get critical bugs."""
        return await self.repo.get_critical_bugs(skip, limit)
    
    async def get_summary(
        self, 
        run_id: Optional[int] = None,
        map_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get bug summary statistics."""
        # Count by type and severity
        by_type = await self.repo.get_summary_by_type(run_id)
        by_severity = await self.repo.get_summary_by_severity(run_id)
        
        # Calculate total
        if run_id:
            total = await self.repo.count_by_run(run_id)
        elif map_id:
            total = await self.repo.count_by_map(map_id)
        else:
            total = await self.repo.count()
        
        return {
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity
        }
    
    async def count_by_run(self, run_id: int) -> int:
        """Count bugs for a run."""
        return await self.repo.count_by_run(run_id)
    
    async def count_by_map(self, map_id: int) -> int:
        """Count bugs for a map."""
        return await self.repo.count_by_map(map_id)
    
    async def detect_stuck_state(
        self, 
        run_id: int, 
        position_events: List[Dict],
        threshold_frames: int = 100
    ) -> List[Dict]:
        """
        Detect stuck states from position events.
        Returns list of detected stuck bugs.
        """
        detected_bugs = []
        
        if len(position_events) < threshold_frames:
            return detected_bugs
        
        # Check for consecutive same positions
        for i in range(len(position_events) - threshold_frames):
            positions = position_events[i:i + threshold_frames]
            
            # Check if all positions are the same
            first_pos = positions[0].get("data", {})
            all_same = all(
                pos.get("data", {}).get("x") == first_pos.get("x") and
                pos.get("data", {}).get("y") == first_pos.get("y")
                for pos in positions
            )
            
            if all_same:
                detected_bugs.append({
                    "bug_type": BugType.STUCK_STATE,
                    "severity": BugSeverity.MAJOR,
                    "title": "Agent Stuck State Detected",
                    "description": f"Agent position unchanged for {threshold_frames} frames",
                    "frame": positions[0].get("frame"),
                    "episode": positions[0].get("episode"),
                    "confidence": 0.95,
                    "detection_source": "telemetry",
                    "data": {"position": first_pos, "frames": threshold_frames}
                })
        
        return detected_bugs
    
    async def detect_instant_death(
        self, 
        run_id: int, 
        health_events: List[Dict],
        threshold_damage: int = 80
    ) -> List[Dict]:
        """
        Detect instant death bugs (damage > threshold in single frame).
        Returns list of detected bugs.
        """
        detected_bugs = []
        
        for event in health_events:
            data = event.get("data", {})
            old_health = data.get("old", 100)
            new_health = data.get("new", 0)
            damage = old_health - new_health
            
            if damage >= threshold_damage and new_health <= 0:
                detected_bugs.append({
                    "bug_type": BugType.INSTANT_DEATH,
                    "severity": BugSeverity.CRITICAL,
                    "title": "Instant Death Detected",
                    "description": f"Agent took {damage} damage in single frame (possibly spawn point issue)",
                    "frame": event.get("frame"),
                    "episode": event.get("episode"),
                    "timestamp": event.get("timestamp"),
                    "confidence": 0.90,
                    "detection_source": "telemetry",
                    "data": {"damage": damage, "old_health": old_health, "new_health": new_health}
                })
        
        return detected_bugs
