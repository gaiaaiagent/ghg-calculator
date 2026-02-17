"""JSON factor file loader with version management."""

import json
from pathlib import Path

from ..models.enums import FactorSource
from ..models.factors import EmissionFactor, FactorVersion

DATA_DIR = Path(__file__).parent / "data"


def load_factor_file(path: Path) -> FactorVersion:
    """Load a single factor JSON file into a FactorVersion."""
    with open(path) as f:
        raw = json.load(f)

    factors = [
        EmissionFactor(
            id=fd["id"],
            name=fd["name"],
            source=FactorSource(raw["source"]),
            co2_factor=fd.get("co2_factor", 0.0),
            ch4_factor=fd.get("ch4_factor", 0.0),
            n2o_factor=fd.get("n2o_factor", 0.0),
            co2e_factor=fd.get("co2e_factor"),
            activity_unit=fd["activity_unit"],
            category=fd.get("category", ""),
            subcategory=fd.get("subcategory", ""),
            fuel_type=fd.get("fuel_type"),
            region=fd.get("region"),
            year=fd.get("year"),
            description=fd.get("description", ""),
            tags=fd.get("tags", []),
        )
        for fd in raw["factors"]
    ]

    return FactorVersion(
        source=FactorSource(raw["source"]),
        version=raw["version"],
        year=raw["year"],
        description=raw.get("description", ""),
        url=raw.get("url", ""),
        factor_count=len(factors),
        factors=factors,
    )


def discover_factor_files() -> list[Path]:
    """Find all factor JSON files in the data directory."""
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.rglob("*.json"))


def load_all_factors() -> list[FactorVersion]:
    """Load all available factor databases."""
    versions = []
    for path in discover_factor_files():
        try:
            versions.append(load_factor_file(path))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log but don't fail on bad files
            print(f"Warning: Failed to load {path}: {e}")
    return versions
