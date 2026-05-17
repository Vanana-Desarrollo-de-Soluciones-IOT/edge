"""Provisioning API for webhook-driven device cache updates."""

from flask import Blueprint, jsonify, request

from shared.infrastructure.environment import get_edge_to_core_token

from provisioning.application.services.device_provisioning_application_service import DeviceProvisioningApplicationService
from provisioning.domain.commands.synchronize_devices_command import SynchronizeDevicesCommand
from provisioning.interfaces.resources.device_cache_resource import DeviceCacheResource

provisioning_api = Blueprint("provisioning_api", __name__)
provisioning_service = DeviceProvisioningApplicationService()


@provisioning_api.route("/api/v1/provisioning/devices/events", methods=["POST"])
def receive_device_change_event():
    """Receive clair-core device change notifications and update local cache.

    Body JSON shape:
        event_type: DeviceChanged or DeviceDeleted.
        device: Object with device_id/id, hardware_id/hardwareId, status.

    Returns:
        200: Device cache was updated.
        400: Missing fields or invalid payload.
        401: Missing or invalid X-Edge-Token.
    """
    provided_token = request.headers.get("X-Edge-Token", "").strip()
    if not provided_token or provided_token != get_edge_to_core_token():
        return jsonify({"error": "Missing or invalid X-Edge-Token"}), 401

    try:
        payload = request.get_json() or {}
        resource = DeviceCacheResource.from_dict(payload.get("device", payload))
        count = provisioning_service.synchronize_devices(
            SynchronizeDevicesCommand([resource.to_command_record()])
        )
        return jsonify({"updated": count}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@provisioning_api.route("/api/v1/provisioning/devices/sync", methods=["POST"])
def sync_devices_from_core():
    """Manually trigger a clair-core device provisioning sync.

    Protected with X-Edge-Token to avoid arbitrary cache poisoning.

    Returns:
        200: Sync completed with number of upserted records.
        401: Missing or invalid X-Edge-Token.
        503: clair-core unreachable or misconfigured.
    """
    provided_token = request.headers.get("X-Edge-Token", "").strip()
    if not provided_token or provided_token != get_edge_to_core_token():
        return jsonify({"error": "Missing or invalid X-Edge-Token"}), 401

    try:
        count = provisioning_service.sync_devices_from_core()
        return jsonify({"updated": count}), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
