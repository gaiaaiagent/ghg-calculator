"""Plotly chart generators for GHG emissions reports."""

import plotly.graph_objects as go

from ..models.enums import Scope3Category
from ..models.results import InventoryResult


def scope_donut_chart(inventory: InventoryResult) -> go.Figure:
    """Donut chart showing emission distribution by scope."""
    labels = ["Scope 1", "Scope 2 (Location)", "Scope 3"]
    values = [
        inventory.scope1.total_co2e_tonnes,
        inventory.scope2_location.total_co2e_tonnes,
        inventory.scope3.total_co2e_tonnes,
    ]
    colors = ["#2196F3", "#4CAF50", "#FF9800"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo="label+percent",
        textposition="outside",
    )])
    fig.update_layout(
        title="GHG Emissions by Scope",
        annotations=[dict(text=f"{sum(values):,.0f}<br>tCO2e", x=0.5, y=0.5, font_size=16, showarrow=False)],
    )
    return fig


def category_stacked_bar(inventory: InventoryResult) -> go.Figure:
    """Stacked bar chart of Scope 1 categories + Scope 2 + Scope 3."""
    categories = []
    values = []

    # Scope 1 by category
    s1_cats: dict[str, float] = {}
    for r in inventory.scope1.results:
        cat = r.scope1_category.name if r.scope1_category else "Other"
        s1_cats[cat] = s1_cats.get(cat, 0) + r.total_co2e_tonnes
    for cat, val in s1_cats.items():
        categories.append(f"S1: {cat}")
        values.append(val)

    categories.append("Scope 2 (Location)")
    values.append(inventory.scope2_location.total_co2e_tonnes)

    categories.append("Scope 3")
    values.append(inventory.scope3.total_co2e_tonnes)

    fig = go.Figure(data=[go.Bar(x=categories, y=values, marker_color="#2196F3")])
    fig.update_layout(
        title="Emissions by Category",
        yaxis_title="tCO2e",
        xaxis_tickangle=-45,
    )
    return fig


def waterfall_chart(inventory: InventoryResult) -> go.Figure:
    """Waterfall chart showing buildup from Scope 1 through Scope 3."""
    fig = go.Figure(go.Waterfall(
        x=["Scope 1", "Scope 2 (Location)", "Scope 3", "Total"],
        y=[
            inventory.scope1.total_co2e_tonnes,
            inventory.scope2_location.total_co2e_tonnes,
            inventory.scope3.total_co2e_tonnes,
            0,
        ],
        measure=["relative", "relative", "relative", "total"],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig.update_layout(title="Emission Buildup by Scope", yaxis_title="tCO2e")
    return fig


def scope3_treemap(inventory: InventoryResult) -> go.Figure:
    """Treemap of Scope 3 categories."""
    labels = []
    values = []
    parents = []

    by_cat: dict[int, float] = {}
    for r in inventory.scope3.results:
        cat_val = r.scope3_category.value if r.scope3_category else 0
        by_cat[cat_val] = by_cat.get(cat_val, 0) + r.total_co2e_tonnes

    labels.append("Scope 3")
    values.append(0)
    parents.append("")

    for cat in Scope3Category:
        tonnes = by_cat.get(cat.value, 0)
        if tonnes > 0:
            name = f"{cat.value}. {cat.name.replace('_', ' ').title()}"
            labels.append(name)
            values.append(tonnes)
            parents.append("Scope 3")

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
    ))
    fig.update_layout(title="Scope 3 Category Breakdown")
    return fig


def trend_line_chart(inventories: list[InventoryResult], target_year: int | None = None, target_value: float | None = None) -> go.Figure:
    """Line chart showing multi-year trend with optional target."""
    years = [inv.year or i for i, inv in enumerate(inventories)]
    totals = [inv.total_co2e_tonnes for inv in inventories]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=totals, mode="lines+markers", name="Actual"))

    if target_year and target_value:
        fig.add_trace(go.Scatter(
            x=[years[0], target_year],
            y=[totals[0], target_value],
            mode="lines",
            name="Target Path",
            line=dict(dash="dash", color="red"),
        ))

    fig.update_layout(title="Emissions Trend", xaxis_title="Year", yaxis_title="tCO2e")
    return fig


def intensity_chart(inventories: list[InventoryResult], denominators: list[float], denominator_label: str = "Revenue ($M)") -> go.Figure:
    """Emission intensity chart (tCO2e per unit of business metric)."""
    years = [inv.year or i for i, inv in enumerate(inventories)]
    intensities = [
        inv.total_co2e_tonnes / d if d > 0 else 0
        for inv, d in zip(inventories, denominators)
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=[inv.total_co2e_tonnes for inv in inventories], name="Absolute (tCO2e)", yaxis="y"))
    fig.add_trace(go.Scatter(x=years, y=intensities, mode="lines+markers", name=f"Intensity (tCO2e/{denominator_label})", yaxis="y2"))

    fig.update_layout(
        title="Absolute vs Intensity Emissions",
        yaxis=dict(title="tCO2e"),
        yaxis2=dict(title=f"tCO2e per {denominator_label}", overlaying="y", side="right"),
    )
    return fig
