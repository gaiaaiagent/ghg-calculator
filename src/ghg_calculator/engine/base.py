"""Base calculator interface for all scope calculators."""

from abc import ABC, abstractmethod

from ..factors.gwp import get_gwp, to_co2e
from ..factors.registry import FactorRegistry
from ..models.activity import ActivityRecord
from ..models.enums import GasType, GWPAssessment
from ..models.results import EmissionResult, GasBreakdown


class BaseScopeCalculator(ABC):
    """Base class for all scope calculators."""

    def __init__(self, registry: FactorRegistry, gwp_assessment: GWPAssessment = GWPAssessment.AR5):
        self.registry = registry
        self.gwp_assessment = gwp_assessment

    @abstractmethod
    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Calculate emissions for a single activity record.

        Returns a list because some activities produce multiple results
        (e.g., Scope 2 produces both location-based and market-based).
        """
        ...

    def _build_gas_breakdown(
        self,
        co2_kg: float,
        ch4_kg: float,
        n2o_kg: float,
    ) -> list[GasBreakdown]:
        """Build per-gas breakdown with CO2e conversion."""
        breakdown = []
        for gas, mass in [
            (GasType.CO2, co2_kg),
            (GasType.CH4, ch4_kg),
            (GasType.N2O, n2o_kg),
        ]:
            if mass > 0:
                gwp = get_gwp(gas, self.gwp_assessment)
                breakdown.append(
                    GasBreakdown(
                        gas=gas,
                        mass_kg=mass,
                        co2e_kg=to_co2e(mass, gas, self.gwp_assessment),
                        gwp_used=gwp,
                        gwp_assessment=self.gwp_assessment,
                    )
                )
        return breakdown

    def _total_co2e(self, breakdown: list[GasBreakdown]) -> float:
        """Sum CO2e from gas breakdown."""
        return sum(g.co2e_kg for g in breakdown)
