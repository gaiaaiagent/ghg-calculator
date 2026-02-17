"""Unit conversion using pint with custom GHG-specific definitions."""

import pint

# Create a unit registry with custom definitions
ureg = pint.UnitRegistry()

# Define custom energy units commonly used in GHG accounting
ureg.define("therm = 100000 BTU")
ureg.define("CCF = 100 * ft**3")  # Hundred cubic feet (natural gas)
ureg.define("MCF = 1000 * ft**3")  # Thousand cubic feet
ureg.define("dekatherm = 10 * therm")
ureg.define("short_ton = 2000 * lb")

# MMBtu = 1,000,000 BTU (define explicitly to avoid alias issues)
ureg.define("MMBtu = 1000000 * BTU")


class UnitConverter:
    """Convert between units commonly used in GHG emissions calculations."""

    def __init__(self) -> None:
        self.ureg = ureg

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert a value between units.

        Args:
            value: Numeric value to convert
            from_unit: Source unit string (e.g., "gallon", "therm", "kWh")
            to_unit: Target unit string

        Returns:
            Converted value

        Raises:
            pint.DimensionalityError: If units are incompatible
            pint.UndefinedUnitError: If unit is not recognized
        """
        quantity = self.ureg.Quantity(value, from_unit)
        return quantity.to(to_unit).magnitude

    def is_compatible(self, unit1: str, unit2: str) -> bool:
        """Check if two units are dimensionally compatible."""
        try:
            q1 = self.ureg.Quantity(1, unit1)
            q1.to(unit2)
            return True
        except (pint.DimensionalityError, pint.UndefinedUnitError):
            return False

    def get_base_unit(self, unit: str) -> str:
        """Get the base SI unit for a given unit."""
        quantity = self.ureg.Quantity(1, unit)
        return str(quantity.to_base_units().units)

    def parse_unit(self, unit_str: str) -> str:
        """Validate and normalize a unit string.

        Raises:
            pint.UndefinedUnitError: If unit is not recognized
        """
        unit = self.ureg.parse_units(unit_str)
        return str(unit)


# Module-level singleton
converter = UnitConverter()
