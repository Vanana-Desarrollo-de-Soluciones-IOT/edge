"""KafkaPresencePublisher — ACL for publishing IAM presence events to Kafka.

Encapsulates the Kafka producer details for the IAM bounded context,
keeping domain and application layers decoupled from messaging infrastructure.
"""

import logging

from shared.infrastructure.kafka_client import KafkaInfrastructureClient
from shared.infrastructure.kafka_topics import ClairKafkaTopics

logger = logging.getLogger(__name__)


class KafkaPresencePublisher:
    """Publishes DevicePresenceChanged integration events to Kafka."""

    def __init__(self, kafka_client: KafkaInfrastructureClient | None = None) -> None:
        self._kafka_client = kafka_client or KafkaInfrastructureClient()
        self._producer = self._kafka_client.create_producer()

    def publish_device_presence_changed(self, payload: dict) -> bool:
        """Publish a presence change event to clair.device.presence.changed.

        Args:
            payload: Dict with device_id, hardware_id, status, occurred_at.

        Returns:
            True if Kafka accepted the record, False otherwise.
        """
        try:
            hardware_id = payload.get("hardware_id", "unknown")
            self._producer.send(
                ClairKafkaTopics.DEVICE_PRESENCE_CHANGED.name,
                key=hardware_id,
                value=payload,
            )
            return True
        except Exception as exc:
            logger.warning("Failed to publish presence event to Kafka: %s", exc)
            return False

    def close(self) -> None:
        if self._producer:
            self._producer.flush()
