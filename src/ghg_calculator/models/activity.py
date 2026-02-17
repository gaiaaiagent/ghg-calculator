"""Activity record model — universal input for all emission calculations."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from .enums import (
    DataQualityScore,
    FactorSource,
    FuelType,
    GasType,
    Scope,
    Scope1Category,
    Scope2Method,
    Scope3Category,
)


class ActivityRecord(BaseModel):
    """Universal input record for emission calculations.

    Represents a single activity that generates GHG emissions.
    The required fields vary by scope and category.
    """

    # Identifiers
    id: str | None = None
    name: str | None = None
    description: str | None = None

    # Scope classification
    scope: Scope
    scope1_category: Scope1Category | None = None
    scope2_method: Scope2Method | None = None
    scope3_category: Scope3Category | None = None

    # Activity data
    quantity: float = Field(gt=0, description="Activity quantity (e.g., gallons, kWh, miles)")
    unit: str = Field(description="Unit of the quantity (e.g., 'therm', 'kWh', 'gallon')")

    # Fuel/source specification
    fuel_type: FuelType | None = None
    custom_fuel: str | None = None

    # Location (for grid electricity, regional factors)
    country: str | None = None
    region: str | None = None
    grid_subregion: str | None = None

    # Custom emission factor override
    custom_factor: float | None = Field(
        None, description="Custom emission factor (kg CO2e per unit)"
    )
    custom_factor_unit: str | None = None
    custom_factor_gas: GasType | None = None

    # Factor source preference
    factor_source: FactorSource | None = None

    # Time period
    start_date: date | None = None
    end_date: date | None = None
    year: int | None = None

    # Data quality
    data_quality: DataQualityScore | None = None

    # Spend-based data (Scope 3)
    spend_amount: float | None = Field(None, gt=0)
    spend_currency: str = "USD"
    naics_code: str | None = None

    # Transport data
    distance: float | None = Field(None, gt=0)
    distance_unit: str | None = None
    weight: float | None = Field(None, gt=0)
    weight_unit: str | None = None
    vehicle_type: str | None = None
    transport_mode: str | None = None

    # Waste data
    waste_type: str | None = None
    disposal_method: str | None = None

    # Refrigerant data
    refrigerant_type: str | None = None

    # Metadata
    tags: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
