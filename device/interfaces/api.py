"""Device API — Flask blueprint and telemetry ingestion endpoint.

Provides the device_api blueprint with the POST endpoint
for creating telemetry data records from authenticated devices.
"""

from flask import Blueprint, jsonify, request

from device.application.services import DeviceCommandApplicationService, DeviceTelemetryAppService
from device.domain.commands import (
    AcknowledgeEmbeddedDeviceCommandCommand,
    CreateFullTelemetryRecordCommand,
    SynchronizeDeviceCommandsCommand,
)
from device.interfaces.resources import (
    AcknowledgeDeviceCommandRequest,
    TelemetryRequest,
    device_command_to_dict,
)
from iam.interfaces.services import authenticate_request
from shared.infrastructure.environment import get_edge_to_core_token

device_api = Blueprint("device_api", __name__)

telemetry_service = DeviceTelemetryAppService()
command_service = DeviceCommandApplicationService()


@device_api.route("/api/v1/device/telemetry", methods=["POST"])
def create_telemetry_record():
    """Create a new telemetry data record for an authenticated device.

    Headers:
        Content-Type: application/json
        X-Hardware-Id: <physical hardware identifier>
        X-Device-Secret: <device secret key>

    Body (JSON) — Optimized Payload:
        {
            "deviceId": "CLAIR-0001",
            "timestamp": "14:30:25",
            "uptime": "00:00:20",
            "airQuality": {
                "co2": 450,
                "temperature": 23.5,
                "humidity": 52.0
            },
            "particulateMatter": {
                "pm1_0": 5,
                "pm2_5": 12,
                "pm10": 25
            },
            "connectivity": {
                "status": "connected"
            },
            "status": "Optimal"
        }

    Returns:
        201: Record created successfully.
        400: Missing fields, invalid values, or malformed request.
        401: Missing credentials or authentication failure.
    """
    auth_error = authenticate_request()
    if auth_error is not None:
        return auth_error

    try:
        data = request.get_json()
        telemetry_request = TelemetryRequest.from_dict(data)

        hardware_id = request.headers.get("X-Hardware-Id") or telemetry_request.device_id

        command = CreateFullTelemetryRecordCommand(
            hardware_id=hardware_id,
            device_time=telemetry_request.timestamp,
            uptime=telemetry_request.uptime,
            air_quality={
                "co2": telemetry_request.air_quality.co2,
                "temperature": telemetry_request.air_quality.temperature,
                "humidity": telemetry_request.air_quality.humidity,
            },
            particulate_matter={
                "pm1_0": telemetry_request.particulate_matter.pm1_0,
                "pm2_5": telemetry_request.particulate_matter.pm2_5,
                "pm10": telemetry_request.particulate_matter.pm10,
            },
            connectivity={
                "status": telemetry_request.connectivity.status,
            },
            status=telemetry_request.status,
            created_at=telemetry_request.created_at,
        )

        record = telemetry_service.create_full_telemetry_record(command, raw_payload=data)

        return jsonify({
            "id": record.id,
            "device_id": record.device_id,
            "device_time": record.device_time,
            "uptime_seconds": record.uptime_seconds,
            "air_quality": {
                "co2": record.air_quality.co2,
                "temperature": record.air_quality.temperature,
                "humidity": record.air_quality.humidity,
            },
            "particulate_matter": {
                "pm1_0": record.particulate_matter.pm1_0,
                "pm2_5": record.particulate_matter.pm2_5,
                "pm10": record.particulate_matter.pm10,
            },
            "connectivity": {
                "status": record.connectivity.status,
            },
            "status": record.status,
            "recorded_at": record.recorded_at.isoformat(),
        }), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid request format: {str(e)}"}), 400


@device_api.route("/api/v1/device/commands/sync", methods=["POST"])
def synchronize_device_commands():
    """Synchronize pending device commands from clair-core into the edge cache.

    Headers:
        X-Edge-Token: shared edge/core token.

    Query Parameters:
        limit: optional max number of commands to fetch, defaults to 100.

    Returns:
        200: Commands synchronized and cached locally.
        401: Missing or invalid edge token.
        400: Invalid limit or core response shape.
    """
    if request.headers.get("X-Edge-Token") != get_edge_to_core_token():
        return jsonify({"error": "Invalid or missing X-Edge-Token"}), 401

    try:
        limit = int(request.args.get("limit", 100))
        commands = command_service.synchronize_pending_commands(
            SynchronizeDeviceCommandsCommand(limit=limit)
        )
        return jsonify({
            "count": len(commands),
            "commands": [device_command_to_dict(command) for command in commands],
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unable to synchronize commands: {str(e)}"}), 400


@device_api.route("/api/v1/device/commands/pending", methods=["GET"])
def get_pending_device_commands_for_embedded():
    """Return commands pending for the authenticated embedded device.

    Headers:
        X-Hardware-Id: physical hardware identifier.
        X-Device-Secret: embedded device secret.

    Returns:
        200: Pending commands, marked as delivered to the embedded device.
        401: Missing or invalid device credentials.
    """
    auth_error = authenticate_request()
    if auth_error is not None:
        return auth_error

    hardware_id = request.headers.get("X-Hardware-Id")
    commands = command_service.get_pending_commands_for_embedded(hardware_id)
    return jsonify({
        "count": len(commands),
        "commands": [device_command_to_dict(command) for command in commands],
    }), 200


@device_api.route("/api/v1/device/commands/<command_id>/ack", methods=["POST"])
def acknowledge_embedded_device_command(command_id):
    """Acknowledge command execution from the authenticated embedded device.

    Headers:
        X-Hardware-Id: physical hardware identifier.
        X-Device-Secret: embedded device secret.

    Body:
        {"status": "EXECUTED"}
        {"status": "FAILED", "failureReason": "Embedded timeout"}

    Returns:
        200: ACK persisted locally and forwarded to clair-core when reachable.
        400: Invalid body or unknown command.
        401: Missing or invalid device credentials.
    """
    auth_error = authenticate_request()
    if auth_error is not None:
        return auth_error

    try:
        ack_request = AcknowledgeDeviceCommandRequest.from_dict(request.get_json())
        hardware_id = request.headers.get("X-Hardware-Id")
        command = command_service.acknowledge_embedded_command(
            AcknowledgeEmbeddedDeviceCommandCommand(
                hardware_id=hardware_id,
                command_id=command_id,
                status=ack_request.status,
                failure_reason=ack_request.failure_reason,
            )
        )
        return jsonify(device_command_to_dict(command)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unable to acknowledge command: {str(e)}"}), 400
