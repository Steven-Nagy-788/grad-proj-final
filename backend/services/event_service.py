"""
Event service - Business logic for events.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Event, EventType
from backend.models.schemas import EventCreate
from backend.repositories.event_repository import EventRepository
from backend.repositories.run_repository import RunRepository


class EventService:
    """Service layer for Event operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EventRepository(db)
        self.run_repo = RunRepository(db)
    
    async def create(self, data: EventCreate) -> Event:
        """Create a new event entry."""
        # Verify run exists
        run = await self.run_repo.get_by_id(data.run_id)
        if not run:
            raise ValueError(f"Run not found: {data.run_id}")
        
        return await self.repo.create(
            run_id=data.run_id,
            event_type=data.event_type,
            timestamp=data.timestamp,
            iteration=data.iteration,
            episode=data.episode,
            frame=data.frame,
            data=data.data,
            raw_log=data.raw_log
        )
    
    async def get_by_id(self, event_id: int) -> Optional[Event]:
        """Get an event by ID."""
        return await self.repo.get_by_id(event_id)
    
    async def get_by_run(
        self, 
        run_id: int, 
        skip: int = 0, 
        limit: int = 1000
    ) -> List[Event]:
        """Get all events for a run."""
        return await self.repo.get_by_run_id(run_id, skip, limit)
    
    async def get_by_run_and_type(
        self, 
        run_id: int, 
        event_type: EventType,
        skip: int = 0, 
        limit: int = 1000
    ) -> List[Event]:
        """Get events of a specific type for a run."""
        return await self.repo.get_by_run_and_type(run_id, event_type, skip, limit)
    
    async def get_by_episode(self, run_id: int, episode: int) -> List[Event]:
        """Get all events for a specific episode."""
        return await self.repo.get_by_episode(run_id, episode)
    
    async def get_by_time_range(
        self, 
        run_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Get events within a time range."""
        return await self.repo.get_by_time_range(run_id, start_time, end_time)
    
    async def bulk_create(self, run_id: int, events: List[Dict[str, Any]]) -> int:
        """Bulk insert events for a run."""
        # Verify run exists
        run = await self.run_repo.get_by_id(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        # Add run_id to each event
        events_with_run_id = [{**e, "run_id": run_id} for e in events]
        return await self.repo.bulk_create(events_with_run_id)
    
    async def delete(self, event_id: int) -> bool:
        """Delete an event."""
        return await self.repo.delete(event_id)
    
    async def delete_by_run(self, run_id: int) -> int:
        """Delete all events for a run."""
        return await self.repo.delete_by_run_id(run_id)
    
    async def count_by_run(self, run_id: int) -> int:
        """Count events for a run."""
        return await self.repo.count_by_run(run_id)
    
    async def count_by_type(self, run_id: int, event_type: EventType) -> int:
        """Count events of a specific type for a run."""
        return await self.repo.count_by_type(run_id, event_type)
    
    async def get_timeline(self, run_id: int, episode: Optional[int] = None) -> List[Dict]:
        """
        Get timeline data for visualization.
        Returns events with running totals for health/kills.
        """
        if episode is not None:
            events = await self.repo.get_by_episode(run_id, episode)
        else:
            events = await self.repo.get_by_run_id(run_id)
        
        timeline = []
        current_health = 100
        current_kills = 0
        
        for event in events:
            # Update running totals based on event type
            if event.event_type == EventType.HEALTH_CHANGE and event.data:
                current_health = event.data.get("new", current_health)
            elif event.event_type == EventType.KILL:
                current_kills += 1
            elif event.event_type == EventType.EPISODE_START:
                current_health = 100
                current_kills = 0
            
            timeline.append({
                "timestamp": event.timestamp,
                "frame": event.frame,
                "health": current_health,
                "kills": current_kills,
                "event_type": event.event_type,
                "event_data": event.data
            })
        
        return timeline
