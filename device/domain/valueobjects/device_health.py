"""DeviceHealth value object — represents device system health metrics.

Immutable value object containing memory usage and sensor status.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceHealth:
    """Device health metrics and sensor status.
    
    Attributes:
        free_heap: Free heap memory in bytes
        min_free_heap: Minimum free heap since boot
        heap_size: Total heap size in bytes
        max_alloc_heap: Maximum allocatable heap in bytes
        scd41_status: SCD41 sensor status string
        pms5003_status: PMS5003 sensor status string
        last_valid_air_quality_sec: Seconds since last valid air quality reading
        last_valid_pm_sec: Seconds since last valid PM reading
    """
    free_heap: int
    min_free_heap: int
    heap_size: int
    max_alloc_heap: int
    scd41_status: str
    pms5003_status: str
    last_valid_air_quality_sec: int
    last_valid_pm_sec: int

    def __post_init__(self):
        """Validate health metrics."""
        if self.free_heap < 0:
            raise ValueError(f"Free heap cannot be negative, got {self.free_heap}")
        if self.heap_size < 0:
            raise ValueError(f"Heap size cannot be negative, got {self.heap_size}")

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceHealth":
        """Create DeviceHealth from dictionary payload."""
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
