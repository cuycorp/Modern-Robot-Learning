# Modern Robot Learning: Team Onboarding Pack

**Version:** 0.2  
**Project Type:** Embodied AI / Modern Robot Learning Research Platform  
**Status:** Active Development / Architecture Under Review

---

# 1. Why this document exists

This document is the starting point for everyone contributing to the **Modern Robot Learning** project.

The project is a research platform for building practical knowledge of modern robotics through controlled experimentation.

Before implementing a new system, every contributor should understand:

1. The research question being investigated.
2. The robotics architecture being used.
3. The current phase and its scope.
4. How experiments are designed and evaluated.
5. How robot data is collected and managed.
6. How classical robotics connects to learned policies.
7. How results are documented and reproduced.

> **Rule:** Nobody implements a robotics system they cannot explain.

AI coding tools can accelerate development, but every contributor must understand, test, and be able to explain the resulting implementation.

---

# 2. Research Vision

## One-Sentence Pitch

A modular robotics research platform for learning and experimentally evaluating modern approaches to robot perception, manipulation, imitation learning, reinforcement learning, and embodied foundation models.

## Long-Term Vision

The project uses a physical robot as the central research platform and progressively introduces increasingly sophisticated capabilities:

```text
Classical Robot Control
        ↓
Reliable Manipulation
        ↓
Perception
        ↓
Teleoperation
        ↓
Dataset Collection
        ↓
Imitation Learning
        ↓
Simulation / Sim-to-Real
        ↓
VLA / Foundation Models
        ↓
Reinforcement Learning
```

The SO100/SO101 arms provide a relatively accessible physical platform for experimenting with this complete research loop.

Chess is the initial application because it provides:

- structured objects;
- repeatable manipulation tasks;
- clear success criteria;
- sequential decision making;
- a natural combination of perception, planning, and manipulation.

However, **the platform is not intended to become a chess-specific codebase**.

The underlying robotics and learning infrastructure should remain reusable for other manipulation tasks.

---

# 3. Research Philosophy

The project prioritizes:

```text
Understanding
      ↓
Controlled Experiments
      ↓
Reproducibility
      ↓
Measurement
      ↓
Research
      ↓
Iteration
```

A successful robot demonstration is useful, but it is not by itself a research result.

For each meaningful experiment we should be able to answer:

- What question were we asking?
- What was the hypothesis?
- What changed?
- What was measured?
- What happened?
- Why did it happen?
- What should we try next?

---

# 4. Current Project State

## Phase 0 — Foundations

**Status: Completed**

The team has already developed practical experience with:

- SO100 robotic arm;
- SO101 robotic arm;
- robot control scripts;
- basic manipulation;
- LeRobot;
- robot configuration and calibration;
- Rerun for visualization and debugging;
- LeRobot/LeLab ecosystem and tooling.

The project is therefore moving beyond basic robot setup.

The next objective is to transform this practical experience into a **controlled and measurable manipulation benchmark**.

---

# 5. Research Roadmap

```text
Phase 0 — Foundations
        ↓
Phase 1 — Manipulation
        ↓
Phase 2 — Perception
        ↓
Phase 3 — Teleoperation & Data
        ↓
Phase 4 — Imitation Learning
        ↓
Phase 5 — Simulation & Sim-to-Real
        ↓
Phase 6 — Foundation Models / VLA
        ↓
Phase 7 — Reinforcement Learning
```

The phases are sequential in terms of dependencies, but not necessarily strictly sequential in research exploration.

The architecture should allow components to be developed independently and connected when appropriate.

---

# 6. Phase 1 — Manipulation

## Status

**Current Phase**

## Goal

Build a **reliable, measurable, and reusable manipulation baseline** for the SO100/SO101.

The objective is no longer simply:

> "Can we make the robot pick something up?"

The objective is:

> **Can we characterize and improve the robot's ability to perform manipulation tasks reliably enough to serve as a baseline for future learning experiments?**

---

## Phase 1 Research Focus

Phase 1 isolates manipulation from perception.

Initially, the robot receives known object and target positions.

```text
Known object pose
        ↓
Motion primitives
        ↓
Robot controller
        ↓
SO100 / SO101
        ↓
Manipulation result
```

This allows manipulation failures to be studied independently of perception failures.

Later, perception will provide those positions:

```text
Camera
   ↓
Perception
   ↓
Object pose
   ↓
World model
   ↓
Manipulation
   ↓
SO100 / SO101
```

