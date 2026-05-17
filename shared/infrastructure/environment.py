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

def get_edge_to_core_token() -> str:
    return _require("EDGE_TO_CORE_TOKEN")


def get_edge_public_base_url() -> str:
    # Only used for docs. Do not require.
    return os.getenv("EDGE_PUBLIC_BASE_URL", "http://127.0.0.1:5000").strip() or "http://127.0.0.1:5000"
