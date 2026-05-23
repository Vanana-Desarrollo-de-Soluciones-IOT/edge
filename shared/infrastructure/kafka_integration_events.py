"""Integration event DTOs for Kafka messaging boundaries.

These dataclasses are allowed at the boundary (ACL / messaging layer)
per the DDD guide.  They represent the contract between Edge and Core
without leaking internal domain objects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class TelemetryRecordedIntegrationEvent:
    """Event published when the edge persists a telemetry record.

    Consumed by clair-core Evaluation bounded context.
    """

    device_id: str
    hardware_id: str
    device_time: str
    uptime_seconds: int
    co2: float
    temperature: float
    humidity: float
    pm1_0: int
    pm2_5: int
    pm10: int
    wifi_status: str
    network_name: str
    signal_strength: int
    country: str
    health_status: int
    status: str
    recorded_at: str
    occurred_at: str


@dataclass(frozen=True)
class DeviceCommandAcknowledgedIntegrationEvent:
    """Event published when the embedded device acknowledges a command."""

    device_id: str
    hardware_id: str
    command_id: str
    status: str  # EXECUTED | FAILED
    failure_reason: Optional[str]
    acknowledged_at: str


@dataclass(frozen=True)
class DeviceCommandIssuedIntegrationEvent:
    """Event consumed from Core that represents a pending command for a device."""

    command_id: str
    device_id: str
    hardware_id: str
    command_type: str  # STANDBY | WAKE | RESTART
    payload: Optional[str]
    issued_at: str


@dataclass(frozen=True)
class DevicePresenceChangedIntegrationEvent:
    """Event published when the edge detects an ONLINE/OFFLINE transition."""

    device_id: str
    hardware_id: str
    status: str  # ONLINE | OFFLINE | STANDBY | ERROR
    occurred_at: str


@dataclass(frozen=True)
class DeviceChangedIntegrationEvent:
    """Event consumed from Core representing a provisioning change."""

    device_id: str
    hardware_id: str
    api_key: str
    device_secret: str
    status: str
    change_type: str  # CREATED | UPDATED | DELETED
    changed_at: str


@dataclass(frozen=True)
class DevicesSyncRequestedIntegrationEvent:
    """Event published by the Edge on startup to request a full device sync."""

    edge_instance_id: str
    requested_at: str
