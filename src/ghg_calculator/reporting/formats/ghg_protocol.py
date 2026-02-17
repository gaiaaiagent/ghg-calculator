"""GHG Protocol Corporate Standard output format."""

from ...models.results import InventoryResult


def format_ghg_protocol(inventory: InventoryResult) -> dict:
    """Format inventory results per GHG Protocol Corporate Standard."""
    return {
        "standard": "GHG Protocol Corporate Accounting and Reporting Standard",
        "reporting_year": inventory.year,
        "organizational_boundary": "Operational control",
        "scope_1": {
            "total_tco2e": round(inventory.scope1.total_co2e_tonnes, 2),
            "categories": _group_scope1(inventory),
        },
        "scope_2": {
            "location_based_tco2e": round(inventory.scope2_location.total_co2e_tonnes, 2),
            "market_based_tco2e": round(inventory.scope2_market.total_co2e_tonnes, 2),
        },
        "scope_3": {
            "total_tco2e": round(inventory.scope3.total_co2e_tonnes, 2),
            "categories": _group_scope3(inventory),
        },
        "total_tco2e_location": round(inventory.total_co2e_tonnes, 2),
    }


def _group_scope1(inventory: InventoryResult) -> dict:
    groups: dict[str, float] = {}
    for r in inventory.scope1.results:
        cat = r.scope1_category.name if r.scope1_category else "unspecified"
        groups[cat] = groups.get(cat, 0) + r.total_co2e_tonnes
    return {k: round(v, 2) for k, v in groups.items()}


def _group_scope3(inventory: InventoryResult) -> dict:
    groups: dict[str, float] = {}
    for r in inventory.scope3.results:
        if r.scope3_category:
            cat = f"{r.scope3_category.value}_{r.scope3_category.name}"
        else:
            cat = "unspecified"
        groups[cat] = groups.get(cat, 0) + r.total_co2e_tonnes
    return {k: round(v, 2) for k, v in groups.items()}
