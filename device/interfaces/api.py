"""Device API — Flask blueprint and telemetry ingestion endpoint.

Provides the device_api blueprint with the POST endpoint
for creating complete telemetry data records from authenticated devices.
"""

from flask import Blueprint, jsonify, request

from device.application.services import DeviceTelemetryAppService
from device.domain.commands import CreateFullTelemetryRecordCommand
from device.interfaces.resources import TelemetryRequest
from iam.interfaces.services import authenticate_request

device_api = Blueprint("device_api", __name__)

telemetry_service = DeviceTelemetryAppService()


@device_api.route("/api/v1/device/telemetry", methods=["POST"])
def create_telemetry_record():
    """Create a new complete telemetry data record for an authenticated device.

    Headers:
        Content-Type: application/json
        X-Hardware-Id: <physical hardware identifier>
        X-Device-Secret: <device secret key>

    Body (JSON):
        {
            "deviceId": "CLAIR001",           // Device identifier
            "timestamp": 20041,               // Device uptime in milliseconds
            "uptime": 30,                     // System uptime in seconds
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
        201: Record created successfully with complete telemetry data.
        400: Missing fields, invalid values, or malformed request.
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

        # Create command from DTO (transformation at boundary)
        command = CreateFullTelemetryRecordCommand(
            hardware_id=hardware_id,
            device_timestamp=telemetry_request.timestamp,
            uptime_seconds=telemetry_request.uptime,
            air_quality={
                "co2": telemetry_request.air_quality.co2,
                "temperature": telemetry_request.air_quality.temperature,
                "humidity": telemetry_request.air_quality.humidity,
                "valid": telemetry_request.air_quality.valid,
            },
            particulate_matter={
                "pm1_0": telemetry_request.particulate_matter.pm1_0,
                "pm2_5": telemetry_request.particulate_matter.pm2_5,
                "pm10": telemetry_request.particulate_matter.pm10,
                "valid": telemetry_request.particulate_matter.valid,
            },
            connectivity={
                "status": telemetry_request.connectivity.status,
                "ssid": telemetry_request.connectivity.ssid,
                "ip": telemetry_request.connectivity.ip,
                "rssi": telemetry_request.connectivity.rssi,
                "mac": telemetry_request.connectivity.mac,
                "channel": telemetry_request.connectivity.channel,
            },
            device_health={
                "freeHeap": telemetry_request.device_health.free_heap,
                "minFreeHeap": telemetry_request.device_health.min_free_heap,
                "heapSize": telemetry_request.device_health.heap_size,
                "maxAllocHeap": telemetry_request.device_health.max_alloc_heap,
                "scd41Status": telemetry_request.device_health.scd41_status,
                "pms5003Status": telemetry_request.device_health.pms5003_status,
                "lastValidAirQualitySec": telemetry_request.device_health.last_valid_air_quality_sec,
                "lastValidPMSec": telemetry_request.device_health.last_valid_pm_sec,
            },
            device_info={
                "chipModel": telemetry_request.device_info.chip_model,
                "chipRevision": telemetry_request.device_info.chip_revision,
                "cpuFreqMHz": telemetry_request.device_info.cpu_freq_mhz,
                "flashSize": telemetry_request.device_info.flash_size,
                "sketchSize": telemetry_request.device_info.sketch_size,
                "freeSketchSpace": telemetry_request.device_info.free_sketch_space,
            },
            status=telemetry_request.status,
            status_code=telemetry_request.status_code,
            created_at=telemetry_request.created_at if telemetry_request.created_at else None,
        )

        # Execute use case via application service (pass raw payload for Core forward)
        record = telemetry_service.create_full_telemetry_record(command, raw_payload=data)

        # Build response with complete data (transformation at boundary)
        return jsonify({
            "id": record.id,
            "device_id": record.device_id,
            "device_timestamp": record.device_timestamp,
            "uptime_seconds": record.uptime_seconds,
            "air_quality": {
                "co2": record.air_quality.co2,
                "temperature": record.air_quality.temperature,
                "humidity": record.air_quality.humidity,
                "valid": record.air_quality.valid,
            },
            "particulate_matter": {
                "pm1_0": record.particulate_matter.pm1_0,
                "pm2_5": record.particulate_matter.pm2_5,
                "pm10": record.particulate_matter.pm10,
                "valid": record.particulate_matter.valid,
            },
            "connectivity": {
                "status": record.connectivity.status,
                "ssid": record.connectivity.ssid,
                "ip": record.connectivity.ip,
                "rssi": record.connectivity.rssi,
                "mac": record.connectivity.mac,
                "channel": record.connectivity.channel,
            },
            "device_health": {
                "free_heap": record.device_health.free_heap,
                "min_free_heap": record.device_health.min_free_heap,
                "heap_size": record.device_health.heap_size,
                "max_alloc_heap": record.device_health.max_alloc_heap,
                "scd41_status": record.device_health.scd41_status,
                "pms5003_status": record.device_health.pms5003_status,
                "last_valid_air_quality_sec": record.device_health.last_valid_air_quality_sec,
                "last_valid_pm_sec": record.device_health.last_valid_pm_sec,
            },
            "device_info": {
                "chip_model": record.device_info.chip_model,
                "chip_revision": record.device_info.chip_revision,
                "cpu_freq_mhz": record.device_info.cpu_freq_mhz,
                "flash_size": record.device_info.flash_size,
                "sketch_size": record.device_info.sketch_size,
                "free_sketch_space": record.device_info.free_sketch_space,
            },
            "status": record.status,
            "status_code": record.status_code,
            "recorded_at": record.recorded_at.isoformat(),
        }), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid request format: {str(e)}"}), 400
