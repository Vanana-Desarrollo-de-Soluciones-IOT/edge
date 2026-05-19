"""Swagger/OpenAPI documentation endpoints for the edge API."""

from flask import Blueprint, jsonify, render_template_string

from shared.infrastructure.environment import get_edge_public_base_url

docs_api = Blueprint("docs_api", __name__)


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Clair Edge API",
        "version": "1.0.0",
        "description": "Edge API for CO2 and PM2.5 telemetry ingestion and clair-core device provisioning.",
    },
    "servers": [{"url": get_edge_public_base_url(), "description": "Edge service"}],
    "tags": [
        {"name": "Telemetry", "description": "Environmental telemetry ingestion from IoT sensors."},
        {"name": "Provisioning", "description": "Device cache synchronization from clair-core."},
    ],
    "components": {
        "securitySchemes": {
            "DeviceCredentials": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Hardware-Id",
                "description": "Physical hardware identifier of the device.",
            },
            "DeviceSecret": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Device-Secret",
                "description": "Device secret key for physical device -> edge authentication.",
            },
            "EdgeToken": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Edge-Token",
                "description": "Shared edge token used to protect provisioning endpoints.",
            },
        },
        "schemas": {
            "CreateTelemetryRequest": {
                "type": "object",
                "required": ["deviceId", "airQuality", "particulateMatter"],
                "properties": {
                    "deviceId": {"type": "string", "description": "Device identifier (also sent in X-Hardware-Id header)."},
                    "timestamp": {"type": "integer", "description": "Device uptime in milliseconds."},
                    "uptime": {"type": "integer", "description": "System uptime in seconds."},
                    "airQuality": {
                        "type": "object",
                        "required": ["co2"],
                        "properties": {
                            "co2": {"type": "number", "format": "float", "minimum": 0, "maximum": 5000, "description": "CO2 concentration in ppm."},
                            "temperature": {"type": "number", "format": "float", "description": "Temperature in Celsius."},
                            "humidity": {"type": "number", "description": "Relative humidity percentage."},
                            "valid": {"type": "boolean", "description": "Whether the sensor reading is valid."},
                        },
                    },
                    "particulateMatter": {
                        "type": "object",
                        "required": ["pm2_5"],
                        "properties": {
                            "pm1_0": {"type": "integer", "description": "PM1.0 concentration in µg/m³."},
                            "pm2_5": {"type": "number", "minimum": 0, "maximum": 500, "description": "PM2.5 concentration in µg/m³."},
                            "pm10": {"type": "integer", "description": "PM10 concentration in µg/m³."},
                            "valid": {"type": "boolean", "description": "Whether the sensor reading is valid."},
                        },
                    },
                    "connectivity": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "WiFi connection status."},
                            "ssid": {"type": "string", "description": "Connected WiFi network name."},
                            "ip": {"type": "string", "description": "Device IP address."},
                            "rssi": {"type": "integer", "description": "Signal strength in dBm."},
                            "mac": {"type": "string", "description": "MAC address."},
                            "channel": {"type": "integer", "description": "WiFi channel."},
                        },
                    },
                    "deviceHealth": {
                        "type": "object",
                        "properties": {
                            "freeHeap": {"type": "integer", "description": "Free heap memory in bytes."},
                            "minFreeHeap": {"type": "integer", "description": "Minimum free heap since boot."},
                            "heapSize": {"type": "integer", "description": "Total heap size."},
                            "maxAllocHeap": {"type": "integer", "description": "Maximum allocatable heap."},
                            "scd41Status": {"type": "string", "description": "SCD41 sensor status."},
                            "pms5003Status": {"type": "string", "description": "PMS5003 sensor status."},
                            "lastValidAirQualitySec": {"type": "integer", "description": "Seconds since last valid air quality reading."},
                            "lastValidPMSec": {"type": "integer", "description": "Seconds since last valid PM reading."},
                        },
                    },
                    "deviceInfo": {
                        "type": "object",
                        "properties": {
                            "chipModel": {"type": "string", "description": "ESP32 chip model."},
                            "chipRevision": {"type": "integer", "description": "Chip revision number."},
                            "cpuFreqMHz": {"type": "integer", "description": "CPU frequency in MHz."},
                            "flashSize": {"type": "integer", "description": "Flash size in bytes."},
                            "sketchSize": {"type": "integer", "description": "Firmware size in bytes."},
                            "freeSketchSpace": {"type": "integer", "description": "Free space for firmware updates."},
                        },
                    },
                    "status": {"type": "string", "description": "Overall device status."},
                    "statusCode": {"type": "integer", "description": "Numeric status code."},
                    "created_at": {"type": "string", "description": "Optional timestamp override."},
                },
            },
            "TelemetryResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Database record ID."},
                    "device_id": {"type": "string", "description": "Logical device identifier."},
                    "device_timestamp": {"type": "integer", "description": "Device uptime in milliseconds."},
                    "uptime_seconds": {"type": "integer", "description": "System uptime in seconds."},
                    "air_quality": {
                        "type": "object",
                        "properties": {
                            "co2": {"type": "number", "format": "float", "description": "CO2 in ppm."},
                            "temperature": {"type": "number", "format": "float", "description": "Temperature in Celsius."},
                            "humidity": {"type": "number", "description": "Relative humidity %."},
                            "valid": {"type": "boolean", "description": "Whether reading is valid."},
                        },
                    },
                    "particulate_matter": {
                        "type": "object",
                        "properties": {
                            "pm1_0": {"type": "integer", "description": "PM1.0 in µg/m³."},
                            "pm2_5": {"type": "integer", "description": "PM2.5 in µg/m³."},
                            "pm10": {"type": "integer", "description": "PM10 in µg/m³."},
                            "valid": {"type": "boolean", "description": "Whether reading is valid."},
                        },
                    },
                    "connectivity": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "WiFi connection status."},
                            "ssid": {"type": "string", "description": "WiFi network name."},
                            "ip": {"type": "string", "description": "Device IP address."},
                            "rssi": {"type": "integer", "description": "Signal strength dBm."},
                            "mac": {"type": "string", "description": "MAC address."},
                            "channel": {"type": "integer", "description": "WiFi channel."},
                        },
                    },
                    "device_health": {
                        "type": "object",
                        "properties": {
                            "free_heap": {"type": "integer", "description": "Free heap memory bytes."},
                            "min_free_heap": {"type": "integer", "description": "Minimum free heap since boot."},
                            "heap_size": {"type": "integer", "description": "Total heap size."},
                            "max_alloc_heap": {"type": "integer", "description": "Maximum allocatable heap."},
                            "scd41_status": {"type": "string", "description": "SCD41 sensor status."},
                            "pms5003_status": {"type": "string", "description": "PMS5003 sensor status."},
                            "last_valid_air_quality_sec": {"type": "integer", "description": "Seconds since last valid AQ reading."},
                            "last_valid_pm_sec": {"type": "integer", "description": "Seconds since last valid PM reading."},
                        },
                    },
                    "device_info": {
                        "type": "object",
                        "properties": {
                            "chip_model": {"type": "string", "description": "ESP32 chip model."},
                            "chip_revision": {"type": "integer", "description": "Chip revision."},
                            "cpu_freq_mhz": {"type": "integer", "description": "CPU frequency MHz."},
                            "flash_size": {"type": "integer", "description": "Flash size bytes."},
                            "sketch_size": {"type": "integer", "description": "Firmware size bytes."},
                            "free_sketch_space": {"type": "integer", "description": "Free space for updates."},
                        },
                    },
                    "status": {"type": "string", "description": "Overall device status."},
                    "status_code": {"type": "integer", "description": "Numeric status code."},
                    "recorded_at": {"type": "string", "format": "date-time", "description": "UTC timestamp when recorded."},
                },
            },
            "DeviceCacheRecord": {
                "type": "object",
                "required": ["device_id", "hardware_id", "api_key", "device_secret", "status"],
                "properties": {
                    "device_id": {"type": "string"},
                    "hardware_id": {"type": "string"},
                    "api_key": {"type": "string"},
                    "device_secret": {"type": "string"},
                    "status": {"type": "string", "enum": ["OFFLINE", "ONLINE", "MAINTENANCE", "DECOMMISSIONED"]},
                },
            },
            "DeviceChangedEvent": {
                "type": "object",
                "required": ["event_type", "device"],
                "properties": {
                    "event_type": {"type": "string", "example": "DeviceChanged"},
                    "device": {"$ref": "#/components/schemas/DeviceCacheRecord"},
                },
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
    "paths": {
        "/api/v1/device/telemetry": {
            "post": {
                "tags": ["Telemetry"],
                "summary": "Create environmental telemetry record",
                "description": "Authenticates the device locally using the SQLite cache, validates all sensor readings (CO2, PM, temperature, humidity), and stores the complete telemetry record with connectivity, health, and hardware info.",
                "security": [{"DeviceCredentials": [], "DeviceSecret": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateTelemetryRequest"}}},
                },
                "responses": {
                    "201": {"description": "Telemetry record created.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TelemetryResponse"}}}},
                    "400": {"description": "Missing fields or invalid telemetry values.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                    "401": {"description": "Missing or invalid device credentials.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                },
            }
        },
        "/api/v1/provisioning/devices/events": {
            "post": {
                "tags": ["Provisioning"],
                "summary": "Receive clair-core device change event",
                "description": "Upserts a device from clair-core into the local edge SQLite cache.",
                "security": [{"EdgeToken": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DeviceChangedEvent"}}},
                },
                "responses": {
                    "200": {"description": "Local device cache updated."},
                    "400": {"description": "Missing fields or invalid payload.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                    "401": {"description": "Missing or invalid edge token.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                },
            }
        },
        
    },
}


@docs_api.route("/openapi.json", methods=["GET"])
def openapi_json():
    """Return the OpenAPI contract consumed by Swagger UI."""
    return jsonify(OPENAPI_SPEC)


@docs_api.route("/docs", methods=["GET"])
def swagger_docs():
    """Render Swagger UI for the edge API at /docs."""
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Clair Edge API Docs</title>
          <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
        </head>
        <body>
          <div id="swagger-ui"></div>
          <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
          <script>
            window.onload = function() {
              SwaggerUIBundle({ url: "/openapi.json", dom_id: "#swagger-ui" });
            };
          </script>
        </body>
        </html>
        """
    )
