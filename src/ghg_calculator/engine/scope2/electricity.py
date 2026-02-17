"""Scope 2 — Electricity calculator (location-based and market-based)."""

from ...models.activity import ActivityRecord
from ...models.enums import FactorSource, Scope, Scope2Method
from ...models.results import EmissionResult
from ...units.converter import converter
from ..base import BaseScopeCalculator


class ElectricityCalculator(BaseScopeCalculator):
    """Calculates Scope 2 emissions from purchased electricity.

    Always produces BOTH location-based and market-based results.
    - Location-based: uses grid average emission factors (eGRID/Ember)
    - Market-based: uses supplier-specific or residual mix factors
    """

    def calculate(self, activity: ActivityRecord) -> list[EmissionResult]:
        results = []

        # Convert to kWh if needed
        quantity_kwh = activity.quantity
        if activity.unit.lower() not in ("kwh", "kilowatt_hour"):
            try:
                quantity_kwh = converter.convert(activity.quantity, activity.unit, "kWh")
            except Exception:
                raise ValueError(f"Cannot convert {activity.unit} to kWh for electricity calculation")

        if activity.custom_factor is not None:
            # Custom factor — treat as single result
            total_co2e = quantity_kwh * activity.custom_factor
            method = activity.scope2_method or Scope2Method.LOCATION_BASED
            return [
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_2,
                    scope2_method=method,
                    total_co2e_kg=total_co2e,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                    notes=["Custom emission factor used"],
                )
            ]

        # Location-based calculation
        location_factor = self._find_location_factor(activity)
        if location_factor:
            co2_kg = quantity_kwh * location_factor.co2_factor
            ch4_kg = quantity_kwh * location_factor.ch4_factor
            n2o_kg = quantity_kwh * location_factor.n2o_factor
            breakdown = self._build_gas_breakdown(co2_kg, ch4_kg, n2o_kg)
            total_co2e = self._total_co2e(breakdown)

            results.append(
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_2,
                    scope2_method=Scope2Method.LOCATION_BASED,
                    total_co2e_kg=total_co2e,
                    gas_breakdown=breakdown,
                    factor_id=location_factor.id,
                    factor_source=location_factor.source.value,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                )
            )

        # Market-based calculation
        market_factor = self._find_market_factor(activity)
        if market_factor:
            co2_kg = quantity_kwh * market_factor.co2_factor
            ch4_kg = quantity_kwh * market_factor.ch4_factor
            n2o_kg = quantity_kwh * market_factor.n2o_factor
            breakdown = self._build_gas_breakdown(co2_kg, ch4_kg, n2o_kg)
            total_co2e = self._total_co2e(breakdown)

            results.append(
                EmissionResult(
                    activity_id=activity.id,
                    activity_name=activity.name,
                    scope=Scope.SCOPE_2,
                    scope2_method=Scope2Method.MARKET_BASED,
                    total_co2e_kg=total_co2e,
                    gas_breakdown=breakdown,
                    factor_id=market_factor.id,
                    factor_source=market_factor.source.value,
                    activity_quantity=activity.quantity,
                    activity_unit=activity.unit,
                    gwp_assessment=self.gwp_assessment,
                    notes=["Market-based: using grid average as proxy (no supplier-specific data)"],
                )
            )

        if not results:
            raise ValueError(
                f"No electricity emission factor found for region={activity.grid_subregion or activity.region or activity.country}. "
                f"Provide grid_subregion (eGRID code) or country, or use custom_factor."
            )

        return results

    def _find_location_factor(self, activity: ActivityRecord):
        """Find location-based emission factor (grid average)."""
        # Try eGRID subregion first
        if activity.grid_subregion:
            factor = self.registry.find_factor(
                category="electricity",
                region=activity.grid_subregion,
                activity_unit="kWh",
                source=FactorSource.EGRID,
            )
            if factor:
                return factor

        # Try country/region with Ember
        if activity.country:
            factor = self.registry.find_factor(
                category="electricity",
                region=activity.country,
                activity_unit="kWh",
                source=FactorSource.EMBER,
            )
            if factor:
                return factor

        # Fall back to US national average
        factor = self.registry.find_factor(
            category="electricity",
            region="US",
            activity_unit="kWh",
        )
        return factor

    def _find_market_factor(self, activity: ActivityRecord):
        """Find market-based emission factor.

        In practice, market-based should use supplier-specific data, RECs,
        or residual mix factors. For now, falls back to location-based.
        """
        # If user specified a specific source factor, use that
        if activity.factor_source:
            factor = self.registry.find_factor(
                category="electricity",
                region=activity.grid_subregion or activity.country,
                activity_unit="kWh",
                source=activity.factor_source,
            )
            if factor:
                return factor

        # Default: use same as location-based (conservative approach)
        return self._find_location_factor(activity)
