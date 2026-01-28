# Faculty of Computing and Information Sciences
# Graduation Project Deliverable #1

---

# **Autonomous Quality Assurance for Game Levels Using Deep Reinforcement Learning: A Framework Demonstration**

## **Team Members:**

| Student ID | Student Name | Track |
|------------|--------------|-------|
|            |              |       |
|            |              |       |
|            |              |       |

**Supervised by:** Prof./Dr. Mohamed Taher  
**Mentored by:** (if existed)

**Date:** January 28, 2026

---

## Table of Contents

1. System Description
   1.1. Problem Statement
   1.2. System Overview
   1.3. System Scope and Limitations
   1.4. System Objectives
   1.5. Stakeholders
   1.6. Project Planning and Management
      1.6.1. Project Timeline Revisited
      1.6.2. Preliminary Budget Adjusted
2. System Development Process/Methodology
3. Requirements Engineering
   3.1. Requirements Elicitation Techniques
   3.2. Similar Systems
      3.2.1. Academic Scientific Research
      3.2.2. Market/Industrial Research
   3.3. Functional Requirements
      3.3.1. System Functions
      3.3.2. Detailed Functional Specification
      3.3.3. Behavioural Modelling
      3.3.4. Domain/Data Modelling
   3.4. Non-functional Requirements
4. System Design
   4.1. Composition/Architectural Viewpoint
   4.2. Database Design
   4.3. Design Classes and Methods
   4.4. Algorithm Viewpoint
   4.5. Patterns Use Viewpoint
5. Data Design
   5.1. Data Description
   5.2. Dataset Description
6. Implementation
7. Appendices
8. References

---

# 1. System Description

## 1.1. Problem Statement

The video game industry faces a persistent and costly challenge in quality assurance: **manual testing of game levels is time-intensive, subjective, and error-prone**, regardless of game engine or genre. This problem manifests across multiple dimensions:

### **Challenge 1: Scalability and Time Constraints**

Traditional manual testing requires human QA testers to repeatedly play through game levels to identify bugs, assess difficulty balance, and validate playability. This process is inherently time-consuming and scales poorly with modern game development demands:

- **Procedural content generation** creates thousands of unique levels requiring validation before player exposure
- **Live-service games** release new content on accelerated schedules, demanding rapid QA turnaround times
- **Independent developers** often lack resources for dedicated QA teams, leading to insufficiently tested content reaching end-users
- **Iterative design** becomes constrained when each modification necessitates complete manual re-testing cycles

Manual testing represents a substantial resource investment in game development pipelines, creating bottlenecks in production schedules and constraining development budgets. Contemporary research indicates that "manual approaches towards game testing are still widely used" across the industry despite their inherent limitations [1].

### **Challenge 2: Subjectivity and Inconsistency**

Human testers provide subjective assessments of game difficulty and quality that exhibit significant variability due to:

- Individual skill levels and prior gaming experience
- Cognitive fatigue and attention degradation during extended testing sessions
- Personal biases, expectations, and gameplay preferences
- Absence of standardized, quantitative metrics for difficulty assessment

This inherent subjectivity prevents reliable cross-level comparisons and impedes data-driven design decisions. Different testers frequently provide inconsistent evaluations of identical content, yielding unreliable feedback for iterative refinement.

### **Challenge 3: Incomplete Coverage and Bug Detection**

Human testers face fundamental cognitive and temporal limitations in exhaustively exploring gameplay state spaces and edge cases. Manual testing provides inherently incomplete coverage:

- Limited exploration of non-obvious gameplay paths and interaction sequences
- Inability to systematically test all permutations of player actions and environmental states
- Cognitive blind spots that allow bugs to persist undetected until discovered by end-users
- Time constraints that force selective rather than comprehensive testing strategies

These limitations result in critical bugs remaining latent in shipped products, negatively impacting player experience, review scores, and commercial success. Recent taxonomic analysis of game defects identified 63 distinct bug categories across eight major fault types, demonstrating the complexity and diversity of quality issues that manual testing must address [1].

