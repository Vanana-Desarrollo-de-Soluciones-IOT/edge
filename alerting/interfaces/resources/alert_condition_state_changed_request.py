"""Boundary DTO for embedded -> edge condition transitions."""

from dataclasses import dataclass


@dataclass
class AlertConditionStateChangedRequest:
    metric: str
    condition_state: str
    occurred_at: str | None = None

    @staticmethod
    def from_dict(data: dict) -> "AlertConditionStateChangedRequest":
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")

        # Accept both camelCase and snake_case to make embedded integration easier.
        metric = data.get("metric")
        condition_state = data.get("conditionState") or data.get("condition_state")
        occurred_at = data.get("occurredAt") or data.get("occurred_at")

        if not metric:
            raise ValueError("metric is required")
        if not condition_state:
            raise ValueError("condition_state is required")

        return AlertConditionStateChangedRequest(
            metric=str(metric),
            condition_state=str(condition_state),
            occurred_at=str(occurred_at) if occurred_at is not None else None,
        )
