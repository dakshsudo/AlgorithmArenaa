"""Playback run states."""
from enum import Enum

class RunState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
