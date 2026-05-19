"""GetDeviceConnectionStatusQueryHandler — application service for checking device status.

Handles the query to determine if a device is online or offline based on
the time elapsed since its last telemetry reception.
"""

from datetime import datetime, timezone

from device.domain.queries.get_device_connection_status_query import (
    GetDeviceConnectionStatusQuery,
)
from device.domain.valueobjects.device_connection_status import DeviceConnectionStatus
from iam.infrastructure.repositories import DeviceRepository


class GetDeviceConnectionStatusQueryHandler:
    """Query handler that determines device connection status.

    A device is considered ONLINE if it sent telemetry within the last
    30 seconds. Otherwise, it is considered OFFLINE.
    """

    OFFLINE_THRESHOLD_SECONDS = 30

    def __init__(self, device_repository: DeviceRepository = None):
        self.device_repository = device_repository or DeviceRepository()

    def handle(self, query: GetDeviceConnectionStatusQuery) -> DeviceConnectionStatus:
        """Execute the query and return the device connection status.

        Args:
            query: GetDeviceConnectionStatusQuery with the hardware_id.

        Returns:
            DeviceConnectionStatus with the calculated status.

        Raises:
            ValueError: If the device is not found.
        """
        device = self.device_repository.find_by_hardware_id(query.hardware_id)

        if device is None:
            raise ValueError(f"Device not found: {query.hardware_id}")

        last_seen = device.last_seen_at
        now = datetime.now(timezone.utc)

        if last_seen is None:
            return DeviceConnectionStatus(
                hardware_id=query.hardware_id,
                status="OFFLINE",
                last_seen_at=None,
                seconds_since_last_seen=-1,
            )

        # Ensure last_seen is timezone-aware
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)

        seconds_since = int((now - last_seen).total_seconds())

        status = "ONLINE" if seconds_since < self.OFFLINE_THRESHOLD_SECONDS else "OFFLINE"

        return DeviceConnectionStatus(
            hardware_id=query.hardware_id,
            status=status,
            last_seen_at=last_seen,
            seconds_since_last_seen=seconds_since,
        )
