# RESEARCH REQUIREMENTS - CITATIONS NEEDED

## CRITICAL: All Quantitative Claims Must Be Cited

### Claims in Current Document That Need Research

#### Section 1.1 - Problem Statement

| Claim | Current Text | Status | Source Needed |
|-------|--------------|--------|---------------|
| Manual testing time | "100+ hours for 50 maps" | ❌ UNVERIFIED | Game dev industry report, academic paper, or case study |
| QA percentage | "30-40% of development timelines and budgets" | ❌ UNVERIFIED | Game industry survey, ESA report, GDC survey |
| Testing speed | "10+ maps per hour vs 0.5 manual" | ❌ UNVERIFIED | Benchmark study or calculate from Arnold performance |
| Time reduction | "95% time reduction" | ❌ UNVERIFIED | Derived from verified testing speeds |
| Bug miss rate | "15-30% of significant bugs" | ❌ UNVERIFIED | Software testing research, QA studies |
| Code reusability | "70% of codebase reusable" | ❌ UNVERIFIED | Calculate from actual architecture (can measure) |

---

## RESEARCH TASKS (Priority Order)

### Task 1: Game Industry QA Statistics (HIGH PRIORITY)
**Search for:**
- GDC (Game Developers Conference) QA surveys
- ESA (Entertainment Software Association) industry reports
- IGDA (International Game Developers Association) studies
- Gamasutra/Game Developer Magazine articles with QA data

**Keywords:**
- "game development QA time percentage"
- "video game testing cost statistics"
- "game QA budget allocation"

**Look for:**
- Industry-standard QA/testing time allocation
- Cost breakdowns in game development
- Manual testing time benchmarks

**Expected sources:**
- [1] GDC State of the Industry Survey (annual)
- [2] ESA Essential Facts report
- [3] Academic papers on game development methodologies

---

### Task 2: Software Testing Bug Detection Rates (HIGH PRIORITY)
**Search for:**
- Software engineering testing research
- QA effectiveness studies
- Bug detection rate analysis

**Keywords:**
- "manual testing bug detection rate"
- "software QA effectiveness metrics"
- "human tester error rate"

**Look for:**
- Percentage of bugs missed by manual testing
- Comparison: manual vs automated testing
- Human cognitive limitations in testing

**Expected sources:**
- IEEE Software journals
- ACM SIGSOFT papers
- Software Testing & Quality Assurance research

---

### Task 3: RL Agent Performance Benchmarks (MEDIUM PRIORITY)
**Search for:**
- VizDoom benchmark studies
- Arnold agent performance papers
- RL testing speed comparisons

**Keywords:**
- "VizDoom agent performance"
- "reinforcement learning game testing speed"
- "Arnold DQN benchmark"

**Look for:**
- Steps per second / FPS of RL agents
- Episode completion times
- Training vs inference speed

**Expected sources:**
- VizDoom competition papers
- Arnold GitHub repo documentation
- RL benchmarking studies

**Alternative:** Run actual benchmarks on Arnold agent to get MEASURED data

---

### Task 4: Code Reusability Analysis (LOW PRIORITY - Can Calculate)
**Action:** Analyze actual codebase structure
- Count lines in engine-specific vs generic modules
- Calculate percentage of adapter layer vs core framework
- Document which components are portable

**Method:**
```bash
# Count lines in adapter code
cloc src/doom/  # Engine-specific

# Count lines in core framework
cloc database/ queries/ visualization/  # Generic

# Calculate ratio
```

This can be MEASURED, not cited.

---

### Task 5: Testing Time Benchmarks (MEDIUM PRIORITY)
**Search for:**
- Game level testing case studies
- QA workflow time studies
- Manual playtesting duration research

**Keywords:**
- "game level testing duration"
- "QA playtesting time per level"
- "video game testing workflow"

**Look for:**
- Average time to test one game level manually
- QA tester productivity metrics
- Industry standards for level testing

**Alternative:** Interview game developers or cite supervisor's industry experience

