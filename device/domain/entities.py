"""DeviceTelemetry entity — aggregate root of the Device bounded context.

Represents a complete telemetry reading from an IoT sensor device including
environmental data, connectivity status, device health, and hardware info.
"""

from datetime import datetime
from typing import Optional

from device.domain.valueobjects import (
    AirQuality,
    Connectivity,
    DeviceHealth,
    DeviceInfo,
    ParticulateMatter,
)


class DeviceTelemetry:
    """Aggregate root entity representing a complete device telemetry reading.

    This entity encapsulates all data sent by the embedded device in a single
    telemetry payload, including environmental sensors, connectivity status,
    system health metrics, and hardware information.

    Attributes:
        id: Auto-incremented database ID (None before persistence).
        device_id: Logical identifier of the source device.
        device_timestamp: Device uptime in milliseconds at time of reading.
        uptime_seconds: System uptime in seconds.
        air_quality: SCD41 CO2/temperature/humidity readings (value object).
        particulate_matter: PMS5003 PM1.0/PM2.5/PM10 readings (value object).
        connectivity: WiFi connection status (value object).
        device_health: System health metrics (value object).
        device_info: Hardware specifications (value object).
        status: Overall device status string.
        status_code: Numeric status code from device.
        recorded_at: UTC timestamp when the reading was recorded by edge.
    """

    def __init__(
        self,
        device_id: str,
        device_timestamp: int,
        uptime_seconds: int,
        air_quality: AirQuality,
        particulate_matter: ParticulateMatter,
        connectivity: Connectivity,
        device_health: DeviceHealth,
        device_info: DeviceInfo,
        status: str,
        status_code: int,
        recorded_at: datetime,
        id: Optional[int] = None,
    ):
        """Initialize a DeviceTelemetry aggregate root.

        Args:
            device_id: Logical device identifier.
            device_timestamp: Device internal timestamp (ms).
            uptime_seconds: Device uptime in seconds.
            air_quality: AirQuality value object.
            particulate_matter: ParticulateMatter value object.
            connectivity: Connectivity value object.
            device_health: DeviceHealth value object.
            device_info: DeviceInfo value object.
            status: Device status string.
            status_code: Numeric status code.
            recorded_at: UTC timestamp when recorded.
            id: Optional database ID (None for new records).

        Raises:
            ValueError: If required parameters are invalid.
        """
        if not device_id:
            raise ValueError("device_id is required")
        if air_quality is None:
            raise ValueError("air_quality is required")
        if particulate_matter is None:
            raise ValueError("particulate_matter is required")
        if connectivity is None:
            raise ValueError("connectivity is required")
        if device_health is None:
            raise ValueError("device_health is required")
        if device_info is None:
            raise ValueError("device_info is required")
        if not status:
            raise ValueError("status is required")
        if recorded_at is None:
            raise ValueError("recorded_at is required")

        self.id = id
        self.device_id = device_id
        self.device_timestamp = device_timestamp
        self.uptime_seconds = uptime_seconds
        self.air_quality = air_quality
        self.particulate_matter = particulate_matter
        self.connectivity = connectivity
        self.device_health = device_health
        self.device_info = device_info
        self.status = status
        self.status_code = status_code
        self.recorded_at = recorded_at

    def get_co2(self) -> float:
        """Get CO2 concentration from air quality readings."""
        return self.air_quality.co2

    def get_pm2_5(self) -> float:
        """Get PM2.5 concentration from particulate matter readings."""
        return float(self.particulate_matter.pm2_5)

    def is_air_quality_valid(self) -> bool:
        """Check if air quality sensor readings are valid."""
        return self.air_quality.valid

    def is_particulate_matter_valid(self) -> bool:
        """Check if particulate matter sensor readings are valid."""
        return self.particulate_matter.valid

    def get_signal_strength(self) -> int:
        """Get WiFi signal strength (RSSI)."""
        return self.connectivity.rssi

    def get_free_heap_percentage(self) -> float:
        """Calculate free heap as percentage of total heap."""
        if self.device_health.heap_size == 0:
            return 0.0
        return (self.device_health.free_heap / self.device_health.heap_size) * 100
