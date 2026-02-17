"""CDP (Carbon Disclosure Project) output format."""

from ...models.results import InventoryResult


def format_cdp(inventory: InventoryResult) -> dict:
    """Format inventory for CDP Climate Change questionnaire."""
    return {
        "framework": "CDP Climate Change",
        "C6.1_scope1": round(inventory.scope1.total_co2e_tonnes, 2),
        "C6.3_scope2_location": round(inventory.scope2_location.total_co2e_tonnes, 2),
        "C6.3_scope2_market": round(inventory.scope2_market.total_co2e_tonnes, 2),
        "C6.5_scope3": {
            "total": round(inventory.scope3.total_co2e_tonnes, 2),
            "categories": _scope3_cdp_categories(inventory),
        },
    }


def _scope3_cdp_categories(inventory: InventoryResult) -> list[dict]:
    by_cat: dict[int, float] = {}
    for r in inventory.scope3.results:
        cat = r.scope3_category.value if r.scope3_category else 0
        by_cat[cat] = by_cat.get(cat, 0) + r.total_co2e_tonnes

    return [
        {"category": k, "tco2e": round(v, 2)}
        for k, v in sorted(by_cat.items())
    ]
