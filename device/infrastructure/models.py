"""Peewee ORM model for the device_telemetry table.

Maps the DeviceTelemetry aggregate root to the SQLite 'device_telemetry' table
with all fields from the embedded device payload.
"""

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    Model,
)

from shared.infrastructure.database import db


class DeviceTelemetryModel(Model):
    """Peewee model representing the 'device_telemetry' table in SQLite.

    Stores complete telemetry readings from embedded devices including:
    - Environmental sensor data (CO2, PM, temperature, humidity)
    - Connectivity status (WiFi, IP, signal strength)
    - Device health metrics (memory, sensor status)
    - Hardware information (chip model, specs)
    """

    # Primary key
    id = AutoField()

    # Device identification
    device_id = CharField(index=True)  # Logical device identifier

    # Device timestamps
    device_timestamp = IntegerField()  # Device uptime in milliseconds
    uptime_seconds = IntegerField()  # System uptime in seconds

    # Air quality readings (SCD41 sensor)
    co2 = FloatField()  # CO2 in ppm
    temperature = FloatField()  # Temperature in Celsius
    humidity = FloatField()  # Relative humidity percentage
    air_quality_valid = BooleanField()  # Whether air quality reading is valid

    # Particulate matter readings (PMS5003 sensor)
    pm1_0 = IntegerField()  # PM1.0 in µg/m³
    pm2_5 = IntegerField()  # PM2.5 in µg/m³
    pm10 = IntegerField()  # PM10 in µg/m³
    pm_valid = BooleanField()  # Whether PM reading is valid

    # Connectivity status
    wifi_status = CharField()  # connected/disconnected
    wifi_ssid = CharField()  # Network name
    wifi_ip = CharField()  # Device IP address
    wifi_rssi = IntegerField()  # Signal strength in dBm
    wifi_mac = CharField()  # MAC address
    wifi_channel = IntegerField()  # WiFi channel

    # Device health
    free_heap = IntegerField()  # Free heap memory in bytes
    min_free_heap = IntegerField()  # Minimum free heap since boot
    heap_size = IntegerField()  # Total heap size in bytes
    max_alloc_heap = IntegerField()  # Maximum allocatable heap
    scd41_status = CharField()  # SCD41 sensor status
    pms5003_status = CharField()  # PMS5003 sensor status
    last_valid_air_quality_sec = IntegerField()  # Seconds since last valid AQ reading
    last_valid_pm_sec = IntegerField()  # Seconds since last valid PM reading

    # Device info
    chip_model = CharField()  # ESP32 chip model
    chip_revision = IntegerField()  # Chip revision
    cpu_freq_mhz = IntegerField()  # CPU frequency
    flash_size = IntegerField()  # Flash size in bytes
    sketch_size = IntegerField()  # Firmware size in bytes
    free_sketch_space = IntegerField()  # Free space for updates

    # Status
    status = CharField()  # Overall device status
    status_code = IntegerField()  # Numeric status code

    # Server timestamp
    recorded_at = DateTimeField()  # When edge received the reading

    class Meta:
        database = db
        table_name = 'device_telemetry'
        indexes = (
            (('device_id', 'recorded_at'), False),  # For querying device history
        )
