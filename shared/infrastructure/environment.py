"""Shared environment configuration.

Even when communicating over HTTP, we keep an ACL module to isolate integration
details (URLs, headers, timeouts, error translation) from domain/application logic.
"""

from __future__ import annotations

import os


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be configured")
    return value


def get_edge_database_path() -> str:
    return os.getenv("EDGE_DATABASE_PATH", "clair_edge.db").strip() or "clair_edge.db"


def should_sync_devices_on_startup() -> bool:
    return os.getenv("EDGE_SYNC_DEVICES_ON_STARTUP", "true").lower() == "true"


def get_clair_core_devices_url() -> str:
    return _require("CLAIR_CORE_DEVICES_URL")


def get_clair_core_evaluations_url() -> str:
    return _require("CLAIR_CORE_EVALUATIONS_URL")


def get_clair_core_device_commands_pending_url() -> str:
    configured = os.getenv("CLAIR_CORE_DEVICE_COMMANDS_PENDING_URL", "").strip()
    if configured:
        return configured
    devices_url = get_clair_core_devices_url().rstrip("/")
    if devices_url.endswith("/provisioning"):
        devices_url = devices_url[: -len("/provisioning")]
    return f"{devices_url}/commands/pending"


def get_clair_core_device_command_ack_url(device_id: str, command_id: str) -> str:
    template = os.getenv("CLAIR_CORE_DEVICE_COMMAND_ACK_URL_TEMPLATE", "").strip()
    if template:
        return template.format(device_id=device_id, command_id=command_id)
    devices_url = get_clair_core_devices_url().rstrip("/")
    if devices_url.endswith("/provisioning"):
        devices_url = devices_url[: -len("/provisioning")]
    return f"{devices_url}/{device_id}/commands/{command_id}/ack"


def get_edge_to_core_token() -> str:
    return _require("EDGE_TO_CORE_TOKEN")


def get_edge_public_base_url() -> str:
    # Only used for docs. Do not require.
    return os.getenv("EDGE_PUBLIC_BASE_URL", "http://127.0.0.1:5000").strip() or "http://127.0.0.1:5000"


def get_edge_cors_allowed_origins() -> list[str]:
    """Return allowed CORS origins.

    Use "*" for development or embedded clients with many origins. In production,
    prefer a comma-separated allowlist such as "https://admin.example.com".
    """
    value = os.getenv("EDGE_CORS_ALLOWED_ORIGINS", "*").strip()
    if not value:
        return ["*"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def get_edge_cors_allowed_headers() -> str:
    return os.getenv(
        "EDGE_CORS_ALLOWED_HEADERS",
        "Content-Type,X-Hardware-Id,X-Device-Secret,X-Edge-Token",
    ).strip()