The interfaces between these systems should remain explicit.

---

# 7. Phase 1 Scope

## In Scope

### 1. Manipulation primitives

Develop reusable primitives such as:

```text
move_home
move_to
move_above
descend
grasp
lift
release
```

These primitives should be composed into higher-level tasks rather than implementing every experiment as a custom motion script.

---

### 2. Pick-and-place

Build a deterministic baseline:

```text
HOME
  ↓
MOVE ABOVE OBJECT
  ↓
DESCEND
  ↓
GRASP
  ↓
LIFT
  ↓
MOVE ABOVE TARGET
  ↓
DESCEND
  ↓
RELEASE
  ↓
LIFT
  ↓
HOME
```

The initial object can be a simple cube.

Chess pieces should be introduced only after the manipulation pipeline is sufficiently characterized.

---

### 3. Grasp evaluation

Study the conditions under which grasping succeeds or fails.

Variables may include:

- object position;
- approach position;
- approach height;
- gripper configuration;
- object geometry;
- object orientation;
- execution speed;
- small positional perturbations.

---

### 4. Motion primitives

Separate task-level logic from robot-level motion.

For example:

```text
pick_and_place()
    ↓
pick()
    ↓
move_above()
descend()
grasp()
lift()
    ↓
place()
    ↓
move_above()
descend()
release()
lift()
```

The same primitives should later be usable by both scripted systems and experimental learned-policy pipelines where appropriate.

---

### 5. Safety

Establish explicit safety constraints before increasing task complexity.

At minimum:

```text
Workspace limits
Joint limits
Velocity limits
Safe home position
Emergency stop
Command validation
Collision awareness
```

Safety should remain a separate layer from task logic.

---

### 6. Experimentation

Every significant manipulation change should be recorded as an experiment.

Example:

```text
projects/chess/experiments/phase1/

EXP-001-baseline-cube-pick-place.md
EXP-002-grasp-position-sweep.md
EXP-003-placement-accuracy.md
```

---

### 7. Logging and visualization

Use the existing tooling, including Rerun where appropriate, to inspect:

- robot state;
- trajectories;
- target positions;
- object positions;
- timing;
- failures;
- experiment metadata.

Visualization should support debugging and analysis rather than become an end in itself.

---

# 8. Phase 1 Experiments

The first experiments should progressively introduce uncertainty.

### EXP-001 — Baseline Pick and Place

Question:

> How reliably can the SO100/SO101 execute a deterministic pick-and-place task under controlled conditions?

Variables:

```text
Fixed object
Fixed target
Known coordinates
Controlled environment
No perception
```

---

### EXP-002 — Grasp Position Sweep

Question:

> How sensitive is grasp success to the relative position of the gripper and object?

Example:

```text
Object position
      +
      ├── -10 mm
      ├── -5 mm
      ├──  0 mm
      ├── +5 mm
      └── +10 mm
```

---

### EXP-003 — Placement Accuracy

Question:

> How accurately can the robot place an object at a target position?

Measure:

```text
Target position
      vs
Actual position
```

---

### EXP-004 — Robustness

Introduce controlled variation:

```text
Object position
Object orientation
Object geometry
Movement speed
```

The objective is to determine where the deterministic baseline starts to fail.

---

# 9. Phase 1 Metrics

The project should establish common metrics before comparing approaches.

| Metric | Purpose |
|---|---|
| Pick success rate | Measures grasp reliability |
| Placement success rate | Measures placement reliability |
| Full-task success rate | Measures complete manipulation |
| Placement error | Measures positioning accuracy |
| Execution time | Measures task efficiency |
| Motion/path length | Measures trajectory efficiency |
| Failure type | Enables failure analysis |
| Recovery success | Measures robustness |
| Control/inference latency | Enables later systems comparison |

A useful baseline experiment should contain enough trials to make the result meaningful rather than relying on a single successful demonstration.

---

# 10. Phase 1 Definition of Done

Phase 1 is not complete when a cube has successfully been moved once.

The phase is complete when:

- reusable manipulation primitives exist;
- the SO100/SO101 can execute a defined pick-and-place task;
- safety constraints are enforced;
- the manipulation pipeline is repeatable;
- experiments are documented;
- failures are classified;
- quantitative metrics are recorded;
- experiment data can be reproduced or inspected;
- a baseline has been established for future learned policies.

The final output of Phase 1 should therefore be a **benchmark**, not merely a script.

---

# 11. Role of LeRobot in Phase 1

