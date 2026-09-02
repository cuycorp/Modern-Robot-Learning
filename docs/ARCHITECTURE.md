# Modern Robot Learning — Architecture

**Version:** 0.1  
**Status:** Proposed / Under Review  
**Scope:** Research platform architecture

---

# 1. Purpose

This document defines the proposed technical architecture for the **Modern Robot Learning** research platform.

The architecture is designed around one principle:

> **Components should be independently testable and replaceable so that research experiments can change one part of the system without requiring a rewrite of the rest.**

This is a proposed architecture. It should be revised as the project develops and after review with robotics mentors.

---

# 2. Design Principles

## 2.1 Separate research concerns

The system separates:

```text
Perception
Planning
Manipulation
Robot Control
Learning
Data
Evaluation
```

A change to one component should have a limited impact on the others.

---

## 2.2 Separate "what" from "how"

The system distinguishes between:

```text
What should happen?
        ↓
Task / Planning

How should the robot execute it?
        ↓
Manipulation / Policy

How does the physical robot receive commands?
        ↓
Robot Interface
```

For example:

```text
Chess engine:
    "Move e2 → e4"

Planning:
    "Pick piece from square e2 and place on e4"

Manipulation:
    "Execute grasp, lift, transport and release"

Robot interface:
    "Convert commands into robot actions"

SO100/SO101:
    Execute physical motion
```

---

# 3. High-Level Architecture

## Current architecture

```text
                         ┌────────────────────┐
                         │     Experiment     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Task / Planning    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Manipulation     │
                         │     Primitives     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Safety Layer     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │  Robot Interface   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    LeRobot        │
                         └─────────┬──────────┘
                                   │
                              ┌────┴────┐
                              ▼         ▼
                           SO100     SO101
```

Later, perception and learned policies are introduced:

```text
                         Cameras
                            │
                            ▼
                     ┌──────────────┐
                     │  Perception  │
                     │ YOLO / OpenCV│
                     └──────┬───────┘
                            │
                       Object Poses
                            │
                            ▼
                     ┌──────────────┐
                     │ World Model  │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Planning   │
                     └──────┬───────┘
                            │
                  ┌─────────┴──────────┐
                  │                    │
                  ▼                    ▼
           Scripted Control      Learned Policy
                  │                    │
                  └─────────┬──────────┘
                            ▼
                     ┌──────────────┐
                     │ Safety Layer │
                     └──────┬───────┘
                            ▼
                     Robot Interface
                            │
                         LeRobot
                            │
                         SO100/101
```

---

# 4. Module Boundaries

## `robot/`

Responsible for communication with the physical robot.

```text
robot/
├── so100.py
├── so101.py
├── state.py
├── safety.py
└── ...
```

Responsibilities:

- robot connection;
- robot state;
- action interface;
- calibration integration;
- hardware-specific behavior;
- safety enforcement.

The rest of the application should not depend directly on low-level robot details.

---

# 5. `manipulation/`

Responsible for reusable manipulation behavior.

```text
manipulation/
├── primitives.py
├── pick_place.py
├── grasp.py
└── workspace.py
```

Example primitives:

```text
move_home()
move_to()
move_above()
descend()
grasp()
lift()
release()
```

Higher-level tasks compose these primitives:

```text
pick()
    ↓
move_above()
descend()
grasp()
lift()
```

and:

```text
place()
    ↓
move_above()
descend()
release()
lift()
```

The manipulation layer should not know whether an object position came from a human, a simulator, YOLO, or another perception system.

---

# 6. `perception/`

Introduced primarily during Phase 2.

```text
perception/
├── camera.py
├── calibration.py
├── board_detection.py
├── yolo_detector.py
├── tracking.py
└── coordinate_transforms.py
```

Responsibilities:

- camera input;
- calibration;
- object detection;
- object localization;
- coordinate transformation;
- confidence estimation.

The desired interface is conceptually:

```text
Camera
  ↓
Detector
  ↓
Object
  ↓
Pose + Confidence
```

Example:

```python
ObjectPose(
    position=[x, y, z],
    orientation=...,
    confidence=0.97,
)
```

The manipulation system consumes the resulting pose rather than knowing how it was detected.

---

# 7. `world_model/`

