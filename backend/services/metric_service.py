"""
Metric service - Business logic for metrics.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Metric
from backend.models.schemas import MetricCreate
from backend.repositories.metric_repository import MetricRepository
from backend.repositories.run_repository import RunRepository
from backend.repositories.event_repository import EventRepository
from backend.models.database import EventType


class MetricService:
    """Service layer for Metric operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MetricRepository(db)
        self.run_repo = RunRepository(db)
        self.event_repo = EventRepository(db)
    
    async def create(self, data: MetricCreate) -> Metric:
        """Create a new metric entry."""
        # Verify run exists
        run = await self.run_repo.get_by_id(data.run_id)
        if not run:
            raise ValueError(f"Run not found: {data.run_id}")
        
        return await self.repo.create(**data.model_dump())
    
    async def get_by_id(self, metric_id: int) -> Optional[Metric]:
        """Get a metric by ID."""
        return await self.repo.get_by_id(metric_id)
    
    async def get_by_run(self, run_id: int) -> Optional[Metric]:
        """Get metrics for a run."""
        return await self.repo.get_by_run_id(run_id)
    
    async def get_by_map(
        self, 
        map_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Metric]:
        """Get all metrics for a map's runs."""
        return await self.repo.get_by_map_id(map_id, skip, limit)
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        min_hardness: Optional[float] = None,
        max_hardness: Optional[float] = None
    ) -> List[Metric]:
        """Get all metrics with optional filtering."""
        if min_hardness is not None or max_hardness is not None:
            return await self.repo.get_by_hardness_range(
                min_hardness or 0, 
                max_hardness or 100, 
                skip, 
                limit
            )
        return await self.repo.get_all(skip, limit)
    
    async def update(self, metric_id: int, **kwargs) -> Optional[Metric]:
        """Update a metric."""
        return await self.repo.update(metric_id, **kwargs)
    
    async def upsert(self, run_id: int, **kwargs) -> Metric:
        """Create or update metrics for a run."""
        return await self.repo.upsert(run_id, **kwargs)
    
    async def delete(self, metric_id: int) -> bool:
        """Delete a metric."""
        return await self.repo.delete(metric_id)
    
    async def calculate_from_events(self, run_id: int) -> Dict[str, Any]:
        """Calculate metrics from a run's events."""
        # Get all events for the run
        events = await self.event_repo.get_by_run_id(run_id)
        
        total_kills = 0
        total_deaths = 0
        health_values = []
        damage_taken = 0
        kills_by_episode: Dict[int, int] = {}
        current_episode_kills = 0
        current_episode = 0
        
        for event in events:
            if event.event_type == EventType.KILL:
                total_kills += 1
                current_episode_kills += 1
                
            elif event.event_type == EventType.DEATH:
                total_deaths += 1
                
            elif event.event_type == EventType.HEALTH_CHANGE and event.data:
                old_health = event.data.get("old", 100)
                new_health = event.data.get("new", 0)
                health_values.append(new_health)
                if new_health < old_health:
                    damage_taken += (old_health - new_health)
                    
            elif event.event_type == EventType.EPISODE_START:
                if current_episode > 0:
                    kills_by_episode[current_episode] = current_episode_kills
                current_episode += 1
                current_episode_kills = 0
                
            elif event.event_type == EventType.EPISODE_END:
                episode = event.data.get("episode", current_episode) if event.data else current_episode
                kills_by_episode[episode] = event.data.get("kills", current_episode_kills) if event.data else current_episode_kills
                current_episode_kills = 0
        
        # Calculate aggregates
        kills_list = list(kills_by_episode.values()) if kills_by_episode else [total_kills]
        avg_kills = sum(kills_list) / len(kills_list) if kills_list else 0
        
        avg_health = sum(health_values) / len(health_values) if health_values else 100
        min_health = min(health_values) if health_values else 0
        
        # Hardness score calculation (0-100)
        total_episodes = max(current_episode, 1)
        death_factor = min(total_deaths / total_episodes, 1.0) * 35
        kill_factor = max(0, (1 - avg_kills / 10)) * 25 if avg_kills < 10 else 0
        health_factor = max(0, (1 - avg_health / 100)) * 20
        
        hardness_score = death_factor + kill_factor + health_factor
        hardness_score = min(100, max(0, hardness_score))
        
        return {
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "avg_kills_per_episode": round(avg_kills, 2),
            "min_kills": min(kills_list) if kills_list else 0,
            "max_kills": max(kills_list) if kills_list else 0,
            "avg_health": round(avg_health, 2),
            "min_health": min_health,
            "total_damage_taken": damage_taken,
            "hardness_score": round(hardness_score, 2),
            "solvability": total_deaths < total_episodes,
        }
    
    async def calculate_and_save(self, run_id: int) -> Metric:
        """Calculate metrics from events and save to database."""
        metrics_data = await self.calculate_from_events(run_id)
        return await self.upsert(run_id, **metrics_data)
    
    async def get_hardest_runs(self, limit: int = 10) -> List[Metric]:
        """Get runs with highest hardness scores."""
        return await self.repo.get_hardest_runs(limit)
    
    async def compare_runs(self, run_ids: List[int]) -> List[Metric]:
        """Get metrics for multiple runs for comparison."""
        metrics = []
        for run_id in run_ids:
            metric = await self.repo.get_by_run_id(run_id)
            if metric:
                metrics.append(metric)
        return metrics
    
    async def get_avg_hardness_by_map(self, map_id: int) -> Optional[float]:
        """Get average hardness score for a map."""
        return await self.repo.get_avg_hardness_by_map(map_id)
