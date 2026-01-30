# Backend - RL Game Tester API

Backend service for the Deep RL Game Quality Assurance Framework.

---

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | ≥0.109.0 |
| ORM | SQLAlchemy 2.0 (async) | ≥2.0.25 |
| Database | PostgreSQL | - |
| DB Driver | asyncpg | ≥0.29.0 |
| Validation | Pydantic v2 | ≥2.5.0 |
| Task Queue | Celery | ≥5.3.6 |
| Cache/Broker | Redis | ≥5.0.1 |
| API Docs | Scalar | CDN |

---

## Implementation Status

### ✅ Completed

| Component | Status | Description |
|-----------|--------|-------------|
| Database Models | ✅ | 5 tables: maps, runs, events, metrics, bugs |
| Pydantic Schemas | ✅ | Request/response validation for all entities |
| Repository Layer | ✅ | Async CRUD + specialized queries per entity |
| Service Layer | ✅ | Business logic for all entities |
| API Routes | ✅ | REST endpoints for all entities |
| Log Parser | ✅ | Parse Arnold training logs |
| Scalar Docs | ✅ | Modern API documentation at `/docs` |
| Async Support | ✅ | All database operations are async |

### ❌ Not Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| Celery Workers | ❌ | Background task processing for agent runs |
| Agent Runner | ❌ | Integration with Arnold DQN agent |
| WebSocket | ❌ | Real-time progress updates |
| File Upload | ❌ | Upload .wad map files |
| Supabase Storage | ❌ | S3-compatible file storage |
| CV Service | ❌ | Computer vision bug detection |
| LLM Service | ❌ | GPT/Claude integration for reports |
| Alembic Migrations | ❌ | Database versioning |

---

## How to Run

### Prerequisites

```bash
# PostgreSQL running (Docker recommended)
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=rl_game_tester -p 5432:5432 -d postgres:15

# Redis running (for future Celery support)
docker run --name redis -p 6379:6379 -d redis:7
```

### Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials
```

### Run Development Server

```bash
# From project root
python -m backend.main

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Access

- **API**: http://localhost:8000
- **Docs (Scalar)**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

---

## Directory Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management (Pydantic Settings)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── __init__.py
│
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py     # Route exports
│       ├── maps.py         # Map CRUD endpoints
│       ├── runs.py         # Run management endpoints
│       ├── events.py       # Event endpoints
│       ├── bugs.py         # Bug endpoints
│       └── metrics.py      # Metrics/analysis endpoints
│
├── models/
│   ├── __init__.py         # Model exports
│   ├── database.py         # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic validation schemas
│
├── repositories/
│   ├── __init__.py         # Repository exports
│   ├── base.py             # Generic async CRUD repository
│   ├── map_repository.py   # Map database operations
│   ├── run_repository.py   # Run database operations
│   ├── event_repository.py # Event database operations
│   ├── metric_repository.py# Metric database operations
│   └── bug_repository.py   # Bug database operations
│
├── services/
│   ├── __init__.py         # Service exports
│   ├── map_service.py      # Map business logic
│   ├── run_service.py      # Run lifecycle management
│   ├── event_service.py    # Event processing & timeline
│   ├── metric_service.py   # Metrics calculation
│   ├── bug_service.py      # Bug detection & management
│   └── log_parser.py       # Arnold log file parser
│
├── utils/
│   ├── __init__.py
│   └── db.py               # Async database connection
│
└── workers/
    └── __init__.py         # (Celery workers - not implemented)
