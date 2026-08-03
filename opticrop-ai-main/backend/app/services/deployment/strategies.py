from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from app.models.deployment import ModelDeployment, DeploymentPolicy

class DeploymentStrategy(ABC):
    """Abstract interface representing a traffic routing deployment strategy."""

    @abstractmethod
    def initialize(self, policy: DeploymentPolicy) -> Tuple[int, str]:
        """Initializes the traffic routing step.
        
        Returns a tuple of (initial_traffic_percentage, initial_state).
        """
        pass

    @abstractmethod
    def evaluate_step(
        self,
        deployment: ModelDeployment,
        policy: DeploymentPolicy,
        health_aggregates: Dict[str, Any],
    ) -> Tuple[int, str]:
        """Evaluates health telemetry to determine the next traffic allocation and state.
        
        Returns a tuple of (next_traffic_percentage, next_state).
        """
        pass


class RollingStrategy(DeploymentStrategy):
    """Progressively replaces old model instances with no traffic splitting (direct transition)."""

    def initialize(self, policy: DeploymentPolicy) -> Tuple[int, str]:
        return 100, "PRODUCTION"

    def evaluate_step(
        self,
        deployment: ModelDeployment,
        policy: DeploymentPolicy,
        health_aggregates: Dict[str, Any],
    ) -> Tuple[int, str]:
        # Direct promotion. If health is bad, fail
        if (
            policy.maximum_error_rate is not None
            and health_aggregates.get("total_errors", 0) > 0
            and health_aggregates.get("unhealthy_count", 0) > 0
        ):
            return 0, "FAILED"
        return 100, "PRODUCTION"


class CanaryStrategy(DeploymentStrategy):
    """Splits traffic starting at a low tier, scaling up incrementally based on promotion stages."""

    def initialize(self, policy: DeploymentPolicy) -> Tuple[int, str]:
        stages = policy.promotion_stages.get("stages", [10, 25, 50, 75, 100])
        initial_percentage = stages[0] if stages else 10
        return initial_percentage, "PROMOTING"

    def evaluate_step(
        self,
        deployment: ModelDeployment,
        policy: DeploymentPolicy,
        health_aggregates: Dict[str, Any],
    ) -> Tuple[int, str]:
        # Validate health metrics
        max_error = policy.maximum_error_rate or 1.0
        avg_latency = health_aggregates.get("avg_latency", 0.0)
        max_latency = policy.maximum_latency_ms or 999999.0

        total_errors = health_aggregates.get("total_errors", 0)
        unhealthy_count = health_aggregates.get("unhealthy_count", 0)

        # Health gate checks
        if unhealthy_count > 0 or avg_latency > max_latency:
            # Rollback
            return 0, "FAILED"

        stages = policy.promotion_stages.get("stages", [10, 25, 50, 75, 100])
        current = deployment.traffic_percentage

        # Find the next stage
        next_percentage = current
        for s in stages:
            if s > current:
                next_percentage = s
                break

        if next_percentage == current:
            # Already at max stage
            return 100, "PRODUCTION"

        next_state = "PRODUCTION" if next_percentage == 100 else "PROMOTING"
        return next_percentage, next_state


class BlueGreenStrategy(DeploymentStrategy):
    """Deploys a duplicate target environment, flipping 100% of traffic after validation."""

    def initialize(self, policy: DeploymentPolicy) -> Tuple[int, str]:
        return 0, "TESTING"

    def evaluate_step(
        self,
        deployment: ModelDeployment,
        policy: DeploymentPolicy,
        health_aggregates: Dict[str, Any],
    ) -> Tuple[int, str]:
        # Validate that the green environment passes health probes
        unhealthy_count = health_aggregates.get("unhealthy_count", 0)
        if unhealthy_count > 0:
            return 0, "FAILED"

        # Flip traffic entirely
        return 100, "PRODUCTION"


class ShadowStrategy(DeploymentStrategy):
    """Replicates 100% of request traffic in parallel, returning 0% to the production client."""

    def initialize(self, policy: DeploymentPolicy) -> Tuple[int, str]:
        return 0, "TESTING"

    def evaluate_step(
        self,
        deployment: ModelDeployment,
        policy: DeploymentPolicy,
        health_aggregates: Dict[str, Any],
    ) -> Tuple[int, str]:
        unhealthy_count = health_aggregates.get("unhealthy_count", 0)
        if unhealthy_count > 0:
            return 0, "FAILED"

        # Keep traffic at 0% but transition to PRODUCTION state (shadow validated)
        return 0, "PRODUCTION"


class StrategyFactory:
    """Factory to retrieve the appropriate traffic routing strategy."""

    _strategies = {
        "ROLLING": RollingStrategy(),
        "CANARY": CanaryStrategy(),
        "BLUE_GREEN": BlueGreenStrategy(),
        "SHADOW": ShadowStrategy(),
    }

    @classmethod
    def get_strategy(cls, strategy_name: str) -> DeploymentStrategy:
        name = strategy_name.upper()
        if name not in cls._strategies:
            raise ValueError(f"Unsupported strategy: {strategy_name}")
        return cls._strategies[name]
