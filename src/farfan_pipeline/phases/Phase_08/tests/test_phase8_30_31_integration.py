"""
Integration tests for phase8_30 (Legal Framework) and phase8_31 (Narrative Generation).

Tests the complete flow:
1. Legal framework compliance validation
2. Narrative generation with Carver principles
3. Integration with existing Phase 8 modules
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(src_path))


class TestColombianLegalFramework:
    """Test suite for phase8_30_00_colombian_legal_framework.py"""
    
    def test_imports(self):
        """Test that all imports work correctly."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            MunicipalCategory,
            SGPComponent,
            FinancingSource,
            LegalFramework,
            PDMFormulationPhase,
            ColombianLegalFrameworkEngine,
        )
        
        assert MunicipalCategory.SPECIAL is not None
        assert SGPComponent.EDUCATION is not None
        assert PDMFormulationPhase.DIAGNOSTIC is not None
    
    def test_municipality_categorization(self):
        """Test municipality category determination."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            ColombianLegalFrameworkEngine,
            MunicipalCategory,
        )
        
        engine = ColombianLegalFrameworkEngine()
        
        # Test Category 3 (Medellín-sized)
        category = engine.get_municipality_category(population=45_000, income_smmlv=35_000)
        assert category == MunicipalCategory.CATEGORY_3
        
        # Test Category 6 (Small rural)
        category = engine.get_municipality_category(population=5_000, income_smmlv=8_000)
        assert category == MunicipalCategory.CATEGORY_6
        
        # Test Special (Large city)
        category = engine.get_municipality_category(population=600_000, income_smmlv=450_000)
        assert category == MunicipalCategory.SPECIAL
    
    def test_sgp_allocation(self):
        """Test SGP allocation calculations."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            ColombianLegalFrameworkEngine,
            MunicipalCategory,
            SGPComponent,
        )
        
        engine = ColombianLegalFrameworkEngine()
        
        # Test education for certificado
        sgp = engine.get_sgp_allocation(MunicipalCategory.CATEGORY_1, SGPComponent.EDUCATION)
        assert sgp["receives_sector"] is True
        assert sgp["total_percentage"] == 0.585
        
        # Test education for non-certificado
        sgp = engine.get_sgp_allocation(MunicipalCategory.CATEGORY_4, SGPComponent.EDUCATION)
        assert sgp["receives_sector"] is False
        assert sgp["total_percentage"] == 0.0
        
        # Test health (all municipalities)
        sgp = engine.get_sgp_allocation(MunicipalCategory.CATEGORY_6, SGPComponent.HEALTH)
        assert sgp["receives_sector"] is True
        assert sgp["total_percentage"] == 0.245
        
        # Test general purpose discretionary for Category 4
        sgp = engine.get_sgp_allocation(MunicipalCategory.CATEGORY_4, SGPComponent.GENERAL_PURPOSE)
        assert sgp["discretionary_percentage"] > 0
        assert sgp["discretionary_percentage"] == 0.116 * 0.42
    
    def test_legal_obligations(self):
        """Test legal framework retrieval."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            ColombianLegalFrameworkEngine,
        )
        
        engine = ColombianLegalFrameworkEngine()
        
        # Test PA01 (Gender Equality) - Ley 1257/2008
        frameworks = engine.get_legal_obligations("PA01")
        assert len(frameworks) > 0
        assert any(f.law_number == "1257" and f.law_year == 2008 for f in frameworks)
        
        # Test PA09 (Health) - Ley 715/2001
        frameworks = engine.get_legal_obligations("PA09")
        assert len(frameworks) > 0
        assert any(f.law_number == "715" and f.law_year == 2001 for f in frameworks)
        
        # Test PA03 (Environment) - Multiple laws
        frameworks = engine.get_legal_obligations("PA03")
        assert len(frameworks) >= 2  # Ley 99/1993 + Ley 388/1997
    
    def test_compliance_validation(self):
        """Test PDM compliance validation."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            ColombianLegalFrameworkEngine,
            MunicipalCategory,
            FinancingSource,
            PDMFormulationPhase,
        )
        
        engine = ColombianLegalFrameworkEngine()
        
        # Test fully compliant recommendation
        compliance = engine.validate_pdm_compliance(
            recommendation_id="PA01-DIM01-CRISIS",
            policy_area="PA01",
            municipality_category=MunicipalCategory.CATEGORY_3,
            required_financing_sources=[FinancingSource.RECURSOS_PROPIOS],
            formulation_phase=PDMFormulationPhase.INVESTMENT_PLAN,
        )
        
        assert compliance.is_legally_compliant
        assert compliance.compliance_level in ["FULL", "PARTIAL"]
        assert compliance.overall_compliance_score >= 0.5
    
    def test_financing_sources(self):
        """Test financing source identification."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            ColombianLegalFrameworkEngine,
            MunicipalCategory,
        )
        
        engine = ColombianLegalFrameworkEngine()
        
        # Test education financing (certificado)
        sources = engine.get_financing_sources(
            instrument_type="SERVICE_DELIVERY",
            municipality_category=MunicipalCategory.CATEGORY_1,
            policy_area="PA08",
        )
        assert len(sources) > 0
        
        # Test infrastructure financing
        sources = engine.get_financing_sources(
            instrument_type="INFRASTRUCTURE",
            municipality_category=MunicipalCategory.CATEGORY_4,
            policy_area="PA07",
        )
        assert len(sources) >= 2


class TestNarrativeGeneration:
    """Test suite for phase8_31_00_narrative_generation.py"""
    
    def test_imports(self):
        """Test that all imports work correctly."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            CarverPrinciples,
            CarverViolation,
            NarrativeTemplate,
            ProseRecommendation,
            NarrativeGenerator,
            convert_bullets_to_prose,
        )
        
        assert CarverPrinciples is not None
        assert NarrativeGenerator is not None
    
    def test_carver_active_voice(self):
        """Test active voice detection."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            CarverPrinciples,
        )
        
        # Test passive voice detection
        passive_text = "El proyecto será ejecutado por la alcaldía."
        violations = CarverPrinciples.check_active_voice(passive_text)
        assert len(violations) > 0
        assert violations[0].principle == "ACTIVE_VOICE"
        
        # Test active voice (should pass)
        active_text = "La alcaldía ejecutará el proyecto."
        violations = CarverPrinciples.check_active_voice(active_text)
        assert len(violations) == 0
    
    def test_carver_sentence_length(self):
        """Test sentence length checking."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            CarverPrinciples,
        )
        
        # Short sentence (should pass)
        short = "La alcaldía construirá diez aulas."
        violations = CarverPrinciples.check_sentence_length(short, max_words=25)
        assert len(violations) == 0
        
        # Long sentence (should fail)
        long = " ".join(["palabra"] * 30) + "."
        violations = CarverPrinciples.check_sentence_length(long, max_words=25)
        assert len(violations) > 0
        assert violations[0].principle == "SENTENCE_LENGTH"
    
    def test_carver_vague_verbs(self):
        """Test vague verb detection."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            CarverPrinciples,
        )
        
        # Vague verbs (should fail)
        vague = "Se fortalecerá la capacidad institucional."
        violations = CarverPrinciples.check_specific_verbs(vague)
        assert len(violations) > 0
        assert "fortalecer" in violations[0].explanation.lower()
        
        # Specific verbs (should pass)
        specific = "Se capacitará a 50 funcionarios."
        violations = CarverPrinciples.check_specific_verbs(specific)
        assert len(violations) == 0
    
    def test_carver_validation_complete(self):
        """Test complete Carver validation."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            CarverPrinciples,
        )
        
        # Bad text (multiple violations)
        bad = (
            "Se fortalecerá la gobernanza mediante la implementación de una estrategia "
            "holística que será ejecutada por la alcaldía para garantizar la sostenibilidad."
        )
        score, violations = CarverPrinciples.validate_all(bad)
        assert score < 100  # Should have violations
        assert len(violations) > 0
        
        # Good text (few/no violations)
        good = (
            "La alcaldía construirá diez aulas. "
            "Los docentes recibirán capacitación. "
            "Se entregarán materiales didácticos."
        )
        score_good, violations_good = CarverPrinciples.validate_all(good)
        assert score_good > score  # Good text should score higher
    
    def test_bullet_to_prose_conversion(self):
        """Test bullet point to prose conversion."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            convert_bullets_to_prose,
        )
        
        # Test with multiple bullets
        bullets = [
            "Falta de infraestructura educativa",
            "Docentes sin capacitación",
            "Ausencia de material didáctico",
        ]
        prose = convert_bullets_to_prose(bullets)
        assert "Se identificó" in prose
        assert "infraestructura educativa" in prose
        assert "capacitación" in prose
        assert " y " in prose  # Should have conjunction
        
        # Test with single bullet
        single = ["Falta de agua potable"]
        prose = convert_bullets_to_prose(single)
        assert "agua potable" in prose
    
    def test_responsible_entity_specification(self):
        """Test responsible entity specification."""
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            NarrativeGenerator,
        )
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            MunicipalCategory,
        )
        
        generator = NarrativeGenerator()
        
        # Test budget responsibility for large municipality
        responsible = generator.specify_responsible_entities("budget", MunicipalCategory.SPECIAL)
        assert "Secretaría de Hacienda" in responsible
        
        # Test budget responsibility for small municipality
        responsible = generator.specify_responsible_entities("budget", MunicipalCategory.CATEGORY_6)
        assert "Tesorería" in responsible
        
        # Test verification responsibility
        responsible = generator.specify_responsible_entities("verification", MunicipalCategory.CATEGORY_1)
        assert "Control Interno" in responsible or "Alcalde" in responsible


class TestIntegration:
    """Integration tests for both modules working together."""
    
    def test_full_workflow_simulation(self):
        """Simulate full workflow: legal validation → narrative generation."""
        from farfan_pipeline.phases.Phase_08.phase8_30_00_colombian_legal_framework import (
            ColombianLegalFrameworkEngine,
            MunicipalCategory,
            FinancingSource,
            PDMFormulationPhase,
        )
        from farfan_pipeline.phases.Phase_08.phase8_31_00_narrative_generation import (
            NarrativeGenerator,
        )
        
        # Step 1: Validate legal compliance
        legal_engine = ColombianLegalFrameworkEngine()
        compliance = legal_engine.validate_pdm_compliance(
            recommendation_id="PA01-DIM01-CRISIS",
            policy_area="PA01",
            municipality_category=MunicipalCategory.CATEGORY_3,
            required_financing_sources=[FinancingSource.RECURSOS_PROPIOS],
            formulation_phase=PDMFormulationPhase.INVESTMENT_PLAN,
        )
        
        assert compliance.is_legally_compliant
        
        # Step 2: Generate narrative (would require full value chain)
        narrative_gen = NarrativeGenerator(legal_engine=legal_engine)
        
        # Test responsible entity specification
        responsible = narrative_gen.specify_responsible_entities(
            "implementation", MunicipalCategory.CATEGORY_3
        )
        assert "Planeación" in responsible or "planeación" in responsible.lower()


def run_tests():
    """Run all tests and report results."""
    print("="*80)
    print("PHASE 8 MODULE 30-31 INTEGRATION TESTS")
    print("="*80)
    
    # Test Legal Framework
    print("\n1. Testing Colombian Legal Framework (phase8_30)...")
    test_legal = TestColombianLegalFramework()
    try:
        test_legal.test_imports()
        print("   ✓ Imports successful")
        
        test_legal.test_municipality_categorization()
        print("   ✓ Municipality categorization works")
        
        test_legal.test_sgp_allocation()
        print("   ✓ SGP allocation calculations correct")
        
        test_legal.test_legal_obligations()
        print("   ✓ Legal framework retrieval successful")
        
        test_legal.test_compliance_validation()
        print("   ✓ Compliance validation functional")
        
        test_legal.test_financing_sources()
        print("   ✓ Financing source identification works")
        
    except Exception as e:
        print(f"   ✗ Legal framework test failed: {e}")
        return False
    
    # Test Narrative Generation
    print("\n2. Testing Narrative Generation (phase8_31)...")
    test_narrative = TestNarrativeGeneration()
    try:
        test_narrative.test_imports()
        print("   ✓ Imports successful")
        
        test_narrative.test_carver_active_voice()
        print("   ✓ Active voice detection works")
        
        test_narrative.test_carver_sentence_length()
        print("   ✓ Sentence length validation works")
        
        test_narrative.test_carver_vague_verbs()
        print("   ✓ Vague verb detection works")
        
        test_narrative.test_carver_validation_complete()
        print("   ✓ Complete Carver validation works")
        
        test_narrative.test_bullet_to_prose_conversion()
        print("   ✓ Bullet-to-prose conversion works")
        
        test_narrative.test_responsible_entity_specification()
        print("   ✓ Responsible entity specification works")
        
    except Exception as e:
        print(f"   ✗ Narrative generation test failed: {e}")
        return False
    
    # Test Integration
    print("\n3. Testing Integration...")
    test_integration = TestIntegration()
    try:
        test_integration.test_full_workflow_simulation()
        print("   ✓ Full workflow simulation successful")
        
    except Exception as e:
        print(f"   ✗ Integration test failed: {e}")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("="*80)
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
