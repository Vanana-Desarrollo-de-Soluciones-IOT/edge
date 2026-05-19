"""Device telemetry request/response DTOs.

Resources define API contracts for the device telemetry endpoint.
These are pure transport classes that map the embedded device payload.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AirQualityData:
    """Air quality sensor data from SCD41 sensor."""
    co2: float
    temperature: float
    humidity: float
    valid: bool

    @classmethod
    def from_dict(cls, data: dict) -> "AirQualityData":
        """Create AirQualityData from dictionary."""
        return cls(
            co2=float(data.get("co2", 0)),
            temperature=float(data.get("temperature", 0)),
            humidity=float(data.get("humidity", 0)),
            valid=bool(data.get("valid", False))
        )


@dataclass
class ParticulateMatterData:
    """Particulate matter sensor data from PMS5003 sensor."""
    pm1_0: int
    pm2_5: int
    pm10: int
    valid: bool

    @classmethod
    def from_dict(cls, data: dict) -> "ParticulateMatterData":
        """Create ParticulateMatterData from dictionary."""
        return cls(
            pm1_0=int(data.get("pm1_0", 0)),
            pm2_5=int(data.get("pm2_5", 0)),
            pm10=int(data.get("pm10", 0)),
            valid=bool(data.get("valid", False))
        )


@dataclass
class ConnectivityData:
    """WiFi connectivity status from the device."""
    status: str
    ssid: str
    ip: str
    rssi: int
    mac: str
    channel: int

    @classmethod
    def from_dict(cls, data: dict) -> "ConnectivityData":
        """Create ConnectivityData from dictionary."""
        return cls(
            status=str(data.get("status", "unknown")),
            ssid=str(data.get("ssid", "")),
            ip=str(data.get("ip", "")),
            rssi=int(data.get("rssi", 0)),
            mac=str(data.get("mac", "")),
            channel=int(data.get("channel", 0))
        )


@dataclass
class DeviceHealthData:
    """Device health metrics and sensor status."""
    free_heap: int
    min_free_heap: int
    heap_size: int
    max_alloc_heap: int
    scd41_status: str
    pms5003_status: str
    last_valid_air_quality_sec: int
    last_valid_pm_sec: int

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceHealthData":
        """Create DeviceHealthData from dictionary."""
        return cls(
            free_heap=int(data.get("freeHeap", 0)),
            min_free_heap=int(data.get("minFreeHeap", 0)),
            heap_size=int(data.get("heapSize", 0)),
            max_alloc_heap=int(data.get("maxAllocHeap", 0)),
            scd41_status=str(data.get("scd41Status", "unknown")),
            pms5003_status=str(data.get("pms5003Status", "unknown")),
            last_valid_air_quality_sec=int(data.get("lastValidAirQualitySec", 0)),
            last_valid_pm_sec=int(data.get("lastValidPMSec", 0))
        )


@dataclass
class DeviceInfoData:
    """Hardware information about the ESP32 device."""
    chip_model: str
    chip_revision: int
    cpu_freq_mhz: int
    flash_size: int
    sketch_size: int
    free_sketch_space: int

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceInfoData":
        """Create DeviceInfoData from dictionary."""
        return cls(
            chip_model=str(data.get("chipModel", "")),
            chip_revision=int(data.get("chipRevision", 0)),
            cpu_freq_mhz=int(data.get("cpuFreqMHz", 0)),
            flash_size=int(data.get("flashSize", 0)),
            sketch_size=int(data.get("sketchSize", 0)),
            free_sketch_space=int(data.get("freeSketchSpace", 0))
        )


@dataclass
class TelemetryRequest:
    """Complete telemetry request from embedded device.
    
    This DTO maps the JSON payload sent by the ESP32 device:
    {
      "deviceId": "CLAIR001",
      "timestamp": 20041,
      "uptime": 30,
      "airQuality": {...},
      "particulateMatter": {...},
      "connectivity": {...},
      "deviceHealth": {...},
      "deviceInfo": {...},
      "status": "Optimal",
      "statusCode": 0,
      "created_at": "20"
    }
    """
    device_id: str
    timestamp: int
    uptime: int
    air_quality: AirQualityData
    particulate_matter: ParticulateMatterData
    connectivity: ConnectivityData
    device_health: DeviceHealthData
    device_info: DeviceInfoData
    status: str
    status_code: int
    created_at: str

    @classmethod
    def from_dict(cls, data: dict) -> "TelemetryRequest":
        """Create TelemetryRequest from the embedded device JSON payload.
        
        Args:
            data: Raw JSON payload from the device.
            
        Returns:
            Parsed TelemetryRequest DTO.
            
        Raises:
            KeyError: If required fields are missing.
            ValueError: If data types are invalid.
        """
        # Support both camelCase and snake_case for device_id
        device_id = data.get("deviceId") or data.get("device_id")
        if not device_id:
            raise KeyError("deviceId or device_id is required")

        return cls(
            device_id=str(device_id),
            timestamp=int(data.get("timestamp", 0)),
            uptime=int(data.get("uptime", 0)),
            air_quality=AirQualityData.from_dict(data.get("airQuality", {})),
            particulate_matter=ParticulateMatterData.from_dict(data.get("particulateMatter", {})),
            connectivity=ConnectivityData.from_dict(data.get("connectivity", {})),
            device_health=DeviceHealthData.from_dict(data.get("deviceHealth", {})),
            device_info=DeviceInfoData.from_dict(data.get("deviceInfo", {})),
            status=str(data.get("status", "unknown")),
            status_code=int(data.get("statusCode", 0)),
            created_at=str(data.get("created_at", ""))
        )

    def get_co2(self) -> float:
        """Extract CO2 value from air quality data."""
        return self.air_quality.co2

    def get_pm2_5(self) -> float:
        """Extract PM2.5 value from particulate matter data."""
        return float(self.particulate_matter.pm2_5)

    def get_timestamp_iso(self) -> Optional[str]:
        """Convert device timestamp to ISO format if valid."""
        # If created_at is provided as a date string, use it
        if self.created_at and len(self.created_at) > 2:
            return self.created_at
        return None
