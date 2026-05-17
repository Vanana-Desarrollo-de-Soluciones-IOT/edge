"""DeviceTelemetry repository — infrastructure layer.

Provides data access operations for the DeviceTelemetry aggregate root,
mapping between Peewee models and domain entities.
"""

from device.domain.entities import DeviceTelemetry
from device.infrastructure.models import DeviceTelemetryModel


class DeviceTelemetryRepository:
    """Repository for DeviceTelemetry aggregate root persistence.

    Handles database operations for telemetry records, translating between
    Peewee ORM models (infrastructure) and DeviceTelemetry domain entities.
    """

    def save(self, telemetry):
        """Persist a telemetry record to the database.

        Args:
            telemetry: A DeviceTelemetry domain entity to persist.

        Returns:
            A new DeviceTelemetry domain entity with the database-assigned ID.
        """
        model = DeviceTelemetryModel.create(
            device_id=telemetry.device_id,
            co2=telemetry.co2,
            pm25=telemetry.pm25,
            created_at=telemetry.created_at,
        )
        return DeviceTelemetry(
            id=model.id,
            device_id=model.device_id,
            co2=model.co2,
            pm25=model.pm25,
            created_at=model.created_at,
        )
