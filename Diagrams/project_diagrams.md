# Arnold Project Documentation Diagrams

This document contains diagrams documenting the architecture, class structure, and execution flow of the Arnold Reinforcement Learning agent.

## 1. System Architecture Diagram

This diagram illustrates the high-level interaction between the main components: the Agent (Trainer & Model), the Environment (VizDoom), and the Data Storage (Replay Memory).

```mermaid
graph TD
    subgraph Environment [VizDoom Environment]
        Game[Game Instance]
    end

    subgraph Agent [Arnold Agent]
        Trainer[Trainer / ReplayMemoryTrainer]
        Model[DQN Network]
    end

    subgraph Storage [Data Storage]
        Memory[Replay Memory]
    end

    %% Flow interactions
    Game -- Observations (Screen, Variables) --> Trainer
    Trainer -- Observations --> Model
    Model -- Action --> Trainer
    Trainer -- Execute Action --> Game
    
    %% Training Loop
    Trainer -- Store Experience (State, Action, Reward) --> Memory
    Memory -- Sample Batch --> Trainer
    Trainer -- Train Batch --> Model
    Model -- Loss / Gradients --> Trainer
```

## 2. UML Class Diagram

This diagram details the static structure of the codebase, showing the relationships and inheritance between the core classes found in `src/trainer.py`, `src/doom/game.py`, `src/replay_memory.py`, and `src/model/dqn/base.py`.

```mermaid
classDiagram
    %% Inheritance
    Trainer <|-- ReplayMemoryTrainer
    nn_Module <|-- DQNModuleBase

    %% Associations
    Trainer --> Game : manages
    Trainer --> DQN : uses
    ReplayMemoryTrainer --> ReplayMemory : owns
    DQN --> DQNModuleBase : wraps

    class Trainer {
        +params
        +game
        +network
        +optimizer
        +n_iter
        +start_game()
        +run()
        +evaluate_model()
        +dump_model()
        +sync_update_parameters()
    }

    class ReplayMemoryTrainer {
        +replay_memory
        +game_iter(last_states, action)
        +training_step(current_loss)
    }

    class Game {
        +scenario
        +screen_resolution
        +variables
        +visible
        +start()
        +reset()
        +observe_state()
        +make_action(action)
        +is_final()
        +is_player_dead()
        +close()
    }

    class ReplayMemory {
        +max_size
        +cursor
        +full
        +screens
        +actions
        +rewards
        +add(screen, variables, action, reward, is_final)
        +get_batch(batch_size, hist_size)
    }

    class DQN {
        +module : DQNModuleBase
        +params
        +reset()
        +next_action(last_states)
        +f_train(loss_history, ...)
    }

    class DQNModuleBase {
        +conv_output_dim
        +output_dim
        +dropout_layer
        +base_forward(x_screens, x_variables)
        +head_forward(state_input)
    }

    %% External classes (simplified)
    class nn_Module {
        <<PyTorch>>
    }
```

## 3. Sequence Diagram (Training Loop)

This diagram visualizes the critical path of the `run()` method in `Trainer.py`, showing how the system executes a single training iteration.

```mermaid
sequenceDiagram
    participant Game
    participant Trainer
    participant Network
    participant Memory as ReplayMemory

    Note over Trainer: Start Training Loop (run)
    
    loop Every Iteration
        Trainer->>Game: observe_state(last_states)
        Game-->>Trainer: Current State

        alt Select Action
            Trainer->>Network: next_action(last_states)
            Network-->>Trainer: Action ID
        else Epsilon Greedy
            Trainer->>Trainer: Random Action
        end

        Trainer->>Game: make_action(action)
        Game-->>Trainer: New State (Internal)

        Note over Trainer: Store Experience
        Trainer->>Memory: add(screen, vars, action, reward...)

        alt Training Step
            Trainer->>Memory: get_batch(batch_size)
            Memory-->>Trainer: Batch Data
            Trainer->>Network: f_train(Batch Data)
            Network-->>Trainer: Loss
            Trainer->>Network: optimizer.step() (Update Weights)
        end

        alt Evaluation Period
            Trainer->>Game: close()
            Trainer->>Network: eval_fn()
            Trainer->>Game: start()
        end
    end
```
