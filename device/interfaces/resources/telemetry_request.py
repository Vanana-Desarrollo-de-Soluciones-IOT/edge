"""Device telemetry request/response DTOs.

Resources define API contracts for the optimized device telemetry endpoint.
These are pure transport classes that map the lightweight embedded device payload.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AirQualityData:
    """Air quality sensor data."""
    co2: float
    temperature: float
    humidity: float

    @classmethod
    def from_dict(cls, data: dict) -> "AirQualityData":
        return cls(
            co2=float(data.get("co2", 0)),
            temperature=float(data.get("temperature", 0)),
            humidity=float(data.get("humidity", 0)),
        )


@dataclass
class ParticulateMatterData:
    """Particulate matter sensor data."""
    pm1_0: int
    pm2_5: int
    pm10: int

    @classmethod
    def from_dict(cls, data: dict) -> "ParticulateMatterData":
        return cls(
            pm1_0=int(data.get("pm1_0", 0)),
            pm2_5=int(data.get("pm2_5", 0)),
            pm10=int(data.get("pm10", 0)),
        )


@dataclass
class ConnectivityData:
    """WiFi connectivity status."""
    status: str
    network: str = ""
    signal_strength: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "ConnectivityData":
        return cls(
            status=str(data.get("status", "unknown")),
            network=str(data.get("network", "")),
            signal_strength=int(data.get("signalStrength", 0)),
        )


@dataclass
class LocationData:
    """Device geographical location."""
    country: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "LocationData":
        return cls(
            country=str(data.get("country", "")),
        )


@dataclass
class TelemetryRequest:
    """Optimized telemetry request from embedded device.

    Maps the lightweight JSON payload:
    {
      "deviceId": "CLAIR-0001",
      "timestamp": "16:57:17",
      "uptime": "00:00:15",
      "airQuality": {"co2": 420, "temperature": 24.99893, "humidity": 50},
      "particulateMatter": {"pm1_0": 12, "pm2_5": 20, "pm10": 32},
      "connectivity": {"status": "connected", "network": "Wokwi-GUEST", "signalStrength": -65},
      "location": {"country": "PERU"},
      "healthStatus": 100,
      "status": "Optimal"
    }
    """
    device_id: str
    timestamp: str
    uptime: str
    air_quality: AirQualityData
    particulate_matter: ParticulateMatterData
    connectivity: ConnectivityData
    location: LocationData
    health_status: int
    status: str
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "TelemetryRequest":
        device_id = data.get("deviceId") or data.get("device_id")
        if not device_id:
            raise KeyError("deviceId or device_id is required")

        return cls(
            device_id=str(device_id),
            timestamp=str(data.get("timestamp", "")),
            uptime=str(data.get("uptime", "")),
            air_quality=AirQualityData.from_dict(data.get("airQuality", {})),
            particulate_matter=ParticulateMatterData.from_dict(data.get("particulateMatter", {})),
            connectivity=ConnectivityData.from_dict(data.get("connectivity", {})),
            location=LocationData.from_dict(data.get("location", {})),
            health_status=int(data.get("healthStatus", 100)),
            status=str(data.get("status", "unknown")),
            created_at=data.get("created_at") if data.get("created_at") else None,
        )
