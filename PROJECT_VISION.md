# PROJECT VISION: Deep RL Game Tester
**100% Complete Vision Document - Context Preservation**

---

## PROJECT IDENTITY

**Name:** Deep RL Game Tester  
**Type:** Graduation Project - Faculty of Computing and Information Sciences  
**Nature:** Research Showcase / Framework Demonstration  
**Supervisor:** Prof./Dr. Mohamed Taher  
**Timeline:** 7-8 weeks  
**Current Phase:** Deliverable #1 (Documentation)  
**Deadline:** 3-4 days for document, 7 days total for 40-50% implementation

**CRITICAL CONTEXT:** This is a **research showcase demonstrating a generalizable methodology**, NOT a Doom-specific tool. Doom is the implementation vehicle for proof-of-concept validation; the framework design is intentionally engine-agnostic.

---

## CORE Pgame level testing (universal problem across ALL game engines) is:**
- Time-consuming (100+ hours for 50 levels in any game)
- Expensive (requires dedicated QA staff)
- Subjective (difficulty assessment varies by tester)
- Error-prone (humans miss bugs, can't test exhaustively)
- Not scalable (can't test thousands of procedurally generated levels)

**This problem exists in:**
- Unity games (most mobile/indie games)
- Unreal Engine games (AAA titles)
- Doom (our showcase implementation)
- Godot, GameMaker, proprietary engines
- Any game with player-traversable levels

### Why It Matters (Industry-Wide)
- Game developers waste 30-40% of development time on QA (all engines)
- Level designers have no objective quality metrics (universal gap)
- Bugs in production hurt player experience and reviews (affects all games)
- No automated way to measure level difficulty before release (unsolved problem)
- Procedural generation demands QA automation (growing industry need)
- Custom map creators have no objective quality metrics
- Bugs in production hurt player experience and reviews
- No automated way to measure map difficulty before release

---

## OUR SOLUTION

### System Purpose
**Automated game level quality testing using Deep Reinforcement Learning**

⚠️ **IMPORTANT: This is a RESEARCH SHOWCASE using Doom as proof-of-concept**
- The methodology is GENERALIZABLE to any game engine
- Doom chosen for: mature RL tools (VizDoom), available agents, research precedent
- Same approach applies to: Unity games, Unreal levels, procedural content, etc.
- Core contribution: RL-based testing framework, not Doom-specific implementation

**Current Implementation:** An RL agent (Arnold - pre-trained DQN) plays custom Doom maps autonomously, collecting comprehensive metrics, detecting bugs, measuring difficulty, and storing results in a queryable database for comparative analysis.

### Key Innovation
**We replace human testers with AI agents that:**
1. Never get tired or bored
2. Provide objective, repeatable metrics
3. Test 10+ levels per hour (vs 0.5 manual)
4. Detect bugs humans might miss
5. Generate quantitative difficulty scores
6. Enable cross-lev (Framework Architecture)
```
┌─────────────────────────────┐
│  Game Level (Any Engine)    │  ← Input: Unity scene, Unreal level, Doom map, etc.
│  Unity/.unity               │
│  Unreal/.umap               │
│  Doom/.wad (our showcase)   │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  Game Engine Adapter        │  ← Abstraction layer (70% reusable)
│  (VizDoom in this impl.)    │     Translates engine-specific to generic
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  RL Agent Controller        │  ← Framework core (100% reusable)
│  (Arnold DQN for showcase)  │     Any trained agent works
└──────────┬──────────────────┐
│  VizDoom Engine │ ← Game simulation environment
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Arnold Agent   │ ← Pre-trained DQN (PyTorch)
│  (DQN - PyTorch)│    Plays the map autonomously
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Metrics Extract │ ← Frame-by-frame data collection
│  - Health       │    - Deaths count
│  - Ammo         │    - Steps taken
│  - Position     │    - Health timeline
│  - Events       │    - Bug detection
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  PostgreSQL DB  │ ← Persistent storage
│  - maps         │    - All test runs
│  - runs         │    - Events timeline
│  - events       │    - Metrics history
│  - metrics      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Query API     │ ← Data access layer
│  - Get stats    │    - Cross-map comparison
│  - Compare maps │    - Aggregate analytics
│  - Find bugs    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Visualization  │ ← (Showcase Implementation)
| Component | Technology | Version | Why | Generalizability |
|-----------|-----------|---------|-----|------------------|
| **Game Engine Adapter** | VizDoom | 1.2.3+ | Doom-based RL platform, Python API | **Swappable:** Unity ML-Agents, Unreal Gym, custom adapters |
| **RL Framework** | PyTorch | 2.0+ | Industry standard, flexible | **Reusable:** Same for any engine |
| **RL Agent** | Arnold (DQN) | Existing | Pre-trained, proven | **Replaceable:** Any trained agent (PPO, SAC, etc.) |
| **Database** | PostgreSQL | 16+ | Robust, relational, handles JSONB | **100% Reusable:** Engine-agnostic schema |
| **ORM** | SQLAlchemy | 2.0+ | Python DB abstraction | **100% Reusable:** No game-specific logic |
| **Visualization** | Matplotlib/Plotly | Latest | Timeline plots, comparative charts | **100% Reusable:** Generic metric plotting |
| **Language** | Python | 3.12+ | Entire system in Python | **100% Reusable:** No engine dependencies |
| **Web Framework** | Flask | 3.0+ (optional) | REST API / Simple dashboard | **100% Reusable:** Engine-agnostic API |
| **Containerization** | Docker | Latest (optional) | Deployment and portability | **100% Reusable:** Platform-independent |

**Key Insight:** Only the **Game Engine Adapter** row needs modification for different engines. Everything else (8/9 components) is **fully reusable**.
| Component | Technology | Version | Why |
|-----------|-----------|---------|-----|
| **Game Engine** | VizDoom | 1.2.3+ | Doom-based RL platform, Python API |
| **RL Framework** | PyTorch | 2.0+ | Arnold agent uses PyTorch DQN |
| **RL Agent** | Arnold (DQN) | Existing | Pre-trained, proven on Doom scenarios |
| **Database** | PostgreSQL | 16+ | Robust, relational, handles JSONB |
| **ORM** | SQLAlchemy | 2.0+ | Python DB abstraction |
| **Visualization** | Matplotlib/Plotly | Latest | Timeline plots, comparative charts |
| **Language** | Python | 3.12+ | Entire system in Python |
| **Web Framework** | Flask | 3.0+ (optional) | REST API / Simple dashboard |
| **Containerization** | Docker | Latest (optional) | Deployment and portability |

### Development Tools
- **IDE:** VS Code
- **Version Control:** Git + GitHub
- **Documentation:** Markdown, draw.io, LaTeX
- **Project Management:** GANTT charts, todo lists
- **Testing:** pytest, manual testing

---

## DATABASE SCHEMA

### Tables Design

#### 1. `maps` Table
Stores metadata about test maps
```sql
CREATE TABLE maps (
    id VARCHAR(50) PRIMARY KEY,           -- Unique map identifier
    name VARCHAR(200) NOT NULL,           -- Human-readable name
    file_path VARCHAR(500) NOT NULL,      -- Absolute path to .wad file
    size_kb INTEGER,                      -- File size
    metadata JSONB,                       -- Extra info (author, description, etc.)
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `runs` Table
Each test run of the agent on a map
```sql
CREATE TABLE runs (
    id SERIAL PRIMARY KEY,
    map_id VARCHAR(50) REFERENCES maps(id) ON DELETE CASCADE,
    run_index INTEGER,                    -- nth run of this map (for multiple tests)
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    outcome VARCHAR(50),                  -- 'completed', 'timeout', 'crashed', 'unsolvable'
    episodes_count INTEGER DEFAULT 1,     -- How many episodes in this run
    agent_config JSONB                    -- Agent parameters used
);
```

#### 3. `events` Table
Frame-by-frame events during gameplay
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id) ON DELETE CASCADE,
    episode_index INTEGER,                -- Which episode within the run
    time_step INTEGER,                    -- Frame number
    event_type VARCHAR(50),               -- 'death', 'health_change', 'stuck', 'ammo_pickup', etc.
    value JSONB,                          -- Event-specific data
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. `metrics` Table
Aggregated metrics per run
```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id) ON DELETE CASCADE,
    total_deaths INTEGER DEFAULT 0,       -- How many times agent died
    total_steps INTEGER DEFAULT 0,        -- Total frames played
    avg_health FLOAT,                     -- Average health across episode
    min_health FLOAT,                     -- Lowest health reached
    max_health FLOAT,                     -- Starting health
    ammo_used INTEGER,                    -- Total ammo consumed
    kills INTEGER DEFAULT 0,              -- Enemies killed
    completion_percentage FLOAT,          -- Map % completed (if detectable)
    hardness_score FLOAT,                 -- Calculated difficulty (0-100)
    is_solvable BOOLEAN,                  -- Agent could complete it
    bugs_detected JSONB,                  -- List of detected bugs
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Relationships
- `maps` 1→N `runs` (one map, many test runs)
- `runs` 1→N `events` (one run, many frame events)
- `runs` 1→1 `metrics` (one run, one aggregated metric)
Level Testing (Engine-Agnostic Process)
**Input:** Game level in any supported format
- Doom: .wad file (current showcase)
- Unity: .unity scene file (future)
- Unreal: .umap level file (future)
- Custom: JSON/XML level descriptor (extensible)

**Process (100% Generic):**
- Load level via engine adapter
- Spawn RL agent controller
- Run N episodes (configurable, default: 5)
- Collect frame-by-frame data (health, position, events)
- Handle crashes/timeouts gracefully
- Store results in engine-agnostic database

**Output:** Complete test run stored in database

**Showcase Implementation (Doom):**
- Load .wad into VizDoom → Spawn Arnold agent → Run 5 episodes
- **Estimated effort to port to Unity:** 2-3 weeks (only adapter layer)
- **Estimated code reuse:** 70-80% of existing implementation
- Run N episodes (default: 5)
- Collect frame-by-frame data
- Handle crashes/timeouts gracefully

**Output:** Complete test run stored in database

### 2. Bug Detection
**Algorithm detects:**

#### A. Stuck Detection
- **Definition:** Agent position unchanged for 100+ consecutive frames
- **Method:** Track (x, y, z) coordinates every frame
- **Threshold:** If `position[i-100:i]` all identical → stuck bug
- **Severity:** High (game-breaking)

#### B. Instant Death
- **Definition:** Health drops >80 in single frame
- **Method:** Monitor health every frame
- **Threshold:** `health[t-1] > 80 AND health[t] == 0`
- **Severity:** Critical (likely map bug, not gameplay)

#### C. Unreachable Areas
- **Definition:** Agent never reaches expected map regions
- **Method:** Heatmap of visited coordinates
- **Threshold:** Coverage <60% after multiple runs
- **Severity:** Medium (design flaw)

#### D. Crash Detection
- **Definition:** Game process terminates unexpectedly
- **Method:** Exception handling in runner
- **Action:** Log crash, mark map as problematic

### 3. Hardness Score Calculation
**Formula (weighted 0-100 scale):**

```python
hardness_score = (
    normalize(total_deaths, 0, 50) * 0.35 +      # 35% weight on deaths
    normalize(completion_time, 0, 2100) * 0.25 + # 25% on time taken
    (1 - normalize(avg_health, 0, 100)) * 0.20 + # 20% on health loss
    normalize(stuck_count, 0, 10) * 0.20         # 20% on stuck events
) * 100
```

**Score Interpretation:**
- **0-20:** Very Easy (beginner-friendly)
- **21-40:** Easy (casual play)
- **41-60:** Medium (balanced challenge)
- **61-80:** Hard (experienced players)
- **81-100:** Very Hard (expert only)

### 4. Solvability Detection
**Definition:** Can the agent complete the map?

**Criteria:**
- Agent reaches exit/completes objectives in ANY episode
- No critical bugs blocking progress
- Timeout not reached (max 2100 steps ~2 minutes)

**Output:** Boolean `is_solvable` in metrics table

### 5. Query API
**Available Queries:**

```python
# Single map statistics
get_map_stats(map_id) → dict
  - Total runs
  - Avg hardness
  - Solvability rate
  - Common bugs
  - Best/worst run

# Compare two maps
compare_maps(map_id_1, map_id_2) → dict
  - Side-by-side metrics
  - Difficulty delta
  - Bug count comparison
  - Visualization URLs

# Find hardest maps
get_hardest_maps(limit=10) → list
  - Ranked by hardness_score
  - Include map name, score, solvability

# Find unsolvable maps
get_unsolvable_maps() → list
  - Maps with is_solvable=False
  - Include bug details

# Aggregate statistics
get_aggregate_stats() → dict
  - Total maps tested
  - Avg hardness across all maps
  - Bug frequency distribution
  - Solvability rate
```

### 6. Timeline Visualization
**Generated Plots:**

#### A. Health Timeline
- X-axis: Time steps (frames)
- Y-axis: Health (0-100)
- Markers: Red dots at death events
- Shaded regions: Bug-detected periods

#### B. Multi-Metric Dashboard
- Subplot 1: Health over time
- Subplot 2: Ammo over time
- Subplot 3: Position heatmap
- Subplot 4: Events histogram

#### C. Comparative Bar Charts
- Compare multiple maps side-by-side
- Metrics: Deaths, time, hardness score
- Export as PNG/PDF

---

## AGENT INTEGRATION

### Arnold Agent Details
**Location:** `mydoom-master-Arnold/Arnold/`

**Pre-trained Models:**
- `deathmatch_shotgun.pth` ← Primary for testing
- `defend_the_center.pth`
- `health_gathering.pth`

**Key Files to Modify:**
- `src/doom/game.py` ← Add custom map loading
- `src/doom/actions.py` ← Ensure action space compatible
- `arnold.py` ← Main agent wrapper

### Required Modifications

#### 1. Custom Map Loader
**Current:** Arnold only loads predefined scenarios  
**Needed:** Accept arbitrary .wad file paths

```python
# In src/doom/game.py
def load_custom_map(wad_path, config=None):
    game = vzd.DoomGame()
    game.set_doom_scenario_path(wad_path)
    game.set_doom_map("MAP01")  # or detect from .wad
    game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
    game.set_window_visible(False)
    game.init()
    return game
```

#### 2. Metrics Extraction
**Add to game loop:**
```python
# Track every frame
state = game.get_state()
metrics_collector.record({
    'health': state.game_variables[0],
    'ammo': state.game_variables[1],
    'position': (state.game_variables[2], state.game_variables[3]),
    'kills': state.game_variables[4]
})

# Detect events
if prev_health > 0 and state.game_variables[0] == 0:
    events.append({'type': 'death', 'time': step})
```

#### 3. Training/Fine-tuning Strategy
**Option A: Use Pre-trained (Faster)**
- Load existing `deathmatch_shotgun.pth`
- Run in evaluation mode (no training)
- Collect metrics as-is
- **Pros:** Fast, works immediately
- **Cons:** May not perform well on unique maps

**Option B: Fine-tune (Better Results)**
- Load pre-trained model
- Continue training on new map for 1000-5000 steps
- Use same hyperparameters as original training
- **Pros:** Better adaptation, higher completion rates
- **Cons:** 30-60 minutes per map (GPU required)

**Recommendation:** Start with Option A, add Option B later

---

## IMPLEMENTATION ROADMAP (40-50%)

### Minimum Viable Product (7 days)

#### Day 1: Setup
- Install PostgreSQL, create database
- Setup Python venv, install dependencies
- Verify Arnold agent runs
- Create project folder structure

#### Day 2: Database Layer
- Create SQLAlchemy models (maps, runs, events, metrics)
- Write `init_db.py` script
- Implement CRUD operations in `db_ops.py`
- Test with dummy data

#### Day 3: Agent Integration
- Modify `src/doom/game.py` for custom maps
- Create `metrics_collector.py`
- Build `run_map.py` orchestration script
- Test on 1 sample map

#### Day 4: Analysis & Queries
- Implement bug detection algorithms
- Create hardness score calculator
- Build `query_api.py` with 5 key queries
- Test queries on 3 maps

#### Day 5: Visualization
- Create `visualizer.py` with matplotlib
- Generate health timeline plots
- **Framework Core (Engine-Agnostic):**  
  - Database schema implemented and tested  
  - Metrics collection pipeline functional  
  - Bug detection algorithms working  
  - Hardness score calculation validated  
  - Query API returns correct results  
  - Timeline visualization generated  

✅ **Showcase Implementation (Doom):**  
  - Agent runs on custom Doom maps  
  - Tested on 5+ diverse .wad files  
  - All metrics stored correctly in DB  
  - Comparative queries functional  

✅ **Generalizability Demonstration:**  
  - Architecture documented with adapter pattern  
  - 70%+ of code is engine-independent (verified)  
  - Extension roadmap to Unity/Unreal documented  
  - Design patterns enable easy porting

#### Day 7: Documentation & Polish
- Add code comments
- Create README with usage examples
- Capture screenshots for deliverable
- Clean up repo

### Success Criteria for 40-50%
✅ Database schema implemented and tested  
✅ Agent runs on custom maps (no training needed)  
✅ Metrics collected and stored correctly  
✅ Bug detection works on sample bugs  
✅ Hardness score calculated  
✅ Basic timeline plot generated  
✅ At least 3 queries functional  
✅ Tested on 5+ maps successfully

---

## USER WORKFLOWS

### Workflow 1: Test a New Map
```bash
# 1. Add map to database
python db_ops.py add-map --path ./maps/custom.wad --name "Custom Arena"

# 2. Run test (5 episodes)
python agent/run_map.py --map-id custom_arena --episodes 5

# 3. View results
python queries/query_api.py --map-id custom_arena --stats

# 4. Generate visualization
python visualization/visualizer.py --map-id custom_arena --output ./plots/
```

### Workflow 2: Compare Maps
```bash
# Compare two maps
python queries/query_api.py --compare map_a map_b

# Output:
# Map A: Hardness=65, Deaths=12, Solvable=Yes
# Map B: Hardness=42, Deaths=7, Solvable=Yes
# Verdict: Map A is 55% harder than Map B
```

### Workflow 3: Find Problematic Maps
```bash
# Find all unsolvable maps
python queries/query_api.py --unsolvable

# Find maps with critical bugs
python queries/query_api.py --bugs --severity critical
```

---

## DATA FLOW EXAMPLES

### Example 1: Single Map Test Run

**Input:**
```json
{
  "map_id": "arena_x1",
  "map_path": "/maps/arena_x1.wad",
  "episodes": 5,
  "agent_model": "deathmatch_shotgun.pth"
}
```

**Processing:**
1. Load map into VizDoom
2. Initialize Arnold agent with model
3. For each episode (1-5):
   - Reset environment
   - Run until death/completion/timeout
   - Collect frame data (2100 frames max)
   - Store events in memory
4. Aggregate metrics across episodes
5. Detect bugs in event timeline
6. Calculate hardness score
7. Insert into database

**Database Inserts:**
```sql
-- Insert map (if new)
INSERT INTO maps (id, name, file_path) VALUES ('arena_x1', 'Arena X1', '/maps/arena_x1.wad');

-- Insert run
INSERT INTO runs (map_id, started_at, finished_at, outcome) 
VALUES ('arena_x1', '2026-01-28 10:00', '2026-01-28 10:15', 'completed');
-- Returns run_id = 123

-- Insert 10500 events (5 episodes × 2100 frames)
INSERT INTO events (run_id, episode_index, time_step, event_type, value) VALUES
  (123, 1, 542, 'death', '{"health": 0}'),
  (123, 1, 1200, 'ammo_pickup', '{"ammo": 50}'),
  ... (10,500 rows total)

-- Insert aggregated metrics
INSERT INTO metrics (run_id, total_deaths, total_steps, hardness_score, is_solvable, bugs_detected) 
VALUES (123, 12, 10500, 67.5, true, '{"stuck": 2, "instant_death": 1}');
```

**Output:**
```json
{
  "run_id": 123,
  "map_id": "arena_x1",
  "outcome": "completed",
  "metrics": {
    "deaths": 12,
    "steps": 10500,
    "avg_health": 45.2,
    "hardness_score": 67.5,
    "is_solvable": true
  },
  "bugs": [
    {"type": "stuck", "count": 2, "severity": "medium"},
    {"type": "instant_death", "count": 1, "severity": "critical"}
  ],
  "timeline_plot": "/outputs/plots/arena_x1_run123.png"
}
```

---

## EDGE CASES & ERROR HANDLING

### 1. Map Loading Failures
**Scenario:** .wad file corrupted or invalid format  
**Handling:**
```python
try:
    game = load_custom_map(wad_path)
except Exception as e:
    log_error(f"Map load failed: {e}")
    mark_map_as_invalid(map_id)
    return {"error": "Invalid map file"}
```

### 2. Agent Crashes
**Scenario:** Agent code throws exception during gameplay  
**Handling:**
```python
try:
    episode_result = agent.run_episode(game)
except Exception as e:
    log_crash(e)
    insert_run(outcome='crashed', error_log=str(e))
    return {"outcome": "crashed", "partial_data": metrics_so_far}
```

### 3. Timeout Handling
**Scenario:** Agent stuck in infinite loop, never completes  
**Handling:**
```python
MAX_STEPS = 2100  # ~2 minutes at 35 FPS
for step in range(MAX_STEPS):
    if game.is_episode_finished():
        break
    agent.step()
else:
    # Timeout reached
    insert_run(outcome='timeout')
    metrics.is_solvable = False
```

### 4. Database Connection Loss
**Scenario:** PostgreSQL server down during run  
**Handling:**
```python
# Use transaction with retry
@retry(max_attempts=3, delay=5)
def insert_with_retry(data):
    session = get_db_session()
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        session.rollback()
        raise
```

### 5. Zero-Length Episodes
**Scenario:** Agent dies instantly on spawn  
**Handling:**
```python
if episode_steps < 10:
    # Suspicious instant death
    bugs.append({
        'type': 'spawn_death',
        'severity': 'critical',
        'description': 'Agent died within 10 frames of spawn'
    })
```

---

## FUTURE ENHANCEMENTS (Beyond 40-50%)

### Phase 2 (50-70%)
- **Web Dashboard:** Flask app with Bootstrap UI
- **Real-time Monitoring:** WebSocket updates during tests
- **Batch Testing:** Run multiple maps in parallel
- **Report Export:** Generate PDF reports with all metrics

### Phase 3 (70-90%)
- **Cloud Deployment:** Docker + AWS/Azure
- **API Endpoints:** REST API for external integrations
- **Advanced Analytics:** ML-based bug prediction
- **Comparative Heatmaps:** Visualize agent paths across maps

### Phase 4 (90-100%)
- **Fine-tuning Pipeline:** Auto-train agent on new maps
- **Public Dashboard:** S (Current Implementation)
1. **Doom Implementation:** Proof-of-concept uses VizDoom (methodology is engine-agnostic)
2. **GPU Dependency:** Fine-tuning requires NVIDI

### Phase 5 (Research Extension - Beyond Graduation)
- **Engine Abstraction Layer:** Adapt to Unity/Unreal
- **Multi-Agent Testing:** Cooperative/competitive scenarios
- **Transfer Learning:** Reuse agents across game types
- **Benchmark Suite:** Standard test corpus for RL game testing researchA GPU (true for all RL approaches)
3. **Map Size Limit:** Large maps (>100MB) may timeout (configurable threshold)
4. **Agent Capability:** Arnold trained on specific scenarios, may fail on exotic maps
5. **Bug Detection Heuristics:** Not perfect, may miss subtle bugs or false positive

**Note:** Constraints #2-5 are inherent to RL-based testing regardless of game engine. Only #1 is implementation-specific.
## KNOWN LIMITATIONS
(at least 1 non-Doom)  
✅ 5+ UML diagrams (Use Case, Sequence, Activity, Class, ER)  
✅ Complete database schema with 4+ tables (engine-agnostic design)  
✅ GANTT chart with realistic timeline  
✅ Architecture diagram showing adapter pattern for generalizability  
✅ Clear distinction: research contribution vs. showcase implementation  
✅ Extension roadmap to Unity/Unreal documentedquires NVIDIA GPU
3. **Map Size Limit:** Large maps (>100MB) may timeout
4. **Agent Capability:** Arnold trained on specific scenarios, may fail on exotic maps
5. **Bug Detection Heuristics:** Not perfect, may miss subtle bugs or false positive

### Functional Limitations
1. **No Multi-player Testing:** Single agent only
2. **No Story/Puzzle Evaluation:** Focuses on combat/survival
3. **No Audio Analysis:** Visual state only
4. **Fixed Action Space:** Can't adapt to custom weapons/mechanics
5. **Manual Map Upload:** No auto-discovery of maps

### Resource Limitations
1. **Testing Speed:** 5-10 minutes per map (with GPU)
2. **Storage Growth:** 10,500 events per run = ~1MB/run
3. **Query Performance:** Large databases (1000+ maps) need indexing
4. **Visualization Time:** Complex plots take 10-30 seconds

---

## SUCCESS METRICS

### For Deliverable #1 (Documentation)
✅ 20+ page document covering all template sections  
✅ 3 Scopus-indexed academic papers cited  
✅ 5+ UML diagrams (Use Case, Sequence, Activity, Class, ER)  
✅ Complete database schema with 4+ tables  
✅ GANTT chart with realistic timeline  
✅ Supervisor approval of design  

### For Phase Implementation (40-50%)
✅ System tests 5+ maps successfully  
✅ Database stores all runs and metrics  
✅ Bug detection identifies at least 2 bug types  
✅ Hardness scores calculated correctly  
✅ Timeline visualization generated  
✅ 3+ queries return accurate results  
✅ Code documented and version controlled  

### For Full Project (100%)
✅ 50+ maps tested with results  
✅ Web dashboard deployed  
✅ Public demo accessible  
✅ Final documentation complete  
✅ Presentation prepared  
✅ Code released (GitHub/GitLab)  

---

## CONTEXT FOR OTHER Lfor showcase (VizDoom, PyTorch, PostgreSQL)
- **CRITICAL:** This is a research showcase, not a product
- **EMPHASIS:** Doom is proof-of-concept; methodology is the contribution
- **POSITIONING:** Framework is generalizable to any game engine
- Document must clearly communicate transferability and research value

### If You're Continuing This Project:

**What's Done:**
- Vision fully defined ✅
- Documentation plan created ✅
- Technical stack decided ✅
- Database schema designed ✅
- Algorithm pseudocode written ✅

**What's Next:**
1. **Start Day 1 of Documentation Plan** (see DOCUMENTATION_PLAN.md)
2. **Focus on academic paper research FIRST** (Task 10 - highest priority)
3. **Create diagrams as you go** (use draw.io or PlantUML)
4. **Don't start coding until document is 80% complete**

**Key Files:**
- `/media/steven/MaD/projects/grad-proj-final/DOCUMENTATION_PLAN.md` ← Execution steps
- `/media/steven/MaD/projects/grad-proj-final/PROJECT_VISION.md` ← This file
- `/media/steven/MaD/projects/grad-proj-final/mydoom-master-Arnold/` ← Existing agent code

**Important Context:**
- User prefers quality over speed (7-day timeline, not 2-day)
- Document submission is PRIORITY before coding
- Supervisor: Prof./Dr. Mohamed Taher
- User wants brutal honesty, no sugar-coating
- Tech stack is FIXED (VizDoom, PyTorch, PostgreSQL)

**Commands to Run:**
```bash
# Navigate to project
cd /media/steven/MaD/projects/grad-proj-final

# Check what's installed
python3 --version  # Should be 3.12+
psql --version     # Should be PostgreSQL 16+

# List existing Arnold code
ls -la mydoom-master-Arnold/Arnold/

# When coding starts:
# Create venv, install deps, init database
```

**User Communication Style:**
- Wants concise, direct answers
- Appreciates structured plans (todo lists, tables)
- Dislikes fluff or over-explanation
- Expects tools to be used proactively
- Values markdown links to files with line numbers

---

## FINAL NOTES

**This is a REAL graduation project with REAL deadlines.**
 (for THIS implementation)
- Add features beyond 40-50% scope without approval
- Skip academic research (3 papers REQUIRED)
- Start coding before documentation is 80% done
- Present this as Doom-only (it's a generalizable methodology)

**DO:**
- Follow DOCUMENTATION_PLAN.md sequentially
- Emphasize research contribution & generalizability in documentation
- Use existing Arnold code (don't rewrite from scratch)
- Keep database schema exactly as specified
- Generate visualizations as described
- Explain in docs WHY Doom was chosen (not a limitation, a strategic choice)UIRED)
- Start coding before documentation is 80% done

**DO:**
- Follow DOCUMENTATION_PLAN.md sequentially
- Ask questions when requirements are unclear
- Use existing Arnold code (don't rewrite from scratch)
- Keep database schema exactly as specified
- Generate visualizations as described

**If stuck, prioritize:**
1. Academic papers (most time-consuming)
2. UML diagrams (most visible in document)
3. Database design (foundation for code)
4. Architecture diagrams (shows big picture)
5. Everything else

---

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Status:** Vision Complete, Ready for Implementation  

**Next Action:** Start Task 1 of DOCUMENTATION_PLAN.md
