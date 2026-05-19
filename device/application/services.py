"""Device application services.

Orchestrates complete telemetry record creation by coordinating cross-context
device verification, domain validation, persistence, and forward to clair-core.
"""

import logging

from device.application.outboundservices.acl.external_core_service import (
    ExternalCoreService,
)
from device.domain.commands import CreateFullTelemetryRecordCommand
from device.domain.entities import DeviceTelemetry
from device.domain.services import DeviceTelemetryService
from device.infrastructure.repositories import DeviceTelemetryRepository
from iam.infrastructure.repositories import DeviceRepository

logger = logging.getLogger(__name__)


class DeviceTelemetryAppService:
    """Application service for complete device telemetry workflows.

    Coordinates between IAM (device verification), Device domain
    (full telemetry validation), Device infrastructure (local persistence),
    and the clair-core Evaluation context (forward via ACL).
    """

    def __init__(self):
        self.telemetry_repository = DeviceTelemetryRepository()
        self.telemetry_service = DeviceTelemetryService()
        self.device_repository = DeviceRepository()
        self.external_core_service = ExternalCoreService()

    def create_full_telemetry_record(
        self,
        command: CreateFullTelemetryRecordCommand,
        raw_payload: dict | None = None,
    ) -> DeviceTelemetry:
        """Create, persist locally, and forward to clair-core a telemetry record.

        Args:
            command: CreateFullTelemetryRecordCommand with all device telemetry data.
            raw_payload: Optional original device payload dict to forward to Core.

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

        # Persist locally
        persisted = self.telemetry_repository.save(record)

        # Forward the original payload to clair-core (best-effort, non-blocking)
        if raw_payload is not None:
            try:
                ok = self.external_core_service.forward_raw_payload(
                    device.api_key, raw_payload
                )
                if not ok:
                    logger.warning("Telemetry forward to clair-core was not acknowledged")
            except Exception as exc:
                logger.warning("Telemetry forward to clair-core failed: %s", exc)

        return persisted
