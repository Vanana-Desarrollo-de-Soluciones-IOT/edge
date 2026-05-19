"""CreateFullTelemetryRecordCommand — command to create an optimized telemetry record.

Immutable command representing the intention to persist the lightweight
telemetry reading sent by the embedded device.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateFullTelemetryRecordCommand:
    """Command to create an optimized device telemetry record.

    Attributes:
        hardware_id: Physical hardware identifier from X-Hardware-Id header.
        device_time: Device local time string (e.g., "14:30:25").
        uptime: System uptime as string (e.g., "00:00:20").
        air_quality: Dict with co2, temperature, humidity.
        particulate_matter: Dict with pm1_0, pm2_5, pm10.
        connectivity: Dict with status.
        status: Overall device status string.
        created_at: Optional timestamp override.
    """
    hardware_id: str
    device_time: str
    uptime: str
    air_quality: dict
    particulate_matter: dict
    connectivity: dict
    status: str
    created_at: Optional[str] = None

    def __post_init__(self):
        if not self.hardware_id:
            raise ValueError("hardware_id is required")
        if not self.device_time:
            raise ValueError("device_time is required")
        if not self.uptime:
            raise ValueError("uptime is required")
        if not isinstance(self.air_quality, dict):
            raise ValueError("air_quality must be a dict")
        if not isinstance(self.particulate_matter, dict):
            raise ValueError("particulate_matter must be a dict")
        if not isinstance(self.connectivity, dict):
            raise ValueError("connectivity must be a dict")
        if not self.status:
            raise ValueError("status is required")
