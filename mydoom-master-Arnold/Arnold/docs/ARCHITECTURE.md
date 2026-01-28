# Arnold — Architecture Overview

Project: Arnold — a VizDoom reinforcement-learning agent and training framework.

High-level components
- Entrypoint: `arnold.py` and `run.sh` — CLI / orchestration for training or evaluation.
- Core training: `src/trainer.py` — training loop, episode control, optimization steps.
- Replay & Data: `src/replay_memory.py` — experience replay buffer for RL.
- Parameter server / coordination: `src/parameter_server.py` — parameter sync or checkpointing.
- Experiment infra: `src/logger.py`, `src/args.py`, `bots.cfg` — logging, CLI args, bot configuration.
- Utilities: `src/utils.py` — common helpers (I/O, seeding, env wrappers).
- Models: `src/model/*` — neural networks used by the agent (DQN feedforward, recurrent variants, embeddings, helpers).
- Doom integration: `src/doom/*` — VizDoom wrappers, action mapping, reward shaping, scenarios and scenario definitions.
- Resources and assets: `resources/` (WADs, scenario files) and `pretrained/` (saved model weights).
- Dumped runs: `dumped/` — training logs, saved params, and run artifacts.

Data & control flow (summary)
- The CLI (`arnold.py`) parses args (`src/args.py`) and config (`bots.cfg`) then constructs environments from `src/doom` and model from `src/model`.
- `src/trainer.py` runs episodes, collects transitions to `src/replay_memory.py`, samples minibatches, and updates `src/model` networks.
- `src/parameter_server.py` likely handles shared parameters (for multi-process or distributed training) and checkpoints.
- `src/logger.py` records metrics to `dumped/` and prints progress.

Key dependencies (likely)
- Python 3.x, PyTorch, VizDoom, NumPy; check `README.md` for exact requirements.

Repository layout
- `arnold.py` — main entrypoint
- `run.sh` — convenience runner
- `src/` — source code (modules: `model`, `doom`, training infra)
- `resources/` — level files and scenario assets
- `pretrained/` — example pretrained weights (.pth)
- `dumped/` — example output and logs

Recommended next steps when forking/updating
- Run `python3 arnold.py --help` to verify CLI and required envs (VizDoom).
- Add a `requirements.txt` or `pyproject.toml` if missing; pin PyTorch & VizDoom versions.
- Add short README sections describing how to reproduce training/eval and where to place VizDoom resources.
- If you plan to modify training, add unit tests around small helpers in `src/utils.py` and model forward passes.

Notes
- This architecture doc is inferred from file layout — see `docs/FILES.md` for per-file summaries and follow-ups for accuracy checks.
