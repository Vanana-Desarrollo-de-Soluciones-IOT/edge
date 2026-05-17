"""Application service for provisioning the local device cache."""

import os

from provisioning.application.outboundservices.acl.clair_core_device_service import ClairCoreDeviceService
from provisioning.domain.commands.synchronize_devices_command import SynchronizeDevicesCommand
from provisioning.domain.services.device_cache_service import DeviceCacheService
from provisioning.infrastructure.device_cache_repository import DeviceCacheRepository


class DeviceProvisioningApplicationService:
    """Coordinates initial and webhook-driven device cache synchronization."""

    def __init__(self):
        self.core_device_service = ClairCoreDeviceService()
        self.device_cache_repository = DeviceCacheRepository()
        self.device_cache_service = DeviceCacheService()

    def sync_devices_from_core(self):
        """Download master devices from clair-core and cache them locally."""
        source_url = os.getenv(
            "CLAIR_CORE_DEVICES_URL",
            "http://localhost:8080/api/v1/devices/provisioning",
        )
        devices = self.core_device_service.fetch_devices(source_url)
        return self.synchronize_devices(SynchronizeDevicesCommand(devices))

    def synchronize_devices(self, command):
        """Upsert validated device records into the local SQLite cache."""
        for device in command.devices:
            self.device_cache_service.validate_device_record(device)
        return self.device_cache_repository.upsert_many(command.devices)
