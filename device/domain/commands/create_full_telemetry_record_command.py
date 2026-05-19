"""CreateFullTelemetryRecordCommand — command to create complete telemetry record.

Immutable command representing the intention to persist a full telemetry reading
from an embedded device with all environmental, connectivity, health, and info data.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateFullTelemetryRecordCommand:
    """Command to create a complete device telemetry record.
    
    This command encapsulates all data sent by the embedded device including:
    - Environmental sensor readings (CO2, PM, temperature, humidity)
    - Connectivity status (WiFi, IP, RSSI)
    - Device health metrics (memory, sensor status)
    - Hardware information (chip model, frequencies)
    
    Attributes:
        hardware_id: Physical hardware identifier from X-Hardware-Id header.
        device_timestamp: Device internal timestamp in milliseconds.
        uptime_seconds: System uptime in seconds.
        air_quality: Dict with co2, temperature, humidity, valid.
        particulate_matter: Dict with pm1_0, pm2_5, pm10, valid.
        connectivity: Dict with status, ssid, ip, rssi, mac, channel.
        device_health: Dict with freeHeap, scd41Status, pms5003Status, etc.
        device_info: Dict with chipModel, cpuFreqMHz, flashSize, etc.
        status: Overall device status string.
        status_code: Numeric status code.
        created_at: Optional timestamp override.
    """
    hardware_id: str
    device_timestamp: int
    uptime_seconds: int
    air_quality: dict
    particulate_matter: dict
    connectivity: dict
    device_health: dict
    device_info: dict
    status: str
    status_code: int
    created_at: Optional[str] = None

    def __post_init__(self):
        """Validate command data."""
        if not self.hardware_id:
            raise ValueError("hardware_id is required")
        if not isinstance(self.air_quality, dict):
            raise ValueError("air_quality must be a dict")
        if not isinstance(self.particulate_matter, dict):
            raise ValueError("particulate_matter must be a dict")
        if not isinstance(self.connectivity, dict):
            raise ValueError("connectivity must be a dict")
        if not isinstance(self.device_health, dict):
            raise ValueError("device_health must be a dict")
        if not isinstance(self.device_info, dict):
            raise ValueError("device_info must be a dict")
        if not self.status:
            raise ValueError("status is required")
