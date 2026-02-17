"""Tests for factor loading and registry."""

import pytest

from ghg_calculator.factors.registry import FactorRegistry
from ghg_calculator.models.enums import FactorSource


@pytest.fixture(scope="module")
def registry():
    return FactorRegistry.load()


class TestFactorRegistry:
    def test_loads_all_sources(self, registry):
        sources = registry.sources
        assert FactorSource.EPA_HUB in sources
        assert FactorSource.EGRID in sources
        assert FactorSource.DEFRA in sources
        assert FactorSource.USEEIO in sources
        assert FactorSource.EMBER in sources
        assert FactorSource.EXIOBASE in sources

    def test_factor_count(self, registry):
        assert registry.factor_count >= 900

    def test_get_by_id(self, registry):
        factor = registry.get("epa_stat_natural_gas_therm")
        assert factor is not None
        assert factor.co2_factor == pytest.approx(5.302)
        assert factor.activity_unit == "therm"

    def test_get_missing(self, registry):
        assert registry.get("nonexistent_factor_xyz") is None

    def test_search_natural_gas(self, registry):
        results = registry.search(query="natural gas", limit=10)
        assert len(results) > 0
        assert any("natural_gas" in r.id for r in results)

    def test_search_by_source(self, registry):
        results = registry.search(source=FactorSource.EGRID, limit=200)
        assert len(results) > 50
        assert all(r.source == FactorSource.EGRID for r in results)

    def test_search_by_category(self, registry):
        results = registry.search(category="stationary_combustion")
        assert len(results) > 10
        assert all(r.category == "stationary_combustion" for r in results)

    def test_search_by_fuel_type(self, registry):
        results = registry.search(fuel_type="diesel")
        assert len(results) > 0

    def test_search_electricity_by_region(self, registry):
        results = registry.search(category="electricity", region="CAMX")
        assert len(results) > 0

    def test_find_factor(self, registry):
        factor = registry.find_factor(
            category="stationary_combustion",
            fuel_type="natural_gas",
            activity_unit="therm",
        )
        assert factor is not None
        assert factor.co2_factor > 5.0

    def test_search_limit(self, registry):
        results = registry.search(limit=5)
        assert len(results) <= 5

    def test_useeio_spend_factors(self, registry):
        results = registry.search(source=FactorSource.USEEIO, limit=300)
        assert len(results) >= 200
        assert all(r.activity_unit == "USD" for r in results)

    def test_ember_countries(self, registry):
        results = registry.search(source=FactorSource.EMBER, limit=150)
        assert len(results) >= 80
        # Check a known country
        us = registry.search(source=FactorSource.EMBER, region="US", limit=1)
        assert len(us) == 1
        assert us[0].co2_factor > 0.3

    def test_refrigerant_factors(self, registry):
        results = registry.search(query="HFC-134a")
        assert len(results) > 0
        r134a = results[0]
        assert r134a.co2e_factor == 1300
