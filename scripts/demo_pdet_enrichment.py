#!/usr/bin/env python3
"""
Demo script for PDET Municipality Context Validation Enrichment.

This script demonstrates the integration of PDET municipality context
with validation templates to ensure contextual accuracy.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E501


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_basic_functionality():
    """Demonstrate basic PDET validator functionality."""
    from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

    print_header("1. BASIC FUNCTIONALITY")

    # Initialize validator
    validator = PDETValidator()
    print("✅ PDETValidator initialized")

    # Get statistics
    stats = validator.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   - PDET Municipalities Indexed: {stats['pdet_municipalities_indexed']}")
    print(f"   - Subregions: {stats['pdet_subregions_indexed']}")
    print(f"   - Total PDET Validations: {stats['total_pdet_validations']}")
    print(f"   - Validation Templates: v{stats['validation_templates_version']}")
    print(f"   - PDET Enrichment: v{stats['pdet_enrichment_version']}")


def demo_municipality_context():
    """Demonstrate municipality context retrieval."""
    from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

    print_header("2. MUNICIPALITY CONTEXT RETRIEVAL")

    validator = PDETValidator()

    # Test municipalities from different subregions
    test_cases = [
        ("19355", "Jambaló", "Alto Patía y Norte del Cauca"),
        ("81001", "Arauca", "Arauca"),
        ("70215", "Chalán", "Montes de María"),
    ]

    for mun_code, expected_name, expected_subregion in test_cases:
        print(f"\n🏛️ Municipality: {expected_name} ({mun_code})")

        # Check if PDET
        is_pdet = validator.is_pdet_municipality(mun_code)
        print(f"   Is PDET: {'✅ Yes' if is_pdet else '❌ No'}")

        if is_pdet:
            # Get context
            context = validator.get_pdet_context(mun_code)
            print(f"   Subregion: {context.subregion_name}")
            print(f"   Category: {context.category}")
            print(f"   Fiscal Autonomy: {context.fiscal_autonomy}")
            print(f"   PATR Initiatives: {context.patr_initiatives}")
            print(f"   OCAD Paz Projects: {context.ocad_paz_projects}")
            print(f"   OCAD Paz Investment: ${context.ocad_paz_investment_cop_millions}M COP")
            print(f"   Key PDET Pillars: {', '.join(context.key_pdet_pillars)}")
            print(f"   Ethnic Composition: {', '.join(context.ethnic_composition)}")


def demo_dimension_validations():
    """Demonstrate dimension-specific PDET validations."""
    from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

    print_header("3. DIMENSION-SPECIFIC VALIDATIONS")

    validator = PDETValidator()

    dimensions = [
        ("DIM01_INSUMOS", "Inputs/Diagnostics"),
        ("DIM02_ACTIVIDADES", "Activities"),
        ("DIM03_PRODUCTOS", "Products/Outputs"),
        ("DIM04_RESULTADOS", "Outcomes/Results"),
        ("DIM05_IMPACTOS", "Long-term Impacts"),
        ("DIM06_CAUSALIDAD", "Causal Logic"),
    ]

    for dim_code, dim_name in dimensions:
        print(f"\n📋 {dim_code}: {dim_name}")

        # Get PDET validations for dimension
        pdet_validations = validator.get_pdet_validations_for_dimension(dim_code)
        print(f"   PDET Validations Available: {len(pdet_validations)}")

        # List validation types
        for val in pdet_validations:
            val_type = val.get("type", "unknown")
            priority = val.get("priority", 0)
            gates = val.get("validation_gates", [])
            print(f"   - {val_type} (Priority: {priority}, Gates: {len(gates)})")


def demo_validation_execution():
    """Demonstrate validation execution with recommendations."""
    from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

    print_header("4. VALIDATION EXECUTION")

    validator = PDETValidator()
    mun_code = "19355"  # Jambaló

    print(f"\n🔍 Validating DIM01_INSUMOS for Jambaló ({mun_code})")

    # Execute validation
    results = validator.validate_pdet_context(
        dimension="DIM01_INSUMOS", municipality_code=mun_code, validation_data={}
    )

    print(f"\n   Total Validations: {len(results)}")

    for result in results:
        print(f"\n   ━━━ {result.validation_type} ━━━")
        print(f"   Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        print(f"   Gates Validated: {', '.join(result.gates_validated)}")

        if result.recommendations:
            print(f"   Recommendations:")
            for rec in result.recommendations:
                print(f"      • {rec}")

        if result.warnings:
            print(f"   Warnings:")
            for warn in result.warnings:
                print(f"      ⚠️ {warn}")


def demo_validation_gates():
    """Demonstrate validation gates configuration."""
    from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

    print_header("5. VALIDATION GATES")

    validator = PDETValidator()
    gates = validator.get_validation_gates_config()

    gate_names = {
        "gate_1_scope": "Gate 1: Consumer Scope Validity",
        "gate_2_value_contribution": "Gate 2: Value Contribution",
        "gate_3_capability_readiness": "Gate 3: Consumer Capability & Readiness",
        "gate_4_channel_integrity": "Gate 4: Channel Integrity",
    }

    for gate_id, gate_name in gate_names.items():
        gate_config = gates.get(gate_id, {})
        enabled = gate_config.get("enabled", False)
        status = "✅ ENABLED" if enabled else "❌ DISABLED"

        print(f"\n{gate_name}")
        print(f"   Status: {status}")
        print(f"   Description: {gate_config.get('description', 'N/A')}")

        # Gate-specific details
        if gate_id == "gate_1_scope":
            signal_types = gate_config.get("required_signal_types", [])
            print(f"   Required Signal Types: {', '.join(signal_types)}")
            print(f"   Min Confidence: {gate_config.get('min_confidence', 0.0)}")

        elif gate_id == "gate_2_value_contribution":
            threshold = gate_config.get("min_value_add_threshold", 0.0)
            print(f"   Min Value-Add Threshold: {threshold * 100:.0f}%")
            contributions = gate_config.get("estimated_contributions", {})
            print(f"   Estimated Contributions:")
            for contrib_type, value in contributions.items():
                print(f"      - {contrib_type}: {value * 100:.0f}%")

        elif gate_id == "gate_3_capability_readiness":
            required = gate_config.get("required_capabilities", [])
            recommended = gate_config.get("recommended_capabilities", [])
            print(f"   Required: {', '.join(required)}")
            print(f"   Recommended: {', '.join(recommended)}")

        elif gate_id == "gate_4_channel_integrity":
            print(f"   Flow ID: {gate_config.get('flow_id', 'N/A')}")
            print(f"   Flow Type: {gate_config.get('flow_type', 'N/A')}")
            print(f"   Source: {gate_config.get('source', 'N/A')}")


def demo_pdet_criteria():
    """Demonstrate PDET municipality criteria."""
    from canonic_questionnaire_central.validations.pdet_validator import PDETValidator

    print_header("6. PDET MUNICIPALITY CRITERIA")

    validator = PDETValidator()
    enrichment = validator.get_pdet_enrichment_metadata()
    criteria = enrichment.get("pdet_municipality_criteria", {})

    print(f"\n📊 Overview:")
    print(f"   Total Municipalities: {criteria.get('total_municipalities', 0)}")
    print(f"   Subregions: {criteria.get('subregions', 0)}")
    print(f"   Legal Basis: {criteria.get('legal_basis', 'N/A')}")

    print(f"\n📚 Data Sources:")
    for source in criteria.get("data_sources", []):
        print(f"   - {source}")

    print(f"\n🎯 Key Characteristics:")
    for char in criteria.get("key_characteristics", []):
        print(f"   - {char}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "PDET MUNICIPALITY CONTEXT VALIDATION DEMO" + " " * 17 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        demo_basic_functionality()
        demo_municipality_context()
        demo_dimension_validations()
        demo_validation_execution()
        demo_validation_gates()
        demo_pdet_criteria()

        print_header("✅ DEMO COMPLETED SUCCESSFULLY")
        print("\n🎉 PDET Enrichment System is fully operational!")
        print("\nFor more information, see:")
        print("   - canonic_questionnaire_central/validations/PDET_VALIDATION_ENRICHMENT.md")
        print("   - canonic_questionnaire_central/validations/pdet_validator.py")
        print("   - canonic_questionnaire_central/validations/validation_templates.json")
        print("")

        return 0

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
