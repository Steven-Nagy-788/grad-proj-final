# GRADUATION PROJECT DELIVERABLE #1 - EXECUTION PLAN
**Deep RL Game Tester - Documentation Priority**

## TIMELINE: 3-4 DAYS FOR COMPLETE DOCUMENT

---

## DAY 1: FOUNDATION & RESEARCH (8-9 hours)

### Morning Session (4 hours)
**Priority: Core Document Structure**

#### Task 1: Section 1.1 - Problem Statement (30 min)
**Output:** 1-2 paragraphs
- Challenge 1: Manual map testing is time-consuming (100+ hours for 50 maps)
- Challenge 2: Human testers miss bugs, subjective difficulty assessment
- Proposed Solution: RL agent automates testing, objective metrics, bug detection
- Impact: 95% time reduction, consistent quality analysis

#### Task 2: Section 1.2 - System Overview (45 min)
**Output:** System diagram + 1 paragraph description
- **Diagram Components:**
  ```
  [Custom Doom Map (.wad)]
         ↓
  [VizDoom Engine]
         ↓
  [Arnold RL Agent (DQN)]
         ↓
  [Metrics Extraction]
         ↓
  [PostgreSQL Database]
         ↓
  [Query API] → [Visualization Dashboard]
  ```
- Use: draw.io, Lucidchart, or PowerPoint
- Export as high-res PNG (300dpi)

#### Task 3: Section 1.3 - Scope & Limitations (30 min)
**Output:** Bullet lists
- **Scope:**
  - Technologies: VizDoom, PyTorch, PostgreSQL, Python 3.12
  - Functionalities: Automated testing, bug detection, hardness scoring, comparative analysis
  - Target: Custom Doom maps (.wad format)
- **Limitations:**
  - Requires pre-trained RL agent (Arnold)
  - GPU recommended (training: 30-60 min/map)
  - Doom engine only (not generalizable to other games)
  - Max map size: 50MB

#### Task 4: Section 1.4 - Objectives (30 min)
**Output:** SMART goals table
| Objective | Metric | Target |
|-----------|--------|--------|
| Testing Speed | Maps/hour | 10+ maps (vs 0.5 manual) |
| Bug Detection | Accuracy | 95%+ |
| Hardness Score | Range | 0-100 normalized |
| Cross-map Comparison | Query time | <2 seconds |
| Timeline Generation | Resolution | Frame-by-frame |

#### Task 5: Section 1.5 - Stakeholders (20 min)
**Output:** Stakeholder diagram + list
- **Primary:**
  - Game Developers (use for QA)
  - QA Teams (automated testing)
- **Secondary:**
  - Map Creators (difficulty validation)
  - Researchers (RL in gaming)
- Draw circle diagram showing relationships

---

### Afternoon Session (4-5 hours)
**Priority: Planning & Research**

#### Task 6: Section 1.6.1 - GANTT Chart (1 hour)
**Output:** Project timeline chart
- **Use:** ProjectLibre, Excel, or Smartsheet
- **Phases:**
  - Week 1-2: Requirements + Research + Design
  - Week 3-4: Database + Agent Integration
  - Week 5-6: Testing + Visualization
  - Week 7-8: Integration + Documentation
- Show dependencies between tasks
- Export as image

#### Task 7: Section 1.6.2 - Budget (20 min)
**Output:** Budget table
| Item | Cost | Justification |
|------|------|---------------|
| GPU Server (cloud) | $200/mo | Training agent |
| PostgreSQL Hosting | $50/mo | Database |
| Development Tools | $0 | Open source |
| **Total** | **$250-300** | 2-month project |

#### Task 8: Section 2 - Methodology (30 min)
**Output:** 2 paragraphs + tools list
- **Methodology:** Agile with 2-week sprints
- **Tools:**
  - Version Control: Git + GitHub
  - Development: Python 3.12, VS Code
  - Database: PostgreSQL 16
  - RL: PyTorch, VizDoom
  - Visualization: Matplotlib, Plotly
  - Containerization: Docker

#### Task 9: Section 3.1 - Requirements Elicitation (20 min)
**Output:** 1 paragraph
- Techniques used:
  - Literature review (academic papers)
  - Competitor analysis (existing tools)
  - Prototyping (proof-of-concept)
- Stakeholders involved: Supervisor, game developers

#### Task 10: Section 3.2.1 - Academic Research (2 hours) ⚠️ **CRITICAL**
**Output:** 3 paper summaries (2-3 paragraphs each)
- **Search terms:**
  - "reinforcement learning game testing"
  - "automated bug detection video games"
  - "procedural content generation evaluation"
