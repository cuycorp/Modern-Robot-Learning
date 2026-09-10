# Modern Robot Learning — Roadmap

**Goal:** a SO100/SO101 arm that plays physical chess, built so that each
layer (perception, planning, manipulation, control, learning) can be
replaced independently and every claim about the system is backed by a
measurement.

**Stack (decided):**

| Layer | Choice |
|---|---|
| Physics / simulation | MuJoCo (MJCF scenes) |
| Robot control & data | LeRobot (Hugging Face) |
| Teleop & recording UI | LeLab |
| Hardware | SO100 / SO101, from day one alongside sim |
| Perception | YOLO detector fine-tuned on real pieces |
| Policy learning | Diffusion policies from the LeRobot / HF catalogue, simplest first |
| Dataset format | `LeRobotDataset` v2, published to the HF Hub |
| Experiment tracking | Weights & Biases |
| Environment | `uv` lockfile, then Docker for the GPU/robot machines |
| Tests | `pytest`, hardware-free path runs in CI |

---

## How to read this file

- `[ ]` not started · `[~]` in progress · `[x]` done
- Every task carries an **AC** (acceptance criterion): the concrete,
  runnable thing that proves it is finished. A task without an AC is not
  ready to be worked on.
- Phases are ordered by dependency, not by priority. Work inside a phase
  can be parallel; work across phases usually cannot.
- Anything that changes an interface or a default gets a short entry in
  `design/<topic>.md` — Problem / Decision / Why / Result (measured) / Cost.

---

## Phase 0 — Foundations

Nothing below this line is trustworthy until the environment is
reproducible and the test harness exists.

- [ ] **P0.1 — Delete the stale `src/pyproject.toml`.**
  It does not parse: `tomllib` fails with
  `TOMLDecodeError: Illegal character '\n' (at line 4, column 19)`
  (unterminated `"opencv-python` string). The root `pyproject.toml` is
  now the real one; the `src/` copy is a leftover that will silently
  shadow it for anyone who runs `uv` from the wrong directory.
  **AC:** `python -c "import tomllib,pathlib;[tomllib.loads(p.read_text()) for p in pathlib.Path('.').rglob('pyproject.toml')]"` exits 0.

- [ ] **P0.2 — Declare the real dependencies in the root `pyproject.toml`.**
  Currently `dependencies = []`; LeLab is the only entry and it sits in
  the dev group. MuJoCo, LeRobot, OpenCV and NumPy are runtime deps.
  Pin with `uv lock`, commit `uv.lock`.
  **AC:** a clean `uv sync --all-groups` in a fresh clone imports
  `mujoco`, `lerobot` and `cv2` without error.

- [ ] **P0.3 — Fix the package layout and make `src/` importable.**
  Decide explicitly: `src`-layout with `[tool.setuptools]`/`hatch`
  packaging, or PEP 420 namespace packages plus `PYTHONPATH`. Today
  imports only work by accident of the current working directory.
  **AC:** `uv run python -c "from projects.chess.manipulation.primitives import Pose"` works from the repository root.

- [ ] **P0.4 — Stand up `pytest`.** The `test/` directory exists and is
  empty. Rename to `tests/` for convention, add `[tool.pytest.ini_options]`
  with the right `pythonpath`/`testpaths`.
  **AC:** `uv run pytest` collects and runs at least one real test.

- [ ] **P0.5 — Lint and format gate.** `ruff` for both, configured in
  `pyproject.toml`, line length agreed once.
  **AC:** `uv run ruff check . && uv run ruff format --check .` exits 0.

- [ ] **P0.6 — `make` targets for the whole loop.** Extend the existing
  `Makefile`: `test`, `lint`, `sim`, `record`, `train`, `eval`.
  **AC:** `make help` lists them and each one runs.

