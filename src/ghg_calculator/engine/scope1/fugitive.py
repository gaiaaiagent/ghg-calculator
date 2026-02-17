"""Scope 1 — Fugitive Emissions calculator (refrigerants, SF6, etc.)."""

from ...factors.gwp import get_gwp
from ...models.activity import ActivityRecord
from ...models.enums import GasType, Scope, Scope1Category
from ...models.results import EmissionResult, GasBreakdown
from ...units.converter import converter
from ..base import BaseScopeCalculator


class FugitiveEmissionsCalculator(BaseScopeCalculator):
    """Calculates emissions from refrigerant leaks, SF6, and other fugitive sources.

    For refrigerants: CO2e = quantity leaked (kg) × GWP of refrigerant
    """

    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        if activity.custom_factor is not None:
            total_co2e = activity.quantity * activity.custom_factor
            return [
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_1,
                    scope1_category=Scope1Category.FUGITIVE_EMISSIONS,
                    total_co2e_kg=total_co2e,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                    notes=["Custom emission factor used"],
                )
            ]

        refrigerant = activity.refrigerant_type
        if refrigerant is None:
            # Try to find by searching the factor registry
            factor = self.registry.find_factor(
                category="fugitive_emissions",
                activity_unit=activity.unit,
                source=activity.factor_source,
            )
            if factor and factor.co2e_factor is not None:
                quantity_kg = activity.quantity
                if activity.unit.lower() != "kg":
                    try:
                        quantity_kg = converter.convert(activity.quantity, activity.unit, "kg")
                    except Exception:
                        raise ValueError(f"Cannot convert {activity.unit} to kg for fugitive emissions")
                total_co2e = quantity_kg * factor.co2e_factor
                return [
                    EmissionResult(
                        activity_id=activity.id,
                        activity_name=activity.name,
                        scope=Scope.SCOPE_1,
                        scope1_category=Scope1Category.FUGITIVE_EMISSIONS,
                        total_co2e_kg=total_co2e,
                        factor_id=factor.id,
                        factor_source=factor.source.value,
                        activity_quantity=activity.quantity,
                        activity_unit=activity.unit,
                        gwp_assessment=self.gwp_assessment,
                    )
                ]
            raise ValueError("No refrigerant_type specified and no matching factor found")

        # Convert quantity to kg if needed
        quantity_kg = activity.quantity
        if activity.unit.lower() != "kg":
            try:
                quantity_kg = converter.convert(activity.quantity, activity.unit, "kg")
            except Exception:
                raise ValueError(f"Cannot convert {activity.unit} to kg for refrigerant calculation")

        # Look up GWP for the refrigerant
        refrigerant_lower = refrigerant.lower()
        try:
            gwp = get_gwp(refrigerant_lower, self.gwp_assessment)
        except KeyError:
            # Try searching the factor registry for a co2e_factor
            results = self.registry.search(
                query=refrigerant,
                category="fugitive_emissions",
                limit=1,
            )
            if results and results[0].co2e_factor is not None:
                gwp = results[0].co2e_factor
            else:
                raise ValueError(
                    f"Unknown refrigerant: {refrigerant}. "
                    f"Provide a custom_factor or use a known refrigerant type."
                )

        total_co2e = quantity_kg * gwp

        breakdown = [
            GasBreakdown(
                gas=GasType.HFC,
                mass_kg=quantity_kg,
                co2e_kg=total_co2e,
                gwp_used=gwp,
                gwp_assessment=self.gwp_assessment,
            )
        ]

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_1,
                scope1_category=Scope1Category.FUGITIVE_EMISSIONS,
                total_co2e_kg=total_co2e,
                gas_breakdown=breakdown,
                activity_quantity=activity.quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
                notes=[f"Refrigerant: {refrigerant}, GWP: {gwp}"],
            )
        ]
