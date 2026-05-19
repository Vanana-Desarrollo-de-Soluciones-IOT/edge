"""Peewee ORM model for the device_telemetry table.

Maps the DeviceTelemetry aggregate root to the SQLite 'device_telemetry' table
with only the fields present in the optimized embedded device payload.
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

    Stores optimized telemetry readings with only the fields sent by
    the embedded device: environmental sensors, connectivity status,
    and overall device state.
    """

    id = AutoField()

    device_id = CharField(index=True)

    device_time = CharField()          # e.g., "14:30:25"
    uptime_seconds = IntegerField()    # Parsed from HH:MM:SS

    co2 = FloatField()
    temperature = FloatField()
    humidity = FloatField()
    air_quality_valid = BooleanField(default=True)

    pm1_0 = IntegerField()
    pm2_5 = IntegerField()
    pm10 = IntegerField()
    pm_valid = BooleanField(default=True)

    wifi_status = CharField()

    status = CharField()

    recorded_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'device_telemetry'
        indexes = (
            (('device_id', 'recorded_at'), False),
        )
