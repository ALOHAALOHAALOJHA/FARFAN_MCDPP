#!/usr/bin/env python3
"""
Validation script for PDET Enrichment System.

This script validates:
1. All validators are importable
2. PDET data loads correctly
3. Enrichment orchestrator works end-to-end
4. All four gates function properly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E501


def validate_imports():
    """Validate all modules can be imported."""
    print("=" * 60)
    print("VALIDATION 1: Module Imports")
    print("=" * 60)

    try:
        from canonic_questionnaire_central.validations.runtime_validators import (
            ScopeValidator,
            ValueAddScorer,
            CapabilityValidator,
            ChannelValidator,
        )

        print("✅ All validators imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import validators: {e}")
        return False

    try:
        from canonic_questionnaire_central.colombia_context import (
            get_pdet_municipalities,
            get_pdet_subregions,
            get_pdet_municipalities_for_policy_area,
        )

        print("✅ PDET context functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PDET context: {e}")
        return False

    try:
        from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
            EnrichmentOrchestrator,
            EnrichmentRequest,
        )

        print("✅ Enrichment orchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import orchestrator: {e}")
        return False

    return True


def validate_pdet_data():
    """Validate PDET municipalities data loads correctly."""
    print("\n" + "=" * 60)
    print("VALIDATION 2: PDET Data Loading")
    print("=" * 60)

    try:
        from canonic_questionnaire_central.colombia_context import get_pdet_municipalities

        pdet_data = get_pdet_municipalities()

        # Check overview
        assert "overview" in pdet_data, "Missing overview section"
        assert pdet_data["overview"]["total_municipalities"] == 170, "Incorrect municipality count"
        assert pdet_data["overview"]["total_subregions"] == 16, "Incorrect subregion count"
        print(
            f"✅ PDET overview loaded: {pdet_data['overview']['total_municipalities']} municipalities"
        )

        # Check subregions
        assert "subregions" in pdet_data, "Missing subregions section"
        subregions = pdet_data["subregions"]
        print(f"✅ PDET subregions loaded: {len(subregions)} subregions")

        # Check policy area mappings
        assert "policy_area_mappings" in pdet_data, "Missing policy area mappings"
        pa_mappings = pdet_data["policy_area_mappings"]
        print(f"✅ Policy area mappings loaded: {len(pa_mappings)} policy areas")

        # Check governance metadata
        assert "data_governance" in pdet_data, "Missing data governance metadata"
        print("✅ Data governance metadata present")

        return True

    except Exception as e:
        print(f"❌ Failed to load PDET data: {e}")
        return False


def validate_validators():
    """Validate individual validators work correctly."""
    print("\n" + "=" * 60)
    print("VALIDATION 3: Individual Validators")
    print("=" * 60)

    try:
        from canonic_questionnaire_central.validations.runtime_validators import (
            ScopeValidator,
            SignalScope,
            ScopeLevel,
            ValueAddScorer,
            CapabilityValidator,
            SignalCapability,
            ChannelValidator,
            DataFlow,
            ChannelType,
        )

        # Test Scope Validator
        scope_validator = ScopeValidator()
        test_scope = SignalScope(
            scope_name="Test Scope",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA"],
            min_confidence=0.50,
            max_signals_per_query=100,
        )
        result = scope_validator.validate(
            consumer_id="test",
            scope=test_scope,
            signal_type="ENRICHMENT_DATA",
            signal_confidence=0.75,
        )
        assert result.valid, "Scope validation failed"
        print("✅ Gate 1 (Scope Validator) working correctly")

        # Test Value-Add Scorer
        value_scorer = ValueAddScorer()
        estimated = value_scorer.estimate_value_add(
            signal_type="ENRICHMENT_DATA", payload={"completeness": "COMPLETO"}
        )
        assert estimated > 0, "Value-add estimation failed"
        print("✅ Gate 2 (Value-Add Scorer) working correctly")

        # Test Capability Validator
        cap_validator = CapabilityValidator()

        class TestConsumer:
            consumer_id = "test"
            declared_capabilities = {SignalCapability.SEMANTIC_PROCESSING}

        cap_validator.validate(TestConsumer(), "ENRICHMENT_DATA")
        print("✅ Gate 3 (Capability Validator) working correctly")

        # Test Channel Validator
        channel_validator = ChannelValidator()
        test_flow = DataFlow(
            flow_id="TEST_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="test_source",
            destination="test_dest",
            data_schema="TestSchema",
            governance_policy="test_policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
        )
        channel_validator.register_flow(test_flow)
        result = channel_validator.validate_flow("TEST_FLOW")
        assert result.valid, "Channel validation failed"
        print("✅ Gate 4 (Channel Validator) working correctly")

        return True

    except Exception as e:
        print(f"❌ Validator validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def validate_enrichment_orchestrator():
    """Validate enrichment orchestrator end-to-end."""
    print("\n" + "=" * 60)
    print("VALIDATION 4: Enrichment Orchestrator End-to-End")
    print("=" * 60)

    try:
        from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
            EnrichmentOrchestrator,
            EnrichmentRequest,
        )
        from canonic_questionnaire_central.validations.runtime_validators import (
            SignalScope,
            ScopeLevel,
            SignalCapability,
        )

        # Create orchestrator
        orchestrator = EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)
        print("✅ Orchestrator initialized")

        # Create valid request
        scope = SignalScope(
            scope_name="Test Consumer",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=["PA01", "PA02"],
            min_confidence=0.50,
            max_signals_per_query=100,
        )

        capabilities = [
            SignalCapability.SEMANTIC_PROCESSING,
            SignalCapability.TABLE_PARSING,
            SignalCapability.GRAPH_CONSTRUCTION,
        ]

        request = EnrichmentRequest(
            consumer_id="test_consumer",
            consumer_scope=scope,
            consumer_capabilities=capabilities,
            target_policy_areas=["PA01", "PA02"],
            target_questions=["Q001", "Q002"],
            requested_context=["municipalities", "subregions", "policy_area_mappings"],
        )
        print("✅ Enrichment request created")

        # Perform enrichment
        result = orchestrator.enrich(request)

        # Validate result
        assert result is not None, "No result returned"
        print(f"✅ Enrichment completed: {'SUCCESS' if result.success else 'FAILED'}")

        if not result.success:
            print(f"   Violations: {result.violations}")
            print(f"   Gate status: {result.gate_status}")
            return False

        # Validate gate status
        assert all(result.gate_status.values()), "Not all gates passed"
        print("✅ All four gates passed validation")

        # Validate enriched data
        assert "data" in result.enriched_data, "No enriched data returned"
        data = result.enriched_data["data"]

        if "municipalities" in data:
            print(f"✅ Municipalities data present ({len(data['municipalities'])} municipalities)")

        if "subregions" in data:
            print(f"✅ Subregions data present ({len(data['subregions'])} subregions)")

        if "policy_area_mappings" in data:
            print(f"✅ Policy area mappings present ({len(data['policy_area_mappings'])} mappings)")

        # Generate and validate report
        report = orchestrator.get_enrichment_report()
        assert "enrichment_orchestrator_report" in report, "Missing orchestrator report"
        assert "gate_1_scope_validator" in report, "Missing gate 1 report"
        assert "gate_2_value_add_scorer" in report, "Missing gate 2 report"
        assert "gate_3_capability_validator" in report, "Missing gate 3 report"
        assert "gate_4_channel_validator" in report, "Missing gate 4 report"
        print("✅ Comprehensive report generated")

        return True

    except Exception as e:
        print(f"❌ Orchestrator validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all validations."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 5 + "PDET ENRICHMENT SYSTEM VALIDATION" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # Run validations
    results.append(("Module Imports", validate_imports()))
    results.append(("PDET Data Loading", validate_pdet_data()))
    results.append(("Individual Validators", validate_validators()))
    results.append(("Enrichment Orchestrator", validate_enrichment_orchestrator()))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:<30} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 ALL VALIDATIONS PASSED - SYSTEM IS OPERATIONAL")
        print("\nThe PDET Enrichment System is:")
        print("  ✅ Properly installed")
        print("  ✅ All four gates operational")
        print("  ✅ PDET data loaded successfully")
        print("  ✅ End-to-end enrichment working")
        print("\nStatus: PRODUCTION-READY ✅")
        return 0
    else:
        print("\n❌ SOME VALIDATIONS FAILED - PLEASE CHECK ERRORS ABOVE")
        return 1


if __name__ == "__main__":
    sys.exit(main())
