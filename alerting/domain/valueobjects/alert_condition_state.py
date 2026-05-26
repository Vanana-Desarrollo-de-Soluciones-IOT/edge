"""Alert condition state value object.

Represents the metric condition classification computed by embedded/edge.
"""

from enum import Enum


class AlertConditionState(str, Enum):
    """Condition state for a metric."""

    CRITICAL = "CRITICAL"
    NORMAL = "NORMAL"
