from dataclasses import dataclass


@dataclass(frozen=True)
class SynchronizeDevicesCommand:
    """Command to replace or upsert the local device cache from clair-core."""

    devices: list[dict]

    def __post_init__(self):
        if self.devices is None:
            raise ValueError("devices is required")
