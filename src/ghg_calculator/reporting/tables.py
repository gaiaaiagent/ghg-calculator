"""Summary tables for GHG emissions reports."""

import pandas as pd

from ..models.enums import Scope3Category
from ..models.results import InventoryResult


def scope_summary_table(inventory: InventoryResult) -> pd.DataFrame:
    """Table 1: Scope summary with totals."""
    rows = [
        {
            "Scope": "Scope 1 - Direct",
            "CO2e (tonnes)": inventory.scope1.total_co2e_tonnes,
            "% of Total": 0.0,
        },
        {
            "Scope": "Scope 2 - Indirect (Location)",
            "CO2e (tonnes)": inventory.scope2_location.total_co2e_tonnes,
            "% of Total": 0.0,
        },
        {
            "Scope": "Scope 2 - Indirect (Market)",
            "CO2e (tonnes)": inventory.scope2_market.total_co2e_tonnes,
            "% of Total": 0.0,
        },
        {
            "Scope": "Scope 3 - Value Chain",
            "CO2e (tonnes)": inventory.scope3.total_co2e_tonnes,
            "% of Total": 0.0,
        },
    ]

    total = inventory.total_co2e_tonnes
    if total > 0:
        for row in rows:
            row["% of Total"] = round(row["CO2e (tonnes)"] / total * 100, 1)

    rows.append({
        "Scope": "TOTAL (Location-based)",
        "CO2e (tonnes)": total,
        "% of Total": 100.0,
    })

    return pd.DataFrame(rows)


def scope3_breakdown_table(inventory: InventoryResult) -> pd.DataFrame:
    """Table 2: Scope 3 category breakdown."""
    by_cat: dict[int, float] = {}
    for r in inventory.scope3.results:
        cat_val = r.scope3_category.value if r.scope3_category else 0
        by_cat[cat_val] = by_cat.get(cat_val, 0) + r.total_co2e_tonnes

    rows = []
    total = inventory.scope3.total_co2e_tonnes
    for cat in Scope3Category:
        tonnes = by_cat.get(cat.value, 0.0)
        rows.append({
            "Category": f"{cat.value}. {cat.name.replace('_', ' ').title()}",
            "CO2e (tonnes)": round(tonnes, 2),
            "% of Scope 3": round(tonnes / total * 100, 1) if total > 0 else 0.0,
        })

    return pd.DataFrame(rows)


def gas_breakdown_table(inventory: InventoryResult) -> pd.DataFrame:
    """Table 3: Breakdown by greenhouse gas."""
    gas_totals: dict[str, float] = {}
    for r in inventory.all_results:
        for gb in r.gas_breakdown:
            gas_name = gb.gas.value.upper()
            gas_totals[gas_name] = gas_totals.get(gas_name, 0) + gb.co2e_kg

    rows = []
    total = sum(gas_totals.values())
    for gas, co2e_kg in sorted(gas_totals.items(), key=lambda x: -x[1]):
        rows.append({
            "Gas": gas,
            "CO2e (kg)": round(co2e_kg, 2),
            "CO2e (tonnes)": round(co2e_kg / 1000, 4),
            "% of Total": round(co2e_kg / total * 100, 1) if total > 0 else 0.0,
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Gas", "CO2e (kg)", "CO2e (tonnes)", "% of Total"])


def multi_year_trend_table(inventories: list[InventoryResult]) -> pd.DataFrame:
    """Table 4: Multi-year comparison."""
    rows = []
    for inv in inventories:
        rows.append({
            "Year": inv.year or "N/A",
            "Scope 1 (tonnes)": inv.scope1.total_co2e_tonnes,
            "Scope 2 Location (tonnes)": inv.scope2_location.total_co2e_tonnes,
            "Scope 3 (tonnes)": inv.scope3.total_co2e_tonnes,
            "Total (tonnes)": inv.total_co2e_tonnes,
        })
    return pd.DataFrame(rows)


def targets_table(
    inventory: InventoryResult,
    base_year_total: float,
    target_year: int,
    target_reduction_pct: float,
) -> pd.DataFrame:
    """Table 5: Progress toward reduction targets."""
    target_total = base_year_total * (1 - target_reduction_pct / 100)
    current_total = inventory.total_co2e_tonnes
    reduction_achieved = (1 - current_total / base_year_total) * 100 if base_year_total > 0 else 0

    return pd.DataFrame([
        {"Metric": "Base Year Total (tonnes)", "Value": round(base_year_total, 2)},
        {"Metric": f"Target ({target_reduction_pct}% reduction)", "Value": round(target_total, 2)},
        {"Metric": "Current Year Total (tonnes)", "Value": round(current_total, 2)},
        {"Metric": "Reduction Achieved (%)", "Value": round(reduction_achieved, 1)},
        {"Metric": "Target Year", "Value": target_year},
        {"Metric": "On Track", "Value": "Yes" if reduction_achieved >= target_reduction_pct else "No"},
    ])
