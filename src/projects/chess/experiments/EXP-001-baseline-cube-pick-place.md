 Experiment 1: Deterministic Manipulation baseline - Pick and place  
  Isolating manipulation from perception
  
  
                   Command
                      │
                      ▼
              Pick & Place Task
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    Pick Position           Place Position
          │                       │
          └───────────┬───────────┘
                      ▼
              Motion Planner
                      │
                      ▼
             Motion Primitives
                      │
                      ▼
               Safety Layer
                      │
                      ▼
                 SO100


Setup:

                 SO100

                   ↓

             ┌───────────┐
             │           │
             │   CUBE    │
             │           │
             └───────────┘

                  ↓

             ┌───────────┐
             │   TARGET  │
             └───────────┘