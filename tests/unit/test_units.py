"""Tests for unit converter."""

import pytest

from ghg_calculator.units.converter import UnitConverter, converter


class TestUnitConverter:
    def test_singleton(self):
        assert isinstance(converter, UnitConverter)

    def test_energy_conversions(self):
        c = converter
        # 1 therm = 100,000 BTU
        assert c.convert(1, "therm", "BTU") == pytest.approx(100000, rel=1e-3)
        # 1 kWh = 3412.14 BTU
        assert c.convert(1, "kWh", "BTU") == pytest.approx(3412.14, rel=1e-3)

    def test_therm_to_mmbtu(self):
        # 1 MMBtu = 10 therms
        assert converter.convert(10, "therm", "MMBtu") == pytest.approx(1.0, rel=1e-3)

    def test_volume_conversions(self):
        # 1 gallon = 3.78541 liters
        assert converter.convert(1, "gallon", "liter") == pytest.approx(3.78541, rel=1e-3)

    def test_mass_conversions(self):
        # 1 short_ton = 2000 lb
        assert converter.convert(1, "short_ton", "lb") == pytest.approx(2000, rel=1e-3)
        # 1 metric_ton = 1000 kg
        assert converter.convert(1, "metric_ton", "kg") == pytest.approx(1000, rel=1e-3)

    def test_ccf_natural_gas(self):
        # CCF = 100 cubic feet
        assert converter.convert(1, "CCF", "ft**3") == pytest.approx(100, rel=1e-3)

    def test_is_compatible(self):
        assert converter.is_compatible("kWh", "BTU")
        assert converter.is_compatible("gallon", "liter")
        assert not converter.is_compatible("kWh", "gallon")

    def test_incompatible_raises(self):
        with pytest.raises(Exception):
            converter.convert(1, "kWh", "gallon")

    def test_parse_unit(self):
        assert converter.parse_unit("kWh") is not None
        assert converter.parse_unit("gallon") is not None

    def test_unknown_unit_raises(self):
        with pytest.raises(Exception):
            converter.parse_unit("flobnarbs")
