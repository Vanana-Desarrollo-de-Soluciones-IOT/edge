"""CoreContextFacade — ACL interface for clair-core messaging via Kafka.

Defines the contract that the edge service uses to publish integration
events into clair-core bounded contexts without coupling to internal Core
details or transport implementation.
"""

from abc import ABC, abstractmethod


class CoreContextFacade(ABC):
    """Anti-corruption layer facade for Kafka-based core integration."""

    @abstractmethod
    def publish_telemetry_recorded(self, payload: dict) -> bool:
        """Publish a TelemetryRecorded integration event to clair-core.

        Args:
            payload: The telemetry payload dict matching the Core contract.

        Returns:
            True if Kafka accepted the record, False otherwise.
        """
        ...

    @abstractmethod
    def publish_command_acknowledged(self, payload: dict) -> bool:
        """Publish a CommandAcknowledged integration event to clair-core.

        Args:
            payload: Dict with device_id, command_id, status, failure_reason.

        Returns:
            True if Kafka accepted the record, False otherwise.
        """
        ...
