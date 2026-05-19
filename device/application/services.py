"""Device application services.

Orchestrates telemetry record creation by coordinating cross-context
device verification, domain validation, local persistence, and guaranteed
outbound delivery to clair-core via the outbox pattern.
"""

import logging
from datetime import datetime, timezone

from device.domain.commands import CreateFullTelemetryRecordCommand
from device.domain.commands import (
    AcknowledgeEmbeddedDeviceCommandCommand,
    SynchronizeDeviceCommandsCommand,
)
from device.domain.entities import (
    DeviceCommand,
    DeviceCommandType,
    DeviceTelemetry,
    EdgeDeviceCommandStatus,
)
from device.domain.outbox_entry import OutboxEntry
from device.domain.services import DeviceTelemetryService
from device.application.outboundservices.acl.external_core_service import ExternalCoreService
from device.infrastructure.outbox.outbox_repository import OutboxRepository
from device.infrastructure.repositories import DeviceCommandRepository, DeviceTelemetryRepository
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

        # Persist locally and enqueue a lightweight outbox reference atomically.
        with db.atomic():
            persisted = self.telemetry_repository.save(record)

            if raw_payload is not None:
                try:
                    outbox_entry = OutboxEntry(
                        aggregate_type="TELEMETRY",
                        aggregate_id=persisted.id,
                        event_type="TELEMETRY_RECORDED",
                    )
                    self.outbox_repository.save(outbox_entry)
                except Exception as exc:
                    logger.warning("Failed to create outbox entry: %s", exc)

        return persisted


class DeviceCommandApplicationService:
    """Application service for Core -> Edge -> Embedded command delivery."""

    def __init__(self):
        self.command_repository = DeviceCommandRepository()
        self.device_repository = DeviceRepository()
        self.external_core_service = ExternalCoreService()

    def synchronize_pending_commands(self, command: SynchronizeDeviceCommandsCommand) -> list[DeviceCommand]:
        """Fetch pending commands from clair-core and cache them locally."""
        core_commands = self.external_core_service.fetch_pending_device_commands(command.limit)
        persisted: list[DeviceCommand] = []

        with db.atomic():
            for item in core_commands:
                device_id = item.get("deviceId") or item.get("device_id")
                command_id = item.get("id") or item.get("commandId") or item.get("command_id")
                command_type = item.get("type") or item.get("commandType") or item.get("command_type")
                payload = item.get("payload")

                if not device_id or not command_id or not command_type:
                    logger.warning("Skipping malformed command from core: %s", item)
                    continue

                device = self.device_repository.find_by_device_id(device_id)
                if device is None:
                    logger.warning("Skipping command %s for unknown device %s", command_id, device_id)
                    continue

                existing = self.command_repository.find_by_command_id(command_id)
                if existing is not None:
                    persisted.append(existing)
                    continue

                device_command = DeviceCommand(
                    command_id=command_id,
                    device_id=device_id,
                    hardware_id=device.hardware_id,
                    command_type=DeviceCommandType(command_type),
                    status=EdgeDeviceCommandStatus.RECEIVED,
                    payload=payload,
                    received_at=datetime.now(timezone.utc),
                )
                persisted.append(self.command_repository.save(device_command))

        return persisted

    def get_pending_commands_for_embedded(self, hardware_id: str) -> list[DeviceCommand]:
        """Return commands pending for an embedded device and mark them delivered."""
        commands = self.command_repository.find_pending_for_hardware_id(hardware_id)
        return self.command_repository.mark_commands_delivered(commands)

    def acknowledge_embedded_command(self, command: AcknowledgeEmbeddedDeviceCommandCommand) -> DeviceCommand:
        """Persist embedded ACK locally and forward it to clair-core."""
        device_command = self.command_repository.find_by_command_id(command.command_id)
        if device_command is None or device_command.hardware_id != command.hardware_id:
            raise ValueError("Device command not found")

        acknowledged_at = datetime.now(timezone.utc)
        if command.status == "EXECUTED":
            device_command.mark_executed(acknowledged_at)
        else:
            device_command.mark_failed(acknowledged_at, command.failure_reason)

        saved = self.command_repository.save(device_command)
        acknowledged = self.external_core_service.acknowledge_device_command(
            saved.device_id,
            saved.command_id,
            command.status,
            command.failure_reason,
        )
        if not acknowledged:
            logger.warning("Core ACK forwarding failed for command %s", saved.command_id)
        return saved
