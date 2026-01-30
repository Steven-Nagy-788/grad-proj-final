# Backend & Database Architecture Plan
## Local Development Environment

---

## Executive Summary

This is a **local web application** with:
- **Frontend:** React.js SPA (Single Page Application) served locally
- **Backend:** FastAPI REST API + WebSocket server for real-time updates
- **Worker Layer:** Celery workers for long-running agent training/testing
- **Database:** PostgreSQL (Docker container - local)
- **File Storage:** Supabase Storage (free 1GB S3-compatible API)
- **Caching:** Redis (task queue + logs storage)
- **Deployment:** Docker Compose (all services run on your machine)

**Why This Architecture Works for Local:**
1. **Training + Testing:** Agent training runs hours → Celery handles background execution with stop/resume
2. **Real-Time Logs:** WebSocket pushes training iterations, DQN loss, kills, health to frontend
3. **Free Storage:** Supabase 1GB free tier for .wad files, training checkpoints, logs
4. **Reliable:** Task queue persists jobs in Redis (can stop/restart training)
5. **Full Control:** Everything runs locally, no cloud costs ($0/month)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER BROWSER                                  │
│  • React.js SPA (Map upload, dashboard, bug reports)                    │
│  • WebSocket client (real-time progress updates)                        │
│  Location: frontend/ (TO CREATE)                                         │
└──────────────────┬─────────────────────────────┬────────────────────────┘
                   │ HTTP/REST                   │ WebSocket
                   ↓                             ↓
┌──────────────────────────────────┐  ┌─────────────────────────────────┐
│       NGINX Reverse Proxy        │  │   WebSocket Server (FastAPI)    │
│  • SSL termination               │  │   • Real-time progress push     │
│  • Static file serving           │  │   • Task status broadcasts      │
│  • Load balancing                │  │   • Connected clients tracking  │
│  Location: docker/nginx.conf     │  │   Location: backend/ws.py       │
│           (TO CREATE)            │  │            (TO CREATE)          │
└──────────────────┬───────────────┘  └──────────────┬──────────────────┘
                   │                                  │
                   ↓                                  ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (API Layer)                           │
│  • REST endpoints (/api/v1/maps, /training, /testing)                    │
│  • Request validation (Pydantic)                                          │
│  • Task dispatch (submit jobs to Celery)                                 │
│  Location: backend/api/ (TO CREATE)                                       │
│    ├── routes/maps.py - Upload/list maps                                │
│    ├── routes/training.py - Start/stop training, get logs ⭐            │
│    ├── routes/testing.py - Start/stop testing, get metrics ⭐           │
│    ├── routes/health.py - System health check                           │
│    ├── schemas/ (Pydantic models)                                        │
│    └── dependencies.py (DB sessions)                                     │
└──────────────────┬──────────────────────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    Service Layer (Business Logic)                         │
│  • MapService, RunService, BugService                                     │
│  • Hardness scoring algorithms                                            │
│  • LLM integration (OpenAI/Anthropic API clients)                        │
│  Location: backend/services/ (TO CREATE)                                  │
│    ├── map_service.py, run_service.py, bug_service.py                   │
│    ├── llm_service.py (GPT-4 integration)                               │
│    └── analysis_service.py (hardness scoring)                            │
└──────────────────┬──────────────────────────────────────────────────────┘
                   │
          ┌────────┴────────┬─────────────────────┬──────────────────┐
          ↓                 ↓              upabase        │  │ Celery Queue │
