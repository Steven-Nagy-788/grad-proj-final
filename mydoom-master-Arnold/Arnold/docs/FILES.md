# Files Reference — per-file summaries

This file lists repository files with short inferred descriptions to help when forking or modifying the project.

- `run.sh`: Shell helper that starts training/evaluation using the project's CLI.
- `README.md`: Project overview, usage notes and setup instructions (open for exact steps).
- `bots.cfg`: Bot configuration file (likely mapping bot names to policies or parameters).
- `arnold.py`: Primary Python entrypoint; parses arguments and starts training/evaluation workflows.

- `src/__init__.py`: Package initializer for `src`.
- `src/utils.py`: Generic utilities used across the project (I/O, seeding, helper functions).
- `src/trainer.py`: Training loop and orchestration of episodes, environment steps, optimization.
- `src/replay_memory.py`: Experience replay buffer implementation for sampling transitions.
- `src/parameter_server.py`: Parameter server or checkpointing orchestration (used for sync or saving weights).
- `src/logger.py`: Logging and metrics collection utilities.
- `src/args.py`: Command-line argument parsing helpers and default argument sets.

- `pretrained/vizdoom_2017_track2.pth`: Pretrained model weights (binary PyTorch checkpoint).
- `pretrained/vizdoom_2017_track1.pth`: Pretrained model weights (binary PyTorch checkpoint).
- `pretrained/health_gathering.pth`: Pretrained agent for health gathering scenario.
- `pretrained/defend_the_center.pth`: Pretrained agent for defend-the-center scenario.
- `pretrained/deathmatch_shotgun.pth`: Pretrained agent for deathmatch shotgun scenario.

- `resources/freedoom2.wad`: Doom engine resource file (map/assets) used by VizDoom.

- `src/model/__init__.py`: Model package initializer.
- `src/model/utils.py`: Model-related helpers (weight init, layers, common ops).
- `src/model/bucketed_embedding.py`: Embedding utilities (bucketed embeddings for discrete features).

- `docs/example.gif`: Example animation or visualization demonstrating agent behavior.

- `src/doom/__init__.py`: Doom integration package initializer.
- `src/doom/utils.py`: VizDoom-specific utilities and environment helpers.
- `src/doom/reward.py`: Reward shaping functions for different scenarios.
- `src/doom/labels.py`: Label definitions and mappings for game state elements.
- `src/doom/game_features.py`: Feature extraction from the raw game state (observations).
- `src/doom/game.py`: Low-level wrapper around VizDoom environment creation and stepping.
- `src/doom/actions.py`: Action space definition and action mapping helpers.

- `resources/scenarios/health_gathering_supreme.wad`: Scenario asset for health_gathering (supreme variant).
- `resources/scenarios/health_gathering.wad`: Health gathering scenario WAD.
- `resources/scenarios/full_deathmatch.wad`: Full deathmatch scenario asset.
- `resources/scenarios/defend_the_center.wad`: Defend-the-center scenario asset.
- `resources/scenarios/deathmatch_shotgun.wad`: Deathmatch shotgun scenario asset.
- `resources/scenarios/deathmatch_rockets.wad`: Deathmatch rockets scenario asset.

- `src/model/dqn/__init__.py`: DQN subpackage initializer.
- `src/model/dqn/recurrent.py`: Recurrent DQN model implementation (RNN/LSTM-based agent networks).
- `src/model/dqn/feedforward.py`: Feedforward DQN model implementation (CNN/MLP agent networks).
- `src/model/dqn/base.py`: Base model abstractions shared by the DQN variants.

- `src/doom/scenarios/__init__.py`: Scenarios package initializer.
- `src/doom/scenarios/self_play.py`: Scenario runner for self-play experiments.
- `src/doom/scenarios/health_gathering.py`: Scenario glue for health gathering tasks.
- `src/doom/scenarios/defend_the_center.py`: Scenario glue for defend-the-center tasks.
- `src/doom/scenarios/deathmatch.py`: Scenario glue for deathmatch tasks.
- `src/doom/scenarios/deathmatch-eval.py`: Evaluation harness or variants for deathmatch.

- `dumped/test/ulxm0jwfth/train.log`: Example training log from a previous run.
- `dumped/test/ulxm0jwfth/params.pkl`: Example saved parameters/state for the run.
- `dumped/test/5az3wx4hlb/train.log`: Example training log from a previous run.
- `dumped/test/5az3wx4hlb/params.pkl`: Example saved parameters/state for the run.
- `dumped/test/bnyesf8ia3/train.log`: Example training log from a previous run.
- `dumped/test/bnyesf8ia3/params.pkl`: Example saved parameters/state for the run.
- `dumped/test/4py72ea66e/train.log`: Example training log from a previous run.
- `dumped/test/4py72ea66e/params.pkl`: Example saved parameters/state for the run.

How to use this file
- Use these one-line summaries as a starting point. To improve accuracy, open each file and copy the module-level docstring / function list into `docs/FILES.md`.
- If you want, I can open each source file and extract the top-level comments, function/class names, and produce a richer 3–6 line summary per file.
