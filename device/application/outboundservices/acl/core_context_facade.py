"""CoreContextFacade — ACL interface for clair-core Evaluation context.

Defines the contract that the edge service uses to forward telemetry
into the clair-core Evaluation bounded context without coupling to
internal Core details.
"""

from abc import ABC, abstractmethod


class CoreContextFacade(ABC):
    """Anti-corruption layer facade for the clair-core evaluation endpoint."""

    @abstractmethod
    def forward_telemetry(self, api_key: str, payload: dict) -> bool:
        """Forward a telemetry payload to clair-core for evaluation.

        Args:
            api_key: The device API key to authenticate the request.
            payload: The telemetry payload dict matching the Core contract.

        Returns:
            True if the Core acknowledged the telemetry (2xx), False otherwise.
        """
        ...
