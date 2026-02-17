"""GHG Calculator data models."""

from .activity import ActivityRecord
from .enums import (
    DataQualityScore,
    FactorSource,
    FuelType,
    GasType,
    GWPAssessment,
    Scope,
    Scope1Category,
    Scope2Method,
    Scope3Category,
)
from .factors import EmissionFactor, FactorVersion
from .quality import DataQualityIndicator
from .report import ChartSpec, ChartType, ReportConfig, ReportFormat
from .results import EmissionResult, GasBreakdown, InventoryResult, ScopeResult

__all__ = [
    "ActivityRecord",
    "ChartSpec",
    "ChartType",
    "DataQualityIndicator",
    "DataQualityScore",
    "EmissionFactor",
    "EmissionResult",
    "FactorSource",
    "FactorVersion",
    "FuelType",
    "GasBreakdown",
    "GWPAssessment",
    "GasType",
    "InventoryResult",
    "ReportConfig",
    "ReportFormat",
    "Scope",
    "Scope1Category",
    "Scope2Method",
    "Scope3Category",
    "ScopeResult",
]
