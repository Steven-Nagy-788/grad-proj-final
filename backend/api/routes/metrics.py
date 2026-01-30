"""
API routes for metrics and analysis - using async services.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.db import get_db
from backend.services.metric_service import MetricService
from backend.services.event_service import EventService
from backend.models.schemas import MetricResponse


router = APIRouter()


async def get_metric_service(db: AsyncSession = Depends(get_db)) -> MetricService:
    """Dependency to get MetricService instance."""
    return MetricService(db)


async def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    """Dependency to get EventService instance."""
    return EventService(db)


@router.get("/", response_model=List[MetricResponse])
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    min_hardness: Optional[float] = None,
    max_hardness: Optional[float] = None,
    service: MetricService = Depends(get_metric_service)
):
    """List all metrics with optional filtering."""
    return await service.get_all(
        skip=skip, 
        limit=limit, 
        min_hardness=min_hardness, 
        max_hardness=max_hardness
    )


@router.get("/hardest", response_model=List[MetricResponse])
async def get_hardest_runs(
    limit: int = Query(10, ge=1, le=50),
    service: MetricService = Depends(get_metric_service)
):
    """Get runs with highest hardness scores."""
    return await service.get_hardest_runs(limit)


@router.get("/compare")
async def compare_runs(
    run_ids: str = Query(..., description="Comma-separated run IDs"),
    service: MetricService = Depends(get_metric_service)
):
    """
    Compare metrics across multiple runs.
    Pass run_ids as comma-separated string, e.g., "1,2,3"
    """
    try:
        ids = [int(x.strip()) for x in run_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_ids format")
    
    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 runs can be compared")
    
    return await service.compare_runs(ids)


@router.get("/{run_id}", response_model=MetricResponse)
async def get_metrics(
    run_id: int, 
    service: MetricService = Depends(get_metric_service)
):
    """Get metrics for a specific run."""
    db_metric = await service.get_by_run(run_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metrics not found for this run")
    return db_metric


@router.get("/{run_id}/timeline")
async def get_timeline(
    run_id: int,
    episode: Optional[int] = None,
    event_service: EventService = Depends(get_event_service)
):
    """
    Get timeline data for visualization.
    Returns events ordered by timestamp for charting.
    """
    timeline = await event_service.get_timeline(run_id, episode)
    if not timeline:
        raise HTTPException(status_code=404, detail="No events found for this run")
    return {"run_id": run_id, "points": timeline}


@router.post("/{run_id}/calculate", response_model=MetricResponse)
async def calculate_metrics(
    run_id: int,
    service: MetricService = Depends(get_metric_service)
):
    """Calculate metrics from events and save to database."""
    try:
        return await service.calculate_and_save(run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
