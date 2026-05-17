"""Device repository — infrastructure layer.

Provides data access operations for the Device aggregate root,
mapping between Peewee models and domain entities.
"""

from datetime import datetime, timezone

from iam.domain.entities import Device
from iam.infrastructure.models import DeviceModel


class DeviceRepository:
    """Repository for Device aggregate root persistence.

    Handles all database operations for devices, translating between
    Peewee ORM models (infrastructure) and Device domain entities.
    """

    def find_by_id_and_api_key(self, device_id, api_key):
        """Find a device by its ID and API key combination.

        Args:
            device_id: The logical device identifier.
            api_key: The secret API key to validate.

        Returns:
            A Device domain entity if found, None otherwise.
        """
        try:
            model = DeviceModel.get(
                (DeviceModel.device_id == device_id) &
                (DeviceModel.api_key == api_key)
            )
            return Device(
                device_id=model.device_id,
                hardware_id=model.hardware_id,
                api_key=model.api_key,
                status=model.status,
                created_at=model.created_at,
                last_seen_at=model.last_seen_at,
                owner_user_id=model.owner_user_id,
            )
        except DeviceModel.DoesNotExist:
            return None

    def get_or_create_test_device(self):
        """Provision the default test device for development.

        Creates the test device if it doesn't exist yet. Uses hardcoded
        development credentials — never use in production.

        Returns:
            The test Device domain entity.
        """
        model, created = DeviceModel.get_or_create(
            device_id="smart-band-001",
            defaults={
                "hardware_id": "HW-SB-001-ABC123",
                "api_key": "test-api-key-123",
                "status": "ACTIVE",
                "created_at": datetime(2025, 6, 4, 23, 23, 0, tzinfo=timezone.utc),
                "last_seen_at": None,
                "owner_user_id": None,
            },
        )
        return Device(
            device_id=model.device_id,
            hardware_id=model.hardware_id,
            api_key=model.api_key,
            status=model.status,
            created_at=model.created_at,
            last_seen_at=model.last_seen_at,
            owner_user_id=model.owner_user_id,
        )

    def update_last_seen(self, device_id):
        """Update the last_seen_at timestamp for a device.

        Called after every successful authentication to track
        device activity and detect offline sensors.

        Args:
            device_id: The logical device identifier to update.
        """
        DeviceModel.update(
            last_seen_at=datetime.now(timezone.utc)
        ).where(
            DeviceModel.device_id == device_id
        ).execute()
