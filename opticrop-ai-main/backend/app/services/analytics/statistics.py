from typing import List


class StatisticsService:
    """Computes rollups, percentiles, growth trends, and aggregations on analytics raw data."""

    def compute_average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def calculate_growth_rate(self, current: float, previous: float) -> float:
        """Calculates percentage growth between current and previous values."""
        if previous == 0.0:
            return 100.0 if current > 0.0 else 0.0
        return ((current - previous) / previous) * 100.0