---

## IMMEDIATE ACTIONS REQUIRED

### 1. Update DELIVERABLE_1.md
Replace all unverified numbers with:
- **[CITATION NEEDED]** tags
- Or conservative "Research indicates..." phrasing
- Or remove specific numbers until verified

### 2. Create Research Log
Track every claim → source mapping:
```
Claim: "X% of development time is QA"
Source: [Author, Year, "Title", Publisher]
Page/Section: Page 42, Figure 3
Confidence: High (industry survey, n=500 developers)
```

### 3. Build References Section
Use Mendeley/Zotero for proper citation management:
- IEEE or APA format (check with supervisor)
- Numbered references [1], [2], etc.
- Complete bibliographic info

---

## ALTERNATIVE APPROACHES (When Data Unavailable)

### Option A: Conservative Phrasing
Instead of: "30-40% of development time"
Use: "A significant portion of development time"

Instead of: "95% time reduction"
Use: "Substantial time reduction" or "Order of magnitude faster"

### Option B: Qualitative Claims
Instead of: "15-30% of bugs missed"
Use: "Human testers frequently miss edge-case bugs due to cognitive limitations"

### Option C: Measured Data
Instead of assumed benchmarks:
- Run Arnold agent 100 times, measure actual speed
- Time how long manual testing takes (ask developers)
- Calculate ACTUAL percentages from implementation

### Option D: Cite Supervisor
If supervisor has industry experience:
"According to industry practitioners [Personal Communication, Prof. Mohamed Taher, 2026], QA typically consumes..."

---

## CORRECTED PROBLEM STATEMENT (Conservative Version)

### Challenge 1: Scalability and Time Constraints

Traditional manual testing requires human QA testers to repeatedly play through game levels to identify bugs, assess difficulty balance, and validate playability. This process is **time-intensive and scales poorly** with modern game development demands:

- **Procedural content generation** creates numerous unique levels requiring validation
- **Live-service games** release new content frequently, demanding rapid QA turnaround  
- **Independent developers** often lack resources for dedicated QA teams
- **Iteration cycles** slow when design changes require complete re-testing

**[RESEARCH NEEDED: Industry survey data on QA time allocation]**

### Challenge 2: Subjectivity and Inconsistency

Human testers provide subjective assessments of game difficulty and quality that vary based on individual skill levels, fatigue, cognitive biases, and expectations. This subjectivity prevents objective cross-level comparisons and makes data-driven design decisions difficult.

**[RESEARCH NEEDED: Studies on inter-rater reliability in game testing]**

### Challenge 3: Incomplete Bug Detection

Human testers cannot exhaustively explore all possible gameplay paths and edge cases. Critical bugs may remain undetected until discovered by end-users, damaging player experience and game reviews.

**[RESEARCH NEEDED: Bug detection rate studies in manual vs automated testing]**

---

## ACTION PLAN

1. **TODAY:** Mark all unverified claims in DELIVERABLE_1.md
2. **Day 1 of Research:** Find 3 academic papers (Task 10 in DOCUMENTATION_PLAN.md) - ensure they include relevant statistics
3. **Day 1 Evening:** Search for industry reports (GDC, ESA, IGDA)
4. **Day 2:** Run actual benchmarks on Arnold agent to get measured performance data
5. **Day 2:** Update document with cited claims, remove/rephrase unverified ones
6. **Before submission:** Every number has [citation] or is marked as preliminary estimate

---

## VERIFICATION CHECKLIST

Before document submission:
- [ ] Every percentage has a citation: "X% [Author, Year]"
- [ ] Every time estimate has a source or is labeled "estimated"
- [ ] Every performance claim is backed by benchmark data
- [ ] Every industry statistic cites a report/survey
- [ ] All citations are in References section
- [ ] No "placeholder" numbers remain

---

**LESSON LEARNED:** Academic rigor demands evidence, not assumptions. This applies to ALL quantitative claims in the document.
