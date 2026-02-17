"""FastMCP server exposing GHG calculator tools."""

from fastmcp import FastMCP

from ..engine.calculator import GHGCalculator
from ..factors.gwp import get_gwp, list_gases
from ..factors.registry import FactorRegistry
from ..models.activity import ActivityRecord
from ..models.enums import (
    FactorSource,
    FuelType,
    GWPAssessment,
    Scope,
    Scope1Category,
    Scope2Method,
    Scope3Category,
)
from ..units.converter import converter

mcp = FastMCP("GHG Emissions Calculator")

# Lazy-loaded globals
_registry: FactorRegistry | None = None
_calculator: GHGCalculator | None = None


def _get_registry() -> FactorRegistry:
    global _registry
    if _registry is None:
        _registry = FactorRegistry.load()
    return _registry


def _get_calculator() -> GHGCalculator:
    global _calculator
    if _calculator is None:
        _calculator = GHGCalculator(registry=_get_registry())
    return _calculator


@mcp.tool()
def calculate_emissions(activities: list[dict]) -> dict:
    """Calculate GHG emissions for multiple activity records.

    Returns a complete inventory with scope breakdowns.

    Args:
        activities: List of activity record dicts with fields:
            - scope: "scope_1", "scope_2", or "scope_3"
            - quantity: positive number
            - unit: unit string (e.g., "therm", "kWh", "gallon")
            - fuel_type: optional fuel type
            - scope1_category: optional for scope 1
            - grid_subregion: optional eGRID code for scope 2
            - scope3_category: optional int 1-15 for scope 3
            - custom_factor: optional override factor (kg CO2e/unit)
    """
    calc = _get_calculator()
    records = [ActivityRecord(**a) for a in activities]
    inventory = calc.calculate_inventory(records)
    return {
        "total_co2e_kg": inventory.total_co2e_kg,
        "total_co2e_tonnes": inventory.total_co2e_tonnes,
        "scope1_co2e_kg": inventory.scope1.total_co2e_kg,
        "scope2_location_co2e_kg": inventory.scope2_location.total_co2e_kg,
        "scope2_market_co2e_kg": inventory.scope2_market.total_co2e_kg,
        "scope3_co2e_kg": inventory.scope3.total_co2e_kg,
        "result_count": len(inventory.all_results),
        "results": [
            {
                "scope": r.scope.value,
                "total_co2e_kg": r.total_co2e_kg,
                "total_co2e_tonnes": r.total_co2e_tonnes,
                "factor_id": r.factor_id,
                "notes": r.notes,
            }
            for r in inventory.all_results
        ],
    }


@mcp.tool()
def calculate_single(
    scope: str,
    quantity: float,
    unit: str,
    category: str | None = None,
    fuel_type: str | None = None,
    region: str | None = None,
    custom_factor: float | None = None,
    refrigerant_type: str | None = None,
) -> dict:
    """Calculate GHG emissions for a single activity.

    Args:
        scope: "scope_1", "scope_2", or "scope_3"
        quantity: Activity quantity (must be > 0)
        unit: Unit of quantity (e.g., "therm", "kWh", "gallon", "mile")
        category: Scope category (e.g., "stationary_combustion", or "1"-"15" for scope 3)
        fuel_type: Fuel type (e.g., "natural_gas", "diesel", "gasoline")
        region: Grid subregion (eGRID code) or country code
        custom_factor: Optional emission factor override (kg CO2e per unit)
        refrigerant_type: Refrigerant type for fugitive emissions

    Returns:
        Dict with total_co2e_kg, gas_breakdown, factor_id, notes
    """
    scope_enum = Scope(scope)
    scope1_cat = None
    scope3_cat = None
    ft = None

    if scope_enum == Scope.SCOPE_1 and category:
        try:
            scope1_cat = Scope1Category(category)
        except ValueError:
            pass

    if scope_enum == Scope.SCOPE_3 and category:
        try:
            scope3_cat = Scope3Category(int(category))
        except (ValueError, KeyError):
            pass

    if fuel_type:
        try:
            ft = FuelType(fuel_type)
        except ValueError:
            pass

    activity = ActivityRecord(
        scope=scope_enum,
        scope1_category=scope1_cat,
        scope3_category=scope3_cat,
        quantity=quantity,
        unit=unit,
        fuel_type=ft,
        custom_fuel=fuel_type if ft is None else None,
        grid_subregion=region if scope_enum == Scope.SCOPE_2 else None,
        country=region if scope_enum != Scope.SCOPE_2 else None,
        custom_factor=custom_factor,
        refrigerant_type=refrigerant_type,
    )

    calc = _get_calculator()
    results = calc.calculate_single(activity)

    return {
        "results": [
            {
                "scope": r.scope.value,
                "scope2_method": r.scope2_method.value if r.scope2_method else None,
                "total_co2e_kg": r.total_co2e_kg,
                "total_co2e_tonnes": r.total_co2e_tonnes,
                "gas_breakdown": [
                    {
                        "gas": g.gas.value,
                        "mass_kg": g.mass_kg,
                        "co2e_kg": g.co2e_kg,
                        "gwp_used": g.gwp_used,
                    }
                    for g in r.gas_breakdown
                ],
                "factor_id": r.factor_id,
                "notes": r.notes,
            }
            for r in results
        ]
    }


