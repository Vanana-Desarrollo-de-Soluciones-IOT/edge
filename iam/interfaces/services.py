"""IAM interface services — Flask blueprint and authentication function.

Provides the iam_api blueprint and the authenticate_request() function
that other bounded contexts use to validate device credentials.
"""

from flask import Blueprint, jsonify, request

from iam.application.services import AuthApplicationService
from iam.infrastructure.repositories import DeviceRepository

iam_api = Blueprint("iam_api", __name__)

auth_service = AuthApplicationService()
device_repository = DeviceRepository()


def authenticate_request():
    """Authenticate the current HTTP request using device credentials.

    Extracts device_id from the JSON body and api_key from the
    X-API-Key header. Validates credentials and updates last_seen_at
    on successful authentication.

    Returns:
        None if authentication succeeds.
        A (response, status_code) tuple if authentication fails (401).
    """
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id")
    api_key = request.headers.get("X-API-Key")

    if not device_id or not api_key:
        return jsonify({"error": "Missing device_id or X-API-Key"}), 401

    if not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401

    # Update last_seen_at on successful authentication
    device_repository.update_last_seen(device_id)
    return None