- [ ] **P0.7 — CI on the hardware-free path.** GitHub Actions:
  `uv sync`, `ruff`, `pytest`, and a headless MuJoCo smoke test. No job
  may require a physical arm.
  **AC:** a green run on a pull request, with the robot unplugged.

- [ ] **P0.8 — Write the real `README.md`.** It is currently three lines
  containing one shell command. It needs: the one-sentence pitch, a
  system diagram, a quickstart, and a **Status** section that mirrors the
  current phase of this file.
  **AC:** a reader who has never seen the repo can run the Phase 1
  experiment from the README alone.

> Commit hygiene for this repository is enforced by local hooks in
> `.git/hooks/` (`pre-commit`, `commit-msg`, `pre-push`). They are
> intentionally not tracked. Bypassing them with `--no-verify` must be a
> deliberate, stated choice.

---

## Phase 1 — Deterministic manipulation baseline (EXP-001)

Isolate manipulation from perception: hard-coded cube and target
positions, no cameras, no learning. This phase proves the
`RobotInterface` seam works before anything is built on top of it.

Existing code: `src/projects/chess/manipulation/primitives.py`,
`src/projects/chess/robot/safety.py`.
`src/projects/chess/scripts/phase1_pick_place.py` is currently empty.

- [ ] **P1.1 — Fix `RobotInterface.open_gripper(selif)`.**
  `primitives.py:31` misspells the first parameter. Confirmed via
  `inspect.signature`, which prints `(selif) -> 'None'`. Harmless today
  only because Python binds the first argument positionally regardless of
  its name — but it breaks keyword calls and any future `Protocol` check,
  and it is direct evidence that this interface has never been
  implemented by anything.
  **AC:** `inspect.signature(RobotInterface.open_gripper)` prints `(self) -> 'None'`.

- [ ] **P1.2 — Add a recording fake robot.** A `RobotInterface`
  implementation that executes nothing and appends every call to an
  ordered list. Location: `src/projects/chess/robot/fake.py`, next to
  `safety.py`, so both the runner and the tests import it from one place.
  **AC:** a full `pick_and_place` run produces a deterministic 10-entry
  call log on a machine with no arm attached.

- [ ] **P1.3 — Write `phase1_pick_place.py`.** The EXP-001 runner:
  build `WorkspaceLimits` → `SafetyController` → a `RobotInterface` →
  `ManipulationPrimitives`, run the sequence, print the call log, return
  a non-zero exit code if a `SafetyViolation` propagated.
  **AC:** `uv run python -m projects.chess.scripts.phase1_pick_place` prints the ordered log and exits 0.

- [ ] **P1.4 — Tests for the primitives.** Assert properties of the
  *sequence*, which is the only place they are observable:
  the gripper closes strictly after the descend; the run starts and ends
  at home; an out-of-workspace target produces **no** `move_to` entry for
  that position and **does** produce a `stop` entry.
  **AC:** `uv run pytest tests/test_primitives.py` passes, and each test fails if its property is broken.

- [ ] **P1.5 — Tests for the safety layer.** Boundary behaviour of
  `WorkspaceLimits.contains` (inclusive bounds — verify, do not assume),
  `validate_position` raising rather than returning, and
  `validate_trajectory` reporting the offending index.
  **AC:** `uv run pytest tests/test_safety.py` passes.

- [ ] **P1.6 — Close the gripper safety gap.** `grasp()` and `release()`
  call the robot directly and never reach `_move`, so
  `SafetyController.validate_gripper` has **zero call sites** — grep
  returns only its own definition. Note the interface mismatch that makes
  this non-trivial: `validate_gripper(opening: float)` expects a
  continuous value, but `RobotInterface` exposes only binary
  `open_gripper()` / `close_gripper()` with no argument. Either give the
  interface a continuous gripper command, or delete the validator.
  Do not leave a validator that reads as coverage and provides none.
  **AC:** either `validate_gripper` has a real call site under test, or it is removed, and `design/safety.md` records which and why.

