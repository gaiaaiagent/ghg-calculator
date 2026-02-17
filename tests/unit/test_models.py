"""Tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from ghg_calculator.models import (
    ActivityRecord,
    DataQualityIndicator,
    DataQualityScore,
    EmissionFactor,
    EmissionResult,
    FactorSource,
    FuelType,
    GasBreakdown,
    GasType,
    GWPAssessment,
    InventoryResult,
    Scope,
    Scope1Category,
    Scope2Method,
    Scope3Category,
    ScopeResult,
)


class TestActivityRecord:
    def test_minimal_scope1(self):
        record = ActivityRecord(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.STATIONARY_COMBUSTION,
            fuel_type=FuelType.NATURAL_GAS,
            quantity=1000,
            unit="therm",
        )
        assert record.scope == Scope.SCOPE_1
        assert record.quantity == 1000
        assert record.unit == "therm"

    def test_minimal_scope2(self):
        record = ActivityRecord(
            scope=Scope.SCOPE_2,
            quantity=50000,
            unit="kWh",
            grid_subregion="CAMX",
        )
        assert record.scope == Scope.SCOPE_2
        assert record.grid_subregion == "CAMX"

    def test_scope3_spend_based(self):
        record = ActivityRecord(
            scope=Scope.SCOPE_3,
            scope3_category=Scope3Category.PURCHASED_GOODS_SERVICES,
            quantity=100000,
            unit="USD",
            spend_amount=100000,
            naics_code="325211",
        )
        assert record.scope3_category == Scope3Category.PURCHASED_GOODS_SERVICES

    def test_quantity_must_be_positive(self):
        with pytest.raises(ValidationError):
            ActivityRecord(scope=Scope.SCOPE_1, quantity=0, unit="therm")

    def test_quantity_must_not_be_negative(self):
        with pytest.raises(ValidationError):
            ActivityRecord(scope=Scope.SCOPE_1, quantity=-100, unit="therm")

    def test_custom_factor_override(self):
        record = ActivityRecord(
            scope=Scope.SCOPE_1,
            quantity=500,
            unit="gallon",
            custom_factor=8.887,
            custom_factor_unit="kg CO2/gallon",
        )
        assert record.custom_factor == 8.887

    def test_tags_and_metadata(self):
        record = ActivityRecord(
            scope=Scope.SCOPE_1,
            quantity=100,
            unit="gallon",
            tags={"facility": "HQ", "department": "ops"},
            metadata={"source_doc": "invoice_123.pdf"},
        )
        assert record.tags["facility"] == "HQ"


class TestEmissionFactor:
    def test_basic_factor(self):
        factor = EmissionFactor(
            id="epa_ng_therm",
            name="Natural Gas (per therm)",
            source=FactorSource.EPA_HUB,
            co2_factor=5.302,
            ch4_factor=0.0001,
            n2o_factor=0.00001,
            activity_unit="therm",
            category="stationary_combustion",
            fuel_type="natural_gas",
        )
        assert factor.co2_factor == 5.302
        assert factor.source == FactorSource.EPA_HUB

    def test_factor_with_hfc(self):
        factor = EmissionFactor(
            id="refrig_r410a",
            name="R-410A Refrigerant",
            source=FactorSource.EPA_HUB,
            other_factors={GasType.HFC: 1.0},
            activity_unit="kg",
        )
        assert GasType.HFC in factor.other_factors


class TestEmissionResult:
    def test_basic_result(self):
        result = EmissionResult(
            scope=Scope.SCOPE_1,
            scope1_category=Scope1Category.STATIONARY_COMBUSTION,
            total_co2e_kg=5300.0,
            gas_breakdown=[
                GasBreakdown(gas=GasType.CO2, mass_kg=5302.0, co2e_kg=5302.0, gwp_used=1.0),
                GasBreakdown(gas=GasType.CH4, mass_kg=0.1, co2e_kg=2.8, gwp_used=28.0),
            ],
        )
        assert result.total_co2e_kg == 5300.0
        assert result.total_co2e_tonnes == pytest.approx(5.3)

    def test_scope2_result(self):
        result = EmissionResult(
            scope=Scope.SCOPE_2,
            scope2_method=Scope2Method.LOCATION_BASED,
            total_co2e_kg=15000.0,
        )
        assert result.scope2_method == Scope2Method.LOCATION_BASED


class TestScopeResult:
    def test_add_results(self):
        scope = ScopeResult(scope=Scope.SCOPE_1)
        r1 = EmissionResult(scope=Scope.SCOPE_1, total_co2e_kg=1000)
        r2 = EmissionResult(scope=Scope.SCOPE_1, total_co2e_kg=2000)
        scope.add_result(r1)
        scope.add_result(r2)
        assert scope.total_co2e_kg == 3000
        assert scope.total_co2e_tonnes == 3.0
        assert len(scope.results) == 2


class TestInventoryResult:
    def test_routing(self):
        inv = InventoryResult()
        inv.add_result(EmissionResult(scope=Scope.SCOPE_1, total_co2e_kg=1000))
        inv.add_result(EmissionResult(scope=Scope.SCOPE_2, scope2_method=Scope2Method.LOCATION_BASED, total_co2e_kg=2000))
        inv.add_result(EmissionResult(scope=Scope.SCOPE_2, scope2_method=Scope2Method.MARKET_BASED, total_co2e_kg=1800))
        inv.add_result(EmissionResult(scope=Scope.SCOPE_3, total_co2e_kg=5000))

        assert inv.scope1.total_co2e_kg == 1000
        assert inv.scope2_location.total_co2e_kg == 2000
        assert inv.scope2_market.total_co2e_kg == 1800
        assert inv.scope3.total_co2e_kg == 5000
        assert inv.total_co2e_kg == 8000  # Uses location-based scope 2
        assert len(inv.all_results) == 4


class TestDataQualityIndicator:
    def test_overall_score(self):
        dq = DataQualityIndicator(
            representativeness=DataQualityScore.GOOD,
            completeness=DataQualityScore.VERY_GOOD,
            temporal=DataQualityScore.GOOD,
            geographical=DataQualityScore.FAIR,
            technological=DataQualityScore.GOOD,
        )
        assert dq.overall_score == pytest.approx(2.0)
        assert dq.overall_quality == DataQualityScore.GOOD

    def test_worst_case(self):
        dq = DataQualityIndicator(
            representativeness=DataQualityScore.VERY_POOR,
            completeness=DataQualityScore.VERY_POOR,
            temporal=DataQualityScore.VERY_POOR,
            geographical=DataQualityScore.VERY_POOR,
            technological=DataQualityScore.VERY_POOR,
        )
        assert dq.overall_score == 5.0
        assert dq.overall_quality == DataQualityScore.VERY_POOR


class TestEnums:
    def test_scope3_categories(self):
        assert Scope3Category.PURCHASED_GOODS_SERVICES == 1
        assert Scope3Category.INVESTMENTS == 15
        assert len(Scope3Category) == 15

    def test_gwp_assessment_values(self):
        assert GWPAssessment.AR5.value == "ar5"
        assert GWPAssessment.AR6.value == "ar6"
