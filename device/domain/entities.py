"""DeviceTelemetry entity — aggregate root of the Device bounded context.

Represents a single environmental reading (CO2 and PM2.5) from an IoT sensor device.
"""


class DeviceTelemetry:
    """Aggregate root entity representing an environmental telemetry reading.

    Attributes:
        id: Auto-incremented database ID (None before persistence).
        device_id: Logical identifier of the source device.
        co2: CO2 concentration in parts per million (ppm).
        pm25: PM2.5 particulate matter concentration in µg/m³.
        created_at: UTC timestamp of when the measurement was taken.
    """

    def __init__(self, device_id, co2, pm25, created_at, id=None):
        self.id = id
        self.device_id = device_id
        self.co2 = co2
        self.pm25 = pm25
        self.created_at = created_at
