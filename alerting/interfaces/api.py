"""Alerting API — Flask blueprint for embedded condition state transitions."""

from flask import Blueprint, jsonify, request

from alerting.application.services.alert_condition_state_application_service import (
    AlertConditionStateApplicationService,
)
from alerting.domain.commands.record_alert_condition_state_changed_command import (
    RecordAlertConditionStateChangedCommand,
)
from alerting.domain.valueobjects.alert_condition_state import AlertConditionState
from alerting.interfaces.resources.alert_condition_state_changed_request import (
    AlertConditionStateChangedRequest,
)
from iam.interfaces.services import authenticate_request

alerting_api = Blueprint("alerting_api", __name__)

alert_condition_service = AlertConditionStateApplicationService()


@alerting_api.route("/api/v1/device/alert-condition", methods=["POST"])
def record_alert_condition_state_changed():
    """Record an embedded condition state change and publish it to Kafka.

    Headers:
        Content-Type: application/json
        X-Hardware-Id: <physical hardware identifier>
        X-API-Key: <device secret key>

    Body (JSON):
        {
            "metric": "CO2",
            "conditionState": "CRITICAL",
            "occurredAt": "2026-05-26T12:34:56Z"  # optional
        }

    Returns:
        202: Event accepted for publishing.
        400: Missing/invalid fields.
        401: Authentication failure.
        503: Kafka unavailable/publish failure.
    """
    auth_error = authenticate_request(update_last_seen=False)
    if auth_error is not None:
        return auth_error

    try:
        data = request.get_json()
        req = AlertConditionStateChangedRequest.from_dict(data)

        hardware_id = request.headers.get("X-Hardware-Id")
        if not hardware_id:
            return jsonify({"error": "Missing X-Hardware-Id header"}), 401

        device_id = hardware_id

        state = AlertConditionState(req.condition_state.upper())
        command = RecordAlertConditionStateChangedCommand(
            device_id=device_id,
            hardware_id=hardware_id,
            metric=req.metric.upper(),
            condition_state=state,
            occurred_at=req.occurred_at,
        )

        ok = alert_condition_service.record_condition_state_changed(command)
        if not ok:
            return jsonify({"error": "Kafka publish failed"}), 503

        return jsonify({"status": "accepted"}), 202
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