- [ ] **P1.7 — Decide and document: endpoint validation vs. path validation.**
  `_move` (`primitives.py:165-168`) validates the *destination* of every
  Cartesian command. The swept path between two consecutive destinations
  is never inspected — `validate_trajectory` also has zero call sites.
  Concretely: the transit from the end of `pick` to the start of `place`
  is one unconstrained straight-line move across the board carrying a
  grasped piece. Both endpoints are legal; the motion between them is
  unverified. For EXP-001 this may be an acceptable scoped limit — but it
  must be *stated* as a limit, not assumed away.
  **AC:** `design/safety.md` states the true guarantee in one sentence, and either interpolated waypoint checking is implemented or the gap is listed under Cost.

- [ ] **P1.8 — Write `design/manipulation.md` and `design/safety.md`.**
  Problem / Decision / Why / Result (measured) / Cost, per decision.
  **AC:** both files exist and each decision reads aloud in 60–90 seconds.

---

## Phase 2 — Simulation and hardware parity

Two `RobotInterface` implementations behind one seam. This is where the
Phase 1 abstraction either pays off or is exposed as fake.

- [ ] **P2.1 — MJCF scene: SO100 arm, table, cube, target.**
  **AC:** `mujoco.viewer` shows the scene; the arm settles under gravity without exploding.

- [ ] **P2.2 — `MujocoRobot(RobotInterface)`.** Implements `move_to`,
  `open_gripper`, `close_gripper`, `stop` against the MuJoCo model.
  **AC:** the unchanged `phase1_pick_place.py` runner moves the simulated cube from source to target.

- [ ] **P2.3 — Inverse kinematics.** `move_to` takes Cartesian XYZ but
  the arm takes joint targets. Choose and justify: analytic IK for the
  5-DoF SO100, damped least squares, or `mink`/`placo`. Handle
  unreachable targets explicitly — an IK failure is a safety event, not
  an exception to swallow.
  **AC:** a test asserts that an unreachable pose raises before any joint command is issued.

- [ ] **P2.4 — `SO100Robot(RobotInterface)` over LeRobot.**
  The real hardware backend, same interface.
  **AC:** the unchanged runner performs the physical pick-and-place.

- [ ] **P2.5 — Calibration procedure, written down.** Joint offsets,
  workspace limits measured on the real arm (not guessed), table plane,
  and the resulting `WorkspaceLimits` values.
  **AC:** `docs/CALIBRATION.md` lets a second person reproduce the numbers.

- [ ] **P2.6 — Sim/real parity test.** Same script, same config, both
  backends; compare the recorded call logs.
  **AC:** the two `move_to` sequences are identical; any divergence is explained in `design/simulation.md`.

- [ ] **P2.7 — Emergency stop that actually stops.** Verify `stop()`
  cuts torque on hardware, and that it is reachable from a keyboard
  interrupt during a run.
  **AC:** a witnessed test where the arm halts mid-trajectory on demand.

---

## Phase 3 — Teleoperation and data collection

- [ ] **P3.1 — Leader/follower teleop working through LeLab.**
  **AC:** a human drives the follower arm end to end for one pick-and-place.

- [ ] **P3.2 — Camera rig.** Number, placement and mounting of cameras
  fixed and documented; wrist camera decided yes/no with a reason.
  **AC:** `docs/PHYSICAL_SETUP.md` updated with the final rig and photos.

- [ ] **P3.3 — Record demonstrations in `LeRobotDataset` v2.**
  **AC:** a dataset of ≥50 cube pick-and-place episodes replays frame-accurately.

- [ ] **P3.4 — Publish to the HF Hub.** Dataset card documents the rig,
  the episode protocol, and known failure cases.
  **AC:** a stranger can `load_dataset` it and understand what they got.

- [ ] **P3.5 — Episode quality gate.** A script that flags episodes with
  dropped frames, desynchronised camera/state timestamps, or failed
  grasps, before they poison training.
  **AC:** the script rejects a deliberately corrupted episode.

