"""Command for synchronizing pending commands from clair-core."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SynchronizeDeviceCommandsCommand:
    limit: int = 100

    def __post_init__(self):
        if self.limit <= 0:
            raise ValueError("limit must be positive")
