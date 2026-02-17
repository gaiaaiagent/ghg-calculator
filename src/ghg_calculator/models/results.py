"""Emission calculation result models."""

from datetime import datetime

from pydantic import BaseModel, Field

from .enums import (
    DataQualityScore,
    GasType,
    GWPAssessment,
    Scope,
    Scope1Category,
    Scope2Method,
    Scope3Category,
)
from .quality import DataQualityIndicator


class GasBreakdown(BaseModel):
    """Per-gas emission breakdown."""

    gas: GasType
    mass_kg: float = Field(description="Mass in kg of the specific gas")
    co2e_kg: float = Field(description="CO2-equivalent in kg using specified GWP")
    gwp_used: float = Field(description="GWP value used for conversion")
    gwp_assessment: GWPAssessment = GWPAssessment.AR5


class EmissionResult(BaseModel):
    """Result of a single emission calculation."""

    # Source activity
    activity_id: str | None = None
    activity_name: str | None = None

    # Classification
    scope: Scope
    scope1_category: Scope1Category | None = None
    scope2_method: Scope2Method | None = None
    scope3_category: Scope3Category | None = None

    # Total emissions
    total_co2e_kg: float = Field(description="Total CO2-equivalent emissions in kg")

    @property
    def total_co2e_tonnes(self) -> float:
        """Total CO2-equivalent emissions in metric tonnes."""
        return self.total_co2e_kg / 1000.0

    # Per-gas breakdown
    gas_breakdown: list[GasBreakdown] = Field(default_factory=list)

    # Factor used
    factor_id: str | None = None
    factor_source: str | None = None

    # Input echo
    activity_quantity: float | None = None
    activity_unit: str | None = None

    # Quality
    data_quality: DataQualityIndicator | None = None
    data_quality_score: DataQualityScore | None = None

    # Metadata
    gwp_assessment: GWPAssessment = GWPAssessment.AR5
    calculated_at: datetime = Field(default_factory=datetime.now)
    notes: list[str] = Field(default_factory=list)


class ScopeResult(BaseModel):
    """Aggregated results for a single scope."""

    scope: Scope
    total_co2e_kg: float = 0.0
    results: list[EmissionResult] = Field(default_factory=list)

    @property
    def total_co2e_tonnes(self) -> float:
        return self.total_co2e_kg / 1000.0

    def add_result(self, result: EmissionResult) -> None:
        self.results.append(result)
        self.total_co2e_kg += result.total_co2e_kg


class InventoryResult(BaseModel):
    """Complete GHG inventory result across all scopes."""

    name: str = "GHG Inventory"
    year: int | None = None

    scope1: ScopeResult = Field(default_factory=lambda: ScopeResult(scope=Scope.SCOPE_1))
    scope2_location: ScopeResult = Field(default_factory=lambda: ScopeResult(scope=Scope.SCOPE_2))
    scope2_market: ScopeResult = Field(default_factory=lambda: ScopeResult(scope=Scope.SCOPE_2))
    scope3: ScopeResult = Field(default_factory=lambda: ScopeResult(scope=Scope.SCOPE_3))

    @property
    def total_co2e_kg(self) -> float:
        """Total using location-based Scope 2."""
        return self.scope1.total_co2e_kg + self.scope2_location.total_co2e_kg + self.scope3.total_co2e_kg

    @property
    def total_co2e_tonnes(self) -> float:
        return self.total_co2e_kg / 1000.0

    @property
    def all_results(self) -> list[EmissionResult]:
        return (
            self.scope1.results
            + self.scope2_location.results
            + self.scope2_market.results
            + self.scope3.results
        )

    def add_result(self, result: EmissionResult) -> None:
        """Route a result to the appropriate scope bucket."""
        if result.scope == Scope.SCOPE_1:
            self.scope1.add_result(result)
        elif result.scope == Scope.SCOPE_2:
            if result.scope2_method == Scope2Method.MARKET_BASED:
                self.scope2_market.add_result(result)
            else:
                self.scope2_location.add_result(result)
        elif result.scope == Scope.SCOPE_3:
            self.scope3.add_result(result)