- **Required:** Scopus-indexed journals/conferences
- **Format for each paper:**
  - [1] Authors. (Year). Title. Journal/Conference.
  - Summary: Problem addressed, methodology, key findings
  - Relevance: How it relates to your project
- **Tools:** Google Scholar, IEEE Xplore, ACM Digital Library

#### Task 11: Section 3.2.2 - Market Research (1 hour)
**Output:** Comparison table + 2 paragraphs
| System | Strengths | Weaknesses | Our Advantage |
|--------|-----------|------------|---------------|
| Unity Test Framework | Integrated with Unity | Unity-only | Works with Doom |
| Unreal Automation Tool | Built-in profiling | Manual scripting | RL-based |
| GameBench | Performance metrics | No bug detection | Detects bugs |

---

## DAY 2: REQUIREMENTS & DIAGRAMS (8-9 hours)

### Morning Session (4-5 hours)
**Priority: Functional Requirements**

#### Task 12: Section 3.3.1 - System Functions (45 min)
**Output:** Prioritized requirement list (12-15 items)
- **Must-have:**
  - FR01: System must load custom .wad map files
  - FR02: System must run RL agent on loaded map
  - FR03: System must track agent deaths, steps, health
  - FR04: System must detect bugs (stuck, instant death)
  - FR05: System must store results in PostgreSQL
  - FR06: System must calculate hardness score (0-100)
- **Should-have:**
  - FR07: System should support multiple episodes per map
  - FR08: System should generate timeline visualizations
  - FR09: System should enable cross-map queries
- **Could-have:**
  - FR10: System could export PDF reports
  - FR11: System could support real-time monitoring

#### Task 13: Section 3.3.2 - Detailed FR Tables (1.5 hours)
**Output:** 8 detailed requirement tables
- **Template for each:**
  ```
  FR01 | Load Custom Map
  Description: System accepts .wad file path and loads map into VizDoom
  Input: Map file path (string)
  Output: Game environment instance
  Priority: Must-have
  Pre-condition: File exists and is valid .wad format
  Post-condition: Map loaded, agent ready to spawn
  ```

#### Task 14: Use Case Diagram (1 hour)
**Output:** UML Use Case diagram
- **Actors:**
  - Developer
  - QA Tester
  - System Admin
- **Use Cases (8+):**
  - Upload Map
  - Run Test
  - View Results
  - Compare Maps
  - Generate Report
  - Configure Agent
  - Query Database
  - Export Data
- Use draw.io or PlantUML

---

### Afternoon Session (4 hours)
**Priority: Behavioral & Domain Modeling**

#### Task 15: Sequence Diagrams (1.5 hours)
**Output:** 2 sequence diagrams
- **Diagram 1: Map Testing Flow**
  - User → System: Upload map
  - System → VizDoom: Load map
  - System → Agent: Initialize
  - Agent ↔ VizDoom: Play episodes (loop)
  - Agent → System: Return metrics
  - System → Database: Store results
  - System → User: Display summary

- **Diagram 2: Query & Visualization**
  - User → API: Request map stats
  - API → Database: Query runs
  - Database → API: Return data
  - API → Visualizer: Generate plot
  - Visualizer → User: Display timeline

#### Task 16: Activity Diagram (45 min)
**Output:** Testing pipeline activity diagram
- **Flow:**
  - START
  - Load map
  - Initialize agent
  - Decision: Episodes complete?
    - No: Run episode → Collect metrics → Loop
    - Yes: Analyze results
  - Detect bugs
  - Calculate hardness
  - Store in database
  - Generate visualization
  - END

#### Task 17: Domain Class Diagram (1 hour)
**Output:** Abstract class diagram
- **Classes:**
  - Map (id, name, path, size)
  - TestRun (id, map_id, timestamp, outcome)
  - Episode (id, run_id, index, duration)
  - Event (id, episode_id, time, type, data)
  - Metric (id, run_id, deaths, score)
  - Bug (id, run_id, type, severity)
- **Relationships:**
  - Map 1→N TestRun
  - TestRun 1→N Episode
  - Episode 1→N Event

#### Task 18: Non-Functional Requirements (30 min)
**Output:** NFR list with metrics
- **Security:** Role-based access, encrypted DB connection
- **Reliability:** 99% uptime, crash recovery
- **Performance:** <10 min per map, <2s query response
- **Usability:** Simple API, clear error messages
- **Maintainability:** Modular design, documented code
- **Portability:** Docker containers, cross-platform

---

