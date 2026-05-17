"""Provisioning API for webhook-driven device cache updates."""

from flask import Blueprint, jsonify, request

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
        device: Object with device_id/id, hardware_id/hardwareId, api_key/apiKey, status.

    Returns:
        200: Device cache was updated.
        400: Missing fields or invalid payload.
    """
    try:
        payload = request.get_json() or {}
        resource = DeviceCacheResource.from_dict(payload.get("device", payload))
        count = provisioning_service.synchronize_devices(
            SynchronizeDevicesCommand([resource.to_command_record()])
        )
        return jsonify({"updated": count}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
