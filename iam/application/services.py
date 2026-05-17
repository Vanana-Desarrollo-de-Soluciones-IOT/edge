"""IAM application services.

Orchestrates device authentication by coordinating domain services
with infrastructure repositories.
"""

from iam.domain.services import AuthService
from iam.infrastructure.repositories import DeviceRepository


class AuthApplicationService:
    """Application service that orchestrates IAM authentication workflows.

    Coordinates between the AuthService (domain logic) and
    DeviceRepository (infrastructure) to authenticate devices.
    """

    def __init__(self):
        self.device_repository = DeviceRepository()
        self.auth_service = AuthService()

    def authenticate(self, device_id, api_key):
        """Authenticate a device by its ID and API key.

        Args:
            device_id: The logical device identifier.
            api_key: The secret API key provided via X-API-Key header.

        Returns:
            True if the device exists and is allowed by its synchronized status.
        """
        device = self.device_repository.find_by_id_and_api_key(device_id, api_key)
        return self.auth_service.authenticate(device)
