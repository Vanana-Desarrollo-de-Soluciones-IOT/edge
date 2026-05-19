"""HTTP ACL for reading master devices from clair-core."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shared.infrastructure.environment import get_edge_to_core_token


class ClairCoreDeviceService:
    """Anti-corruption layer for the clair-core device API."""

    def fetch_devices(self, source_url):
        """Fetch devices from clair-core and transform them into edge cache records."""
        request = Request(
            source_url,
            headers={
                "Accept": "application/json",
                "X-Edge-Token": get_edge_to_core_token(),
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"Unable to sync devices from clair-core: {exc}") from exc

        if isinstance(payload, dict) and "content" in payload:
            payload = payload["content"]
        if not isinstance(payload, list):
            raise ValueError("clair-core devices response must be a list")

        return [self._to_cache_record(device) for device in payload]

    @staticmethod
    def _to_cache_record(device):
        return {
            "device_id": str(device.get("id") or device.get("device_id")),
            "hardware_id": device.get("hardwareId") or device.get("hardware_id"),
            "api_key": device.get("apiKey") or device.get("api_key"),
            "device_secret": device.get("deviceSecret") or device.get("device_secret"),
            "status": device.get("status"),
        }
