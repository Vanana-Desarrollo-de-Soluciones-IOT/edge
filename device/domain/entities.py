"""DeviceTelemetry entity — aggregate root of the Device bounded context.

Represents the optimized telemetry reading received from the embedded device.
"""

from datetime import datetime
from typing import Optional

from device.domain.valueobjects import AirQuality, Connectivity, ParticulateMatter


class DeviceTelemetry:
    """Aggregate root entity representing an optimized device telemetry reading.

    Encapsulates only the data sent by the embedded device in the lightweight
    payload: environmental sensors, connectivity status, and overall state.

    Attributes:
        id: Auto-incremented database ID (None before persistence).
        device_id: Logical identifier of the source device.
        device_time: Device local time as string (e.g., "14:30:25").
        uptime_seconds: System uptime in seconds (parsed from HH:MM:SS).
        air_quality: SCD41 CO2/temperature/humidity readings (value object).
        particulate_matter: PMS5003 PM1.0/PM2.5/PM10 readings (value object).
        connectivity: WiFi connection status (value object).
        status: Overall device status string.
        recorded_at: UTC timestamp when the reading was recorded by edge.
    """

    def __init__(
        self,
        device_id: str,
        device_time: str,
        uptime_seconds: int,
        air_quality: AirQuality,
        particulate_matter: ParticulateMatter,
        connectivity: Connectivity,
        status: str,
        recorded_at: datetime,
        id: Optional[int] = None,
    ):
        if not device_id:
            raise ValueError("device_id is required")
        if not device_time:
            raise ValueError("device_time is required")
        if air_quality is None:
            raise ValueError("air_quality is required")
        if particulate_matter is None:
            raise ValueError("particulate_matter is required")
        if connectivity is None:
            raise ValueError("connectivity is required")
        if not status:
            raise ValueError("status is required")
        if recorded_at is None:
            raise ValueError("recorded_at is required")

        self.id = id
        self.device_id = device_id
        self.device_time = device_time
        self.uptime_seconds = uptime_seconds
        self.air_quality = air_quality
        self.particulate_matter = particulate_matter
        self.connectivity = connectivity
        self.status = status
        self.recorded_at = recorded_at

    def get_co2(self) -> float:
        """Get CO2 concentration from air quality readings."""
        return self.air_quality.co2

    def get_pm2_5(self) -> float:
        """Get PM2.5 concentration from particulate matter readings."""
        return float(self.particulate_matter.pm2_5)
