"""
Log parser service for Arnold training/testing logs.
Parses train.log files and extracts structured events.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class ParsedEventType(str, Enum):
    """Types of events extracted from logs."""
    RUN_START = "run_start"
    CONFIG = "config"
    ITERATION = "iteration"
    HEALTH_CHANGE = "health_change"
    AMMO_CHANGE = "ammo_change"
    KILL = "kill"
    DEATH = "death"
    EPISODE_START = "episode_start"
    EPISODE_END = "episode_end"
    EVALUATION_START = "evaluation_start"
    EVALUATION_END = "evaluation_end"
    MODEL_SAVE = "model_save"


@dataclass
class ParsedEvent:
    """A single parsed event from the log."""
    event_type: ParsedEventType
    timestamp: datetime
    elapsed_time: str  # e.g., "0:01:34"
    data: Dict[str, Any] = field(default_factory=dict)
    raw_line: str = ""
    line_number: int = 0


@dataclass
class ParsedRun:
    """Complete parsed run from a log file."""
    log_path: str
    scenario: str
    config: Dict[str, Any]
    events: List[ParsedEvent]
    
    # Summary stats
    total_iterations: int = 0
    total_episodes: int = 0
    final_avg_kills: Optional[float] = None
    best_score: Optional[float] = None


class LogParser:
    """
    Parser for Arnold training/testing logs.
    
    Example usage:
        parser = LogParser()
        run = parser.parse_file("/path/to/train.log")
        for event in run.events:
            print(event.event_type, event.data)
    """
    
    # Regex patterns for log parsing
    PATTERNS = {
        # INFO [365664] - 01/30/26 03:34:56 - 0:00:00 - message
        "log_line": re.compile(
            r'INFO \[(\d+)\] - (\d{2}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) - (\d+:\d{2}:\d{2}) - (.+)'
        ),
        
        # Health changes: Lost health (100 -> 60)
        "health_change": re.compile(r'Lost health \((\d+) -> (-?\d+)\)'),
        
        # Ammo changes: Lost ammo: bullets (56 -> 55)
        "ammo_change": re.compile(r'Lost ammo: (\w+) \((\d+) -> (\d+)\)'),
        
        # Kill event
        "kill": re.compile(r'^Kill$'),
        
        # Death event
        "death": re.compile(r'^Dead$'),
        
        # Episode markers
        "new_episode": re.compile(r'^New episode$'),
        "episode_separator": re.compile(r'^===============$'),
        "kills_count": re.compile(r'^(\d+) kills?\.$'),
        
        # Iteration: === Iteration 400
        "iteration": re.compile(r'^=== Iteration (\d+)$'),
        
        # DQN loss: DQN loss: 0.19955
        "dqn_loss": re.compile(r'^DQN loss: ([\d.]+)$'),
        
        # Scenario: scenario: defend_the_center
        "scenario": re.compile(r'^scenario: (\w+)$'),
        
        # Evaluation start
        "eval_start": re.compile(r'^Evaluating the model\.\.\.$'),
        
        # Summary line: 1586 iterations on 20 episodes.
        "summary": re.compile(r'^(\d+) iterations on (\d+) episodes\.$'),
        
        # Average kills: 0.400000 kills / episode average.
        "avg_kills": re.compile(r'^([\d.]+) kills / episode average\.$'),
        
        # Best score: New best score: 0.400000
        "best_score": re.compile(r'^New best score: ([\d.]+)$'),
        
        # Model save: Best model dump: path
        "model_save": re.compile(r'^Best model dump: (.+)$'),
        
        # Training on map: Training on map 1 ...
        "training_map": re.compile(r'^Training on map (\d+) \.\.\.$'),
    }
    
    def __init__(self):
        self.current_episode = 0
        self.current_iteration = 0
        self.in_evaluation = False
    
    def parse_file(self, log_path: str) -> ParsedRun:
        """Parse a complete log file and return structured data."""
        path = Path(log_path)
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")
        
        events: List[ParsedEvent] = []
        config: Dict[str, Any] = {}
        scenario = ""
        
        with open(path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip()
                if not line:
                    continue
                
                parsed = self._parse_line(line, line_num)
                if parsed:
                    events.append(parsed)
                    
                    # Extract config/scenario from early events
                    if parsed.event_type == ParsedEventType.CONFIG:
                        if "scenario" in parsed.data:
                            scenario = parsed.data["scenario"]
                        config.update(parsed.data)
        
        # Build summary
        run = ParsedRun(
            log_path=str(path),
            scenario=scenario,
            config=config,
            events=events,
            total_iterations=self.current_iteration,
            total_episodes=self.current_episode,
        )
        
        # Extract final stats from events
        for event in reversed(events):
            if event.event_type == ParsedEventType.EVALUATION_END:
                if "avg_kills" in event.data:
                    run.final_avg_kills = event.data["avg_kills"]
                break
        
        for event in events:
            if event.event_type == ParsedEventType.MODEL_SAVE:
                run.best_score = event.data.get("score")
        
        return run
    
    def _parse_line(self, line: str, line_num: int) -> Optional[ParsedEvent]:
        """Parse a single log line."""
        
        # Match the standard log format
        match = self.PATTERNS["log_line"].match(line)
        if not match:
            # Handle config continuation lines (indented)
            if line.startswith("                "):
                # These are config continuation lines, skip for now
                return None
            return None
        
        pid, date_str, time_str, elapsed, message = match.groups()
        
        # Parse timestamp
        timestamp = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M:%S")
        
        # Create base event
        event = ParsedEvent(
            event_type=ParsedEventType.ITERATION,  # Default, will be overridden
            timestamp=timestamp,
            elapsed_time=elapsed,
            raw_line=line,
            line_number=line_num,
        )
        
        # Match against content patterns
        message = message.strip()
        
        # Run start
        if message == "========== Running DOOM ==========":
            event.event_type = ParsedEventType.RUN_START
            return event
        
        # Scenario
        m = self.PATTERNS["scenario"].match(message)
        if m:
            event.event_type = ParsedEventType.CONFIG
            event.data = {"scenario": m.group(1)}
            return event
        
        # Iteration
        m = self.PATTERNS["iteration"].match(message)
        if m:
            self.current_iteration = int(m.group(1))
            event.event_type = ParsedEventType.ITERATION
            event.data = {"iteration": self.current_iteration}
            return event
        
        # DQN loss
        m = self.PATTERNS["dqn_loss"].match(message)
        if m:
            event.event_type = ParsedEventType.ITERATION
            event.data = {"loss": float(m.group(1)), "iteration": self.current_iteration}
            return event
        
        # Health change
        m = self.PATTERNS["health_change"].match(message)
        if m:
            event.event_type = ParsedEventType.HEALTH_CHANGE
            event.data = {
                "old": int(m.group(1)),
                "new": int(m.group(2)),
                "episode": self.current_episode
            }
            return event
        
        # Ammo change
        m = self.PATTERNS["ammo_change"].match(message)
        if m:
            event.event_type = ParsedEventType.AMMO_CHANGE
            event.data = {
                "type": m.group(1),
                "old": int(m.group(2)),
                "new": int(m.group(3)),
                "episode": self.current_episode
            }
            return event
        
        # Kill
        if self.PATTERNS["kill"].match(message):
            event.event_type = ParsedEventType.KILL
            event.data = {"episode": self.current_episode}
            return event
        
        # Death
        if self.PATTERNS["death"].match(message):
            event.event_type = ParsedEventType.DEATH
            event.data = {"episode": self.current_episode}
            return event
        
        # New episode
        if self.PATTERNS["new_episode"].match(message):
            self.current_episode += 1
            event.event_type = ParsedEventType.EPISODE_START
            event.data = {"episode": self.current_episode}
            return event
        
        # Kills count (end of episode)
        m = self.PATTERNS["kills_count"].match(message)
        if m:
            event.event_type = ParsedEventType.EPISODE_END
            event.data = {"kills": int(m.group(1)), "episode": self.current_episode}
            return event
        
        # Evaluation start
        if self.PATTERNS["eval_start"].match(message):
            self.in_evaluation = True
            event.event_type = ParsedEventType.EVALUATION_START
            event.data = {"iteration": self.current_iteration}
            return event
        
        # Summary (end of evaluation)
        m = self.PATTERNS["summary"].match(message)
        if m:
            event.event_type = ParsedEventType.EVALUATION_END
            event.data = {
                "iterations": int(m.group(1)),
                "episodes": int(m.group(2)),
                "iteration": self.current_iteration
            }
            self.in_evaluation = False
            return event
        
        # Average kills
        m = self.PATTERNS["avg_kills"].match(message)
        if m:
            event.event_type = ParsedEventType.EVALUATION_END
            event.data = {"avg_kills": float(m.group(1))}
            return event
        
        # Best score
        m = self.PATTERNS["best_score"].match(message)
        if m:
            event.event_type = ParsedEventType.MODEL_SAVE
            event.data = {"score": float(m.group(1))}
            return event
        
        # Model save
        m = self.PATTERNS["model_save"].match(message)
        if m:
            event.event_type = ParsedEventType.MODEL_SAVE
            event.data = {"path": m.group(1)}
            return event
        
        # Unrecognized - skip
        return None
    
    def stream_parse(self, log_path: str) -> Generator[ParsedEvent, None, None]:
        """
        Generator that yields events as they are parsed.
        Useful for large files or real-time processing.
        """
        path = Path(log_path)
        with open(path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip()
                if not line:
                    continue
                
                parsed = self._parse_line(line, line_num)
                if parsed:
                    yield parsed


def calculate_metrics(run: ParsedRun) -> Dict[str, Any]:
    """
    Calculate aggregated metrics from a parsed run.
    Returns dict matching the Metric model fields.
    """
    total_kills = 0
    total_deaths = 0
    kills_by_episode: Dict[int, int] = {}
    health_values: List[int] = []
    damage_taken = 0
    losses: List[float] = []
    
    current_episode_kills = 0
    last_health = 100
    
    for event in run.events:
        if event.event_type == ParsedEventType.KILL:
            total_kills += 1
            current_episode_kills += 1
            
        elif event.event_type == ParsedEventType.DEATH:
            total_deaths += 1
            
        elif event.event_type == ParsedEventType.HEALTH_CHANGE:
            old_health = event.data.get("old", 100)
            new_health = event.data.get("new", 0)
            health_values.append(new_health)
            if new_health < old_health:
                damage_taken += (old_health - new_health)
            last_health = new_health
            
        elif event.event_type == ParsedEventType.EPISODE_START:
            episode = event.data.get("episode", 0)
            if episode > 1:
                kills_by_episode[episode - 1] = current_episode_kills
            current_episode_kills = 0
            last_health = 100
            
        elif event.event_type == ParsedEventType.EPISODE_END:
            episode = event.data.get("episode", 0)
            kills_by_episode[episode] = event.data.get("kills", current_episode_kills)
            current_episode_kills = 0
            
        elif event.event_type == ParsedEventType.ITERATION:
            if "loss" in event.data:
                losses.append(event.data["loss"])
    
    # Calculate aggregates
    kills_list = list(kills_by_episode.values()) if kills_by_episode else [0]
    avg_kills = sum(kills_list) / len(kills_list) if kills_list else 0
    
    avg_health = sum(health_values) / len(health_values) if health_values else 100
    min_health = min(health_values) if health_values else 0
    
    # Hardness score calculation (0-100)
    # Higher deaths = harder, lower avg kills = harder, lower avg health = harder
    death_factor = min(total_deaths / max(run.total_episodes, 1), 1.0) * 35
    kill_factor = max(0, (1 - avg_kills / 10)) * 25 if avg_kills < 10 else 0
    health_factor = max(0, (1 - avg_health / 100)) * 20
    stuck_factor = 0  # TODO: implement stuck detection
    
    hardness_score = death_factor + kill_factor + health_factor + stuck_factor
    hardness_score = min(100, max(0, hardness_score))
    
    return {
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "avg_kills_per_episode": round(avg_kills, 2),
        "min_kills": min(kills_list) if kills_list else 0,
        "max_kills": max(kills_list) if kills_list else 0,
        "avg_health": round(avg_health, 2),
        "min_health": min_health,
        "total_damage_taken": damage_taken,
        "final_loss": losses[-1] if losses else None,
        "avg_loss": round(sum(losses) / len(losses), 5) if losses else None,
        "hardness_score": round(hardness_score, 2),
        "solvability": total_deaths < run.total_episodes if run.total_episodes > 0 else None,
    }
