"""Peewee ORM model for the device_telemetry table.

Maps the DeviceTelemetry aggregate root to the SQLite 'device_telemetry' table.
"""

from peewee import AutoField, CharField, DateTimeField, FloatField, Model

from shared.infrastructure.database import db


class DeviceTelemetryModel(Model):
    """Peewee model representing the 'device_telemetry' table in SQLite.

    Columns:
        id: Auto-incremented primary key.
        device_id: Logical device identifier (no FK — bounded contexts are decoupled).
        co2: CO2 concentration in ppm.
        pm25: PM2.5 particulate matter in µg/m³.
        created_at: Measurement timestamp.
    """

    id = AutoField()
    device_id = CharField()
    co2 = FloatField()
    pm25 = FloatField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'device_telemetry'
