# Embodied Learning Platform: Team Onboarding Pack

**Version:** 0.1

**Project Type:** Embodied AI Research Platform

**Status:** Research Planning / Source of Truth

---

# 1. Why this document exists

This document is the single starting point for everyone contributing to the **Embodied Learning Platform**.

Before writing code or training policies, every contributor must understand:

1. The research problem we are trying to solve.
2. The robotics stack and system architecture.
3. The project scope and research roadmap.
4. How experiments are designed and evaluated.
5. How data is collected and managed.
6. How models are trained and deployed.
7. The engineering standards expected throughout the project.

**Rule**

> Nobody trains or deploys a policy they cannot explain.

AI tools are used as engineering assistants, **never** as a substitute for understanding. Every experiment, implementation, and design decision must be explainable and reproducible.

---

# 2. Research Vision

## Project Name

**Embodied Learning Platform**

### One-Sentence Pitch

A modular robotics research platform for studying modern robot learning using imitation learning, reinforcement learning, and foundation models through the benchmark task of autonomous chess manipulation.

---

## Long-Term Vision

The project is **not** about building a chess-playing robot.

Instead, it aims to develop a complete embodied AI pipeline capable of:

- Perception
- Planning
- Manipulation
- Robot Learning
- Simulation
- Sim-to-Real Transfer
- Human-in-the-Loop Data Collection

Chess is used as a **structured benchmark** because it combines:

- Precise object manipulation
- Vision
- Sequential planning
- Repeatable evaluation
- Long-horizon tasks

The architecture should be reusable for other tabletop manipulation tasks.

---

# 3. Research Questions

The project is driven by research questions rather than implementation goals.

Examples include:

- How much demonstration data does ACT require?
- Can Diffusion Policies outperform ACT for chess manipulation?
- Does simulation reduce the amount of real-world data needed?
- How effective is domain randomization for sim-to-real transfer?
- Can Vision-Language-Action models generalize to unseen chess configurations?
- How should failure recovery be integrated into learned policies?
- What are the latency bottlenecks in a complete robot learning pipeline?

Each experiment should answer a measurable research question.

---

# 4. Product Overview

## Core System

```text
                RGB Cameras
                     │
              Perception Layer
                     │
               World Model
                     │
              Task Planning
                     │
        Robot Learning Policy
                     │
           Robot Controller
                     │
               SO100 Robot
                     │
             Environment Update
```

The project separates **decision making** from **robot execution**.

Example:

```
Stockfish

↓

Move e2 → e4

↓

Motion Planner

↓

Pick Pose

↓

Robot Policy

↓

Robot Actions
```

The chess engine defines **what** to do.

The robot learning policy determines **how** to execute it.

---

# 5. Project Philosophy

The platform prioritizes:

```
Understanding

↓

Reproducibility

↓

Research

↓

Engineering Quality

↓

Demonstrations
```

Every contribution should satisfy:

- Reproducible
- Explainable
- Modular
- Well documented
- Experimentally validated

---

# 6. Project Scope

## In Scope

- SO100 robotic arm
- LeRobot
- Imitation Learning
- Reinforcement Learning
- Diffusion Policies
- ACT
- OpenVLA / SmolVLA experiments
- YOLO-based perception
- Multi-camera calibration
- MuJoCo simulation
- Sim-to-Real transfer
- Teleoperation
- Dataset collection
- Benchmarking
- Failure recovery

---

## Explicitly Out of Scope (Initial Version)

- Humanoid robots
- Bimanual manipulation
- Dexterous hands
- Multi-agent robotics
- Large-scale reinforcement learning
- Custom robot hardware

The project focuses on building one excellent embodied AI platform rather than many incomplete features.

---

# 7. Software Architecture

```
robot-learning-platform/

│
├── configs/
│
├── perception/
│   ├── calibration.py
│   ├── board_detection.py
│   ├── yolo_detector.py
│   ├── tracking.py
│   └── coordinate_transforms.py
│
├── world_model/
│
├── planning/
│   ├── stockfish.py
│   ├── move_planner.py
│   ├── recovery.py
│
├── robot/
│   ├── so100.py
│   ├── kinematics.py
│   ├── trajectory.py
│
├── policies/
│   ├── scripted/
│   ├── act/
│   ├── diffusion/
│   ├── openvla/
│
├── teleoperation/
│
├── datasets/
│
├── simulation/
│
├── evaluation/
│
├── experiments/
│
└── docs/
```

Each module should remain independent and testable.

---

# 8. Robotics Stack

## Perception

Responsibilities:

- Camera calibration
- Chessboard localization
- Piece detection
- Coordinate transformations
- Multi-camera synchronization

Technology:

- OpenCV
- YOLO
- ArUco markers
- Camera calibration

---

