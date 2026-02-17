"""Core enumerations for GHG emissions calculations."""

from enum import Enum


class Scope(str, Enum):
    """GHG Protocol emission scopes."""

    SCOPE_1 = "scope_1"
    SCOPE_2 = "scope_2"
    SCOPE_3 = "scope_3"


class Scope1Category(str, Enum):
    """Scope 1 emission categories."""

    STATIONARY_COMBUSTION = "stationary_combustion"
    MOBILE_COMBUSTION = "mobile_combustion"
    FUGITIVE_EMISSIONS = "fugitive_emissions"
    PROCESS_EMISSIONS = "process_emissions"


class Scope2Method(str, Enum):
    """Scope 2 calculation methods."""

    LOCATION_BASED = "location_based"
    MARKET_BASED = "market_based"


class Scope3Category(int, Enum):
    """Scope 3 categories (1-15) per GHG Protocol."""

    PURCHASED_GOODS_SERVICES = 1
    CAPITAL_GOODS = 2
    FUEL_ENERGY_ACTIVITIES = 3
    UPSTREAM_TRANSPORT = 4
    WASTE = 5
    BUSINESS_TRAVEL = 6
    EMPLOYEE_COMMUTING = 7
    UPSTREAM_LEASED_ASSETS = 8
    DOWNSTREAM_TRANSPORT = 9
    PROCESSING_SOLD_PRODUCTS = 10
    USE_OF_SOLD_PRODUCTS = 11
    END_OF_LIFE_SOLD_PRODUCTS = 12
    DOWNSTREAM_LEASED_ASSETS = 13
    FRANCHISES = 14
    INVESTMENTS = 15


class GasType(str, Enum):
    """Greenhouse gas types."""

    CO2 = "co2"
    CH4 = "ch4"
    N2O = "n2o"
    HFC = "hfc"
    PFC = "pfc"
    SF6 = "sf6"
    NF3 = "nf3"
    CO2E = "co2e"  # Pre-calculated CO2-equivalent


class GWPAssessment(str, Enum):
    """IPCC Assessment Report versions for GWP values."""

    AR5 = "ar5"
    AR6 = "ar6"


class DataQualityScore(int, Enum):
    """Data quality indicator score (1=best, 5=worst) per GHG Protocol Ch.7."""

    VERY_GOOD = 1
    GOOD = 2
    FAIR = 3
    POOR = 4
    VERY_POOR = 5


class FactorSource(str, Enum):
    """Emission factor database sources."""

    EPA_HUB = "epa_hub"
    EGRID = "egrid"
    DEFRA = "defra"
    USEEIO = "useeio"
    EMBER = "ember"
    EXIOBASE = "exiobase"
    CUSTOM = "custom"


class FuelType(str, Enum):
    """Common fuel types for combustion calculations."""

    NATURAL_GAS = "natural_gas"
    DIESEL = "diesel"
    GASOLINE = "gasoline"
    PROPANE = "propane"
    FUEL_OIL_NO2 = "fuel_oil_no2"
    FUEL_OIL_NO6 = "fuel_oil_no6"
    KEROSENE = "kerosene"
    LPG = "lpg"
    COAL_BITUMINOUS = "coal_bituminous"
    COAL_ANTHRACITE = "coal_anthracite"
    COAL_SUBBITUMINOUS = "coal_subbituminous"
    WOOD = "wood"
    LANDFILL_GAS = "landfill_gas"
    JET_FUEL = "jet_fuel"
    AVIATION_GASOLINE = "aviation_gasoline"
    RESIDUAL_FUEL_OIL = "residual_fuel_oil"
    E85 = "e85"
    B20 = "b20"
    CNG = "cng"
    LNG = "lng"
