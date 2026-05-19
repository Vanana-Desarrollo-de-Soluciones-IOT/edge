"""Device API — Flask blueprint and telemetry ingestion endpoint.

Provides the device_api blueprint with the POST endpoint
for creating telemetry data records from authenticated devices.
"""

from flask import Blueprint, jsonify, request

from device.application.services import DeviceTelemetryAppService
from device.interfaces.resources import TelemetryRequest
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
        {
            "deviceId": "CLAIR001",           // Device identifier (camelCase)
            "timestamp": 20041,               // Device uptime milliseconds
            "uptime": 30,                     // System uptime seconds
            "airQuality": {                   // SCD41 sensor data
                "co2": 420,                   // CO2 in ppm (REQUIRED)
                "temperature": 24.99893,      // Temperature in Celsius
                "humidity": 50,               // Relative humidity %
                "valid": true                 // Data validity flag
            },
            "particulateMatter": {            // PMS5003 sensor data
                "pm1_0": 16,                  // PM1.0 in µg/m³
                "pm2_5": 27,                  // PM2.5 in µg/m³ (REQUIRED)
                "pm10": 35,                   // PM10 in µg/m³
                "valid": true                 // Data validity flag
            },
            "connectivity": {                 // WiFi status
                "status": "connected",
                "ssid": "Wokwi-GUEST",
                "ip": "10.13.37.2",
                "rssi": -80,                  // Signal strength dBm
                "mac": "24:0A:C4:00:01:10",
                "channel": 6
            },
            "deviceHealth": {                 // System health
                "freeHeap": 241176,
                "minFreeHeap": 236932,
                "heapSize": 318968,
                "maxAllocHeap": 110580,
                "scd41Status": "ok",
                "pms5003Status": "ok",
                "lastValidAirQualitySec": 0,
                "lastValidPMSec": 0
            },
            "deviceInfo": {                   // Hardware info
                "chipModel": "ESP32-D0WDQ6-V3",
                "chipRevision": 3,
                "cpuFreqMHz": 240,
                "flashSize": 4194304,
                "sketchSize": 978384,
                "freeSketchSpace": 0
            },
            "status": "Optimal",              // Overall device status
            "statusCode": 0,                  // Status code
            "created_at": "20"                // Optional timestamp override
        }

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
        # Parse JSON payload using DTO
        data = request.get_json()
        telemetry_request = TelemetryRequest.from_dict(data)
        
        # Get hardware_id from header (primary) or payload (fallback)
        hardware_id = request.headers.get("X-Hardware-Id") or telemetry_request.device_id
        
        # Extract CO2 and PM2.5 from nested structure
        co2 = telemetry_request.get_co2()
        pm25 = telemetry_request.get_pm2_5()
        created_at = telemetry_request.get_timestamp_iso()

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

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid request format: {str(e)}"}), 400
