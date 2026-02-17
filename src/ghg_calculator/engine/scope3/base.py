"""Scope 3 — Base calculator supporting all 15 categories."""

from ...models.activity import ActivityRecord
from ...models.enums import FactorSource, Scope, Scope3Category
from ...models.results import EmissionResult
from ...units.converter import converter
from ..base import BaseScopeCalculator


class Scope3Calculator(BaseScopeCalculator):
    """Calculates Scope 3 emissions across all 15 categories.

    Supports multiple calculation methods:
    - Spend-based: uses economic input-output factors (USEEIO/EXIOBASE)
    - Activity-based: uses physical activity factors (DEFRA/EPA)
    - Distance-based: for transport categories
    - Custom factors: user-provided emission factors
    """

    # Mapping of scope3 categories to typical factor categories in the registry
    _CATEGORY_MAP: dict[Scope3Category, str] = {
        Scope3Category.PURCHASED_GOODS_SERVICES: "purchased_goods",
        Scope3Category.CAPITAL_GOODS: "capital_goods",
        Scope3Category.FUEL_ENERGY_ACTIVITIES: "fuel_energy",
        Scope3Category.UPSTREAM_TRANSPORT: "transport",
        Scope3Category.WASTE: "waste",
        Scope3Category.BUSINESS_TRAVEL: "business_travel",
        Scope3Category.EMPLOYEE_COMMUTING: "commuting",
        Scope3Category.UPSTREAM_LEASED_ASSETS: "leased_assets",
        Scope3Category.DOWNSTREAM_TRANSPORT: "transport",
        Scope3Category.PROCESSING_SOLD_PRODUCTS: "processing",
        Scope3Category.USE_OF_SOLD_PRODUCTS: "product_use",
        Scope3Category.END_OF_LIFE_SOLD_PRODUCTS: "end_of_life",
        Scope3Category.DOWNSTREAM_LEASED_ASSETS: "leased_assets",
        Scope3Category.FRANCHISES: "franchises",
        Scope3Category.INVESTMENTS: "investments",
    }

    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        if activity.custom_factor is not None:
            return self._calculate_custom(activity)

        category = activity.scope3_category
        if category is None:
            raise ValueError("scope3_category is required for Scope 3 calculations")

        # Spend-based approach
        if activity.spend_amount is not None:
            return self._calculate_spend_based(activity)

        # Distance-based approach (transport, travel, commuting)
        if activity.distance is not None and category in (
            Scope3Category.UPSTREAM_TRANSPORT,
            Scope3Category.DOWNSTREAM_TRANSPORT,
            Scope3Category.BUSINESS_TRAVEL,
            Scope3Category.EMPLOYEE_COMMUTING,
        ):
            return self._calculate_distance_based(activity)

        # Waste-specific
        if category == Scope3Category.WASTE:
            return self._calculate_waste(activity)

        # Activity-based (generic)
        return self._calculate_activity_based(activity)

    def _calculate_custom(self, activity: ActivityRecord) -> list[EmissionResult]:
        total_co2e = activity.quantity * activity.custom_factor
        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_3,
                scope3_category=activity.scope3_category,
                total_co2e_kg=total_co2e,
                activity_quantity=activity.quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
                notes=["Custom emission factor used"],
            )
        ]

    def _calculate_spend_based(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Use economic input-output factors (kg CO2e per dollar spent)."""
        # Search for USEEIO or EXIOBASE factor by NAICS code
        factor = None
        if activity.naics_code:
            factor = self.registry.find_factor(
                category="spend_based",
                fuel_type=activity.naics_code,
                source=FactorSource.USEEIO,
            )
            if factor is None:
                # Try searching by NAICS code in tags
                results = self.registry.search(
                    query=activity.naics_code,
                    source=FactorSource.USEEIO,
                    limit=1,
                )
                if results:
                    factor = results[0]

        if factor is None:
            # Try EXIOBASE
            results = self.registry.search(
                query=activity.naics_code or "",
                source=FactorSource.EXIOBASE,
                limit=1,
            )
            if results:
                factor = results[0]

        if factor is None:
            raise ValueError(
                f"No spend-based emission factor found for NAICS={activity.naics_code}. "
                f"Provide a custom_factor (kg CO2e per USD)."
            )

        spend = activity.spend_amount or activity.quantity
        co2e_factor = factor.co2e_factor if factor.co2e_factor is not None else factor.co2_factor
        total_co2e = spend * co2e_factor

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_3,
                scope3_category=activity.scope3_category,
                total_co2e_kg=total_co2e,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=spend,
                activity_unit="USD",
                gwp_assessment=self.gwp_assessment,
                notes=[f"Spend-based: {co2e_factor:.4f} kg CO2e/USD"],
            )
        ]

    def _calculate_distance_based(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Calculate transport/travel emissions from distance."""
        mode = activity.transport_mode or activity.vehicle_type or "average"

        # Search for factor by transport mode
        cat_name = self._CATEGORY_MAP.get(activity.scope3_category, "transport")
        factor = self.registry.find_factor(
            category=cat_name,
            fuel_type=mode,
            activity_unit=activity.distance_unit or "km",
        )

        if factor is None:
            # Broader search
            results = self.registry.search(
                query=f"{cat_name} {mode}",
                limit=1,
            )
            if results:
                factor = results[0]

        if factor is None:
            raise ValueError(
                f"No distance-based factor found for {cat_name}, mode={mode}. "
                f"Provide a custom_factor."
            )

        distance = activity.distance
        if activity.distance_unit and activity.distance_unit.lower() != factor.activity_unit.lower():
            try:
                distance = converter.convert(distance, activity.distance_unit, factor.activity_unit)
            except Exception:
                pass  # Use as-is

        # Weight-distance if applicable (tonne-km)
        if activity.weight and "tonne_km" in factor.activity_unit.lower():
            weight_tonnes = activity.weight
            if activity.weight_unit and activity.weight_unit.lower() != "tonne":
                try:
                    weight_tonnes = converter.convert(activity.weight, activity.weight_unit, "metric_ton")
                except Exception:
                    pass
            quantity = distance * weight_tonnes
        else:
            quantity = distance

        co2e_factor = factor.co2e_factor if factor.co2e_factor is not None else factor.co2_factor
        total_co2e = quantity * co2e_factor

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_3,
                scope3_category=activity.scope3_category,
                total_co2e_kg=total_co2e,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=quantity,
                activity_unit=factor.activity_unit,
                gwp_assessment=self.gwp_assessment,
                notes=[f"Distance-based: mode={mode}"],
            )
        ]

    def _calculate_waste(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Calculate waste disposal emissions."""
        waste_type = activity.waste_type or "mixed"
        disposal = activity.disposal_method or "landfill"

        factor = self.registry.find_factor(
            category="waste",
            fuel_type=f"{waste_type}_{disposal}",
        )

        if factor is None:
            results = self.registry.search(
                query=f"waste {waste_type} {disposal}",
                limit=1,
            )
            if results:
                factor = results[0]

        if factor is None:
            raise ValueError(
                f"No waste emission factor found for type={waste_type}, "
                f"disposal={disposal}. Provide a custom_factor."
            )

        quantity = activity.quantity
        co2e_factor = factor.co2e_factor if factor.co2e_factor is not None else factor.co2_factor
        total_co2e = quantity * co2e_factor

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_3,
                scope3_category=Scope3Category.WASTE,
                total_co2e_kg=total_co2e,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
                notes=[f"Waste: {waste_type}/{disposal}"],
            )
        ]

    def _calculate_activity_based(self, activity: ActivityRecord) -> list[EmissionResult]:
        """Generic activity-based calculation for any Scope 3 category."""
        cat = activity.scope3_category
        cat_name = self._CATEGORY_MAP.get(cat, "")

        factor = self.registry.find_factor(
            category=cat_name,
            activity_unit=activity.unit,
            source=activity.factor_source,
        )

        if factor is None:
            results = self.registry.search(
                query=cat_name,
                activity_unit=activity.unit,
                limit=1,
            )
            if results:
                factor = results[0]

        if factor is None:
            raise ValueError(
                f"No emission factor found for Scope 3 category {cat.value} ({cat.name}). "
                f"Provide a custom_factor (kg CO2e per {activity.unit})."
            )

        co2_kg = activity.quantity * factor.co2_factor
        ch4_kg = activity.quantity * factor.ch4_factor
        n2o_kg = activity.quantity * factor.n2o_factor

        breakdown = self._build_gas_breakdown(co2_kg, ch4_kg, n2o_kg)
        total_co2e = self._total_co2e(breakdown)

        # Use co2e_factor if provided
        if factor.co2e_factor is not None:
            total_co2e = activity.quantity * factor.co2e_factor

        return [
            EmissionResult(
                activity_id=activity.id,
                activity_name=activity.name,
                scope=Scope.SCOPE_3,
                scope3_category=cat,
                total_co2e_kg=total_co2e,
                gas_breakdown=breakdown,
                factor_id=factor.id,
                factor_source=factor.source.value,
                activity_quantity=activity.quantity,
                activity_unit=activity.unit,
                gwp_assessment=self.gwp_assessment,
            )
        ]
