"""Application services for alert condition state transitions."""

from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

from alerting.domain.commands.record_alert_condition_state_changed_command import (
    RecordAlertConditionStateChangedCommand,
)
from alerting.application.outboundservices.acl.kafka_alerting_publisher import (
    KafkaAlertingPublisher,
)


class AlertConditionStateApplicationService:
    """Orchestrates publishing condition state changes to clair-core."""

    def __init__(self, publisher: KafkaAlertingPublisher | None = None) -> None:
        self._publisher = publisher or KafkaAlertingPublisher()

    def record_condition_state_changed(self, command: RecordAlertConditionStateChangedCommand) -> bool:
        """Publish a condition state change integration event.

        Returns:
            True if Kafka accepted the record, False otherwise.
        """

        occurred_at = self._normalize_iso_timestamp(command.occurred_at)
        recorded_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        payload = {
            "device_id": command.device_id,
            "hardware_id": command.hardware_id,
            "metric": command.metric.upper(),
            "condition_state": command.condition_state.value,
            "occurred_at": occurred_at,
            "recorded_at": recorded_at,
        }
        return self._publisher.publish_alert_condition_state_changed(payload)

    @staticmethod
    def _normalize_iso_timestamp(candidate: str | None) -> str:
        """Return an ISO-8601 UTC timestamp string.

        Accepts None and returns now().
        """
        if candidate is None:
            return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        try:
            parsed = dateutil_parser.parse(candidate)
            return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid timestamp format: {candidate}") from exc
