"""Peewee ORM model for the devices table.

Maps the Device aggregate root to the SQLite 'devices' table
with 7 columns matching the domain entity attributes.
"""

from peewee import CharField, DateTimeField, Model

from shared.infrastructure.database import db


class DeviceModel(Model):
    """Peewee model representing the 'devices' table in SQLite.

    Columns:
        device_id: Primary key — logical device identifier.
        hardware_id: Unique physical hardware ID.
        api_key: Secret authentication key.
        status: Lifecycle state (ACTIVE, INACTIVE, BLOCKED).
        created_at: Registration timestamp.
        last_seen_at: Last telemetry timestamp (nullable).
        owner_user_id: Owning user ID (nullable).
    """

    device_id = CharField(primary_key=True)
    hardware_id = CharField(unique=True)
    api_key = CharField()
    status = CharField(default="ACTIVE")
    created_at = DateTimeField()
    last_seen_at = DateTimeField(null=True)
    owner_user_id = CharField(null=True)

    class Meta:
        database = db
        table_name = 'devices'
