"""DeviceTelemetry repository — infrastructure layer.

Provides data access operations for the DeviceTelemetry aggregate root,
mapping between Peewee models and domain entities.
"""

from typing import Optional

from device.domain.entities import DeviceTelemetry
from device.domain.valueobjects import AirQuality, Connectivity, ParticulateMatter
from device.infrastructure.models import DeviceTelemetryModel


class DeviceTelemetryRepository:
    """Repository for DeviceTelemetry aggregate root persistence."""

    def save(self, telemetry: DeviceTelemetry) -> DeviceTelemetry:
        """Persist a telemetry record to the database.

        Args:
            telemetry: A DeviceTelemetry domain entity to persist.

        Returns:
            A new DeviceTelemetry domain entity with the database-assigned ID.
        """
        model = DeviceTelemetryModel.create(
            device_id=telemetry.device_id,
            device_time=telemetry.device_time,
            uptime_seconds=telemetry.uptime_seconds,
            co2=telemetry.air_quality.co2,
            temperature=telemetry.air_quality.temperature,
            humidity=telemetry.air_quality.humidity,
            air_quality_valid=telemetry.air_quality.valid,
            pm1_0=telemetry.particulate_matter.pm1_0,
            pm2_5=telemetry.particulate_matter.pm2_5,
            pm10=telemetry.particulate_matter.pm10,
            pm_valid=telemetry.particulate_matter.valid,
            wifi_status=telemetry.connectivity.status,
            status=telemetry.status,
            recorded_at=telemetry.recorded_at,
        )

        return self._model_to_entity(model)

    def find_by_id(self, record_id: int) -> Optional[DeviceTelemetry]:
        """Find a telemetry record by its database ID.

        Args:
            record_id: The database ID to search for.

        Returns:
            DeviceTelemetry entity if found, None otherwise.
        """
        try:
            model = DeviceTelemetryModel.get(DeviceTelemetryModel.id == record_id)
            return self._model_to_entity(model)
        except DeviceTelemetryModel.DoesNotExist:
            return None

    def _model_to_entity(self, model: DeviceTelemetryModel) -> DeviceTelemetry:
        """Convert a Peewee model instance to a DeviceTelemetry domain entity.

        Args:
            model: A DeviceTelemetryModel instance from the database.

        Returns:
            A fully populated DeviceTelemetry domain entity.
        """
        air_quality = AirQuality(
            co2=model.co2,
            temperature=model.temperature,
            humidity=model.humidity,
            valid=model.air_quality_valid,
        )

        particulate_matter = ParticulateMatter(
            pm1_0=model.pm1_0,
            pm2_5=model.pm2_5,
            pm10=model.pm10,
            valid=model.pm_valid,
        )

        connectivity = Connectivity(
            status=model.wifi_status,
        )

        return DeviceTelemetry(
            id=model.id,
            device_id=model.device_id,
            device_time=model.device_time,
            uptime_seconds=model.uptime_seconds,
            air_quality=air_quality,
            particulate_matter=particulate_matter,
            connectivity=connectivity,
            status=model.status,
            recorded_at=model.recorded_at,
        )
