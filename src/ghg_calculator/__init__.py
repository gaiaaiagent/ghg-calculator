"""GHG Emissions Calculator — GHG Protocol Corporate Standard implementation."""

from .engine.calculator import GHGCalculator
from .factors.registry import FactorRegistry
from .models.activity import ActivityRecord
from .models.results import EmissionResult, InventoryResult

__all__ = [
    "ActivityRecord",
    "EmissionResult",
    "GHGCalculator",
    "FactorRegistry",
    "InventoryResult",
]
__version__ = "0.1.0"
