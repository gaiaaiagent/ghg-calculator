"""Data quality indicator model per GHG Protocol Chapter 7."""

from pydantic import BaseModel, Field

from .enums import DataQualityScore


class DataQualityIndicator(BaseModel):
    """5-dimension data quality assessment per GHG Protocol Corporate Standard Ch.7."""

    representativeness: DataQualityScore = Field(
        description="How well the data represents the actual activity"
    )
    completeness: DataQualityScore = Field(
        description="Whether all relevant data is included"
    )
    temporal: DataQualityScore = Field(
        description="How recent and time-appropriate the data is"
    )
    geographical: DataQualityScore = Field(
        description="How well the data matches the geographic scope"
    )
    technological: DataQualityScore = Field(
        description="How well the data matches the technology/process"
    )

    @property
    def overall_score(self) -> float:
        """Average score across all 5 dimensions (1.0=best, 5.0=worst)."""
        return (
            self.representativeness.value
            + self.completeness.value
            + self.temporal.value
            + self.geographical.value
            + self.technological.value
        ) / 5.0

    @property
    def overall_quality(self) -> DataQualityScore:
        """Overall quality as a discrete score (rounded)."""
        return DataQualityScore(round(self.overall_score))
