"""Scope 1 — Mobile Combustion calculator."""

from ...models.activity import ActivityRecord
from ...models.enums import Scope, Scope1Category
from ...models.results import EmissionResult
from ...units.converter import converter
from ..base import BaseScopeCalculator


class MobileCombustionCalculator(BaseScopeCalculator):
    """Calculates emissions from mobile combustion (company-owned vehicles)."""

    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        if activity.custom_factor is not None:
            total_co2e = activity.quantity * activity.custom_factor
            return [
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_1,
                    scope1_category=Scope1Category.MOBILE_COMBUSTION,
                    total_co2e_kg=total_co2e,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                    notes=["Custom emission factor used"],
                )
            ]

        fuel_type = activity.fuel_type.value if activity.fuel_type else activity.custom_fuel
        vehicle = activity.vehicle_type

        # Try to find factor by vehicle type + fuel, or just fuel
        factor = None
        if vehicle:
            factor = self.registry.find_factor(
                category="mobile_combustion",
                fuel_type=fuel_type,
                activity_unit=activity.unit,
                source=activity.factor_source,
            )
        if factor is None and fuel_type:
            factor = self.registry.find_factor(
                category="mobile_combustion",
                fuel_type=fuel_type,
                activity_unit=activity.unit,
                source=activity.factor_source,
            )

        if factor is None:
            raise ValueError(
                f"No emission factor found for mobile combustion: "
                f"fuel={fuel_type}, vehicle={vehicle}, unit={activity.unit}"
            )

        quantity = activity.quantity
        if activity.unit.lower() != factor.activity_unit.lower():
            try:
                quantity = converter.convert(activity.quantity, activity.unit, factor.activity_unit)
            except Exception:
                raise ValueError(
                    f"Cannot convert {activity.unit} to {factor.activity_unit}"
                )

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
                scope1_category=Scope1Category.MOBILE_COMBUSTION,
                total_co2e_kg=total_co2e,
                gas_breakdown=breakdown,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=activity.quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
            )
        ]
