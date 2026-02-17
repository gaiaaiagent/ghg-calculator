"""Emission factor database."""

from .gwp import get_gwp, list_gases, to_co2e
from .loader import load_all_factors
from .registry import FactorRegistry

__all__ = ["FactorRegistry", "get_gwp", "list_gases", "load_all_factors", "to_co2e"]
