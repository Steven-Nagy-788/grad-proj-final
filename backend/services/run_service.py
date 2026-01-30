"""
Run service - Business logic for runs.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Run, RunStatus, RunType
from backend.models.schemas import RunCreate, RunWithMetrics
from backend.repositories.run_repository import RunRepository
from backend.repositories.map_repository import MapRepository
from backend.repositories.metric_repository import MetricRepository
from backend.repositories.bug_repository import BugRepository


class RunService:
    """Service layer for Run operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RunRepository(db)
        self.map_repo = MapRepository(db)
        self.metric_repo = MetricRepository(db)
        self.bug_repo = BugRepository(db)
    
    async def create(self, data: RunCreate) -> Run:
        """Create a new run entry."""
        # Verify map exists
        map_obj = await self.map_repo.get_by_id(data.map_id)
        if not map_obj:
            raise ValueError(f"Map not found: {data.map_id}")
        
        return await self.repo.create(
            map_id=data.map_id,
            run_type=data.run_type,
            scenario=data.scenario,
            seed=data.seed,
            agent_model=data.agent_model,
            config=data.config,
            status=RunStatus.PENDING
        )
    
    async def get_by_id(self, run_id: int) -> Optional[Run]:
        """Get a run by ID."""
        return await self.repo.get_by_id(run_id)
    
    async def get_with_metrics(self, run_id: int) -> Optional[RunWithMetrics]:
        """Get a run with its metrics."""
        run = await self.repo.get_with_metrics(run_id)
        if not run:
            return None
        
        bug_count = await self.bug_repo.count_by_run(run_id)
        metric = await self.metric_repo.get_by_run_id(run_id)
        
        return RunWithMetrics(
            id=run.id,
            map_id=run.map_id,
            run_type=run.run_type,
            status=run.status,
            scenario=run.scenario,
            seed=run.seed,
            agent_model=run.agent_model,
            started_at=run.started_at,
            completed_at=run.completed_at,
            total_episodes=run.total_episodes,
            total_iterations=run.total_iterations,
            log_path=run.log_path,
            error_message=run.error_message,
            config=run.config,
            created_at=run.created_at,
            metrics=metric,
            bug_count=bug_count
        )
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        map_id: Optional[int] = None,
        status: Optional[RunStatus] = None,
        run_type: Optional[RunType] = None
    ) -> List[Run]:
        """Get all runs with optional filtering."""
        if map_id:
            return await self.repo.get_by_map_id(map_id, skip, limit)
        if status:
            return await self.repo.get_by_status(status, skip, limit)
        if run_type:
            return await self.repo.get_by_type(run_type, skip, limit)
        return await self.repo.get_all(skip, limit, order_by=Run.created_at.desc())
    
    async def update(self, run_id: int, **kwargs) -> Optional[Run]:
        """Update a run."""
        return await self.repo.update(run_id, **kwargs)
    
    async def delete(self, run_id: int) -> bool:
        """Delete a run and all associated data."""
        return await self.repo.delete(run_id)
    
    async def start(self, run_id: int) -> Run:
        """Start a pending run."""
        run = await self.repo.get_by_id(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        if run.status != RunStatus.PENDING:
            raise ValueError(f"Run is not pending: {run.status}")
        
        return await self.repo.update_status(run_id, RunStatus.RUNNING)
    
    async def complete(
        self, 
        run_id: int,
        total_episodes: Optional[int] = None,
        total_iterations: Optional[int] = None,
        log_path: Optional[str] = None
    ) -> Run:
        """Mark a run as completed."""
        update_data = {
            "status": RunStatus.COMPLETED,
            "completed_at": datetime.utcnow()
        }
        if total_episodes:
            update_data["total_episodes"] = total_episodes
        if total_iterations:
            update_data["total_iterations"] = total_iterations
        if log_path:
            update_data["log_path"] = log_path
        
        return await self.repo.update(run_id, **update_data)
    
    async def fail(self, run_id: int, error_message: str) -> Run:
        """Mark a run as failed."""
        return await self.repo.update_status(
            run_id, 
            RunStatus.FAILED, 
            error_message=error_message
        )
    
    async def cancel(self, run_id: int) -> Run:
        """Cancel a running or pending run."""
        run = await self.repo.get_by_id(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        if run.status not in [RunStatus.PENDING, RunStatus.RUNNING]:
            raise ValueError(f"Cannot cancel run with status: {run.status}")
        
        return await self.repo.update_status(run_id, RunStatus.CANCELLED)
    
    async def get_pending(self, limit: int = 10) -> List[Run]:
        """Get pending runs waiting to be executed."""
        return await self.repo.get_pending_runs(limit)
    
    async def get_running(self) -> List[Run]:
        """Get currently running runs."""
        return await self.repo.get_running_runs()
