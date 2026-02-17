"""GRI 305 (Global Reporting Initiative) output format."""

from ...models.results import InventoryResult


def format_gri305(inventory: InventoryResult) -> dict:
    """Format inventory per GRI 305: Emissions disclosures."""
    gas_totals = _gas_totals(inventory)

    return {
        "standard": "GRI 305: Emissions (2016)",
        "305-1_direct_ghg": {
            "gross_tco2e": round(inventory.scope1.total_co2e_tonnes, 2),
            "gases_included": list(gas_totals.keys()),
            "biogenic_co2_tonnes": 0,  # Would need biomass tracking
        },
        "305-2_indirect_ghg": {
            "location_based_tco2e": round(inventory.scope2_location.total_co2e_tonnes, 2),
            "market_based_tco2e": round(inventory.scope2_market.total_co2e_tonnes, 2),
        },
        "305-3_other_indirect_ghg": {
            "total_tco2e": round(inventory.scope3.total_co2e_tonnes, 2),
        },
        "305-4_ghg_intensity": None,  # Requires denominator
        "305-5_reduction": None,  # Requires baseline
    }


def _gas_totals(inventory: InventoryResult) -> dict[str, float]:
    totals: dict[str, float] = {}
    for r in inventory.all_results:
        for gb in r.gas_breakdown:
            gas = gb.gas.value.upper()
            totals[gas] = totals.get(gas, 0) + gb.co2e_kg / 1000
    return {k: round(v, 2) for k, v in totals.items()}
