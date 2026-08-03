import numpy as np


class StatisticsService:
    """Helper service computing array means, variances, modes, and percentiles."""

    def mean(self, arr: np.ndarray) -> float:
        return float(np.mean(arr)) if len(arr) > 0 else 0.0

    def std(self, arr: np.ndarray) -> float:
        return float(np.std(arr)) if len(arr) > 0 else 0.0
