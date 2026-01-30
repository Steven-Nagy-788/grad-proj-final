"""
Event repository - Database operations for events.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.models.database import Event, EventType
from backend.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """Repository for Event entity operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Event, db)
    
    async def get_by_run_id(
        self, 
        run_id: int, 
        skip: int = 0, 
        limit: int = 1000
    ) -> List[Event]:
        """Get all events for a specific run."""
        result = await self.db.execute(
            select(Event)
            .where(Event.run_id == run_id)
            .order_by(Event.timestamp.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_run_and_type(
        self, 
        run_id: int, 
        event_type: EventType,
        skip: int = 0, 
        limit: int = 1000
    ) -> List[Event]:
        """Get events of a specific type for a run."""
        result = await self.db.execute(
            select(Event)
            .where(
                and_(
                    Event.run_id == run_id,
                    Event.event_type == event_type
                )
            )
            .order_by(Event.timestamp.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_episode(
        self, 
        run_id: int, 
        episode: int
    ) -> List[Event]:
        """Get all events for a specific episode."""
        result = await self.db.execute(
            select(Event)
            .where(
                and_(
                    Event.run_id == run_id,
                    Event.episode == episode
                )
            )
            .order_by(Event.timestamp.asc())
        )
        return list(result.scalars().all())
    
    async def get_by_time_range(
        self, 
        run_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Get events within a time range."""
        result = await self.db.execute(
            select(Event)
            .where(
                and_(
                    Event.run_id == run_id,
                    Event.timestamp >= start_time,
                    Event.timestamp <= end_time
                )
            )
            .order_by(Event.timestamp.asc())
        )
        return list(result.scalars().all())
    
    async def bulk_create(self, events: List[dict]) -> int:
        """Bulk insert events. Returns count of inserted events."""
        if not events:
            return 0
        
        event_objects = [Event(**e) for e in events]
        self.db.add_all(event_objects)
        await self.db.commit()
        return len(event_objects)
    
    async def delete_by_run_id(self, run_id: int) -> int:
        """Delete all events for a run. Returns count deleted."""
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(Event).where(Event.run_id == run_id)
        )
        await self.db.commit()
        return result.rowcount
    
    async def count_by_run(self, run_id: int) -> int:
        """Count events for a specific run."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).select_from(Event).where(Event.run_id == run_id)
        )
        return result.scalar_one()
    
    async def count_by_type(self, run_id: int, event_type: EventType) -> int:
        """Count events of a specific type for a run."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count())
            .select_from(Event)
            .where(
                and_(
                    Event.run_id == run_id,
                    Event.event_type == event_type
                )
            )
        )
        return result.scalar_one()