---

## Phase 4 — Perception (YOLO on chess pieces)

- [ ] **P4.1 — Board registration with fiducials.** ArUco markers at the
  board corners give a deterministic board→robot transform, independent
  of the learned detector. This is the fallback that keeps the system
  debuggable when the detector is wrong.
  **AC:** the four corner squares' measured robot-frame positions match the model within a stated tolerance.

- [ ] **P4.2 — Hand-eye calibration.** Camera→robot transform, measured.
  **AC:** a piece placed at a known square is localised to within a stated millimetre error.

- [ ] **P4.3 — Piece image dataset.** Collect and label real images
  across lighting conditions and board angles. Record class balance.
  **AC:** a versioned dataset with a documented train/val/test split, split by *scene* not by frame.

- [ ] **P4.4 — Fine-tune YOLO on the 12 piece classes.**
  **AC:** mAP@50 reported on the held-out split, with a confusion matrix showing which pieces are mistaken for which.

- [ ] **P4.5 — Detections → board state.** Map detections onto the 8×8
  grid via the registration from P4.1; resolve conflicts explicitly.
  **AC:** the pipeline reconstructs a known board position with a measured per-square accuracy.

- [ ] **P4.6 — Perception failure policy.** What happens on low
  confidence, an occluded square, or an illegal reconstructed position.
  The answer must not be "pick anyway."
  **AC:** a test where a deliberately occluded board causes a refusal, not a grasp.

---

## Phase 5 — Learned policies (diffusion)

Ordered simplest → most effective, as decided. Each policy is trained on
the same dataset and evaluated with the same harness, so the comparison
is real.

- [ ] **P5.1 — Evaluation harness first.** Success rate over N trials
  from randomised start states, in sim and on hardware, with a fixed
  seed and a written success criterion.
  **AC:** the harness scores the Phase 1 scripted baseline — that number is the bar every policy must beat.

- [ ] **P5.2 — Baseline: Diffusion Policy (UNet, LeRobot implementation).**
  **AC:** trained to convergence, W&B run linked, success rate reported against the P5.1 baseline.

- [ ] **P5.3 — Diffusion Policy (Transformer backbone).**
  **AC:** same harness, same dataset, delta vs. P5.2 reported.

- [ ] **P5.4 — Survey the remaining HF/LeRobot diffusion-family policies**
  (e.g. consistency- or flow-matching-based variants) and pick the next
  one on stated criteria: inference latency on the robot machine, data
  requirement, reported performance.
  **AC:** `design/policies.md` records the shortlist, the criteria, and the choice.

- [ ] **P5.5 — Train the chosen advanced policy.**
  **AC:** same harness, delta reported, and an honest statement of what it did *not* improve.

- [ ] **P5.6 — Policy behind the same seam.** A learned policy must be
  swappable for the scripted planner without touching the safety layer or
  the robot interface.
  **AC:** the safety layer rejects an out-of-workspace *policy* action exactly as it rejects a scripted one — proven by a test.

- [ ] **P5.7 — Latency budget.** Measure inference time and the
  resulting control frequency on the real machine.
  **AC:** a number, and a statement of whether it is fast enough for closed-loop control.

---

## Phase 6 — Chess task integration

- [ ] **P6.1 — Chess engine integration.** `python-chess` + an engine;
  legal-move generation and game state.
  **AC:** the system proposes a legal move from a board state.

- [ ] **P6.2 — Move → manipulation plan.** `e2e4` becomes pick(e2),
  place(e4), including the special cases that break the naive mapping:
  captures (remove the captured piece first), castling (two pieces),
  en passant, promotion.
  **AC:** a test covering all four special cases produces the correct primitive sequence.

- [ ] **P6.3 — World model.** The board state representation that sits
  between perception and planning, with an explicit answer to: what
  happens when the observed board disagrees with the expected board.
  **AC:** a detected illegal transition halts the game loop and reports.

