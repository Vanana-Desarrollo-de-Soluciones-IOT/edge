"""CoreContextFacadeImpl — HTTP implementation of the Core ACL facade."""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from device.application.outboundservices.acl.core_context_facade import (
    CoreContextFacade,
)
from shared.infrastructure.environment import (
    get_clair_core_device_command_ack_url,
    get_clair_core_device_commands_pending_url,
    get_clair_core_evaluations_url,
    get_edge_to_core_token,
)

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

    def fetch_pending_device_commands(self, limit: int) -> list[dict]:
        """GET pending commands from clair-core /api/v1/devices/commands/pending."""
        url = f"{get_clair_core_device_commands_pending_url()}?limit={limit}"
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "X-Edge-Token": get_edge_to_core_token(),
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=10) as response:
                if not (200 <= response.status < 300):
                    return []
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            logger.warning(
                "Core returned HTTP %s for command fetch: %s",
                exc.code,
                exc.read().decode("utf-8", errors="replace")[:200],
            )
            return []
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            logger.warning("Unable to fetch clair-core device commands: %s", exc)
            return []

    def acknowledge_device_command(
        self,
        device_id: str,
        command_id: str,
        status: str,
        failure_reason: str | None = None,
    ) -> bool:
        """POST command ACK to clair-core."""
        body = json.dumps({
            "status": status,
            "failureReason": failure_reason,
        }).encode("utf-8")
        request = Request(
            get_clair_core_device_command_ack_url(device_id, command_id),
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Edge-Token": get_edge_to_core_token(),
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                return 200 <= response.status < 300
        except HTTPError as exc:
            logger.warning(
                "Core returned HTTP %s for command ACK: %s",
                exc.code,
                exc.read().decode("utf-8", errors="replace")[:200],
            )
            return False
        except (URLError, TimeoutError) as exc:
            logger.warning("Unable to ACK clair-core device command: %s", exc)
            return False