## World Model

Responsibilities:

- Robot state
- Board state
- Object poses
- Coordinate frames

---

## Planning

Responsibilities:

- Chess planning
- Motion planning
- Recovery planning

Technology:

- python-chess
- Stockfish

---

## Robot Learning

Policies to evaluate:

- Scripted baseline
- ACT
- Diffusion Policy
- OpenVLA
- SmolVLA

---

## Deployment

Responsibilities:

- Robot control
- Logging
- Safety checks
- Runtime monitoring

---

# 9. Learning Philosophy

Development follows progressively more difficult robotics capabilities.

```
Scripted Control

↓

Teleoperation

↓

Imitation Learning

↓

Foundation Policies

↓

Reinforcement Learning

↓

Research Experiments
```

No advanced learning methods are introduced before reliable scripted manipulation exists.

---

# 10. Research Roadmap

## Phase 0 — Foundations

Goal:

Bring the robot online.

Deliverables:

- SO100 operational
- Cameras calibrated
- Workspace defined
- Basic robot interface

---

## Phase 1 — Manipulation

Goal:

Reliable pick-and-place.

Deliverables:

- Cube manipulation
- Grasp evaluation
- Motion primitives
- Safety testing

---

## Phase 2 — Perception

Goal:

Reliable visual understanding.

Deliverables:

- Chessboard detection
- YOLO dataset
- Piece classification
- Coordinate transforms

---

## Phase 3 — Teleoperation

Goal:

Collect demonstrations.

Deliverables:

- Teleoperation interface
- Trajectory recording
- Replay
- Dataset validation

---

## Phase 4 — Imitation Learning

Goal:

Train robot policies.

Deliverables:

- ACT implementation
- Training pipeline
- Evaluation
- Failure analysis

---

## Phase 5 — Simulation

Goal:

Reduce real-world data collection.

Deliverables:

- MuJoCo environment
- Domain randomization
- Sim-to-real evaluation

---

## Phase 6 — Foundation Models

Goal:

Evaluate modern VLA approaches.

Deliverables:

- OpenVLA experiments
- SmolVLA experiments
- Language-conditioned manipulation

---

## Phase 7 — Reinforcement Learning

Goal:

Improve policies beyond demonstrations.

Deliverables:

- Reward design
- RL fine-tuning
- Benchmark comparisons

---

# 11. Experiment Workflow

Every experiment follows the same process.

```
Research Question

↓

Hypothesis

↓

Implementation

↓

Dataset

↓

Training

↓

Evaluation

↓

Discussion

↓

Next Experiment
```

Experiments are considered complete only when documented.

---

# 12. Evaluation Metrics

Every policy should be evaluated using identical metrics.

| Metric | Description |
|----------|------------|
| Success Rate | Successful task completion |
| Placement Error | Distance from target square |
| Grasp Success | Successful grasps |
| Completion Time | Seconds per move |
| Policy Latency | Inference latency |
| Recovery Success | Successful recovery after failure |
| Sim-to-Real Gap | Difference between simulation and reality |

---

# 13. Required Reading

The project follows current robotics research.

Core papers:

- ACT
- Diffusion Policy
- LeRobot
- OpenVLA
- SmolVLA
- EquiBot
- ChainedDiffuser
- Open Source Chess Robot
- Deep Reinforcement Learning for Robotic Manipulation

Each paper should include:

- Summary
- Main contributions
- Implementation ideas
- Relevance to this project

---

# 14. Documentation

```
README.md

docs/

    ONBOARDING.md

    ARCHITECTURE.md

    DATASETS.md

    SIMULATION.md

    TELEOPERATION.md

    POLICIES.md

    BENCHMARKS.md

    PAPERS.md

    EXPERIMENTS.md

    ROADMAP.md

    LESSONS_LEARNED.md
```

Documentation is treated as part of the project deliverable.

---

# 15. Engineering Principles

The project follows several engineering principles.

## Modular Design

Every subsystem should be replaceable without modifying the rest of the system.

## Reproducibility

Every experiment should be reproducible from the repository.

## Research First

Every implementation should answer a research question.

## Benchmark Everything

Every policy should be compared against a baseline.

## Fail Gracefully

Robot failures are valuable data and should be logged and analyzed rather than ignored.

---

# 16. Long-Term Vision

The final repository should resemble the internal repository of a robotics research startup.

A new researcher should be able to:

1. Clone the repository.
2. Read the onboarding documentation.
3. Set up the robot.
4. Reproduce published experiments.
5. Train a new policy.
6. Deploy the policy on the SO100.
7. Evaluate it using standardized benchmarks.
8. Compare results with previous approaches.

The project should demonstrate the complete robotics research lifecycle, from data collection to deployment, mirroring the workflow of modern embodied AI teams.