## DAY 3: DESIGN & ARCHITECTURE (7-8 hours)

### Morning Session (4 hours)
**Priority: System Design**

#### Task 19: Architecture Diagram (1 hour)
**Output:** Layered architecture diagram
- **Presentation Layer:**
  - REST API (Flask)
  - Web Dashboard (Optional)
  - CLI Interface
- **Business Logic Layer:**
  - Agent Runner
  - Metrics Collector
  - Bug Detector
  - Hardness Calculator
  - Query Engine
- **Data Layer:**
  - PostgreSQL Database
  - File Storage (maps, plots)

#### Task 20: Database Design (1.5 hours)
**Output:** ER diagram + SQL schema
- **Tables:**
  ```sql
  maps (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200),
    file_path VARCHAR(500),
    size_kb INT,
    created_at TIMESTAMP
  )
  
  runs (
    id SERIAL PRIMARY KEY,
    map_id VARCHAR(50) REFERENCES maps(id),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    outcome VARCHAR(50), -- 'completed', 'timeout', 'crashed'
    episodes_count INT
  )
  
  events (
    id SERIAL PRIMARY KEY,
    run_id INT REFERENCES runs(id),
    episode_index INT,
    time_step INT,
    event_type VARCHAR(50), -- 'death', 'health_change', 'stuck'
    value JSONB
  )
  
  metrics (
    id SERIAL PRIMARY KEY,
    run_id INT REFERENCES runs(id),
    total_deaths INT,
    total_steps INT,
    avg_health FLOAT,
    hardness_score FLOAT,
    is_solvable BOOLEAN
  )
  ```
- Draw ER diagram showing relationships

#### Task 21: Design Class Diagram (1 hour)
**Output:** Detailed class diagram with methods
- **Classes:**
  ```
  MapLoader
    +load(path: str) -> GameEnv
    +validate(path: str) -> bool
  
  AgentRunner
    +run_episode(env: GameEnv) -> Episode
    +configure(model: str) -> None
  
  MetricsCollector
    +track_frame(state: dict) -> None
    +get_summary() -> dict
  
  BugDetector
    +detect_stuck(positions: list) -> bool
    +detect_instant_death(health: list) -> bool
  
  DatabaseManager
    +insert_run(data: dict) -> int
    +query_map(id: str) -> dict
  
  Visualizer
    +plot_timeline(data: dict) -> Image
    +export_report(data: dict) -> PDF
  ```

---

### Afternoon Session (3-4 hours)
**Priority: Algorithms & Patterns**

#### Task 22: Algorithm Viewpoint (45 min)
**Output:** Pseudocode for 2 algorithms
- **Algorithm 1: Bug Detection**
  ```
  FUNCTION detect_bugs(events):
    bugs = []
    
    // Stuck Detection
    positions = extract_positions(events)
    for i in range(100, len(positions)):
      if positions[i-100:i] are all same:
        bugs.append({'type': 'stuck', 'time': i})
    
    // Instant Death Detection
    health = extract_health(events)
    for i in range(1, len(health)):
      if health[i-1] > 80 AND health[i] == 0:
        bugs.append({'type': 'instant_death', 'time': i})
    
    return bugs
  ```

- **Algorithm 2: Hardness Calculation**
  ```
  FUNCTION calculate_hardness(metrics):
    death_score = normalize(metrics.deaths, 0, 50) * 0.35
    time_score = normalize(metrics.time, 0, 2100) * 0.25
    health_loss = 1 - normalize(metrics.avg_health, 0, 100) * 0.20
    stuck_score = normalize(metrics.stuck_count, 0, 10) * 0.20
    
    hardness = death_score + time_score + health_loss + stuck_score
    return round(hardness * 100)  // Scale to 0-100
  ```

#### Task 23: Design Patterns (30 min)
**Output:** Pattern usage list
- **Singleton:** Database connection pool (ensure one instance)
- **Factory:** Map loader (create different game environments)
- **Observer:** Event tracking (notify collectors on game state change)
- **Strategy:** Hardness calculation (switch between formulas)
- **Repository:** Database operations (abstract DB access)

#### Task 24: Data/Dataset Description (30 min)
**Output:** Dataset table
| Property | Details |
|----------|---------|
| Dataset Name | Custom Doom Map Test Suite |
| Source | idgames archive + custom created |
| Size | 50 maps, ~500MB total |
| Format | .wad (Doom WAD format) |
| Categories | Easy (15), Medium (20), Hard (15) |
| Features | Varied layouts, enemy counts, item placements |
| Usage | Training and evaluation of RL agent |

