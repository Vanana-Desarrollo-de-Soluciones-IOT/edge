"""RecordAlertConditionStateChangedCommand.

Intention to record that a given metric condition state changed for a device.
"""

from dataclasses import dataclass

from alerting.domain.valueobjects.alert_condition_state import AlertConditionState


@dataclass(frozen=True)
class RecordAlertConditionStateChangedCommand:
    device_id: str
    hardware_id: str
    metric: str
    condition_state: AlertConditionState
    occurred_at: str | None = None

    def __post_init__(self) -> None:
        if not self.device_id:
            raise ValueError("device_id is required")
        if not self.hardware_id:
            raise ValueError("hardware_id is required")
        if not self.metric:
            raise ValueError("metric is required")
        if self.condition_state is None:
            raise ValueError("condition_state is required")
