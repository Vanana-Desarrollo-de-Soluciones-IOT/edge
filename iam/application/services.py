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

    def authenticate(self, hardware_id, device_secret):
        """Authenticate a physical device by its hardware ID and device secret.

        Args:
            hardware_id: The physical hardware identifier.
            device_secret: The secret key provided by the physical embedded device.

        Returns:
            True if the device exists and is allowed by its synchronized status.
        """
        device = self.device_repository.find_by_hardware_id_and_device_secret(hardware_id, device_secret)
        return self.auth_service.authenticate(device)
