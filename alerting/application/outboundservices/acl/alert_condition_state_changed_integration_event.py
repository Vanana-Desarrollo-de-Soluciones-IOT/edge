"""AlertConditionStateChangedIntegrationEvent — outbound ACL DTO.

Published by the Alerting bounded context to Kafka topic
`clair.device.alert.condition.changed` for consumption by clair-core.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertConditionStateChangedIntegrationEvent:
    device_id: str
    hardware_id: str
    metric: str
    condition_state: str
    recorded_at: str
    occurred_at: str