@mcp.tool()
def get_emission_factors(
    query: str = "",
    source: str | None = None,
    category: str | None = None,
    fuel_type: str | None = None,
    limit: int = 20,
) -> dict:
    """Search the emission factor database.

    Args:
        query: Free-text search (searches name, description, tags)
        source: Filter by source: epa_hub, egrid, defra, useeio, ember, exiobase
        category: Filter by category (e.g., "stationary_combustion", "electricity")
        fuel_type: Filter by fuel type
        limit: Maximum results (default 20)

    Returns:
        Dict with matching factors and their details
    """
    registry = _get_registry()
    source_enum = FactorSource(source) if source else None
    results = registry.search(
        query=query,
        source=source_enum,
        category=category,
        fuel_type=fuel_type,
        limit=limit,
    )
    return {
        "count": len(results),
        "total_in_registry": registry.factor_count,
        "factors": [
            {
                "id": f.id,
                "name": f.name,
                "source": f.source.value,
                "co2_factor": f.co2_factor,
                "ch4_factor": f.ch4_factor,
                "n2o_factor": f.n2o_factor,
                "co2e_factor": f.co2e_factor,
                "activity_unit": f.activity_unit,
                "category": f.category,
                "fuel_type": f.fuel_type,
                "region": f.region,
            }
            for f in results
        ],
    }


@mcp.tool()
def list_scopes() -> dict:
    """List all available emission scopes and their categories.

    Returns complete taxonomy of scopes, categories, and descriptions.
    """
    return {
        "scopes": {
            "scope_1": {
                "name": "Direct Emissions",
                "categories": {c.value: c.name for c in Scope1Category},
            },
            "scope_2": {
                "name": "Indirect Emissions from Purchased Energy",
                "methods": {m.value: m.name for m in Scope2Method},
            },
            "scope_3": {
                "name": "Other Indirect Emissions",
                "categories": {str(c.value): c.name for c in Scope3Category},
            },
        }
    }


@mcp.tool()
def list_factor_sources() -> dict:
    """List all available emission factor databases with metadata."""
    registry = _get_registry()
    return {
        "sources": [
            {
                "source": v.source.value,
                "version": v.version,
                "year": v.year,
                "description": v.description,
                "factor_count": v.factor_count,
                "url": v.url,
            }
            for v in registry.versions
        ],
        "total_factors": registry.factor_count,
    }


@mcp.tool()
def get_gwp_values(
    gas: str | None = None,
    assessment: str = "ar5",
) -> dict:
    """Get Global Warming Potential (GWP) values.

    Args:
        gas: Specific gas (e.g., "ch4", "hfc-134a", "r-410a"). If None, returns all.
        assessment: IPCC assessment report: "ar5" (default) or "ar6"

    Returns:
        GWP values for the specified gas(es)
    """
    gwp_assessment = GWPAssessment(assessment.lower())

    if gas:
        try:
            value = get_gwp(gas, gwp_assessment)
            return {"gas": gas, "gwp": value, "assessment": gwp_assessment.value}
        except KeyError as e:
            return {"error": str(e)}

    gases = list_gases(gwp_assessment)
    return {
        "assessment": gwp_assessment.value,
        "gases": {g: get_gwp(g, gwp_assessment) for g in gases},
    }


@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert between units commonly used in GHG calculations.

    Supports energy (kWh, BTU, therm, MMBtu), mass (kg, lb, short_ton),
    volume (gallon, liter), and more.

    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., "therm", "gallon", "kWh")
        to_unit: Target unit

    Returns:
        Dict with converted value
    """
    try:
        result = converter.convert(value, from_unit, to_unit)
        return {
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def generate_report(activities: list[dict], title: str = "GHG Emissions Report") -> dict:
    """Generate a summary report from activity records.

    Args:
        activities: List of activity record dicts
        title: Report title

    Returns:
        Dict with inventory summary, scope breakdowns, and key metrics
    """
    calc = _get_calculator()
    records = [ActivityRecord(**a) for a in activities]
    inventory = calc.calculate_inventory(records, name=title)

    # Build scope 3 category breakdown
    scope3_by_cat: dict[str, float] = {}
    for r in inventory.scope3.results:
        cat_name = r.scope3_category.name if r.scope3_category else "Unknown"
        scope3_by_cat[cat_name] = scope3_by_cat.get(cat_name, 0) + r.total_co2e_kg

    return {
        "title": title,
        "summary": {
            "total_co2e_tonnes": inventory.total_co2e_tonnes,
            "scope1_co2e_tonnes": inventory.scope1.total_co2e_tonnes,
            "scope2_location_co2e_tonnes": inventory.scope2_location.total_co2e_tonnes,
            "scope2_market_co2e_tonnes": inventory.scope2_market.total_co2e_tonnes,
            "scope3_co2e_tonnes": inventory.scope3.total_co2e_tonnes,
        },
        "scope3_breakdown": {k: v / 1000 for k, v in scope3_by_cat.items()},
        "activity_count": len(records),
        "result_count": len(inventory.all_results),
    }


def main():
    """Entry point for ghg-mcp command."""
    mcp.run()


if __name__ == "__main__":
    main()
