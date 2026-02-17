"""Global Warming Potential (GWP) tables from IPCC AR5 and AR6.

100-year GWP values used for converting individual GHGs to CO2-equivalent.
"""

from ..models.enums import GasType, GWPAssessment

# AR5 (2014) - 100-year GWP values (used by most current reporting frameworks)
AR5_GWP: dict[str, float] = {
    # Core gases
    "co2": 1.0,
    "ch4": 28.0,
    "n2o": 265.0,
    "sf6": 23500.0,
    "nf3": 16100.0,
    # Common HFCs
    "hfc-23": 12400.0,
    "hfc-32": 677.0,
    "hfc-125": 3170.0,
    "hfc-134a": 1300.0,
    "hfc-143a": 4800.0,
    "hfc-152a": 138.0,
    "hfc-227ea": 3350.0,
    "hfc-236fa": 8060.0,
    "hfc-245fa": 858.0,
    "hfc-365mfc": 804.0,
    "hfc-43-10mee": 1650.0,
    # Common PFCs
    "cf4": 6630.0,
    "c2f6": 11100.0,
    "c3f8": 8900.0,
    "c4f10": 9200.0,
    "c5f12": 8550.0,
    "c6f14": 7910.0,
    # Refrigerant blends (weighted averages)
    "r-404a": 3922.0,
    "r-407a": 2107.0,
    "r-407c": 1774.0,
    "r-410a": 2088.0,
    "r-507a": 3985.0,
    "r-508b": 13396.0,
}

# AR6 (2021) - 100-year GWP values (latest science)
AR6_GWP: dict[str, float] = {
    # Core gases
    "co2": 1.0,
    "ch4": 27.9,  # Slightly revised from AR5
    "n2o": 273.0,
    "sf6": 25200.0,
    "nf3": 17400.0,
    # Common HFCs
    "hfc-23": 14600.0,
    "hfc-32": 771.0,
    "hfc-125": 3740.0,
    "hfc-134a": 1530.0,
    "hfc-143a": 5810.0,
    "hfc-152a": 164.0,
    "hfc-227ea": 3600.0,
    "hfc-236fa": 8690.0,
    "hfc-245fa": 962.0,
    "hfc-365mfc": 914.0,
    "hfc-43-10mee": 1600.0,
    # Common PFCs
    "cf4": 7380.0,
    "c2f6": 12400.0,
    "c3f8": 9290.0,
    "c4f10": 10000.0,
    "c5f12": 9220.0,
    "c6f14": 8620.0,
    # Refrigerant blends (recalculated with AR6 component values)
    "r-404a": 4728.0,
    "r-407a": 2446.0,
    "r-407c": 2088.0,
    "r-410a": 2256.0,
    "r-507a": 4728.0,
    "r-508b": 14760.0,
}

_GWP_TABLES: dict[GWPAssessment, dict[str, float]] = {
    GWPAssessment.AR5: AR5_GWP,
    GWPAssessment.AR6: AR6_GWP,
}


def get_gwp(gas: str | GasType, assessment: GWPAssessment = GWPAssessment.AR5) -> float:
    """Get the 100-year GWP value for a gas.

    Args:
        gas: Gas identifier (e.g., "co2", "ch4", GasType.CO2, "hfc-134a", "r-410a")
        assessment: IPCC Assessment Report version

    Returns:
        GWP value (dimensionless, relative to CO2=1)

    Raises:
        KeyError: If gas is not found in the GWP table
    """
    table = _GWP_TABLES[assessment]
    key = gas.value if isinstance(gas, GasType) else gas.lower()

    # CO2e has GWP of 1 (already converted)
    if key == "co2e":
        return 1.0

    if key not in table:
        raise KeyError(
            f"Unknown gas '{key}' for {assessment.value}. "
            f"Available gases: {sorted(table.keys())}"
        )
    return table[key]


def list_gases(assessment: GWPAssessment = GWPAssessment.AR5) -> list[str]:
    """List all available gases for a given assessment."""
    return sorted(_GWP_TABLES[assessment].keys())


def to_co2e(mass_kg: float, gas: str | GasType, assessment: GWPAssessment = GWPAssessment.AR5) -> float:
    """Convert a mass of a specific gas to CO2-equivalent.

    Args:
        mass_kg: Mass in kg of the specific gas
        gas: Gas identifier
        assessment: IPCC Assessment Report version

    Returns:
        CO2-equivalent mass in kg
    """
    return mass_kg * get_gwp(gas, assessment)
