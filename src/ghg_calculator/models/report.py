"""Report configuration models."""

from enum import Enum

from pydantic import BaseModel, Field


class ReportFormat(str, Enum):
    """Output report format standards."""

    GHG_PROTOCOL = "ghg_protocol"
    CDP = "cdp"
    GRI_305 = "gri_305"


class ChartType(str, Enum):
    """Available chart types for reports."""

    SCOPE_DONUT = "scope_donut"
    CATEGORY_BAR = "category_bar"
    WATERFALL = "waterfall"
    TREEMAP = "treemap"
    TREND_LINE = "trend_line"
    INTENSITY = "intensity"


class ChartSpec(BaseModel):
    """Specification for a single chart in a report."""

    chart_type: ChartType
    title: str = ""
    width: int = 800
    height: int = 500
    show_legend: bool = True


class ReportConfig(BaseModel):
    """Configuration for report generation."""

    title: str = "GHG Emissions Report"
    format: ReportFormat = ReportFormat.GHG_PROTOCOL
    charts: list[ChartSpec] = Field(default_factory=list)
    include_methodology: bool = True
    include_data_quality: bool = True
    include_scope3_breakdown: bool = True
    output_html: bool = True
    output_json: bool = False
    base_year: int | None = None
    target_year: int | None = None
    target_reduction_pct: float | None = None
