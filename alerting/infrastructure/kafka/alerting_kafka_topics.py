"""Alerting bounded context Kafka topic definitions."""

from shared.infrastructure.kafka_topics import KafkaTopicConfig


class AlertingKafkaTopics:
    """Topics produced or consumed by the Alerting bounded context."""

    ALERT_CONDITION_STATE_CHANGED = KafkaTopicConfig(
        name="clair.device.alert.condition.changed",
        num_partitions=1,
        replication_factor=1,
        retention_ms=604_800_000,
    )

    @classmethod
    def all(cls) -> list[KafkaTopicConfig]:
        return [cls.ALERT_CONDITION_STATE_CHANGED]
