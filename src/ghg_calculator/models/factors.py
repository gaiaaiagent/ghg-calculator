"""Emission factor models."""

from pydantic import BaseModel, Field

from .enums import FactorSource, GasType, Scope


class EmissionFactor(BaseModel):
    """A single emission factor from a database source."""

    id: str
    name: str
    source: FactorSource
    scope: Scope | None = None

    # Factor values per gas (kg per unit of activity)
    co2_factor: float = 0.0  # kg CO2 per unit
    ch4_factor: float = 0.0  # kg CH4 per unit
    n2o_factor: float = 0.0  # kg N2O per unit
    co2e_factor: float | None = None  # Pre-calculated kg CO2e per unit (if provided)

    # Other gases (HFCs, PFCs, etc.)
    other_factors: dict[GasType, float] = Field(default_factory=dict)

    # Unit info
    activity_unit: str = Field(description="Unit of the activity data (e.g., 'gallon', 'kWh')")
    factor_unit: str = "kg"  # Unit of the factor output (always kg)

    # Metadata
    category: str = ""
    subcategory: str = ""
    fuel_type: str | None = None
    region: str | None = None
    year: int | None = None
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class FactorVersion(BaseModel):
    """Version metadata for a factor database file."""

    source: FactorSource
    version: str
    year: int
    description: str = ""
    url: str = ""
    factor_count: int = 0
    factors: list[EmissionFactor] = Field(default_factory=list)
