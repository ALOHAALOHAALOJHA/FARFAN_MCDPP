#!/usr/bin/env python3
"""
Quick validation script for Meta Layer implementation.
Tests that the implementation is importable and has correct structure.
"""

import sys

def validate():
    try:
        from src.orchestration.meta_layer import (
            MetaLayerEvaluator,
            MetaLayerConfig,
            TransparencyArtifacts,
            GovernanceArtifacts,
            CostMetrics,
            create_default_config,
            compute_config_hash
        )
        print("✓ All imports successful")
        
        config = create_default_config()
        print(f"✓ Default config created: w_transp={config.w_transparency}, w_gov={config.w_governance}, w_cost={config.w_cost}")
        
        assert config.w_transparency == 0.5, "w_transparency should be 0.5"
        assert config.w_governance == 0.4, "w_governance should be 0.4"
        assert config.w_cost == 0.1, "w_cost should be 0.1"
        print("✓ Weights correct: 0.5·m_transp + 0.4·m_gov + 0.1·m_cost")
        
        evaluator = MetaLayerEvaluator(config)
        print("✓ Evaluator instantiated")
        
        # Test discrete values for transparency
        print("\n--- Testing m_transp discrete values ---")
        m_transp_1 = evaluator.evaluate_transparency(
            {"formula_export": "Cal(I) = Choquet formula", 
             "trace": "Phase 0 step method execution trace",
             "logs": {"timestamp": "2024", "level": "INFO", "method_name": "test", "phase": "test", "message": "test"}},
            {"required": ["timestamp", "level", "method_name", "phase", "message"]}
        )
        print(f"  3/3 conditions: {m_transp_1} (expected 1.0)")
        assert m_transp_1 == 1.0, f"Should be 1.0, got {m_transp_1}"
        
        m_transp_07 = evaluator.evaluate_transparency(
            {"formula_export": "Cal(I) = expanded Choquet integral", "trace": "Phase 1 step execution trace complete", "logs": None}, None
        )
        print(f"  2/3 conditions: {m_transp_07} (expected 0.7)")
        assert m_transp_07 == 0.7, f"Should be 0.7, got {m_transp_07}"
        
        m_transp_04 = evaluator.evaluate_transparency(
            {"formula_export": None, "trace": "Phase 0 step execution method trace", "logs": None}, None
        )
        print(f"  1/3 conditions: {m_transp_04} (expected 0.4)")
        assert m_transp_04 == 0.4, f"Should be 0.4, got {m_transp_04}"
        
        m_transp_0 = evaluator.evaluate_transparency(
            {"formula_export": None, "trace": None, "logs": None}, None
        )
        print(f"  0/3 conditions: {m_transp_0} (expected 0.0)")
        assert m_transp_0 == 0.0, f"Should be 0.0, got {m_transp_0}"
        
        print("✓ m_transp discrete values: {1.0, 0.7, 0.4, 0.0}")
        
        # Test discrete values for governance
        print("\n--- Testing m_gov discrete values ---")
        m_gov_1 = evaluator.evaluate_governance(
            {"version_tag": "v2.1.3", "config_hash": "a" * 64, "signature": None}
        )
        print(f"  3/3 conditions: {m_gov_1} (expected 1.0)")
        assert m_gov_1 == 1.0, f"Should be 1.0, got {m_gov_1}"
        
        m_gov_066 = evaluator.evaluate_governance(
            {"version_tag": "v1.0.0", "config_hash": "", "signature": None}
        )
        print(f"  2/3 conditions: {m_gov_066} (expected 0.66)")
        assert m_gov_066 == 0.66, f"Should be 0.66, got {m_gov_066}"
        
        # Create config with signature required to test 1/3 and 0/3
        from src.orchestration.meta_layer import MetaLayerConfig
        config_with_sig = MetaLayerConfig(
            w_transparency=0.5,
            w_governance=0.4,
            w_cost=0.1,
            transparency_requirements={
                "require_formula_export": True,
                "require_trace_complete": True,
                "require_logs_conform": True
            },
            governance_requirements={
                "require_version_tag": True,
                "require_config_hash": True,
                "require_signature": True  # Make signature required
            },
            cost_thresholds={
                "threshold_fast": 1.0,
                "threshold_acceptable": 5.0,
                "threshold_memory_normal": 512.0
            }
        )
        evaluator_with_sig = MetaLayerEvaluator(config_with_sig)
        
        m_gov_033 = evaluator_with_sig.evaluate_governance(
            {"version_tag": "v1.5.0", "config_hash": "", "signature": None}
        )
        print(f"  1/3 conditions (sig required): {m_gov_033} (expected 0.33)")
        assert m_gov_033 == 0.33, f"Should be 0.33, got {m_gov_033}"
        
        m_gov_0 = evaluator_with_sig.evaluate_governance(
            {"version_tag": "unknown", "config_hash": "", "signature": None}
        )
        print(f"  0/3 conditions (sig required): {m_gov_0} (expected 0.0)")
        assert m_gov_0 == 0.0, f"Should be 0.0, got {m_gov_0}"
        
        print("✓ m_gov discrete values: {1.0, 0.66, 0.33, 0.0}")
        
        # Test discrete values for cost
        print("\n--- Testing m_cost discrete values ---")
        m_cost_1 = evaluator.evaluate_cost(
            {"execution_time_s": 0.5, "memory_usage_mb": 256.0}
        )
        print(f"  Fast (<1s, ≤512MB): {m_cost_1} (expected 1.0)")
        assert m_cost_1 == 1.0, f"Should be 1.0, got {m_cost_1}"
        
        m_cost_08 = evaluator.evaluate_cost(
            {"execution_time_s": 3.0, "memory_usage_mb": 400.0}
        )
        print(f"  Acceptable (<5s, ≤512MB): {m_cost_08} (expected 0.8)")
        assert m_cost_08 == 0.8, f"Should be 0.8, got {m_cost_08}"
        
        m_cost_05 = evaluator.evaluate_cost(
            {"execution_time_s": 6.0, "memory_usage_mb": 256.0}
        )
        print(f"  Poor (≥5s): {m_cost_05} (expected 0.5)")
        assert m_cost_05 == 0.5, f"Should be 0.5, got {m_cost_05}"
        
        m_cost_0 = evaluator.evaluate_cost(
            {"execution_time_s": -1.0, "memory_usage_mb": 256.0}
        )
        print(f"  Invalid (negative): {m_cost_0} (expected 0.0)")
        assert m_cost_0 == 0.0, f"Should be 0.0, got {m_cost_0}"
        
        print("✓ m_cost discrete values: {1.0, 0.8, 0.5, 0.0}")
        
        # Test full evaluation with perfect score
        print("\n--- Testing full evaluation ---")
        test_transp: TransparencyArtifacts = {
            "formula_export": "Cal(I) = Choquet formula",
            "trace": "Phase 0 step method execution",
            "logs": {"timestamp": "2024", "level": "INFO", "method_name": "test", "phase": "test", "message": "test"}
        }
        
        test_gov: GovernanceArtifacts = {
            "version_tag": "v2.1.3",
            "config_hash": "a" * 64,
            "signature": None
        }
        
        test_cost: CostMetrics = {
            "execution_time_s": 0.5,
            "memory_usage_mb": 256.0
        }
        
        log_schema = {"required": ["timestamp", "level", "method_name", "phase", "message"]}
        
        result = evaluator.evaluate(test_transp, test_gov, test_cost, log_schema)
        print(f"  Overall score: {result['score']:.3f}")
        print(f"  - m_transparency: {result['m_transparency']:.3f}")
        print(f"  - m_governance: {result['m_governance']:.3f}")
        print(f"  - m_cost: {result['m_cost']:.3f}")
        
        assert result['m_transparency'] == 1.0, f"m_transp should be 1.0, got {result['m_transparency']}"
        assert result['m_governance'] == 1.0, f"m_gov should be 1.0, got {result['m_governance']}"
        assert result['m_cost'] == 1.0, f"m_cost should be 1.0, got {result['m_cost']}"
        assert result['score'] == 1.0, f"Perfect score should be 1.0, got {result['score']}"
        print("✓ Perfect score evaluation: 1.0")
        
        # Test aggregation formula
        print("\n--- Testing aggregation formula ---")
        result2 = evaluator.evaluate(
            {"formula_export": "x_@m calibration formula expanded", "trace": "Phase 1 step execution method trace complete", "logs": None},  # 0.7
            {"version_tag": "v1.0.0", "config_hash": "", "signature": None},  # 0.66
            {"execution_time_s": 6.0, "memory_usage_mb": 256.0},  # 0.5
            None
        )
        expected = 0.5 * 0.7 + 0.4 * 0.66 + 0.1 * 0.5
        print(f"  Score: {result2['score']:.4f}")
        print(f"  Expected: {expected:.4f} (0.5×0.7 + 0.4×0.66 + 0.1×0.5)")
        assert abs(result2['score'] - expected) < 1e-6, f"Formula mismatch"
        print("✓ Aggregation formula: x_@m = 0.5·m_transp + 0.4·m_gov + 0.1·m_cost")
        
        # Test config hash
        config_hash = compute_config_hash({"test": "data"})
        assert len(config_hash) == 64, "Config hash should be 64 chars (SHA256)"
        print(f"\n✓ Config hash generation: {config_hash[:16]}...")
        
        print("\n" + "="*60)
        print("✓✓✓ ALL VALIDATIONS PASSED ✓✓✓")
        print("="*60)
        print("\nImplementation Summary:")
        print("  - m_transp: {1.0, 0.7, 0.4, 0.0} ✓")
        print("  - m_gov: {1.0, 0.66, 0.33, 0.0} ✓")
        print("  - m_cost: {1.0, 0.8, 0.5, 0.0} ✓")
        print("  - Aggregation: x_@m = 0.5·m_transp + 0.4·m_gov + 0.1·m_cost ✓")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Validation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(validate())
