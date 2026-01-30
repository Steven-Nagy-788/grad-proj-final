"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS (mirror database enums)
# =============================================================================

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunType(str, Enum):
    TRAINING = "training"
    TESTING = "testing"
    EVALUATION = "evaluation"


class EventType(str, Enum):
    HEALTH_CHANGE = "health_change"
    AMMO_CHANGE = "ammo_change"
    KILL = "kill"
    DEATH = "death"
    POSITION = "position"
    EPISODE_START = "episode_start"
    EPISODE_END = "episode_end"
    STUCK = "stuck"
    ITERATION = "iteration"


class BugSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class BugType(str, Enum):
    STUCK_STATE = "stuck_state"
    INSTANT_DEATH = "instant_death"
    UNREACHABLE_AREA = "unreachable_area"
    VISUAL_GLITCH = "visual_glitch"
    CRASH = "crash"
    PERFORMANCE = "performance"


# =============================================================================
# MAP SCHEMAS
# =============================================================================

class MapBase(BaseModel):
    name: str
    scenario: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MapCreate(MapBase):
    file_path: str


class MapResponse(MapBase):
    id: int
    file_path: str
    file_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MapStats(BaseModel):
    """Aggregated statistics for a map across all runs."""
    map_id: int
    total_runs: int
    avg_hardness: Optional[float] = None
    solvability_rate: Optional[float] = None
    total_bugs: int = 0
    avg_kills: Optional[float] = None


# =============================================================================
# RUN SCHEMAS
# =============================================================================

class RunBase(BaseModel):
    run_type: RunType = RunType.TESTING
    scenario: Optional[str] = None
    seed: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class RunCreate(RunBase):
    map_id: int
    agent_model: Optional[str] = None


class RunResponse(RunBase):
    id: int
    map_id: int
    status: RunStatus
    agent_model: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_episodes: Optional[int] = None
    total_iterations: Optional[int] = None
    log_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RunWithMetrics(RunResponse):
    """Run with embedded metrics."""
    metrics: Optional["MetricResponse"] = None
    bug_count: int = 0


# =============================================================================
# EVENT SCHEMAS
# =============================================================================

class EventBase(BaseModel):
    event_type: EventType
    timestamp: datetime
    iteration: Optional[int] = None
    episode: Optional[int] = None
    frame: Optional[int] = None
    data: Optional[Dict[str, Any]] = None


class EventCreate(EventBase):
    run_id: int
    raw_log: Optional[str] = None


class EventResponse(EventBase):
    id: int
    run_id: int
    
    class Config:
        from_attributes = True


# =============================================================================
# METRIC SCHEMAS
# =============================================================================

class MetricBase(BaseModel):
    total_kills: int = 0
    total_deaths: int = 0
    avg_kills_per_episode: Optional[float] = None
    min_kills: Optional[int] = None
    max_kills: Optional[int] = None
    avg_health: Optional[float] = None
    min_health: Optional[int] = None
    total_damage_taken: Optional[int] = None
    avg_episode_duration: Optional[float] = None
    total_duration: Optional[float] = None
    stuck_count: int = 0
    final_loss: Optional[float] = None
    avg_loss: Optional[float] = None
    hardness_score: Optional[float] = None
    solvability: Optional[bool] = None


class MetricCreate(MetricBase):
    run_id: int


class MetricResponse(MetricBase):
    id: int
    run_id: int
    calculated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# BUG SCHEMAS
# =============================================================================

class BugBase(BaseModel):
    bug_type: BugType
    severity: BugSeverity = BugSeverity.MINOR
    title: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    frame: Optional[int] = None
    episode: Optional[int] = None
    confidence: Optional[float] = None
    detection_source: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class BugCreate(BugBase):
    run_id: int


class BugResponse(BugBase):
    id: int
    run_id: int
    screenshot_path: Optional[str] = None
    video_clip_path: Optional[str] = None
    detected_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# COMPARISON & ANALYSIS SCHEMAS
# =============================================================================

class MapComparison(BaseModel):
    """Side-by-side comparison of multiple maps."""
    maps: List[MapStats]


class TimelinePoint(BaseModel):
    """Single point in a timeline visualization."""
    timestamp: datetime
    frame: Optional[int] = None
    health: Optional[int] = None
    kills: Optional[int] = None
    event_type: Optional[EventType] = None
    event_data: Optional[Dict[str, Any]] = None


class RunTimeline(BaseModel):
    """Full timeline for a run."""
    run_id: int
    points: List[TimelinePoint]
    bugs: List[BugResponse] = []


# =============================================================================
# TASK SCHEMAS (for async operations)
# =============================================================================

class TaskResponse(BaseModel):
    """Response for async task creation."""
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    """Status of an async task."""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: Optional[float] = None  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Update forward references
RunWithMetrics.model_rebuild()
