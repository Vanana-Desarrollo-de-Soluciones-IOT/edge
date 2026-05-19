"""Device repository — infrastructure layer.

Provides data access operations for the Device aggregate root,
mapping between Peewee models and domain entities.
"""

from datetime import datetime, timezone
from typing import Optional

from iam.domain.entities import Device
from iam.infrastructure.models import DeviceModel


class DeviceRepository:
    """Repository for Device aggregate root persistence.

    Handles all database operations for devices, translating between
    Peewee ORM models (infrastructure) and Device domain entities.
    """

    def find_by_hardware_id_and_device_secret(self, hardware_id, device_secret):
        """Find a device by its hardware ID and device secret combination.

        Args:
            hardware_id: The physical hardware identifier.
            device_secret: The secret key provided by the physical embedded device.

        Returns:
            A Device domain entity if found, None otherwise.
        """
        try:
            model = DeviceModel.get(
                (DeviceModel.hardware_id == hardware_id) &
                (DeviceModel.device_secret == device_secret)
            )
            return Device(
                device_id=model.device_id,
                hardware_id=model.hardware_id,
                api_key=model.api_key,
                device_secret=model.device_secret,
                status=model.status,
                created_at=model.created_at,
                last_seen_at=model.last_seen_at,
            )
        except DeviceModel.DoesNotExist:
            return None

    def update_last_seen(self, hardware_id):
        """Update the last_seen_at timestamp for a device.

        Called after every successful authentication to track
        device activity and detect offline sensors.

        Args:
            hardware_id: The physical hardware identifier to update.
        """
        now = datetime.now(timezone.utc)
        DeviceModel.update(last_seen_at=now, status="ONLINE").where(
            DeviceModel.hardware_id == hardware_id
        ).execute()

    def mark_offline_stale_devices(self, offline_before: datetime) -> int:
        """Mark devices as OFFLINE when their last_seen_at is stale.

        Args:
            offline_before: Devices seen before this UTC timestamp become OFFLINE.

        Returns:
            Number of updated rows.
        """
        return (
            DeviceModel.update(status="OFFLINE")
            .where(
                (DeviceModel.last_seen_at.is_null(False))
                & (DeviceModel.last_seen_at < offline_before)
                & (DeviceModel.status != "OFFLINE")
            )
            .execute()
        )

    def find_by_hardware_id(self, hardware_id):
        """Find a device by its hardware ID (without validating credentials)."""
        try:
            model = DeviceModel.get(DeviceModel.hardware_id == hardware_id)
            return Device(
                device_id=model.device_id,
                hardware_id=model.hardware_id,
                api_key=model.api_key,
                device_secret=model.device_secret,
                status=model.status,
                created_at=model.created_at,
                last_seen_at=model.last_seen_at,
            )
        except DeviceModel.DoesNotExist:
            return None

    def find_by_device_id(self, device_id):
        """Find a device by its clair-core device ID."""
        try:
            model = DeviceModel.get(DeviceModel.device_id == device_id)
            return Device(
                device_id=model.device_id,
                hardware_id=model.hardware_id,
                api_key=model.api_key,
                device_secret=model.device_secret,
                status=model.status,
                created_at=model.created_at,
                last_seen_at=model.last_seen_at,
            )
        except DeviceModel.DoesNotExist:
            return None
