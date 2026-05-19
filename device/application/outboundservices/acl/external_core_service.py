"""ExternalCoreService — consumer-side ACL service for clair-core.

Translates the original device payload dict into the exact JSON expected by
the Core evaluation endpoint, keeping the device bounded context decoupled from
HTTP concerns.
"""

from device.application.outboundservices.acl.core_context_facade import (
    CoreContextFacade,
)
from device.application.outboundservices.acl.core_context_facade_impl import (
    CoreContextFacadeImpl,
)


class ExternalCoreService:
    """ACL service that forwards the original device payload to clair-core.

    This is the consumer-side anti-corruption layer: it receives the raw
    payload dict that the device sent to the edge and forwards it verbatim
    to the Core, adding only the X-API-Key header.
    """

    def __init__(self, facade: CoreContextFacade | None = None):
        self._facade = facade or CoreContextFacadeImpl()

    def forward_raw_payload(self, api_key: str, payload: dict) -> bool:
        """Forward the original device payload dict to clair-core.

        Args:
            api_key: The device API key used by the Core to resolve the device.
            payload: The raw JSON dict as received from the device.

        Returns:
            True if the Core acknowledged the telemetry, False otherwise.
        """
        return self._facade.forward_telemetry(api_key, payload)
