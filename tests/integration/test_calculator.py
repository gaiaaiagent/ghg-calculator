"""Integration tests for GHG calculator engine."""

import pytest

from ghg_calculator.engine.calculator import GHGCalculator
from ghg_calculator.factors.registry import FactorRegistry
from ghg_calculator.models.activity import ActivityRecord
from ghg_calculator.models.enums import (
    FuelType,
    Scope,
    Scope1Category,
    Scope2Method,
    Scope3Category,
)


@pytest.fixture(scope="module")
def calc():
    registry = FactorRegistry.load()
    return GHGCalculator(registry=registry)


class TestScope1Stationary:
    def test_natural_gas_1000_therms(self, calc):
        """Reference: 1000 therms NG ≈ 5.3 tCO2e."""
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.STATIONARY_COMBUSTION,
            fuel_type=FuelType.NATURAL_GAS,
            quantity=1000,
            unit="therm",
        )
        results = calc.calculate_single(activity)
        assert len(results) == 1
        r = results[0]
        assert r.total_co2e_tonnes == pytest.approx(5.3, abs=0.2)
        assert r.scope == Scope.SCOPE_1
        assert len(r.gas_breakdown) >= 2  # At least CO2 and CH4

    def test_diesel_100_gallons(self, calc):
        """Reference: 100 gallons diesel ≈ 1.02 tCO2e."""
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.STATIONARY_COMBUSTION,
            fuel_type=FuelType.DIESEL,
            quantity=100,
            unit="gallon",
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_tonnes == pytest.approx(1.02, abs=0.1)

    def test_custom_factor(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.STATIONARY_COMBUSTION,
            quantity=500,
            unit="gallon",
            custom_factor=10.0,
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg == 5000.0

    def test_missing_fuel_raises(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.STATIONARY_COMBUSTION,
            quantity=100,
            unit="therm",
        )
        with pytest.raises(ValueError, match="No emission factor"):
            calc.calculate_single(activity)


class TestScope1Mobile:
    def test_gasoline_gallons(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.MOBILE_COMBUSTION,
            fuel_type=FuelType.GASOLINE,
            quantity=100,
            unit="gallon",
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg > 800  # ~878 kg

    def test_diesel_gallons(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.MOBILE_COMBUSTION,
            fuel_type=FuelType.DIESEL,
            quantity=100,
            unit="gallon",
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg > 1000


class TestScope1Fugitive:
    def test_r410a_leak(self, calc):
        """10 kg R-410A leaked = 10 × 2088 = 20,880 kg CO2e."""
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.FUGITIVE_EMISSIONS,
            quantity=10,
            unit="kg",
            refrigerant_type="r-410a",
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg == pytest.approx(20880, rel=0.01)

    def test_hfc134a(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.FUGITIVE_EMISSIONS,
            quantity=5,
            unit="kg",
            refrigerant_type="hfc-134a",
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg == pytest.approx(6500, rel=0.01)


class TestScope1Process:
    def test_custom_factor_required(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.PROCESS_EMISSIONS,
            quantity=100,
            unit="tonne",
        )
        with pytest.raises(ValueError):
            calc.calculate_single(activity)

    def test_custom_factor(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.PROCESS_EMISSIONS,
            quantity=100,
            unit="tonne",
            custom_factor=500,
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg == 50000


class TestScope2:
    def test_electricity_egrid(self, calc):
        """50,000 kWh in CAMX (California) region."""
        activity = ActivityRecord(
            scope=Scope.SCOPE_2,
            quantity=50000,
            unit="kWh",
            grid_subregion="CAMX",
        )
        results = calc.calculate_single(activity)
        # Should produce both location and market results
        assert len(results) == 2
        location = [r for r in results if r.scope2_method == Scope2Method.LOCATION_BASED]
        market = [r for r in results if r.scope2_method == Scope2Method.MARKET_BASED]
        assert len(location) == 1
        assert len(market) == 1
        # CAMX ≈ 0.24 kg/kWh → ~12 tCO2e for 50,000 kWh
        assert location[0].total_co2e_tonnes > 5
        assert location[0].total_co2e_tonnes < 30

    def test_electricity_custom_factor(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_2,
            quantity=10000,
            unit="kWh",
            custom_factor=0.5,
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg == 5000


class TestScope3:
    def test_custom_factor(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_3,
            scope3_category=Scope3Category.PURCHASED_GOODS_SERVICES,
            quantity=100000,
            unit="USD",
            custom_factor=0.5,
        )
        results = calc.calculate_single(activity)
        assert results[0].total_co2e_kg == 50000

    def test_missing_category_raises(self, calc):
        activity = ActivityRecord(
            scope=Scope.SCOPE_3,
            quantity=100,
            unit="kg",
        )
        with pytest.raises(ValueError, match="scope3_category"):
            calc.calculate_single(activity)


class TestInventory:
    def test_multi_activity_inventory(self, calc):
        activities = [
            ActivityRecord(
                scope=Scope.SCOPE_1,
                scope1_category=Scope1Category.STATIONARY_COMBUSTION,
                fuel_type=FuelType.NATURAL_GAS,
                quantity=1000,
                unit="therm",
            ),
            ActivityRecord(
                scope=Scope.SCOPE_2,
                quantity=50000,
                unit="kWh",
                grid_subregion="CAMX",
            ),
            ActivityRecord(
                scope=Scope.SCOPE_3,
                scope3_category=Scope3Category.BUSINESS_TRAVEL,
                quantity=50000,
                unit="USD",
                custom_factor=0.3,
            ),
        ]
        inventory = calc.calculate_inventory(activities, name="Test Corp", year=2024)

        assert inventory.name == "Test Corp"
        assert inventory.year == 2024
        assert inventory.scope1.total_co2e_kg > 0
        assert inventory.scope2_location.total_co2e_kg > 0
        assert inventory.scope3.total_co2e_kg == 15000
        assert inventory.total_co2e_kg > 0
        assert len(inventory.all_results) >= 4  # S1 + S2(loc) + S2(mkt) + S3
