from dataclasses import dataclass


@dataclass
class DeviceCacheResource:
    """REST resource received from clair-core device webhook notifications."""

    device_id: str
    hardware_id: str
    api_key: str
    status: str

    @staticmethod
    def from_dict(payload):
        return DeviceCacheResource(
            device_id=str(payload.get("device_id") or payload.get("id")),
            hardware_id=payload.get("hardware_id") or payload.get("hardwareId"),
            api_key=payload.get("api_key") or payload.get("apiKey"),
            status=payload.get("status"),
        )

    def to_command_record(self):
        return {
            "device_id": self.device_id,
            "hardware_id": self.hardware_id,
            "api_key": self.api_key,
            "status": self.status,
        }
