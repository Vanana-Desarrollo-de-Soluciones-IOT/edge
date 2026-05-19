"""Device application services.

Orchestrates complete telemetry record creation by coordinating cross-context
device verification, domain validation, and persistence of all device data.
"""

from device.domain.commands import CreateFullTelemetryRecordCommand
from device.domain.entities import DeviceTelemetry
from device.domain.services import DeviceTelemetryService
from device.infrastructure.repositories import DeviceTelemetryRepository
from iam.infrastructure.repositories import DeviceRepository


class DeviceTelemetryAppService:
    """Application service for complete device telemetry workflows.

    Coordinates between IAM (device verification), Device domain
    (full telemetry validation), and Device infrastructure (persistence).
    """

    def __init__(self):
        self.telemetry_repository = DeviceTelemetryRepository()
        self.telemetry_service = DeviceTelemetryService()
        self.device_repository = DeviceRepository()

    def create_full_telemetry_record(self, command: CreateFullTelemetryRecordCommand) -> DeviceTelemetry:
        """Create and persist a complete validated telemetry record.

        This method:
        1. Verifies the device exists in IAM
        2. Creates value objects and validates all data via domain service
        3. Persists the complete telemetry record with all fields

        Args:
            command: CreateFullTelemetryRecordCommand with all device telemetry data.

        Returns:
            The persisted DeviceTelemetry domain entity with assigned ID.

        Raises:
            ValueError: If device not found, or any validation fails.
        """
        # Verify device exists in IAM
        device = self.device_repository.find_by_hardware_id(command.hardware_id)
        if device is None:
            raise ValueError(f"Device not found: {command.hardware_id}")

        # Create the complete telemetry entity via domain service
        record = self.telemetry_service.create_record_from_command(command)

        # Persist and return
        return self.telemetry_repository.save(record)
