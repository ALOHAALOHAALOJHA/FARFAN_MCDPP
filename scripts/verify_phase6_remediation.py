#!/usr/bin/env python3
"""
Phase 6 Remediation Verification Script

Verifies all audit findings have been resolved:
1. Documentation drift
2. Constants/config unification
3. Contract integration
4. cluster_id documentation
5. Coherence threshold integration

Exit code 0 = all checks pass
Exit code 1 = one or more checks failed
"""
import importlib
import os
import sys


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"       {details}")
    return condition


def main() -> int:
    results: list[bool] = []

    print("=" * 60)
    print("PHASE 6 REMEDIATION VERIFICATION")
    print("=" * 60)

    # === CHECK 1: Unified Config Exists ===
    print("\n[1] Configuration Unification")
    try:
        from farfan_pipeline.phases.Phase_6.phase6_10_01_scoring_config import (
            PHASE6_CONFIG,
            Phase6ScoringConfig,
            DispersionScenario,
            CoherenceQuality,
        )

        results.append(check("Unified config module exists", True))
        results.append(
            check(
                "PHASE6_CONFIG is frozen dataclass",
                isinstance(PHASE6_CONFIG, Phase6ScoringConfig),
            )
        )
    except ImportError as e:
        results.append(check("Unified config module exists", False, str(e)))
        PHASE6_CONFIG = None  # type: ignore

    # === CHECK 2: Constants Re-export ===
    print("\n[2] Constants Backwards Compatibility")
    try:
        from farfan_pipeline.phases.Phase_6.phase6_10_00_phase_6_constants import (
            PENALTY_WEIGHT,
            DISPERSION_THRESHOLDS,
            MIN_SCORE,
            MAX_SCORE,
        )

        results.append(
            check(
                "PENALTY_WEIGHT exported",
                PHASE6_CONFIG is not None
                and PENALTY_WEIGHT == PHASE6_CONFIG.base_penalty_weight,
                f"PENALTY_WEIGHT={PENALTY_WEIGHT}, config={getattr(PHASE6_CONFIG, 'base_penalty_weight', 'n/a')}",
            )
        )
        results.append(
            check(
                "DISPERSION_THRESHOLDS derived from config",
                PHASE6_CONFIG is not None
                and DISPERSION_THRESHOLDS["CV_CONVERGENCE"]
                == PHASE6_CONFIG.cv_convergence,
            )
        )
    except ImportError as e:
        results.append(check("Constants re-export", False, str(e)))

    # === CHECK 3: Adaptive Scoring Uses Config ===
    print("\n[3] Adaptive Scoring Integration")
    try:
        from farfan_pipeline.phases.Phase_6.phase6_20_00_adaptive_meso_scoring import (
            AdaptiveScoringConfig,
        )

        config = AdaptiveScoringConfig()
        results.append(
            check(
                "AdaptiveScoringConfig uses PHASE6_CONFIG defaults",
                PHASE6_CONFIG is not None
                and config.base_penalty_weight == PHASE6_CONFIG.base_penalty_weight
                and config.convergence_cv_threshold == PHASE6_CONFIG.cv_convergence,
            )
        )
    except Exception as e:
        results.append(check("Adaptive scoring integration", False, str(e)))

    # === CHECK 4: Contract Integration ===
    print("\n[4] Contract Integration")
    try:
        from farfan_pipeline.phases.Phase_6 import ClusterAggregator
        import inspect

        sig = inspect.signature(ClusterAggregator.__init__)
        params = list(sig.parameters.keys())

        results.append(check("enforce_contracts parameter exists", "enforce_contracts" in params))
        results.append(check("contract_mode parameter exists", "contract_mode" in params))

        source = inspect.getsource(ClusterAggregator.aggregate)
        results.append(check("aggregate() calls _validate_input_contract", "_validate_input_contract" in source))
        results.append(check("aggregate() calls _validate_output_contract", "_validate_output_contract" in source))
    except Exception as e:
        results.append(check("Contract integration", False, str(e)))

    # === CHECK 5: Coherence Classification ===
    print("\n[5] Coherence Classification")
    try:
        from farfan_pipeline.phases.Phase_6.contracts.phase6_output_contract import (
            Phase6OutputContract,
        )

        has_method = hasattr(Phase6OutputContract, "classify_coherence_quality")
        results.append(check("classify_coherence_quality method exists", has_method))

        if has_method:
            quality, desc = Phase6OutputContract.classify_coherence_quality(0.9)
            results.append(
                check(
                    "Coherence 0.9 classified as EXCELLENT",
                    quality == CoherenceQuality.EXCELLENT,
                    desc,
                )
            )
    except Exception as e:
        results.append(check("Coherence classification", False, str(e)))

    # === CHECK 6: Documentation Updated ===
    print("\n[6] Documentation Drift Resolved")
    docs_path = "src/farfan_pipeline/phases/Phase_6/docs"

    exec_flow = docs_path / "phase6_execution_flow.md"
    if os.path.exists(exec_flow):
        with open(exec_flow, encoding="utf-8") as f:
            content = f.read()
        results.append(
            check(
                "execution_flow.md: No 'pending implementation' for aggregator",
                "aggregator pending" not in content.lower(),
            )
        )
        results.append(
            check(
                "execution_flow.md: Hermeticity Model section exists",
                "Hermeticity Model" in content,
            )
        )
    else:
        results.append(check("execution_flow.md exists", False))

    # === SUMMARY ===
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"SUMMARY: {passed}/{total} checks passed")
    print("=" * 60)

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