│  • Logs cache   │  │  • Training  │  │  • Maps (.wad)   │  │  • Tasks     │
│  • Task queue   │  │    logs      │  │  • Checkpoints   │  │  • Training  │
│  Redis image    │  │  • Testing   │  │  • Test logs     │  │  • Testing   │
│  (docker-compose)│ │    metrics   │  │  Free 1GB S3 API │  │  Redis broker│
│  port 6379      │  │  PostgreSQL  │  │  supabase.co     │  │  (same Redis)│
│                 │  │  local Docker│  │  backend/storage/│  │  backend/    │
│  backend/cache/ │  │  port 5432   │  │  supabase.py     │  │  celery_app.py│
│  (TO CREATE)    │  │  backend/db/ │  │  (TO CREATE)     │  │  (TO CREATE)py│
│  backend/cache/ │  │  backend/db/ │  │  backend/storage/│  │  (TO CREATE) │
│  (TO CREATE)    │  │  (TO CREATE) │  │  (TO CREATE)     │  │              │
└─────────────────┘  └──────────────┘  └──────────────────┘  └──────┬───────┘
                                                                     ↓
                     ┌────────────────────────────────────────────────────┐
                     │         Celery Workers (Agent Training/Testing)    │
                     │  TRAINING TASKS:                                   │
                     │  • Load DQN agent from mydoom-master-Arnold/       │
                     │  • Run training loop (Trainer.run())               │
                     │  • Log: iteration, DQN loss, reward                │
                     │  • Save checkpoints every N iterations             │
                     │  • Broadcast progress: {iter, loss} via WebSocket  │
                     │  • Store logs as JSON in PostgreSQL                │
                     │                                                    │
                     │  TESTING TASKS:                                    │
                     │  • Load pre-trained checkpoint                     │
                     │  • Run N episodes (inference only)                 │
                     │  • Track: kills, deaths, health, ammo per episode  │
                     │  • Calculate: min/max/mean kills                   │
                     │  • Broadcast progress: {episode, kills, health}    │
                     │  • Store test metrics as JSON                      │
                     │                                                    │
                     │  Location: backend/workers/                        │
                     │    ├── training_worker.py (TO CREATE) ⭐⭐⭐       │
                     │    └── testing_worker.py (TO CREATE) ⭐⭐⭐        │
                     │  Uses: mydoom-master-Arnold/Arnold/                │
                     │    ├── src/trainer.py (EXISTING - training loop)  │
                     │    ├── src/doom/game.py (EXISTING - VizDoom wrap) │
                     │    ├── src/model/dqn/ (EXISTING - networks)       │
                     │    └── pretrained/*.pth (EXISTING - checkpoints)  │
                     └────────────────────────────────────────────────────┘
```

**Data Flow Example:**
1. User uploads map via frontend → POST `/api/v1/maps` (backend/api/routes/maps.py - TO CREATE)
2. FastAPI saves map file to S3 (backend/storage/s3_client.py - TO CREATE), creates DB entry, returns map_id
3. User clicks "Test Map" → POST `/api/v1/runs` (backend/api/routes/runs.py - TO CREATE)
4. FastAPI creates test_run record (status=pending), dispatches Celery task (backend/celery_app.py - TO CREATE)
5. Celery worker (backend/workers/agent_runner.py - TO CREATE) picks up task, wraps Arnold agent
6. Worker loads DQN model from mydoom-master-Arnold/Arnold/pretrained/*.pth (EXISTING)
7. Worker initializes VizDoom via mydoom-master-Arnold/Arnold/src/doom/game.py (EXISTING - 889 lines)
8. Worker runs 5 episodes, captures 2100 frames/episode via game.py buffers
9. Worker sends progress updates to WebSocket server (backend/ws.py - TO CREATE) every 5 seconds
10. WebSocket broadcasts to connected frontend clients (real-time progress bar)
11. Worker extracts events via mydoom-master-Arnold/Arnold/src/doom/reward.py (EXISTING - reward parsing)
12. Worker runs CV model (backend/services/cv_service.py - TO CREATE) on frames for bug detection
13. Worker calls LLM API (backend/services/llm_service.py - TO CREATE) with events + screenshots
14. Worker stores results: PostgreSQL (backend/db/ - TO CREATE), S3 (videos/screenshots)
15. Worker updates test_run status=completed, broadcasts completion event
16. Frontend fetches results via GET `/api/v1/runs/{run_id}` (backend/api/routes/runs.py), displays dashboard

---

## Updated Project Directory Structure

```
grad-proj-final/
├── arnold/                              # Agent code (existing, read-only)
│   ├── deathmatch.py
│   ├── health_gathering.py
│   └── ... (don't modify Arnold code)
│
├── backend/                             # Backend application
│   ├── __init__.py
│   ├── main.py                          # FastAPI app entry point
│   ├── wsgi.py                          # WSGI server entry (optional)
│   │
│   ├── api/                             # REST API controllers
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── maps.py                  # Map upload, list, delete
│   │   │   ├── runs.py                  # Trigger test, get status
│   │   │   ├── bugs.py                  # Bug reports, filtering
│   │   │   ├── analysis.py              # Compare maps, statistics
│   │   │   └── health.py                # System health check
│   │   ├── websocket.py                 # WebSocket endpoint (/ws)
│   │   └── dependencies.py              # Shared deps (auth, db session)
│   │
│   ├── models/                          # Data models
│   │   ├── __init__.py
│   │   ├── schemas.py                   # Pydantic (API validation)
│   │   └── database.py                  # SQLAlchemy ORM (DB tables)
│   │
│   ├── services/                        # Business logic
│   │   ├── __init__.py
│   │   ├── map_service.py
│   │   ├── run_service.py
│   │   ├── bug_service.py
│   │   ├── metrics_service.py
│   │   ├── llm_service.py               # OpenAI/Anthropic client
│   │   └── storage_service.py           # S3/MinIO file operations
│   │
│   ├── storage/                         # Data access layer
│   │   ├── __init__.py
│   │   ├── database.py                  # DB connection, session mgmt
│   │   ├── cache.py                     # Redis client
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── map_repository.py
│   │   │   ├── run_repository.py
│   │   │   ├── event_repository.py
│   │   │   └── bug_repository.py
│   │   └── migrations/                  # Alembic migrations
│   │       ├── env.py
│   │       └── versions/
│   │           └── 001_initial_schema.py
│   │
│   ├── workers/                         # Celery task definitions
│   │   ├── __init__.py
│   │   ├── celery_app.py                # Celery instance config
│   │   ├── tasks.py                     # Task functions (@celery.task)
│   │   └── agent_runner.py              # Arnold agent execution wrapper
│   │
│   ├── core/                            # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                    # Environment variables
│   │   ├── logging.py                   # Structured logging
│   │   ├── exceptions.py                # Custom exceptions
│   │   └── security.py                  # JWT auth, password hashing
│   │
│   └── tests/                           # Unit/integration tests
│       ├── __init__.py
│       ├── test_api/
│       ├── test_services/
│       ├── test_storage/
│       └── test_workers/
│
├── frontend/                            # React.js application
│   ├── public/
│   ├── src/
│   │   ├── components/                  # Reusable UI components
│   │   ├── pages/                       # Route pages
│   │   ├── services/                    # API client
│   │   ├── hooks/                       # React hooks (useWebSocket)
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── nginx/                               # NGINX configuration
│   ├── nginx.conf                       # Main config
│   └── ssl/                             # SSL certificates (Let's Encrypt)
│
├── deployment/                          # Deployment configs
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── worker.Dockerfile
│   │   └── frontend.Dockerfile
│   ├── docker-compose.yml               # Local development
│   ├── docker-compose.prod.yml          # Production stack
│   └── kubernetes/                      # K8s manifests (optional)
│       ├── backend-deployment.yaml
│       ├── worker-deployment.yaml
│       ├── postgres-statefulset.yaml
│       └── ingress.yaml
│
├── scripts/                             # Utility scripts
│   ├── seed_database.py                 # Sample data
│   ├── migrate_database.sh              # Run Alembic migrations
│   ├── backup_database.sh               # Daily backups
│   └── cleanup_old_files.py             # Delete files >30 days
│
├── configs/
│   ├── database.yml
│   ├── redis.yml
│   └── celery.yml
│
├── requirements.txt                     # Python dependencies
├── requirements-dev.txt                 # Dev dependencies (pytest, black)
├── .env.example                         # Environment template
├── .gitignore
├── docker-compose.yml
├── Makefile                             # Common commands
└── README.md
```

---

## API Endpoints Specification

### Maps API

#### POST /api/v1/maps/upload
Upload custom .wad map file to Supabase storage.

**Request:**
```http
POST /api/v1/maps/upload
Content-Type: multipart/form-data

file: custom_map.wad (binary file)
name: "My Test Map" (optional, defaults to filename)
```

**Response:** (201 Created)
```json
{
  "id": 123,
  "name": "My Test Map",
  "filename": "custom_map.wad",
  "file_url": "https://abc.supabase.co/storage/v1/object/maps/123_custom_map.wad",
  "uploaded_at": "2026-01-30T12:00:00Z",
  "size_bytes": 2048576
}
```

#### GET /api/v1/maps
List all uploaded maps.

**Response:** (200 OK)
```json
{
  "maps": [
    {
      "id": 123,
      "name": "My Test Map",
      "filename": "custom_map.wad",
      "uploaded_at": "2026-01-30T12:00:00Z",
      "size_bytes": 2048576,
      "train_count": 5,
      "test_count": 12
    }
  ],
  "total": 1
}
```

#### DELETE /api/v1/maps/{map_id}
Delete map from database and Supabase storage.

---

### Training API ⭐

#### POST /api/v1/training/start
Start training agent on specified map with fixed parameters.

**Request:**
```http
POST /api/v1/training/start
Content-Type: application/json

{
  "map_id": 123,
  "max_iterations": 100000,
  "action_combinations": "move_fb;move_lr;turn_lr;attack",
  "params": {
    "scenario": "deathmatch",
    "height": 60,
    "width": 108,
    "frame_skip": 4,
    "network_type": "dqn_ff",
    "batch_size": 32,
    "learning_rate": 0.0002,
    "gamma": 0.99
  }
}
```

**Response:** (202 Accepted)
```json
{
  "training_id": "train_abc123",
  "status": "started",
  "map_id": 123,
  "max_iterations": 100000,
  "started_at": "2026-01-30T12:00:00Z",
  "task_id": "celery-task-id-123"
}
```

#### POST /api/v1/training/stop
Stop all running training tasks.

**Request:**
```http
POST /api/v1/training/stop
Content-Type: application/json

{
  "training_id": "train_abc123"  // optional, if empty stops ALL training
}
```

**Response:** (200 OK)
```json
{
  "stopped_count": 1,
  "training_ids": ["train_abc123"],
  "message": "Training stopped successfully"
}
```

#### GET /api/v1/training/{training_id}/status
Get training status and latest metrics.

**Response:** (200 OK)
```json
{
  "training_id": "train_abc123",
  "status": "running",  // pending, running, stopped, completed, failed
  "map_id": 123,
  "map_name": "My Test Map",
  "progress": {
    "current_iteration": 45620,
    "max_iterations": 100000,
    "progress_percent": 45.62,
    "elapsed_seconds": 1825,
    "estimated_remaining_seconds": 2175
  },
  "latest_metrics": {
    "iteration": 45620,
    "dqn_loss": 0.18525,
    "timestamp": "2026-01-30T12:30:25Z"
  },
  "started_at": "2026-01-30T12:00:00Z"
}
```

#### GET /api/v1/training/{training_id}/logs
Get complete training log as JSON.

**Response:** (200 OK)
```json
{
  "training_id": "train_abc123",
  "map_id": 123,
  "max_iterations": 100000,
  "final_iteration": 100000,
  "started_at": "2026-01-30T12:00:00Z",
  "completed_at": "2026-01-30T15:30:00Z",
  "duration_seconds": 12600,
  "iterations": [
    {
      "iteration": 400,
      "dqn_loss": 0.11225,
      "timestamp": "2026-01-30T12:00:04Z"
    },
    {
      "iteration": 800,
      "dqn_loss": 0.16216,
      "timestamp": "2026-01-30T12:00:05Z"
    }
    // ... 250 iterations total (every 400 iterations logged)
  ],
  "max_loss": 0.25066,
  "min_loss": 0.10480,
  "mean_loss": 0.18234,
  "final_loss": 0.14522
}
```

---

### Testing API ⭐

#### POST /api/v1/testing/start
Start testing pre-trained agent on specified map.

**Request:**
```http
POST /api/v1/testing/start
Content-Type: application/json

{
  "map_id": 123,
  "checkpoint": "pretrained/defend_the_center.pth",  // or training checkpoint
  "episodes": 20,
  "action_combinations": "move_fb;move_lr;turn_lr;attack",
  "params": {
    "scenario": "deathmatch",
    "episode_time": 120,  // seconds per episode
    "visualize": false
  }
}
```

**Response:** (202 Accepted)
```json
{
  "test_id": "test_xyz789",
  "status": "started",
  "map_id": 123,
  "checkpoint": "pretrained/defend_the_center.pth",
  "episodes": 20,
  "started_at": "2026-01-30T16:00:00Z",
  "task_id": "celery-task-id-789"
}
```

#### POST /api/v1/testing/stop
Stop all running testing tasks.

**Request:**
```http
POST /api/v1/testing/stop
Content-Type: application/json

{
  "test_id": "test_xyz789"  // optional, if empty stops ALL testing
}
```

**Response:** (200 OK)
```json
{
  "stopped_count": 1,
  "test_ids": ["test_xyz789"],
  "message": "Testing stopped successfully"
}
```

#### GET /api/v1/testing/{test_id}/status
Get testing status and current episode.

**Response:** (200 OK)
```json
{
  "test_id": "test_xyz789",
  "status": "running",  // pending, running, stopped, completed, failed
  "map_id": 123,
  "map_name": "My Test Map",
  "checkpoint": "pretrained/defend_the_center.pth",
  "progress": {
    "current_episode": 12,
    "total_episodes": 20,
    "progress_percent": 60.0,
    "elapsed_seconds": 1440,
    "estimated_remaining_seconds": 960
  },
  "latest_episode": {
    "episode_num": 12,
    "kills": 35,
    "health_remaining": 84,
    "duration_seconds": 28,
    "timestamp": "2026-01-30T16:24:00Z"
  },
  "started_at": "2026-01-30T16:00:00Z"
}
```

#### GET /api/v1/testing/{test_id}/results
Get complete testing results with aggregated metrics.

**Response:** (200 OK)
```json
{
  "test_id": "test_xyz789",
  "map_id": 123,
  "map_name": "My Test Map",
  "checkpoint": "pretrained/defend_the_center.pth",
  "started_at": "2026-01-30T16:00:00Z",
  "completed_at": "2026-01-30T16:40:00Z",
  "duration_seconds": 2400,
  "episodes": [
    {
      "episode_num": 1,
      "kills": 42,
      "deaths": 1,
      "duration_seconds": 7,
      "health_lost": 116,  // 100 → -16 (dead)
      "ammo_used": 56,
      "final_health": -16,
      "events": [
        {"timestamp": 0.0, "type": "kill"},
        {"timestamp": 0.2, "type": "ammo_lost", "amount": 1},
        {"timestamp": 7.0, "type": "death", "health": -16}
      ]
    },
    {
      "episode_num": 2,
      "kills": 40,
      "deaths": 1,
      "duration_seconds": 13,
      "health_lost": 104,
      "ammo_used": 56,
      "final_health": -28
    }
    // ... 20 episodes total
  ],
  "aggregate_metrics": {
    "total_kills": 750,
    "total_deaths": 20,
    "min_kills": 26,
    "max_kills": 42,
    "mean_kills": 37.5,
    "median_kills": 38,
    "std_kills": 4.2,
    "min_health_lost": 96,
    "max_health_lost": 136,
    "mean_health_lost": 110.4,
    "mean_duration_seconds": 18.5,
    "survival_rate": 0.0,  // 0% (died in all episodes)
    "kill_death_ratio": 37.5
  }
}
```

#### GET /api/v1/testing/{test_id}/logs
Get detailed frame-by-frame logs for specific episode.

**Query Parameters:**
- `episode_num` (required): Episode number to get logs for

**Response:** (200 OK)
```json
{
  "test_id": "test_xyz789",
  "episode_num": 1,
  "duration_seconds": 7,
  "frames": 245,  // 7 seconds × 35 fps
  "events": [
    {
      "frame": 8,
      "timestamp": 0.0,
      "type": "kill",
      "health": 100,
      "ammo": 55
    },
    {
      "frame": 12,
      "timestamp": 0.2,
      "type": "ammo_lost",
      "ammo_before": 56,
      "ammo_after": 55
    },
    {
      "frame": 200,
      "timestamp": 6.0,
      "type": "health_lost",
      "health_before": 100,
      "health_after": 88,
      "damage": 12
    },
    {
      "frame": 245,
      "timestamp": 7.0,
      "type": "death",
      "health": -16
    }
  ],
  "health_timeline": [
    {"timestamp": 0.0, "health": 100},
    {"timestamp": 6.0, "health": 88},
    {"timestamp": 6.2, "health": 68},
    {"timestamp": 6.4, "health": 36},
    {"timestamp": 7.0, "health": -16}
  ]
}
```

---

### WebSocket API

#### WS /ws
Real-time updates for training/testing progress.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
```

**Message Types:**

**Training Progress:**
```json
{
  "type": "training_progress",
  "training_id": "train_abc123",
  "iteration": 45620,
  "dqn_loss": 0.18525,
  "timestamp": "2026-01-30T12:30:25Z"
}
```

**Testing Progress:**
```json
{
  "type": "testing_progress",
  "test_id": "test_xyz789",
  "episode": 12,
  "kills": 35,
  "health": 84,
  "timestamp": "2026-01-30T16:24:00Z"
}
```

**Training Completed:**
```json
{
  "type": "training_completed",
  "training_id": "train_abc123",
  "final_iteration": 100000,
  "final_loss": 0.14522,
  "duration_seconds": 12600
}
```

**Testing Completed:**
```json
{
  "type": "testing_completed",
  "test_id": "test_xyz789",
  "episodes_completed": 20,
  "total_kills": 750,
  "mean_kills": 37.5
}
```

---

## Updated Project Directory Structure

This section provides a **comprehensive file-by-file breakdown** of the entire repository structure, indicating which files exist in the Arnold agent directory (with line counts and purposes), and which files need to be created for the backend.

### Arnold Agent Directory (EXISTING - Read-Only)

**Base Path:** `/media/steven/MaD/projects/grad-proj-final/mydoom-master-Arnold/Arnold/`

#### Root Files
```
arnold.py                                    # EXISTING (50 lines)
├── Purpose: Main training script entry point
├── Status: DO NOT MODIFY (standalone training tool)
├── Usage: Not used by backend (we only use inference)
├── Key Imports: vizdoom, src.logger, src.args
├── Key Functions: parse_game_args(), logger setup
└── Note: Backend uses pre-trained models, not training

run.sh                                       # EXISTING (bash script)
├── Purpose: Launch distributed training
├── Status: IGNORE (not needed for testing)
└── Usage: Training only (e.g., python arnold.py --scenario deathmatch)

bots.cfg                                     # EXISTING (config file)
├── Purpose: Define in-game bot behaviors
├── Status: READ-ONLY (may need copy to backend/config/)
├── Usage: VizDoom loads this for deathmatch scenarios
└── Contains: Bot AI difficulty levels, weapon preferences

README.md                                    # EXISTING (documentation)
└── Purpose: Arnold agent documentation, setup instructions
```

#### docs/
```
docs/ARCHITECTURE.md                         # EXISTING
├── Purpose: Deep learning architecture documentation
└── Contains: Network architecture, training methodology

docs/FILES.md                                # EXISTING
└── Purpose: File structure explanation
```

#### pretrained/ ⭐⭐⭐ (CRITICAL - Pre-trained Models)
```
pretrained/deathmatch_shotgun.pth            # EXISTING (~50MB)
├── Purpose: DQN checkpoint for shotgun deathmatch
├── Status: READ-ONLY - Copy reference to backend/config/
├── Usage: Primary model for map testing
└── Load: torch.load('pretrained/deathmatch_shotgun.pth')

pretrained/defend_the_center.pth             # EXISTING
├── Purpose: Defense scenario checkpoint
└── Usage: Alternative model for defense maps

pretrained/health_gathering.pth              # EXISTING
├── Purpose: Survival scenario checkpoint
└── Usage: Health/item collection testing

pretrained/vizdoom_2017_track1.pth           # EXISTING
├── Purpose: Competition checkpoint (Track 1)
└── Usage: Advanced testing scenarios

pretrained/vizdoom_2017_track2.pth           # EXISTING
├── Purpose: Competition checkpoint (Track 2)
└── Usage: Advanced testing scenarios
```

#### resources/ ⭐ (Game Assets)
```
resources/freedoom2.wad                      # EXISTING (~50MB)
├── Purpose: Core DOOM game engine data
├── Status: READ-ONLY - Must reference from backend
├── Usage: VizDoom requires this file path in initialization
├── Contains: Levels, textures, sounds, sprites
└── Note: CRITICAL - VizDoom won't run without this

resources/scenarios/                         # Official test maps
├── deathmatch_shotgun.wad                   # Multiplayer combat map
├── deathmatch_rockets.wad                   # Rocket launcher map
├── defend_the_center.wad                    # Survival defense map
├── full_deathmatch.wad                      # Full weapon deathmatch
├── health_gathering.wad                     # Item collection map
└── health_gathering_supreme.wad             # Advanced survival map
    ├── Purpose: Official VizDoom test scenarios
    ├── Status: READ-ONLY - User maps go to S3
    └── Usage: Baseline performance testing only
```

#### dumped/ (Training Outputs)
```
dumped/test/                                 # EXISTING (training experiments)
├── 4py72ea66e/, 5az3wx4hlb/, ...            # Timestamped run folders
├── Purpose: Training checkpoints, logs, replay data
├── Status: IGNORE (not used by backend)
└── Note: Generated during training, not needed for inference
```

#### src/ ⭐⭐⭐ (Core Agent Code)

**src/ Root Files:**
```
src/__init__.py                              # EXISTING (package marker)

src/args.py                                  # EXISTING (176 lines) ⭐
├── Purpose: CLI argument parsing for game configuration
├── Status: WRAP - Import parse_game_args() in backend
├── Usage: Configure VizDoom parameters (resolution, frame skip, actions)
├── Key Functions:
│   └── parse_game_args(args: List[str]) -> Namespace
│       ├── --scenario: deathmatch, health_gathering, defend_the_center
│       ├── --map_ids_train/test: Map numbers to use
│       ├── --height/width: Screen resolution (default 60x108)
│       ├── --frame_skip: Frames to skip (default 4 = 35fps → 8.75fps)
│       ├── --action_combinations: move_fb+turn_lr+attack
│       ├── --game_features: health, ammo, weapon, etc.
│       └── --network_type: recurrent (LSTM) or feedforward
└── Backend Usage:
    from src.args import parse_game_args
    params = parse_game_args(["--scenario", "deathmatch", "--height", "60"])

src/trainer.py                               # EXISTING (236 lines)
├── Purpose: Training loop with DQN optimization
├── Status: PARTIALLY USE (extract inference logic only)
├── Classes:
│   └── Trainer(params, game, network, eval_fn, parameter_server)
│       ├── .start_game(): Initialize episode with random map
│       ├── .run(): Main training loop (NOT NEEDED for inference)
│       ├── .optimizer: DQN optimizer (NOT NEEDED)
│       └── Inference parts: game.start(), network.forward()
└── Backend Usage: Reference patterns, don't import directly

src/parameter_server.py                      # EXISTING (45 lines)
├── Purpose: Multi-process parameter sharing (distributed training)
├── Status: IGNORE (not needed for single-worker inference)
├── Classes: ParameterServer (manages shared model weights)
└── Usage: Training only (synchronizes weights across GPUs)

src/replay_memory.py                         # EXISTING (108 lines)
├── Purpose: Experience replay buffer for DQN training
├── Status: IGNORE (not needed for inference)
├── Classes: ReplayMemory
│   ├── .add(): Store experience tuple
│   ├── .get_batch(): Sample random batch
│   └── Memory: screens, actions, rewards, isfinal flags
└── Usage: Training only (experience replay algorithm)

src/logger.py                                # EXISTING
├── Purpose: Training log formatter
├── Status: REFERENCE (use patterns for backend/core/logging.py)
└── Usage: Don't import directly, copy logging patterns

src/utils.py                                 # EXISTING
├── Purpose: Helper functions (optimizer, paths, flags)
├── Status: PARTIALLY USE (import specific functions if needed)
├── Functions:
│   ├── get_optimizer(): Returns optimizer function + params
│   ├── bool_flag(): Parse boolean CLI arguments
│   ├── map_ids_flag(): Parse map ID lists
│   └── get_dump_path(): Create experiment directory
└── Backend Usage: Import get_dump_path if needed for temp files
```

**src/doom/ ⭐⭐⭐ (VizDoom Wrapper - CRITICAL):**
```
src/doom/__init__.py                         # EXISTING (package marker)

src/doom/game.py                             # EXISTING (889 lines) ⭐⭐⭐
├── Purpose: VizDoom environment wrapper (THE most critical file)
├── Status: MUST WRAP in backend/workers/agent_runner.py
├── Usage: Core interface to VizDoom game engine
├── Key Classes/Functions:
│   ├── DoomGame (wrapper around vizdoom.DoomGame)
│   │   ├── __init__(params): Initialize with game parameters
│   │   ├── .start(map_id, episode_time, log_events, manual_control)
│   │   │   └── Starts new episode, loads map, initializes bots
│   │   ├── .new_episode(): Reset environment for new episode
│   │   ├── .make_action(action_idx): Execute agent action
│   │   │   └── Returns: reward (float)
│   │   ├── .get_state(): Get current game state
│   │   │   └── Returns: GameState(screen_buffer, game_variables, labels)
│   │   ├── .is_episode_finished(): Check if episode done
│   │   ├── .get_total_reward(): Get cumulative reward
│   │   ├── .get_available_game_variables(): List game vars
│   │   ├── .randomize_textures(enable): Enable texture randomization
│   │   ├── .init_bots_health(health): Set bot health
│   │   └── Buffers: screen_buffer (60x108x3), depth_buffer, labels_buffer
│   ├── WEAPON_NAMES: List of weapon strings
│   ├── WEAPONS_PREFERENCES: Weapon priority ordering
│   └── game_variables: health, ammo, killcount, etc.
├── Backend Integration:
│   └── from mydoom-master-Arnold.Arnold.src.doom.game import DoomGame
│       game = DoomGame(params)
│       game.start(map_id='/path/to/custom.wad')
│       while not game.is_episode_finished():
│           state = game.get_state()
│           action = network.forward(state)
│           reward = game.make_action(action)
└── Note: This file wraps vizdoom library, handles all game logic

src/doom/actions.py                          # EXISTING
├── Purpose: Action space definitions
├── Status: USE AS-IS (import action mappings)
├── Functions:
│   └── add_buttons(game, actions: List[str])
│       └── Configures available actions in VizDoom
├── Action Types:
│   ├── MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT
│   ├── TURN_LEFT, TURN_RIGHT
│   ├── ATTACK, SPEED (run)
│   └── Combinations: "move_fb+turn_lr+attack" (9 actions)
└── Backend Usage: Import to configure agent actions

src/doom/game_features.py                    # EXISTING
├── Purpose: Feature extraction from game state
├── Status: USE AS-IS (import feature parsers)
├── Functions:
│   └── parse_game_features(features_str: str) -> List
│       ├── Extracts: health, ammo, weapon, position, velocity
│       └── Example: "health,ammo,weapon" → [100, 50, 3]
└── Backend Usage: Parse telemetry data for database

src/doom/reward.py                           # EXISTING ⭐
├── Purpose: Reward function definition + event extraction
├── Status: READ + MODIFY for bug detection
├── Classes:
│   └── RewardBuilder
│       ├── __init__(params): Configure reward weights
│       ├── .get_reward(game_state, variables) -> float
│       │   └── Calculates reward from kills, deaths, pickups, damage
│       └── Event types: KILL, DEATH, PICKUP, DAMAGE, HEALTH_LOST
├── Backend Usage:
│   ├── Import RewardBuilder to parse events
│   ├── Modify: Add event logging to database (events table)
│   └── Extract events for LLM analysis
└── Integration:
    from src.doom.reward import RewardBuilder
    reward_builder = RewardBuilder(params)
    reward, events = reward_builder.get_reward(state)
    # Log events to PostgreSQL events table

src/doom/labels.py                           # EXISTING
├── Purpose: Object detection labels (enemies, items, walls)
├── Status: USE AS-IS (import label mappings)
├── Functions:
│   └── parse_labels_mapping(labels_str: str) -> Dict
│       └── Maps object IDs to semantic labels
└── Backend Usage: Identify objects in screenshots

src/doom/utils.py                            # EXISTING
├── Purpose: Image preprocessing utilities
├── Status: USE AS-IS (import preprocessing functions)
├── Functions:
│   └── process_buffers(screen, depth, labels, params)
│       ├── Resize, normalize, grayscale conversion
│       └── Returns: Processed numpy array for network input
└── Backend Usage: Preprocess frames before CV analysis

src/doom/scenarios/                          # Scenario-specific configs
├── __init__.py                              # EXISTING (package marker)
├── deathmatch.py                            # EXISTING
│   ├── Purpose: Deathmatch mode parameters
│   └── Contains: Map IDs, episode time, reward weights
├── deathmatch-eval.py                       # EXISTING
│   └── Purpose: Evaluation mode (no training)
├── defend_the_center.py                     # EXISTING
│   └── Purpose: Defense scenario params
├── health_gathering.py                      # EXISTING
│   └── Purpose: Survival mode params
└── self_play.py                             # EXISTING
    └── Purpose: Self-play training configuration
    
Status: REFERENCE (see how params are set)
Usage: Copy patterns to backend/config/scenarios.py
Backend: Create similar config files for custom scenarios
```

**src/model/ ⭐ (Neural Networks):**
```
src/model/__init__.py                        # EXISTING (package marker)

src/model/dqn/__init__.py                    # EXISTING (package marker)

src/model/dqn/base.py                        # EXISTING ⭐
├── Purpose: Base DQN class (Q-network architecture)
├── Status: IMPORT in backend/workers/agent_runner.py
├── Usage: Neural network forward pass for action selection
├── Classes:
│   └── DQN(nn.Module)
│       ├── __init__(params): Build CNN + FC layers
│       ├── .forward(screen, variables, features) -> q_values
│       │   ├── screen: (batch, channels, height, width)
│       │   ├── variables: (batch, n_variables) [health, ammo, ...]
│       │   ├── features: (batch, n_features) [optional game features]
│       │   └── Returns: (batch, n_actions) Q-values
│       ├── .reset(): Reset recurrent state (if LSTM)
│       └── Architecture:
│           CNN (screen) → Flatten → Concat(variables, features) → FC → Q-values
└── Backend Integration:
    from src.model.dqn.base import DQN
    network = DQN(params)
    network.load_state_dict(torch.load('pretrained/deathmatch_shotgun.pth'))
    network.eval()  # Set to inference mode
    
    with torch.no_grad():
        q_values = network.forward(screen_tensor, variables_tensor, None)
        action = q_values.argmax(dim=1).item()  # Greedy action selection

src/model/dqn/feedforward.py                 # EXISTING
├── Purpose: Feedforward DQN variant (no recurrence)
├── Status: USE if needed (base.py is default)
├── Classes: FeedforwardDQN(DQN)
│   └── Simpler architecture without LSTM
└── Usage: For non-sequential tasks (not recommended for DOOM)

src/model/dqn/recurrent.py                   # EXISTING ⭐
├── Purpose: LSTM-based DQN (handles temporal sequences)
├── Status: PRIMARY NETWORK (used in pre-trained models)
├── Usage: Same as base.py but maintains hidden state across frames
├── Classes:
│   └── RecurrentDQN(DQN)
│       ├── .reset(): Clear LSTM hidden state per episode
│       │   └── CRITICAL: Call before each episode
│       ├── .forward(screen, variables, features) -> q_values
│       │   └── Processes frame sequence through LSTM
│       └── Architecture:
│           CNN (screen) → LSTM → FC → Q-values
└── Backend Usage:
    from src.model.dqn.recurrent import RecurrentDQN
    network = RecurrentDQN(params)
    network.load_state_dict(torch.load('pretrained/...'))
    
    # Reset LSTM state at episode start
    network.reset()
    
    for frame in episode:
        q_values = network.forward(frame_tensor, vars_tensor, None)
        action = q_values.argmax().item()

src/model/bucketed_embedding.py              # EXISTING
├── Purpose: Feature embedding layer (bucketed continuous values)
├── Status: USED by DQN internally (don't import directly)
├── Classes: BucketedEmbedding(nn.Module)
│   └── Converts continuous features to embeddings
└── Usage: Internal to DQN, no direct backend usage

src/model/utils.py                           # EXISTING
├── Purpose: Model utility functions
├── Status: USE AS-IS (import if needed)
└── Functions: Model initialization, parameter counting, etc.
```

### Backend Directory (TO CREATE)

**Base Path:** `/media/steven/MaD/projects/grad-proj-final/backend/`

All files below need to be created from scratch. Development timeline provided.

#### Root Files
```
backend/__init__.py                          # TO CREATE (Week 1, Day 1)
├── Purpose: Package marker
└── Contents: Empty file or package exports

backend/main.py                              # TO CREATE (Week 1, Day 1) ⭐⭐⭐
├── Purpose: FastAPI application entry point
├── Status: CREATE FIRST (foundation for all API work)
├── Dependencies: fastapi, uvicorn
├── Contents (~100 lines):
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from backend.api.v1 import maps, runs, bugs, analysis, health
    from backend.api.websocket import router as ws_router
    from backend.core.config import settings
    from backend.core.logging import setup_logging
    
    # Initialize logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title="RL Game Testing API",
        version="1.0.0",
        description="Automated game testing using deep RL agents"
    )
    
    # CORS middleware (allow frontend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # React dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Include routers
    app.include_router(maps.router, prefix="/api/v1", tags=["maps"])
    app.include_router(runs.router, prefix="/api/v1", tags=["runs"])
    app.include_router(bugs.router, prefix="/api/v1", tags=["bugs"])
    app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(ws_router, tags=["websocket"])
    
    @app.on_event("startup")
    async def startup():
        # Initialize database connection pool
        # Initialize Redis connection
        pass
    
    @app.on_event("shutdown")
    async def shutdown():
        # Close connections
        pass

└── Run Command:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

backend/requirements.txt                     # TO CREATE (Week 1, Day 1) ⭐
├── Purpose: Python dependencies
└── Contents:
    # Web Framework
    fastapi==0.109.0
    uvicorn[standard]==0.27.0
    python-multipart==0.0.6  # File uploads
    
    # Database
    sqlalchemy==2.0.25
    alembic==1.13.1  # Migrations
    psycopg2-binary==2.9.9  # PostgreSQL driver
    asyncpg==0.29.0  # Async PostgreSQL
    
    # Cache & Queue
    redis==5.0.1
    celery==5.3.6
    flower==2.0.1  # Celery monitoring
    
    # File Storage
    boto3==1.34.34  # S3/MinIO client
    
    # AI/ML
    openai==1.10.0
    anthropic==0.18.0  # Claude API
    opencv-python==4.9.0.80  # Computer vision
    torch==2.2.0  # PyTorch
    torchvision==0.17.0
    vizdoom==1.2.3  # Game engine
    
    # Data Validation
    pydantic==2.6.0
    pydantic-settings==2.1.0  # Settings management
    
    # Security
    python-jose[cryptography]==3.3.0  # JWT
    passlib[bcrypt]==1.7.4  # Password hashing
    
    # Testing
    pytest==8.0.0
    pytest-asyncio==0.23.4
    httpx==0.26.0  # Async HTTP client for tests
    faker==22.6.0  # Generate test data
    
    # Development
    black==24.1.1  # Code formatter
    ruff==0.2.0  # Linter
    mypy==1.8.0  # Type checker
```

---

## Database Design (PostgreSQL - Web Optimized)

### Why PostgreSQL for Web Apps?

1. **ACID Compliance:** Critical for financial data, test results integrity
2. **JSONB Support:** Flexible schema for agent configs, metadata (NoSQL-like flexibility)
3. **Full-Text Search:** Search map names, bug descriptions without ElasticSearch
4. **Mature Ecosystem:** Excellent ORMs (SQLAlchemy), migration tools (Alembic)
5. **Horizontal Scaling:** Read replicas for analytics, write master for transactions
6. **Managed Services:** DigitalOcean ($15/mo), AWS RDS, Heroku Postgres (easy ops)

### Managed PostgreSQL Options

| Provider | Pricing | Specs | Features |
|----------|---------|-------|----------|
| **DigitalOcean Managed DB** | $15/mo | 1GB RAM, 10GB storage, 25 connections | Auto backups, monitoring, SSL |
| **AWS RDS PostgreSQL** | $25/mo | db.t3.micro (1GB RAM, 20GB storage) | Auto scaling, Multi-AZ, snapshots |
| **Heroku Postgres** | $50/mo | Standard-0 (2.5GB RAM, 64GB storage) | Continuous protection, rollback |
| **Supabase** | $25/mo | Pro plan (8GB storage, 2GB DB size) | Built-in auth, real-time, REST API |
| **Self-Hosted (Docker)** | $0 | Limited by server | Full control, no vendor lock-in |

**Recommendation:** Start with **DigitalOcean Managed DB** ($15/mo) → migrate to AWS RDS if scaling needs grow.

### Database Schema (Production-Optimized)

All tables from original design, with these web-specific additions:

#### New Table: `users` (Authentication)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,    -- bcrypt hashed
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- admin, user, viewer
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_role CHECK (role IN ('admin', 'user', 'viewer'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### New Table: `api_keys` (Programmatic Access)

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,      -- SHA256 hashed
    name VARCHAR(100) NOT NULL,                 -- "CI/CD Pipeline Key"
    last_used TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

#### Updated Table: `test_runs` (Add User Tracking)

```sql
ALTER TABLE test_runs 
ADD COLUMN created_by UUID REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_runs_created_by ON test_runs(created_by);
```

### Connection Pooling Configuration

```python
# backend/storage/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# Connection pool settings for web traffic
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,                    # Base connections (handles 20 concurrent requests)
    max_overflow=30,                 # Burst to 50 total connections under load
    pool_timeout=30,                 # Wait 30s for connection before error
    pool_recycle=1800,               # Recycle connections every 30 min (prevent stale connections)
    pool_pre_ping=True,              # Test connection validity before use (detect dead connections)
    echo=False,                      # Set True in dev for SQL query logging
    connect_args={
        "options": "-c statement_timeout=30000"  # 30s query timeout (prevent long-running queries)
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency injection for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Database Migrations (Alembic)

```bash
# Initialize Alembic (one-time)
alembic init backend/storage/migrations

# Create migration
alembic revision --autogenerate -m "add users table"

# Apply migrations (production)
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

**Migration Workflow:**
1. Developer makes schema changes in `models/database.py`
2. Run `alembic revision --autogenerate` → generates migration file
3. Review generated SQL in `migrations/versions/XXX_description.py`
4. Commit migration file to Git
5. CI/CD runs `alembic upgrade head` on deploy

---

## File Storage (S3-Compatible)

### Why S3 Over Local Filesystem?

| Aspect | Local Filesystem | S3/MinIO |
|--------|------------------|----------|
| **Scalability** | Limited by disk size | Unlimited (pay-as-you-go) |
| **Redundancy** | Single point of failure | Multi-region replication |
| **CDN Integration** | Requires NGINX config | Native CloudFront/Cloudflare |
| **Docker Compatibility** | Volumes get lost on container restart | Persistent across deployments |
| **Backup** | Manual rsync scripts | Automatic versioning |
| **Cost** | $0 (uses server disk) | $5-20/mo (1TB = $23/mo AWS S3) |

**Decision:**
- **Development:** Local filesystem or MinIO (self-hosted S3 clone in Docker)
- **Production:** AWS S3 (reliability + CDN) or DigitalOcean Spaces ($5/mo for 250GB)

### MinIO Setup (Docker)

```yaml
# docker-compose.yml
services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"      # S3 API
      - "9001:9001"      # Web UI
    volumes:
      - minio_data:/data

volumes:
  minio_data:
```

### Storage Service Implementation

```python
# backend/services/storage_service.py
import boto3
from pathlib import Path
from typing import BinaryIO
from backend.core.config import settings

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,        # http://localhost:9000 for MinIO
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket = settings.S3_BUCKET_NAME
    
    def upload_video(self, run_id: str, episode_num: int, file_content: BinaryIO) -> str:
        """Upload episode video to S3."""
        key = f"videos/{run_id}/episode_{episode_num}.mp4"
        self.s3.upload_fileobj(file_content, self.bucket, key)
        return self._get_public_url(key)
    
    def upload_screenshot(self, run_id: str, frame_num: int, image_bytes: bytes) -> str:
        """Upload bug screenshot to S3."""
        key = f"screenshots/{run_id}/frame_{frame_num}.png"
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=image_bytes)
        return self._get_public_url(key)
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate temporary signed URL (1 hour expiry by default)."""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expiration
        )
    
    def _get_public_url(self, key: str) -> str:
        """Get public URL (for public buckets) or presigned URL (for private buckets)."""
        if settings.S3_PUBLIC_BUCKET:
            return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"
        else:
            return self.generate_presigned_url(key)
    
    def delete_run_files(self, run_id: str) -> int:
        """Delete all files for a test run."""
        prefix = f"videos/{run_id}/"
        objects = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        
        if 'Contents' not in objects:
            return 0
        
        delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
        self.s3.delete_objects(Bucket=self.bucket, Delete={'Objects': delete_keys})
        
        return len(delete_keys)
```

---

## Redis Integration

### Redis Purposes

1. **Celery Task Queue:** Job persistence, result backend
2. **API Response Caching:** Cache expensive queries (e.g., map statistics)
3. **WebSocket State:** Track connected clients, broadcast channels
4. **Rate Limiting:** Prevent API abuse (X requests per minute per IP)
5. **Session Storage:** User sessions (optional, can use JWT stateless tokens)

### Redis Setup

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Redis Client

```python
# backend/storage/cache.py
import redis
import json
from typing import Optional, Any
from backend.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set cached value with TTL (default 5 minutes)."""
        self.redis.setex(key, ttl, json.dumps(value))
    
    def delete(self, key: str):
        """Invalidate cache."""
        self.redis.delete(key)
    
    def clear_pattern(self, pattern: str):
        """Delete all keys matching pattern (e.g., 'map:*')."""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

# Usage in API endpoint
@router.get("/api/v1/maps/{map_id}")
async def get_map(map_id: UUID, cache: CacheService = Depends(get_cache)):
    # Try cache first
    cache_key = f"map:{map_id}:details"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Cache miss, fetch from DB
    map_data = service.get_map_details(map_id)
    
    # Store in cache (5 min TTL)
    cache.set(cache_key, map_data, ttl=300)
    
    return map_data
```

---

## Celery Worker Layer

### Why Celery?

**Problem:** Agent test runs take 5-10 minutes. HTTP requests timeout after 30-60 seconds. Can't block API requests.

**Solution:** Celery offloads long-running tasks to background workers. API returns immediately with task_id, client polls for status.

**Architecture:**
```
FastAPI (API) → Celery (Task Queue) → Worker (Executes Task) → PostgreSQL (Results)
       ↓                                        ↓
  Returns task_id                    Broadcasts progress via WebSocket
       ↓
  Client polls GET /runs/{id}
```

### Celery Configuration

```python
# backend/workers/celery_app.py
from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "rl_game_tester",
    broker=settings.CELERY_BROKER_URL,      # redis://localhost:6379/0
    backend=settings.CELERY_RESULT_BACKEND  # redis://localhost:6379/1
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,                # Track task start time
    task_time_limit=1800,                   # 30 min max (prevent hung tasks)
    task_soft_time_limit=1500,              # 25 min soft limit (graceful shutdown)
    worker_prefetch_multiplier=1,           # Disable prefetch (important for long tasks)
    worker_max_tasks_per_child=10,          # Restart worker after 10 tasks (prevent memory leaks)
)
```

### Task Definition

```python
# backend/workers/tasks.py
from celery import Task
from backend.workers.celery_app import celery_app
from backend.workers.agent_runner import AgentRunner
from backend.storage.database import SessionLocal
from backend.services.run_service import RunService
from backend.api.websocket import broadcast_progress

class RunTestTask(Task):
    """Custom task class with retry logic."""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True

@celery_app.task(base=RunTestTask, bind=True)
def run_agent_test(self, run_id: str):
    """Execute agent test in background."""
    db = SessionLocal()
    
    try:
        # Update status to running
        run_service = RunService(db)
        run_service.update_status(run_id, "running")
        
        # Initialize agent runner
        runner = AgentRunner(run_id=run_id, db=db)
        
        # Run test with progress callbacks
        def on_progress(episode: int, frame: int, total_frames: int):
            progress = {
                "run_id": run_id,
                "episode": episode,
                "frame": frame,
                "percentage": (frame / total_frames) * 100
            }
            # Broadcast via WebSocket
            broadcast_progress(progress)
            # Update Celery task state
            self.update_state(state='PROGRESS', meta=progress)
        
        result = runner.execute(progress_callback=on_progress)
        
        # Update status to completed
        run_service.update_status(run_id, "completed", result=result)
        
        return {"run_id": run_id, "status": "completed", "result": result}
    
    except Exception as e:
        # Update status to failed
        run_service.update_status(run_id, "failed", error=str(e))
        raise  # Re-raise to trigger retry
    
    finally:
        db.close()
```

### Agent Runner Wrapper

```python
# backend/workers/agent_runner.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "arnold"))

from arnold.arnold import Arnold  # Import existing agent
from backend.models.database import TestRun, Episode, Event
from backend.services.bug_service import BugService

class AgentRunner:
    def __init__(self, run_id: str, db):
        self.run_id = run_id
        self.db = db
        self.bug_service = BugService(db)
    
    def execute(self, progress_callback=None):
        """Execute agent test."""
        # Load test run config
        run = self.db.query(TestRun).filter(TestRun.id == self.run_id).first()
        agent_config = run.agent_config
        
        # Initialize Arnold agent
        agent = Arnold(
            model_path=agent_config['model'],
            episodes=agent_config['episodes'],
            seed=agent_config['seed']
        )
        
        results = []
        
        # Run episodes
        for ep_num in range(agent_config['episodes']):
            episode_result = agent.run_episode(
                map_path=run.map.file_path,
                episode_number=ep_num
            )
            
            # Create episode record
            episode = Episode(
                run_id=self.run_id,
                episode_number=ep_num + 1,
                outcome=episode_result['outcome'],
                duration_seconds=episode_result['duration'],
                final_health=episode_result['final_health']
            )
            self.db.add(episode)
            self.db.commit()
            
            # Store events (telemetry)
            events = []
            for frame_data in episode_result['frames']:
                event = Event(
                    episode_id=episode.id,
                    frame_number=frame_data['frame'],
                    timestamp_seconds=frame_data['timestamp'],
                    event_type=frame_data['event_type'],
                    event_data=frame_data['data'],
                    agent_position=frame_data['position'],
                    agent_health=frame_data['health']
                )
                events.append(event)
            
            self.db.bulk_save_objects(events)
            self.db.commit()
            
            # Run bug detection (CV + LLM)
            bugs = self.bug_service.detect_bugs(episode.id, episode_result['frames'])
            
            # Progress callback
            if progress_callback:
                progress_callback(
                    episode=ep_num + 1,
                    frame=len(episode_result['frames']),
                    total_frames=agent_config['episodes'] * 2100
                )
            
            results.append({
                "episode": ep_num + 1,
                "bugs_found": len(bugs),
                "outcome": episode_result['outcome']
            })
        
        return results
```

### Dispatching Tasks from API

```python
# backend/api/v1/runs.py
from backend.workers.tasks import run_agent_test

@router.post("", response_model=TestRunResponse, status_code=202)
async def create_test_run(
    request: TestRunCreateRequest,
    service: RunService = Depends(get_run_service)
):
    """Create and start a test run."""
    # Create database record
    run = service.create_run(request.map_id, request.agent_config)
    
    # Dispatch Celery task (non-blocking)
    task = run_agent_test.delay(str(run.id))
    
    # Return immediately with task ID
    return {
        "run_id": run.id,
        "map_id": request.map_id,
        "status": "pending",
        "task_id": task.id,
        "estimated_duration_seconds": 360,
        "message": f"Test run queued. Check status at /api/v1/runs/{run.id}"
    }

@router.get("/{run_id}")
async def get_test_run(
    run_id: UUID,
    service: RunService = Depends(get_run_service)
):
    """Get test run status and results."""
    run = service.get_run(run_id)
    
    # If still running, include progress from Celery state
    if run.status == "running":
        task = celery_app.AsyncResult(run.task_id)
        if task.state == 'PROGRESS':
            run.progress = task.info
    
    return run
```

---

## WebSocket Server (Real-Time Updates)

### Why WebSockets?

**Without WebSockets (Polling):**
```javascript
// Frontend polls every 2 seconds (inefficient, 30 requests/minute)
setInterval(() => {
  fetch(`/api/v1/runs/${runId}`)
    .then(res => res.json())
    .then(data => updateProgress(data.progress))
}, 2000)
```

**With WebSockets (Push):**
```javascript
// Backend pushes updates only when something changes (1 connection, instant updates)
const ws = new WebSocket('ws://localhost:8000/ws')
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  updateProgress(data.progress)
}
```

### WebSocket Implementation

```python
# backend/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json

class ConnectionManager:
    """Manage WebSocket connections."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}  # run_id -> [connections]
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for subscribers in self.subscriptions.values():
            if websocket in subscribers:
                subscribers.remove(websocket)
    
    def subscribe(self, run_id: str, websocket: WebSocket):
        """Subscribe connection to run updates."""
        if run_id not in self.subscriptions:
            self.subscriptions[run_id] = []
        self.subscriptions[run_id].append(websocket)
    
    async def broadcast_to_run(self, run_id: str, message: dict):
        """Send message to all subscribers of a run."""
        if run_id not in self.subscriptions:
            return
        
        disconnected = []
        for connection in self.subscriptions[run_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.subscriptions[run_id].remove(conn)
    
    async def broadcast_all(self, message: dict):
        """Broadcast to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# WebSocket endpoint
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, run_id: str = None):
    await manager.connect(websocket)
    
    if run_id:
        manager.subscribe(run_id, websocket)
        await websocket.send_json({
            "type": "subscribed",
            "run_id": run_id
        })
    
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client commands (e.g., subscribe to different run)
            if message['type'] == 'subscribe':
                manager.subscribe(message['run_id'], websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Helper function called from Celery worker
def broadcast_progress(progress: dict):
    """Called from Celery task to broadcast progress."""
    import asyncio
    run_id = progress['run_id']
    
    # Run async broadcast in new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(manager.broadcast_to_run(run_id, {
        "type": "progress",
        "data": progress
    }))
    loop.close()
```

### Frontend WebSocket Client

```typescript
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useState } from 'react'

export function useTestRunProgress(runId: string) {
  const [progress, setProgress] = useState({ percentage: 0, episode: 0, frame: 0 })
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws?run_id=${runId}`)
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      if (message.type === 'progress') {
        setProgress(message.data)
      }
      
      if (message.type === 'completed') {
        // Fetch final results
        window.location.href = `/runs/${runId}/results`
      }
    }
    
    ws.onerror = (error) => console.error('WebSocket error:', error)
    
    return () => ws.close()
  }, [runId])
  
  return progress
}
```

---

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml (local development)
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: rl_user
      POSTGRES_PASSWORD: rl_password
      POSTGRES_DB: rl_game_tester
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
  
  backend:
    build:
      context: .
      dockerfile: deployment/docker/backend.Dockerfile
    environment:
      DATABASE_URL: postgresql://rl_user:rl_password@postgres:5432/rl_game_tester
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT: http://minio:9000
      CELERY_BROKER_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./arnold:/app/arnold
    depends_on:
      - postgres
      - redis
      - minio
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
  
  worker:
    build:
      context: .
      dockerfile: deployment/docker/worker.Dockerfile
    environment:
      DATABASE_URL: postgresql://rl_user:rl_password@postgres:5432/rl_game_tester
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT: http://minio:9000
      CELERY_BROKER_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app/backend
      - ./arnold:/app/arnold
    depends_on:
      - postgres
      - redis
      - minio
    command: celery -A backend.workers.celery_app worker --loglevel=info --concurrency=2
  
  frontend:
    build:
      context: ./frontend
      dockerfile: ../deployment/docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

**Start Development Environment:**
```bash
docker-compose up -d
```

---

### Production Environment (DigitalOcean Droplet Example)

**Server Specs:**
- Droplet: $48/mo (8GB RAM, 4 vCPUs, 160GB SSD)
- Managed PostgreSQL: $15/mo (1GB RAM, 10GB storage)
- Spaces (S3): $5/mo (250GB storage + CDN)

**Total: $68/mo**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - frontend_build:/usr/share/nginx/html:ro
    depends_on:
      - backend
  
  backend:
    image: your-registry/rl-game-tester-backend:latest
    environment:
      DATABASE_URL: ${DATABASE_URL}  # Managed DB connection string
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT: https://nyc3.digitaloceanspaces.com
      S3_BUCKET_NAME: rl-game-tester
      JWT_SECRET: ${JWT_SECRET}
    deploy:
      replicas: 2  # Load-balanced API instances
      restart_policy:
        condition: on-failure
    depends_on:
      - redis
  
  worker:
    image: your-registry/rl-game-tester-worker:latest
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT: https://nyc3.digitaloceanspaces.com
    deploy:
      replicas: 4  # 4 concurrent test runs
      resources:
        limits:
          cpus: '0.75'
          memory: 1.5G
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
  frontend_build:
```

### NGINX Configuration

```nginx
# nginx/nginx.conf
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name rl-game-tester.com;
    return 301 https://$server_name$request_uri;  # Redirect to HTTPS
}

server {
    listen 443 ssl http2;
    server_name rl-game-tester.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;  # 1 hour timeout
    }
    
    # File uploads (increase limits)
    client_max_body_size 100M;
}
```

### SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d rl-game-tester.com

# Auto-renewal (cron job)
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

---

## CI/CD Pipeline (GitHub Actions Example)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest backend/tests/
      
      - name: Lint
        run: |
          black --check backend/
          flake8 backend/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t your-registry/backend:latest -f deployment/docker/backend.Dockerfile .
          docker build -t your-registry/worker:latest -f deployment/docker/worker.Dockerfile .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push your-registry/backend:latest
          docker push your-registry/worker:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to DigitalOcean
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DO_HOST }}
          username: ${{ secrets.DO_USERNAME }}
          key: ${{ secrets.DO_SSH_KEY }}
          script: |
            cd /opt/rl-game-tester
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
            docker system prune -af
```

---

## Monitoring & Logging

### Application Logging

```python
# backend/core/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Usage in code
from backend.core.logging import setup_logging
logger = setup_logging()

logger.info("Test run started", extra={
    "run_id": run_id,
    "map_id": map_id,
    "user_id": user_id
})
```

### Health Check Endpoint

```python
# backend/api/v1/health.py
@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """System health check."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        cache = CacheService()
        cache.redis.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check S3
    try:
        storage = StorageService()
        storage.s3.list_buckets()
        health_status["storage"] = "accessible"
    except Exception as e:
        health_status["storage"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Celery workers
    try:
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        health_status["workers"] = {
            "count": len(active_workers) if active_workers else 0,
            "status": "active" if active_workers else "no workers"
        }
    except Exception as e:
        health_status["workers"] = f"error: {str(e)}"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

### Monitoring with Grafana + Prometheus (Optional)

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

---

## Cost Estimation (Production)

### Monthly Costs

| Service | Tier | Cost |
|---------|------|------|
| **DigitalOcean Droplet** | 8GB RAM, 4 vCPUs | $48/mo |
| **Managed PostgreSQL** | 1GB RAM, 10GB storage | $15/mo |
| **Spaces (S3)** | 250GB + CDN | $5/mo |
| **Domain Name** | .com TLD | $12/yr = $1/mo |
| **SSL Certificate** | Let's Encrypt | $0 (free) |
| **LLM API** | 200 tests/mo × $0.15 | $30/mo |
| **Monitoring** | Self-hosted Grafana | $0 |
| **Backup Storage** | 50GB backups | $2/mo |
| **Total** | | **$101/mo** |

### Scaling Path

**Stage 1 (MVP - 10 users):** $101/mo
- 1 droplet (API + workers)
- Managed DB (10GB)
- 250GB storage

**Stage 2 (Growth - 100 users):** $250/mo
- 2 droplets (load balanced)
- Managed DB upgraded to 4GB RAM
- 1TB storage
- Redis upgraded to cluster

**Stage 3 (Scale - 1000+ users):** $800+/mo
- 4 API instances (load balanced)
- 8 worker instances (dedicated)
- Multi-region DB (read replicas)
- CloudFront CDN
- Kubernetes orchestration

---

## Implementation Timeline (Updated for Web Deployment)

### Week 1 (Days 1-7): Foundation
- **Day 1-2:** Docker setup (Postgres, Redis, MinIO containers)
- **Day 3-4:** Database schema implementation + migrations
- **Day 5-6:** Repository layer + basic CRUD operations
- **Day 7:** Testing framework setup

**Deliverable:** Database operational, can insert/query test data

---

### Week 2 (Days 8-14): Backend Core
- **Day 8-9:** Service layer (MapService, RunService)
- **Day 10-11:** Storage service (S3/MinIO integration)
- **Day 12-13:** API endpoints (maps, runs - basic CRUD)
- **Day 14:** Authentication (JWT, user registration)

**Deliverable:** API endpoints work, can upload maps via Postman

---

### Week 3 (Days 15-21): Celery Integration
- **Day 15-16:** Celery setup (workers, task queue)
- **Day 17-18:** Agent runner wrapper (connect Arnold to Celery)
- **Day 19-20:** Progress tracking + error handling
- **Day 21:** Testing Celery tasks end-to-end

**Deliverable:** Background task execution works, test runs complete

---

### Week 4 (Days 22-28): Bug Detection
- **Day 22-23:** CV model integration (frame analysis)
- **Day 24-25:** LLM service (OpenAI/Anthropic API client)
- **Day 26-27:** Bug detection pipeline (CV → LLM → DB)
- **Day 28:** Testing bug detection on sample runs

**Deliverable:** Bugs detected and stored with LLM descriptions

---

### Week 5 (Days 29-35): WebSocket + Real-Time
- **Day 29-30:** WebSocket server implementation
- **Day 31-32:** Integrate WebSocket with Celery (progress broadcasts)
- **Day 33-34:** Advanced API endpoints (analysis, comparison)
- **Day 35:** API documentation (Swagger/OpenAPI)

**Deliverable:** Real-time progress updates working, API complete

---

### Week 6 (Days 36-42): API Optimization
- **Day 36-37:** Redis caching layer
- **Day 38-39:** Query optimization (indexes, N+1 fixes)
- **Day 40-41:** Rate limiting + security hardening
- **Day 42:** Load testing (simulate 50 concurrent users)

**Deliverable:** API responses <100ms, handles load

---

### Week 7-10 (Days 43-70): Frontend Development
*(Member 4 full-time)*

**Week 7 (Days 43-49):**
- Project setup (React + TypeScript + Vite)
- API client (Axios with interceptors)
- Authentication pages (login, register)
- Dashboard layout (sidebar, navigation)

**Week 8 (Days 50-56):**
- Map library page (grid, upload, delete)
- Map detail page (stats, hardness gauge)
- Test run trigger UI
- WebSocket client hook (useTestRunProgress)

**Week 9 (Days 57-63):**
- Bug report dashboard (filterable table)
- Timeline visualization (Plotly.js charts)
- Screenshot modal (image viewer)
- Progress tracking UI (real-time)

**Week 10 (Days 64-70):**
- Comparative analysis page (radar charts)
- Statistics dashboard (aggregate data)
- Video playback component
- Responsive design (mobile support)

**Deliverable:** Complete frontend, integrated with backend

---

### Week 11 (Days 71-77): Integration & Testing
- **Day 71-73:** End-to-end testing (30+ test runs)
- **Day 74-75:** Bug fixes from testing
- **Day 76-77:** User acceptance testing (team walkthrough)

**Deliverable:** Stable system, all features functional

---

### Week 12 (Days 78-84): Deployment & Documentation
- **Day 78-79:** Production deployment (DigitalOcean)
- **Day 80-81:** Documentation (API docs, user guide)
- **Day 82-83:** Monitoring setup (Grafana dashboards)
- **Day 84:** Final presentation preparation

**Deliverable:** Live production system, complete documentation

---

## Security Considerations

### Authentication (JWT)

```python
# backend/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### Input Validation

```python
# Pydantic handles this automatically
class MapUploadRequest(BaseModel):
    name: str = Field(..., max_length=255, regex="^[a-zA-Z0-9_-]+$")
    # Only alphanumeric, underscores, hyphens allowed (prevent injection)
```

### SQL Injection Prevention

```python
# SQLAlchemy ORM prevents SQL injection automatically
# DON'T DO THIS (raw SQL):
db.execute(f"SELECT * FROM maps WHERE name = '{user_input}'")  # VULNERABLE!

# DO THIS (parameterized query via ORM):
db.query(Map).filter(Map.name == user_input).first()  # SAFE
```

---

## Backup Strategy

### Database Backups

```bash
# scripts/backup_database.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DATABASE_URL="postgresql://user:pass@localhost:5432/rl_game_tester"

# Create backup
pg_dump $DATABASE_URL | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Delete backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://backups/postgres/
```

**Schedule with cron:**
```bash
0 2 * * * /opt/rl-game-tester/scripts/backup_database.sh  # Daily at 2 AM
```

---

## Summary

**This architecture is production-ready for a web application because:**

1. ✅ **Scalable:** Stateless API, horizontal worker scaling, managed database
2. ✅ **Reliable:** Task queue persists jobs, database transactions, error handling
3. ✅ **Fast:** Redis caching, CDN for media, indexed queries, connection pooling
4. ✅ **Real-Time:** WebSocket push updates, no polling overhead
5. ✅ **Maintainable:** Clean layered architecture, dependency injection, tests
6. ✅ **Secure:** JWT auth, input validation, SQL injection prevention
7. ✅ **Observable:** Health checks, structured logging, monitoring support
8. ✅ **Cost-Effective:** $101/mo production deployment, scales to $800/mo at 1000+ users

**The layered architecture (API → Service → Storage → Database) works perfectly for web deployment with the addition of:**
- Celery workers for async task processing
- WebSocket server for real-time updates
- Redis for caching and task queue
- S3/MinIO for file storage
- NGINX for reverse proxy and static file serving

**No shortcuts. Build it right. Ship it to production.**
