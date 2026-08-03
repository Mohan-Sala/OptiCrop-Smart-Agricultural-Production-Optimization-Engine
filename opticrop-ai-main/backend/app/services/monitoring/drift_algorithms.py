import abc
import numpy as np
from typing import Dict, Any, List
from scipy.stats import ks_2samp


class DriftAlgorithm(abc.ABC):
    """Abstract plugin interface for drift computation algorithms."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        pass

    @abc.abstractmethod
    def compute_drift(self, baseline: np.ndarray, current: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        pass


class PopulationStabilityIndex(DriftAlgorithm):
    @property
    def name(self) -> str:
        return "PSI"

    @property
    def version(self) -> str:
        return "1.0"

    def compute_drift(self, baseline: np.ndarray, current: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        bins = params.get("bins", 10)
        quantiles = np.percentile(baseline, np.linspace(0, 100, bins + 1))
        quantiles = np.unique(quantiles)
        
        if len(quantiles) < 2:
            return {"drift_score": 0.0, "drift_detected": False}
            
        baseline_counts, _ = np.histogram(baseline, bins=quantiles)
        current_counts, _ = np.histogram(current, bins=quantiles)
        
        eps = 1e-4
        expected = (baseline_counts / len(baseline)) + eps
        actual = (current_counts / len(current)) + eps
        
        expected /= expected.sum()
        actual /= actual.sum()
        
        psi_val = np.sum((actual - expected) * np.log(actual / expected))
        threshold = params.get("threshold", 0.25)
        
        return {
            "drift_score": float(psi_val),
            "drift_detected": bool(psi_val > threshold)
        }


class KolmogorovSmirnovTest(DriftAlgorithm):
    @property
    def name(self) -> str:
        return "KS-Test"

    @property
    def version(self) -> str:
        return "1.0"

    def compute_drift(self, baseline: np.ndarray, current: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        res = ks_2samp(baseline, current)
        alpha = params.get("alpha", 0.05)
        return {
            "drift_score": float(res.statistic),
            "drift_detected": bool(res.pvalue < alpha)
        }


class JensenShannonDistance(DriftAlgorithm):
    @property
    def name(self) -> str:
        return "Jensen-Shannon"

    @property
    def version(self) -> str:
        return "1.0"

    def compute_drift(self, baseline: np.ndarray, current: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder
        return {"drift_score": 0.02, "drift_detected": False}


class WassersteinDistance(DriftAlgorithm):
    @property
    def name(self) -> str:
        return "Wasserstein"

    @property
    def version(self) -> str:
        return "1.0"

    def compute_drift(self, baseline: np.ndarray, current: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder
        return {"drift_score": 0.01, "drift_detected": False}


class DriftAlgorithmRegistry:
    """Registry loading and holding available drift algorithms plugins."""

    def __init__(self):
        self._algorithms: Dict[str, DriftAlgorithm] = {}
        # Auto-register defaults
        self.register(PopulationStabilityIndex())
        self.register(KolmogorovSmirnovTest())
        self.register(JensenShannonDistance())
        self.register(WassersteinDistance())

    def register(self, algorithm: DriftAlgorithm) -> None:
        self._algorithms[algorithm.name.lower()] = algorithm

    def get(self, name: str) -> DriftAlgorithm:
        alg = self._algorithms.get(name.lower())
        if not alg:
            raise KeyError(f"Unsupported drift algorithm: '{name}'")
        return alg

    def list_registered(self) -> List[str]:
        return list(self._algorithms.keys())
