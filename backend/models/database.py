"""
SQLAlchemy database models for the RL Game Tester.

Tables:
- maps: Game level metadata
- runs: Test/training execution records
- events: Frame-by-frame gameplay telemetry
- metrics: Aggregated statistics and scores
- bugs: Detected bugs and anomalies
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, DeclarativeBase
from enum import Enum


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class RunStatus(str, Enum):
    """Status of a test/training run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunType(str, Enum):
    """Type of run."""
    TRAINING = "training"
    TESTING = "testing"
    EVALUATION = "evaluation"


class EventType(str, Enum):
    """Types of gameplay events."""
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
    """Bug severity levels."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class BugType(str, Enum):
    """Types of detected bugs."""
    STUCK_STATE = "stuck_state"
    INSTANT_DEATH = "instant_death"
    UNREACHABLE_AREA = "unreachable_area"
    VISUAL_GLITCH = "visual_glitch"
    CRASH = "crash"
    PERFORMANCE = "performance"


# =============================================================================
# MODELS
# =============================================================================

class Map(Base):
    """Game level/map metadata."""
    __tablename__ = "maps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA256 for deduplication
    scenario = Column(String(100), nullable=True)  # e.g., "defend_the_center"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional metadata from map analysis
    metadata = Column(JSON, nullable=True)  # Flexible storage for map-specific data
    
    # Relationships
    runs = relationship("Run", back_populates="map", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Map(id={self.id}, name='{self.name}')>"


class Run(Base):
    """Test or training run execution record."""
    __tablename__ = "runs"
    
    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False, index=True)
    
    # Run configuration
    run_type = Column(SQLEnum(RunType), nullable=False, default=RunType.TESTING)
    status = Column(SQLEnum(RunStatus), nullable=False, default=RunStatus.PENDING)
    
    # Agent configuration
    agent_model = Column(String(255), nullable=True)  # Path to .pth file
    scenario = Column(String(100), nullable=True)
    seed = Column(Integer, nullable=True)  # For reproducibility
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results summary
    total_episodes = Column(Integer, nullable=True)
    total_iterations = Column(Integer, nullable=True)
    
    # Log file reference
    log_path = Column(String(512), nullable=True)
    
    # Configuration snapshot
    config = Column(JSON, nullable=True)
    
    # Error info if failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    map = relationship("Map", back_populates="runs")
    events = relationship("Event", back_populates="run", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="run", uselist=False, cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Run(id={self.id}, map_id={self.map_id}, status='{self.status}')>"


class Event(Base):
    """Frame-by-frame gameplay telemetry event."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    
    # Event identification
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    
    # Game state at event time
    iteration = Column(Integer, nullable=True)
    episode = Column(Integer, nullable=True)
    frame = Column(Integer, nullable=True)
    
    # Event-specific data (flexible JSON storage)
    # Examples:
    # - health_change: {"old": 100, "new": 80}
    # - kill: {"enemy_type": "zombie"}
    # - position: {"x": 123.5, "y": 456.7, "z": 0}
    data = Column(JSON, nullable=True)
    
    # Raw log line for debugging
    raw_log = Column(Text, nullable=True)
    
    # Relationship
    run = relationship("Run", back_populates="events")
    
    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', run_id={self.run_id})>"


class Metric(Base):
    """Aggregated metrics for a run."""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, unique=True, index=True)
    
    # Core metrics
    total_kills = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)
    avg_kills_per_episode = Column(Float, nullable=True)
    min_kills = Column(Integer, nullable=True)
    max_kills = Column(Integer, nullable=True)
    
    # Health metrics
    avg_health = Column(Float, nullable=True)
    min_health = Column(Integer, nullable=True)
    total_damage_taken = Column(Integer, nullable=True)
    
    # Time metrics
    avg_episode_duration = Column(Float, nullable=True)  # in seconds
    total_duration = Column(Float, nullable=True)
    
    # Navigation metrics
    stuck_count = Column(Integer, default=0)
    
    # Training metrics (if applicable)
    final_loss = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    
    # Computed scores
    hardness_score = Column(Float, nullable=True)  # 0-100 scale
    solvability = Column(Boolean, nullable=True)  # Can the level be completed?
    
    # Calculated at
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    run = relationship("Run", back_populates="metrics")
    
    def __repr__(self):
        return f"<Metric(run_id={self.run_id}, hardness={self.hardness_score})>"


class Bug(Base):
    """Detected bug or anomaly."""
    __tablename__ = "bugs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    
    # Bug classification
    bug_type = Column(SQLEnum(BugType), nullable=False)
    severity = Column(SQLEnum(BugSeverity), nullable=False, default=BugSeverity.MINOR)
    
    # Location in run
    timestamp = Column(DateTime, nullable=True)
    frame = Column(Integer, nullable=True)
    episode = Column(Integer, nullable=True)
    
    # Detection details
    confidence = Column(Float, nullable=True)  # 0-1 for CV/ML detections
    detection_source = Column(String(50), nullable=True)  # "telemetry", "cv", "llm"
    
    # Description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # LLM-generated or template
    
    # Evidence
    screenshot_path = Column(String(512), nullable=True)
    video_clip_path = Column(String(512), nullable=True)
    
    # Additional data
    data = Column(JSON, nullable=True)  # Flexible storage for bug-specific info
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    run = relationship("Run", back_populates="bugs")
    
    def __repr__(self):
        return f"<Bug(id={self.id}, type='{self.bug_type}', severity='{self.severity}')>"