```

---

## File Documentation

### Core Files

#### `main.py`
FastAPI application entry point.

- Creates FastAPI app with CORS middleware
- Registers all API routers
- Serves Scalar API documentation at `/docs`
- Handles application lifespan (startup/shutdown)

```python
# Run the server
python -m backend.main
```

#### `config.py`
Configuration management using Pydantic Settings.

- Loads settings from environment variables
- Reads from `.env` file automatically
- Provides `get_settings()` function for dependency injection

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `API_HOST` | `0.0.0.0` | API bind host |
| `API_PORT` | `8000` | API bind port |
| `DEBUG` | `true` | Enable debug mode |
| `ARNOLD_PATH` | `../mydoom-master-Arnold/Arnold` | Path to Arnold agent |

#### `requirements.txt`
Python dependencies for the backend.

Key packages:
- `fastapi` - Web framework
- `sqlalchemy[asyncio]` - ORM with async support
- `asyncpg` - Async PostgreSQL driver
- `pydantic-settings` - Configuration management
- `celery` - Task queue (for workers)
- `redis` - Cache and message broker

---

### Models (`models/`)

#### `database.py`
SQLAlchemy ORM models defining the database schema.

**Tables:**

| Table | Description | Key Fields |
|-------|-------------|-----------|
| `maps` | Game level metadata | `name`, `file_path`, `file_hash`, `scenario` |
| `runs` | Test/training execution records | `map_id`, `run_type`, `status`, `started_at` |
| `events` | Frame-by-frame gameplay telemetry | `run_id`, `event_type`, `timestamp`, `data` |
| `metrics` | Aggregated statistics | `run_id`, `hardness_score`, `total_kills` |
| `bugs` | Detected bugs and anomalies | `run_id`, `bug_type`, `severity`, `title` |

**Enums:**
- `RunStatus`: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
- `RunType`: TRAINING, TESTING, EVALUATION
- `EventType`: HEALTH_CHANGE, AMMO_CHANGE, KILL, DEATH, etc.
- `BugSeverity`: CRITICAL, MAJOR, MINOR, INFO
- `BugType`: STUCK_STATE, INSTANT_DEATH, VISUAL_GLITCH, etc.

#### `schemas.py`
Pydantic models for API request/response validation.

**Schema Groups:**
- `MapCreate`, `MapResponse`, `MapStats`
- `RunCreate`, `RunResponse`, `RunWithMetrics`
- `EventCreate`, `EventResponse`
- `MetricCreate`, `MetricResponse`
- `BugCreate`, `BugResponse`
- `TaskResponse`, `TaskStatus` (for async operations)

---

### Repositories (`repositories/`)

Repository pattern for database access. All methods are **async**.

#### `base.py`
Generic base repository with common CRUD operations.

```python
class BaseRepository(Generic[ModelType]):
    async def create(**kwargs) -> ModelType
    async def get_by_id(id: int) -> Optional[ModelType]
    async def get_all(skip, limit) -> List[ModelType]
    async def update(id, **kwargs) -> Optional[ModelType]
    async def delete(id) -> bool
    async def count() -> int
    async def exists(id) -> bool
```

#### `map_repository.py`
Map-specific database operations.

```python
class MapRepository(BaseRepository[Map]):
    async def get_by_name(name: str)
    async def get_by_file_path(file_path: str)
    async def get_by_file_hash(file_hash: str)  # Deduplication
    async def get_by_scenario(scenario: str)
    async def search_by_name(query: str)
```

#### `run_repository.py`
Run-specific database operations.

```python
class RunRepository(BaseRepository[Run]):
    async def get_by_map_id(map_id: int)
    async def get_by_status(status: RunStatus)
    async def get_by_type(run_type: RunType)
    async def get_with_metrics(run_id: int)  # Eager load
    async def get_pending_runs(limit: int)
    async def get_running_runs()
    async def update_status(run_id, status, error_message)
```

#### `event_repository.py`
Event-specific database operations.

```python
class EventRepository(BaseRepository[Event]):
    async def get_by_run_id(run_id: int)
    async def get_by_run_and_type(run_id, event_type)
    async def get_by_episode(run_id, episode)
    async def get_by_time_range(run_id, start_time, end_time)
    async def bulk_create(events: List[dict])  # Batch insert
    async def delete_by_run_id(run_id: int)
