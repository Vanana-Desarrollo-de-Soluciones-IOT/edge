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


def _migrate_telemetry_schema():
    """Recreate device_telemetry table if it still uses the legacy full schema.

    The optimized payload no longer sends deviceHealth, deviceInfo, or detailed
    connectivity fields. If the old columns are detected, the legacy table is
    dropped so Peewee can create the clean new schema on startup.
    """
    cursor = db.execute_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='device_telemetry'"
    )
    if not cursor.fetchone():
        return

    # Detect legacy column that does not exist in the optimized schema
    col_cursor = db.execute_sql("PRAGMA table_info(device_telemetry)")
    columns = {row[1] for row in col_cursor.fetchall()}
    if "wifi_ssid" in columns or "free_heap" in columns or "chip_model" in columns:
        db.execute_sql("DROP TABLE IF EXISTS device_telemetry")


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
        from device.infrastructure.outbox.outbox_record_model import OutboxRecordModel

        _migrate_telemetry_schema()
        db.create_tables([DeviceModel, DeviceTelemetryModel, OutboxRecordModel], safe=True)
        _migrate_device_secret()
    finally:
        db.close()