#### Task 25: Implementation Section (15 min)
**Output:** Placeholder text
- "Implementation is in progress. The following components are under development:"
- List: Agent integration, database layer, visualization module
- "Screenshots and detailed results will be provided in Deliverable #2"

#### Task 26: Appendices (30 min)
**Output:** Glossary + acronyms
- **Glossary:**
  - Reinforcement Learning (RL): AI technique where agent learns by trial and error
  - DQN: Deep Q-Network, value-based RL algorithm
  - VizDoom: Doom-based RL research platform
  - WAD: Where's All the Data, Doom map file format
- **Acronyms:**
  - FR: Functional Requirement
  - NFR: Non-Functional Requirement
  - API: Application Programming Interface
  - ER: Entity-Relationship

---

## DAY 4: FINALIZATION (4-5 hours)

### Final Tasks

#### Task 27: References (45 min)
**Output:** Formatted reference list (IEEE or APA)
- Use Mendeley or Zotero
- Include:
  - 3 academic papers (from Task 10)
  - VizDoom documentation
  - PyTorch documentation
  - Arnold GitHub repository
  - PostgreSQL documentation
- **Format example (IEEE):**
  ```
  [1] A. Smith et al., "Automated Testing of Game Levels Using RL,"
      IEEE Trans. Games, vol. 12, no. 3, pp. 234-245, 2024.
  ```

#### Task 28: Proofread & Format (1 hour)
**Checklist:**
- [ ] All sections numbered correctly
- [ ] All figures captioned (Figure 1: ...)
- [ ] All tables captioned (Table 1: ...)
- [ ] Table of contents matches sections
- [ ] Page numbers correct
- [ ] Grammar check (Grammarly)
- [ ] Consistent font (Times New Roman 12pt)
- [ ] 1.5 line spacing
- [ ] References formatted consistently

#### Task 29: Export PDF (15 min)
- Export from Word/LaTeX
- Check image quality
- Verify file size <10MB
- Test PDF opens correctly
- Final filename: `DeepRL_GameTester_Deliverable1_<YourName>.pdf`

---

## TOTAL TIME BREAKDOWN

| Day | Hours | Focus |
|-----|-------|-------|
| Day 1 | 8-9 | Foundation + Research |
| Day 2 | 8-9 | Requirements + Diagrams |
| Day 3 | 7-8 | Design + Architecture |
| Day 4 | 4-5 | Finalization |
| **Total** | **27-31 hours** | **Complete Document** |

---

## CRITICAL SUCCESS FACTORS

### ⚠️ **BLOCKERS TO AVOID**
1. **Academic Papers:** Start searching EARLY (Day 1). If stuck, ask supervisor for recommendations.
2. **Diagrams:** Use simple tools (draw.io). Don't waste time on perfect aesthetics.
3. **Scope Creep:** Stick to the template. Don't add extra sections.

### ✅ **QUALITY CHECKERS**
- [ ] Problem statement is clear (1-2 key challenges)
- [ ] All diagrams are high-resolution and labeled
- [ ] GANTT chart shows realistic timeline
- [ ] 3 academic papers are Scopus-indexed
- [ ] All functional requirements have detailed tables
- [ ] Database schema includes 4+ tables
- [ ] Architecture diagram shows 3 layers
- [ ] References formatted consistently

### 🚀 **PRODUCTIVITY HACKS**
1. **Templates:** Create diagram templates on Day 1, reuse for all diagrams
2. **Parallel Work:** While searching papers (2 hours), take breaks to draw simple diagrams
3. **Don't Overthink:** First draft > Perfect draft. Iterate later.
4. **Ask for Help:** If stuck on any section >30 min, ask supervisor/peers

---

## DELIVERABLE CHECKLIST

### Before Submission:
- [ ] Cover page with team names, supervisor, date
- [ ] Table of contents auto-generated
- [ ] All 7 sections complete
- [ ] Minimum 20 pages (excluding cover/TOC)
- [ ] All figures numbered and referenced in text
- [ ] All tables numbered and referenced in text
- [ ] References section complete (8+ sources)
- [ ] Appendices included
- [ ] PDF exported and tested
- [ ] File named correctly
- [ ] Submitted before deadline

---

## NEXT PHASE: DELIVERABLE #2 (After Document Approved)

**Code Implementation (40-50% of system):**
1. Database setup + models (Day 1-2)
2. Agent integration (Day 3-4)
3. Basic testing pipeline (Day 5-6)
4. Simple visualization (Day 7)

**This document is your CONTRACT with the supervisor. Stick to this plan.**
