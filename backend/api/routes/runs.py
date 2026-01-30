"""
API routes for test/training run management - using async services.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.db import get_db
from backend.services.run_service import RunService
from backend.models.database import RunStatus, RunType
from backend.models.schemas import RunCreate, RunResponse, RunWithMetrics, TaskResponse


router = APIRouter()


async def get_run_service(db: AsyncSession = Depends(get_db)) -> RunService:
    """Dependency to get RunService instance."""
    return RunService(db)


@router.get("/", response_model=List[RunResponse])
async def list_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    map_id: Optional[int] = None,
    status: Optional[RunStatus] = None,
    run_type: Optional[RunType] = None,
    service: RunService = Depends(get_run_service)
):
    """List all runs with optional filtering."""
    return await service.get_all(
        skip=skip, 
        limit=limit, 
        map_id=map_id, 
        status=status, 
        run_type=run_type
    )


@router.post("/", response_model=RunResponse, status_code=201)
async def create_run(
    run_data: RunCreate, 
    service: RunService = Depends(get_run_service)
):
    """Create a new run entry (does not start execution)."""
    try:
        return await service.create(run_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pending", response_model=List[RunResponse])
async def list_pending_runs(
    limit: int = Query(10, ge=1, le=50),
    service: RunService = Depends(get_run_service)
):
    """Get pending runs waiting to be executed."""
    return await service.get_pending(limit)


@router.get("/running", response_model=List[RunResponse])
async def list_running_runs(
    service: RunService = Depends(get_run_service)
):
    """Get currently running runs."""
    return await service.get_running()


@router.get("/{run_id}", response_model=RunWithMetrics)
async def get_run(
    run_id: int, 
    service: RunService = Depends(get_run_service)
):
    """Get a single run with metrics."""
    run = await service.get_with_metrics(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.delete("/{run_id}", status_code=204)
async def delete_run(
    run_id: int, 
    service: RunService = Depends(get_run_service)
):
    """Delete a run and all associated data."""
    success = await service.delete(run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")


@router.post("/{run_id}/start", response_model=TaskResponse)
async def start_run(
    run_id: int,
    service: RunService = Depends(get_run_service)
):
    """
    Start execution of a pending run.
    This enqueues a background task to run the agent.
    """
    try:
        await service.start(run_id)
        # TODO: Add Celery task here to actually run the agent
        return TaskResponse(
            task_id=f"run-{run_id}",
            status="started",
            message=f"Run {run_id} has been started"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{run_id}/cancel", response_model=RunResponse)
async def cancel_run(
    run_id: int, 
    service: RunService = Depends(get_run_service)
):
    """Cancel a running or pending run."""
    try:
        return await service.cancel(run_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{run_id}/complete", response_model=RunResponse)
async def complete_run(
    run_id: int,
    total_episodes: Optional[int] = None,
    total_iterations: Optional[int] = None,
    log_path: Optional[str] = None,
    service: RunService = Depends(get_run_service)
):
    """Mark a run as completed (called by worker)."""
    try:
        return await service.complete(
            run_id, 
            total_episodes=total_episodes,
            total_iterations=total_iterations,
            log_path=log_path
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{run_id}/fail", response_model=RunResponse)
async def fail_run(
    run_id: int,
    error_message: str,
    service: RunService = Depends(get_run_service)
):
    """Mark a run as failed (called by worker)."""
    try:
        return await service.fail(run_id, error_message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