```

#### `metric_repository.py`
Metric-specific database operations.

```python
class MetricRepository(BaseRepository[Metric]):
    async def get_by_run_id(run_id: int)
    async def get_by_map_id(map_id: int)
    async def get_by_hardness_range(min, max)
    async def get_avg_hardness_by_map(map_id: int)
    async def get_hardest_runs(limit: int)
    async def upsert(run_id, **kwargs)  # Create or update
```

#### `bug_repository.py`
Bug-specific database operations.

```python
class BugRepository(BaseRepository[Bug]):
    async def get_by_run_id(run_id: int)
    async def get_by_map_id(map_id: int)
    async def get_by_type(bug_type: BugType)
    async def get_by_severity(severity: BugSeverity)
    async def get_critical_bugs()
    async def get_summary_by_type(run_id)  # Grouped counts
    async def bulk_create(bugs: List[dict])
```

---

### Services (`services/`)

Business logic layer. All methods are **async**.

#### `map_service.py`
Map management business logic.

```python
class MapService:
    async def create(data: MapCreate)       # With hash calculation
    async def get_by_id(map_id: int)
    async def get_all(skip, limit, scenario)
    async def search(query: str)
    async def update(map_id, **kwargs)
    async def delete(map_id: int)
    async def get_stats(map_id: int)        # Aggregated stats
    async def check_duplicate(file_path)    # By path or hash
```

#### `run_service.py`
Run lifecycle management.

```python
class RunService:
    async def create(data: RunCreate)
    async def get_by_id(run_id: int)
    async def get_with_metrics(run_id: int)
    async def get_all(skip, limit, map_id, status, run_type)
    async def start(run_id: int)            # PENDING -> RUNNING
    async def complete(run_id, episodes, iterations, log_path)
    async def fail(run_id, error_message)   # Mark as failed
    async def cancel(run_id: int)           # Mark as cancelled
    async def get_pending(limit: int)
    async def get_running()
```

#### `event_service.py`
Event processing and timeline generation.

```python
class EventService:
    async def create(data: EventCreate)
    async def get_by_id(event_id: int)
    async def get_by_run(run_id, skip, limit)
    async def get_by_run_and_type(run_id, event_type)
    async def get_by_episode(run_id, episode)
    async def bulk_create(run_id, events)   # Batch insert
    async def delete_by_run(run_id: int)
    async def get_timeline(run_id, episode) # For visualization
```

#### `metric_service.py`
Metrics calculation from events.

```python
class MetricService:
    async def create(data: MetricCreate)
    async def get_by_run(run_id: int)
    async def get_by_map(map_id: int)
    async def calculate_from_events(run_id) # Returns dict
    async def calculate_and_save(run_id)    # Calculate + persist
    async def get_hardest_runs(limit: int)
    async def compare_runs(run_ids: List[int])
```

**Hardness Score Calculation:**
```
hardness = death_factor + kill_factor + health_factor
         = (deaths/episodes * 35) + ((1 - avg_kills/10) * 25) + ((1 - avg_health/100) * 20)
```

#### `bug_service.py`
Bug detection and management.

```python
class BugService:
    async def create(data: BugCreate)
    async def get_by_run(run_id, skip, limit)
    async def get_by_map(map_id: int)
    async def get_critical(skip, limit)
    async def get_summary(run_id, map_id)   # Grouped counts
    async def bulk_create(run_id, bugs)
    
    # Detection algorithms
    async def detect_stuck_state(run_id, position_events, threshold_frames)
    async def detect_instant_death(run_id, health_events, threshold_damage)
```

#### `log_parser.py`
Arnold training log parser.

```python
class LogParser:
    def parse_file(log_path: str) -> ParsedRun
    def stream_parse(log_path: str) -> Generator[ParsedEvent]

