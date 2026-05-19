"""Device domain services.

Contains business rules for telemetry data validation, timestamp normalization,
and creation of complete DeviceTelemetry aggregate roots with all value objects.
"""

from datetime import datetime, timezone
from typing import Optional

from dateutil import parser as dateutil_parser

from device.domain.commands import CreateFullTelemetryRecordCommand
from device.domain.entities import DeviceTelemetry
from device.domain.valueobjects import (
    AirQuality,
    Connectivity,
    DeviceHealth,
    DeviceInfo,
    ParticulateMatter,
)


class DeviceTelemetryService:
    """Domain service for complete telemetry validation and creation.

    Enforces business rules:
    - All sensor readings must be within valid ranges
    - Value objects validate their own invariants
    - Timestamps are normalized to UTC
    """

    @staticmethod
    def create_record_from_command(command: CreateFullTelemetryRecordCommand) -> DeviceTelemetry:
        """Validate command data and create a complete DeviceTelemetry entity.

        This method creates value objects from the raw command data, which perform
        their own validation. Then constructs the aggregate root with all data.

        Args:
            command: CreateFullTelemetryRecordCommand with all device data.

        Returns:
            A validated DeviceTelemetry aggregate root entity.

        Raises:
            ValueError: If any validation fails in value objects or entity creation.
        """
        # Create value objects from command data (validation happens in __post_init__)
        air_quality = AirQuality.from_dict(command.air_quality)
        particulate_matter = ParticulateMatter.from_dict(command.particulate_matter)
        connectivity = Connectivity.from_dict(command.connectivity)
        device_health = DeviceHealth.from_dict(command.device_health)
        device_info = DeviceInfo.from_dict(command.device_info)

        # Parse timestamp - use provided or current UTC time
        recorded_at = DeviceTelemetryService._parse_timestamp(command.created_at)

        # Create and return the aggregate root
        return DeviceTelemetry(
            device_id=command.hardware_id,
            device_timestamp=command.device_timestamp,
            uptime_seconds=command.uptime_seconds,
            air_quality=air_quality,
            particulate_matter=particulate_matter,
            connectivity=connectivity,
            device_health=device_health,
            device_info=device_info,
            status=command.status,
            status_code=command.status_code,
            recorded_at=recorded_at,
        )

    @staticmethod
    def _parse_timestamp(created_at: Optional[str]) -> datetime:
        """Parse timestamp string to UTC datetime.

        Args:
            created_at: ISO 8601 timestamp string or None.

        Returns:
            UTC datetime.

        Raises:
            ValueError: If timestamp cannot be parsed.
        """
        if created_at is None:
            return datetime.now(timezone.utc)

        try:
            parsed = dateutil_parser.parse(created_at)
            return parsed.astimezone(timezone.utc)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid timestamp format: {created_at}") from e
