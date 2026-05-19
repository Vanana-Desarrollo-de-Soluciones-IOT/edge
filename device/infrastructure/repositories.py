"""DeviceTelemetry repository — infrastructure layer.

Provides data access operations for the DeviceTelemetry aggregate root,
mapping between Peewee models and domain entities with all value objects.
"""

from datetime import datetime, timezone
from typing import Optional

from device.domain.entities import DeviceTelemetry
from device.domain.valueobjects import (
    AirQuality,
    Connectivity,
    DeviceHealth,
    DeviceInfo,
    ParticulateMatter,
)
from device.infrastructure.models import DeviceTelemetryModel


class DeviceTelemetryRepository:
    """Repository for DeviceTelemetry aggregate root persistence.

    Handles database operations for complete telemetry records, translating between
    Peewee ORM models (infrastructure) and DeviceTelemetry domain entities
    with all value objects (AirQuality, ParticulateMatter, Connectivity, etc.).
    """

    def save(self, telemetry: DeviceTelemetry) -> DeviceTelemetry:
        """Persist a complete telemetry record to the database.

        Args:
            telemetry: A DeviceTelemetry domain entity to persist.

        Returns:
            A new DeviceTelemetry domain entity with the database-assigned ID.
        """
        model = DeviceTelemetryModel.create(
            # Device identification
            device_id=telemetry.device_id,

            # Timestamps
            device_timestamp=telemetry.device_timestamp,
            uptime_seconds=telemetry.uptime_seconds,

            # Air quality (from value object)
            co2=telemetry.air_quality.co2,
            temperature=telemetry.air_quality.temperature,
            humidity=telemetry.air_quality.humidity,
            air_quality_valid=telemetry.air_quality.valid,

            # Particulate matter (from value object)
            pm1_0=telemetry.particulate_matter.pm1_0,
            pm2_5=telemetry.particulate_matter.pm2_5,
            pm10=telemetry.particulate_matter.pm10,
            pm_valid=telemetry.particulate_matter.valid,

            # Connectivity (from value object)
            wifi_status=telemetry.connectivity.status,
            wifi_ssid=telemetry.connectivity.ssid,
            wifi_ip=telemetry.connectivity.ip,
            wifi_rssi=telemetry.connectivity.rssi,
            wifi_mac=telemetry.connectivity.mac,
            wifi_channel=telemetry.connectivity.channel,

            # Device health (from value object)
            free_heap=telemetry.device_health.free_heap,
            min_free_heap=telemetry.device_health.min_free_heap,
            heap_size=telemetry.device_health.heap_size,
            max_alloc_heap=telemetry.device_health.max_alloc_heap,
            scd41_status=telemetry.device_health.scd41_status,
            pms5003_status=telemetry.device_health.pms5003_status,
            last_valid_air_quality_sec=telemetry.device_health.last_valid_air_quality_sec,
            last_valid_pm_sec=telemetry.device_health.last_valid_pm_sec,

            # Device info (from value object)
            chip_model=telemetry.device_info.chip_model,
            chip_revision=telemetry.device_info.chip_revision,
            cpu_freq_mhz=telemetry.device_info.cpu_freq_mhz,
            flash_size=telemetry.device_info.flash_size,
            sketch_size=telemetry.device_info.sketch_size,
            free_sketch_space=telemetry.device_info.free_sketch_space,

            # Status
            status=telemetry.status,
            status_code=telemetry.status_code,

            # Server timestamp
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

        This method performs explicit mapping between the infrastructure model
        and the domain entity, reconstructing all value objects.

        Args:
            model: A DeviceTelemetryModel instance from the database.

        Returns:
            A fully populated DeviceTelemetry domain entity.
        """
        # Reconstruct value objects from model fields
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
            ssid=model.wifi_ssid,
            ip=model.wifi_ip,
            rssi=model.wifi_rssi,
            mac=model.wifi_mac,
            channel=model.wifi_channel,
        )

        device_health = DeviceHealth(
            free_heap=model.free_heap,
            min_free_heap=model.min_free_heap,
            heap_size=model.heap_size,
            max_alloc_heap=model.max_alloc_heap,
            scd41_status=model.scd41_status,
            pms5003_status=model.pms5003_status,
            last_valid_air_quality_sec=model.last_valid_air_quality_sec,
            last_valid_pm_sec=model.last_valid_pm_sec,
        )

        device_info = DeviceInfo(
            chip_model=model.chip_model,
            chip_revision=model.chip_revision,
            cpu_freq_mhz=model.cpu_freq_mhz,
            flash_size=model.flash_size,
            sketch_size=model.sketch_size,
            free_sketch_space=model.free_sketch_space,
        )

        # Build and return the domain entity
        return DeviceTelemetry(
            id=model.id,
            device_id=model.device_id,
            device_timestamp=model.device_timestamp,
            uptime_seconds=model.uptime_seconds,
            air_quality=air_quality,
            particulate_matter=particulate_matter,
            connectivity=connectivity,
            device_health=device_health,
            device_info=device_info,
            status=model.status,
            status_code=model.status_code,
            recorded_at=model.recorded_at,
        )