- [ ] **P6.4 — Full game loop.** Observe → reconstruct → decide → plan →
  execute → verify.
  **AC:** a complete game played against a human, with the failure modes logged.

- [ ] **P6.5 — Recovery behaviours.** Dropped piece, piece knocked over,
  piece placed off-centre.
  **AC:** each of the three is triggered deliberately and handled without a crash or an unsafe motion.

---

## Phase 7 — Evaluation and publication

- [ ] **P7.1 — Consolidated results.** Success rates for every stage,
  scripted vs. each learned policy, sim vs. real.
- [ ] **P7.2 — Experiment write-ups.** One `EXP-XXX` file per experiment,
  following the existing EXP-001 template.
- [ ] **P7.3 — Failure gallery.** Video and analysis of what does not
  work. This is the most credible part of any robotics portfolio.
- [ ] **P7.4 — Reproduction guide.** Bill of materials, setup, commands.
- [ ] **P7.5 — Docker image** for the GPU and robot machines.
  **AC:** a fresh machine runs training and evaluation from the image alone.

---

## Architecture revisions required

`docs/ARCHITECTURE.md` is marked *Proposed / Under Review*. These are the
concrete gaps found by reading it against the code that exists.

- [ ] **A.1 — `Pose` cannot express orientation.** It is `(x, y, z)`
  only (`primitives.py:9-18`). Grasping a chess piece requires at least a
  gripper yaw, and anything beyond a top-down grasp requires full
  orientation. This is the single largest gap between the current
  interface and the stated chess goal, and it invalidates parts of the
  `manipulation/` design.
  **Decision needed:** add `roll/pitch/yaw` or a quaternion to `Pose`, or
  state explicitly that the system is top-down-grasp-only forever.

- [ ] **A.2 — `RobotInterface` is write-only.** It has no `get_state()`,
  no joint feedback, no gripper feedback. The system therefore cannot
  detect a failed grasp, cannot close a control loop, and cannot support
  any learned policy that consumes proprioception — which every diffusion
  policy in Phase 5 does.
  **Decision needed:** the observation half of the interface, before Phase 5.

- [ ] **A.3 — No async / timing model.** `move_to` is implicitly
  blocking, but nothing says so, and nothing defines what "the move
  finished" means (commanded? settled within tolerance? timed out?).
  **Decision needed:** state the contract in the docstring and enforce it in both backends.

- [ ] **A.4 — Safety layer is advisory, not enforcing.** See P1.6 and
  P1.7: it gates the paths that choose to route through it. Document the
  true guarantee.

- [ ] **A.5 — `perception/` and `planning/` are empty directories.**
  The architecture describes them in detail; no interface exists. Define
  the seam (what a detection is, what a plan is) before writing either.

- [ ] **A.6 — Where does the simulator live in the diagram?**
  ARCHITECTURE.md shows LeRobot → SO100/SO101 with no simulation branch,
  yet MuJoCo is now a day-one dependency.
  **Decision needed:** update the diagram so sim and hardware are visibly the same seam.

- [ ] **A.7 — Split ARCHITECTURE.md.** At 938 lines it is not reviewable.
  Keep the diagrams and module boundaries there; move every rationale
  into `design/<topic>.md` where decisions carry measurements.

---

## Open questions

1. Does the SO100's reachable workspace actually cover a full-size chess
   board, or does the board need to be smaller than standard? **Measure
   before designing around it** — this constrains everything downstream.
2. One arm or two? Captures are much simpler with somewhere to put pieces.
3. Fixed overhead camera, wrist camera, or both?
4. Is the target a full game, or a reliable single-move demonstration?
   The second is a far stronger portfolio piece than an unreliable first.
5. Sim-to-real: is MuJoCo used for policy *training*, or only for
   development and regression testing? The answer changes how much
   effort domain randomisation deserves.
