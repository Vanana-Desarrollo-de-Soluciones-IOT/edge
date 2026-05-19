"""CoreContextFacadeImpl — HTTP implementation of the Core ACL facade."""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from device.application.outboundservices.acl.core_context_facade import (
    CoreContextFacade,
)
from shared.infrastructure.environment import get_clair_core_evaluations_url

logger = logging.getLogger(__name__)


class CoreContextFacadeImpl(CoreContextFacade):
    """HTTP-based ACL implementation that posts telemetry to clair-core."""

    def forward_telemetry(self, api_key: str, payload: dict) -> bool:
        """POST telemetry to clair-core /api/v1/evaluations/telemetry."""
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            get_clair_core_evaluations_url(),
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                return 200 <= response.status < 300
        except HTTPError as exc:
            logger.warning(
                "Core returned HTTP %s for telemetry forward: %s",
                exc.code,
                exc.read().decode("utf-8", errors="replace")[:200],
            )
            return False
        except (URLError, TimeoutError) as exc:
            logger.warning("Unable to reach clair-core for telemetry forward: %s", exc)
            return False
