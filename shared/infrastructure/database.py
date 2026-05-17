"""SQLite database configuration and initialization.

Provides the shared SqliteDatabase instance and init_db() function
that creates all tables across bounded contexts.
Database file: smart_band.db (created automatically in project root).
"""

from peewee import SqliteDatabase

db = SqliteDatabase('smart_band.db')


def init_db():
    """Initialize the database by creating all tables if they don't exist.

    Uses deferred imports to avoid circular dependencies between
    bounded context modules.
    """
    db.connect()
    try:
        # Deferred imports to avoid circular dependencies
        from iam.infrastructure.models import DeviceModel
        from device.infrastructure.models import DeviceTelemetryModel

        db.create_tables([DeviceModel, DeviceTelemetryModel], safe=True)
    finally:
        db.close()
