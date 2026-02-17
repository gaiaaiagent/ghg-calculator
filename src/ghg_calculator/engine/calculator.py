"""GHG Calculator orchestrator — routes activities to scope calculators."""

from ..factors.registry import FactorRegistry
from ..models.activity import ActivityRecord
from ..models.enums import GWPAssessment, Scope, Scope1Category
from ..models.results import EmissionResult, InventoryResult
from .scope1.fugitive import FugitiveEmissionsCalculator
from .scope1.mobile import MobileCombustionCalculator
from .scope1.process import ProcessEmissionsCalculator
from .scope1.stationary import StationaryCombustionCalculator
from .scope2.electricity import ElectricityCalculator
from .scope3.base import Scope3Calculator


class GHGCalculator:
    """Main orchestrator that routes activities to appropriate scope calculators."""

    def __init__(
        self,
        registry: FactorRegistry | None = None,
        gwp_assessment: GWPAssessment = GWPAssessment.AR5,
    ):
        self.registry = registry or FactorRegistry.load()
        self.gwp_assessment = gwp_assessment

        # Initialize scope calculators
        self._scope1_stationary = StationaryCombustionCalculator(self.registry, gwp_assessment)
        self._scope1_mobile = MobileCombustionCalculator(self.registry, gwp_assessment)
        self._scope1_fugitive = FugitiveEmissionsCalculator(self.registry, gwp_assessment)
        self._scope1_process = ProcessEmissionsCalculator(self.registry, gwp_assessment)
        self._scope2_electricity = ElectricityCalculator(self.registry, gwp_assessment)
        self._scope3 = Scope3Calculator(self.registry, gwp_assessment)

    def calculate_single(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Calculate emissions for a single activity record.

        Returns a list because some activities produce multiple results.
        """
        if activity.scope == Scope.SCOPE_1:
            return self._route_scope1(activity)
        elif activity.scope == Scope.SCOPE_2:
            return self._scope2_electricity.calculate(activity)
        elif activity.scope == Scope.SCOPE_3:
            return self._scope3.calculate(activity)
        else:
            raise ValueError(f"Unknown scope: {activity.scope}")

    def calculate_inventory(
        self,
        activities: list[ActivityRecord],
        name: str = "GHG Inventory",
        year: int | None = None,
    ) -> InventoryResult:
        """Calculate a complete GHG inventory from multiple activity records."""
        inventory = InventoryResult(name=name, year=year)

        for activity in activities:
            results = self.calculate_single(activity)
            for result in results:
                inventory.add_result(result)

        return inventory

    def _route_scope1(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Route Scope 1 activity to the appropriate sub-calculator."""
        category = activity.scope1_category

        if category == Scope1Category.STATIONARY_COMBUSTION:
            return self._scope1_stationary.calculate(activity)
        elif category == Scope1Category.MOBILE_COMBUSTION:
            return self._scope1_mobile.calculate(activity)
        elif category == Scope1Category.FUGITIVE_EMISSIONS:
            return self._scope1_fugitive.calculate(activity)
        elif category == Scope1Category.PROCESS_EMISSIONS:
            return self._scope1_process.calculate(activity)
        else:
            # Try to infer from activity data
            if activity.refrigerant_type:
                return self._scope1_fugitive.calculate(activity)
            if activity.fuel_type or activity.custom_fuel:
                return self._scope1_stationary.calculate(activity)
            raise ValueError(
                f"Cannot determine Scope 1 category. "
                f"Set scope1_category to one of: {[c.value for c in Scope1Category]}"
            )