The world model represents the current state of the environment.

Conceptually:

```text
WorldState

Robot
 ├── joint positions
 ├── gripper state
 └── pose

Objects
 ├── cube
 ├── chess pieces
 └── target locations

Environment
 ├── board
 └── workspace
```

This provides a common interface between perception, planning and manipulation.

---

# 8. `planning/`

Planning determines the desired task.

For chess:

```text
Stockfish
    ↓
Chess move
    ↓
Move planner
    ↓
Manipulation goal
```

Example:

```text
e2 → e4
```

becomes:

```text
Pick object at e2
Place object at e4
```

Planning should not directly control individual robot joints.

---

# 9. `policies/`

Learned policies are treated as interchangeable components.

```text
policies/
├── scripted/
├── act/
├── diffusion/
├── openvla/
└── smolvla/
```

The initial scripted system provides the baseline.

Later:

```text
Scripted
   vs
ACT
   vs
Diffusion Policy
   vs
VLA
```

can be evaluated using the same task and benchmark infrastructure.

---

# 10. Safety Layer

Safety sits between high-level control and physical robot execution.

```text
Task
 ↓
Policy / Manipulation
 ↓
Safety
 ↓
Robot Interface
 ↓
Robot
```

The safety layer should validate:

- workspace limits;
- joint limits;
- velocity limits;
- action validity;
- robot state;
- emergency-stop conditions.

A learned policy should not be trusted to enforce physical safety by itself.

---

# 11. LeRobot Boundary

LeRobot is an important part of the project ecosystem, but it should not define the architecture of the entire application.

Conceptually:

```text
                Research Platform

 ┌─────────────────────────────────────────┐
 │                                         │
 │  Planning                               │
 │  Manipulation                           │
 │  Perception                             │
 │  Policies                               │
 │  Evaluation                             │
 │                                         │
 └───────────────────┬─────────────────────┘
                     │
              Robot Interface
                     │
 ┌───────────────────▼─────────────────────┐
 │                LeRobot                  │
 └───────────────────┬─────────────────────┘
                     │
                  SO100/101
```

This keeps the application logic independent from a specific robotics framework where practical.

LeRobot becomes increasingly important as the project moves toward:

```text
Teleoperation
      ↓
Dataset collection
      ↓
Policy training
      ↓
Policy deployment
```

---

# 12. Rerun

Rerun is treated primarily as an **observability and visualization layer**.

It should not become a core dependency of manipulation logic.

Conceptually:

```text
Robot ───────────────┐
                     │
Perception ──────────┼──→ Rerun
                     │
Planning ────────────┤
                     │
Experiment ──────────┘
```

Useful information to visualize includes:

- camera frames;
- detected objects;
- robot trajectories;
- coordinate frames;
- target positions;
- robot state;
- timing;
- experiment events.

This allows failures to be investigated visually and quantitatively.

---

# 13. Data Architecture

Datasets should be treated as research artifacts rather than simply files produced by scripts.

The repository contains:

```text
datasets/
├── README.md
├── schemas/
└── scripts/
```

The actual large datasets can be stored and versioned on the Hugging Face Hub.

Conceptually:

```text
Robot
  ↓
Recording
  ↓
Dataset validation
  ↓
Hugging Face Dataset
  ↓
Training / Evaluation
```

The Git repository should record which dataset version was used for each experiment.

Example:

```text
Experiment:
    EXP-004

Dataset:
    so100-phase1-manipulation

Dataset version:
    v1.2

Code commit:
    abc123
```

This creates a link between:

```text
Code
+
Experiment
+
Dataset
+
Results
```

---

# 14. Proposed Repository Structure

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
│   ├── PAPERS.md
│   └── LESSONS_LEARNED.md
│
├── projects/
│   └── chess/
│       │
│       ├── robot/
│       │   ├── so100.py
│       │   ├── so101.py
│       │   ├── state.py
│       │   └── safety.py
│       │
│       ├── manipulation/
│       │   ├── primitives.py
│       │   ├── pick_place.py
│       │   ├── grasp.py
│       │   └── workspace.py
│       │
│       ├── perception/
│       │
│       ├── planning/
│       │   ├── chess.py
│       │   ├── stockfish.py
│       │   └── move_planner.py
│       │
│       ├── policies/
│       │   ├── scripted/
│       │   ├── act/
│       │   ├── diffusion/
│       │   └── vla/
│       │
│       └── experiments/
│           ├── phase1/
│           │   ├── EXP-001-baseline-cube-pick-place.md
│           │   ├── EXP-002-grasp-position-sweep.md
│           │   └── EXP-003-placement-accuracy.md
│           │
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

