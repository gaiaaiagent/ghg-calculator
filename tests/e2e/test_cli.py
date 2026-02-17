"""End-to-end CLI tests."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ghg_calculator.cli.app import app

runner = CliRunner()


class TestCalculateCommand:
    def test_natural_gas_therms(self):
        result = runner.invoke(app, [
            "calculate",
            "--scope", "1",
            "--category", "stationary_combustion",
            "--fuel", "natural_gas",
            "--quantity", "1000",
            "--unit", "therm",
        ])
        assert result.exit_code == 0
        assert "5,307" in result.output or "5307" in result.output

    def test_json_output(self):
        result = runner.invoke(app, [
            "calculate",
            "--scope", "1",
            "--category", "stationary_combustion",
            "--fuel", "natural_gas",
            "--quantity", "1000",
            "--unit", "therm",
            "--json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["total_co2e_kg"] > 5000

    def test_scope2_electricity(self):
        result = runner.invoke(app, [
            "calculate",
            "--scope", "2",
            "--quantity", "50000",
            "--unit", "kWh",
            "--region", "CAMX",
        ])
        assert result.exit_code == 0
        assert "location_based" in result.output

    def test_custom_factor(self):
        result = runner.invoke(app, [
            "calculate",
            "--scope", "1",
            "--category", "stationary_combustion",
            "--quantity", "100",
            "--unit", "gallon",
            "--factor", "10.0",
        ])
        assert result.exit_code == 0
        assert "1,000" in result.output or "1000" in result.output

    def test_zero_quantity_error(self):
        result = runner.invoke(app, [
            "calculate",
            "--scope", "1",
            "--quantity", "0",
            "--unit", "therm",
        ])
        assert result.exit_code == 1


class TestFactorsCommand:
    def test_search(self):
        result = runner.invoke(app, ["factors", "diesel"])
        assert result.exit_code == 0
        assert "diesel" in result.output.lower()

    def test_search_with_source(self):
        result = runner.invoke(app, ["factors", "--source", "egrid"])
        assert result.exit_code == 0
        assert "egrid" in result.output

    def test_no_results(self):
        result = runner.invoke(app, ["factors", "zzz_nonexistent_zzz"])
        assert result.exit_code == 0
        assert "No factors" in result.output


class TestGWPCommand:
    def test_specific_gas(self):
        result = runner.invoke(app, ["gwp", "ch4"])
        assert result.exit_code == 0
        assert "28" in result.output

    def test_all_gases(self):
        result = runner.invoke(app, ["gwp"])
        assert result.exit_code == 0
        assert "co2" in result.output

    def test_unknown_gas(self):
        result = runner.invoke(app, ["gwp", "unobtainium"])
        assert result.exit_code == 1


class TestConvertCommand:
    def test_energy_conversion(self):
        result = runner.invoke(app, ["convert", "100", "therm", "MMBtu"])
        assert result.exit_code == 0
        assert "10" in result.output

    def test_incompatible_units(self):
        result = runner.invoke(app, ["convert", "100", "kWh", "gallon"])
        assert result.exit_code == 1


class TestValidateCommand:
    def test_valid_file(self, tmp_path):
        data = [{"scope": "scope_1", "scope1_category": "stationary_combustion",
                 "fuel_type": "natural_gas", "quantity": 1000, "unit": "therm"}]
        f = tmp_path / "test.json"
        f.write_text(json.dumps(data))
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 0
        assert "1 valid" in result.output

    def test_invalid_file(self, tmp_path):
        data = [{"scope": "scope_1", "quantity": -5, "unit": "therm"}]
        f = tmp_path / "test.json"
        f.write_text(json.dumps(data))
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "invalid" in result.output

    def test_missing_file(self):
        result = runner.invoke(app, ["validate", "/tmp/nonexistent_ghg_file.json"])
        assert result.exit_code == 1


class TestReportCommand:
    def test_report_generation(self, tmp_path):
        data = [
            {"scope": "scope_1", "scope1_category": "stationary_combustion",
             "fuel_type": "natural_gas", "quantity": 1000, "unit": "therm"},
            {"scope": "scope_2", "quantity": 50000, "unit": "kWh",
             "grid_subregion": "CAMX"},
            {"scope": "scope_3", "scope3_category": 6, "quantity": 10000,
             "unit": "USD", "custom_factor": 0.3},
        ]
        input_f = tmp_path / "activities.json"
        input_f.write_text(json.dumps(data))
        output_f = tmp_path / "report.html"

        result = runner.invoke(app, ["report", str(input_f), "--output", str(output_f)])
        assert result.exit_code == 0
        assert output_f.exists()
        html = output_f.read_text()
        assert "GHG Emissions" in html
        assert "Scope 1" in html
