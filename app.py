"""Edge Service — Flask application entry point.

Registers bounded-context blueprints, initializes the SQLite database,
and synchronizes devices from clair-core on first request.
"""

from flask import Flask
import logging

from dotenv import load_dotenv

load_dotenv()

from device.interfaces.api import device_api
from iam.interfaces.services import iam_api
from provisioning.application.services.device_provisioning_application_service import DeviceProvisioningApplicationService
from provisioning.interfaces.api import provisioning_api
from shared.interfaces.docs_api import docs_api
from shared.infrastructure.database import init_db
from shared.infrastructure.environment import should_sync_devices_on_startup

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(device_api)
app.register_blueprint(provisioning_api)
app.register_blueprint(docs_api)

logger = logging.getLogger(__name__)

_initialized = False


@app.before_request
def initialize():
    """Initialize database and sync clair-core devices on first request."""
    global _initialized
    if not _initialized:
        init_db()
        if should_sync_devices_on_startup():
            try:
                DeviceProvisioningApplicationService().sync_devices_from_core()
            except RuntimeError as exc:
                logger.warning("Device startup sync skipped: %s", exc)
        _initialized = True


if __name__ == "__main__":
    # Ensure the edge cache is ready even before the first HTTP request.
    initialize()
    app.run(debug=True)
