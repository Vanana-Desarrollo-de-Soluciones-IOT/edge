"""Kafka topic definitions — configured entirely from Python (ORM-style).

Topics, partitions, replication factor, and retention are defined as code,
not external configuration files. The KafkaAdminClient ensures these exist
at runtime.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class KafkaTopicConfig:
    """Topic configuration defined as an immutable dataclass."""

    name: str
    num_partitions: int
    replication_factor: int
    retention_ms: int = 604800000  # 7 days default
    cleanup_policy: str = "delete"

    def to_new_topic_kwargs(self) -> dict:
        """Return kwargs compatible with kafka.admin.NewTopic."""
        return {
            "num_partitions": self.num_partitions,
            "replication_factor": self.replication_factor,
            "topic_configs": {
                "retention.ms": str(self.retention_ms),
                "cleanup.policy": self.cleanup_policy,
            },
        }


class ClairKafkaTopics:
    """Central registry of all Kafka topics used across bounded contexts.

    Treat this as the schema/topic DDL: modify here and the bootstrapper
    will reconcile topics at runtime.
    """

    # ------------------------------------------------------------------
    # device bounded context — outbound (Edge -> Core)
    # ------------------------------------------------------------------
    DEVICE_TELEMETRY_RECORDED = KafkaTopicConfig(
        name="clair.device.telemetry.recorded",
        num_partitions=3,
        replication_factor=1,
        retention_ms=604800000,
    )

    DEVICE_COMMANDS_ACKNOWLEDGED = KafkaTopicConfig(
        name="clair.device.commands.acknowledged",
        num_partitions=1,
        replication_factor=1,
        retention_ms=604800000,
    )

    # ------------------------------------------------------------------
    # device bounded context — inbound (Core -> Edge)
    # ------------------------------------------------------------------
    DEVICE_COMMANDS_PENDING = KafkaTopicConfig(
        name="clair.device.commands.pending",
        num_partitions=3,
        replication_factor=1,
        retention_ms=604800000,
    )

    # ------------------------------------------------------------------
    # iam bounded context — outbound (Edge -> Core)
    # ------------------------------------------------------------------
    DEVICE_PRESENCE_CHANGED = KafkaTopicConfig(
        name="clair.device.presence.changed",
        num_partitions=1,
        replication_factor=1,
        retention_ms=259200000,  # 3 days
    )

    # ------------------------------------------------------------------
    # provisioning bounded context — inbound (Core -> Edge)
    # ------------------------------------------------------------------
    PROVISIONING_DEVICES_CHANGED = KafkaTopicConfig(
        name="clair.provisioning.devices.changed",
        num_partitions=1,
        replication_factor=1,
        retention_ms=604800000,
    )

    PROVISIONING_DEVICES_SYNC_REQUESTED = KafkaTopicConfig(
        name="clair.provisioning.devices.sync.requested",
        num_partitions=1,
        replication_factor=1,
        retention_ms=86400000,  # 1 day
    )

    @classmethod
    def all(cls) -> list[KafkaTopicConfig]:
        """Return every topic that must exist in the Kafka cluster."""
        return [
            cls.DEVICE_TELEMETRY_RECORDED,
            cls.DEVICE_COMMANDS_ACKNOWLEDGED,
            cls.DEVICE_COMMANDS_PENDING,
            cls.DEVICE_PRESENCE_CHANGED,
            cls.PROVISIONING_DEVICES_CHANGED,
            cls.PROVISIONING_DEVICES_SYNC_REQUESTED,
        ]


class KafkaConsumerGroups:
    """Consumer group IDs defined as code."""

    EDGE_COMMAND_CONSUMER = "edge-device-commands-consumer"
    EDGE_PROVISIONING_CONSUMER = "edge-provisioning-consumer"
