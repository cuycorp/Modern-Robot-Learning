
# Physical Setup

**Version:** 0.2  

**Status:** Active Development |  Under Review

**Source:** https://notebook.google.com/notebook/612c495f-c236-45f4-a50d-7f120b382b22 

## Reccomendations based on Papers | Experimentation of Researchers

## Sim to Real Robotic Learning
To establish a robust real-to-sim-to-real robotic learning pipeline in your laboratory, you must design a system that tightly couples precise physical-visual alignment, asynchronous data collection tools, automated visual digitization, and hybrid co-training paradigms.
The direct answer to achieving this pipeline successfully involves a four-part strategy: first, construct a physical workspace featuring physical overlay alignment tools and hardware-linked teleoperation devices (such as USB foot pedals); second, digitize the environment using 3D Gaussian Splatting paired with generative object reconstructors; third, train your policies in simulation using delta action spaces, System 2 heuristic progress trackers, and structured-noise flow matching; and fourth, deploy a human-in-the-loop DAgger pipeline that dynamically weights manual corrections and uses parallel, asynchronous simulation workers to eliminate human downtime.

#### Detailed Recommendations
##### A. Physical Laboratory Setup & Teleoperation Infrastructure
A high-yield real-world setup requires hardware and software tools designed to maximize human demonstration efficiency and minimize sensory mismatches.

* Human-Intervention Rig (DAgger Setup):
USB Foot Pedals: When performing DAgger or teleoperation, your hands will be fully occupied controlling the robot. Integrate a cheap three-button USB foot pedal into your workstation
. Program the pedals to handle critical pipeline actions—such as starting/stopping policy rollouts, saving successful episodes, or discarding failed trials
.
Leader-Follower Arm Tracking: To prevent control jumps, jitters, or spatial lag when a human intervenes, set up a physical leader-follower configuration
. The leader arms must actively and physically track the positions of the follower arms in real-time so that when you take manual control, the transition is seamless and free of trajectory jumps

* Sensor & Camera Alignment:
Visual Overlay Tool: Minor camera shifts drastically degrade policy performance
. Develop a script that loads historical frames from your target training dataset, moves your physical robot arms to the exact corresponding joint coordinates, and displays a live-camera-to-historical-frame transparency overlay
. This allows you to hand-adjust your cameras and tables to achieve a near-perfect visual match

Domain Randomization & Purposed Miscalibration: Do not try to maintain a fragile, perfectly static setup. On purpose, miscalibrate and shift your cameras by a few centimeters periodically, and run daily arm calibrations
. This forces the neural network to generalize rather than overfitting to a single camera pose
. Apply heavy training-time visual augmentations (random blurs, color shifts, white balance adjustments, and random cutout rectangles) to shield the policy from real-world lighting changes
.
Physical Gripper Matching: If you cannot replicate the exact colors of your simulation or target robot arms, 3D print matching outer shells or grippers (e.g., bright orange grippers) so the visual perspective of your wrist-mounted cameras matches perfectly
.
##### B. Workspace Digitization & Scene Reconstruction
To bypass manual modeling and asset-creation bottlenecks, use visual digitization pipelines to construct your simulation.
Background and Object Scanning:
2D Gaussian Splatting: Scan your physical lab environment and extract meshes using 2D Gaussian Splatting
. This technique provides visually rich backgrounds and handles complex reflection characteristics much more easily than handcrafted simulations
.
Generative Object Reconstruction: For objects on the table, use generative models (like Trellis or Sand 3D) to construct complete 3D assets from single-view or multi-view images, bypassing occlusions caused by the table surface
.
Generative Trajectory & Flow Extraction (Modular Alternative):
If physical scanning is unavailable, you can generate reference videos of tasks using text-guided generative video models (such as Gemini or One)
.
Lift these 2D videos to metric 3D using monocular depth estimation calibrated against your initial real depth image
. Track 3D point flows (actionable flow) or hand-pose trajectories using MegaSAM and Tap3D to provide geometric guidance to the robot via trajectory optimization or MPC
.
Use rejection sampling via a large Vision-Language Model (VLM) to analyze parallel video rollouts (generating 8 to 16 in parallel) and filter out physical hallucinations or tracking errors

