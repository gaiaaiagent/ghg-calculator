"""Scope 1 — Stationary Combustion calculator."""

from ...factors.registry import FactorRegistry
from ...models.activity import ActivityRecord
from ...models.enums import GWPAssessment, Scope, Scope1Category
from ...models.results import EmissionResult
from ...units.converter import converter
from ..base import BaseScopeCalculator


class StationaryCombustionCalculator(BaseScopeCalculator):
    """Calculates emissions from stationary combustion sources.

    Covers boilers, furnaces, heaters, generators, etc.
    Formula: CO2e = fuel quantity × emission factor × GWP (per gas)
    """

    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        # Find the appropriate emission factor
        factor = None

        if activity.custom_factor is not None:
            # Use custom factor directly
            total_co2e = activity.quantity * activity.custom_factor
            return [
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_1,
                    scope1_category=Scope1Category.STATIONARY_COMBUSTION,
                    total_co2e_kg=total_co2e,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                    notes=["Custom emission factor used"],
                )
            ]

        # Search for factor by fuel type
        fuel_type = activity.fuel_type.value if activity.fuel_type else activity.custom_fuel
        if fuel_type:
            factor = self.registry.find_factor(
                category="stationary_combustion",
                fuel_type=fuel_type,
                activity_unit=activity.unit,
                source=activity.factor_source,
            )

        if factor is None:
            raise ValueError(
                f"No emission factor found for stationary combustion: "
                f"fuel={fuel_type}, unit={activity.unit}"
            )

        # Convert units if needed
        quantity = activity.quantity
        if activity.unit.lower() != factor.activity_unit.lower():
            try:
                quantity = converter.convert(activity.quantity, activity.unit, factor.activity_unit)
            except Exception:
                raise ValueError(
                    f"Cannot convert {activity.unit} to {factor.activity_unit} "
                    f"for factor {factor.id}"
                )

        # Calculate per-gas emissions
        co2_kg = quantity * factor.co2_factor
        ch4_kg = quantity * factor.ch4_factor
        n2o_kg = quantity * factor.n2o_factor

        breakdown = self._build_gas_breakdown(co2_kg, ch4_kg, n2o_kg)
        total_co2e = self._total_co2e(breakdown)

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_1,
                scope1_category=Scope1Category.STATIONARY_COMBUSTION,
                total_co2e_kg=total_co2e,
                gas_breakdown=breakdown,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=activity.quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
            )
        ]
