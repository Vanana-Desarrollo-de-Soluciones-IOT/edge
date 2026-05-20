"""ParticulateMatter value object — represents PMS5003 sensor readings.

Immutable value object containing PM1.0, PM2.5 and PM10 measurements.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ParticulateMatter:
    """PMS5003 particulate matter sensor readings.

    Attributes:
        pm1_0: PM1.0 concentration in µg/m³
        pm2_5: PM2.5 concentration in µg/m³
        pm10: PM10 concentration in µg/m³
    """
    pm1_0: int
    pm2_5: int
    pm10: int

    def __post_init__(self):
        """Validate particulate matter values."""
        if self.pm1_0 < 0 or self.pm1_0 > 1000:
            raise ValueError(f"PM1.0 must be between 0 and 1000 µg/m³, got {self.pm1_0}")
        if self.pm2_5 < 0 or self.pm2_5 > 1000:
            raise ValueError(f"PM2.5 must be between 0 and 1000 µg/m³, got {self.pm2_5}")
        if self.pm10 < 0 or self.pm10 > 1000:
            raise ValueError(f"PM10 must be between 0 and 1000 µg/m³, got {self.pm10}")

    @classmethod
    def from_dict(cls, data: dict) -> "ParticulateMatter":
        """Create ParticulateMatter from dictionary payload."""
        return cls(
            pm1_0=int(data.get("pm1_0", 0)),
            pm2_5=int(data.get("pm2_5", 0)),
            pm10=int(data.get("pm10", 0)),
        )
