"""Connectivity value object — represents WiFi connection status.

Immutable value object containing network connection information.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Connectivity:
    """WiFi connectivity status from the device.

    Attributes:
        status: Connection status (connected, disconnected, etc.)
        ssid: WiFi network name (optional for optimized payloads)
        ip: Device IP address (optional for optimized payloads)
        rssi: Signal strength in dBm (optional for optimized payloads)
        mac: Device MAC address (optional for optimized payloads)
        channel: WiFi channel number (optional for optimized payloads)
    """
    status: str
    ssid: str = ""
    ip: str = ""
    rssi: int = 0
    mac: str = ""
    channel: int = 0

    def __post_init__(self):
        """Validate connectivity data."""
        if not self.status:
            raise ValueError("Status cannot be empty")
        if self.rssi != 0 and (self.rssi < -100 or self.rssi > 0):
            raise ValueError(f"RSSI must be between -100 and 0 dBm or 0 if absent, got {self.rssi}")
        if self.channel != 0 and (self.channel < 1 or self.channel > 14):
            raise ValueError(f"WiFi channel must be between 1 and 14 or 0 if absent, got {self.channel}")

    @classmethod
    def from_dict(cls, data: dict) -> "Connectivity":
        """Create Connectivity from dictionary payload."""
        return cls(
            status=str(data.get("status", "unknown")),
            ssid=str(data.get("ssid", "")),
            ip=str(data.get("ip", "")),
            rssi=int(data.get("rssi", 0)),
            mac=str(data.get("mac", "")),
            channel=int(data.get("channel", 0))
        )
