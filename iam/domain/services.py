"""IAM domain services.

Contains authentication business rules that operate on the Device entity.
"""


class AuthService:
    """Domain service for device authentication logic.

    Encapsulates the business rule: a device can only authenticate
    if it exists AND has an ACTIVE status.
    """

    @staticmethod
    def authenticate(device):
        """Verify that a device is allowed to authenticate.

        Args:
            device: A Device entity instance, or None if not found.

        Returns:
            True only if device is not None and device.status == "ACTIVE".
        """
        return device is not None and device.status == "ACTIVE"
