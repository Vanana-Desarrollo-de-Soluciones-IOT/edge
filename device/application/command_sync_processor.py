"""CommandSyncProcessor — background worker for Core -> Edge command synchronization.

Implements a polling loop that periodically fetches pending device commands
from clair-core and caches them locally for embedded device consumption.
"""

import logging
import threading
import time
from typing import Optional

from device.application.outboundservices.acl.external_core_service import (
    ExternalCoreService,
)
from device.application.services import DeviceCommandApplicationService
from device.domain.commands import SynchronizeDeviceCommandsCommand
from shared.infrastructure.database import db

logger = logging.getLogger(__name__)


class CommandSyncProcessor:
    """Background processor that polls clair-core for pending device commands.

    Guarantees eventual delivery by periodically synchronizing commands
    from the core into the edge local cache.
    """

    POLL_INTERVAL_SECONDS = 10
    BATCH_LIMIT = 100

    def __init__(self) -> None:
        self.command_application_service = DeviceCommandApplicationService()
        self.external_core_service = ExternalCoreService()
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
        logger.info("CommandSyncProcessor started")

    def stop(self) -> None:
        """Signal the processor to stop."""
        self._running = False

    def _run(self) -> None:
        """Main loop with per-iteration DB connection management."""
        while self._running:
            try:
                if db.is_closed():
                    db.connect()
                self._sync_pending_commands()
                self._cycles += 1
            except Exception:
                logger.exception("Command sync processor loop error")
            finally:
                if not db.is_closed():
                    db.close()
            time.sleep(self.POLL_INTERVAL_SECONDS)

    def _sync_pending_commands(self) -> None:
        """Fetch pending commands from clair-core and cache them locally."""
        commands = self.command_application_service.synchronize_pending_commands(
            SynchronizeDeviceCommandsCommand(limit=self.BATCH_LIMIT)
        )
        if commands:
            logger.info(
                "CommandSyncProcessor synchronized %d commands from core",
                len(commands),
            )
