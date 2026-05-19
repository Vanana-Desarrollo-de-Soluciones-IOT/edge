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


def authenticate_request(update_last_seen: bool = False):
    """Authenticate the current HTTP request using device credentials.

    Extracts hardware_id from the X-Hardware-Id header and device_secret
    from the X-Device-Secret header. Validates credentials and updates
    last_seen_at on successful authentication.

    Returns:
        None if authentication succeeds.
        A (response, status_code) tuple if authentication fails (401).
    """
    hardware_id = request.headers.get("X-Hardware-Id", "").strip()
    device_secret = request.headers.get("X-Device-Secret", "").strip()

    if not hardware_id or not device_secret:
        return jsonify({"error": "Missing X-Hardware-Id or X-Device-Secret"}), 401

    if not auth_service.authenticate(hardware_id, device_secret):
        return jsonify({"error": "Invalid hardware ID or device secret"}), 401

    if update_last_seen:
        device_repository.update_last_seen(hardware_id)
    return None
