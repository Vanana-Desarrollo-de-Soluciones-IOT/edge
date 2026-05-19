"""Device API — Flask blueprint and telemetry ingestion endpoint.

Provides the device_api blueprint with the POST endpoint
for creating telemetry data records from authenticated devices.
"""

from flask import Blueprint, jsonify, request

from device.application.services import DeviceTelemetryAppService
from iam.interfaces.services import authenticate_request

device_api = Blueprint("device_api", __name__)

telemetry_service = DeviceTelemetryAppService()


@device_api.route("/api/v1/device/telemetry", methods=["POST"])
def create_telemetry_record():
    """Create a new telemetry data record for an authenticated device.

    Headers:
        Content-Type: application/json
        X-Hardware-Id: <physical hardware identifier>
        X-Device-Secret: <device secret key>

    Body (JSON):
        co2 (number, required): CO2 concentration in ppm.
        pm25 (number, required): PM2.5 concentration in µg/m³.
        created_at (str, optional): ISO 8601 timestamp; defaults to UTC now.

    Returns:
        201: Record created successfully with id, hardware_id, co2, pm25, created_at.
        400: Missing fields, invalid CO2/PM2.5, or malformed timestamp.
        401: Missing credentials or authentication failure.
    """
    # Authenticate via IAM bounded context
    auth_error = authenticate_request()
    if auth_error is not None:
        return auth_error

    try:
        data = request.get_json()
        hardware_id = request.headers.get("X-Hardware-Id")
        co2 = data["co2"]
        pm25 = data["pm25"]
        created_at = data.get("created_at")

        record = telemetry_service.create_telemetry_record(
            hardware_id, co2, pm25, created_at
        )

        return jsonify({
            "id": record.id,
            "hardware_id": record.device_id,
            "co2": record.co2,
            "pm25": record.pm25,
            "created_at": record.created_at.isoformat(),
        }), 201

    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