---

### **Proposed Solution: RL-Based Automated Testing Framework**

This project presents a **generalizable framework for automated game level testing using Deep Reinforcement Learning agents**, demonstrated through a Doom implementation as proof-of-concept. The core methodology addresses the identified challenges through systematic automation:

**Addressing Challenge 1 (Scalability):** RL agents execute autonomous level testing without human intervention, enabling parallel testing workflows and continuous integration pipelines. Agents operate at computational speeds orders of magnitude faster than real-time human gameplay, substantially reducing testing cycle durations.

**Addressing Challenge 2 (Objectivity):** The framework generates quantitative, deterministic metrics including precise event counts, temporal measurements, resource consumption patterns, and algorithmically computed difficulty scores on normalized scales. These objective measurements enable consistent cross-level comparisons and evidence-based design iteration.

**Addressing Challenge 3 (Coverage):** Automated agents can execute thousands of gameplay iterations, systematically exploring state spaces through stochastic policies. Algorithmic analysis of gameplay telemetry identifies anomalous patterns indicative of bugs (stuck states, anomalous state transitions, unreachable regions) with detection capabilities beyond manual testing constraints. Prior research demonstrates that RL-based agents can achieve bug-finding performance competitive with human testers while providing exhaustive coverage [2].

---

### **Research Contribution and Generalizability**

While this implementation utilizes Doom via the VizDoom platform as the research testbed—selected for its mature RL tooling ecosystem, availability of pre-trained agents, and extensive research precedent in the RL community—**the core methodology is engine-agnostic and architecturally transferable to contemporary game engines** including Unity, Unreal Engine, Godot, and proprietary platforms. This approach addresses the industry need for advanced testing strategies, as "the increasing complexity of video games is pushing the limits of scripted solutions, necessitating the adoption of more advanced testing strategies" [3]. 

The framework employs a modular architecture with clear separation between:
- **Game engine adapters** (implementation-specific interface layer)
- **Core testing logic** (engine-independent analysis and orchestration)
- **Data infrastructure** (fully generalizable database schema and query system)

Preliminary architectural analysis of the Arnold agent codebase indicates that engine-specific code (doom interaction modules) constitutes approximately **39%** of the total implementation (2,489 lines of doom-specific code out of 4,005 total lines in src/), suggesting that **approximately 61% of existing infrastructure is directly reusable** for alternative game engine adaptations. This modular separation enables systematic extension to additional platforms through targeted adapter development while preserving the majority of analytical and infrastructure components.

This research demonstrates the technical feasibility and practical viability of RL-based automated game testing, providing a methodological blueprint applicable across diverse game engines and genres. The system addresses a critical gap between academic RL research and applied game development requirements, offering evidence-based validation for AI-powered quality assurance adoption in production environments.

---

**Formal Problem Statement:**

*How can we develop an automated, objective, and scalable framework for game level quality testing that substantially reduces QA cycle duration, provides quantitative difficulty metrics with inter-rater reliability, systematically detects bugs through telemetry analysis, and maintains architectural generalizability across multiple game engine platforms?*

---

## References (Preliminary)

[1] N. A. Butt, S. Sherin, M. U. Khan, A. A. Jilani, and M. Z. Iqbal, "Deriving and Evaluating a Detailed Taxonomy of Game Bugs," arXiv:2311.16645 [cs.SE], Nov. 2023. [Online]. Available: https://arxiv.org/abs/2311.16645

[2] S. Arıyürek, A. Betin-Can, and E. Sürer, "Automated Video Game Testing Using Synthetic and Humanlike Agents," IEEE Transactions on Games, vol. 13, no. 1, pp. 50-67, Mar. 2021, doi: 10.1109/TG.2019.2947597.

[3] V. Mastain and F. Petrillo, "BDD-Based Framework with RL Integration: An approach for videogames automated testing," arXiv:2311.03364 [cs.SE], Oct. 2023. [Online]. Available: https://arxiv.org/abs/2311.03364

---
