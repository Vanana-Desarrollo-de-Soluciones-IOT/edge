"""Edge Service — Flask application entry point.

Registers IAM and Device blueprints, initializes the SQLite database,
and seeds the test device on first request.
"""

from flask import Flask

from device.interfaces.api import device_api
from iam.application.services import AuthApplicationService
from iam.interfaces.services import iam_api
from shared.infrastructure.database import init_db

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(device_api)

_initialized = False


@app.before_request
def initialize():
    """Initialize database and seed test device on first request."""
    global _initialized
    if not _initialized:
        init_db()
        auth_app_service = AuthApplicationService()
        auth_app_service.get_or_create_test_device()
        _initialized = True


if __name__ == "__main__":
    app.run(debug=True)
