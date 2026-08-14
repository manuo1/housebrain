from enum import StrEnum


class EquipmentStatusLevel(StrEnum):
    """
    Generic status level for an equipment card, orthogonal to the readable
    state text. The front uses this alone to pick a color — it never
    parses/interprets `state` itself, keeping that logic in the backend.
    """

    OK = "ok"
    WARNING = "warning"
    PROBLEM = "problem"
