"""Connectivity value object — represents WiFi connection status.

Immutable value object containing network connection information.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Connectivity:
    """WiFi connectivity status from the device.
    
    Attributes:
        status: Connection status (connected, disconnected, etc.)
        ssid: WiFi network name
        ip: Device IP address
        rssi: Signal strength in dBm (negative value)
        mac: Device MAC address
        channel: WiFi channel number
    """
    status: str
    ssid: str
    ip: str
    rssi: int
    mac: str
    channel: int

    def __post_init__(self):
        """Validate connectivity data."""
        if not self.status:
            raise ValueError("Status cannot be empty")
        if self.rssi < -100 or self.rssi > 0:
            raise ValueError(f"RSSI must be between -100 and 0 dBm, got {self.rssi}")
        if self.channel < 1 or self.channel > 14:
            raise ValueError(f"WiFi channel must be between 1 and 14, got {self.channel}")

    @classmethod
    def from_dict(cls, data: dict) -> "Connectivity":
        """Create Connectivity from dictionary payload."""
        return cls(
            status=str(data.get("status", "unknown")),
            ssid=str(data.get("ssid", "")),
            ip=str(data.get("ip", "")),
            rssi=int(data.get("rssi", -100)),
            mac=str(data.get("mac", "")),
            channel=int(data.get("channel", 1))
        )
