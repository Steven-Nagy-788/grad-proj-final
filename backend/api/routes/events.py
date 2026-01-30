"""
API routes for events - using async services.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.db import get_db
from backend.services.event_service import EventService
from backend.models.database import EventType
from backend.models.schemas import EventCreate, EventResponse


router = APIRouter()


async def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    """Dependency to get EventService instance."""
    return EventService(db)


@router.get("/", response_model=List[EventResponse])
async def list_events(
    run_id: int = Query(..., description="Run ID to get events for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    event_type: Optional[EventType] = None,
    service: EventService = Depends(get_event_service)
):
    """List events for a run with optional type filtering."""
    if event_type:
        return await service.get_by_run_and_type(run_id, event_type, skip, limit)
    return await service.get_by_run(run_id, skip, limit)


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event_data: EventCreate, 
    service: EventService = Depends(get_event_service)
):
    """Create a new event entry."""
    try:
        return await service.create(event_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk", status_code=201)
async def bulk_create_events(
    run_id: int,
    events: List[dict],
    service: EventService = Depends(get_event_service)
):
    """Bulk insert events for a run."""
    try:
        count = await service.bulk_create(run_id, events)
        return {"inserted": count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/episode/{run_id}/{episode}", response_model=List[EventResponse])
async def get_episode_events(
    run_id: int,
    episode: int,
    service: EventService = Depends(get_event_service)
):
    """Get all events for a specific episode."""
    return await service.get_by_episode(run_id, episode)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int, 
    service: EventService = Depends(get_event_service)
):
    """Get a single event by ID."""
    db_event = await service.get_by_id(event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: int, 
    service: EventService = Depends(get_event_service)
):
    """Delete an event."""
    success = await service.delete(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")


@router.delete("/run/{run_id}", status_code=200)
async def delete_run_events(
    run_id: int,
    service: EventService = Depends(get_event_service)
):
    """Delete all events for a run."""
    count = await service.delete_by_run(run_id)
    return {"deleted": count}


@router.get("/count/{run_id}")
async def count_events(
    run_id: int,
    event_type: Optional[EventType] = None,
    service: EventService = Depends(get_event_service)
):
    """Count events for a run."""
    if event_type:
        count = await service.count_by_type(run_id, event_type)
    else:
        count = await service.count_by_run(run_id)
    return {"run_id": run_id, "count": count, "event_type": event_type}
