"""Device application services.

Orchestrates telemetry record creation by coordinating cross-context
device verification, domain validation, local persistence, and guaranteed
outbound delivery to clair-core via the outbox pattern.
"""

import json
import logging
from datetime import datetime, timezone

from device.domain.commands import CreateFullTelemetryRecordCommand
from device.domain.entities import DeviceTelemetry
from device.domain.outbox_entry import OutboxEntry
from device.domain.services import DeviceTelemetryService
from device.infrastructure.outbox.outbox_repository import OutboxRepository
from device.infrastructure.repositories import DeviceTelemetryRepository
from iam.infrastructure.repositories import DeviceRepository
from shared.infrastructure.database import db

logger = logging.getLogger(__name__)


class DeviceTelemetryAppService:
    """Application service for device telemetry workflows.

    Coordinates between IAM (device verification), Device domain
    (telemetry validation), Device infrastructure (local persistence),
    and the outbox (guaranteed forward to clair-core).
    """

    def __init__(self):
        self.telemetry_repository = DeviceTelemetryRepository()
        self.telemetry_service = DeviceTelemetryService()
        self.device_repository = DeviceRepository()
        self.outbox_repository = OutboxRepository()

    def create_full_telemetry_record(
        self,
        command: CreateFullTelemetryRecordCommand,
        raw_payload: dict | None = None,
    ) -> DeviceTelemetry:
        """Create, persist locally, and queue for core delivery a telemetry record.

        The raw payload is written to the outbox table within the same
        database transaction as the telemetry record, ensuring at-least-once
        delivery without blocking the device response.

        Args:
            command: CreateFullTelemetryRecordCommand with device telemetry data.
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

        # Create the telemetry entity via domain service
        record = self.telemetry_service.create_record_from_command(command)

        # Persist locally and enqueue outbox entry atomically
        with db.atomic():
            persisted = self.telemetry_repository.save(record)

            if raw_payload is not None:
                try:
                    outbox_entry = OutboxEntry(
                        device_id=command.hardware_id,
                        payload=json.dumps(raw_payload),
                        api_key=device.api_key,
                    )
                    self.outbox_repository.save(outbox_entry)
                except Exception as exc:
                    logger.warning("Failed to create outbox entry: %s", exc)

        return persisted
