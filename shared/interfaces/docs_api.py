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
            "DeviceApiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key synchronized from clair-core for the device.",
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
                "required": ["device_id", "co2", "pm25"],
                "properties": {
                    "device_id": {"type": "string", "description": "clair-core device UUID cached by the edge."},
                    "co2": {"type": "number", "format": "float", "minimum": 0, "maximum": 5000, "description": "CO2 concentration in ppm."},
                    "pm25": {"type": "number", "format": "float", "minimum": 0, "maximum": 500, "description": "PM2.5 concentration in micrograms per cubic meter."},
                    "created_at": {"type": "string", "format": "date-time", "description": "Optional measurement timestamp. Defaults to current UTC time."},
                },
            },
            "TelemetryResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "device_id": {"type": "string"},
                    "co2": {"type": "number", "format": "float"},
                    "pm25": {"type": "number", "format": "float"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
                "DeviceCacheRecord": {
                    "type": "object",
                    "required": ["device_id", "hardware_id", "api_key", "status"],
                    "properties": {
                        "device_id": {"type": "string"},
                        "hardware_id": {"type": "string"},
                        "api_key": {"type": "string"},
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
                "description": "Authenticates the device locally using the SQLite cache, validates CO2 and PM2.5, and stores the reading.",
                "security": [{"DeviceApiKey": []}],
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
        "/api/v1/provisioning/devices/sync": {
            "post": {
                "tags": ["Provisioning"],
                "summary": "Trigger provisioning sync",
                "description": "Downloads devices from clair-core provisioning endpoint and upserts into SQLite cache.",
                "security": [{"EdgeToken": []}],
                "responses": {
                    "200": {"description": "Sync completed."},
                    "401": {"description": "Missing or invalid edge token.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                    "503": {"description": "clair-core unreachable.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
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