##### C. Policy Design & Simulation Infrastructure
Training a model that transfers effectively between sim and real requires designing appropriate action representations, training compositions, and temporal architectures.
Action Space Representations:
Delta Arm, Absolute Hand: Control your robot arm using a delta action space (relative position changes), which significantly improves exploration and stability over absolute joints
. Keep gripper or fine-finger controls absolute or binary (simple grasp/release commands) to reduce control complexity
.
Latency Modeling: You must explicitly model visual and tracking latencies (e.g., ~100ms delays in pose trackers) directly inside your simulator
. If omitted, the policy will fail in the real world, often dropping or re-grasping objects due to temporal confusion
.
Data Mixing & Co-Training:
The 10% Co-Training Rule: Do not rely on pure zero-shot transfer
. Co-train your real-world data with a small slice of simulation data (e.g., 90% real-world data and 10% out-of-distribution simulation data in your training batch)
. This small sim co-training mix acts as a visual regularizer, teaching the policy to ignore minor visual artifacts, splat fuzziness, or lighting mismatches without overfitting to the evaluation task
.
Speed Alignment: Apply speed-up/slow-down scaling coefficients to your datasets
. Slow down fast simulation-generated behaviors and speed up sluggish human teleoperation trajectories to prevent policy action multi-modality
.
Temporal Stability & Progress Tracking:
System 2 Heuristic Progress Tracker: Sequential tasks often suffer from temporal ambiguity (e.g., starting a task looks identical to ending it)
. Group your task into 5 to 15 discrete stages
. Train your model to predict the current stage, and feed that stage back as an input token—isolated carefully with an attention block mask to prevent leakage
. Use a voting-based System 2 filter during inference to only allow incremental stage transitions
.
Action Chunking with Soft Inpainting: Predict actions in chunks (e.g., 30 steps representing 1 second)
. To smooth transitions between independent chunks, execute only the first 26 steps and use the remaining 4 as soft-inpainted conditioning inputs for the next chunk, guided by your action correlation matrix
. Squeeze and execute action chunks slightly faster using cubic interpolation to boost physical throughput
.
Noise Correlation in Flow Matching: If using flow matching, avoid starting from uncorrelated white noise
. Start from noise that matches the actual temporal correlation structure of your robot actions to eliminate training shortcuts and balance gradient dynamics

##### D. DAgger & Human-in-the-Loop Implementation
To scale your data efficiently, build an asynchronous framework for collecting corrective actions.
Asynchronous Multi-Simulation Preloading: If running DAgger in simulation, launch multiple environments in parallel using a multi-worker asynchronous queue
. While you are correcting a robot in Worker 1, Worker 2 should be saving your previous rollout, and Worker 3 should be preloading the next complex garment or scenario
. This completely eliminates simulation loading latency for the human operator
.
Heuristic Fail State Extraction: Run parallel simulations in the cloud autonomously
. Use heuristics (such as sudden drops in predicted success probability or task completion) to detect failure points
. Automatically save the environment state and robot positions at these failure points into a hard cases database for you to target and correct later
.
Closed-Loop Correction Validation: After you manually correct a difficult state, let the policy resume autonomy from your final state
. If the policy successfully finishes the task, accept and save your correction to the training mix
. If the policy still fails, discard your correction to keep your dataset clean from poor human demonstrations

### Comprehensive Summary
An optimized real-to-sim pipeline transitions from a simple, isolated laboratory environment into an intelligent, data-scaling machine. You begin by physically setting up two robot arms with an adjustable table and a USB foot pedal to streamline human interaction
. You visually align the physical cameras using a custom visual overlay tool
, and use 2D Gaussian Splatting to digitize your real setup into a highly accurate visual simulator
.
When training begins, you run a two-stage teacher-student reinforcement learning loop or co-train using a 90% real / 10% sim data mix to bridge the visual gap
. Your models should predict delta action spaces in action chunks to prevent physical drift, stabilized by a Heuristic System 2 Progress Tracker to resolve temporal ambiguities
. Finally, you execute an active DAgger loop where parallel simulation workers preload failed scenarios, allowing you to quickly input bottleneck corrections
. This combined approach of structured visual alignment, deliberate data mixing, and targeted human correction guarantees a highly robust policy capable of zero-shot real-world deployment.

## Physical setup

