# Robot Chess Learning Platform
### A Modern Robot Learning Project using LeRobot, SO100 Robotic Arms, YOLO, and Chess

---

# Project Overview

This project aims to build an autonomous robotic system capable of playing chess by combining:
- modern robot learning
- computer vision
- classical planning
- manipulation.

Rather than simply creating a chess-playing robot, the goal is to develop a **modular embodied AI platform** that integrates:

- Robot Learning (LeRobot - Hugging Face)
- Computer Vision (YOLO + OpenCV)
- Robot Manipulation (SO100 robotic arm)
- Chess Planning (Stockfish + python-chess)
- Learning from Demonstrations (Imitation Learning)
- Modern Robot Policies (ACT, Diffusion Policies, etc.)

The architecture is intentionally modular so that each subsystem can evolve independently.


//better separation, repetition of the concepts included e.g. Robot Learning and Modern Robot Policies are the same

---

# High-Level System Architecture

```text
                        Cameras
                           │
                    Vision Pipeline
                           │
      ┌────────────────────┴─────────────────────┐
      │                                          │
YOLO Piece Detection                    Board Detection
      │                                          │
      └──────────────► Chess State ◄─────────────┘
                           │
                     Stockfish Engine
                           │
                     Desired Chess Move
                           │
                High-level Motion Planner
                           │
             Pick Pose + Place Pose Generator
                           │
                  LeRobot Policy Network
                           │
                  SO100 Robot Controller
                           │
                    Robot Manipulation
                           │
                   New Camera Observation
```

///are board and piece detection done by YOLO?
The chess engine **never directly controls the robot**.

It only outputs the desired move, for example:

```
Move Knight from g1 to f3
```

The robotics system is responsible for executing this move safely and accurately.

---

# Software Architecture

```
robot-chess/

│
├── configs/
│
├── lerobot/
│
├── vision/
│   ├── yolo_detector.py
│   ├── board_detector.py
│   ├── calibration.py
│   ├── board_state.py
│
├── planning/
│   ├── stockfish_interface.py
│   ├── move_planner.py
│   ├── grasp_generation.py
│
├── robot/
│   ├── so100_interface.py
│   ├── trajectory.py
│   ├── kinematics.py
│
├── learning/
│   ├── dataset.py
│   ├── train.py
│   ├── evaluate.py
│
├── data/
│
├── notebooks/
│
└── experiments/
```

Each package has a clear responsibility and can be developed and tested independently.

---

# Vision Stack

The perception pipeline should separate board localization from piece detection.

```
Camera

↓

Board Localization

↓

Perspective Transform

↓

64 Square Extraction

↓

YOLO

↓

Piece Classification

↓

Board State
```

This approach is significantly more robust than attempting to detect the entire board state directly with YOLO.

---

# YOLO Object Detection

YOLO should classify every chess piece independently.

Suggested classes:

```
white pawn
white rook
white knight
white bishop
white queen
white king

black pawn
black rook
black knight
black bishop
black queen
black king
```

Each prediction contains:

- Bounding Box
- Piece Class
- Confidence Score

The board detector converts each detection into a board square.

---

# Chess Representation

Internally, the board should be represented using the `python-chess` library.
https://python-chess.readthedocs.io/en/latest/ 

Example representations:

```
rnbqkbnr
pppppppp
........
........
........
........
PPPPPPPP
RNBQKBNR
```

or using a standard **FEN (Forsyth–Edwards Notation)** string.

This makes integration with Stockfish straightforward.

---

# Motion Planning Layer

Stockfish outputs a chess move:

```
e2 -> e4
```

The motion planner converts this into physical robot commands:

```
Pick Pose
    x
    y
    z

↓

Place Pose
    x
    y
    z
```

These poses are generated using camera calibration and workspace transformations.

---

# Robot Layer

Initially, manipulation can rely on classical robotics rather than learned policies.

Example primitive actions:

```
MoveHome()

MoveAbovePiece()

Descend()

CloseGripper()

Lift()

MoveAboveDestination()

Descend()

OpenGripper()

ReturnHome()
```

These primitives establish a reliable baseline before introducing learning.

---

# Learning Layer (LeRobot)

Once scripted manipulation works reliably, LeRobot can learn the manipulation policy.

Inputs:

```
RGB Image

+

Robot Joint States

+

Gripper State

+

Target Square
```

↓

```
Neural Network
```

↓

```
Joint Actions
```

The learned policy replaces manually designed trajectories.

---

# Dataset Collection

LeRobot is designed around Learning from Demonstrations (LfD).

Each dataset sample should contain:

