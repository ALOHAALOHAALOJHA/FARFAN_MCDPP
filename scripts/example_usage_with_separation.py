#!/usr/bin/env python3
"""
Example: Using calibration and parametrization together in practice.

This demonstrates how a typical pipeline execution would:
1. Load calibration data (quality characteristics)
2. Load parametrization data (runtime parameters)
3. Execute analysis maintaining boundary separation
"""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.core.orchestrator import ExecutorConfig, load_executor_config


class CalibrationLoader:
    """Load calibration data (WHAT domain)."""

    @staticmethod
    def load_intrinsic_quality() -> dict[str, float]:
        """Load base quality scores."""
        intrinsic_file = Path("system/config/calibration/intrinsic_calibration.json")
        if not intrinsic_file.exists():
            return {"b_theory": 0.85, "b_impl": 0.78, "b_deploy": 0.82}

        with open(intrinsic_file) as f:
            data = json.load(f)
            return data.get("base_quality", {})

    @staticmethod
    def load_fusion_weights(role: str) -> dict[str, Any]:
        """Load fusion weights for specific role."""
        fusion_file = Path("config/json_files_ no_schemas/fusion_specification.json")
        if not fusion_file.exists():
            return {
                "linear_weights": {"@b": 0.35, "@chain": 0.25},
                "interaction_weights": {"(@u, @chain)": 0.15},
            }

        with open(fusion_file) as f:
            data = json.load(f)
            return data.get("role_fusion_parameters", {}).get(role, {})


class ParametrizationLoader:
    """Load parametrization data (HOW domain)."""

    @staticmethod
    def load_runtime_config(
        env: str = "production", cli_overrides: dict[str, Any] | None = None
    ) -> ExecutorConfig:
        """Load runtime execution parameters with hierarchy."""
        return load_executor_config(env=env, cli_overrides=cli_overrides)


class PolicyAnalyzer:
    """Example policy analyzer using separated concerns."""

    def __init__(
        self,
        calibration: dict[str, Any],
        executor_config: ExecutorConfig,
    ) -> None:
        """
        Initialize analyzer with separate calibration and parametrization.

        Args:
            calibration: Quality characteristics (WHAT)
            executor_config: Runtime parameters (HOW)
        """
        self.calibration = calibration
        self.executor_config = executor_config

    def analyze(self, policy_text: str) -> dict[str, Any]:
        """
        Analyze policy maintaining separation of concerns.

        Uses calibration for quality assessment, parametrization for execution control.
        """
        print(f"Analyzing with timeout={self.executor_config.timeout_s}s...")

        quality_score = self._compute_quality_score(policy_text)

        return {
            "quality_score": quality_score,
            "calibration_used": {
                "b_theory": self.calibration["intrinsic"]["b_theory"],
                "fusion_weights": self.calibration["fusion"]["linear_weights"],
            },
            "execution_params": {
                "timeout_s": self.executor_config.timeout_s,
                "retry": self.executor_config.retry,
                "max_tokens": self.executor_config.max_tokens,
            },
        }

    def _compute_quality_score(self, policy_text: str) -> float:
        """Compute quality score using calibration data."""
        base_quality = self.calibration["intrinsic"]["b_theory"]
        weights = self.calibration["fusion"]["linear_weights"]

        weight_b = weights.get("@b", 0.35)
        simulated_score = base_quality * weight_b

        return simulated_score


def main() -> int:
    """Demonstrate complete usage with separation."""
    print("=" * 80)
    print("EXAMPLE: Policy Analysis with Calibration/Parametrization Separation")
    print("=" * 80)
    print()

    print("Step 1: Load Calibration Data (WHAT)")
    print("-" * 80)

    calibration = {
        "intrinsic": CalibrationLoader.load_intrinsic_quality(),
        "fusion": CalibrationLoader.load_fusion_weights("SCORE_Q"),
    }

    print(
        f"✓ Loaded intrinsic quality: b_theory={calibration['intrinsic'].get('b_theory', 'N/A')}"
    )
    print(
        f"✓ Loaded fusion weights: {list(calibration['fusion'].get('linear_weights', {}).keys())}"
    )
    print()

    print("Step 2: Load Parametrization Data (HOW)")
    print("-" * 80)

    env = "production"
    cli_overrides = {"timeout_s": 180.0}

    executor_config = ParametrizationLoader.load_runtime_config(
        env=env, cli_overrides=cli_overrides
    )

    print(f"✓ Environment: {env}")
    print(f"✓ Timeout: {executor_config.timeout_s}s (CLI override)")
    print(f"✓ Retry: {executor_config.retry}")
    print(f"✓ Max tokens: {executor_config.max_tokens}")
    print()

    print("Step 3: Initialize Analyzer")
    print("-" * 80)

    analyzer = PolicyAnalyzer(
        calibration=calibration,
        executor_config=executor_config,
    )

    print("✓ Analyzer initialized with:")
    print(f"  - Calibration: {len(calibration)} domains")
    print(f"  - ExecutorConfig: timeout={executor_config.timeout_s}s")
    print()

    print("Step 4: Run Analysis")
    print("-" * 80)

    sample_policy = "Sample policy text for analysis..."
    result = analyzer.analyze(sample_policy)

    print("✓ Analysis complete:")
    print(f"  - Quality Score: {result['quality_score']:.3f}")
    print(f"  - Used calibration: b_theory={result['calibration_used']['b_theory']}")
    print(f"  - Executed with: timeout={result['execution_params']['timeout_s']}s")
    print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✓ Calibration loaded separately (quality characteristics)")
    print("✓ Parametrization loaded separately (runtime parameters)")
    print("✓ Boundary maintained throughout execution")
    print("✓ Quality measurements independent of execution environment")
    print("✓ Runtime parameters adjustable without affecting quality scores")
    print()
    print("This separation ensures:")
    print("  • Scientific integrity (quality scores stable across deployments)")
    print("  • Operational flexibility (runtime params adjustable per-run)")
    print("  • Clear governance (different approval processes)")
    print("  • Reproducibility (calibration version controlled)")
    print()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
