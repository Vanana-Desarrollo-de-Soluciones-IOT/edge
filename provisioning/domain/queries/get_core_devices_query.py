from dataclasses import dataclass


@dataclass(frozen=True)
class GetCoreDevicesQuery:
    """Query to request provisioned device records from clair-core."""

    source_url: str

    def __post_init__(self):
        if not self.source_url:
            raise ValueError("source_url is required")