---

# 15. Why Experiments Live Inside the Project

Experiments are associated with the task/application they investigate.

Therefore:

```text
projects/chess/experiments/
```

contains the experimental record for the chess manipulation system.

This keeps:

```text
Implementation
+
Experiments
+
Task
```

close together.

The experiment itself should not contain the entire dataset.

Instead:

```text
Experiment
    ↓
references
    ↓
Dataset
    ↓
Hugging Face Hub
```

---

# 16. Experiment Structure

Each experiment should have a scientific record.

Example:

```text
phase1/
└── EXP-001-baseline-cube-pick-place.md
```

Recommended structure:

```markdown
# EXP-001 — Baseline Cube Pick and Place

## Research Question

## Hypothesis

## Hardware

## Environment

## Variables

## Procedure

## Metrics

## Dataset

## Results

## Failure Analysis

## Conclusions

## Next Experiment
```

For larger experiments, the structure can evolve into:

```text
EXP-001/
├── README.md
├── config.yaml
├── results.json
├── plots/
└── logs/
```

The architecture should support both forms.

---

# 17. Architecture by Project Phase

## Phase 1

```text
Experiment
   ↓
Scripted Manipulation
   ↓
Safety
   ↓
Robot Interface
   ↓
LeRobot
   ↓
SO100/SO101
```

Primary research:

```text
Reliability
Accuracy
Grasping
Motion
Failure modes
```

---

## Phase 2

```text
Camera
   ↓
Perception
   ↓
World Model
   ↓
Manipulation
   ↓
Robot
```

Primary research:

```text
Detection
Localization
Calibration
Perception robustness
```

---

## Phase 3

```text
Human
   ↓
Teleoperation
   ↓
LeRobot
   ↓
Dataset
```

Primary research:

```text
Demonstration quality
Data collection
Teleoperation interfaces
Dataset design
```

---

## Phase 4

```text
Dataset
   ↓
ACT / Diffusion
   ↓
Policy
   ↓
Safety
   ↓
Robot
```

Primary research:

```text
Imitation learning
Generalization
Data efficiency
Policy robustness
```

---

## Phase 5

```text
Simulation
   ↓
Synthetic Data
   ↓
Policy
   ↓
Sim-to-Real
   ↓
Physical Robot
```

---

## Phase 6+

```text
Vision
 +
Language
 +
Robot State
       ↓
     VLA
       ↓
  Action Policy
       ↓
     Safety
       ↓
     Robot
```

The architecture should allow these stages to coexist rather than forcing one approach to replace the previous one.

---

# 18. Baselines Are First-Class Components

The scripted manipulation system is not temporary code that will eventually be deleted.

It provides:

```text
Baseline
Reference implementation
Debugging tool
Safety fallback
Evaluation reference
Data collection primitive
```

Later experiments should answer:

```text
Is ACT better than our scripted baseline?

Is Diffusion Policy more robust?

Does additional data improve performance?

Does simulation reduce real-world data requirements?

Does perception introduce a measurable failure mode?
```

This makes the project a research platform rather than a sequence of unrelated demos.

---

# 19. Architecture Evolution

The initial architecture is intentionally conservative.

We should avoid introducing abstractions solely because they might become useful later.

A new abstraction should be introduced when:

```text
Repeated implementation
        OR
Experiment requires it
        OR
Two components need a stable interface
        OR
A research comparison requires it
```

Architecture should follow demonstrated requirements.

---

# 20. Current Architectural Decision

The current proposal is:

```text
Application logic
        ↓
Own project interfaces
        ↓
LeRobot / external robotics libraries
        ↓
Hardware
```

with:

```text
Perception
Planning
Manipulation
Policies
Evaluation
Data
```

kept as separate conceptual modules.

This decision is **provisional** and should be reviewed with mentors before becoming a rigid project standard.