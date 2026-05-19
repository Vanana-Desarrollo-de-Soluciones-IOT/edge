"""SQLite database configuration and initialization.

Provides the shared SqliteDatabase instance and init_db() function
that creates all tables across bounded contexts.
"""

from peewee import SqliteDatabase

from shared.infrastructure.environment import get_edge_database_path

db = SqliteDatabase(get_edge_database_path())


def _migrate_device_secret():
    """Add device_secret column to existing devices table if missing."""
    from peewee import OperationalError
    try:
        db.execute_sql("ALTER TABLE devices ADD COLUMN device_secret TEXT")
    except OperationalError:
        # Column already exists
        pass


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
        _migrate_device_secret()
    finally:
        db.close()
