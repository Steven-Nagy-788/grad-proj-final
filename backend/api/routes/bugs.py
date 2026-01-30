"""
API routes for bug management - using async services.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.db import get_db
from backend.services.bug_service import BugService
from backend.models.database import BugType, BugSeverity
from backend.models.schemas import BugCreate, BugResponse


router = APIRouter()


async def get_bug_service(db: AsyncSession = Depends(get_db)) -> BugService:
    """Dependency to get BugService instance."""
    return BugService(db)


@router.get("/", response_model=List[BugResponse])
async def list_bugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    run_id: Optional[int] = None,
    bug_type: Optional[BugType] = None,
    severity: Optional[BugSeverity] = None,
    service: BugService = Depends(get_bug_service)
):
    """List all bugs with optional filtering."""
    if run_id:
        return await service.get_by_run(run_id, skip, limit)
    return await service.get_all(
        skip=skip, 
        limit=limit, 
        bug_type=bug_type, 
        severity=severity
    )


@router.post("/", response_model=BugResponse, status_code=201)
async def create_bug(
    bug_data: BugCreate, 
    service: BugService = Depends(get_bug_service)
):
    """Create a new bug entry."""
    try:
        return await service.create(bug_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/critical", response_model=List[BugResponse])
async def list_critical_bugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: BugService = Depends(get_bug_service)
):
    """Get all critical bugs."""
    return await service.get_critical(skip, limit)


@router.get("/summary")
async def get_bug_summary(
    run_id: Optional[int] = None,
    map_id: Optional[int] = None,
    service: BugService = Depends(get_bug_service)
):
    """Get bug summary statistics."""
    return await service.get_summary(run_id=run_id, map_id=map_id)


@router.get("/{bug_id}", response_model=BugResponse)
async def get_bug(
    bug_id: int, 
    service: BugService = Depends(get_bug_service)
):
    """Get a single bug by ID."""
    db_bug = await service.get_by_id(bug_id)
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return db_bug


@router.delete("/{bug_id}", status_code=204)
async def delete_bug(
    bug_id: int, 
    service: BugService = Depends(get_bug_service)
):
    """Delete a bug."""
    success = await service.delete(bug_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bug not found")
