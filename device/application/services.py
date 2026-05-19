"""Device application services.

Orchestrates telemetry record creation by coordinating cross-context
device verification, domain validation, and persistence.
"""

from device.domain.services import DeviceTelemetryService
from device.infrastructure.repositories import DeviceTelemetryRepository
from iam.infrastructure.repositories import DeviceRepository


class DeviceTelemetryAppService:
    """Application service for device telemetry workflows.

    Coordinates between IAM (device verification), Device domain
    (CO2/PM2.5 validation), and Device infrastructure (persistence).
    """

    def __init__(self):
        self.telemetry_repository = DeviceTelemetryRepository()
        self.telemetry_service = DeviceTelemetryService()
        self.device_repository = DeviceRepository()

    def create_telemetry_record(self, hardware_id, co2, pm25, created_at):
        """Create and persist a validated telemetry record.

        Args:
            hardware_id: Physical hardware identifier of the source device.
            co2: CO2 concentration in ppm.
            pm25: PM2.5 concentration in µg/m³.
            created_at: ISO 8601 timestamp string or None.

        Returns:
            The persisted DeviceTelemetry domain entity with assigned ID.

        Raises:
            ValueError: If CO2/PM2.5 invalid, or timestamp malformed.
        """
        device = self.device_repository.find_by_hardware_id(hardware_id)
        if device is None:
            raise ValueError("Device not found")

        record = self.telemetry_service.create_record(hardware_id, co2, pm25, created_at)
        return self.telemetry_repository.save(record)
