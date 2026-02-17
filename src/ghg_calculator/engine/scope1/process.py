"""Scope 1 — Process Emissions calculator."""

from ...models.activity import ActivityRecord
from ...models.enums import Scope, Scope1Category
from ...models.results import EmissionResult
from ..base import BaseScopeCalculator


class ProcessEmissionsCalculator(BaseScopeCalculator):
    """Calculates emissions from industrial processes (cement, chemicals, etc.).

    Process emissions typically require custom factors since they are
    highly specific to the industrial process.
    """

    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        if activity.custom_factor is not None:
            total_co2e = activity.quantity * activity.custom_factor
            return [
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_1,
                    scope1_category=Scope1Category.PROCESS_EMISSIONS,
                    total_co2e_kg=total_co2e,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                    notes=["Custom emission factor used for process emissions"],
                )
            ]

        # Try factor registry
        factor = self.registry.find_factor(
            category="process_emissions",
            activity_unit=activity.unit,
            source=activity.factor_source,
        )

        if factor is None:
            raise ValueError(
                "Process emissions require a custom_factor or matching factor in the registry. "
                "Provide custom_factor (kg CO2e per unit of activity)."
            )

        co2_kg = activity.quantity * factor.co2_factor
        ch4_kg = activity.quantity * factor.ch4_factor
        n2o_kg = activity.quantity * factor.n2o_factor

        breakdown = self._build_gas_breakdown(co2_kg, ch4_kg, n2o_kg)
        total_co2e = self._total_co2e(breakdown)

        # If factor has a pre-calculated co2e_factor, use that instead
        if factor.co2e_factor is not None:
            total_co2e = activity.quantity * factor.co2e_factor

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_1,
                scope1_category=Scope1Category.PROCESS_EMISSIONS,
                total_co2e_kg=total_co2e,
                gas_breakdown=breakdown,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=activity.quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
            )
        ]