To set up your physical real-to-sim laboratory environment effectively, you should construct a bimanual workspace with a solid white background, standardized 3D-printed colored grippers (matching your simulation's visual assets), a fixed arm-to-arm spacing of approximately 46 cm, a top-view RGB-D camera, and a three-button USB foot pedal for hands-free workflow management
. This physical rig must connect to an operator station featuring two leader arms mounted on an adjustable table that actively mirror the follower arms' autonomous movements
. This mirroring setup is crucial because it allows you to step in and execute seamless, zero-jitter human-in-the-loop (DAgger) corrections without controller jumps
.
#### Detailed Recommendations
##### 1. Tabletop Workspace & Hardware Selection
Arm Spacing and Reach Limits: Position your dual follower arms at a distance of approximately 46 cm
. Because compact bimanual arms have limited range, adult-sized garments or large household objects will likely spill off your table
. Sourcing specialized kid-sized clothes or compact tools is necessary to ensure the arms can complete tasks within their reachable workspace
.
Visual Gripper Matching: 3D-print matching outer shells or grippers (such as orange grippers) for your physical robot
. This guarantees that your robot's wrist cameras see identical visual features (colors and geometry) in both the physical lab and your simulated environment
.
Background and Workspace Setup: Use a clean, solid white background for the tabletop surface to simplify visual segmentation and depth processing
.
End-Effector Considerations: If you are focusing on tool manipulation, the choice of hand is highly important. Thinner-fingered hands (like the Sharpa hand) make it much easier to scoop underneath flat objects compared to bulkier hands (like the Allegro hand)
. However, note that highly geared dexterous hands are stiff and less compliant for direct force control
.
##### 2. Camera Placement, Alignment, & Calibration
Sensor Configuration: Position wrist-mounted cameras near each gripper and place a top-view camera (such as a RealSense RGB-D camera) directly above the table
. To keep latency low, your policies can be trained on scaled-down, low-resolution feeds (e.g., 224x224 or 128x128 RGB images) while ignoring high-definition depth data during policy rollout
.
The Visual Overlay Alignment Tool: Manually aligning your top camera to match a simulator or a reference dataset is incredibly challenging. To solve this, develop a script that reads joint states from a reference frame, drives the physical robot arms to those exact joint positions, and displays a live-camera-to-historical-frame transparency overlay
. You can then adjust the physical camera’s height, angle, and rotation until the live and reference images perfectly align
.
Deliberate Miscalibration (Robustness): On purpose, miscalibrate and shift your top camera by a few centimeters or rotate it slightly from day to day
. Recalibrate your arms frequently so that they undergo slight, manual variations
. This intentional noise prevents the policy from overfitting to a highly specific camera position and ensures it remains robust during evaluations
.
Occlusion and Object Size: When utilizing real-world object pose trackers (such as Foundation Pose), avoid tiny objects
. A physical hand can occlude up to 80% of a small object, causing the pose tracker to fail or experience high latency
. Select larger tools (such as brushes or hammers) with distinct, visible grasping handles
.
##### 3. Human-in-the-Loop (DAgger) Infrastructure
Hands-Free USB Foot Pedal: Connect a cheap, plastic three-button USB foot pedal via USB to your workstation
. Because your hands will be fully occupied manipulating the leader arms, map the pedals to critical workflow actions: button one to start/pause a policy rollout, button two to save a successful recovery episode to your dataset, and button three to instantly discard a failed or glitched episode
.
Active mirroring Leader Arms: Set up your operator station with two leader arms
. Program these leader arms to physically mirror the follower arms while the policy is running autonomously
. This keeps your hands in the exact spatial coordinates of the robot at all times, meaning you can press your foot pedal to take instant manual control with zero trajectory jumps or lag
.
Cable and Power Management: A bimanual rig at a workstation or dining table involves a minimum of eight USB connections, four independent power sources, and HDMI displays
. Spend time organizing this cabling so that wires do not physically snag or limit the high-velocity movements of your robot arms
.
### Summary of the Setup
In summary, a real-to-sim physical setup must balance physical-to-sim alignment with human operational efficiency. Your table should feature a white background with bimanual arms spaced 46 cm apart, utilizing 3D-printed colored grippers, a top-view RealSense camera, and wrist-mounted sensors
. To prevent your model from failing due to minor real-world variations, use a custom camera-overlay tool to align your initial viewpoints, and then deliberately randomize camera positions and arm calibrations daily
. Finally, link the rig to a mirroring leader-follower workstation equipped with a USB foot pedal
. This allows you to easily step in, correct mistakes at policy bottlenecks, and seamlessly compile highly valuable recovery data
.


## Reccomendations based on personal experimentation

[to be tested in lab]

## Resources

How We Trained a Robot to Do 50 Household Tasks in Simulation (BEHAVIOR Challenge 1st place) | https://www.youtube.com/watch?v=J4wpO0EdCZs&list=PLVjt7Jt0DBaM&index=7

Trained on a Dining Table, Deployed at the ICRA Robotics Conference. How to Make Your Policy Robust | https://www.youtube.com/watch?v=0j2B2cXoiu4

Ep#82: SimTooReal: An Object-Centric Policy for Zero-Shot Dexterous Tool Manipulation | https://www.youtube.com/watch?v=dsXB33MK6no

Ep#63: NovaFlow: Zero-Shot Manipulation via Actionable Flow from Generated Videos | https://www.youtube.com/watch?v=N7I5TosoAeI

Ep#60: Sim-to-Real Manipulation with VIRAL and Doorman | https://www.youtube.com/watch?v=0lHC6Et10V4

Ep#62: PolaRiS: Scalable Real-to-Sim Evaluations for Generalist Robot Policies | https://www.youtube.com/watch?v=pwGI527luV8

Ep#19 Learning to Drive from a World Model | https://www.youtube.com/watch?v=XCoz_oqpDw0

Ep#11 Sim-and-Real Co-Training: A Simple Recipe for Vision-Based Robotic Manipulation | https://www.youtube.com/watch?v=Rk3Gieu19JI