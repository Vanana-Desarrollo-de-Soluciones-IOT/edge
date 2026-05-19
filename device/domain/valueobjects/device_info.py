"""DeviceInfo value object — represents ESP32 hardware information.

Immutable value object containing hardware specifications.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInfo:
    """Hardware information about the ESP32 device.
    
    Attributes:
        chip_model: ESP32 chip model name
        chip_revision: Chip revision number
        cpu_freq_mhz: CPU frequency in MHz
        flash_size: Flash size in bytes
        sketch_size: Firmware size in bytes
        free_sketch_space: Free space for firmware updates
    """
    chip_model: str
    chip_revision: int
    cpu_freq_mhz: int
    flash_size: int
    sketch_size: int
    free_sketch_space: int

    def __post_init__(self):
        """Validate device info."""
        if not self.chip_model:
            raise ValueError("Chip model cannot be empty")
        if self.cpu_freq_mhz < 1:
            raise ValueError(f"CPU frequency must be positive, got {self.cpu_freq_mhz}")

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceInfo":
        """Create DeviceInfo from dictionary payload."""
        return cls(
            chip_model=str(data.get("chipModel", "")),
            chip_revision=int(data.get("chipRevision", 0)),
            cpu_freq_mhz=int(data.get("cpuFreqMHz", 0)),
            flash_size=int(data.get("flashSize", 0)),
            sketch_size=int(data.get("sketchSize", 0)),
            free_sketch_space=int(data.get("freeSketchSpace", 0))
        )