```
Observation

RGB Images

Robot Joint Angles

Gripper State

Timestamp

↓

Action

Joint Velocities

Gripper Commands
```

A complete trajectory might look like:

```
Home

↓

Move Above Piece

↓

Pick Piece

↓

Lift

↓

Move Above Destination

↓

Place Piece

↓

Return Home
```

Thousands of demonstrations should be collected for robust policy learning.

---

# Training Pipeline

```
Teleoperate Robot

↓

Collect Demonstrations

↓

Create LeRobot Dataset

↓

Train Policy

↓

Evaluate

↓

Fine Tune

↓

Deploy
```

---

# Progressive Learning Roadmap

Rather than beginning directly with chess, the robot should learn progressively harder manipulation tasks.

---

## Phase 1 — Cube Pick and Place

```
Cube

↓

Pick

↓

Drop
```

Goal:

- Learn basic manipulation.

---

## Phase 2 — Colored Object Picking

```
Vision

↓

Pick Correct Object
```

Goal:

- Integrate vision into manipulation.

---

## Phase 3 — Chess Piece Manipulation

Goal:

- Handle different piece geometries.

---

## Phase 4 — Accurate Piece Placement

Goal:

- Place pieces precisely inside board squares.

---

## Phase 5 — Captures

Goal:

- Remove captured pieces.
- Handle occupied destinations.

---

## Phase 6 — Full Chess Gameplay

Goal:

- Execute complete legal chess games autonomously.

---

# Research Extensions

## 1. End-to-End Manipulation

Current pipeline:

```
YOLO

↓

Planner

↓

Robot
```

Future pipeline:

```
Image

↓

Policy

↓

Robot Actions
```

This eliminates explicit planning and is closer to current embodied AI research.

---

## 2. Vision-Language Models

Replace symbolic goals with natural language.

Example:

```
Move the white queen to h5.
```

The robot interprets the instruction directly.

---

## 3. Diffusion Policies

LeRobot supports several modern robot learning algorithms.

Potential comparisons:

- ACT
- Diffusion Policy
- π₀-style policies (when available)
- SmolVLA / Vision-Language-Action models (where applicable)

Evaluate:

- Sample efficiency
- Success rate
- Generalization
- Robustness

---

## 4. Multi-Camera Learning

```
Top Camera

+

Wrist Camera

↓

Policy
```

Multi-view observations improve manipulation accuracy.

---

## 5. Self-Correction

Instead of failing after a bad grasp:

```
Observe

↓

Detect Failure

↓

Replan

↓

Retry
```

This introduces robustness and closed-loop behavior.

---

# Project Milestones

| Milestone | Goal |
|------------|------|
| M1 | Calibrate camera and robot workspace |
| M2 | Detect chessboard and pieces with YOLO |
| M3 | Convert detections into a valid board state (FEN) |
| M4 | Integrate Stockfish for legal move generation |
| M5 | Execute scripted pick-and-place motions |
| M6 | Collect demonstrations using LeRobot |
| M7 | Train an imitation learning policy |
| M8 | Compare learned policy against scripted baseline |
| M9 | Handle captures, promotions, and recovery behaviors |
| M10 | Demonstrate autonomous chess gameplay |

---

# Recommended Technology Stack

## Robot Learning

- LeRobot (Hugging Face)

## Machine Learning

- PyTorch

## Robot Hardware

- SO100 Robotic Arm
- Gripper

## Vision

- YOLOv11 (or newer)
- OpenCV

## Chess

- python-chess
- Stockfish

## Simulation (Optional)

- MuJoCo

## Middleware

- ROS2 (optional)

For a single robotic arm, a lightweight Python architecture is sufficient initially.

---

# Long-Term Vision

This project should not be viewed merely as a "robot that plays chess."

Instead, it serves as an **Embodied AI Research Platform**.

Chess provides:

- Structured rules
- Rich visual perception
- Precise manipulation
- Long-horizon planning
- Quantifiable evaluation

Once the architecture is established, the same platform can be adapted to many other tabletop manipulation tasks, including:

- Object sorting
- Assembly
- Pick-and-place
- Industrial manipulation
- Human-robot collaboration

By keeping perception, planning, learning, and control modular, the project becomes a reusable research framework rather than a single-purpose application.

---

# Future Directions

Potential future research includes:

- Reinforcement Learning fine-tuning
- Sim-to-Real transfer
- Foundation Vision-Language-Action models
- Multi-arm coordination
- Dexterous manipulation
- Active perception
- Online continual learning
- Autonomous recovery from unexpected failures

This roadmap aligns closely with current research trends in embodied AI and modern robot learning.