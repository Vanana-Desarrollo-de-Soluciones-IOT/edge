"""Device domain services.

Contains business rules for CO2/PM2.5 data validation
and timestamp normalization.
"""

from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

from device.domain.entities import DeviceTelemetry


class DeviceTelemetryService:
    """Domain service for telemetry data validation and creation.

    Enforces business rules:
    - CO2 must be a valid float in range [0, 5000] ppm
    - PM2.5 must be a valid float in range [0, 500] µg/m³
    - Timestamps are normalized to UTC
    """

    @staticmethod
    def create_record(device_id, co2, pm25, created_at=None):
        """Validate inputs and create a DeviceTelemetry domain entity.

        Args:
            device_id: Logical identifier of the source device.
            co2: CO2 concentration in ppm (will be cast to float).
            pm25: PM2.5 concentration in µg/m³ (will be cast to float).
            created_at: ISO 8601 string, datetime, or None (defaults to UTC now).

        Returns:
            A validated DeviceTelemetry domain entity.

        Raises:
            ValueError: If co2 or pm25 are not valid numbers or out of range,
                        or if created_at cannot be parsed.
        """
        # Validate CO2
        try:
            co2 = float(co2)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid CO2 value: {co2}")

        if co2 < 0 or co2 > 5000:
            raise ValueError(f"CO2 must be between 0 and 5000 ppm, got {co2}")

        # Validate PM2.5
        try:
            pm25 = float(pm25)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid PM2.5 value: {pm25}")

        if pm25 < 0 or pm25 > 500:
            raise ValueError(f"PM2.5 must be between 0 and 500 µg/m³, got {pm25}")

        # Parse timestamp
        if created_at is None:
            parsed_created_at = datetime.now(timezone.utc)
        elif isinstance(created_at, str):
            parsed_created_at = dateutil_parser.parse(created_at).astimezone(timezone.utc)
        else:
            parsed_created_at = created_at.astimezone(timezone.utc)

        return DeviceTelemetry(
            device_id=device_id,
            co2=co2,
            pm25=pm25,
            created_at=parsed_created_at,
        )
