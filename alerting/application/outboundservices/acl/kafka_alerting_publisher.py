"""KafkaAlertingPublisher — ACL for publishing alerting integration events."""

import logging

from alerting.infrastructure.kafka.alerting_kafka_topics import AlertingKafkaTopics
from shared.infrastructure.kafka_client import KafkaInfrastructureClient

logger = logging.getLogger(__name__)


class KafkaAlertingPublisher:
    """Publishes alerting integration events to Kafka."""

    def __init__(self, kafka_client: KafkaInfrastructureClient | None = None) -> None:
        self._kafka_client = kafka_client or KafkaInfrastructureClient()
        self._producer = self._kafka_client.create_producer()

    def publish_alert_condition_state_changed(self, payload: dict) -> bool:
        """Publish a condition transition to clair.device.alert.condition.changed."""

        if self._producer is None:
            logger.warning("Kafka producer unavailable; alert condition event skipped")
            return False

        try:
            hardware_id = payload.get("hardware_id", "unknown")
            self._producer.send(
                AlertingKafkaTopics.ALERT_CONDITION_STATE_CHANGED.name,
                key=hardware_id,
                value=payload,
            )
            return True
        except Exception as exc:
            logger.warning("Failed to publish alert condition event to Kafka: %s", exc)
            return False

    def close(self) -> None:
        if self._producer:
            self._producer.flush()
