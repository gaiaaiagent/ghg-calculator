"""Factor registry — loads, indexes, and queries all emission factors."""

from ..models.enums import FactorSource, Scope
from ..models.factors import EmissionFactor, FactorVersion
from .loader import load_all_factors


class FactorRegistry:
    """Central registry for querying emission factors across all sources."""

    def __init__(self) -> None:
        self._versions: list[FactorVersion] = []
        self._factors: list[EmissionFactor] = []
        self._by_id: dict[str, EmissionFactor] = {}

    @classmethod
    def load(cls) -> "FactorRegistry":
        """Load all available factor databases and return a populated registry."""
        registry = cls()
        for version in load_all_factors():
            registry.add_version(version)
        return registry

    def add_version(self, version: FactorVersion) -> None:
        """Add a factor database version to the registry."""
        self._versions.append(version)
        for factor in version.factors:
            self._factors.append(factor)
            self._by_id[factor.id] = factor

    def get(self, factor_id: str) -> EmissionFactor | None:
        """Get a factor by its exact ID."""
        return self._by_id.get(factor_id)

    def search(
        self,
        query: str = "",
        source: FactorSource | None = None,
        category: str | None = None,
        fuel_type: str | None = None,
        region: str | None = None,
        scope: Scope | None = None,
        activity_unit: str | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[EmissionFactor]:
        """Search factors with flexible filtering.

        Args:
            query: Free-text search across name, description, tags, fuel_type
            source: Filter by factor database source
            category: Filter by category (e.g., 'stationary_combustion')
            fuel_type: Filter by fuel type
            region: Filter by region
            scope: Filter by scope
            activity_unit: Filter by activity unit
            tags: Filter by tags (all must match)
            limit: Maximum results to return

        Returns:
            List of matching EmissionFactors, best matches first
        """
        results = self._factors

        if source is not None:
            results = [f for f in results if f.source == source]

        if category is not None:
            results = [f for f in results if f.category == category]

        if fuel_type is not None:
            fuel_lower = fuel_type.lower()
            results = [f for f in results if f.fuel_type and f.fuel_type.lower() == fuel_lower]

        if region is not None:
            region_lower = region.lower()
            results = [f for f in results if f.region and f.region.lower() == region_lower]

        if scope is not None:
            results = [f for f in results if f.scope == scope]

        if activity_unit is not None:
            unit_lower = activity_unit.lower()
            results = [f for f in results if f.activity_unit.lower() == unit_lower]

        if tags:
            tag_set = set(t.lower() for t in tags)
            results = [
                f for f in results
                if tag_set.issubset(set(t.lower() for t in f.tags))
            ]

        if query:
            query_lower = query.lower()
            scored: list[tuple[int, EmissionFactor]] = []
            for f in results:
                score = 0
                searchable = f"{f.name} {f.description} {f.category} {f.subcategory} {f.fuel_type or ''} {' '.join(f.tags)}"
                searchable_lower = searchable.lower()
                if query_lower in searchable_lower:
                    score += 10
                # Boost exact name matches
                if query_lower in f.name.lower():
                    score += 20
                if query_lower == (f.fuel_type or "").lower():
                    score += 15
                # Word-level matching
                for word in query_lower.split():
                    if word in searchable_lower:
                        score += 5
                if score > 0:
                    scored.append((score, f))
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [f for _, f in scored]

        return results[:limit]

    def find_factor(
        self,
        category: str,
        fuel_type: str | None = None,
        region: str | None = None,
        activity_unit: str | None = None,
        source: FactorSource | None = None,
    ) -> EmissionFactor | None:
        """Find the best matching single factor for a calculation.

        Returns the first match, preferring exact matches on all criteria.
        """
        results = self.search(
            category=category,
            fuel_type=fuel_type,
            region=region,
            activity_unit=activity_unit,
            source=source,
            limit=1,
        )
        return results[0] if results else None

    @property
    def factor_count(self) -> int:
        return len(self._factors)

    @property
    def sources(self) -> list[FactorSource]:
        return list({v.source for v in self._versions})

    @property
    def versions(self) -> list[FactorVersion]:
        return self._versions
