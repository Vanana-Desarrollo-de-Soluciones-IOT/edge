"""OutboxEntry entity — represents a pending outbound message to clair-core.

Part of the Device bounded context; ensures reliable delivery of telemetry
payloads from edge to core via the outbox pattern.
"""

from datetime import datetime, timezone
from typing import Optional


class OutboxEntry:
    """Domain entity for an outbox record ensuring reliable delivery to clair-core.

    Attributes:
        id: Database ID (None before persistence).
        device_id: Source device identifier.
        payload: Serialized JSON payload to forward.
        api_key: Device API key for core authentication.
        status: pending, sent, or dead_letter.
        retry_count: Number of delivery attempts made.
        next_retry_at: UTC timestamp when the entry is eligible for retry.
        created_at: UTC timestamp when the entry was created.
        sent_at: UTC timestamp when successfully sent (None if not sent).
        error_message: Last error message if delivery failed.
    """

    def __init__(
        self,
        device_id: str,
        payload: str,
        api_key: str,
        status: str = "pending",
        retry_count: int = 0,
        next_retry_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        id: Optional[int] = None,
        sent_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
    ):
        if not device_id:
            raise ValueError("device_id is required")
        if not payload:
            raise ValueError("payload is required")
        if not api_key:
            raise ValueError("api_key is required")
        if status not in ("pending", "sent", "dead_letter"):
            raise ValueError("status must be pending, sent, or dead_letter")

        self.id = id
        self.device_id = device_id
        self.payload = payload
        self.api_key = api_key
        self.status = status
        self.retry_count = retry_count
        self.next_retry_at = next_retry_at or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)
        self.sent_at = sent_at
        self.error_message = error_message
