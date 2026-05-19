"""Peewee ORM model for the devices table.

Maps the local clair-core device cache to the SQLite 'devices' table.
"""

from peewee import CharField, DateTimeField, Model

from shared.infrastructure.database import db


class DeviceModel(Model):
    """Peewee model representing the 'devices' table in SQLite.

    Columns:
        device_id: Primary key — logical device identifier.
        hardware_id: Unique physical hardware ID.
        api_key: Secret authentication key for edge -> core communication.
        device_secret: Secret authentication key for physical device -> edge communication.
        status: Lifecycle state synchronized from clair-core.
        created_at: Registration timestamp.
        last_seen_at: Last telemetry timestamp (nullable).
    """

    device_id = CharField(primary_key=True)
    hardware_id = CharField(unique=True)
    api_key = CharField()
    device_secret = CharField()
    status = CharField()
    created_at = DateTimeField()
    last_seen_at = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = 'devices'
