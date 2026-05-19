"""TelemetryOutboxProcessor — background worker for guaranteed core delivery.

Implements the outbox pattern with exponential backoff and circuit breaker
protection for forwarding telemetry payloads to clair-core.
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from device.application.outboundservices.acl.external_core_service import (
    ExternalCoreService,
)
from device.domain.outbox_entry import OutboxEntry
from device.infrastructure.outbox.outbox_repository import OutboxRepository
from device.infrastructure.repositories import DeviceTelemetryRepository
from device.infrastructure.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
)
from shared.infrastructure.database import db

logger = logging.getLogger(__name__)


class TelemetryOutboxProcessor:
    """Background processor that polls the outbox and forwards payloads to core.

    Guarantees at-least-once delivery by retrying with exponential backoff.
    Protects the core from overload via circuit breaker.
    """

    MAX_RETRIES = 5
    BASE_DELAY_SECONDS = 5
    MAX_DELAY_SECONDS = 300
    POLL_INTERVAL_SECONDS = 5
    CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes
    BATCH_SIZE = 10

    def __init__(self) -> None:
        self.outbox_repository = OutboxRepository()
        self.telemetry_repository = DeviceTelemetryRepository()
        self.external_core_service = ExternalCoreService()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3, recovery_timeout=30.0
        )
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cycles = 0

    def start(self) -> None:
        """Start the background processor thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("TelemetryOutboxProcessor started")

    def stop(self) -> None:
        """Signal the processor to stop."""
        self._running = False

    def _run(self) -> None:
        """Main loop with per-iteration DB connection management."""
        while self._running:
            try:
                if db.is_closed():
                    db.connect()
                self._process_batch()
                self._cycles += 1
                cleanup_every = self.CLEANUP_INTERVAL_SECONDS // self.POLL_INTERVAL_SECONDS
                if cleanup_every > 0 and self._cycles % cleanup_every == 0:
                    self._cleanup_sent()
            except Exception:
                logger.exception("Outbox processor loop error")
            finally:
                if not db.is_closed():
                    db.close()
            time.sleep(self.POLL_INTERVAL_SECONDS)

    def _process_batch(self) -> None:
        """Fetch and attempt to send pending outbox entries."""
        entries = self.outbox_repository.find_pending(limit=self.BATCH_SIZE)
        if not entries:
            return

        for entry in entries:
            try:
                self._send_entry(entry)
            except CircuitBreakerOpenException:
                logger.warning(
                    "Circuit breaker OPEN; pausing outbox processing until recovery"
                )
                return
            except Exception as exc:
                logger.warning(
                    "Failed to process outbox entry %s: %s", entry.id, exc
                )

    def _send_entry(self, entry: OutboxEntry) -> bool:
        """Attempt to forward a single outbox entry to clair-core.

        Args:
            entry: OutboxEntry to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        payload, api_key = self._build_payload_and_api_key(entry)
        try:
            self.circuit_breaker.call(
                self.external_core_service.forward_raw_payload,
                api_key,
                payload,
            )
            self.outbox_repository.mark_sent(entry.id)
            logger.info("Outbox entry %s forwarded to core", entry.id)
            return True
        except CircuitBreakerOpenException:
            raise
        except Exception as exc:
            error = str(exc)
            if entry.retry_count >= self.MAX_RETRIES:
                self.outbox_repository.mark_dead_letter(entry.id, error)
                logger.error(
                    "Outbox entry %s moved to dead letter after %s retries: %s",
                    entry.id,
                    entry.retry_count,
                    error,
                )
            else:
                next_retry = self._calculate_next_retry(entry.retry_count)
                self.outbox_repository.mark_retry(entry.id, next_retry, error)
                logger.info(
                    "Outbox entry %s scheduled for retry %s at %s",
                    entry.id,
                    entry.retry_count + 1,
                    next_retry.isoformat(),
                )
            return False

    def _build_payload_and_api_key(self, entry: OutboxEntry) -> tuple[dict, str]:
        """Rebuild the outbound payload from the aggregate referenced by outbox."""
        if entry.aggregate_type != "TELEMETRY" or entry.event_type != "TELEMETRY_RECORDED":
            raise ValueError(f"Unsupported outbox event: {entry.aggregate_type}/{entry.event_type}")

        record = self.telemetry_repository.find_by_id(entry.aggregate_id)
        if record is None:
            raise ValueError(f"Telemetry record not found: {entry.aggregate_id}")

        device = self.telemetry_repository.find_cached_device_by_hardware_id(record.device_id)
        if device is None:
            raise ValueError(f"Cached device not found: {record.device_id}")

        payload = {
            "deviceId": record.device_id,
            "timestamp": record.device_time,
            "uptime": self._format_uptime(record.uptime_seconds),
            "airQuality": {
                "co2": record.air_quality.co2,
                "temperature": record.air_quality.temperature,
                "humidity": record.air_quality.humidity,
            },
            "particulateMatter": {
                "pm1_0": record.particulate_matter.pm1_0,
                "pm2_5": record.particulate_matter.pm2_5,
                "pm10": record.particulate_matter.pm10,
            },
            "connectivity": {
                "status": record.connectivity.status,
                "network": record.connectivity.network,
                "signalStrength": record.connectivity.signal_strength,
            },
            "location": {
                "country": record.location.country,
            },
            "healthStatus": record.health_status,
            "status": record.status,
            "created_at": record.recorded_at.isoformat(),
        }
        return payload, device.api_key

    def _format_uptime(self, uptime_seconds: int) -> str:
        """Format uptime seconds as HH:MM:SS for clair-core compatibility."""
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _calculate_next_retry(self, retry_count: int) -> datetime:
        """Calculate next retry timestamp using exponential backoff.

        Args:
            retry_count: Current number of failed attempts.

        Returns:
            UTC datetime for the next retry attempt.
        """
        delay = min(
            self.BASE_DELAY_SECONDS * (2 ** retry_count),
            self.MAX_DELAY_SECONDS,
        )
        return datetime.now(timezone.utc) + timedelta(seconds=delay)

    def _cleanup_sent(self) -> None:
        """Delete old sent outbox records to prevent table bloat."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        deleted = self.outbox_repository.delete_sent_older_than(cutoff)
        if deleted:
            logger.info("Cleaned up %s old sent outbox records", deleted)
