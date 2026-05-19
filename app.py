"""Edge Service — Flask application entry point.

Registers bounded-context blueprints, initializes the SQLite database,
and synchronizes devices from clair-core on first request.
"""

from flask import Flask, request
import logging

from dotenv import load_dotenv

load_dotenv()

from device.application.outbox_processor import TelemetryOutboxProcessor
from device.interfaces.api import device_api
from iam.interfaces.services import iam_api
from provisioning.application.services.device_provisioning_application_service import DeviceProvisioningApplicationService
from provisioning.interfaces.api import provisioning_api
from shared.interfaces.docs_api import docs_api
from shared.infrastructure.database import init_db
from shared.infrastructure.environment import (
    get_edge_cors_allowed_headers,
    get_edge_cors_allowed_origins,
    should_sync_devices_on_startup,
)

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(device_api)
app.register_blueprint(provisioning_api)
app.register_blueprint(docs_api)

logger = logging.getLogger(__name__)

_initialized = False
_outbox_processor = TelemetryOutboxProcessor()


@app.after_request
def add_cors_headers(response):
    """Allow browser clients to call the edge API with device auth headers."""
    allowed_origins = get_edge_cors_allowed_origins()
    request_origin = request.headers.get("Origin")

    if "*" in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = "*"
    elif request_origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = request_origin
        response.headers.add("Vary", "Origin")

    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = get_edge_cors_allowed_headers()
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


@app.before_request
def initialize():
    """Initialize database, start outbox processor, and sync clair-core devices on first request."""
    global _initialized
    if not _initialized:
        init_db()
        _outbox_processor.start()
        if should_sync_devices_on_startup():
            try:
                DeviceProvisioningApplicationService().sync_devices_from_core()
            except RuntimeError as exc:
                logger.warning("Device startup sync skipped: %s", exc)
        _initialized = True


if __name__ == "__main__":
    # Ensure the edge cache is ready even before the first HTTP request.
    initialize()
    app.run(host="0.0.0.0", port=5000, debug=True)
