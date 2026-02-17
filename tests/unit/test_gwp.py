"""Tests for GWP tables and conversion."""

import pytest

from ghg_calculator.factors.gwp import get_gwp, list_gases, to_co2e
from ghg_calculator.models.enums import GasType, GWPAssessment


class TestGetGWP:
    def test_co2_is_one(self):
        assert get_gwp("co2") == 1.0
        assert get_gwp(GasType.CO2) == 1.0

    def test_ch4_ar5(self):
        assert get_gwp("ch4", GWPAssessment.AR5) == 28.0

    def test_ch4_ar6(self):
        assert get_gwp("ch4", GWPAssessment.AR6) == 27.9

    def test_n2o_ar5(self):
        assert get_gwp("n2o", GWPAssessment.AR5) == 265.0

    def test_n2o_ar6(self):
        assert get_gwp("n2o", GWPAssessment.AR6) == 273.0

    def test_sf6(self):
        assert get_gwp("sf6", GWPAssessment.AR5) == 23500.0

    def test_hfc_134a(self):
        assert get_gwp("hfc-134a", GWPAssessment.AR5) == 1300.0

    def test_refrigerant_blend(self):
        assert get_gwp("r-410a", GWPAssessment.AR5) == 2088.0

    def test_case_insensitive(self):
        assert get_gwp("CO2") == 1.0
        assert get_gwp("CH4") == 28.0

    def test_co2e_returns_one(self):
        assert get_gwp("co2e") == 1.0
        assert get_gwp(GasType.CO2E) == 1.0

    def test_unknown_gas_raises(self):
        with pytest.raises(KeyError, match="Unknown gas"):
            get_gwp("unobtainium")

    def test_gas_type_enum(self):
        assert get_gwp(GasType.CH4) == 28.0
        assert get_gwp(GasType.N2O) == 265.0


class TestToCO2e:
    def test_co2_passthrough(self):
        assert to_co2e(100.0, "co2") == 100.0

    def test_ch4_conversion(self):
        assert to_co2e(1.0, "ch4") == 28.0

    def test_n2o_conversion(self):
        assert to_co2e(1.0, "n2o", GWPAssessment.AR5) == 265.0

    def test_hfc_134a_conversion(self):
        # 10 kg of HFC-134a = 13,000 kg CO2e
        assert to_co2e(10.0, "hfc-134a") == 13000.0


class TestListGases:
    def test_ar5_has_core_gases(self):
        gases = list_gases(GWPAssessment.AR5)
        assert "co2" in gases
        assert "ch4" in gases
        assert "n2o" in gases
        assert "sf6" in gases

    def test_ar6_has_core_gases(self):
        gases = list_gases(GWPAssessment.AR6)
        assert "co2" in gases
        assert "ch4" in gases

    def test_sorted(self):
        gases = list_gases()
        assert gases == sorted(gases)
