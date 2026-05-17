"""Device entity — aggregate root of the IAM bounded context.

A Device represents a registered IoT smart band with authentication
credentials, lifecycle status, and ownership information.
"""


class Device:
    """Aggregate root entity representing a registered IoT device.

    Attributes:
        device_id: Unique logical identifier for the device (e.g., "smart-band-001").
        hardware_id: Physical hardware ID — prevents device cloning.
        api_key: Secret key for authentication via X-API-Key header.
        status: Device lifecycle state: "ACTIVE", "INACTIVE", or "BLOCKED".
        created_at: UTC timestamp of when the device was registered (audit trail).
        last_seen_at: Last time the device sent data — detects offline sensors.
        owner_user_id: ID of the owning user — for device claiming.
    """

    def __init__(self, device_id, hardware_id, api_key, status, created_at,
                 last_seen_at=None, owner_user_id=None):
        self.device_id = device_id
        self.hardware_id = hardware_id
        self.api_key = api_key
        self.status = status
        self.created_at = created_at
        self.last_seen_at = last_seen_at
        self.owner_user_id = owner_user_id