LeRobot remains part of the project stack, but Phase 1 is **not primarily a LeRobot policy-training phase**.

Its role at this stage is primarily:

```text
Robot ecosystem
Robot interface
Calibration
State/action representation
Data recording infrastructure
Replay / dataset preparation
Policy ecosystem familiarity
```

The manipulation layer should not become tightly coupled to LeRobot-specific implementation details.

Conceptually:

```text
                    Project Code

             Manipulation / Planning
                      │
                      ▼
                Robot Interface
                      │
                      ▼
                   LeRobot
                      │
                      ▼
                 SO100/SO101
```

This allows the project to later introduce:

```text
LeRobot Dataset
       ↓
ACT
       ↓
Diffusion Policy
       ↓
VLA
```

without rewriting the manipulation architecture.

---

# 12. Proposed Repository Architecture

The following structure is the **current proposal**, not a permanent architectural decision.

It should be reviewed with mentors and updated as the project grows.

```text
Modern-Robot-Learning/
│
├── README.md
├── pyproject.toml
│
├── docs/
│   ├── ONBOARDING.md
│   ├── ARCHITECTURE.md
│   ├── DATASETS.md
│   ├── POLICIES.md
│   ├── BENCHMARKS.md
│   ├── EXPERIMENTS.md
│   └── ...
│
├── projects/
│   └── chess/
│       │
│       ├── robot/
│       ├── manipulation/
│       ├── perception/
│       ├── planning/
│       └── experiments/
│           │
│           ├── phase1/
│           ├── phase2/
│           ├── phase3/
│           └── ...
│
├── datasets/
│   ├── README.md
│   ├── schemas/
│   └── scripts/
│
├── notebooks/
│
├── scripts/
│
└── configs/
```

The actual robot datasets should not be committed directly to Git when they become large.

The repository should contain:

- dataset schemas;
- metadata;
- collection scripts;
- validation tools;
- experiment references.

The actual datasets can be versioned and stored through the Hugging Face Hub.

---

# 13. Why the Architecture May Change

This is a research platform.

The architecture should therefore evolve when experiments reveal better abstractions.

Architecture decisions should be changed deliberately rather than treating the first directory structure as permanent.

When a meaningful architectural decision is made, document:

```text
Problem
    ↓
Options considered
    ↓
Decision
    ↓
Reason
    ↓
Consequences
```

The goal is not to predict the perfect architecture.

The goal is to build an architecture that makes experimentation easy while preserving enough structure to understand and reproduce results.

---

# 14. Documentation Structure

The repository should gradually develop the following documentation:

```text
docs/

ONBOARDING.md
    Project vision, roadmap, phases, team rules

ARCHITECTURE.md
    Technical architecture and module boundaries

DATASETS.md
    Dataset conventions, schemas, versioning and storage

POLICIES.md
    Learned policies and training conventions

BENCHMARKS.md
    Evaluation methodology and metrics

EXPERIMENTS.md
    Experiment conventions and lifecycle

PAPERS.md
    Research literature and implementation relevance

LESSONS_LEARNED.md
    Important findings from experiments
```

Documentation should evolve alongside the implementation.

---

# 15. Research Workflow

Every meaningful experiment follows:

```text
Research Question
        ↓
Hypothesis
        ↓
Experimental Design
        ↓
Implementation
        ↓
Data Collection
        ↓
Evaluation
        ↓
Failure Analysis
        ↓
Conclusion
        ↓
Next Experiment
```

Experiments should produce both:

```text
Technical artifact
+
Scientific record
```

---

# 16. Team Working Principles

We optimize for:

```text
understanding > copying
experiments > demos
measurement > intuition
reproducibility > one-off success
clear interfaces > unnecessary abstraction
integration > isolated components
```

A contribution is valuable when the team can:

1. run it;
2. test it;
3. explain it;
4. reproduce it;
5. understand its limitations.

---

# 17. Long-Term Target

By the end of the project, a new contributor should be able to:

```text
Clone repository
      ↓
Understand architecture
      ↓
Run baseline
      ↓
Run existing experiment
      ↓
Inspect dataset
      ↓
Train a policy
      ↓
Evaluate policy
      ↓
Deploy to robot
      ↓
Compare against baseline
```

The platform should demonstrate the complete modern robot-learning workflow:

```text
Perception
    +
Data
    +
Planning
    +
Learning
    +
Control
    +
Hardware
    +
Evaluation
```

The chess robot is the first application used to connect these components.