def calculate_metrics(run: ParsedRun) -> Dict[str, Any]
```

**Parsed Event Types:**
- `RUN_START`, `CONFIG`, `ITERATION`
- `HEALTH_CHANGE`, `AMMO_CHANGE`, `KILL`, `DEATH`
- `EPISODE_START`, `EPISODE_END`
- `EVALUATION_START`, `EVALUATION_END`
- `MODEL_SAVE`

---

### API Routes (`api/routes/`)

All routes are **async** and use dependency injection for services.

#### `maps.py`
Map management endpoints.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/maps` | List maps (filter by scenario) |
| POST | `/api/maps` | Create map |
| GET | `/api/maps/search` | Search by name |
| GET | `/api/maps/{id}` | Get single map |
| DELETE | `/api/maps/{id}` | Delete map |
| GET | `/api/maps/{id}/stats` | Get aggregated stats |

#### `runs.py`
Run management endpoints.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/runs` | List runs (filter by map, status, type) |
| POST | `/api/runs` | Create run |
| GET | `/api/runs/pending` | List pending runs |
| GET | `/api/runs/running` | List running runs |
| GET | `/api/runs/{id}` | Get run with metrics |
| DELETE | `/api/runs/{id}` | Delete run |
| POST | `/api/runs/{id}/start` | Start execution |
| POST | `/api/runs/{id}/cancel` | Cancel run |
| POST | `/api/runs/{id}/complete` | Mark completed |
| POST | `/api/runs/{id}/fail` | Mark failed |

#### `events.py`
Event endpoints.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events?run_id=X` | List events for run |
| POST | `/api/events` | Create event |
| POST | `/api/events/bulk` | Bulk insert events |
| GET | `/api/events/episode/{run_id}/{episode}` | Events by episode |
| GET | `/api/events/{id}` | Get single event |
| DELETE | `/api/events/{id}` | Delete event |
| DELETE | `/api/events/run/{run_id}` | Delete all run events |
| GET | `/api/events/count/{run_id}` | Count events |

#### `bugs.py`
Bug endpoints.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bugs` | List bugs (filter by run, type, severity) |
| POST | `/api/bugs` | Create bug |
| GET | `/api/bugs/critical` | List critical bugs |
| GET | `/api/bugs/summary` | Bug counts by type/severity |
| GET | `/api/bugs/{id}` | Get single bug |
| DELETE | `/api/bugs/{id}` | Delete bug |

#### `metrics.py`
Metrics and analysis endpoints.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/metrics` | List metrics (filter by hardness) |
| GET | `/api/metrics/hardest` | Highest hardness scores |
| GET | `/api/metrics/compare?run_ids=1,2,3` | Compare runs |
| GET | `/api/metrics/{run_id}` | Get run metrics |
| GET | `/api/metrics/{run_id}/timeline` | Timeline for charts |
| POST | `/api/metrics/{run_id}/calculate` | Calculate from events |

---

### Utils (`utils/`)

#### `db.py`
Async database connection using SQLAlchemy 2.0.

```python
# Dependency for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]

# Context manager for services/workers
async with get_db_session() as db:
    ...

# Table management
await create_tables()
await drop_tables()
```

---

### Workers (`workers/`)

**Not implemented yet.** Will contain Celery workers for:

- `training_worker.py` - Run agent training
- `testing_worker.py` - Run agent testing
- `analysis_worker.py` - Post-run analysis

---

## API Usage Examples

### Create a Map
```bash
curl -X POST http://localhost:8000/api/maps \
  -H "Content-Type: application/json" \
  -d '{"name": "E1M1", "file_path": "/path/to/maps/e1m1.wad", "scenario": "defend_the_center"}'
```

### Create and Start a Run
```bash
# Create run
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{"map_id": 1, "run_type": "testing"}'

# Start run
curl -X POST http://localhost:8000/api/runs/1/start
```

### Get Run Timeline
```bash
curl http://localhost:8000/api/metrics/1/timeline
```

### Calculate Metrics from Events
```bash
curl -X POST http://localhost:8000/api/metrics/1/calculate
```

---

## Next Steps

1. **Celery Workers** - Background processing for agent runs
2. **Agent Runner** - Integration with Arnold DQN
3. **WebSocket** - Real-time progress streaming
4. **File Upload** - Upload map files via API
5. **CV Service** - Visual bug detection
6. **LLM Service** - Natural language bug reports
