"""
API routes for map management - using async services.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.db import get_db
from backend.services.map_service import MapService
from backend.models.schemas import MapCreate, MapResponse, MapStats


router = APIRouter()


async def get_map_service(db: AsyncSession = Depends(get_db)) -> MapService:
    """Dependency to get MapService instance."""
    return MapService(db)


@router.get("/", response_model=List[MapResponse])
async def list_maps(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    scenario: Optional[str] = None,
    service: MapService = Depends(get_map_service)
):
    """List all maps with optional filtering."""
    maps = await service.get_all(skip=skip, limit=limit, scenario=scenario)
    return maps


@router.post("/", response_model=MapResponse, status_code=201)
async def create_map(
    map_data: MapCreate, 
    service: MapService = Depends(get_map_service)
):
    """Create a new map entry."""
    try:
        return await service.create(map_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[MapResponse])
async def search_maps(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: MapService = Depends(get_map_service)
):
    """Search maps by name."""
    return await service.search(q, skip, limit)


@router.get("/{map_id}", response_model=MapResponse)
async def get_map(
    map_id: int, 
    service: MapService = Depends(get_map_service)
):
    """Get a single map by ID."""
    db_map = await service.get_by_id(map_id)
    if not db_map:
        raise HTTPException(status_code=404, detail="Map not found")
    return db_map


@router.delete("/{map_id}", status_code=204)
async def delete_map(
    map_id: int, 
    service: MapService = Depends(get_map_service)
):
    """Delete a map and all associated runs."""
    success = await service.delete(map_id)
    if not success:
        raise HTTPException(status_code=404, detail="Map not found")


@router.get("/{map_id}/stats", response_model=MapStats)
async def get_map_stats(
    map_id: int, 
    service: MapService = Depends(get_map_service)
):
    """Get aggregated statistics for a map."""
    stats = await service.get_stats(map_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Map not found")
    return stats
